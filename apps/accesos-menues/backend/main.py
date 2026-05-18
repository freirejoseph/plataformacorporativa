from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Annotated, Optional
import sqlite3

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from shared.auth.security import generate_token, hash_password, verify_password
from shared.config.settings import load_settings
from shared.database.connection import get_sqlite_connection
from shared.menu_router.router import MenuItem, build_menu_tree
from shared.permissions.resolver import ALLOWED, DENIED, READ_ONLY


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = Path(__file__).resolve().parent
PORTAL_DIR = APP_DIR.parent
FRONTEND_DIR = PORTAL_DIR / "frontend"
ASSETS_DIR = PORTAL_DIR / "assets"
SCHEMA_PATH = APP_DIR / "schema.sql"
SEED_PATH = APP_DIR / "seed.sql"
DB_PATH = ROOT_DIR / "portal-data" / "accesos_menues.sqlite"

load_dotenv(ROOT_DIR / ".env")
SETTINGS = load_settings(ROOT_DIR)

def bootstrap_database() -> None:
    if not SCHEMA_PATH.exists() or not SEED_PATH.exists():
        return
    with open_db() as conn:
        usuario_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(usuarios)").fetchall()
        }
        schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
        sesiones_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(sesiones)").fetchall()
        }
        menus_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(menus)").fetchall()
        }
        if "token" not in sesiones_columns:
            schema_text = schema_text.replace(
                "CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token);\n",
                "",
            )
        conn.executescript(schema_text)
        if "password_hash" not in usuario_columns:
            conn.execute("ALTER TABLE usuarios ADD COLUMN password_hash TEXT")
        if "token" not in sesiones_columns:
            conn.execute("ALTER TABLE sesiones ADD COLUMN token TEXT")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token)")
        if "url" not in menus_columns:
            conn.execute("ALTER TABLE menus ADD COLUMN url TEXT")
        if "componente" not in menus_columns:
            conn.execute("ALTER TABLE menus ADD COLUMN componente TEXT")
        if "abre_nueva_pestana" not in menus_columns:
            conn.execute("ALTER TABLE menus ADD COLUMN abre_nueva_pestana INTEGER DEFAULT 0")
        if "requiere_log" not in menus_columns:
            conn.execute("ALTER TABLE menus ADD COLUMN requiere_log INTEGER DEFAULT 1")
        conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
        demo_hash = "pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507"
        demo_emails = [
            "joseph@empresa.com",
            "carlos.alberto@empresa.com",
            "maria.jaramillo@empresa.com",
            "juan.rodriguez@empresa.com",
            "luis.paredes@empresa.com",
            "gabriel.fuentes@empresa.com",
        ]
        for correo in demo_emails:
            conn.execute(
                """
                UPDATE usuarios
                SET password_hash = ?
                WHERE lower(correo) = lower(?)
                """,
                (demo_hash, correo),
            )
        conn.commit()

app = FastAPI(
    title="Accesos Menues",
    version="0.2.0",
    description="Tablero madre de usuarios, roles, grupos, menus, permisos y auditoria.",
)

allowed_origins = ["*"]
if SETTINGS.cors_origins.strip() and SETTINGS.cors_origins.strip() != "*":
    allowed_origins = [origin.strip() for origin in SETTINGS.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request, call_next):  # type: ignore[no-untyped-def]
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self' https: data:; img-src 'self' https: data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';",
    )
    return response


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def now_time() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).time().isoformat(timespec="seconds")


def parse_time_reference(value: str | None, fallback_date: str | None = None) -> datetime:
    reference_date = fallback_date or now_date()
    candidate = (value or "").strip()
    if not candidate:
        return datetime.now(timezone.utc).replace(microsecond=0)
    normalized = candidate.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        pass
    for pattern in ("%Y-%m-%d %H:%M:%S", "%H:%M:%S"):
        try:
            if pattern == "%H:%M:%S":
                combined = f"{reference_date} {candidate}"
                return datetime.strptime(combined, "%Y-%m-%d %H:%M:%S")
            return datetime.strptime(candidate, pattern)
        except ValueError:
            continue
    return datetime.now(timezone.utc).replace(microsecond=0)


def session_ttl() -> timedelta:
    hours = max(int(getattr(SETTINGS, "session_ttl_hours", 8)), 1)
    return timedelta(hours=hours)


def session_expires_at(session_row: dict[str, Any]) -> datetime:
    started = parse_time_reference(str(session_row.get("inicio") or now_iso()))
    return started + session_ttl()


def is_session_expired(session_row: dict[str, Any]) -> bool:
    estado = normalize_estado(session_row.get("estado"), "ACTIVA")
    if estado != "ACTIVA":
        return True
    return datetime.now(timezone.utc).replace(tzinfo=None) >= session_expires_at(session_row)


def expire_session(token: str, session_row: dict[str, Any]) -> None:
    if not token:
        return
    execute(
        """
        UPDATE sesiones
        SET fin = ?, estado = 'EXPIRADA'
        WHERE token = ? AND estado = 'ACTIVA'
        """,
        (now_iso(), token),
    )
    SESSION_CACHE.pop(token, None)


def open_db() -> sqlite3.Connection:
    return get_sqlite_connection(DB_PATH)


bootstrap_database()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with open_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with open_db() as conn:
        row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    with open_db() as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return int(cursor.lastrowid or 0)


def execute_many(statements: Iterable[tuple[str, tuple[Any, ...]]]) -> None:
    with open_db() as conn:
        for sql, params in statements:
            conn.execute(sql, params)
        conn.commit()


