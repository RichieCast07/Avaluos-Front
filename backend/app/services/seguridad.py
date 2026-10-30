import hashlib
import hmac
import secrets
from datetime import timedelta
from ..domain.tiempo import ahora_utc

import jwt

from ..config import get_settings
from ..domain.errores import NoAutenticado


def hash_password(pw: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${h}"


def verificar_password(pw: str, almacenado: str) -> bool:
    salt, _ = almacenado.split("$")
    return hmac.compare_digest(hash_password(pw, salt), almacenado)


def crear_token(user_id: int, horas: int | None = None) -> str:
    s = get_settings()
    exp = ahora_utc() + timedelta(hours=horas or s.token_horas)
    return jwt.encode({"sub": str(user_id), "exp": exp}, s.secret_key, "HS256")


def leer_token(token: str) -> int:
    try:
        return int(jwt.decode(token, get_settings().secret_key, ["HS256"])["sub"])
    except Exception:
        raise NoAutenticado("Sesión inválida o vencida")
