import os
import re
import unicodedata

from ..domain.errores import DatoInvalido, ErrorServicio, NoEncontrado
from ..infrastructure import conversor_pdf, plantilla_avaluo, storage
from ..infrastructure.models import Documento
from ..infrastructure.repositorios import ArchivoRepo, AvaluoRepo, DocumentoRepo
from .empresa import EmpresaService


def _nombre_seguro(texto: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9_-]+", "_", ascii_).strip("_")[:80]


class DocumentoService:
    """Llena la plantilla de Excel de la inmobiliaria y, si se pide, la imprime a PDF.
    Cada archivo generado queda en el historial como una version nueva."""

    def __init__(self, session):
        self.avaluos = AvaluoRepo(session)
        self.archivos = ArchivoRepo(session)
        self.repo = DocumentoRepo(session)
        self.empresa = EmpresaService(session)

    def _fotos(self, aid: int) -> dict:
        fotos = {"anexo": []}
        for f in self.archivos.de_avaluo(aid):
            if f.seccion == "anexo":
                fotos["anexo"].append(f.ruta)
            else:
                fotos[f.seccion] = f.ruta
        for f in self.archivos.de_empresa():
            if f.seccion == "cedula":
                fotos["cedula"] = f.ruta
        return fotos

    def generar(self, aid: int, formato: str, usuario_id: int) -> Documento:
        if formato not in ("pdf", "xlsx"):
            raise DatoInvalido("Formato inválido")
        a = self.avaluos.por_id(aid)
        if not a:
            raise NoEncontrado("Avalúo no encontrado")
        version = self.repo.contar(aid, formato) + 1
        xlsx = storage.ruta_documento("xlsx")
        try:
            plantilla_avaluo.generar(a.data, self.empresa.obtener(), self._fotos(aid), xlsx)
            if formato == "xlsx":
                ruta = xlsx
            else:
                ruta = storage.ruta_documento("pdf")
                try:
                    conversor_pdf.xlsx_a_pdf(xlsx, ruta)
                except (conversor_pdf.ErrorConversion, OSError) as e:
                    raise ErrorServicio(f"No se pudo generar el PDF: {e}")
                finally:
                    storage.borrar(xlsx)
        except ErrorServicio:
            raise
        except Exception as e:  # plantilla danada, imagen ilegible, etc.
            storage.borrar(xlsx)
            raise ErrorServicio(f"No se pudo llenar la plantilla: {e}")
        return self.repo.agregar(Documento(avaluo_id=aid, formato=formato, version=version, ruta=ruta, valor=a.valor,
                                           nombre=f"{a.folio}_{_nombre_seguro(a.titulo)}_v{version}.{formato}",
                                           tamano=os.path.getsize(ruta), creado_por=usuario_id))

    def historial(self, aid: int):
        return self.repo.de_avaluo(aid)

    def obtener(self, did: int) -> Documento:
        d = self.repo.por_id(did)
        if not d:
            raise NoEncontrado("Documento no encontrado")
        return d
