# Revision de Codigo y Arquitectura - Agente: Codex

**Fecha:** 2026-05-18  
**Proyecto:** Plataforma Corporativa

## Ya resuelto

- `SKILL_Plataforma` ya obliga a sincronizar local y Ubuntu al cerrar cada cambio.
- `core/` y `shared/` ya tienen base funcional para:
  - autenticacion
  - sesiones
  - auditoria
  - resolucion de permisos
  - arbol de menus
- `apps/accesos-menues` ya quedo operativo con:
  - backend FastAPI con login, logout, CRUD, asignaciones y logs
  - bootstrap de SQLite con migracion para bases viejas
  - frontend principal del portal madre
  - matriz de permisos y arbol de menus
  - seed demo compatible con el login de prueba
- `apps/portal-corporativo` ya lanza el subportal `accesos-menues`.
- La validacion tecnica ya paso:
  - `python -m py_compile`
  - `pytest tests/test_accesos_menues.py`
  - `node --check apps/portal-corporativo/app.js`

## Pendiente real

- Completar los `SKILL` funcionales y aprobados de los tableros de negocio que aun no tienen definicion final:
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

La base transversal y el portal madre ya estan listos. Lo que sigue es definicion de negocio por tablero, no rearmar la plataforma comun.
