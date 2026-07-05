{
    'name': 'Automatiza Modulo Mantenimiento Campos Personalizados - MAINTENANCE',
    'version': '17.0.1.0.0',
    'category': 'Maintenance',
    'summary': ' Automatiza - Vincula equipos de mantenimiento con oportunidades CRM y cuentas analíticas',
    'description': """
        Módulo que extiende los equipos de mantenimiento para referenciar
        oportunidades de CRM y cuentas analíticas, gestión de giras y datos técnicos de equipos.
    """,
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'depends': ['maintenance', 'analytic', 'crm', 'product', 'custom_giras'],
    'data': [
        'views/maintenance_equipment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

