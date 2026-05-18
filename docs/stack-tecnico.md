# Stack tecnico inicial

Este es el stack base del modulo madre `accesos-menues`.

## Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Alembic
- python-dotenv
- Exportacion estandar de OpenAPI para stakeholders y validacion tecnica

## Base de datos
- SQLite para desarrollo local
- SQL Server para integracion corporativa cuando aplique

## Frontend
- HTML
- CSS
- JavaScript
- Accesibilidad basica con roles, labels y estados invalidos

## Assets
- Logos y mockups versionados dentro del repositorio
- Sin dependencias visuales externas para la experiencia base del portal

## Uso esperado
- El backend lee configuracion desde `.env`
- El tablero madre administra usuarios, roles, grupos, menus y permisos
- Los demas tableros heredan el contexto de acceso desde este modulo
- Las sesiones tienen TTL configurable y se rotan al iniciar una nueva autenticacion del mismo usuario
