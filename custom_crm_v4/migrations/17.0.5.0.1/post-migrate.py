import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    if 'x_proyecto_id' not in env['crm.lead']._fields:
        return

    linked_opportunities = env['project.project'].search([
        ('opportunity_id', '!=', False),
    ]).mapped('opportunity_id')
    if linked_opportunities:
        linked_opportunities._refresh_x_proyecto_id()
        _logger.info(
            'Refreshed x_proyecto_id for %s linked opportunities.',
            len(linked_opportunities),
        )
