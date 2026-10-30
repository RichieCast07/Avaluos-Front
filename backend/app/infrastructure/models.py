from datetime import datetime
from ..domain.tiempo import ahora_utc
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON

from .database import Base


class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    password_hash = Column(String(300), nullable=False)
    rol = Column(String(20), default="valuador")  # admin | valuador
    activo = Column(Boolean, default=True)


class Avaluo(Base):
    __tablename__ = "avaluos"
    id = Column(Integer, primary_key=True)
    folio = Column(String(30), unique=True, index=True)
    titulo = Column(String(300), default="")
    estado = Column(String(20), default="borrador")  # borrador | final
    data = Column(JSON, nullable=False)
    valor = Column(Float, default=0)
    created_by = Column(Integer, ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=ahora_utc)
    updated_at = Column(DateTime, default=ahora_utc, onupdate=ahora_utc)


class Archivo(Base):
    __tablename__ = "archivos"
    id = Column(Integer, primary_key=True)
    avaluo_id = Column(Integer, ForeignKey("avaluos.id", ondelete="CASCADE"), nullable=True, index=True)
    seccion = Column(String(20), nullable=False)  # portada | anexo | macro | micro | logo | cedula
    nombre = Column(String(300))
    ruta = Column(String(500))
    mime = Column(String(100))
    pie = Column(String(300), default="")
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=ahora_utc)


class Documento(Base):
    """Historial de Excel y PDF generados de cada avaluo."""
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True)
    avaluo_id = Column(Integer, ForeignKey("avaluos.id", ondelete="CASCADE"), nullable=False, index=True)
    formato = Column(String(10), nullable=False)  # pdf | xlsx
    version = Column(Integer, default=1)
    nombre = Column(String(300))
    ruta = Column(String(500))
    tamano = Column(Integer, default=0)
    valor = Column(Float, default=0)
    creado_por = Column(Integer, ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=ahora_utc)


class Config(Base):
    __tablename__ = "config"
    clave = Column(String(100), primary_key=True)
    valor = Column(JSON)
