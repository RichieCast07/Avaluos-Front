"""Configuracion de la aplicacion: todo sale de variables de entorno."""
import os
from dataclasses import dataclass, field
from functools import lru_cache


def _normalizar_db(url: str) -> str:
    # Railway entrega postgres:// o postgresql://; SQLAlchemy necesita el driver explicito
    for prefijo in ("postgres://", "postgresql://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg2://" + url[len(prefijo):]
    return url


@dataclass(frozen=True)
class Settings:
    secret_key: str
    data_dir: str
    database_url: str
    frontend_urls: tuple
    frontend_regex: str | None
    admin_email: str
    admin_password: str
    token_horas: int = 12

    @property
    def frontend_principal(self) -> str:
        return self.frontend_urls[0]


@lru_cache
def get_settings() -> Settings:
    data_dir = os.path.abspath(os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data")))
    os.makedirs(data_dir, exist_ok=True)  # SQLite y los archivos viven aqui (en Railway: el Volume)
    urls = tuple(u.strip().rstrip("/") for u in os.environ.get("FRONTEND_URL", "http://localhost:5173").split(",") if u.strip())
    return Settings(
        secret_key=os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion-por-una-larga-y-aleatoria"),
        data_dir=data_dir,
        database_url=_normalizar_db(os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(data_dir, 'avaluos.db')}")),
        frontend_urls=urls,
        frontend_regex=os.environ.get("FRONTEND_REGEX") or None,  # p. ej. https://.*\.vercel\.app para previews
        admin_email=os.environ.get("ADMIN_EMAIL", "admin@avaluos.local").strip().lower(),
        admin_password=os.environ.get("ADMIN_PASSWORD", "cambiar123"),
    )
