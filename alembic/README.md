# Alembic

Inicializacion de migraciones versionadas para `plataformacorporativa`.

## Uso

```powershell
alembic upgrade head
```

## Configuracion

- La URL de base de datos se toma de `DATABASE_URL` si existe.
- Si no existe, se usa el valor `DB_URL` del `.env`.
- El contrato de datos de la plataforma vive en `docs/SKILL_Plataforma.md`.
