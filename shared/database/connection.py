from __future__ import annotations

from pathlib import Path
import sqlite3


def get_sqlite_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_database(db_path: Path, schema_sql: str, seed_sql: str | None = None) -> None:
    conn = get_sqlite_connection(db_path)
    try:
        conn.executescript(schema_sql)
        if seed_sql:
            conn.executescript(seed_sql)
        conn.commit()
    finally:
        conn.close()
