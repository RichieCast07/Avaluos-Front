from ..infrastructure.repositorios import ArchivoRepo, ConfigRepo

DEFECTO = {
    "valuador": {
        "nombre": "M.V. Lic. Daniel Arturo Guzmán Lozano",
        "maestria": "Maestría en Valuación por la Universidad Autónoma de Nuevo León",
        "cedula": "7799537",
        "experiencia": [
            "Socio fundador de la empresa Avalúos A+, creando un grupo multidisciplinario con fines valuatorios, dentro del equipo tenemos diferentes especialidades lo que nos permite valuar bienes inmuebles, maquinaria y equipo, intangibles y negocios en marcha, con los diferentes fines tales como judiciales, patrimoniales, fiscales etc.",
            "Socio activo del CMVNL Colegio Mexicano de Valuación de Nuevo León, que a su vez estamos reconocidos por la FECOVAL.",
            "Representante de la Unidad de Valuación VIASC, con cobertura nacional y reconocida por el Infonavit como una de las primeras tres más importantes de México.",
            "La experiencia de 10 años en el área inmobiliaria como asesor inmobiliario, miembro de la AMPI por 5 años y parte del consejo, me permitió entrar al tema de valuación con conocimiento de causa.",
        ],
    },
}


class EmpresaService:
    """Datos de la inmobiliaria y del valuador que salen en todos los avaluos."""

    def __init__(self, session):
        self.cfg = ConfigRepo(session)
        self.archivos = ArchivoRepo(session)

    def obtener(self) -> dict:
        base = {**DEFECTO, "valuador": dict(DEFECTO["valuador"])}
        guardado = self.cfg.obtener("empresa") or {}
        base.update({k: v for k, v in guardado.items() if k != "valuador"})
        base["valuador"].update(guardado.get("valuador", {}))
        base["archivos"] = {f.seccion: f.id for f in self.archivos.de_empresa()}
        return base

    def guardar(self, datos: dict) -> None:
        datos = {k: v for k, v in datos.items() if k != "archivos"}
        self.cfg.guardar("empresa", datos)
