from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Constantes para el puesto de Responsable de inventario
STOCK_MANAGER_JOB_EXT = {'module': '_hr.job_', 'name': 'stockManager_extID'}


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

    @api.model
    def _register_hook(self):
        """
        Fuerza prioridad sobre custom_helpdesk_maintenanceV0 (u otras herencias):
        reescribe en el registro los métodos de actividad Envío/Retiro.
        """
        super()._register_hook()
        Model = self.env.registry[self._name]

        Model._safe_get_external_record_id = HelpdeskTicket._safe_get_external_record_id
        Model._get_stock_manager_job = HelpdeskTicket._get_stock_manager_job
        Model._get_warehouse_responsible_user = HelpdeskTicket._get_warehouse_responsible_user
        Model._get_envio_retiro_activities = HelpdeskTicket._get_envio_retiro_activities
        Model._automatiza_sync_envio_retiro_activity = HelpdeskTicket._automatiza_sync_envio_retiro_activity
        Model._schedule_warehouse_activity_for_envio_retiro = (
            HelpdeskTicket._automatiza_sync_envio_retiro_activity
        )
        Model.activity_schedule = HelpdeskTicket.activity_schedule

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
        tickets._automatiza_sync_envio_retiro_activity()
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
            self._automatiza_sync_envio_retiro_activity()
        return res

    @api.model
    def _safe_get_external_record_id(self, module, name, model=None):
        xmlid = '%s.%s' % (module, name)
        record = self.env.ref(xmlid, raise_if_not_found=False)
        if record and (not model or record._name == model):
            return record.id

        domain = [
            ('module', '=', module),
            ('name', '=', name),
        ]
        if model:
            domain.append(('model', '=', model))
        ext_id = self.env['ir.model.data'].sudo().search(domain, limit=1)
        return ext_id.res_id if ext_id else False

    @api.model
    def _get_stock_manager_job(self):
        """Puesto 'Responsable de inventario' vía STOCK_MANAGER_JOB_EXT."""
        job_id = self._safe_get_external_record_id(
            STOCK_MANAGER_JOB_EXT['module'],
            STOCK_MANAGER_JOB_EXT['name'],
            model='hr.job',
        )
        if not job_id:
            return self.env['hr.job']
        job = self.env['hr.job'].browse(job_id)
        return job if job.exists() else self.env['hr.job']

    def _get_warehouse_responsible_user(self):
        """
        Solo el usuario del empleado con el puesto de STOCK_MANAGER_JOB_EXT.
        Sin fallbacks: si no hay nadie con ese puesto + usuario Odoo, retorna vacío.
        """
        job = self._get_stock_manager_job()
        if not job:
            return self.env['res.users']

        employee = self.env['hr.employee'].search([
            ('job_id', '=', job.id),
            ('active', '=', True),
            ('user_id', '!=', False),
        ], limit=1)
        if not employee or not employee.user_id:
            return self.env['res.users']
        return employee.user_id

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        """
        Intercepta la programación de la actividad Envío/Retiro.
        Sin responsable (XML ID): no crea nada.
        Con responsable: fuerza la asignación a ese usuario.
        """
        summary_norm = (summary or '')
        try:
            from odoo.addons.custom_helpdesk_maintenance.models.mail_activity import _strip_accents
            is_envio = 'atender solicitud de envio/retiro' in _strip_accents(summary_norm)
        except Exception:
            is_envio = 'Envío/Retiro' in (summary or '') or 'Envio/Retiro' in (summary or '')
        if is_envio:
            user = self._get_warehouse_responsible_user()
            if not user:
                return self.env['mail.activity']
            act_values = dict(act_values, user_id=user.id)
        return super().activity_schedule(
            act_type_xmlid=act_type_xmlid,
            date_deadline=date_deadline,
            summary=summary,
            note=note,
            **act_values,
        )

    def _get_envio_retiro_activities(self):
        """Actividades automáticas de Envío/Retiro sobre estos tickets."""
        self.ensure_one()
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return self.env['mail.activity']
        return self.env['mail.activity'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', activity_type.id),
            ('summary', 'ilike', 'Atender solicitud de Env%/Retiro'),
        ])

    def _automatiza_sync_envio_retiro_activity(self):
        """
        Sincroniza la actividad Envío/Retiro:
        - Con responsable (XML ID + usuario Odoo): actividad solo para ese usuario.
        - Sin responsable: no crea nada y elimina actividades automáticas previas.
        """
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return

        user = self._get_warehouse_responsible_user()

        for ticket in self.filtered(lambda item: item.ticket_type_id.name == 'Envío/Retiro'):
            activities = ticket._get_envio_retiro_activities()

            if not user:
                activities.unlink()
                continue

            wrong_activities = activities.filtered(lambda act: act.user_id != user)
            if wrong_activities:
                wrong_activities.unlink()

            remaining = ticket._get_envio_retiro_activities().filtered(
                lambda act: act.user_id == user
            )
            if remaining:
                continue

            ticket.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user.id,
                summary='Atender solicitud de Envío/Retiro',
                note='Ticket de tipo Envío/Retiro: coordinar la solicitud desde almacén.',
            )

    def _schedule_warehouse_activity_for_envio_retiro(self):
        """Compatibilidad: redirige a la sincronización correcta (sin fallbacks)."""
        return self._automatiza_sync_envio_retiro_activity()
