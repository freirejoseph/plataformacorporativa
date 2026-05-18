"""initial schema for accesos menues

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-18 00:00:00
"""
from __future__ import annotations

from pathlib import Path

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT_DIR / "apps" / "accesos-menues" / "backend" / "schema.sql"


def upgrade() -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    for statement in schema_sql.split(";"):
        text = statement.strip()
        if text:
            op.execute(text)


def downgrade() -> None:
    statements = [
        "DROP TABLE IF EXISTS log_accesos",
        "DROP TABLE IF EXISTS log_actividad",
        "DROP TABLE IF EXISTS sesiones",
        "DROP TABLE IF EXISTS permisos_grupo",
        "DROP TABLE IF EXISTS permisos_usuario",
        "DROP TABLE IF EXISTS permisos_rol",
        "DROP TABLE IF EXISTS opciones_programa",
        "DROP TABLE IF EXISTS menus",
        "DROP TABLE IF EXISTS modulos",
        "DROP TABLE IF EXISTS portales",
        "DROP TABLE IF EXISTS usuarios_grupos",
        "DROP TABLE IF EXISTS usuarios_roles",
        "DROP TABLE IF EXISTS grupos",
        "DROP TABLE IF EXISTS roles",
        "DROP TABLE IF EXISTS usuarios",
    ]
    for statement in statements:
        op.execute(statement)
