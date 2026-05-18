# Revision de Codigo y Arquitectura - Agente: Codex

**Fecha:** 2026-05-18  
**Proyecto:** Plataforma Corporativa

## Ya resuelto

- `SKILL_Plataforma` centralizado en `docs/` como contrato global de la plataforma.
- `docs/arquitectura/contrato-plataforma.md` ampliado con:
  - formato ISO 8601 para fechas y horas
  - estructura comun de error
  - contrato minimo de entrada entre tableros
- `docs/stack-tecnico.md` actualizado con:
  - Alembic
  - accesibilidad basica
  - politica de assets locales
  - exportacion estatica de OpenAPI
- `apps/accesos-menues` reforzado con:
  - endpoints de login/logout
  - registro de inicio y fin de accesos
  - CRUD y asignaciones
  - CRUD de modulos y opciones
  - persistencia de sesiones con token
  - duracion de accesos calculada al cierre
  - TTL configurable y rotacion de sesiones al autenticar nuevamente
  - resolucion de permisos
  - auditoria y matriz de permisos
- El frontend del portal madre ahora incorpora:
  - `aria-live`
  - tablas con semantica y `scope`
  - estados `is-invalid`
  - logos/avatares locales versionados en el repo
- Se inicializo Alembic como base de migraciones versionadas.
- `Portal Corporativo` ahora consume contexto real del backend de accesos:
  - session token
  - usuario, roles y grupos
  - accesos visibles por contexto
  - notificaciones y acciones rapidas
  - launch surface para `accesos-menues`
- La exportacion estatica de OpenAPI ya queda disponible en `docs/openapi.json`.
- La validacion tecnica del portal madre ya paso.

## Pendiente real

- Validar en una etapa futura la capa de SQL Server corporativa si el despliegue productivo la requiere.
- Definir por completo los `SKILL` de los tableros de negocio que aun no tienen reglas finales aprobadas:
  - `administracion-general`
  - `compras`
  - `cxc`
  - `cxp`
  - `finanzas`
  - `inventario`
  - `produccion`
  - `reportes`
  - `rrhh`

## Cierre

La base transversal ya esta cerrada. Lo que sigue depende de la capa de SQL Server futura y de definicion funcional por dominio.
