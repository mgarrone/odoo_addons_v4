from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    ticket_origin_id = fields.Many2one(
        'helpdesk.ticket', 
        string='Origen del Ticket', 
        readonly=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    
    tour_id = fields.Many2one(
        'maintenance.giras', 
        string='Gira',
        related='equipment_id.x_mat_gira',
        readonly=True,
        store=True
    )
    
    robot_out_of_service = fields.Boolean(
        string='Robot Fuera de Servicio',
        related='equipment_id.robot_out_of_service',
        readonly=True,
        store=True
    )
    
    ticket_ids = fields.Many2many(
        'helpdesk.ticket',
        string='Tickets de Soporte'
    )
    
    assigned_employee_id = fields.Many2one(
        'hr.employee', 
        string='Empleado asignado a Mantenimiento'
    )
    
    equipment_manager_id = fields.Many2one(
        'hr.employee', 
        string='Responsable de equipo', 
        related='equipment_id.employee_id',
        store=True,
        readonly=True,
        help="Campo informativo del responsable del equipo de mantenimiento"
    )

    # --- Smart Button: Contador de Tickets ---
    ticket_count = fields.Integer(
        compute='_compute_ticket_count', 
        string='Cantidad de Tickets'
    )

    def _compute_ticket_count(self):
        for record in self:
            # Contamos los tickets que apuntan a este mantenimiento
            # Asegúrate de que en helpdesk.ticket el campo se llame 'maintenance_request_id'
            record.ticket_count = self.env['helpdesk.ticket'].search_count([
                ('maintenance_request_id', '=', record.id)
            ])

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tickets de Soporte',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.ticket_ids.ids)],
            'context': {'default_maintenance_request_ids': [(4, self.id)]},
        }

    def action_create_helpdesk_ticket(self):
        for record in self:
            if not record.equipment_id:
                raise models.ValidationError("⚠️ Por favor, seleccione un 'Equipo' antes de crear un ticket de soporte.")
            
            vals = {
                'name': f'Ticket desde Mantenimiento: {record.name}',
                'equipment_id': record.equipment_id.id,
                'description': record.description,
                'partner_id': record.partner_id.id if record.partner_id else False,
                'maintenance_request_ids': [(4, record.id)],
            }
            ticket = self.env['helpdesk.ticket'].create(vals)
            record.write({'ticket_ids': [(4, ticket.id)]})
            
            record.message_post(body="🛠️ Se ha creado un ticket de soporte automáticamente.")

    # --- Lógica de Vencimiento para Kanban ---
    is_overdue = fields.Boolean(
        string='Vencida', 
        compute='_compute_is_overdue',
        store=False
    )
    
    kanban_state = fields.Selection(
        selection=[('normal', 'In Progress'), ('done', 'Ready for next stage'), ('blocked', 'Blocked')],
        string='Kanban State',
        compute='_compute_kanban_state',
        store=True,
        readonly=False
    )

    @api.depends('schedule_date', 'archive')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.schedule_date and record.schedule_date.date() < today and not getattr(record, 'archive', False):
                record.is_overdue = True
            else:
                record.is_overdue = False

    @api.depends('robot_out_of_service', 'schedule_date', 'archive')
    def _compute_kanban_state(self):
        today = fields.Date.today()
        for record in self:
            if record.robot_out_of_service:
                record.kanban_state = 'blocked'
            elif record.schedule_date and record.schedule_date.date() < today and not getattr(record, 'archive', False):
                record.kanban_state = 'done'
            else:
                record.kanban_state = 'normal'

    @api.model
    def _cron_update_kanban_state(self):
        """
        Cron job para actualizar automáticamente el estado Kanban cuando 
        la fecha programada (schedule_date) ha pasado y no está archivado.
        """
        today = fields.Date.today()
        records = self.search([
            ('archive', '=', False),
            ('schedule_date', '<', today),
            ('kanban_state', '!=', 'done')
        ])
        for record in records:
            if record.robot_out_of_service:
                record.kanban_state = 'blocked'
            else:
                record.kanban_state = 'done'