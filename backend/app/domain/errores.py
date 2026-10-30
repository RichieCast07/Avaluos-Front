"""Errores de negocio. La capa web los traduce a codigos HTTP."""


class ErrorNegocio(Exception):
    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorNegocio):
    pass


class DatoInvalido(ErrorNegocio):
    pass


class NoAutenticado(ErrorNegocio):
    pass


class Prohibido(ErrorNegocio):
    pass


class ErrorServicio(ErrorNegocio):
    """Falla de algo externo (por ejemplo LibreOffice)."""
