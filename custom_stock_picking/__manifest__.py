{
    'name': 'Automatiza - Equipo Destino en Transferencias',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Añade el campo Equipo Destino a las transferencias de inventario',
    'description': """
        Personalizaciones de Inventario para Automatiza.

        Cambios principales:
        - Agrega x_mat_equipo_destino para relacionar transferencias con equipos de mantenimiento.
        - Agrega x_mat_empleado_destino para registrar a quién se entrega la transferencia.
        - Agrega x_fecha_recepcion para registrar la fecha de recepción de la transferencia.
        - Muestra los campos personalizados en el formulario de transferencias.
    """,
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'maintenance'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
