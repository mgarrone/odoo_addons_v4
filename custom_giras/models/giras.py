# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Giras(models.Model):
    _name = 'maintenance.giras'
    _description = 'Giras'
    _order = 'name desc'

    name = fields.Char(
        string='Nombre',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('maintenance.giras') or 'Nueva Gira',
    )
    
    description = fields.Text(
        string='Descripción',
    )
    
    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'Nueva Gira':
            vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.giras') or 'Nueva Gira'
        return super(Giras, self).create(vals)
