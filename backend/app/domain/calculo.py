"""Dominio: calculo del avaluo (sin dependencias de web ni base de datos). Replica las formulas del Excel original (hojas
Mercado Terr, Costos, I-Espec, Mer Inm Similares y Conclusion)."""
from decimal import Decimal, ROUND_HALF_UP

from .numero_letras import pesos_a_letras

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def num(v, default=0.0):
    """Convierte lo que venga del formulario a float sin tronar."""
    if v is None or v == "":
        return default
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", "").strip())
    except ValueError:
        return default


def xround(x, dec=0):
    """ROUND de Excel (mitad hacia arriba), no el redondeo bancario de Python."""
    q = Decimal(1).scaleb(-dec)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def promedio(lst):
    return sum(lst) / len(lst) if lst else 0.0


def fecha_texto(iso):
    try:
        y, m, d = [int(x) for x in str(iso).split("-")[:3]]
        return f"{d} de {MESES[m - 1]} {y}"
    except Exception:
        return str(iso or "")


# ---------------------------------------------------------------- calculo
def calcular(d):
    t = d.get("terreno", {})
    sup_terreno = num(t.get("superficie"))
    sup_constr = num(t.get("construccion"))
    indiviso = num(t.get("indiviso"), 100) / 100.0

    # ---- comparables de terreno
    filas_t = []
    for it in d.get("comparables_terreno", {}).get("items", []):
        sup, oferta = num(it.get("sup")), num(it.get("oferta"))
        if sup <= 0 or oferta <= 0:
            filas_t.append(None)
            continue
        pm2 = oferta / sup
        f_sup = (sup / sup_terreno) ** (1 / 6) if sup_terreno > 0 else 1.0
        fre = (num(it.get("neg"), 1) * num(it.get("ubic"), 1) * num(it.get("zona"), 1) *
               num(it.get("forma"), 1) * f_sup * num(it.get("otro"), 1))
        filas_t.append({"pm2": pm2, "f_sup": f_sup, "fre": fre, "homologado": pm2 * fre})
    hom_t = [f["homologado"] for f in filas_t if f]
    valor_homologado_t = promedio(hom_t)
    vnr_terreno = xround(valor_homologado_t, -2)

    # ---- enfoque de costos
    c = d.get("costos", {})
    coef = num(c.get("terreno_coef"), 1)
    valor_terreno = sup_terreno * vnr_terreno * coef
    terreno_sub = valor_terreno * indiviso

    constr = []
    for it in c.get("construcciones", []):
        area, vrn, dem = num(it.get("area")), num(it.get("vrn")), num(it.get("demerito"), 1)
        vnr = vrn * dem
        constr.append({"vnr": vnr, "valor": vnr * area})
    constr_sub = sum(x["valor"] for x in constr)
    area_constr = sum(num(it.get("area")) for it in c.get("construcciones", []))

    esp = []
    for it in c.get("especiales", []):
        cant, vrn, dem = num(it.get("cantidad")), num(it.get("vrn")), num(it.get("demerito"), 1)
        vnr = vrn * dem
        esp.append({"vnr": vnr, "valor": vnr * cant})
    esp_sub = sum(x["valor"] for x in esp) * indiviso

    valor_fisico = terreno_sub + constr_sub + esp_sub
    part = {k: (v / valor_fisico * 100 if valor_fisico else 0)
            for k, v in (("terreno", terreno_sub), ("construccion", constr_sub), ("instalaciones", esp_sub))}

    # ---- comparables de inmuebles
    filas_i = []
    for it in d.get("comparables_inmuebles", {}).get("items", []):
        sup, oferta = num(it.get("constr")), num(it.get("oferta"))
        if sup <= 0 or oferta <= 0:
            filas_i.append(None)
            continue
        pm2 = oferta / sup
        f_sup = (sup / sup_constr) ** (1 / 6) if sup_constr > 0 else 1.0
        fre = (num(it.get("neg"), 1) * num(it.get("ubic"), 1) * f_sup * num(it.get("calid"), 1) *
               num(it.get("edo"), 1) * num(it.get("otro"), 1))
        filas_i.append({"pm2": pm2, "f_sup": f_sup, "fre": fre, "homologado": pm2 * fre})
    hom_i = [f["homologado"] for f in filas_i if f]
    valor_homologado_i = promedio(hom_i)
    en_nr = xround(valor_homologado_i, -1)
    subtotal_mercado = en_nr * sup_constr
    adicional = num(d.get("comparables_inmuebles", {}).get("monto_adicional"))
    valor_mercado = xround(subtotal_mercado + adicional, -3)

    # ---- conclusion
    fisico_red = xround(valor_fisico, -3)
    modo = d.get("conclusion", {}).get("valor_conclusion", "mercado")
    if modo == "fisico":
        conclusion = fisico_red
    elif modo == "promedio":
        conclusion = xround((valor_mercado + fisico_red) / 2, -3)
    else:
        conclusion = valor_mercado

    return {
        "terreno": {"filas": filas_t, "valor_homologado": valor_homologado_t, "vnr": vnr_terreno},
        "costos": {"valor_terreno": valor_terreno, "terreno_sub": terreno_sub,
                   "construcciones": constr, "construccion_sub": constr_sub,
                   "area_construccion": area_constr,
                   "vnr_medio_construccion": constr_sub / area_constr if area_constr else 0,
                   "especiales": esp, "especiales_sub": esp_sub,
                   "valor_fisico": valor_fisico, "participacion": part},
        "inmuebles": {"filas": filas_i, "valor_homologado": valor_homologado_i, "en_nr": en_nr,
                      "subtotal": subtotal_mercado, "valor_mercado": valor_mercado},
        "conclusion": {"valor_mercado": valor_mercado, "valor_fisico": fisico_red,
                       "valor": conclusion, "letras": pesos_a_letras(conclusion),
                       "fecha_texto": fecha_texto(d.get("fecha"))},
    }
