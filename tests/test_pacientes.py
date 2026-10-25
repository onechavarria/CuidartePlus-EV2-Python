import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


@pytest.fixture
def service(load_service, monkeypatch):
    main = load_service("pacientes")
    patient = {"id": 5, "usuario_id": 1, "nombre": "Ana Pérez", "rut": None, "telefono": None}
    monkeypatch.setattr(main.db, "query_one", lambda *args: patient)
    monkeypatch.setattr(main.db, "query_all", lambda *args: [patient])
    return main


@pytest.fixture
def headers():
    token = jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "test_secret_value_for_unit_tests", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_sin_token(service):
    assert TestClient(service.app).get("/pacientes").status_code == 401


def test_token_invalido(service):
    assert TestClient(service.app).get("/pacientes", headers={"Authorization": "Bearer falso"}).status_code == 401


def test_listar(service, headers):
    assert len(TestClient(service.app).get("/pacientes", headers=headers).json()) == 1


def test_obtener(service, headers):
    assert TestClient(service.app).get("/pacientes/5", headers=headers).status_code == 200


def test_obtener_no_existe(service, headers, monkeypatch):
    monkeypatch.setattr(service.db, "query_one", lambda *args: None)
    assert TestClient(service.app).get("/pacientes/100", headers=headers).status_code == 404


def test_crear(service, headers):
    result = TestClient(service.app).post("/pacientes", headers=headers, json={"usuario_id": 1, "nombre": "Ana Pérez"})
    assert result.status_code == 201


def test_crear_otro_usuario(service, headers):
    result = TestClient(service.app).post("/pacientes", headers=headers, json={"usuario_id": 2, "nombre": "Ana Pérez"})
    assert result.status_code == 403


def test_crear_invalido(service, headers):
    assert TestClient(service.app).post("/pacientes", headers=headers, json={"usuario_id": -1, "nombre": "A"}).status_code == 422


def test_actualizar(service, headers):
    assert TestClient(service.app).put("/pacientes/5", headers=headers, json={"nombre": "Ana Actualizada"}).status_code == 200


def test_actualizar_inexistente(service, headers, monkeypatch):
    monkeypatch.setattr(service.db, "query_one", lambda *args: None)
    assert TestClient(service.app).put("/pacientes/50", headers=headers, json={"nombre": "Ana"}).status_code == 404


def test_eliminar(service, headers):
    assert TestClient(service.app).delete("/pacientes/5", headers=headers).json()["mensaje"] == "Paciente eliminado"


def test_eliminar_inexistente(service, headers, monkeypatch):
    monkeypatch.setattr(service.db, "query_one", lambda *args: None)
    assert TestClient(service.app).delete("/pacientes/50", headers=headers).status_code == 404


def test_health(service):
    assert TestClient(service.app).get("/health").status_code == 200


def test_health_falla(service, monkeypatch):
    def fail(*args):
        raise RuntimeError("db down")
    monkeypatch.setattr(service.db, "query_one", fail)
    assert TestClient(service.app).get("/health").status_code == 503
