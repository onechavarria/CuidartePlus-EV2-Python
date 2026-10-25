import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def service(load_service, monkeypatch):
    main = load_service("usuarios")
    monkeypatch.setattr(main.db, "query_one", lambda *args: {"id": 1, "nombre_usuario": "ana", "correo": "ana@test.cl"})
    return main


def test_registro_correcto(service):
    result = TestClient(service.app).post("/autenticacion/registro", json={"nombre_usuario": "ana", "correo": "ana@test.cl", "password": "secreto123"})
    assert result.status_code == 201
    assert result.json()["nombre_usuario"] == "ana"
    assert "contrasena" not in result.json()


@pytest.mark.parametrize("body", [
    {"nombre_usuario": "ab", "correo": "ana@test.cl", "password": "secreto123"},
    {"nombre_usuario": "ana", "correo": "no-es-email", "password": "secreto123"},
    {"nombre_usuario": "ana", "correo": "ana@test.cl", "password": "123"},
])
def test_registro_datos_invalidos(service, body):
    assert TestClient(service.app).post("/autenticacion/registro", json=body).status_code == 422


def test_login_invalido(service, monkeypatch):
    monkeypatch.setattr(service.db, "query_one", lambda *args: None)
    assert TestClient(service.app).post("/autenticacion/login", json={"nombre_usuario": "nadie", "password": "incorrecta"}).status_code == 401


def test_login_correcto(service, monkeypatch):
    password = service.password_hash.hash("secreto123")
    monkeypatch.setattr(service.db, "query_one", lambda *args: {"id": 1, "nombre_usuario": "ana", "contrasena": password})
    result = TestClient(service.app).post("/autenticacion/login", json={"nombre_usuario": "ana", "password": "secreto123"})
    assert result.status_code == 200
    assert result.json()["token"]


def test_usuario_no_encontrado(service, monkeypatch):
    monkeypatch.setattr(service.db, "query_one", lambda *args: None)
    assert TestClient(service.app).get("/usuarios/99").status_code == 404


def test_usuario_encontrado(service):
    assert TestClient(service.app).get("/usuarios/1").status_code == 200


def test_health(service):
    assert TestClient(service.app).get("/health").status_code == 200


def test_health_db_falla(service, monkeypatch):
    def fail(*args):
        raise RuntimeError("sin conexion")
    monkeypatch.setattr(service.db, "query_one", fail)
    assert TestClient(service.app).get("/health").status_code == 503
