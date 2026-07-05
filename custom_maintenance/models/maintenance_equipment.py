# -*- coding: utf-8 -*-
from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    # Relaciones Many2one
    x_mat_cuenta_analitica = fields.Many2one(
        'account.analytic.account',
        string='Cuenta analítica',
    )
    x_mat_oportunidad = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
    )
    x_mat_modelo = fields.Many2one(
        'product.template',
        string='Modelo',
    )
    x_mat_gira = fields.Many2one(
        'maintenance.giras',
        string='Gira',
    )

    # Campos de dimensiones y técnicos
    x_mat_alto = fields.Float(string='Alto')
    x_mat_largo = fields.Float(string='Largo')
    x_mat_ancho = fields.Float(string='Ancho')
    x_mat_espirales = fields.Integer(string='Espirales')
    x_mat_segundo_brazo_de_pickeo = fields.Boolean(string='Segundo brazo de pickeo')
    x_mat_modulo_refrigeracion = fields.Boolean(string='Módulo de refrigeración')
    x_mat_modulo_limpieza = fields.Boolean(string='Módulo de limpieza')

    # Campos de Vidrios
    x_mat_vidrios_laterales = fields.Integer(string='Vidrios laterales')
    x_mat_vidrios_piso = fields.Boolean(string='Vidrios piso')
    x_mat_vidrios_fondo = fields.Boolean(string='Vidrios fondo')

    # Logística y Ubicación
    x_mat_easy_load = fields.Boolean(string='Easy Load')
    x_mat_buffer_easy_load = fields.Float(string='Buffer Easy Load (m)')
    x_mat_transporte = fields.Integer(string='Transporte')
    x_mat_ubicacion = fields.Char(string='Ubicación')
