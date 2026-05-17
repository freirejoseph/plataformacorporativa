# Stack técnico inicial

Este es el stack base del módulo madre `accesos-menues`.

## Backend
- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- python-dotenv

## Base de datos
- SQLite para desarrollo local
- SQL Server para integración corporativa cuando aplique

## Frontend
- HTML
- CSS
- JavaScript

## Uso esperado
- El backend lee configuración desde `.env`
- El tablero madre administra usuarios, roles, grupos, menús y permisos
- Los demás tableros heredan el contexto de acceso desde este módulo

