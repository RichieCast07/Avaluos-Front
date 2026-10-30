import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.routers import auth, avaluos, archivos, documentos
from .config import get_settings
from .domain.errores import DatoInvalido, ErrorNegocio, ErrorServicio, NoAutenticado, NoEncontrado, Prohibido
from .infrastructure.database import SessionLocal, init_db
from .services.usuarios import UsuarioService

ESTADOS = {NoEncontrado: 404, DatoInvalido: 400, NoAutenticado: 401, Prohibido: 403, ErrorServicio: 500}


@asynccontextmanager
async def ciclo(_: FastAPI):
    init_db()
    s = SessionLocal()
    try:
        UsuarioService(s).sembrar_admin()
    finally:
        s.close()
    yield


def crear_app() -> FastAPI:
    cfg = get_settings()
    app = FastAPI(title="Avalúos", lifespan=ciclo)
    app.add_middleware(CORSMiddleware, allow_origins=list(cfg.frontend_urls), allow_origin_regex=cfg.frontend_regex,
                       allow_methods=["*"], allow_headers=["*"], allow_credentials=False)

    @app.exception_handler(ErrorNegocio)
    async def _error_negocio(_: Request, e: ErrorNegocio):
        return JSONResponse({"detail": e.mensaje}, status_code=ESTADOS.get(type(e), 400))

    @app.get("/salud")
    def salud():
        return {"ok": True}

    for r in (auth.router, avaluos.router, archivos.router, documentos.router):
        app.include_router(r)

    # Frontend compilado (solo si existe: en produccion Vercel lo sirve aparte)
    dist = os.environ.get("FRONTEND_DIST", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")))
    if os.path.isdir(os.path.join(dist, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(dist, "assets")), name="assets")

        @app.get("/{ruta:path}", include_in_schema=False)
        def spa(ruta: str):
            if ruta.startswith("api/"):
                return JSONResponse({"detail": "No encontrado"}, status_code=404)
            archivo = os.path.realpath(os.path.join(dist, ruta))
            if ruta and archivo.startswith(os.path.realpath(dist) + os.sep) and os.path.isfile(archivo):
                return FileResponse(archivo)
            return FileResponse(os.path.join(dist, "index.html"))
    return app


app = crear_app()
