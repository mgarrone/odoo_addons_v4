# -*- coding: utf-8 -*-
import unicodedata

from odoo import api, models


def _strip_accents(value):
    text = unicodedata.normalize('NFKD', value or '')
    return ''.join(ch for ch in text if not unicodedata.combining(ch)).lower()


ENVIO_RETIRO_ACTIVITY_SUMMARY = 'Atender solicitud de Envío/Retiro'
ENVIO_RETIRO_SUMMARY_NORM = _strip_accents(ENVIO_RETIRO_ACTIVITY_SUMMARY)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def _is_envio_retiro_activity_vals(self, vals):
        summary_norm = _strip_accents(vals.get('summary') or '')
        note_norm = _strip_accents(vals.get('note') or '')
        is_envio_summary = (
            ENVIO_RETIRO_SUMMARY_NORM in summary_norm
            or 'atender solicitud de envio/retiro' in summary_norm
            or (
                'envio/retiro' in note_norm
                and 'coordinar la solicitud desde almacen' in note_norm
            )
        )
        if not is_envio_summary:
            return False

        res_model = vals.get('res_model')
        if res_model == 'helpdesk.ticket':
            return True
        res_model_id = vals.get('res_model_id')
        if res_model_id:
            model = self.env['ir.model'].browse(res_model_id)
            return model.model == 'helpdesk.ticket'
        # activity_schedule a veces manda solo res_id + res_model_id
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """
        Bloquea actividades Envío/Retiro si no hay Responsable de inventario
        (XML ID + usuario Odoo). Si hay responsable, fuerza ese user_id.
        """
        Ticket = self.env['helpdesk.ticket']
        responsible = Ticket._get_warehouse_responsible_user()
        filtered_vals = []
        for vals in vals_list:
            if self._is_envio_retiro_activity_vals(vals):
                if not responsible:
                    continue
                vals = dict(vals, user_id=responsible.id)
            filtered_vals.append(vals)
        if not filtered_vals:
            return self.browse()
        return super().create(filtered_vals)
