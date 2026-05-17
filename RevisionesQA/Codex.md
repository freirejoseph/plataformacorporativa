# Revision de Codigo y Arquitectura - Agente: Codex

**Fecha:** 2026-05-17  
**Proyecto:** Plataforma Corporativa

## Ya resuelto

- `SKILL_Plataforma` ya incluye la regla obligatoria de sincronizar local y Ubuntu al cerrar cada cambio.
- `core/` y `shared/` ya tienen una base funcional real para:
  - autenticacion
  - sesiones
  - auditoria
  - rutas compartidas
  - resolucion de permisos
  - arbol de menus
- `apps/accesos-menues` ya incluye:
  - login con token de sesion
  - CRUD de usuarios, roles, grupos y menus
  - asignacion y desasignacion de usuarios a roles y grupos
  - arbol de menus
  - matriz de permisos
  - auditoria
  - seed SQLite consistente con el acceso de prueba
  - formularios reales en el frontend para altas y asignaciones
- La infraestructura ya cuenta con:
  - `infra/docker`
  - `infra/nginx`
  - `infra/systemd`
  - scripts de backup, despliegue, migracion y health check
  - CI automatizado
- La rutina de sincronizacion local/Ubuntu ya existe y tiene modo `watch`.
- Los tests del portal madre ya quedaron preparados para cubrir login y asignaciones.

## Pendiente real

- Completar los `SKILL` funcionales de los tableros de negocio restantes:
  - `portal-corporativo`
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

La base transversal ya esta operativa para seguir construyendo. El siguiente esfuerzo grande ya no es el portal madre, sino el detalle funcional de cada tablero de negocio.
