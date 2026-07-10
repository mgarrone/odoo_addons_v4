from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    robot_out_of_service = fields.Boolean(string='Robot Fuera de Servicio', default=False)