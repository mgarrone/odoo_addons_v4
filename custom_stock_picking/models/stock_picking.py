# -*- coding: utf-8 -*-
from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_mat_equipo_destino = fields.Many2one(
        'maintenance.equipment',
        string='Equipo destino',
        help='Equipo de mantenimiento al que se destina esta entrega'       

    )

    x_mat_empleado_destino = fields.Many2one(
        'hr.employee',
        string='Entregado a',
        help='Empleado al que se entrega'

    )    

    x_fecha_recepcion = fields.Date(
        string='Fecha de recepción',
        help='Fecha en la que se recibió la transferencia.'
    )
