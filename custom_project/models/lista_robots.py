# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ListaRobotsTag(models.Model):
    _name = 'x_lista_de_robots_tag'
    _description = 'Etiqueta de lista de robots'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'La etiqueta ya existe.'),
    ]


class ListaRobots(models.Model):
    _name = 'x_lista_de_robots'
    _description = 'Escenario de producto'
    _rec_name = 'name'
    _order = 'project_id, scenario, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        default='Ej: Rowa 1 - Farmacia X'
    )
    tag_ids = fields.Many2many(
        'x_lista_de_robots_tag',
        'x_lista_de_robots_tag_rel',
        'robot_id',
        'tag_id',
        string='Etiquetas'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto',
        ondelete='cascade'
    )
    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        ondelete='set null',
        readonly=True
    )
    product_id = fields.Many2one('product.product', string='Producto')
    scenario = fields.Integer(string='Escenario')
    ffq_url = fields.Char(string='FFQ')
    height = fields.Float(string='Alto', digits=(16, 2))
    length = fields.Float(string='Largo', digits=(16, 2))
    width = fields.Float(string='Ancho', digits=(16, 2))
    min_capacity = fields.Integer(string='Capacidad mínima')
    max_capacity = fields.Integer(string='Capacidad máxima')
    conveyor_belt = fields.Float(string='Cinta de transporte', digits=(16, 2))
    deflectors = fields.Integer(string='Deflectores')
    easy_load = fields.Boolean(string='Easy Load')
    easy_load_buffer = fields.Float(string='Buffer Easy Load', digits=(16, 2))
    spirals = fields.Integer(string='Espirales')
    second_picking_arm = fields.Boolean(string='Segundo brazo de pickeo')
    second_input_belt = fields.Boolean(string='Segunda cinta de ingreso')
    refrigeration_module = fields.Boolean(string='Módulo de refrigeración')
    cleaning_module = fields.Boolean(string='Módulo de limpieza', default=True)
    side_glasses = fields.Integer(string='Vidrios laterales')
    back_glass = fields.Boolean(string='Vidrios fondo')
    floor_glass = fields.Boolean(string='Vidrios piso')
    location = fields.Selection([
        ('planta_baja', 'Planta baja'),
        ('subsuelo', 'Subsuelo'),
        ('planta_alta', 'Planta alta'),
        ('entre_piso', 'Entre piso'),
        ('otra', 'Otra'),
    ], string='Ubicación')
    other_complement = fields.Text(string='Otro complemento')
    comments = fields.Text(string='Comentarios')

    @api.model_create_multi
    def create(self, vals_list):
        robots = super().create(vals_list)
        robots._sync_opportunity_from_project()
        return robots

    def write(self, vals):
        res = super().write(vals)
        if 'project_id' in vals:
            self._sync_opportunity_from_project()
        return res

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self._sync_opportunity_from_project()

    @api.onchange('product_id', 'width')
    def _onchange_robot_width(self):
        for robot in self:
            if robot._is_smart() or robot._is_vmax():
                robot.width = 1.63

    def _sync_opportunity_from_project(self):
        for robot in self:
            if robot.project_id:
                robot.opportunity_id = robot.project_id.opportunity_id

    @api.constrains(
        'product_id',
        'height',
        'length',
        'width',
        'easy_load',
        'easy_load_buffer',
        'second_picking_arm',
    )
    def _check_robot_dimensions(self):
        for robot in self:
            if not robot.product_id:
                continue
            if robot._is_smart():
                robot._validate_smart()
            elif robot._is_vmax():
                robot._validate_vmax()

    def _is_smart(self):
        self.ensure_one()
        return self.product_id.display_name == 'Robot BD ROWA SMART'

    def _is_vmax(self):
        self.ensure_one()
        return self.product_id.display_name == 'Robot BD ROWA VMAX'

    def _validate_length_multiple(self, length, rule_name):
        if round((length or 0.0) % 0.5, 2) != 0:
            raise ValidationError(
                f'REGLA {rule_name}: El largo debe aumentar de a 0.5m '
                '(Ej: 3.0, 3.5, 4.0...).'
            )

    def _validate_easy_load_buffer(self, allowed_values, product_name):
        self.ensure_one()
        if not self.easy_load:
            return
        easy_load = round(float(self.easy_load_buffer or 0.0), 2)
        if easy_load not in allowed_values:
            values = ', '.join(str(value) for value in allowed_values)
            raise ValidationError(
                f'El buffer del Easy Load solo puede ser {values} metros para '
                f'{product_name} (ingresaste: {easy_load})'
            )

    def _validate_smart(self):
        self.ensure_one()
        height = round(float(self.height or 0.0), 1)
        if height not in [2.3, 2.5, 2.8]:
            raise ValidationError(
                f'REGLA SMART: El alto debe ser exactamente 2.3, 2.5 o 2.8 metros '
                f'(ingresaste: {height})'
            )

        length = float(self.length or 0.0)
        if length < 3.0 or length > 6.5:
            raise ValidationError(
                f'REGLA SMART: El largo debe estar entre 3.0 y 6.5 metros. '
                f'(ingresaste: {length})'
            )
        self._validate_length_multiple(length, 'SMART')
        self._validate_easy_load_buffer([1, 1.5, 2, 2.5, 3, 4], 'SMART')

    def _validate_vmax(self):
        self.ensure_one()
        height = round(float(self.height or 0.0), 2)
        if height < 1.70 or height > 3.50:
            raise ValidationError(
                f'REGLA VMAX: El alto debe estar entre 1.70 y 3.50 metros '
                f'(ingresaste: {height})'
            )

        height_cm = int(round(height * 100))
        if height_cm % 5 != 0:
            raise ValidationError(
                'REGLA VMAX: El alto debe configurarse en saltos exactos de 5 cm '
                f'(ej: 1.70, 1.75, 1.80, etc.). Ingresaste: {height} metros.'
            )

        length = float(self.length or 0.0)
        if self.second_picking_arm:
            if length < 6.5 or length > 15:
                raise ValidationError(
                    'REGLA VMAX: El largo debe estar entre 6.5 y 15 metros si se '
                    f'elige segundo brazo de pickeo. (ingresaste: {length})'
                )
        elif length < 3.0 or length > 15:
            raise ValidationError(
                f'REGLA VMAX: El largo debe estar entre 3.0 y 15 metros. '
                f'(ingresaste: {length})'
            )

        self._validate_length_multiple(length, 'VMAX')
        self._validate_easy_load_buffer([1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8], 'VMAX')