def get_session_by_token(token: str) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT s.id, s.token, s.usuario_id, s.inicio, s.fin, s.estado, s.ip, s.equipo, s.navegador,
               COALESCE(u.nombre, 'Sistema') AS usuario_nombre,
               COALESCE(u.correo, '') AS usuario_correo
        FROM sesiones s
        LEFT JOIN usuarios u ON u.id = s.usuario_id
        WHERE s.token = ?
        LIMIT 1
        """,
        (token,),
    )


class LoginPayload(BaseModel):
    correo: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: str = Field(min_length=5, max_length=120)
    cargo: Optional[str] = Field(default=None, max_length=120)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)
    password_plain: Optional[str] = Field(default=None, min_length=8, max_length=256)


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    correo: Optional[str] = Field(default=None, min_length=5, max_length=120)
    cargo: Optional[str] = Field(default=None, max_length=120)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=20)
    password_plain: Optional[str] = Field(default=None, min_length=8, max_length=256)


class RolePayload(BaseModel):
    codigo: str = Field(min_length=2, max_length=50)
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)


class RoleUpdatePayload(BaseModel):
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=50)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=20)


class GroupPayload(BaseModel):
    codigo: str = Field(min_length=2, max_length=50)
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)


class GroupUpdatePayload(BaseModel):
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=50)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=20)


class AssignmentPayload(BaseModel):
    rol_id: Optional[int] = Field(default=None, ge=1)
    grupo_id: Optional[int] = Field(default=None, ge=1)


class MenuPayload(BaseModel):
    codigo: str = Field(min_length=2, max_length=64)
    nombre: str = Field(min_length=2, max_length=120)
    portal_id: Optional[int] = Field(default=None, ge=1)
    modulo_id: Optional[int] = Field(default=None, ge=1)
    menu_padre_id: Optional[int] = Field(default=None, ge=1)
    icono: Optional[str] = Field(default=None, max_length=50)
    orden: int = Field(default=0, ge=0)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)
    url: Optional[str] = Field(default=None, max_length=255)
    componente: Optional[str] = Field(default=None, max_length=255)
    abre_nueva_pestana: bool = Field(default=False)
    requiere_log: bool = Field(default=True)


class ModulePayload(BaseModel):
    portal_id: int = Field(ge=1)
    codigo: str = Field(min_length=2, max_length=64)
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    icono: Optional[str] = Field(default=None, max_length=50)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)


class ModuleUpdatePayload(BaseModel):
    portal_id: Optional[int] = Field(default=None, ge=1)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=64)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    icono: Optional[str] = Field(default=None, max_length=50)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=20)


class OptionPayload(BaseModel):
    menu_id: int = Field(ge=1)
    codigo: str = Field(min_length=2, max_length=64)
    nombre: str = Field(min_length=2, max_length=120)
    tipo: str = Field(min_length=2, max_length=40)
    url: Optional[str] = Field(default=None, max_length=255)
    componente: Optional[str] = Field(default=None, max_length=255)
    abre_nueva_pestana: bool = Field(default=False)
    requiere_log: bool = Field(default=True)
    estado: str = Field(default="ACTIVO", min_length=2, max_length=20)


class OptionUpdatePayload(BaseModel):
    menu_id: Optional[int] = Field(default=None, ge=1)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=64)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    tipo: Optional[str] = Field(default=None, min_length=2, max_length=40)
    url: Optional[str] = Field(default=None, max_length=255)
    componente: Optional[str] = Field(default=None, max_length=255)
    abre_nueva_pestana: Optional[bool] = Field(default=None)
    requiere_log: Optional[bool] = Field(default=None)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=20)


class LogAccessPayload(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)
    rol_id: Optional[int] = Field(default=None, ge=1)
    portal_id: Optional[int] = Field(default=None, ge=1)
    modulo_id: Optional[int] = Field(default=None, ge=1)
    menu_id: Optional[int] = Field(default=None, ge=1)
    opcion_id: Optional[int] = Field(default=None, ge=1)
    programa_nombre: Optional[str] = Field(default=None, max_length=255)
    programa_url: Optional[str] = Field(default=None, max_length=255)
    hora_inicio: Optional[str] = Field(default=None, max_length=32)
    hora_fin: Optional[str] = Field(default=None, max_length=32)
    duracion_segundos: Optional[int] = Field(default=None, ge=0)
    estado: str = Field(default="EXITOSO", min_length=2, max_length=20)
    ip: Optional[str] = Field(default=None, max_length=64)
    equipo: Optional[str] = Field(default=None, max_length=120)
    navegador: Optional[str] = Field(default=None, max_length=120)
    mensaje_error: Optional[str] = Field(default=None, max_length=255)


for _model in (
    LoginPayload,
    UsuarioCreate,
    UsuarioUpdate,
    RolePayload,
    RoleUpdatePayload,
    GroupPayload,
    GroupUpdatePayload,
    AssignmentPayload,
    MenuPayload,
    ModulePayload,
    ModuleUpdatePayload,
    OptionPayload,
    OptionUpdatePayload,
    LogAccessPayload,
):
    _model.model_rebuild()


SESSION_CACHE: dict[str, dict[str, Any]] = {}

ROLE_PORTAL_PRIORITY = {
    "SUPER_ADMIN": "SYSPRO ERP",
    "ADMIN": "Portal Corporativo",
    "GERENTE": "Portal Corporativo",
    "CONTADOR": "Odoo RRHH",
    "BASICO": "Portal Corporativo",
    "INVITADO": "Portal Reportes",
}

ROLE_NAME_PRIORITY = {
    "Super Administrador": "SYSPRO ERP",
    "Administrador": "Portal Corporativo",
    "Gerente": "Portal Corporativo",
    "Contador": "Odoo RRHH",
    "Usuario Basico": "Portal Corporativo",
    "Invitado": "Portal Reportes",
}


def normalize_estado(value: str | None, default: str = "ACTIVO") -> str:
    normalized = str(value or default).strip().upper()
    return normalized or default


def is_valid_email(value: str) -> bool:
    value = value.strip()
    return "@" in value and "." in value and " " not in value


def is_valid_code(value: str) -> bool:
    value = value.strip().upper()
    return bool(value) and all(char.isalnum() or char == "_" for char in value)


def status_to_bool(value: str | None) -> bool:
    return normalize_estado(value) == "ACTIVO"


def get_user_roles(usuario_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT r.id, r.codigo, r.nombre, r.descripcion, r.estado
        FROM usuarios_roles ur
        JOIN roles r ON r.id = ur.rol_id
        WHERE ur.usuario_id = ?
        ORDER BY r.nombre
        """,
        (usuario_id,),
    )


def get_user_groups(usuario_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT g.id, g.codigo, g.nombre, g.descripcion, g.estado
        FROM usuarios_grupos ug
        JOIN grupos g ON g.id = ug.grupo_id
        WHERE ug.usuario_id = ?
        ORDER BY g.nombre
        """,
        (usuario_id,),
    )


def pick_portal(roles: list[dict[str, Any]]) -> str:
    if not roles:
        return "Accesos y Menues"
    for role in roles:
        portal = ROLE_PORTAL_PRIORITY.get(role["codigo"], ROLE_NAME_PRIORITY.get(role["nombre"]))
        if portal:
            return portal
    return "Accesos y Menues"


def build_user_row(row: dict[str, Any]) -> dict[str, Any]:
    roles = get_user_roles(int(row["id"]))
    groups = get_user_groups(int(row["id"]))
    role_name = roles[0]["nombre"] if roles else "Sin rol"
    return {
        "id": row["id"],
        "nombre": row["nombre"],
        "correo": row["correo"],
        "cargo": row.get("cargo") or "",
        "estado": row.get("estado") or "ACTIVO",
        "avatar_url": row.get("avatar_url"),
        "fecha_creacion": row.get("fecha_creacion"),
        "ultimo_acceso": row.get("ultimo_acceso"),
        "password_hash": row.get("password_hash"),
        "rol": role_name,
        "portal": pick_portal(roles),
        "roles": [role["nombre"] for role in roles],
        "grupos": [group["nombre"] for group in groups],
    }


def list_users() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT id, nombre, correo, cargo, estado, avatar_url, fecha_creacion, ultimo_acceso, password_hash
        FROM usuarios
        ORDER BY id
        """
    )
    return [build_user_row(row) for row in rows]


