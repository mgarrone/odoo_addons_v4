from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Campos nuevos con nombres limpios
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipo')
    tour_id = fields.Many2one('maintenance.giras', string='Gira', related='equipment_id.x_mat_gira', store=True, readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')
    x_resuelto_ia = fields.Boolean(string='Resuelto exclusivamente con IA')
    
    # Creamos un campo relacionado que "mira" dentro del equipo seleccionado
    # equipment_id es el campo nativo de Odoo que relaciona la solicitud con el equipo
    suspended_support = fields.Boolean(
        string='Soporte Suspendido', 
        related='equipment_id.suspended_support', 
        store=True, 
        readonly=True
    )
    
    robot_out_of_service = fields.Boolean(
        string='Robot Fuera de Servicio',
        related='equipment_id.robot_out_of_service',
        store=True,
        readonly=True
    )
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            if 'x_mat_cuenta_analitica' in self.equipment_id._fields and self.equipment_id.x_mat_cuenta_analitica:
                self.analytic_account_id = self.equipment_id.x_mat_cuenta_analitica
    progress = fields.Selection([
        ('0', '0%'),
        ('25', '25%'),
        ('50', '50%'),
        ('75', '75%'),
        ('100', '100%')
    ], string='Progreso', default='0')

    employee_follower_ids = fields.Many2many(
        'hr.employee', 
        string='Seguidores del ticket',
        domain="[('department_id.name', 'in', ['Técnica', 'Servicio post venta', 'Hotline', 'Instalación y hotline'])]"
    )
    
    parent_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket Padre')
    
    evidence_ids = fields.Many2many(
        'ir.attachment', 
        string='Evidencia'
    )
    
    maintenance_request_id = fields.Many2one(
        'maintenance.request', 
        string='Solicitud de Mantenimiento Legacy', 
        copy=False
    )

    maintenance_request_ids = fields.Many2many(
        'maintenance.request',
        string='Solicitudes de Mantenimiento'
    )

    def action_create_maintenance_request(self):
        for record in self:
            if not record.equipment_id:
                raise UserError("⚠️ Por favor, seleccione un 'Equipo' antes de crear el mantenimiento.")
            
            vals = {
                'name': f'Soporte: {record.name}',
                'equipment_id': record.equipment_id.id,
                'description': record.description,
                'maintenance_type': 'corrective',
                'partner_id': record.partner_id.id if record.partner_id else False,
                'ticket_ids': [(4, record.id)],
            }
            maintenance = self.env['maintenance.request'].create(vals)
            record.write({'maintenance_request_ids': [(4, maintenance.id)]})
            
            record.message_post(body="🛠️ Se ha creado la solicitud de mantenimiento automáticamente.")
        
    # Campo para contar cuántos mantenimientos hay asociados
    maintenance_count = fields.Integer(compute='_compute_maintenance_count', string='Cantidad de Mantenimientos')

    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)

    def action_view_maintenance_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Solicitudes de Mantenimiento',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.maintenance_request_ids.ids)],
            'context': {'default_ticket_ids': [(4, self.id)]},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ticket_type_id'):
                ticket_type = self.env['helpdesk.ticket.type'].browse(vals.get('ticket_type_id'))
                if ticket_type.name == 'Calibración':
                    checklist = "<p><strong>Checklist Calibración:</strong><br/>1. Verificación inicial<br/>2. Limpieza de sensores<br/>3. Ajuste de ejes<br/>4. Prueba de movimiento<br/>5. Calibración de software<br/>6. Prueba de carga<br/>7. Reporte final</p>"
                    if 'description' not in vals or not vals['description']:
                        vals['description'] = checklist
                    elif 'Checklist Calibración' not in vals['description']:
                        vals['description'] += '<br/>' + checklist
        tickets = super(HelpdeskTicket, self).create(vals_list)
        tickets._schedule_warehouse_activity_for_envio_retiro()
        return tickets
        
    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        if 'ticket_type_id' in vals:
            for record in self:
                if record.ticket_type_id.name == 'Calibración':
                    checklist = "<p><strong>Checklist Calibración:</strong><br/>1. Verificación inicial<br/>2. Limpieza de sensores<br/>3. Ajuste de ejes<br/>4. Prueba de movimiento<br/>5. Calibración de software<br/>6. Prueba de carga<br/>7. Reporte final</p>"
                    if not record.description:
                        record.description = checklist
                    elif 'Checklist Calibración' not in record.description:
                        record.description += '<br/>' + checklist
            self._schedule_warehouse_activity_for_envio_retiro()
        return res

    def _get_warehouse_responsible_user(self):
        job = self.env.ref('custom_helpdesk_maintenance.job_responsable_inventario', raise_if_not_found=False)
        employee = False

        if job and job._name == 'hr.job':
            employee = self.env['hr.employee'].search([
                ('job_id', '=', job.id),
                ('active', '=', True),
                ('user_id', '!=', False),
            ], limit=1)

        if not employee:
            employee = self.env['hr.employee'].search([
                ('job_id.name', 'ilike', 'Responsable de inventario'),
                ('active', '=', True),
                ('user_id', '!=', False),
            ], limit=1)

        if employee and employee.user_id:
            return employee.user_id

        return self.env['res.users'].search([
            ('login', 'ilike', 'agustin'),
        ], limit=1)

    def _schedule_warehouse_activity_for_envio_retiro(self):
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        user = self._get_warehouse_responsible_user()
        if not activity_type or not user:
            return

        for ticket in self.filtered(lambda item: item.ticket_type_id.name == 'Envío/Retiro'):
            existing_activity = self.env['mail.activity'].search([
                ('res_model', '=', ticket._name),
                ('res_id', '=', ticket.id),
                ('activity_type_id', '=', activity_type.id),
                ('user_id', '=', user.id),
                ('summary', '=', 'Atender solicitud de Envío/Retiro'),
            ], limit=1)
            if existing_activity:
                continue

            ticket.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user.id,
                summary='Atender solicitud de Envío/Retiro',
                note='Ticket de tipo Envío/Retiro: coordinar la solicitud desde almacén.',
            )