# Shared Database

Area compartida para esquemas, migraciones y acceso a SQLite.

Base principal:
- `portal-data/accesos_menues.sqlite`

## Archivos
- `accesos_menues.schema.sql`: contrato de tablas para identidad, menus, permisos, sesiones y auditoria.
- `accesos_menues.seed.sql`: datos demo y de arranque para desarrollo local.

## Nota
- Mantener estos archivos alineados con el backend de `accesos-menues` para evitar divergencias entre el contrato compartido y la implementacion.
