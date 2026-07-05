# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        copy=False,
        ondelete='set null',
        help='Oportunidad comercial relacionada con este proyecto.'
    )
    bd_robot_code = fields.Char(string='BD Código de robot')
    bd_pid = fields.Integer(string='BD PID')
    robot_scenario_ids = fields.One2many(
        'x_lista_de_robots',
        'project_id',
        string='Detalle de equipos'
    )

    _sql_constraints = [
        (
            'opportunity_id_uniq',
            'unique (opportunity_id)',
            'La oportunidad ya está vinculada a otro proyecto.'
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        projects.mapped('robot_scenario_ids')._sync_opportunity_from_project()
        projects._refresh_linked_opportunities()
        return projects

    def write(self, vals):
        previous_opportunities = (
            self.mapped('opportunity_id') if 'opportunity_id' in vals
            else self.env['crm.lead']
        )
        res = super().write(vals)
        if 'opportunity_id' in vals:
            self.mapped('robot_scenario_ids')._sync_opportunity_from_project()
            (previous_opportunities | self.mapped('opportunity_id'))._refresh_x_proyecto_id()
        return res

    def _refresh_linked_opportunities(self):
        self.mapped('opportunity_id')._refresh_x_proyecto_id()


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_ids = fields.One2many(
        'project.project',
        'opportunity_id',
        string='Proyectos vinculados',
    )

    def _refresh_x_proyecto_id(self):
        if 'x_proyecto_id' not in self._fields:
            return
        self.invalidate_recordset(['x_proyecto_id'])
        self._compute_x_proyecto_id()
