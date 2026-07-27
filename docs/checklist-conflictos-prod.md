# Checklist conflictos pre-producción — customs Julio 2026

Fecha verificación: 2026-07-23  
BD testing: `odooJunio2026` (contenedor `odoo_enterprise_v17` / DB `odoo_db_v15`)

## Flujo de carpetas

| Rol | Path |
|-----|------|
| Desarrollo | `C:\odoo_project\odoo_addons\automatiza\` |
| Testing (Odoo carga) | `C:\odoo_project\odoo_addons\` (módulos sueltos) |
| `addons_path` relevante | `/mnt/extra-addons` (= `odoo_addons`), `/mnt/desarrollo` (= `EnDesarrollo`). **No** incluye `automatiza`. |

---

## Fase 0 — Sync Dev vs Testing

| Módulo | Sync contenido | Notas |
|--------|----------------|-------|
| custom_crm_v4 | OK | Solo falta `CAMBIOS.md` en testing (doc) |
| custom_project | OK | Solo falta `CAMBIOS.md` en testing (doc) |
| custom_helpdesk_maintenance | OK | |
| custom_maintenance | OK | |
| custom_giras | OK | |
| custom_stock_picking | OK | |
| custom_helpdesk_maintenanceV0 | DESYNC (irrelevante) | V0 no debe usarse; diferencias esperadas |

### Estado `ir.module.module`

| Módulo | Estado | Versión BD | Manifest testing |
|--------|--------|------------|------------------|
| custom_crm_v4 | installed | 17.0.5.0.1 | 17.0.5.0.1 |
| custom_project | installed | 17.0.2.1.0 | 17.0.2.1.0 |
| custom_maintenance | installed | 17.0.1.0.0 | 17.0.1.0.0 |
| custom_helpdesk_maintenance | installed | **17.0.1.0.6** | **17.0.1.0.7** (pendiente `-u`) |
| custom_giras | installed | 17.0.1.0.0 | — |
| custom_stock_picking | installed | 17.0.1.0.0 | — |
| custom_maintenance_planning | installed | 17.0.1.0.0 | (solo en testing root) |
| custom_helpdesk_maintenanceV0 | **uninstalled** | — | OK |
| custom_crm_v3 | uninstalled | — | OK |
| custom_crm_atmtz | uninstalled | — | OK (EnDesarrollo) |
| **modulo_crm_v3** | **installed** | 17.0.1.1 | Legacy aún activo |

---

## Fase 1 — Matriz de solapes

| Área | Nuevos | Anteriores | Resultado |
|------|--------|------------|-----------|
| `crm.lead` campos | custom_crm_v4 (+ project_ids en custom_project) | modulo_crm_v3 redefine mismos `x_studio_*` | **Riesgo medio**: doble herencia de mismos campos (compatibles hoy, pero legacy instalado de más) |
| `crm.lead` form | v4 `crm.lead.form.custom.automatiza` active | v3 form **inactive** (cleanup OK); Studio form **active** | **Riesgo UX**: Studio + v4 pueden solapar UI |
| `crm.lead` tree | v4 trees active | v3 trees **aún active** (xmlids distintos) | **Riesgo bajo/UX**: listados legacy duplicados en catálogo de vistas |
| `project.project.opportunity_id` | UNIQUE en BD | — | **Sin solape de datos** (0 duplicados) |
| `x_proyecto_id` | computed non-stored | No hay Studio `x_proyecto_*` conflictivo | **OK** |
| `helpdesk.ticket` create/write | custom_helpdesk_maintenance (Envío/Retiro) | custom_maintenance_planning (followers + descripción) | **Compatible** si ambos llaman `super()` (cadena MRO) |
| `mail.activity.create` | solo summary Envío/Retiro | ningún otro custom | **OK** |
| `product.product.name_search` | filtro robots (contexto) | ningún otro | **OK** |
| `maintenance.equipment` | custom_maintenance + helpdesk views | giras / planning | **Sin conflicto de campo detectado** |
| `stock.picking` | — | custom_stock_picking | **Sin solape** con cadena Julio |
| V0 helpdesk | — | uninstalled | **OK** (no cargar) |
| Ext ID job inventario | usa `_hr.job_.stockManager_extID` (id 65) | xmlid `job_responsable_inventario` → job **67** huérfano (sin empleados) | **Riesgo bajo**: job duplicado residual; lógica nueva usa 65 |
| Tipo ticket Envío/Retiro | id 12 único | — | **OK** |
| Categoría robots_extID | id 11, ~2 productos | — | **OK** (pocos productos en cat.) |

### Overrides MRO (resumen)

| Método | Módulos | ¿super()? | Riesgo |
|--------|---------|-----------|--------|
| `helpdesk.ticket.create/write` | helpdesk_maintenance + maintenance_planning | Sí (ambos) | Bajo si orden de carga estable |
| `helpdesk.ticket.activity_schedule` | helpdesk_maintenance | Guarda solo summary exacto | Bajo |
| `mail.activity.create` | helpdesk_maintenance | Guarda solo summary Envío/Retiro | Bajo |
| `project.project.create/write` | custom_project | Sí + sync oportunidad | Bajo |
| `product.product.name_search` | custom_project | Condicional por contexto | Bajo |
| `crm.lead` (auto proyecto) | custom_crm_atmtz | N/A | Nulo (uninstalled) |

---

## Fase 2 — Integridad BD (resumen)

- UNIQUE `project_project_opportunity_id_uniq`: presente; **0** oportunidades con >1 proyecto.
- `x_proyecto_id`: many2one, `store=false` (computed).
- Form legacy v3: `active=false`.
- Studio form CRM: `active=true` (revisar UX).
- Ext IDs críticos presentes.
- Empleados job 65: Agustín (user 16) + Javier (sin user_id).
- Job 67 “Responsable de inventario” vacío (residual xmlid).

---

## Fase 3 — Upgrade smoke (ejecutado 2026-07-23)

Orden `-u`: `custom_project,custom_crm_v4,custom_maintenance,custom_helpdesk_maintenance`  
Resultado: **EXIT 0**. Helpdesk pasó a **17.0.1.0.7**.

| Check | Resultado |
|-------|-----------|
| Versiones módulos cadena Julio | OK (helpdesk 17.0.1.0.7) |
| Form v4 activo / form v3 inactivo | OK |
| Studio form CRM activo | Sí (activo) — UX |
| Trees v3 aún activos | Sí (3269–3272) |
| `x_proyecto_id` runtime (lead↔proyecto) | OK (proyecto 459 ↔ opp 464) |
| Ticket Envío/Retiro → actividad | OK (1 actividad → `aaguero@...`) |
| V0 | uninstalled |
| Giras / equipment | OK (modelo + 227 equipos) |
| stock + custom_stock_picking | instalados (smoke `bool(model)` fue falso positivo) |
| Warning upgrade | `kanban_state` selection override (helpdesk + planning); `custom_giras.create` no batch |

---

## Fase 4 — Go / No-go

### Veredicto: **GO CONDICIONADO**

No hay conflicto bloqueante que impida el upgrade de la cadena Julio 2026 en testing (upgrade + smoke Envío/Retiro y vínculo proyecto/oportunidad OK). Antes de producción, aplicar remediaciones abajo.

### Bloqueantes / remediaciones previas a prod

| Severidad | Hallazgo | Acción |
|-----------|----------|--------|
| Alta (recomendado) | `modulo_crm_v3` **sigue instalado** (trees activos; form ya desactivado) | Desinstalar `modulo_crm_v3` en staging, validar CRM, luego prod |
| Media (UX) | Vista Studio form `crm.lead` activa junto a v4 | Revisar UI; desactivar Studio si duplica pestañas/campos |
| Baja | Job `hr.job` id 67 + xmlid `job_responsable_inventario` huérfano | No usar; opcional archivar job 67. Lógica correcta usa `stockManager_extID` (65) |
| Operativa | Sync Dev→Testing | Mantener copia en `odoo_addons\` alineada antes de cada deploy (hoy cadena Julio OK) |
| Obligatoria | No instalar V0 | Confirmar `custom_helpdesk_maintenanceV0` uninstalled en prod |

### No bloqueantes (documentados)

- Carpetas duplicadas `automatiza/` vs `odoo_addons/` (flujo esperado).
- `custom_maintenance_planning` + helpdesk: ambos override create/write con `super()` — compatible.
- Javier Vallori sin `user_id`: no recibe actividad (esperado).
- Warning `kanban_state` selection (preexistente helpdesk/planning).
- Pocos productos en categoría robots (2): filtro UI OK, datos a completar en negocio.

### No tocar en este plan

- Código de desarrollo en `automatiza` (sin cambios).
- Producción (solo verificado testing `odooJunio2026`).
