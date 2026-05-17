from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn


BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

app = FastAPI(
    title="Accesos Menues",
    version="0.1.0",
    description="Tablero madre de usuarios, roles, grupos, menús y permisos.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app_env": os.getenv("APP_ENV", "unknown"),
        "db_url": os.getenv("DB_URL", ""),
        "usuario_sistema": os.getenv("USUARIO_SISTEMA", ""),
    }


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Accesos Menues API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
