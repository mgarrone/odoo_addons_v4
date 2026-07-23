{
    'name': 'Automatiza Personalización Helpdesk y Mantenimiento',
    'version': '17.0.1.0.7',
    'category': 'Services/Helpdesk',
    'summary': ' Automatiza - Personaliza Solicitudes de mantenimiento y Tickets y las relaciona con giras',
     'description': """
<h3>Módulo de Personalización Helpdesk y Mantenimiento</h3>
<p>Este módulo integra de manera nativa y automatizada los flujos entre la mesa de ayuda (Helpdesk) y el Mantenimiento ademas relaciona con giras.</p>
<h4>Características y Últimos Cambios:</h4>
<ul>
    <li><b>Helpdesk y Mantenimiento:</b> Relación de muchos-a-muchos entre tickets y solicitudes de mantenimiento, con botones inteligentes (Smart Buttons) para rápida navegación.</li>
    <li><b>Alertas Visuales:</b> Implementación de carteles de advertencia (Banners) y cintas (Ribbons) en los formularios para notificar instantáneamente si el <i>Robot se encuentra fuera de servicio</i> o si el <i>Soporte está suspendido</i>.</li>
    <li><b>Automatización de Estados Kanban:</b> Nueva acción planificada (Cron Job) que revisa a diario y cambia automáticamente el estado de los mantenimientos a 'Bloqueado' (si el robot falla) o 'Hecho' (si la fecha programada expiró).</li>
    <li><b>Checklist Automático:</b> Inserción automática de pasos de calibración en la descripción del ticket de Helpdesk.</li>
    <li><b>Envío/Retiro:</b> Actividad automática solo si hay empleado con puesto _hr.job_.stockManager_extID y usuario Odoo. Prevalece sobre custom_helpdesk_maintenanceV0.</li>
    <li><b>Interfaz Optimizada:</b> Limpieza y organización de las vistas de los formularios para mostrar de manera clara los clientes, la gira asociada y el progreso.</li>
</ul>
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