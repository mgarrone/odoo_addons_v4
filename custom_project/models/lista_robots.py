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


# Se mantiene la lógica basada en IDs externos para distinguir SMART/VMAX.
# Si no existen, se hace fallback por nombre para no bloquear la carga del formulario.
VMAX_EXT = {'module': '_product.template_', 'name': 'VMAX_extID'}
SMART_EXT = {'module': '_product.template_', 'name': 'Smart_extID'}
ROBOTS_CATEG_EXT = {'module': '_product.category_', 'name': 'robots_extID'}


class ListaRobots(models.Model):
    _name = 'x_lista_de_robots'
    _description = 'Escenario de producto'
    _rec_name = 'name'
    _order = 'project_id, scenario, name'

    @api.model
    def _safe_get_external_record_id(self, module, name, model=None):
        """Resuelve un XML ID de forma segura (env.ref + ir.model.data)."""
        xmlid = '%s.%s' % (module, name)
        record = self.env.ref(xmlid, raise_if_not_found=False)
        if record and (not model or record._name == model):
            return record.id

        domain = [
            ('module', '=', module),
            ('name', '=', name),
        ]
        if model:
            domain.append(('model', '=', model))
        ext_id = self.env['ir.model.data'].sudo().search(domain, limit=1)
        return ext_id.res_id if ext_id else False

    @api.model
    def _get_robots_category(self):
        """
        Devuelve la categoría Robots definida en ROBOTS_CATEG_EXT.
        Si el XML ID no existe o el registro fue borrado, retorna vacío.
        """
        robots_category_id = self._safe_get_external_record_id(
            ROBOTS_CATEG_EXT['module'],
            ROBOTS_CATEG_EXT['name'],
            model='product.category',
        )
        if not robots_category_id:
            return self.env['product.category']
        category = self.env['product.category'].browse(robots_category_id)
        return category if category.exists() else self.env['product.category']

    @api.model
    def _get_robots_product_domain(self):
        """
        Dominio del campo Producto:
        - Si existe la categoría de ROBOTS_CATEG_EXT → solo productos de esa categoría.
        - Si no existe → todos los productos activos.
        """
        robots_category = self._get_robots_category()
        if not robots_category:
            return [('active', '=', True)]
        return [
            ('active', '=', True),
            ('categ_id', 'child_of', robots_category.id),
        ]

    @api.model
    def _get_robots_project_domain(self):
        return [('active', '=', True)]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Inyecta el dominio con el ID real de categoría para el cliente web."""
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if 'product_id' in res:
            res['product_id']['domain'] = self._get_robots_product_domain()
        return res

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
        ondelete='cascade',
        domain='[(\'active\', \'=\', True)]',
    )
    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        ondelete='set null',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        domain=lambda self: self._get_robots_product_domain(),
        context={'restrict_to_robots_category': True},
    )

    is_vmax = fields.Boolean(
        string='Es VMAX',
        compute='_compute_is_vmax',
        store=True,
    )
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
        if 'product_id' in vals:
            self._sync_product_type_fields()
        return res

    @api.depends('product_id.product_tmpl_id')
    def _compute_is_vmax(self):
        for robot in self:
            robot.is_vmax = robot._is_vmax()

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self._sync_opportunity_from_project()
        return {
            'domain': {
                'project_id': self._get_robots_project_domain(),
                'product_id': self._get_robots_product_domain(),
            }
        }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self._sync_product_type_fields()
        return {
            'domain': {
                'product_id': self._get_robots_product_domain(),
            }
        }

    @api.onchange('product_id', 'width')
    def _onchange_robot_width(self):
        for robot in self:
            if robot._is_smart() or robot._is_vmax():
                robot.width = 1.63

    def _sync_product_type_fields(self):
        for robot in self:
            if not robot.product_id:
                continue
            if not robot._is_vmax():
                robot.second_picking_arm = False
                robot.second_input_belt = False
                robot.refrigeration_module = False

    def _sync_opportunity_from_project(self):
        for robot in self:
            if robot.project_id:
                robot.opportunity_id = robot.project_id.opportunity_id

    @api.constrains('product_id')
    def _check_product_robots_category(self):
        robots_category = self._get_robots_category()
        if not robots_category:
            return
        allowed_products = self.env['product.product'].search(
            self._get_robots_product_domain()
        )
        for robot in self:
            if robot.product_id and robot.product_id not in allowed_products:
                raise ValidationError(
                    'El producto seleccionado debe pertenecer a la categoría Robots.'
                )

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

    def _is_product_type(self, product_type):
        self.ensure_one()
        if not self.product_id or not self.product_id.product_tmpl_id:
            return False

        ext_conf = VMAX_EXT if product_type == 'VMAX' else SMART_EXT
        external_template_id = self._safe_get_external_record_id(
            ext_conf['module'],
            ext_conf['name'],
        )
        if not external_template_id:
            template_name = (self.product_id.product_tmpl_id.name or '').strip().lower()
            if product_type == 'VMAX':
                return 'vmax' in template_name
            return 'smart' in template_name

        return self.product_id.product_tmpl_id.id == external_template_id

    def _is_vmax(self):
        return self._is_product_type('VMAX')

    def _is_smart(self):
        return self._is_product_type('SMART')

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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Aplica el filtro de categoría Robots solo cuando el many2one de
        x_lista_de_robots lo solicita vía contexto.
        Si la categoría no existe, no agrega filtro extra (muestra todos).
        """
        args = list(args or [])
        if self.env.context.get('restrict_to_robots_category'):
            robots_domain = self.env['x_lista_de_robots']._get_robots_product_domain()
            for leaf in robots_domain:
                if leaf not in args:
                    args.append(leaf)
        return super().name_search(name, args=args, operator=operator, limit=limit)