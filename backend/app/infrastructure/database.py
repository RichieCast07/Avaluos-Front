from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config import get_settings

_s = get_settings()
engine = create_engine(_s.database_url, pool_pre_ping=True,
                       connect_args={"check_same_thread": False} if _s.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def init_db() -> None:
    from . import models  # noqa: F401  (registra las tablas)
    Base.metadata.create_all(engine)
