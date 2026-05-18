from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


@dataclass(frozen=True)
class PlatformSettings:
    root_dir: Path
    app_env: str = "dev"
    headless: bool = False
    log_level: str = "INFO"
    db_url: str = "sqlite:///./data/app.db"
    usuario_sistema: str = ""
    cors_origins: str = "*"
    session_ttl_hours: int = 8


def load_settings(root_dir: Path | None = None) -> PlatformSettings:
    root = root_dir or Path(__file__).resolve().parents[3]
    values = dotenv_values(root / ".env")
    return PlatformSettings(
        root_dir=root,
        app_env=str(values.get("APP_ENV", "dev")),
        headless=str(values.get("HEADLESS", "false")).lower() == "true",
        log_level=str(values.get("LOG_LEVEL", "INFO")),
        db_url=str(values.get("DB_URL", "sqlite:///./data/app.db")),
        usuario_sistema=str(values.get("USUARIO_SISTEMA", "")),
        cors_origins=str(values.get("CORS_ORIGINS", "*")),
        session_ttl_hours=int(values.get("SESSION_TTL_HOURS", 8)),
    )
