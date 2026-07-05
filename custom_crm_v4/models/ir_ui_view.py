# -*- coding: utf-8 -*-
from odoo import api, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def action_cleanup_automatiza_crm_legacy_views(self):
        legacy_xmlids = [
            'custom_crm_v3.crm_lead_view_form_custom',
            'modulo_crm_v3.crm_lead_view_form_custom',
        ]

        legacy_views = self.env['ir.ui.view']
        for xmlid in legacy_xmlids:
            view = self.env.ref(xmlid, raise_if_not_found=False)
            if view:
                legacy_views |= view

        current_view = self.env.ref(
            'custom_crm_v4.crm_lead_view_form_custom',
            raise_if_not_found=False
        )
        current_view_ids = current_view.ids if current_view else []

        legacy_views |= self.search([
            ('model', '=', 'crm.lead'),
            ('name', '=', 'crm.lead.form.custom'),
            ('id', 'not in', current_view_ids),
        ])

        legacy_views.filtered('active').write({'active': False})
        return True
