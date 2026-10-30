import copy
from ..domain.tiempo import ahora_utc

from ..domain import calculo, plantillas
from ..domain.errores import DatoInvalido, NoEncontrado
from ..infrastructure import storage
from ..infrastructure.models import Avaluo, Archivo
from ..infrastructure.repositorios import AvaluoRepo, ArchivoRepo, DocumentoRepo
from .empresa import EmpresaService


def titulo_de(data: dict) -> str:
    i = data.get("inmueble", {})
    partes = [i.get("calle"), i.get("numero")]
    sitio = " ".join(p for p in partes if p)
    if i.get("colonia"):
        sitio = f"{sitio} - {i['colonia']}" if sitio else i["colonia"]
    return sitio or "Avalúo sin dirección"


def validar_capacidad(data: dict) -> None:
    """El formato de Excel tiene renglones fijos: se rechaza lo que no cabe en vez de perderlo en silencio."""
    limites = [
        (data["comparables_terreno"]["items"], plantillas.MAX_COMPARABLES, "comparables de terreno"),
        (data["comparables_inmuebles"]["items"], plantillas.MAX_COMPARABLES, "comparables de inmuebles"),
        (data["costos"]["construcciones"], plantillas.MAX_CONSTRUCCIONES, "construcciones"),
        (data["costos"]["especiales"], plantillas.MAX_ESPECIALES, "instalaciones especiales"),
    ]
    for lista, maximo, nombre in limites:
        if len(lista) > maximo:
            raise DatoInvalido(f"El formato de Excel admite máximo {maximo} {nombre}")


class AvaluoService:
    def __init__(self, session):
        self.repo = AvaluoRepo(session)
        self.archivos = ArchivoRepo(session)
        self.documentos = DocumentoRepo(session)
        self.empresa = EmpresaService(session)

    def _obtener(self, aid: int) -> Avaluo:
        a = self.repo.por_id(aid)
        if not a:
            raise NoEncontrado("Avalúo no encontrado")
        return a

    def listar(self, q: str = ""):
        return [(a, self.documentos.contar(a.id)) for a in self.repo.buscar(q)]

    def crear(self, usuario_id: int, ejemplo=False, duplicar_de: int | None = None) -> Avaluo:
        if duplicar_de:
            data = copy.deepcopy(self._obtener(duplicar_de).data)
        else:
            data = plantillas.ejemplo() if ejemplo else plantillas.vacio()
        a = self.repo.agregar(Avaluo(folio=self.repo.folio_siguiente(ahora_utc().year), titulo=titulo_de(data), data=data,
                                     valor=calculo.calcular(data)["conclusion"]["valor"], created_by=usuario_id))
        if duplicar_de:  # las fotos tambien se copian
            for f in self.archivos.de_avaluo(duplicar_de):
                self.archivos.agregar(Archivo(avaluo_id=a.id, seccion=f.seccion, nombre=f.nombre, ruta=storage.copiar(f.ruta),
                                              mime=f.mime, pie=f.pie, orden=f.orden))
        return a

    def detalle(self, aid: int) -> dict:
        a = self._obtener(aid)
        return {"avaluo": a, "calc": calculo.calcular(a.data), "archivos": self.archivos.de_avaluo(aid)}

    def guardar(self, aid: int, data: dict, estado: str | None = None) -> tuple[Avaluo, dict]:
        a = self._obtener(aid)
        try:
            validar_capacidad(data)
        except KeyError as e:
            raise DatoInvalido(f"Falta la sección {e} en el avalúo")
        calc = calculo.calcular(data)
        a.data, a.titulo, a.valor = data, titulo_de(data), calc["conclusion"]["valor"]
        if estado in ("borrador", "final"):
            a.estado = estado
        a.updated_at = ahora_utc()
        self.repo.guardar()
        return a, calc

    def borrar(self, aid: int) -> None:
        a = self._obtener(aid)
        for f in self.archivos.de_avaluo(aid):
            storage.borrar(f.ruta)
            self.archivos.borrar(f)
        for d in self.documentos.de_avaluo(aid):
            storage.borrar(d.ruta)
        self.documentos.borrar_de_avaluo(aid)
        self.repo.borrar(a)