def list_roles() -> list[dict[str, Any]]:
    roles = fetch_all(
        """
        SELECT id, codigo, nombre, descripcion, estado
        FROM roles
        ORDER BY nombre
        """
    )
    for role in roles:
        role["usuarios"] = fetch_one(
            "SELECT COUNT(*) AS total FROM usuarios_roles WHERE rol_id = ?",
            (role["id"],),
        )["total"]
    return roles


def list_groups() -> list[dict[str, Any]]:
    groups = fetch_all(
        """
        SELECT id, codigo, nombre, descripcion, estado
        FROM grupos
        ORDER BY nombre
        """
    )
    for group in groups:
        group["usuarios"] = fetch_one(
            "SELECT COUNT(*) AS total FROM usuarios_grupos WHERE grupo_id = ?",
            (group["id"],),
        )["total"]
    return groups


def list_portals() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, codigo, nombre, tipo, url_base, estado
        FROM portales
        ORDER BY id
        """
    )


def list_modules() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT m.id, m.portal_id, m.codigo, m.nombre, m.descripcion, m.icono, m.estado,
               p.nombre AS portal
        FROM modulos m
        JOIN portales p ON p.id = m.portal_id
        ORDER BY m.id
        """
    )


def list_options() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT o.id, o.menu_id, o.codigo, o.nombre, o.tipo, o.url, o.componente,
               o.abre_nueva_pestana, o.requiere_log, o.estado,
               me.nombre AS menu,
               p.nombre AS portal,
               m.nombre AS modulo
        FROM opciones_programa o
        JOIN menus me ON me.id = o.menu_id
        LEFT JOIN portales p ON p.id = me.portal_id
        LEFT JOIN modulos m ON m.id = me.modulo_id
        ORDER BY o.id
        """
    )


def list_sessions() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT s.id, s.token, s.usuario_id, s.inicio, s.fin, s.estado, s.ip, s.equipo, s.navegador,
               COALESCE(u.nombre, 'Sistema') AS usuario,
               COALESCE(u.correo, '') AS correo
        FROM sesiones s
        LEFT JOIN usuarios u ON u.id = s.usuario_id
        ORDER BY datetime(s.inicio) DESC, s.id DESC
        """
    )


def list_menus() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT me.id, me.portal_id, me.modulo_id, me.menu_padre_id, me.codigo, me.nombre,
               me.icono, me.orden, me.estado,
               p.nombre AS portal,
               m.nombre AS modulo
        FROM menus me
        LEFT JOIN portales p ON p.id = me.portal_id
        LEFT JOIN modulos m ON m.id = me.modulo_id
        ORDER BY me.orden, me.id
        """
    )


def get_module_by_id(modulo_id: int) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT m.id, m.portal_id, m.codigo, m.nombre, m.descripcion, m.icono, m.estado,
               p.nombre AS portal
        FROM modulos m
        JOIN portales p ON p.id = m.portal_id
        WHERE m.id = ?
        """,
        (modulo_id,),
    )


def get_option_by_id(opcion_id: int) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT o.id, o.menu_id, o.codigo, o.nombre, o.tipo, o.url, o.componente,
               o.abre_nueva_pestana, o.requiere_log, o.estado
        FROM opciones_programa o
        WHERE o.id = ?
        """,
        (opcion_id,),
    )


def list_menu_tree() -> list[dict[str, object]]:
    menus = [
        MenuItem(
            id=int(row["id"]),
            codigo=row["codigo"],
            nombre=row["nombre"],
            menu_padre_id=row.get("menu_padre_id"),
            icono=row.get("icono"),
            orden=int(row.get("orden") or 0),
            estado=row.get("estado") or "ACTIVO",
        )
        for row in list_menus()
    ]
    return build_menu_tree(menus)


def dashboard_summary() -> dict[str, int]:
    resumen = fetch_one(
        """
        SELECT
          (SELECT COUNT(*) FROM usuarios) AS usuarios_totales,
          (SELECT COUNT(*) FROM roles) AS roles_creados,
          (SELECT COUNT(*) FROM modulos) AS modulos_disponibles,
          (SELECT COUNT(*) FROM sesiones WHERE estado = 'ACTIVA') AS sesiones_activas,
          (SELECT COUNT(*) FROM portales WHERE estado = 'ACTIVO') AS portales_conectados,
          (SELECT COUNT(*) FROM usuarios WHERE estado = 'ACTIVO') AS usuarios_activos,
          (SELECT COUNT(*) FROM usuarios WHERE estado <> 'ACTIVO') AS usuarios_inactivos,
          (SELECT COUNT(*) FROM roles WHERE estado = 'ACTIVO') AS roles_activos,
          (SELECT COUNT(*) FROM roles WHERE estado <> 'ACTIVO') AS roles_inactivos
        """
    )
    return {
        "usuarios_totales": int(resumen["usuarios_totales"] or 0),
        "roles_creados": int(resumen["roles_creados"] or 0),
        "modulos": int(resumen["modulos_disponibles"] or 0),
        "sesiones_activas": int(resumen["sesiones_activas"] or 0),
        "portales": int(resumen["portales_conectados"] or 0),
        "usuarios_activos": int(resumen["usuarios_activos"] or 0),
        "usuarios_inactivos": int(resumen["usuarios_inactivos"] or 0),
        "roles_activos": int(resumen["roles_activos"] or 0),
        "roles_inactivos": int(resumen["roles_inactivos"] or 0),
    }


def activity_rows(limit: int = 20) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT la.id, la.usuario_id, la.fecha_hora, la.accion, la.detalle, la.ip, la.equipo,
               COALESCE(u.nombre, 'Sistema') AS usuario
        FROM log_actividad la
        LEFT JOIN usuarios u ON u.id = la.usuario_id
        ORDER BY datetime(la.fecha_hora) DESC, la.id DESC
        LIMIT ?
        """,
        (limit,),
    )


def access_rows(limit: int = 25) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT la.*, COALESCE(u.nombre, 'Sistema') AS usuario, COALESCE(r.nombre, '') AS rol_nombre
        FROM log_accesos la
        LEFT JOIN usuarios u ON u.id = la.usuario_id
        LEFT JOIN roles r ON r.id = la.rol_id
        ORDER BY la.id DESC
        LIMIT ?
        """,
        (limit,),
    )


def add_activity(
    usuario_id: int | None,
    accion: str,
    detalle: str | None = None,
    ip: str | None = None,
    equipo: str | None = None,
) -> None:
    execute(
        """
        INSERT INTO log_actividad (usuario_id, fecha_hora, accion, detalle, ip, equipo)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (usuario_id, now_iso(), accion, detalle, ip, equipo),
    )


