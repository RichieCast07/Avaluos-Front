from fastapi import APIRouter, Depends

from ...domain import calculo
from ...services.avaluos import AvaluoService
from ..deps import get_session, usuario_actual, solo_admin
from ..schemas import AvaluoCrearIn, AvaluoGuardarIn, avaluo_out, archivo_out

router = APIRouter(prefix="/api", tags=["avaluos"])


@router.get("/avaluos")
def listar(q: str = "", _=Depends(usuario_actual), s=Depends(get_session)):
    return [{**avaluo_out(a), "propietario": a.data.get("generales", {}).get("propietario", ""), "documentos": n}
            for a, n in AvaluoService(s).listar(q)]


@router.post("/avaluos")
def crear(b: AvaluoCrearIn, u=Depends(usuario_actual), s=Depends(get_session)):
    return avaluo_out(AvaluoService(s).crear(u.id, b.ejemplo, b.duplicar_de))


@router.get("/avaluos/{aid}")
def detalle(aid: int, _=Depends(usuario_actual), s=Depends(get_session)):
    d = AvaluoService(s).detalle(aid)
    return {**avaluo_out(d["avaluo"]), "data": d["avaluo"].data, "calc": d["calc"],
            "archivos": [archivo_out(f) for f in d["archivos"]]}


@router.put("/avaluos/{aid}")
def guardar(aid: int, b: AvaluoGuardarIn, _=Depends(usuario_actual), s=Depends(get_session)):
    a, calc = AvaluoService(s).guardar(aid, b.data, b.estado)
    return {"calc": calc, "updated_at": a.updated_at.isoformat(), "titulo": a.titulo}


@router.delete("/avaluos/{aid}")
def borrar(aid: int, _=Depends(solo_admin), s=Depends(get_session)):
    AvaluoService(s).borrar(aid)
    return {"ok": True}


@router.post("/calcular")
def calcular(b: AvaluoGuardarIn, _=Depends(usuario_actual)):
    return calculo.calcular(b.data)
