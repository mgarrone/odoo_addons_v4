# -*- coding: utf-8 -*-
import unicodedata

from odoo import api, models


def _strip_accents(value):
    text = unicodedata.normalize('NFKD', value or '')
    return ''.join(ch for ch in text if not unicodedata.combining(ch)).lower().strip()


# Solo esta actividad automática (no otras del sistema)
ENVIO_RETIRO_ACTIVITY_SUMMARY = 'Atender solicitud de Envío/Retiro'
ENVIO_RETIRO_SUMMARY_NORM = _strip_accents(ENVIO_RETIRO_ACTIVITY_SUMMARY)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def _is_envio_retiro_auto_activity_vals(self, vals):
        """
        True SOLO para la actividad automática de Envío/Retiro en helpdesk.ticket.
        No aplica a ninguna otra actividad del sistema.
        """
        summary_norm = _strip_accents(vals.get('summary') or '')
        if summary_norm != ENVIO_RETIRO_SUMMARY_NORM:
            return False

        res_model = vals.get('res_model')
        if res_model == 'helpdesk.ticket':
            return True

        res_model_id = vals.get('res_model_id')
        if res_model_id:
            model = self.env['ir.model'].browse(res_model_id)
            return bool(model) and model.model == 'helpdesk.ticket'

        return False

    @api.model_create_multi
    def create(self, vals_list):
        """
        Interviene únicamente en actividades con summary
        'Atender solicitud de Envío/Retiro' sobre helpdesk.ticket.
        El resto de actividades del sistema pasan sin cambios.
        """
        Ticket = self.env['helpdesk.ticket']
        responsible = None
        filtered_vals = []

        for vals in vals_list:
            if not self._is_envio_retiro_auto_activity_vals(vals):
                filtered_vals.append(vals)
                continue

            # Lazy: solo consultar responsable si aparece esta actividad
            if responsible is None:
                responsible = Ticket._get_warehouse_responsible_user()

            if not responsible:
                # Sin responsable válido: no crear esta actividad automática
                continue

            vals = dict(vals, user_id=responsible.id)
            filtered_vals.append(vals)

        if not filtered_vals:
            return self.browse()
        return super().create(filtered_vals)
