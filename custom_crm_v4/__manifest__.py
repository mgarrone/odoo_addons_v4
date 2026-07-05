{
    'name': 'Automatiza CRM v4 Campos Personalizados',
    'version': '17.0.5.0.1',
    'category': 'Sales/CRM',
    'summary': 'Automatiza - Campos personalizados para oportunidades de CRM',
    'description': """
        Personalizaciones CRM v4 para Automatiza.

        Cambios principales:
        - Agrega campos nuevos en oportunidades: x_proyecto_id (calculado desde el proyecto
          que seleccione la oportunidad), x_complejidad,
          x_contacto_ids, x_responsable_comercial_id, x_responsable_proyecto_id,
          x_fecha_torta_aniversario, x_fecha_foto_aniversario y x_cantidad_robots.
        - Agrega x_detalle_de_equipos como relación One2many a x_lista_de_robots
          mediante el campo limpio opportunity_id.
        - Agrega x_cotizaciones como relación One2many a sale.order mediante opportunity_id.
        - Mantiene campos legacy x_studio_* existentes para compatibilidad con datos
          y vistas anteriores de CRM.
        - Reorganiza el formulario de oportunidad: Información adicional, Cronología
          y Configuración de Equipos.
        - Mueve datos de cotización y valores comerciales a Configuración de Equipos.
        - Agrega contactos de la empresa como lista editable filtrada por cliente.
        - Limpia/desactiva vistas heredadas legacy de custom_crm_v3/modulo_crm_v3
          para evitar pestañas y bloques duplicados.
        - Agrega búsqueda de clientes por razón social/company_name.
    """,
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'depends': ['crm', 'sale', 'sale_crm', 'project', 'custom_project'],
    'data': [
        'data/cleanup_legacy_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
