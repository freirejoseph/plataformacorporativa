# SKILL accesos-menues

## Objetivo
`accesos-menues` es el subportal madre de administracion de la plataforma.
Su responsabilidad es definir, mantener y auditar:

- usuarios
- roles
- grupos
- menus
- opciones
- permisos
- portales
- modulos
- sesiones
- auditoria

Este subportal no es el portal de entrada del usuario final.
Es el centro de administracion que alimenta al Portal Corporativo.

## Relacion con el Portal Corporativo
El Portal Corporativo consume lo que aqui se define.

Flujo esperado:
1. El usuario entra al Portal Corporativo.
2. El portal resuelve su sesion y permisos.
3. Si tiene acceso a administracion, se muestra `accesos-menues`.
4. Desde `accesos-menues` se gestionan usuarios, menus y accesos.
5. Los cambios se reflejan en los tableros visibles para cada usuario.

## Alcance funcional
Este subportal debe permitir:
- crear y editar usuarios
- crear y editar roles
- crear y editar grupos
- crear arboles de menus
- asignar menus a roles y grupos
- resolver permisos por usuario
- registrar logs de actividad
- revisar auditoria
- ver sesiones activas

## Reglas de negocio
- Un usuario puede tener acceso directo, por rol, por grupo o por permiso puntual.
- La asignacion directa al usuario tiene prioridad si existe.
- Un menu no debe mostrarse si no esta autorizado.
- El subportal debe validar el contexto de usuario antes de operar.
- Toda accion importante debe dejar registro de auditoria.

## UI esperada
La vista debe seguir el mockup corporativo oscuro:
- sidebar izquierda fija
- header superior con busqueda y acciones
- tarjetas KPI en la parte superior
- tabla de usuarios
- panel de roles
- matriz de permisos
- actividad reciente
- acciones rapidas

## Integracion tecnica
Este subportal debe apoyarse en:
- SQLite para desarrollo local
- backend FastAPI
- frontend HTML/CSS/JavaScript
- sincronizacion obligatoria con Ubuntu al final de cada cambio

## Artefactos asociados
- `docs/SKILL_accesos-menues.css`
- `docs/SKILLPortalCorporativo.md`
- `docs/SKILLPortalCorporativo.css`
- `docs/stack-tecnico.md`

## Criterios de aceptacion
- Se pueden administrar usuarios, roles, grupos y menus.
- Se puede construir y resolver la matriz de permisos.
- La UI coincide con el mockup base.
- El subportal alimenta correctamente al Portal Corporativo.
- Los cambios quedan sincronizados local y Ubuntu.

## Pendientes de implementacion
- completar persistencia real de sesiones
- consolidar autenticacion del portal corporativo
- terminar CRUD completo de opciones y modulos
- conectar pantallas con permisos calculados en tiempo real

