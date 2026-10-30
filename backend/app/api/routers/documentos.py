import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from ...domain.errores import NoEncontrado
from ...services.documentos import DocumentoService
from ...services.empresa import EmpresaService
from ..deps import get_session, usuario_actual, solo_admin
from ..schemas import DocumentoIn, documento_out

router = APIRouter(prefix="/api", tags=["documentos"])
MIME = {"pdf": "application/pdf", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}


@router.post("/avaluos/{aid}/documentos")
def generar(aid: int, b: DocumentoIn, u=Depends(usuario_actual), s=Depends(get_session)):
    return documento_out(DocumentoService(s).generar(aid, b.formato, u.id))


@router.get("/avaluos/{aid}/documentos")
def historial(aid: int, _=Depends(usuario_actual), s=Depends(get_session)):
    return [documento_out(d) for d in DocumentoService(s).historial(aid)]


@router.get("/documentos/{did}/descargar")
def descargar(did: int, _=Depends(usuario_actual), s=Depends(get_session)):
    d = DocumentoService(s).obtener(did)
    if not os.path.exists(d.ruta):
        raise NoEncontrado("El archivo ya no está en el servidor")
    return FileResponse(d.ruta, media_type=MIME[d.formato], filename=d.nombre)


@router.get("/configuracion")
def ver_configuracion(_=Depends(usuario_actual), s=Depends(get_session)):
    return EmpresaService(s).obtener()


@router.put("/configuracion")
def guardar_configuracion(b: dict, _=Depends(solo_admin), s=Depends(get_session)):
    EmpresaService(s).guardar(b)
    return {"ok": True}