def add_access_log(payload: LogAccessPayload) -> int:
    return execute(
        """
        INSERT INTO log_accesos (
          usuario_id, rol_id, portal_id, modulo_id, menu_id, opcion_id,
          programa_nombre, programa_url, fecha_acceso, hora_inicio, hora_fin,
          duracion_segundos, estado, ip, equipo, navegador, mensaje_error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.usuario_id,
            payload.rol_id,
            payload.portal_id,
            payload.modulo_id,
            payload.menu_id,
            payload.opcion_id,
            payload.programa_nombre,
            payload.programa_url,
            now_date(),
            payload.hora_inicio or now_time(),
            payload.hora_fin,
            payload.duracion_segundos,
            payload.estado,
            payload.ip,
            payload.equipo,
            payload.navegador,
            payload.mensaje_error,
        ),
    )


def find_open_access_log(usuario_id: int, programa_url: str | None, programa_nombre: str | None) -> dict[str, Any] | None:
    url = (programa_url or "").strip()
    nombre = (programa_nombre or "").strip()
    if url:
        row = fetch_one(
            """
            SELECT *
            FROM log_accesos
            WHERE usuario_id = ? AND programa_url = ? AND hora_fin IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (usuario_id, url),
        )
        if row:
            return row
    if nombre:
        return fetch_one(
            """
            SELECT *
            FROM log_accesos
            WHERE usuario_id = ? AND programa_nombre = ? AND hora_fin IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (usuario_id, nombre),
        )
    return None


def close_access_log(payload: LogAccessPayload, estado: str) -> int:
    hora_inicio = (payload.hora_inicio or now_time()).strip()
    hora_fin = (payload.hora_fin or now_time()).strip()
    inicio_dt = parse_time_reference(hora_inicio)
    fin_dt = parse_time_reference(hora_fin)
    duracion = payload.duracion_segundos
    if duracion is None:
        duracion = int(max((fin_dt - inicio_dt).total_seconds(), 0))
    open_log = find_open_access_log(payload.usuario_id, payload.programa_url, payload.programa_nombre)
    if open_log:
        execute(
            """
            UPDATE log_accesos
            SET rol_id = ?, portal_id = ?, modulo_id = ?, menu_id = ?, opcion_id = ?,
                programa_nombre = ?, programa_url = ?, hora_inicio = ?, hora_fin = ?,
                duracion_segundos = ?, estado = ?, ip = ?, equipo = ?, navegador = ?,
                mensaje_error = ?
            WHERE id = ?
            """,
            (
                payload.rol_id,
                payload.portal_id,
                payload.modulo_id,
                payload.menu_id,
                payload.opcion_id,
                payload.programa_nombre,
                payload.programa_url,
                hora_inicio,
                hora_fin,
                duracion,
                estado,
                payload.ip,
                payload.equipo,
                payload.navegador,
                payload.mensaje_error,
                open_log["id"],
            ),
        )
        return int(open_log["id"])
    payload.hora_inicio = hora_inicio
    payload.hora_fin = hora_fin
    payload.duracion_segundos = duracion
    payload.estado = estado
    return add_access_log(payload)


def session_from_header(
    x_session_token: Annotated[Optional[str], Header(alias="X-Session-Token")] = None,
) -> dict[str, Any]:
    token = (x_session_token or "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Sesion requerida.")
    session = SESSION_CACHE.get(token)
    if session is None:
        session_row = get_session_by_token(token)
        if session_row and normalize_estado(session_row.get("estado"), "ACTIVA") == "ACTIVA":
            if is_session_expired(session_row):
                expire_session(token, session_row)
                raise HTTPException(status_code=401, detail="Sesion expirada. Vuelve a iniciar sesion.")
            session = {
                "token": token,
                "usuario_id": int(session_row["usuario_id"]),
                "nombre": session_row.get("usuario_nombre") or "",
                "correo": session_row.get("usuario_correo") or "",
                "inicio": session_row.get("inicio") or now_iso(),
                "ip": session_row.get("ip"),
                "equipo": session_row.get("equipo"),
                "navegador": session_row.get("navegador"),
            }
            SESSION_CACHE[token] = session
    if session is None:
        raise HTTPException(status_code=401, detail="Sesion invalida o expirada.")
    return session


def close_existing_sessions(usuario_id: int, keep_token: str | None = None) -> None:
    active_sessions = fetch_all(
        "SELECT token FROM sesiones WHERE usuario_id = ? AND estado = 'ACTIVA'",
        (usuario_id,),
    )
    for row in active_sessions:
        token = str(row.get("token") or "").strip()
        if not token or token == keep_token:
            continue
        execute(
            """
            UPDATE sesiones
            SET fin = ?, estado = 'CERRADA'
            WHERE token = ? AND estado = 'ACTIVA'
            """,
            (now_iso(), token),
        )
        SESSION_CACHE.pop(token, None)


def unique_email_exists(correo: str, usuario_id: int | None = None) -> bool:
    params: tuple[Any, ...]
    if usuario_id is None:
        params = (correo,)
        sql = "SELECT 1 FROM usuarios WHERE lower(correo) = lower(?) LIMIT 1"
    else:
        params = (correo, usuario_id)
        sql = "SELECT 1 FROM usuarios WHERE lower(correo) = lower(?) AND id <> ? LIMIT 1"
    return fetch_one(sql, params) is not None


def get_user_by_id(usuario_id: int) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT id, nombre, correo, cargo, estado, avatar_url, fecha_creacion, ultimo_acceso, password_hash
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,),
    )


def get_role_by_id(rol_id: int) -> dict[str, Any] | None:
    return fetch_one("SELECT id, codigo, nombre, descripcion, estado FROM roles WHERE id = ?", (rol_id,))


def get_group_by_id(grupo_id: int) -> dict[str, Any] | None:
    return fetch_one("SELECT id, codigo, nombre, descripcion, estado FROM grupos WHERE id = ?", (grupo_id,))


def get_menu_by_id(menu_id: int) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT id, portal_id, modulo_id, menu_padre_id, codigo, nombre, icono, orden, estado,
               url, componente, abre_nueva_pestana, requiere_log
        FROM menus
        WHERE id = ?
        """,
        (menu_id,),
    )


def validate_active_row(row: dict[str, Any] | None, entity_name: str) -> dict[str, Any]:
    if row is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} no encontrado.")
    return row


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "app_env": SETTINGS.app_env,
        "db_url": SETTINGS.db_url,
        "usuario_sistema": SETTINGS.usuario_sistema,
        "root_dir": str(ROOT_DIR),
        "frontend_ready": FRONTEND_DIR.exists(),
    }


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/portal", include_in_schema=False)
def portal() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/docs/openapi.json", include_in_schema=False)
def openapi_json() -> dict[str, Any]:
    return app.openapi()


def load_assets() -> None:
    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=True), name="assets")


load_assets()


