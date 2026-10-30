from typing import Iterator, Optional
from fastapi import Depends, Header, Query

from ..domain.errores import Prohibido
from ..infrastructure.database import SessionLocal
from ..services.usuarios import UsuarioService


def get_session() -> Iterator:
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def usuario_actual(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None), s=Depends(get_session)):
    """El token va en el encabezado Authorization; ?token= se acepta solo para las etiquetas <img> de las fotos."""
    t = token or (authorization or "").removeprefix("Bearer ").strip()
    return UsuarioService(s).desde_token(t)


def solo_admin(u=Depends(usuario_actual)):
    if u.rol != "admin":
        raise Prohibido("Solo administradores")
    return u
