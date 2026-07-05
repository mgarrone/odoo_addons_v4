{
    'name': 'Automatiza Proyecto y Lista de Robots',
    'version': '17.0.2.0.1',
    'category': 'Project',
    'summary': 'Relación entre proyectos, oportunidades y robots propuestos',
    'description': """
        Personalizaciones de Proyecto para Automatiza.

        Cambios principales:
        - Agrega campos en proyectos: opportunity_id, bd_robot_code, bd_pid y robot_scenario_ids.
        - Crea el modelo x_lista_de_robots para administrar escenarios de productos/robots.
        - Crea etiquetas para escenarios mediante x_lista_de_robots_tag.
        - Agrega campos limpios en escenarios: project_id, opportunity_id, product_id, scenario,
          ffq_url, height, length, width, min_capacity, max_capacity, conveyor_belt,
          deflectors, easy_load, easy_load_buffer, spirals, second_picking_arm,
          second_input_belt, refrigeration_module, cleaning_module, side_glasses,
          back_glass, floor_glass, location, other_complement y comments.
        - Agrega la sección Detalle de Equipos en el formulario de proyecto.
        - Agrega el menú Configuración > Escenarios de Productos.
        - Sincroniza automáticamente la oportunidad del proyecto con sus escenarios.
        - Expone project_ids en oportunidades como relación inversa de opportunity_id.
        - Valida dimensiones y configuraciones permitidas para productos SMART y VMAX.
    """,
    'author': 'Automatiza S.A.',
    'website': 'https://www.automatizasa.com',
    'license': 'LGPL-3',
    'depends': ['project', 'crm', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/lista_robots_views.xml',
        'views/project_project_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
