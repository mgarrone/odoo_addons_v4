# Documentación de cambios — custom_helpdesk_maintenance

**Módulo:** Automatiza Personalización Helpdesk y Mantenimiento  
**Versión documentada:** 17.0.1.0.7  
**Fecha:** Julio 2026

## Resumen

Automatización de actividad en tickets de tipo **Envío/Retiro**, asignada únicamente al usuario del empleado con el puesto **Responsable de inventario** (clave externa). Si no hay nadie con ese puesto y usuario Odoo vinculado, **no se crea** la actividad.

---

## 1. Actividad automática Envío/Retiro

**Archivos:**

- `models/helpdesk_ticket.py`
- `models/mail_activity.py`

### Constante del puesto

```python
STOCK_MANAGER_JOB_EXT = {'module': '_hr.job_', 'name': 'stockManager_extID'}
```

### Comportamiento

| Situación | Resultado |
|-----------|-----------|
| Empleado activo con ese `job_id` **y** usuario Odoo | Actividad *Atender solicitud de Envío/Retiro* asignada a ese usuario |
| Puesto sin empleados, o empleado sin usuario Odoo | **No se crea** actividad; se eliminan automáticas previas con ese resumen |

### Disparadores

- Al **crear** un ticket con tipo Envío/Retiro.
- Al **cambiar** el tipo de ticket a Envío/Retiro.

### Capas de control

1. `_get_warehouse_responsible_user()` — solo XML ID, **sin** fallbacks (ni por nombre ni por login `agustin`).
2. `activity_schedule` — intercepta la programación de esa actividad.
3. `mail.activity.create` — bloquea o corrige creaciones desde otras fuentes (p. ej. módulos legacy).
4. `_register_hook` — asegura prioridad de esta lógica sobre herencias concurrentes.

### Requisitos para que se asigne bien

1. Debe existir el XML ID `_hr.job_.stockManager_extID`.
2. El empleado debe tener ese puesto.
3. El empleado debe tener **Usuario relacionado** en Odoo.

---

## 2. Nota operativa importante (Docker / addons)

En el entorno Docker de desarrollo pueden coexistir dos carpetas:

| Ruta | Uso |
|------|-----|
| `odoo_addons/custom_helpdesk_maintenance` | **La que carga Odoo** (`/mnt/extra-addons/...`) |
| `odoo_addons/automatiza/custom_helpdesk_maintenance` | Repo/workspace de trabajo |

Tras modificar en `automatiza`, hay que **sincronizar** a `odoo_addons/custom_helpdesk_maintenance` y reiniciar el contenedor `odoo_enterprise_v17`.

`custom_helpdesk_maintenanceV0` puede existir en el addons path; en la base documentada estaba **uninstalled**. Esta versión no depende de V0 y neutraliza su lógica de actividad si estuviera presente.

---

## Verificación en consola Odoo

```python
env['helpdesk.ticket']._get_stock_manager_job().display_name
env['helpdesk.ticket']._get_warehouse_responsible_user().name
# Sin responsable válido → False / vacío → no debe crearse actividad
```

## Cómo aplicar

```bash
docker restart odoo_enterprise_v17
# y/o
odoo -d NOMBRE_BD -u custom_helpdesk_maintenance --stop-after-init
```
