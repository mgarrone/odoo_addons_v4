{
    'name': 'Giras',
    'version': '17.0.1.0.0',
    'category': 'Maintenance',
    'summary': 'Automatiza - Gestión de Giras para equipos de mantenimiento',
    'description': """
        Módulo para gestionar giras que pueden ser asignadas a equipos de mantenimiento.
    """,
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'depends': ['maintenance'],
    'data': [
        'data/giras_data.xml',
        'views/giras_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
