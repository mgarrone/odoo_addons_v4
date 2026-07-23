# Documentación de cambios — custom_project

**Módulo:** Automatiza Proyecto y Lista de Robots  
**Versión documentada:** 17.0.2.x  
**Fecha:** Julio 2026

## Resumen

Relación proyecto ↔ oportunidad, sincronización de escenarios, y filtro de productos de la categoría **Robots** en la lista de robots / escenarios.

---

## 1. Relación Proyecto ↔ Oportunidad

**Archivo:** `models/project_project.py`

- Campo `opportunity_id` en `project.project` (unique: una oportunidad → un solo proyecto).
- Relación inversa `project_ids` en `crm.lead`.
- Al crear/cambiar `opportunity_id`, se sincroniza la oportunidad en los escenarios (`robot_scenario_ids`).

La oportunidad en CRM muestra el proyecto vía `x_proyecto_id` (calculado en `custom_crm_v4`).

---

## 2. Filtro de productos en Lista de Robots

**Archivos:**

- `models/lista_robots.py`
- `views/lista_robots_views.xml`
- `views/project_project_views.xml`

### Constante

```python
ROBOTS_CATEG_EXT = {'module': '_product.category_', 'name': 'robots_extID'}
```

### Comportamiento

| Situación | Selector de Producto |
|-----------|----------------------|
| Existe la categoría del XML ID | Solo productos de esa categoría (y subcategorías) |
| No existe la categoría | Todos los productos activos |

### Implementación

1. Dominio dinámico en el campo `product_id`.
2. Contexto `restrict_to_robots_category` en las vistas.
3. Override de `name_search` en `product.product` cuando ese contexto está activo.
4. Constraint al guardar: el producto debe pertenecer a la categoría Robots (si la categoría existe).

### Verificación en consola

```python
env['x_lista_de_robots']._get_robots_product_domain()
# Esperado con categoría: [('active', '=', True), ('categ_id', 'child_of', 11)]

env['product.product'].with_context(restrict_to_robots_category=True).name_search('')
```

---

## Cómo aplicar

```bash
-u custom_project
```
