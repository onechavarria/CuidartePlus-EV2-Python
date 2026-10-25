import os

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from psycopg import errors

from app import db

app = FastAPI(title="CuidartePlus - Pacientes", version="1.0")


class Paciente(BaseModel):
    usuario_id: int = Field(gt=0)
    nombre: str = Field(min_length=2, max_length=120)
    rut: str | None = Field(default=None, max_length=20)
    telefono: str | None = Field(default=None, max_length=30)


class PacienteCambio(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    rut: str | None = Field(default=None, max_length=20)
    telefono: str | None = Field(default=None, max_length=30)


def autorizado(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        payload = jwt.decode(authorization[7:], os.environ["JWT_SECRET"], algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc


@app.get("/health")
def health():
    try:
        db.query_one("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ok"}


@app.get("/pacientes")
def listar_pacientes(usuario_id: int = Depends(autorizado)):
    return db.query_all("SELECT id, usuario_id, nombre, rut, telefono FROM pacientes WHERE usuario_id = %s ORDER BY id", (usuario_id,))


@app.get("/pacientes/{paciente_id}")
def obtener_paciente(paciente_id: int, usuario_id: int = Depends(autorizado)):
    row = db.query_one("SELECT id, usuario_id, nombre, rut, telefono FROM pacientes WHERE id = %s AND usuario_id = %s", (paciente_id, usuario_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return row


@app.post("/pacientes", status_code=201)
def crear_paciente(body: Paciente, usuario_id: int = Depends(autorizado)):
    if body.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="No puedes crear pacientes de otro usuario")
    try:
        return db.query_one("INSERT INTO pacientes (usuario_id, nombre, rut, telefono) VALUES (%s, %s, %s, %s) RETURNING id, usuario_id, nombre, rut, telefono", (body.usuario_id, body.nombre, body.rut, body.telefono))
    except errors.ForeignKeyViolation as exc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from exc
    except errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Paciente ya registrado") from exc


@app.put("/pacientes/{paciente_id}")
def actualizar_paciente(paciente_id: int, body: PacienteCambio, usuario_id: int = Depends(autorizado)):
    row = db.query_one("UPDATE pacientes SET nombre = %s, rut = %s, telefono = %s WHERE id = %s AND usuario_id = %s RETURNING id, usuario_id, nombre, rut, telefono", (body.nombre, body.rut, body.telefono, paciente_id, usuario_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return row


@app.delete("/pacientes/{paciente_id}")
def eliminar_paciente(paciente_id: int, usuario_id: int = Depends(autorizado)):
    row = db.query_one("DELETE FROM pacientes WHERE id = %s AND usuario_id = %s RETURNING id", (paciente_id, usuario_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"mensaje": "Paciente eliminado", "id": paciente_id}
