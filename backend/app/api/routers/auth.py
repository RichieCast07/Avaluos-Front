from fastapi import APIRouter, Depends

from ...services.usuarios import UsuarioService
from ..deps import get_session, usuario_actual, solo_admin
from ..schemas import LoginIn, UsuarioIn, usuario_out

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login")
def login(b: LoginIn, s=Depends(get_session)):
    token, u = UsuarioService(s).autenticar(b.email, b.password)
    return {"token": token, "usuario": usuario_out(u)}


@router.get("/me")
def me(u=Depends(usuario_actual)):
    return usuario_out(u)


@router.get("/usuarios")
def listar(_=Depends(solo_admin), s=Depends(get_session)):
    return [usuario_out(u) for u in UsuarioService(s).listar()]


@router.post("/usuarios")
def crear(b: UsuarioIn, _=Depends(solo_admin), s=Depends(get_session)):
    return usuario_out(UsuarioService(s).crear(b.email, b.nombre, b.password, b.rol))


@router.patch("/usuarios/{uid}")
def activar(uid: int, activo: bool, admin=Depends(solo_admin), s=Depends(get_session)):
    UsuarioService(s).cambiar_activo(uid, activo, admin)
    return {"ok": True}
