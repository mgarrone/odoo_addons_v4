# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Campo de moneda para campos Monetary
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id',
        readonly=True,
        store=False
    )

    # Campos de Cronología
    x_studio_ingreso_consulta = fields.Date(string='Ingreso Consulta')
    x_studio_date_field_3vh_1jau2o5rh = fields.Date(string='Primer Llamada')
    x_studio_videollamada = fields.Date(string='Videollamada')
    x_studio_reunin_presencial = fields.Date(string='Reunión Presencial')
    x_studio_envo_presentacin = fields.Date(string='Envío Presentación')
    x_studio_envo_ffq = fields.Date(string='Envío FFQ')
    x_studio_cotizacin = fields.Date(string='Cotización')
    x_studio_firma_cotizacin = fields.Date(string='Firma Cotización')
    x_studio_acta_ec = fields.Date(string='Acta EC')
    x_studio_vencimiento = fields.Date(string='Vencimiento')
    x_studio_visita_de_cortesa = fields.Date(string='Visita de Cortesía')
    x_fecha_torta_aniversario = fields.Date(string='Envío torta aniversario')
    x_fecha_foto_aniversario = fields.Date(string='Foto aniversario')

    # Campos de Información adicional
    x_proyecto_id = fields.Many2one(
        'project.project',
        string='Proyecto',
        compute='_compute_x_proyecto_id',
        readonly=True,
        copy=False,
        help='Proyecto vinculado a esta oportunidad (se completa al seleccionar la oportunidad en el proyecto).'
    )

    def _compute_x_proyecto_id(self):
        if not self:
            return
        projects = self.env['project.project'].search([
            ('opportunity_id', 'in', self.ids),
        ])
        project_by_opportunity = {
            project.opportunity_id.id: project for project in projects
        }
        for lead in self:
            lead.x_proyecto_id = project_by_opportunity.get(lead.id, False)
    x_complejidad = fields.Selection([
        ('bajo', 'Bajo'),
        ('normal', 'Normal'),
        ('alto', 'Alto'),
    ], string='Complejidad')
    x_contacto_ids = fields.Many2many(
        'res.partner',
        'crm_lead_x_contacto_rel',
        'lead_id',
        'partner_id',
        string='Contactos de la empresa',
        domain="[('parent_id', '=', partner_id)]"
    )
    x_responsable_comercial_id = fields.Many2one(
        'res.users',
        string='Responsable comercial'
    )
    x_responsable_proyecto_id = fields.Many2one(
        'res.users',
        string='Responsable de proyecto'
    )
    x_id_cliente = fields.Integer(
        string='ID Cliente',
        related='partner_id.id',
        readonly=True
    )
    x_canal_de_ingreso = fields.Char(
        string='Canal de ingreso'
    )
    
    # Campos de Datos de Cotización
    x_studio_cotizacin_bd = fields.Char(string='Cotización BD')
    x_studio_char_field_4bc_1jbo2kegr = fields.Char(string='Url Cotización')
    x_studio_modelo_comercial_1 = fields.Selection([
        ('bd_argentina', 'Bd Argentina'),
        ('atza_uy', 'Automatiza Uruguay'),
        ('otro', 'Otro')
    ], string='Modelo Comercial')
    x_studio_tipo_de_cotizacin = fields.Selection([
        ('robot', 'Robot'),
        ('refit', 'Refit'),
        ('otro', 'Otro')
    ], string='Tipo de Cotización')
    x_studio_hardware = fields.Monetary(string='Hardware', currency_field='currency_id')
    x_studio_servicio = fields.Monetary(string='Servicio', currency_field='currency_id')
    x_studio_descuento_aplicado_ = fields.Float(string='Descuento Aplicado', digits=(16, 2))
    x_studio_total_neto = fields.Monetary(string='Total Neto', currency_field='currency_id')
    x_studio_nmero_de_venta = fields.Integer(string='Número de Venta')
    x_studio_nmero_de_cliente = fields.Integer(string='Número de Cliente')
    x_studio_nmero_de_instalacin = fields.Integer(string='Número de Instalación')
    x_cantidad_robots = fields.Integer(string='Cantidad de robots')
    x_detalle_de_equipos = fields.One2many(
        'x_lista_de_robots',
        'opportunity_id',
        string='Detalle de equipos cotizados'
    )
    x_cotizaciones = fields.One2many(
        'sale.order',
        'opportunity_id',
        string='Cotizaciones creadas'
    )

    # Campos de Producto Cotizado
    x_studio_producto = fields.Selection([
        ('smart', 'Smart'),
        ('vmax', 'Vmax'),
        ('otro', 'Otro')
    ], string='Producto')
    x_studio_alto = fields.Float(string='Alto', digits=(16, 2))
    x_studio_ancho = fields.Float(string='Ancho', digits=(16, 2))
    x_studio_largo = fields.Float(string='Largo', digits=(16, 2))
    x_studio_salidas = fields.Integer(string='Salidas')
    x_studio_capacidad_mnima_1 = fields.Integer(string='Capacidad Mínima')
    x_studio_capacidad_mxima = fields.Integer(string='Capacidad Máxima')
    x_studio_cinta_de_transporte_1 = fields.Float(string='Cinta de Transporte', digits=(16, 2))
    x_studio_easy_load_1 = fields.Integer(string='Easy Load')
    x_studio_espirales_1 = fields.Integer(string='Espirales')
    x_studio_vidrios_laterales_1 = fields.Integer(string='Vidrios Laterales')
    x_studio_vidrios_fondo = fields.Integer(string='Vidrios Fondo')
    x_studio_vidrios_piso = fields.Integer(string='Vidrios Piso')
    x_studio_ubicacin = fields.Selection([
        ('planta_baja', 'Planta Baja'),
        ('planta_alta', 'Planta Alta'),
        ('subsuelo', 'Subsuelo'),
         ('entrepiso', 'Entrepiso'),
        ('otra', 'Otra')
    ], string='Ubicación')
    x_studio_software_gestion_text = fields.Char(string='Software de Gestión')
    x_studio_otro_complemento = fields.Html(string='Otros Complementos')
   
