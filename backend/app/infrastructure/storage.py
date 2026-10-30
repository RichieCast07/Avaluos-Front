"""Almacenamiento de archivos en disco (en Railway: un Volume montado en DATA_DIR)."""
import os
import shutil
import uuid

from ..config import get_settings


def _carpeta(sub: str) -> str:
    ruta = os.path.join(get_settings().data_dir, sub)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def guardar_imagen(fileobj, nombre_original: str) -> str:
    ext = os.path.splitext(nombre_original or "")[1].lower() or ".jpg"
    ruta = os.path.join(_carpeta("archivos"), f"{uuid.uuid4().hex}{ext}")
    with open(ruta, "wb") as out:
        shutil.copyfileobj(fileobj, out)
    return ruta


def copiar(ruta: str) -> str:
    nueva = os.path.join(_carpeta("archivos"), f"{uuid.uuid4().hex}{os.path.splitext(ruta)[1]}")
    shutil.copy(ruta, nueva)
    return nueva


def ruta_documento(extension: str) -> str:
    return os.path.join(_carpeta("documentos"), f"{uuid.uuid4().hex}.{extension}")


def borrar(ruta: str | None) -> None:
    if not ruta:
        return
    try:
        os.remove(ruta)
    except OSError:
        pass
