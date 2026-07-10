# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

def post_init_hook(cr, registry):
    """Asigna las etapas predeterminadas a todos los proyectos existentes."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    Project = env['project.project']

    stage_ids = Project._get_default_stage_ids()
    if not stage_ids:
        return

    all_projects = Project.search([])
    if all_projects:
        commands = [(4, sid) for sid in stage_ids]
        for project in all_projects:
            project.write({'type_ids': commands})
            
        # Forzamos a las etapas a actualizar su relación inversa en el caché de Odoo
        stages = env['project.task.type'].browse(stage_ids)
        stages.modified(['project_ids'])