# Automatiza: Personalización Helpdesk y Mantenimiento

## Descripción General
Este módulo unificado (`custom_helpdesk_maintenance`) reemplaza y formaliza de manera centralizada las personalizaciones generadas previamente con Odoo Studio y en módulos antiguos dispersos (como `custom_maintenance_request`) para los modelos de **Helpdesk (`helpdesk.ticket`)**, **Mantenimiento (`maintenance.request`)** y **Equipos (`maintenance.equipment`)**. 

El principal objetivo fue limpiar la convención de nombres de los campos (eliminando los prefijos `x_` y `x_studio_`), evitar la duplicidad de relaciones de base de datos, integrarlos de manera nativa utilizando buenas prácticas de programación en Odoo 17, y habilitar flujos automáticos robustos como la creación de solictudes de mantenimiento desde Helpdesk.

## Cambios y Arquitectura

### 1. Dependencias
- `helpdesk`, `maintenance`, `hr`, `analytic`.

### 2. Modelos Modificados

#### `helpdesk.ticket`
- **Nuevos campos formalizados:**
  - `equipment_id`: Relación con el equipo de mantenimiento en avería.
  - `tour_id`: Relación estandarizada hacia el viaje/gira (Modelo: `maintenance.giras`).
  - `progress`: Control porcentual (`0`, `25`, `50`, `75`, `100`).
  - `employee_follower_ids`: Múltiples empleados (seguidores) del ticket. Solo admite a miembros de 'Servicio Técnico', 'Call Center' y 'Gerencia'.
  - `parent_ticket_id`: Definición de jerarquías originarias entre tickets.
  - `evidence_ids`: Adjuntos / evidencias del problema.
  - `maintenance_request_id`: Enlace formal entre el ticket de nivel 1 de helpdesk hacia un mantenimiento de nivel 2.
- **Lógica de negocio:**
  - `action_create_maintenance_request()`: Crea de manera automática un Ticket de Tipo Correctivo en Mantenimiento enlazándolo con el Ticket padre y notificando al Chatter.

#### `maintenance.request`
- **Fusión y estandarización:** Toda la lógica de Studio y del anterior módulo complementario ha sido unificada aquí.
- **Nuevos campos formalizados:**
  - `ticket_origin_id`: Guarda la referencia transparente de Solo Lectura del ticket de Helpdesk originario de esta avería/solicitud. Reemplaza al obsoleto `x_ticket_id`.
  - `tour_id`: Relación a la gira (`maintenance.giras`).
  - `assigned_employee_id`: Empleado a ser asignado para dicha reparación de mantenimiento.
  - `equipment_manager_id`: Relacional de solo lectura que carga informativamente quién es el responsable del equipo (`equipment_id.employee_id`).
  - `is_overdue`: Booleano computado (`_compute_is_overdue`) que calcula transparentemente si la `schedule_date` superó la fecha de hoy, para aplicar rojo estético. 

#### `maintenance.equipment`
- **Nuevo campo:**
  - `partner_id`: Permite designar explícitamente el *Cliente / Farmacia* al equipo, lo que heredan automáticamente las solicitudes de Mantenimiento referenciadas desde el Helpdesk.

### 3. Modificaciones en Interfaz de Usuario (XML)
- **`helpdesk_ticket_views.xml`:** Rediseño a dos columnas para limpiar la sábana de la vista ("Sheet"). Se introdujo el widget _Statusbar_ interactivo para el progreso de forma prominente, la inclusión condicional automática del botón *Crear Mantenimiento*, y se previnieron crash por posibles dependencias no instaladas de terceros (`sale_line_id`). Adicionalmente, se ha integrado un **Smart Button (Botón Estadístico)** en la caja de botones principal (`button_box`) para visualizar la cantidad y navegar rápidamente a las solicitudes de mantenimiento vinculadas, gestionando dinámicamente su visibilidad (apoyándose en el campo oculto `maintenance_count`).
- **`maintenance_request_views.xml`:** Trae la integración visual de la fusión completa:
   - Formulario: Inserta `tour_id`, `assigned_employee_id`, `equipment_manager_id` transparentemente y el Ticket Origen oculto. Se incorporó un nuevo **Smart Button** inyectado directamente en el `button_box` de la cabecera (creado dinámicamente) para visualizar la estadística y saltar de inmediato al Ticket de Helpdesk originario (`ticket_count`). Además, se oculta visualmente el técnico originario (`user_id`) para descongestionar el formulario, y se puentean los dominios nativos en `equipment_id` (`domain="[]"`) para habilitar la libre selección global de los aparatos.
   - Kanban: Evalúa a nivel de vista el booleano `is_overdue` y pinta de color con la clase de Bootstrap `bg-danger text-white` toda la tarjeta de mantenimiento si ya superó su fecha límite.
- **`maintenance_equipment_views.xml`:** Adición del cliente referenciado tras la especificación del modelo del aparato.

### 4. Datos por Defecto Inteligentes (Data XML)
Se reescribió `data/helpdesk_data.xml`. Durante la instalación asegura que el catálogo de incidencias de mesa de ayuda exista universalmente (`Actualización de versión`, `Calibración`, `Commissioning`, `Errores Robot`, etc.). Teniendo `noupdate="1"`, previene la sobreescritura futura si el cliente los renombra.

## Consideraciones Post-Instalación (IMPORTANTE)
1. Dado que este módulo unifica y migra el comportamiento de campos de *Studio/custom_* hacia estándar formal, **los datos anteriores no se migrarán solos**. Los valores en viejas tablas `x_studio_X` deberán moverse manualmente desde base de datos.
2. Es fuertemente recomendado **borrar u ocultar el módulo viejo (`custom_maintenance_request`)** del árbol de directorios de Odoo (`Desarrollo/`) antes de instalar esta versión final unificada, para asegurar la homogeneidad y evitar variables duplicadas u olvidadas a nivel de kernel de la instancia.


##
##Actualizaciones Del Módulo 
##
### Actualización 14/05/2026

Se aplicaron nuevas personalizaciones para mantener la compatibilidad con el entorno de Odoo Studio y optimizar la vinculación Helpdesk-Mantenimiento:
- **Equipos (`maintenance.equipment`)**: Adición del campo `robot_out_of_service`.
- **Mantenimiento (`maintenance.request`)**: 
  - Cambio en la lógica del estado Kanban (`kanban_state`) computado de forma automática según la prioridad (si el equipo está fuera de servicio o si la fecha límite ya expiró).
  - Integración de `tour_id` y `robot_out_of_service` como campos relacionados directos (`related`) desde el Equipo.
  - Implementación de relación Many2many (`ticket_ids`) para soporte a múltiples tickets por mantenimiento.
- **Helpdesk (`helpdesk.ticket`)**:
  - Implementación de relación Many2many (`maintenance_request_ids`) y automatización del campo `tour_id`.
  - **Automatización de Checklist**: Inserción automática de un checklist en formato HTML en el campo descripción cuando el tipo de ticket es "Calibración".
- **Interconectividad**: Botones actualizados en ambas vistas para la creación cruzada e intervinculada de registros mediante la nueva estructura Many2many, manteniendo las vistas limpias y ocultando la carga técnica.
