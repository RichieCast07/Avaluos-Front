"""Entradas (validacion) y salidas (serializacion) de la API."""
from typing import Optional
from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    email: str
    password: str


class UsuarioIn(BaseModel):
    email: str
    nombre: str = Field(min_length=1)
    password: str
    rol: str = "valuador"


class AvaluoCrearIn(BaseModel):
    ejemplo: bool = False
    duplicar_de: Optional[int] = None


class AvaluoGuardarIn(BaseModel):
    data: dict
    estado: Optional[str] = None


class DocumentoIn(BaseModel):
    formato: str


def usuario_out(u):
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol, "activo": u.activo}


def avaluo_out(a):
    return {"id": a.id, "folio": a.folio, "titulo": a.titulo, "estado": a.estado, "valor": a.valor,
            "created_at": a.created_at.isoformat(), "updated_at": a.updated_at.isoformat()}


def archivo_out(f):
    return {"id": f.id, "seccion": f.seccion, "nombre": f.nombre, "pie": f.pie, "orden": f.orden}


def documento_out(d):
    return {"id": d.id, "formato": d.formato, "version": d.version, "nombre": d.nombre,
            "tamano": d.tamano, "valor": d.valor, "created_at": d.created_at.isoformat()}
