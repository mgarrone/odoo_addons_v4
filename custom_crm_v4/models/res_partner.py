# -*- coding: utf-8 -*-
from odoo import models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
        domain = list(domain or [])
        if name and self.env.context.get('search_by_company_name'):
            search_domain = ['|', ('company_name', operator, name), ('name', operator, name)]
            domain = expression.AND([domain, search_domain])
            return self._search(domain, limit=limit, order=order)
        return super()._name_search(
            name=name,
            domain=domain,
            operator=operator,
            limit=limit,
            order=order,
        )
