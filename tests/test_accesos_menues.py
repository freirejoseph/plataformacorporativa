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


def test_module_option_and_access_duration_crud() -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"correo": "joseph@empresa.com", "password": "Plataforma123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    module_code = f"QA_MOD_{uuid4().hex[:8].upper()}"
    module_create = client.post(
        "/api/modulos",
        headers={"X-Session-Token": token},
        json={
            "portal_id": 1,
            "codigo": module_code,
            "nombre": "Modulo QA",
            "descripcion": "Modulo de prueba",
            "icono": "cube",
            "estado": "ACTIVO",
        },
    )
    assert module_create.status_code == 200
    module_id = module_create.json()["id"]

    module_update = client.put(
        f"/api/modulos/{module_id}",
        headers={"X-Session-Token": token},
        json={"nombre": "Modulo QA Actualizado"},
    )
    assert module_update.status_code == 200
    assert module_update.json()["nombre"] == "Modulo QA Actualizado"

    menu_response = client.get("/api/menus")
    assert menu_response.status_code == 200
    menu_id = menu_response.json()[0]["id"]

    option_code = f"QA_OPT_{uuid4().hex[:8].upper()}"
    option_create = client.post(
        "/api/opciones",
        headers={"X-Session-Token": token},
        json={
            "menu_id": menu_id,
            "codigo": option_code,
            "nombre": "Opcion QA",
            "tipo": "PROGRAMA",
            "url": "/qa",
            "componente": "QAComponent",
            "abre_nueva_pestana": False,
            "requiere_log": True,
            "estado": "ACTIVO",
        },
    )
    assert option_create.status_code == 200
    option_id = option_create.json()["id"]

    option_update = client.put(
        f"/api/opciones/{option_id}",
        headers={"X-Session-Token": token},
        json={"nombre": "Opcion QA Actualizada"},
    )
    assert option_update.status_code == 200
    assert option_update.json()["nombre"] == "Opcion QA Actualizada"

    access_name = f"Programa QA {uuid4().hex[:8]}"
    access_start = client.post(
        "/api/log-accesos/inicio",
        json={
            "usuario_id": 1,
            "rol_id": 1,
            "portal_id": 1,
            "modulo_id": module_id,
            "menu_id": menu_id,
            "opcion_id": option_id,
            "programa_nombre": access_name,
            "programa_url": "/qa/programa",
            "hora_inicio": "08:00:00",
            "estado": "EN_PROGRESO",
        },
    )
    assert access_start.status_code == 200

    access_end = client.post(
        "/api/log-accesos/fin",
        json={
            "usuario_id": 1,
            "rol_id": 1,
            "portal_id": 1,
            "modulo_id": module_id,
            "menu_id": menu_id,
            "opcion_id": option_id,
            "programa_nombre": access_name,
            "programa_url": "/qa/programa",
            "hora_inicio": "08:00:00",
            "hora_fin": "08:05:00",
            "estado": "EXITOSO",
        },
    )
    assert access_end.status_code == 200

    access_logs = client.get("/api/log-accesos").json()
    matching = next((row for row in access_logs if row["programa_url"] == "/qa/programa"), None)
    assert matching is not None
    assert int(matching["duracion_segundos"] or 0) >= 300

    client.delete(f"/api/opciones/{option_id}", headers={"X-Session-Token": token})
    client.delete(f"/api/modulos/{module_id}", headers={"X-Session-Token": token})
