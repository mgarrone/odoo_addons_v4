{
    'name': 'Automatiza Personalización Helpdesk y Mantenimiento',
    'version': '17.0.1.0.0',
    'category': 'Services/Helpdesk',
    'summary': ' Automatiza - Personaliza Solicitudes de mantenimiento y las relaciona con giras',
     'description': """
        Personalizaciones de Helpdesk y Mantenimiento para Automatiza.

        Cambios principales:
        - Relaciona tickets de helpdesk con equipos, giras y cuentas analíticas.
        - Permite crear solicitudes de mantenimiento desde tickets.
        - Relaciona tickets y solicitudes de mantenimiento en forma Many2many.
        - Agrega progreso, seguidores empleados, ticket padre y evidencias.
        - Mantiene checklist automático para tickets de tipo Calibración.
        - Agrega el campo x_resuelto_ia para indicar tickets resueltos exclusivamente con IA.
        - Crea una actividad automática para el responsable de almacén cuando el ticket
          es de tipo Envío/Retiro.
    """,
    'depends': ['helpdesk', 'maintenance', 'hr_maintenance', 'analytic', 'helpdesk_timesheet', 'custom_maintenance'],
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'data': [
        'data/helpdesk_data.xml',
        'data/maintenance_cron.xml',
        'views/helpdesk_ticket_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
    ],
    'installable': True,
    'application': False,
}
