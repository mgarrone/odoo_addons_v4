# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        copy=False,
        ondelete='set null',
        help='Oportunidad comercial relacionada con este proyecto.',
    )
    bd_robot_code = fields.Char(string='BD Código de robot')
    bd_pid = fields.Integer(string='BD PID')
    robot_scenario_ids = fields.One2many(
        'x_lista_de_robots',
        'project_id',
        string='Detalle de equipos',
    )
    task_count = fields.Integer(
        string='Tareas',
        compute='_compute_task_count',
    )

    _sql_constraints = [
        (
            'opportunity_id_uniq',
            'unique (opportunity_id)',
            'La oportunidad ya está vinculada a otro proyecto.',
        ),
    ]

    @api.model
    def _get_default_stage_ids(self):
        """Devuelve los IDs de las etapas predeterminadas del módulo."""
        xml_ids = [
            'custom_project.project_stage_a_realizar',
            'custom_project.project_stage_en_proceso',
            'custom_project.project_stage_finalizadas',
            'custom_project.project_stage_canceladas',
        ]
        stage_ids = []
        for xml_id in xml_ids:
            stage = self.env.ref(xml_id, raise_if_not_found=False)
            if stage:
                stage_ids.append(stage.id)
        return stage_ids

    @api.model_create_multi
    def create(self, vals_list):
        default_stage_ids = self._get_default_stage_ids()
        projects = super().create(vals_list)

        # Garantizamos que todo proyecto nuevo quede vinculado a las etapas base.
        if default_stage_ids:
            for project in projects:
                missing_stage_ids = [sid for sid in default_stage_ids if sid not in project.type_ids.ids]
                if missing_stage_ids:
                    project.write({'type_ids': [(4, sid) for sid in missing_stage_ids]})

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

    @api.depends('name')
    def _compute_task_count(self):
        super()._compute_task_count()
        Task = self.env['project.task']
        grouped = Task.read_group(
            [('project_id', 'in', self.ids)],
            ['project_id'],
            ['project_id'],
        )
        counts = {item['project_id'][0]: item['project_id_count'] for item in grouped if item.get('project_id')}
        for project in self:
            project.task_count = counts.get(project.id, 0)

    def action_open_project_tasks(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Tareas',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'views': [
                (self.env.ref('project.view_task_kanban').id, 'kanban'),
                (self.env.ref('project.view_task_tree').id, 'tree'),
                (self.env.ref('project.view_task_form2').id, 'form'),
            ],
            'target': 'current',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'search_default_project_id': self.id,
                'group_by': 'stage_id',
                'default_group_by': 'stage_id',
            },
        }
        return action


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
