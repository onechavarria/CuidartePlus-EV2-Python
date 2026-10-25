import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from psycopg import errors

from app import db

app = FastAPI(title="CuidartePlus - Usuarios", version="1.0")
password_hash = PasswordHash.recommended()


class Registro(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=80)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    nombre_usuario: str
    password: str


@app.get("/health")
def health():
    try:
        db.query_one("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ok"}


@app.post("/autenticacion/registro", status_code=201)
def registro(body: Registro):
    try:
        row = db.query_one(
            "INSERT INTO usuarios (nombre_usuario, correo, contrasena) VALUES (%s, %s, %s) RETURNING id, nombre_usuario, correo",
            (body.nombre_usuario, body.correo, password_hash.hash(body.password)),
        )
    except errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Usuario o correo ya existe") from exc
    return row


@app.post("/autenticacion/login")
def login(body: Login):
    user = db.query_one(
        "SELECT id, nombre_usuario, contrasena FROM usuarios WHERE nombre_usuario = %s",
        (body.nombre_usuario,),
    )
    if not user or not password_hash.verify(body.password, user["contrasena"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = jwt.encode(
        {"sub": str(user["id"]), "exp": datetime.now(timezone.utc) + timedelta(hours=2)},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    return {"token": token, "token_type": "bearer"}


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    user = db.query_one(
        "SELECT id, nombre_usuario, correo FROM usuarios WHERE id = %s", (usuario_id,)
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