@app.post("/api/auth/login")
def login(payload: LoginPayload) -> dict[str, Any]:
    user_row = fetch_one(
        "SELECT id FROM usuarios WHERE lower(correo) = lower(?) LIMIT 1",
        (payload.correo.strip(),),
    )
    user = get_user_by_id(int(user_row["id"])) if user_row else None
    if user is None or normalize_estado(user["estado"]) != "ACTIVO":
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")
    password_hash = user.get("password_hash") or ""
    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    close_existing_sessions(int(user["id"]))
    token = generate_token()
    roles = get_user_roles(int(user["id"]))
    groups = get_user_groups(int(user["id"]))
    started_at = now_iso()
    session_payload = {
        "token": token,
        "usuario_id": int(user["id"]),
        "nombre": user["nombre"],
        "correo": user["correo"],
        "roles": [role["nombre"] for role in roles],
        "grupos": [group["nombre"] for group in groups],
        "inicio": started_at,
        "estado": "ACTIVA",
    }
    SESSION_CACHE[token] = session_payload
    execute(
        """
        INSERT INTO sesiones (token, usuario_id, inicio, fin, estado, ip, equipo, navegador)
        VALUES (?, ?, ?, NULL, 'ACTIVA', ?, ?, ?)
        """,
        (token, user["id"], started_at, None, None, None),
    )
    execute(
        "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?",
        (started_at, user["id"]),
    )
    add_activity(int(user["id"]), "Inicio de sesion", "Inicio de sesion exitoso")
    add_access_log(
        LogAccessPayload(
            usuario_id=int(user["id"]),
            rol_id=roles[0]["id"] if roles else None,
            portal_id=1,
            modulo_id=1,
            menu_id=1,
            opcion_id=1,
            programa_nombre="Login",
            programa_url="/api/auth/login",
            hora_inicio=now_time(),
            hora_fin=now_time(),
            duracion_segundos=0,
            estado="EXITOSO",
            ip="127.0.0.1",
            equipo="localhost",
            navegador="backend",
        )
    )
    return {
        "token": token,
        "usuario_id": user["id"],
        "nombre": user["nombre"],
        "correo": user["correo"],
        "roles": [role["nombre"] for role in roles],
        "grupos": [group["nombre"] for group in groups],
    }


