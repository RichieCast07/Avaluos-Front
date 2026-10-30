"""Dominio: cantidad con letra en pesos mexicanos."""
from decimal import Decimal, ROUND_HALF_UP


def _redondear(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


_UNI = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ",
        "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO",
        "DIECINUEVE", "VEINTE", "VEINTIUN", "VEINTIDOS", "VEINTITRES", "VEINTICUATRO",
        "VEINTICINCO", "VEINTISEIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
_DEC = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
_CEN = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
        "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]


def _menos_mil(n):
    if n == 0:
        return ""
    if n == 100:
        return "CIEN"
    c, r = divmod(n, 100)
    partes = []
    if c:
        partes.append(_CEN[c])
    if r:
        if r < 30:
            partes.append(_UNI[r])
        else:
            d, u = divmod(r, 10)
            partes.append(_DEC[d] + (" Y " + _UNI[u] if u else ""))
    return " ".join(partes)


def entero_a_letras(n):
    if n == 0:
        return "CERO"
    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1000)
    partes = []
    if millones:
        partes.append("UN MILLON" if millones == 1 else _menos_mil(millones) + " MILLONES")
    if miles:
        partes.append("MIL" if miles == 1 else _menos_mil(miles) + " MIL")
    if unidades:
        partes.append(_menos_mil(unidades))
    return " ".join(partes)


def pesos_a_letras(x):
    x = _redondear(x)
    ent = int(x)
    cent = int(round((x - ent) * 100))
    sufijo = "DE PESOS" if ent != 0 and ent % 1_000_000 == 0 else "PESOS"
    return f"{entero_a_letras(ent)} {sufijo} {cent:02d}/100 M.N."


