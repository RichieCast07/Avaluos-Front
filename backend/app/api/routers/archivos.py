from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from ...domain.errores import DatoInvalido, NoEncontrado
from ...services.archivos import ArchivoService
from ..deps import get_session, usuario_actual, solo_admin
from ..schemas import archivo_out

router = APIRouter(prefix="/api", tags=["archivos"])


@router.post("/avaluos/{aid}/archivos")
def subir(aid: int, seccion: str = Form(...), archivo: UploadFile = File(...), _=Depends(usuario_actual), s=Depends(get_session)):
    if seccion in ("logo", "cedula"):
        raise DatoInvalido("Usa la configuración de la empresa")
    return archivo_out(ArchivoService(s).subir(archivo.file, archivo.filename, archivo.content_type, seccion, aid))


@router.post("/configuracion/archivo")
def subir_empresa(seccion: str = Form(...), archivo: UploadFile = File(...), _=Depends(solo_admin), s=Depends(get_session)):
    if seccion not in ("logo", "cedula"):
        raise DatoInvalido("Sección inválida")
    return archivo_out(ArchivoService(s).subir(archivo.file, archivo.filename, archivo.content_type, seccion, None))


@router.patch("/archivos/{fid}")
def editar(fid: int, pie: str = "", orden: Optional[int] = None, _=Depends(usuario_actual), s=Depends(get_session)):
    return archivo_out(ArchivoService(s).editar(fid, pie, orden))


@router.delete("/archivos/{fid}")
def borrar(fid: int, _=Depends(usuario_actual), s=Depends(get_session)):
    ArchivoService(s).borrar(fid)
    return {"ok": True}


@router.get("/archivos/{fid}/contenido")
def contenido(fid: int, _=Depends(usuario_actual), s=Depends(get_session)):
    import os
    f = ArchivoService(s).obtener(fid)
    if not os.path.exists(f.ruta):
        raise NoEncontrado("Archivo no encontrado")
    return FileResponse(f.ruta, media_type=f.mime, headers={"Cache-Control": "private, max-age=3600"})