@app.post("/api/auth/logout")
def logout(session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    token = session.get("token") or next((key for key, value in SESSION_CACHE.items() if value == session), None)
    if token:
        SESSION_CACHE.pop(token, None)
    execute(
        """
        UPDATE sesiones
        SET fin = ?, estado = 'CERRADA'
        WHERE token = ? AND estado = 'ACTIVA'
        """,
        (now_iso(), token),
    )
    add_activity(session["usuario_id"], "Cierre de sesion", "Sesion finalizada por el usuario")
    return {"status": "cerrado"}


@app.get("/api/auth/session")
def current_session(session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    return session


@app.get("/api/dashboard/resumen")
def get_dashboard_summary() -> dict[str, int]:
    return dashboard_summary()


@app.get("/api/usuarios")
def get_users() -> list[dict[str, Any]]:
    return list_users()


@app.post("/api/usuarios")
def create_user(payload: UsuarioCreate, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    nombre = payload.nombre.strip()
    correo = payload.correo.strip().lower()
    cargo = (payload.cargo or "").strip() or None
    estado = normalize_estado(payload.estado)
    if not is_valid_email(correo):
        raise HTTPException(status_code=422, detail="Correo invalido.")
    if unique_email_exists(correo):
        raise HTTPException(status_code=409, detail="El correo ya existe.")
    password_hash = hash_password(payload.password_plain) if payload.password_plain else None
    usuario_id = execute(
        """
        INSERT INTO usuarios (nombre, correo, password_hash, cargo, estado, avatar_url, fecha_creacion, ultimo_acceso)
        VALUES (?, ?, ?, ?, ?, NULL, ?, NULL)
        """,
        (nombre, correo, password_hash, cargo, estado, now_iso()),
    )
    add_activity(session["usuario_id"], "Creacion de usuario", f"Se creo el usuario {correo}")
    return validate_active_row(get_user_by_id(usuario_id), "Usuario")


@app.put("/api/usuarios/{usuario_id}")
def update_user(
    usuario_id: int,
    payload: UsuarioUpdate,
    session: dict[str, Any] = Depends(session_from_header),
) -> dict[str, Any]:
    current = validate_active_row(get_user_by_id(usuario_id), "Usuario")
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    correo = payload.correo.strip().lower() if payload.correo is not None else current["correo"]
    cargo = payload.cargo.strip() if payload.cargo is not None else current.get("cargo")
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_email(correo):
        raise HTTPException(status_code=422, detail="Correo invalido.")
    if unique_email_exists(correo, usuario_id):
        raise HTTPException(status_code=409, detail="El correo ya existe.")
    password_hash = current.get("password_hash")
    if payload.password_plain:
        password_hash = hash_password(payload.password_plain)
    execute(
        """
        UPDATE usuarios
        SET nombre = ?, correo = ?, password_hash = ?, cargo = ?, estado = ?
        WHERE id = ?
        """,
        (nombre, correo, password_hash, cargo, estado, usuario_id),
    )
    add_activity(session["usuario_id"], "Actualizacion de usuario", f"Usuario {usuario_id} actualizado")
    return validate_active_row(get_user_by_id(usuario_id), "Usuario")


@app.delete("/api/usuarios/{usuario_id}")
def delete_user(usuario_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_user_by_id(usuario_id), "Usuario")
    execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    add_activity(session["usuario_id"], "Eliminacion de usuario", f"Usuario {usuario_id} eliminado")
    return {"status": "eliminado"}


@app.get("/api/usuarios/{usuario_id}/asignaciones")
def get_user_assignments(usuario_id: int) -> dict[str, Any]:
    validate_active_row(get_user_by_id(usuario_id), "Usuario")
    return {
        "usuario_id": usuario_id,
        "roles": get_user_roles(usuario_id),
        "grupos": get_user_groups(usuario_id),
    }


@app.post("/api/usuarios/{usuario_id}/roles")
def assign_role(usuario_id: int, payload: AssignmentPayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    if payload.rol_id is None:
        raise HTTPException(status_code=422, detail="rol_id requerido.")
    validate_active_row(get_user_by_id(usuario_id), "Usuario")
    validate_active_row(get_role_by_id(payload.rol_id), "Rol")
    execute(
        "INSERT OR IGNORE INTO usuarios_roles (usuario_id, rol_id) VALUES (?, ?)",
        (usuario_id, payload.rol_id),
    )
    add_activity(session["usuario_id"], "Asignacion de rol", f"Rol {payload.rol_id} asignado al usuario {usuario_id}")
    return {"status": "asignado"}


@app.delete("/api/usuarios/{usuario_id}/roles/{rol_id}")
def remove_role(usuario_id: int, rol_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    execute("DELETE FROM usuarios_roles WHERE usuario_id = ? AND rol_id = ?", (usuario_id, rol_id))
    add_activity(session["usuario_id"], "Desasignacion de rol", f"Rol {rol_id} retirado del usuario {usuario_id}")
    return {"status": "retirado"}


@app.post("/api/usuarios/{usuario_id}/grupos")
def assign_group(usuario_id: int, payload: AssignmentPayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    if payload.grupo_id is None:
        raise HTTPException(status_code=422, detail="grupo_id requerido.")
    validate_active_row(get_user_by_id(usuario_id), "Usuario")
    validate_active_row(get_group_by_id(payload.grupo_id), "Grupo")
    execute(
        "INSERT OR IGNORE INTO usuarios_grupos (usuario_id, grupo_id) VALUES (?, ?)",
        (usuario_id, payload.grupo_id),
    )
    add_activity(session["usuario_id"], "Asignacion de grupo", f"Grupo {payload.grupo_id} asignado al usuario {usuario_id}")
    return {"status": "asignado"}


@app.delete("/api/usuarios/{usuario_id}/grupos/{grupo_id}")
def remove_group(usuario_id: int, grupo_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    execute("DELETE FROM usuarios_grupos WHERE usuario_id = ? AND grupo_id = ?", (usuario_id, grupo_id))
    add_activity(session["usuario_id"], "Desasignacion de grupo", f"Grupo {grupo_id} retirado del usuario {usuario_id}")
    return {"status": "retirado"}


@app.get("/api/roles")
def get_roles() -> list[dict[str, Any]]:
    return list_roles()


@app.post("/api/roles")
def create_role(payload: RolePayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    codigo = payload.codigo.strip().upper()
    nombre = payload.nombre.strip()
    descripcion = (payload.descripcion or "").strip() or None
    estado = normalize_estado(payload.estado)
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de rol invalido.")
    if fetch_one("SELECT 1 FROM roles WHERE codigo = ? LIMIT 1", (codigo,)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de rol ya existe.")
    rol_id = execute(
        "INSERT INTO roles (codigo, nombre, descripcion, estado) VALUES (?, ?, ?, ?)",
        (codigo, nombre, descripcion, estado),
    )
    add_activity(session["usuario_id"], "Creacion de rol", f"Rol {codigo} creado")
    return validate_active_row(get_role_by_id(rol_id), "Rol")


@app.put("/api/roles/{rol_id}")
def update_role(rol_id: int, payload: RoleUpdatePayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    current = validate_active_row(get_role_by_id(rol_id), "Rol")
    codigo = payload.codigo.strip().upper() if payload.codigo is not None else current["codigo"]
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    descripcion = payload.descripcion.strip() if payload.descripcion is not None else current.get("descripcion")
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de rol invalido.")
    if fetch_one("SELECT 1 FROM roles WHERE codigo = ? AND id <> ? LIMIT 1", (codigo, rol_id)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de rol ya existe.")
    execute(
        "UPDATE roles SET codigo = ?, nombre = ?, descripcion = ?, estado = ? WHERE id = ?",
        (codigo, nombre, descripcion, estado, rol_id),
    )
    add_activity(session["usuario_id"], "Actualizacion de rol", f"Rol {rol_id} actualizado")
    return validate_active_row(get_role_by_id(rol_id), "Rol")


@app.delete("/api/roles/{rol_id}")
def delete_role(rol_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_role_by_id(rol_id), "Rol")
    execute("DELETE FROM roles WHERE id = ?", (rol_id,))
    add_activity(session["usuario_id"], "Eliminacion de rol", f"Rol {rol_id} eliminado")
    return {"status": "eliminado"}


@app.get("/api/grupos")
def get_groups() -> list[dict[str, Any]]:
    return list_groups()


@app.post("/api/grupos")
def create_group(payload: GroupPayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    codigo = payload.codigo.strip().upper()
    nombre = payload.nombre.strip()
    descripcion = (payload.descripcion or "").strip() or None
    estado = normalize_estado(payload.estado)
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de grupo invalido.")
    if fetch_one("SELECT 1 FROM grupos WHERE codigo = ? LIMIT 1", (codigo,)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de grupo ya existe.")
    grupo_id = execute(
        "INSERT INTO grupos (codigo, nombre, descripcion, estado) VALUES (?, ?, ?, ?)",
        (codigo, nombre, descripcion, estado),
    )
    add_activity(session["usuario_id"], "Creacion de grupo", f"Grupo {codigo} creado")
    return validate_active_row(get_group_by_id(grupo_id), "Grupo")


@app.put("/api/grupos/{grupo_id}")
def update_group(
    grupo_id: int,
    payload: GroupUpdatePayload,
    session: dict[str, Any] = Depends(session_from_header),
) -> dict[str, Any]:
    current = validate_active_row(get_group_by_id(grupo_id), "Grupo")
    codigo = payload.codigo.strip().upper() if payload.codigo is not None else current["codigo"]
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    descripcion = payload.descripcion.strip() if payload.descripcion is not None else current.get("descripcion")
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de grupo invalido.")
    if fetch_one("SELECT 1 FROM grupos WHERE codigo = ? AND id <> ? LIMIT 1", (codigo, grupo_id)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de grupo ya existe.")
    execute(
        "UPDATE grupos SET codigo = ?, nombre = ?, descripcion = ?, estado = ? WHERE id = ?",
        (codigo, nombre, descripcion, estado, grupo_id),
    )
    add_activity(session["usuario_id"], "Actualizacion de grupo", f"Grupo {grupo_id} actualizado")
    return validate_active_row(get_group_by_id(grupo_id), "Grupo")


@app.delete("/api/grupos/{grupo_id}")
def delete_group(grupo_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_group_by_id(grupo_id), "Grupo")
    execute("DELETE FROM grupos WHERE id = ?", (grupo_id,))
    add_activity(session["usuario_id"], "Eliminacion de grupo", f"Grupo {grupo_id} eliminado")
    return {"status": "eliminado"}


@app.get("/api/menus")
def get_menus() -> list[dict[str, Any]]:
    return list_menus()


@app.get("/api/menus/arbol")
def get_menu_tree() -> list[dict[str, object]]:
    return list_menu_tree()


@app.post("/api/menus")
def create_menu(payload: MenuPayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    codigo = payload.codigo.strip().upper()
    nombre = payload.nombre.strip()
    estado = normalize_estado(payload.estado)
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de menu invalido.")
    if fetch_one("SELECT 1 FROM menus WHERE codigo = ? LIMIT 1", (codigo,)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de menu ya existe.")
    menu_id = execute(
        """
        INSERT INTO menus (
          portal_id, modulo_id, menu_padre_id, codigo, nombre, icono, orden, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.portal_id,
            payload.modulo_id,
            payload.menu_padre_id,
            codigo,
            nombre,
            payload.icono,
            payload.orden,
            estado,
        ),
    )
    add_activity(session["usuario_id"], "Creacion de menu", f"Menu {codigo} creado")
    return validate_active_row(get_menu_by_id(menu_id), "Menu")


@app.put("/api/menus/{menu_id}")
def update_menu(
    menu_id: int,
    payload: MenuPayload,
    session: dict[str, Any] = Depends(session_from_header),
) -> dict[str, Any]:
    current = validate_active_row(get_menu_by_id(menu_id), "Menu")
    codigo = payload.codigo.strip().upper() if payload.codigo is not None else current["codigo"]
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de menu invalido.")
    if fetch_one("SELECT 1 FROM menus WHERE codigo = ? AND id <> ? LIMIT 1", (codigo, menu_id)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de menu ya existe.")
    execute(
        """
        UPDATE menus
        SET portal_id = ?, modulo_id = ?, menu_padre_id = ?, codigo = ?, nombre = ?, icono = ?, orden = ?, estado = ?
        WHERE id = ?
        """,
        (
            payload.portal_id,
            payload.modulo_id,
            payload.menu_padre_id,
            codigo,
            nombre,
            payload.icono,
            payload.orden,
            estado,
            menu_id,
        ),
    )
    add_activity(session["usuario_id"], "Actualizacion de menu", f"Menu {menu_id} actualizado")
    return validate_active_row(get_menu_by_id(menu_id), "Menu")


@app.delete("/api/menus/{menu_id}")
def delete_menu(menu_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_menu_by_id(menu_id), "Menu")
    execute("DELETE FROM menus WHERE id = ?", (menu_id,))
    add_activity(session["usuario_id"], "Eliminacion de menu", f"Menu {menu_id} eliminado")
    return {"status": "eliminado"}


@app.get("/api/modulos")
def get_modules() -> list[dict[str, Any]]:
    return list_modules()


@app.post("/api/modulos")
def create_module(payload: ModulePayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    portal = validate_active_row(fetch_one("SELECT id, nombre FROM portales WHERE id = ?", (payload.portal_id,)), "Portal")
    codigo = payload.codigo.strip().upper()
    nombre = payload.nombre.strip()
    descripcion = (payload.descripcion or "").strip() or None
    icono = (payload.icono or "").strip() or None
    estado = normalize_estado(payload.estado)
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de modulo invalido.")
    if fetch_one("SELECT 1 FROM modulos WHERE codigo = ? LIMIT 1", (codigo,)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de modulo ya existe.")
    modulo_id = execute(
        "INSERT INTO modulos (portal_id, codigo, nombre, descripcion, icono, estado) VALUES (?, ?, ?, ?, ?, ?)",
        (portal["id"], codigo, nombre, descripcion, icono, estado),
    )
    add_activity(session["usuario_id"], "Creacion de modulo", f"Modulo {codigo} creado")
    return validate_active_row(get_module_by_id(modulo_id), "Modulo")


@app.put("/api/modulos/{modulo_id}")
def update_module(
    modulo_id: int,
    payload: ModuleUpdatePayload,
    session: dict[str, Any] = Depends(session_from_header),
) -> dict[str, Any]:
    current = validate_active_row(get_module_by_id(modulo_id), "Modulo")
    portal_id = payload.portal_id if payload.portal_id is not None else current["portal_id"]
    portal = validate_active_row(fetch_one("SELECT id, nombre FROM portales WHERE id = ?", (portal_id,)), "Portal")
    codigo = payload.codigo.strip().upper() if payload.codigo is not None else current["codigo"]
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    descripcion = payload.descripcion.strip() if payload.descripcion is not None else current.get("descripcion")
    icono = payload.icono.strip() if payload.icono is not None else current.get("icono")
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de modulo invalido.")
    if fetch_one("SELECT 1 FROM modulos WHERE codigo = ? AND id <> ? LIMIT 1", (codigo, modulo_id)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de modulo ya existe.")
    execute(
        "UPDATE modulos SET portal_id = ?, codigo = ?, nombre = ?, descripcion = ?, icono = ?, estado = ? WHERE id = ?",
        (portal["id"], codigo, nombre, descripcion, icono, estado, modulo_id),
    )
    add_activity(session["usuario_id"], "Actualizacion de modulo", f"Modulo {modulo_id} actualizado")
    return validate_active_row(get_module_by_id(modulo_id), "Modulo")


@app.delete("/api/modulos/{modulo_id}")
def delete_module(modulo_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_module_by_id(modulo_id), "Modulo")
    execute("DELETE FROM modulos WHERE id = ?", (modulo_id,))
    add_activity(session["usuario_id"], "Eliminacion de modulo", f"Modulo {modulo_id} eliminado")
    return {"status": "eliminado"}


@app.get("/api/opciones")
def get_options() -> list[dict[str, Any]]:
    return list_options()


@app.post("/api/opciones")
def create_option(payload: OptionPayload, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    validate_active_row(get_menu_by_id(payload.menu_id), "Menu")
    codigo = payload.codigo.strip().upper()
    nombre = payload.nombre.strip()
    tipo = payload.tipo.strip().upper()
    estado = normalize_estado(payload.estado)
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de opcion invalido.")
    if fetch_one("SELECT 1 FROM opciones_programa WHERE codigo = ? LIMIT 1", (codigo,)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de opcion ya existe.")
    option_id = execute(
        """
        INSERT INTO opciones_programa (
          menu_id, codigo, nombre, tipo, url, componente, abre_nueva_pestana, requiere_log, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.menu_id,
            codigo,
            nombre,
            tipo,
            (payload.url or "").strip() or None,
            (payload.componente or "").strip() or None,
            1 if payload.abre_nueva_pestana else 0,
            1 if payload.requiere_log else 0,
            estado,
        ),
    )
    add_activity(session["usuario_id"], "Creacion de opcion", f"Opcion {codigo} creada")
    return validate_active_row(get_option_by_id(option_id), "Opcion")


@app.put("/api/opciones/{opcion_id}")
def update_option(
    opcion_id: int,
    payload: OptionUpdatePayload,
    session: dict[str, Any] = Depends(session_from_header),
) -> dict[str, Any]:
    current = validate_active_row(get_option_by_id(opcion_id), "Opcion")
    menu_id = payload.menu_id if payload.menu_id is not None else current["menu_id"]
    validate_active_row(get_menu_by_id(int(menu_id)), "Menu")
    codigo = payload.codigo.strip().upper() if payload.codigo is not None else current["codigo"]
    nombre = payload.nombre.strip() if payload.nombre is not None else current["nombre"]
    tipo = payload.tipo.strip().upper() if payload.tipo is not None else current["tipo"]
    estado = normalize_estado(payload.estado, current["estado"]) if payload.estado is not None else current["estado"]
    if not is_valid_code(codigo):
        raise HTTPException(status_code=422, detail="Codigo de opcion invalido.")
    if fetch_one("SELECT 1 FROM opciones_programa WHERE codigo = ? AND id <> ? LIMIT 1", (codigo, opcion_id)) is not None:
        raise HTTPException(status_code=409, detail="El codigo de opcion ya existe.")
    execute(
        """
        UPDATE opciones_programa
        SET menu_id = ?, codigo = ?, nombre = ?, tipo = ?, url = ?, componente = ?,
            abre_nueva_pestana = ?, requiere_log = ?, estado = ?
        WHERE id = ?
        """,
        (
            menu_id,
            codigo,
            nombre,
            tipo,
            (payload.url.strip() if payload.url is not None else current.get("url")),
            (payload.componente.strip() if payload.componente is not None else current.get("componente")),
            int(payload.abre_nueva_pestana) if payload.abre_nueva_pestana is not None else int(current.get("abre_nueva_pestana") or 0),
            int(payload.requiere_log) if payload.requiere_log is not None else int(current.get("requiere_log") or 1),
            estado,
            opcion_id,
        ),
    )
    add_activity(session["usuario_id"], "Actualizacion de opcion", f"Opcion {opcion_id} actualizada")
    return validate_active_row(get_option_by_id(opcion_id), "Opcion")


@app.delete("/api/opciones/{opcion_id}")
def delete_option(opcion_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    validate_active_row(get_option_by_id(opcion_id), "Opcion")
    execute("DELETE FROM opciones_programa WHERE id = ?", (opcion_id,))
    add_activity(session["usuario_id"], "Eliminacion de opcion", f"Opcion {opcion_id} eliminada")
    return {"status": "eliminado"}


@app.get("/api/sesiones")
def get_sessions() -> list[dict[str, Any]]:
    return list_sessions()


@app.get("/api/sesiones/activas")
def get_active_sessions() -> list[dict[str, Any]]:
    return [row for row in list_sessions() if normalize_estado(row.get("estado"), "ACTIVA") == "ACTIVA"]


@app.post("/api/sesiones/{sesion_id}/cerrar")
def close_session(sesion_id: int, session: dict[str, Any] = Depends(session_from_header)) -> dict[str, str]:
    target = validate_active_row(fetch_one("SELECT id, token FROM sesiones WHERE id = ?", (sesion_id,)), "Sesion")
    token = str(target.get("token") or "").strip()
    execute(
        """
        UPDATE sesiones
        SET fin = ?, estado = 'CERRADA'
        WHERE id = ? AND estado = 'ACTIVA'
        """,
        (now_iso(), sesion_id),
    )
    if token:
        SESSION_CACHE.pop(token, None)
    add_activity(session["usuario_id"], "Cierre de sesion", f"Sesion {sesion_id} cerrada")
    return {"status": "cerrado"}


@app.get("/api/permisos/matriz")
def get_permissions_matrix() -> dict[str, Any]:
    portals = list_portals()
    headers = ["Modulo / Portal"] + [portal["nombre"] for portal in portals]
    module_rows = list_modules()
    rows = []
    for module in module_rows:
        cells = []
        for portal in portals:
            same_portal = int(module["portal_id"]) == int(portal["id"])
            if same_portal:
                permission = ALLOWED
            elif "Reportes" in portal["nombre"] and "Reportes" not in module["nombre"]:
                permission = READ_ONLY
            elif "RRHH" in portal["nombre"] and module["nombre"] in {"Produccion", "Inventario"}:
                permission = DENIED
            else:
                permission = READ_ONLY if portal["codigo"] == "COMPRAS" else ALLOWED
            cells.append(permission)
        rows.append(
            {
                "module": module["nombre"],
                "cells": cells,
            }
        )
    return {"headers": headers, "rows": rows}


@app.get("/api/logs/actividad")
def get_activity(limit: int = 20) -> list[dict[str, Any]]:
    return activity_rows(limit)


@app.get("/api/log-accesos")
def get_access_logs(limit: int = 25) -> list[dict[str, Any]]:
    return access_rows(limit)


@app.post("/api/log-accesos/inicio")
def register_access_start(payload: LogAccessPayload) -> dict[str, Any]:
    payload.hora_inicio = payload.hora_inicio or now_time()
    payload.estado = payload.estado or "EN_PROGRESO"
    log_id = add_access_log(payload)
    add_activity(payload.usuario_id, "Acceso a modulo", payload.programa_nombre or "Acceso registrado", payload.ip, payload.equipo)
    return {"status": "registrado", "id": log_id}


@app.post("/api/log-accesos/fin")
def register_access_end(payload: LogAccessPayload) -> dict[str, Any]:
    payload.hora_fin = payload.hora_fin or now_time()
    estado = payload.estado or "EXITOSO"
    log_id = close_access_log(payload, estado)
    return {"status": "cerrado", "id": log_id}


@app.get("/api/portal/estado")
def portal_state() -> dict[str, Any]:
    return {
        "portal": "Portal Corporativo",
        "subportal": "Accesos Menues",
        "raiz": str(ROOT_DIR),
        "frontend": str(FRONTEND_DIR),
        "database": str(DB_PATH),
        "menus": len(list_menus()),
        "roles": len(list_roles()),
        "usuarios": len(list_users()),
    }


@app.get("/api/portal/contexto")
def portal_context(session: dict[str, Any] = Depends(session_from_header)) -> dict[str, Any]:
    user_id = int(session["usuario_id"])
    user = validate_active_row(get_user_by_id(user_id), "Usuario")
    roles = get_user_roles(user_id)
    groups = get_user_groups(user_id)
    menu_tree = list_menu_tree()
    permissions = get_permissions_matrix()
    resumen = dashboard_summary()
    return {
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "correo": user["correo"],
            "cargo": user["cargo"],
            "estado": user["estado"],
        },
        "roles": roles,
        "grupos": groups,
        "portal_principal": pick_portal(roles),
        "menu_arbol": menu_tree,
        "permisos": permissions,
        "resumen": resumen,
        "estado": portal_state(),
        "notificaciones": [
            {
                "titulo": "Permisos sincronizados",
                "detalle": "El portal madre refleja tus roles y grupos actuales.",
                "nivel": "success",
            },
            {
                "titulo": "Acceso directo",
                "detalle": "Usuarios y Accesos esta disponible como primer subportal.",
                "nivel": "info",
            },
        ],
        "acciones_rapidas": [
            {"titulo": "Usuarios", "descripcion": "Gestion de cuentas"},
            {"titulo": "Roles", "descripcion": "Perfiles autorizados"},
            {"titulo": "Menus", "descripcion": "Navegacion corporativa"},
            {"titulo": "Permisos", "descripcion": "Accesos por rol y grupo"},
        ],
    }


@app.get("/api/usuarios/{usuario_id}/contexto")
def user_context(usuario_id: int) -> dict[str, Any]:
    user = validate_active_row(get_user_by_id(usuario_id), "Usuario")
    roles = get_user_roles(usuario_id)
    groups = get_user_groups(usuario_id)
    return {
        "usuario": user,
        "roles": roles,
        "grupos": groups,
        "portal_principal": pick_portal(roles),
    }
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
