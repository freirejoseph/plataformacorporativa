from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class AuditEntry:
    usuario_id: int | None
    accion: str
    detalle: str | None = None
    ip: str | None = None
    equipo: str | None = None


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def append_audit_log(db_path: Path, entry: AuditEntry) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO log_actividad (usuario_id, fecha_hora, accion, detalle, ip, equipo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entry.usuario_id, now, entry.accion, entry.detalle, entry.ip, entry.equipo),
        )
        conn.commit()
    finally:
        conn.close()


def append_access_log(
    db_path: Path,
    usuario_id: int | None,
    rol_id: int | None,
    portal_id: int | None,
    modulo_id: int | None,
    menu_id: int | None,
    opcion_id: int | None,
    programa_nombre: str | None,
    programa_url: str | None,
    estado: str,
    ip: str | None = None,
    equipo: str | None = None,
    navegador: str | None = None,
    mensaje_error: str | None = None,
) -> None:
    now = datetime.now()
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO log_accesos (
              usuario_id, rol_id, portal_id, modulo_id, menu_id, opcion_id,
              programa_nombre, programa_url, fecha_acceso, hora_inicio, hora_fin,
              duracion_segundos, estado, ip, equipo, navegador, mensaje_error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario_id,
                rol_id,
                portal_id,
                modulo_id,
                menu_id,
                opcion_id,
                programa_nombre,
                programa_url,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                now.strftime("%H:%M:%S"),
                0,
                estado,
                ip,
                equipo,
                navegador,
                mensaje_error,
            ),
        )
        conn.commit()
    finally:
        conn.close()
