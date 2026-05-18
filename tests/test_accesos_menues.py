from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "apps" / "accesos-menues" / "backend" / "main.py"

spec = spec_from_file_location("accesos_menues_main", MODULE_PATH)
assert spec and spec.loader
module = module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "db_url" in payload


def test_dashboard_summary() -> None:
    response = client.get("/api/dashboard/resumen")
    assert response.status_code == 200
    payload = response.json()
    assert "usuarios_totales" in payload
    assert "roles_creados" in payload


def test_roles_listing() -> None:
    response = client.get("/api/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_login_and_create_user_with_session() -> None:
    unique_email = f"qa.test.{uuid4().hex[:8]}@empresa.com"
    login_response = client.post(
        "/api/auth/login",
        json={"correo": "joseph@empresa.com", "password": "Plataforma123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    create_response = client.post(
        "/api/usuarios",
        headers={"X-Session-Token": token},
        json={
            "nombre": "QA Test",
            "correo": unique_email,
            "cargo": "Analista",
            "estado": "ACTIVO",
        },
    )
    assert create_response.status_code == 200


def test_assign_role_and_group_to_user() -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"correo": "joseph@empresa.com", "password": "Plataforma123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    assign_role = client.post(
        "/api/usuarios/1/roles",
        headers={"X-Session-Token": token},
        json={"rol_id": 2},
    )
    assert assign_role.status_code == 200
    assign_group = client.post(
        "/api/usuarios/1/grupos",
        headers={"X-Session-Token": token},
        json={"grupo_id": 2},
    )
    assert assign_group.status_code == 200
    assigned = client.get("/api/usuarios/1/asignaciones")
    assert assigned.status_code == 200
    payload = assigned.json()
    assert isinstance(payload["roles"], list)
    assert isinstance(payload["grupos"], list)
