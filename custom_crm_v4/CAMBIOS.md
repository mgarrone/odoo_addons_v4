# Documentación de cambios — custom_crm_v4

**Módulo:** Automatiza CRM v4 Campos Personalizados  
**Versión documentada:** 17.0.5.0.1  
**Fecha:** Julio 2026

## Resumen

Ajustes de layout en el formulario de oportunidad/lead y automatización del campo **Proyecto** (`x_proyecto_id`) a partir de la relación con `project.project`.

---

## 1. Layout de “Información adicional”

**Archivo:** `views/crm_lead_views.xml`

Se reorganizó la pestaña **Información adicional** (páginas `extra` y `lead`) con layout `col="2"`:

| Columna izquierda | Columna derecha |
|------------------|-----------------|
| INFORMACIÓN DE LA COMPAÑÍA | CONTACTOS DE LA EMPRESA |
| MARKETING | SEGUIMIENTO |

**Objetivo:** que el grupo **SEGUIMIENTO** quede debajo de contactos y a la derecha de marketing, según el diseño funcional.

---

## 2. Campo Proyecto en la oportunidad (`x_proyecto_id`)

**Archivo:** `models/crm_lead.py`

- `x_proyecto_id` pasó a ser un campo **calculado** (no editable a mano).
- Se completa cuando un proyecto tiene la oportunidad seleccionada en `opportunity_id`.
- Depende de la relación inversa `project_ids` definida en `custom_project`.

**Comportamiento:**

- Al vincular oportunidad ↔ proyecto desde Proyecto → se muestra el proyecto en CRM.
- Al quitar el vínculo → el campo se vacía.

**Migración:** `migrations/17.0.5.0.1/post-migrate.py` refresca vínculos ya existentes al actualizar el módulo.

---

## Dependencias relacionadas

- Requiere `custom_project` (campo `opportunity_id` y `project_ids` en `crm.lead`).

## Cómo aplicar

```bash
-u custom_project,custom_crm_v4
```
