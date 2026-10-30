from ..domain.errores import DatoInvalido, NoEncontrado
from ..domain.plantillas import MAX_FOTOS_ANEXO
from ..infrastructure import storage
from ..infrastructure.models import Archivo
from ..infrastructure.repositorios import ArchivoRepo, AvaluoRepo

SECCIONES = {"portada", "anexo", "macro", "micro", "cedula"}
UNICAS = {"portada", "macro", "micro", "cedula"}  # una sola por avaluo: reemplaza la anterior
MAX_BYTES = 12 * 1024 * 1024


class ArchivoService:
    def __init__(self, session):
        self.repo = ArchivoRepo(session)
        self.avaluos = AvaluoRepo(session)

    def subir(self, fileobj, nombre: str, mime: str, seccion: str, avaluo_id: int | None) -> Archivo:
        if seccion not in SECCIONES:
            raise DatoInvalido("Sección inválida")
        if avaluo_id is not None and not self.avaluos.por_id(avaluo_id):
            raise NoEncontrado("Avalúo no encontrado")
        if not (mime or "").startswith("image/"):
            raise DatoInvalido("Solo se aceptan imágenes")
        if seccion == "anexo" and len(self.repo.de_seccion(avaluo_id, seccion)) >= MAX_FOTOS_ANEXO:
            raise DatoInvalido(f"El formato admite máximo {MAX_FOTOS_ANEXO} fotos de anexo")
        fileobj.seek(0, 2)
        if fileobj.tell() > MAX_BYTES:
            raise DatoInvalido("La imagen pesa más de 12 MB")
        fileobj.seek(0)
        ruta = storage.guardar_imagen(fileobj, nombre)
        if seccion in UNICAS:
            for viejo in self.repo.de_seccion(avaluo_id, seccion):
                storage.borrar(viejo.ruta)
                self.repo.borrar(viejo)
        orden = len(self.repo.de_seccion(avaluo_id, seccion))
        return self.repo.agregar(Archivo(avaluo_id=avaluo_id, seccion=seccion, nombre=nombre, ruta=ruta, mime=mime, orden=orden))

    def obtener(self, fid: int) -> Archivo:
        f = self.repo.por_id(fid)
        if not f:
            raise NoEncontrado("Archivo no encontrado")
        return f

    def editar(self, fid: int, pie: str, orden: int | None) -> Archivo:
        f = self.obtener(fid)
        f.pie = pie
        if orden is not None:
            f.orden = orden
        self.repo.guardar()
        return f

    def borrar(self, fid: int) -> None:
        f = self.obtener(fid)
        storage.borrar(f.ruta)
        self.repo.borrar(f)
