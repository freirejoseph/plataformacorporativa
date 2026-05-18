# Revision de Codigo y Arquitectura - Agente: Gemini Code Assist

**Fecha:** 2026-05-18  
**Proyecto:** Plataforma Corporativa

## Ya resuelto

- `SKILL_Plataforma` ya vive centralizado en `docs/` y define el contrato comun de la plataforma.
- `docs/arquitectura/contrato-plataforma.md` ahora explicita:
  - ISO 8601 para fechas
  - formato uniforme de error
  - contrato minimo de contexto entre tableros
- `docs/stack-tecnico.md` ya contempla:
  - Alembic
  - SQLAlchemy
  - accesibilidad
  - assets locales
- `apps/accesos-menues` ya cubre:
  - login/logout
  - inicio y fin de accesos
  - CRUD de usuarios, roles, grupos y menus
  - asignaciones y auditoria
  - matriz de permisos
  - CRUD de modulos y opciones
  - persistencia de sesiones con token
  - duracion de accesos calculada al cierre
- El frontend del portal madre ya fue reforzado con:
  - `aria-live`
  - tablas con `scope`
  - clases de error `.is-invalid`
  - logos y avatares locales
- Se agrego la base de Alembic como migracion versionada.
- `apps/portal-corporativo` ya lanza el subportal de accesos y consume contexto real de sesion.

## Pendiente real

- Definir por completo los `SKILL` funcionales y aprobados de los tableros de negocio que aun no tienen reglas finales:
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

La capa comun ya quedo cerrada. El siguiente trabajo depende de reglas de negocio por dominio y de completar el ciclo de sesiones.
