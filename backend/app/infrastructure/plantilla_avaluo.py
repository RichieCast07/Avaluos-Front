"""Llena el Excel de la inmobiliaria (assets/plantilla_avaluo.xlsx) con los datos de un avaluo.

El archivo conserva su formato, formulas, imagenes y graficas: aqui solo se escriben las celdas de captura.
Los calculos los hace el propio Excel (por eso al abrirlo se recalcula todo).
"""
import io
import os
import re

from PIL import Image

from ..domain.calculo import fecha_texto, num, pesos_a_letras
from ..domain.plantillas import MAX_COMPARABLES, MAX_CONSTRUCCIONES, MAX_ESPECIALES, MAX_EXPERIENCIA, MAX_FOTOS_ANEXO
from .xlsx_editor import Paquete

PLANTILLA = os.path.join(os.path.dirname(__file__), "..", "assets", "plantilla_avaluo.xlsx")

# Capacidad fija de la plantilla (renglones/espacios que tiene el formato)

NIVEL_TERRENO = {"MUY ALTA": "C7", "MEDIA": "G7", "BAJA": "K7", "ALTA": "C8", "MEDIA BAJA": "G8", "NULA": "K8"}
NIVEL_INMUEBLES = {"MUY ALTA": "D5", "MEDIA": "H5", "BAJA": "L5", "ALTA": "D6", "MEDIA BAJA": "H6", "NULA": "L6"}
BLOQUES_TERRENO = [(11, 12), (14, 15), (17, 18), (20, 21)]      # (renglon direccion, renglon superficie)
BLOQUES_INMUEBLES = [(8, 9), (11, 12), (14, 15), (17, 18)]
FILAS_OFERTA_TERRENO = [29, 30, 31, 32]
FILAS_OFERTA_INMUEBLES = [23, 24, 25, 26]
FILAS_ESPECIALES = [10, 11, 12, 13, 14]
FILAS_EXPERIENCIA = [11, 18, 21, 25, 29]

# elemento de la construccion -> celda de 'Resumen' de donde lo toma el formato
ELEMENTOS = {
    "cimientos": "E86", "estructura": "E88", "muros": "E90", "entrepisos": "E92", "techos": "E94", "azoteas": "E96",
    "bardas": "E98", "aplanados_int": "E103", "aplanados_ext": "E105", "techos_acab": "E107", "lambrines": "E109",
    "pisos": "E111", "escaleras": "E113", "pintura": "E115", "recubrimientos": "E117", "carpinteria": "E119",
    "hidraulicas": "E121", "electricas": "E125", "puertas": "E127", "herreria": "E129", "vidrieria": "E131",
    "cerrajeria": "E133", "fachada": "E135", "especiales": "E137",
}


def _t(v):
    """Texto para el formato: vacio -> un espacio (si no, las celdas ligadas muestran 0)."""
    s = "" if v is None else str(v).strip()
    return s or " "


def _n(v):
    return num(v) if str(v if v is not None else "").strip() != "" else None


def _cedula(v):
    s = str(v or "").strip()
    return int(s) if s.isdigit() else s


# ------------------------------------------------------------------ imagenes
def _preparar_imagen(ruta, aspecto, formato):
    """Recorta al centro con la proporcion del espacio de la plantilla y reduce el peso."""
    im = Image.open(ruta)
    im.load()
    if im.mode not in ("RGB", "L"):
        fondo = Image.new("RGB", im.size, "white")
        fondo.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
        im = fondo
    w, h = im.size
    if w / h > aspecto:
        nw = int(h * aspecto)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / aspecto)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.thumbnail((1600, 1600))
    out = io.BytesIO()
    if formato == "png":
        im.convert("RGB").save(out, "PNG", optimize=True)
    else:
        im.convert("RGB").save(out, "JPEG", quality=88)
    return out.getvalue()


def _poner_imagenes(paq, hoja, indices_y_rutas, todos_los_indices, quitar_vacios=True):
    """indices_y_rutas: {indice_de_ancla: ruta}. Los espacios de todos_los_indices sin ruta se quitan."""
    dibujo = paq.hoja(hoja).ruta_dibujo()
    sin_usar = []
    for i in todos_los_indices:
        ruta = indices_y_rutas.get(i)
        if not ruta:
            if quitar_vacios:
                sin_usar.append(i)
            continue
        w, h = paq.dimensiones_imagen(dibujo, i)
        formato = "png" if paq._media_de(dibujo, i).lower().endswith(".png") else "jpeg"
        paq.reemplazar_imagen(dibujo, i, _preparar_imagen(ruta, w / h, formato))
    if sin_usar:
        paq.quitar_imagenes(dibujo, sin_usar)


# ------------------------------------------------------------------ llenado
def generar(data, empresa, fotos, destino):
    """data: dict del avaluo. empresa: configuracion (valuador). fotos: {'portada','macro','micro','cedula': ruta|None, 'anexo': [rutas]}"""
    paq = Paquete(PLANTILLA)
    paq.congelar_vinculos_externos()
    paq.hoja("Portada ").vaciar("E46")      # apuntaba a un libro externo y quedaba como fecha 12/30/1899
    paq.quitar_textos_fijos_de_graficas()

    d_inm, d_gen, d_zona, d_ter, d_des = data["inmueble"], data["generales"], data["zona"], data["terreno"], data["descripcion"]
    val = empresa.get("valuador", {})

    # ---------------- Resumen (hoja de captura del formato)
    r = paq.hoja("Resumen")
    r.texto("D3", fecha_texto(data.get("fecha")))
    r.texto("D7", _t(d_inm.get("calle")))
    r.poner("D8", _n(d_inm.get("numero")) if str(d_inm.get("numero", "")).strip().isdigit() else _t(d_inm.get("numero")))
    r.texto("D9", _t(d_inm.get("colonia")))
    r.texto("D10", _t(d_inm.get("municipio")))
    r.poner("D11", _n(d_inm.get("cp")) if str(d_inm.get("cp", "")).strip().isdigit() else _t(d_inm.get("cp")))
    r.texto("D12", _t(d_inm.get("estado")))
    r.texto("E16", _t(d_gen.get("regimen")))
    r.texto("E17", _t(d_gen.get("solicitante")))
    r.texto("E18", _t(d_gen.get("proposito")))
    r.texto("E19", _t(d_gen.get("uso")))
    r.texto("E20", _t(d_inm.get("cuenta_predial")))
    r.texto("E21", _t(d_inm.get("cuenta_agua") or "-"))
    r.texto("E22", _t(d_zona.get("construccion_dominante")))
    r.texto("E24", _t(d_zona.get("saturacion")))
    r.texto("E25", _t(d_zona.get("densidad")))
    r.texto("E27", _t(d_zona.get("contaminacion")))
    r.texto("E28", _t(d_zona.get("uso_suelo")))
    r.texto("E30", _t(d_zona.get("vias_acceso")))
    r.texto("E32", _t(d_zona.get("servicios")))
    r.texto("E34", _t(d_zona.get("equipamiento")))
    r.texto("E36", _t(d_ter.get("tramos")))
    r.texto("E38", _t(d_ter.get("escritura")))
    for fila, k in zip((40, 41, 42, 43), ("norte", "sur", "oriente", "poniente")):
        r.poner(f"E{fila}", _n(d_ter[k].get("medida")))
        r.texto(f"F{fila}", f"m. colinda con {d_ter[k].get('colinda', '')}".strip())
    r.poner("E45", _n(d_ter.get("superficie")))
    r.poner("E47", _n(d_ter.get("construccion")))
    r.texto("E49", f"{d_ter.get('indiviso') or 100}%")
    r.texto("E51", _t(d_ter.get("topografia")))
    r.texto("E52", _t(d_ter.get("frentes")))
    r.texto("E53", _t(d_ter.get("panoramicas")))
    r.texto("E54", _t(d_ter.get("densidad_hab")))
    r.texto("E55", _t(d_ter.get("intensidad")))
    r.texto("E56", _t(d_ter.get("servidumbre")))
    r.texto("F59", _t(d_ter.get("longitud")))
    r.texto("F60", _t(d_ter.get("latitud")))
    alt = str(d_ter.get("altitud", "")).strip()
    r.texto("F61", f"{alt} M" if alt.replace(".", "").isdigit() else _t(alt))
    r.texto("E65", _t(d_des.get("uso_actual")))
    r.poner("E68", _n(d_des.get("tipo1_m2")))
    r.texto("E75", _t(d_des.get("calidad")))
    r.poner("E76", _n(d_des.get("niveles")))
    r.poner("E77", _n(d_des.get("edad")))
    r.poner("E78", _n(d_des.get("vida_remanente")))
    r.poner("E79", _n(d_des.get("vida_total")))
    r.texto("E80", _t(d_des.get("conservacion")))
    r.texto("E81", _t(d_des.get("calidad")))
    r.poner("E82", _n(d_des.get("unidades_rentables")))
    for k, celda in ELEMENTOS.items():
        r.texto(celda, _t(d_des["elementos"].get(k)))
    r.texto("E123", " ")
    r.texto("E140", _t(data["conclusion"].get("comentarios")))

    # ---------------- Datos (el formato lleva aqui varios datos escritos a mano)
    h = paq.hoja("Datos")
    h.texto("C7", _t(val.get("nombre")))
    h.poner("C9", _cedula(val.get("cedula")))
    h.texto("C10", _t(d_gen.get("bien")))
    h.texto("C11", _t(d_gen.get("regimen")))
    h.texto("C12", _t(d_gen.get("propietario")))
    h.texto("C13", _t(d_gen.get("proposito")))
    h.texto("C14", _t(d_gen.get("uso")))
    h.texto("D32", _t(d_zona.get("construccion_dominante")))
    h.texto("D33", _t(d_zona.get("densidad")))
    h.texto("D34", _t(d_zona.get("contaminacion")))
    h.texto("D35", _t(d_zona.get("uso_suelo")))
    h.poner("D36", _n(d_zona.get("saturacion")))
    h.texto("D41", _t(d_zona.get("servicios")))
    h.texto("D46", _t(d_zona.get("equipamiento")))

    h = paq.hoja("Car. Terreno")
    h.texto("C23", _t(d_ter.get("topografia")))
    h.poner("C24", _n(d_ter.get("frentes")) if str(d_ter.get("frentes", "")).strip().isdigit() else _t(d_ter.get("frentes")))

    h = paq.hoja("Des. Inmueble")
    h.poner("C17", _n(d_des.get("edad")))
    h.poner("C18", _n(d_des.get("vida_remanente")))
    h.poner("C19", _n(d_des.get("vida_total")))
    h.formula("C31", "+Resumen!E98")        # las bardas no estaban ligadas en el formato original
    h.copiar_estilo("C31", "C30")

    # ---------------- Mercado del terreno
    h = paq.hoja("Mercado Terr ")
    h.quitar_hipervinculos()
    marcas = {k: "(     )" for k in NIVEL_TERRENO}
    marcas[str(data["comparables_terreno"].get("nivel_oferta", "MEDIA")).upper()] = "(  x  )"
    for k, celda in NIVEL_TERRENO.items():
        h.texto(celda, marcas[k])
    comps = [c for c in data["comparables_terreno"]["items"] if num(c.get("sup")) > 0 and num(c.get("oferta")) > 0][:MAX_COMPARABLES]
    for i, (f1, f2) in enumerate(BLOQUES_TERRENO):
        fo = FILAS_OFERTA_TERRENO[i]
        if i < len(comps):
            c = comps[i]
            h.numero(f"A{f1}", i + 1)
            h.texto(f"B{f1}", _t(c.get("direccion")))
            h.texto(f"H{f1}", _t(c.get("telefono")))
            h.texto(f"J{f1}", _t(c.get("liga")))
            if h.celda(f"H{f1}").get("s") is None:
                h.copiar_estilo(f"H{f1}", "H11")
            h.numero(f"B{f2}", num(c.get("sup")))
            h.texto(f"C{f2}", "m2 terreno ")
            h.numero(f"B{fo}", num(c.get("oferta")))
            for col, k in zip("EFGH", ("neg", "ubic", "zona", "forma")):
                h.numero(f"{col}{fo}", num(c.get(k), 1))
            h.numero(f"J{fo}", num(c.get("otro"), 1))
        else:
            for ref in (f"A{f1}", f"B{f1}", f"H{f1}", f"J{f1}", f"B{f2}", f"C{f2}"):
                h.vaciar(ref)
            for col in "ABCDEFGHIJKL":
                h.vaciar(f"{col}{fo}")
    for fila, k in zip((40, 41, 42, 43, 44, 45), ("neg", "ubic", "zona", "forma", "sup", "otro")):
        h.texto(f"C{fila}", _t(data["comparables_terreno"]["notas"].get(k)))
    for ref in ("L33", "O16", "O17", "O18", "O28", "O29", "O30", "O31"):   # apuntes del avaluo de muestra
        h.vaciar(ref)

    # ---------------- Mercado de inmuebles
    h = paq.hoja("Mer Inm Similares")
    h.quitar_hipervinculos()
    marcas = {k: "(     )" for k in NIVEL_INMUEBLES}
    marcas[str(data["comparables_inmuebles"].get("nivel_oferta", "MEDIA")).upper()] = "( X  )"
    for k, celda in NIVEL_INMUEBLES.items():
        h.texto(celda, marcas[k])
    comps = [c for c in data["comparables_inmuebles"]["items"] if num(c.get("constr")) > 0 and num(c.get("oferta")) > 0][:MAX_COMPARABLES]
    for i, (f1, f2) in enumerate(BLOQUES_INMUEBLES):
        fo = FILAS_OFERTA_INMUEBLES[i]
        if i < len(comps):
            c = comps[i]
            h.numero(f"A{f1}", i + 1)
            h.texto(f"C{f1}", _t(c.get("direccion")))
            h.texto(f"I{f1}", _t(c.get("telefono")))
            h.texto(f"K{f1}", _t(c.get("liga")))
            h.numero(f"C{f2}", num(c.get("constr")))
            h.texto(f"A{f2}", "Características")
            h.texto(f"D{f2}", f"m² construccion y {num(c.get('terreno')):.2f} m² terreno")
            h.numero(f"B{fo}", num(c.get("oferta")))
            for col, k in zip("FGIJK", ("neg", "ubic", "calid", "edo", "otro")):
                h.numero(f"{col}{fo}", num(c.get(k), 1))
        else:
            for ref in (f"A{f1}", f"C{f1}", f"I{f1}", f"K{f1}", f"A{f2}", f"C{f2}", f"D{f2}"):
                h.vaciar(ref)
            for col in "ABCDEFGHIJKLM":
                h.vaciar(f"{col}{fo}")
    h.poner("M32", _n(data["comparables_inmuebles"].get("monto_adicional")) or None)
    for fila, k in zip((36, 37, 38, 39, 40, 41), ("neg", "ubic", "sup", "calid", "edo", "otro")):
        h.texto(f"C{fila}", _t(data["comparables_inmuebles"]["notas"].get(k)))
    for ref in ("Q23", "Q26", "Q27"):
        h.vaciar(ref)

    # ---------------- Costos
    h = paq.hoja("Costos")
    h.poner("E15", num(data["costos"].get("terreno_coef"), 1))
    h.texto("F15", _t(data["costos"].get("terreno_motivo")))
    construcciones = [c for c in data["costos"]["construcciones"] if num(c.get("area")) > 0][:MAX_CONSTRUCCIONES]
    for i, fila in enumerate((36, 37, 38)):
        if i < len(construcciones):
            c = construcciones[i]
            if fila > 36:
                for col in "ABCDEFGHI":
                    if h.celda(f"{col}{fila}").get("s") is None:
                        h.copiar_estilo(f"{col}{fila}", f"{col}36")
                h.numero(f"A{fila}", i + 1)
                h.formula(f"H{fila}", f"+F{fila}*(G{fila})")
                h.formula(f"I{fila}", f"H{fila}*E{fila}")
            h.texto(f"C{fila}", _t(c.get("uso")))
            h.numero(f"E{fila}", num(c.get("area")))
            h.numero(f"F{fila}", num(c.get("vrn")))
            h.numero(f"G{fila}", num(c.get("demerito"), 1))
        elif fila > 36:
            for col in "CEFGHI":
                h.vaciar(f"{col}{fila}")
            h.vaciar(f"A{fila}")
    h = paq.hoja("I-Espec")
    esp = [e for e in data["costos"]["especiales"] if num(e.get("cantidad")) > 0][:MAX_ESPECIALES]
    for i, fila in enumerate(FILAS_ESPECIALES):
        if i < len(esp):
            e = esp[i]
            h.texto(f"A{fila}", _t(e.get("concepto")))
            h.texto(f"C{fila}", _t(e.get("unidad")))
            h.numero(f"D{fila}", num(e.get("cantidad")))
            h.numero(f"F{fila}", num(e.get("vrn")))
            h.numero(f"G{fila}", num(e.get("demerito"), 1))
            h.numero(f"H{fila}", 1)
            h.numero(f"I{fila}", 1)
        else:
            for col in "ACDFGHI":
                h.vaciar(f"{col}{fila}")
    h.formula("L16", "SUM(L10:L14)")        # el formato original solo sumaba 3 de los 5 renglones

    # ---------------- Conclusion
    h = paq.hoja("Conclusión")
    modo = data["conclusion"].get("valor_conclusion", "mercado")
    h.formula("D29", {"fisico": "C9", "promedio": "ROUND((C8+C9)/2,-3)"}.get(modo, "I8"))
    from ..domain.calculo import calcular
    h.texto("E29", pesos_a_letras(calcular(data)["conclusion"]["valor"]))
    decl = data["conclusion"].get("declaraciones", ["", ""])
    h.texto("C17", _t(decl[0] if decl else ""))
    h.texto("C19", _t(decl[1] if len(decl) > 1 else ""))
    meses = str(data["conclusion"].get("vigencia_meses", "6")).strip() or "6"
    h.texto("A34", f"VIGENCIA DEL ESTIMADO DE VALOR: {meses} MESES A PARTIR DE LA FECHA DEL PRESENTE AVALÚO.")

    # ---------------- Anexo 2: valuador
    h = paq.hoja("A2.Datos Valuador")
    h.texto("C7", _t(val.get("nombre")))
    h.texto("C8", _t(val.get("maestria")))
    h.poner("C9", _cedula(val.get("cedula")))
    parrafos = [p for p in val.get("experiencia", []) if p.strip()][:MAX_EXPERIENCIA]
    for i, fila in enumerate(FILAS_EXPERIENCIA):
        h.texto(f"C{fila}", parrafos[i] if i < len(parrafos) else None)

    # ---------------- Fotos
    _poner_imagenes(paq, "Portada ", {1: fotos.get("portada")}, [1])
    _poner_imagenes(paq, "Car. Terreno", {0: fotos.get("macro"), 1: fotos.get("micro")}, [0, 1])
    orden_visual = [0, 2, 1, 3, 4, 5]   # izquierda-derecha, arriba-abajo
    anexo = (fotos.get("anexo") or [])[:MAX_FOTOS_ANEXO]
    _poner_imagenes(paq, "A1.Fotos", {orden_visual[i]: ruta for i, ruta in enumerate(anexo)}, list(range(6)))
    _poner_imagenes(paq, "A2.Datos Valuador", {0: fotos.get("cedula")}, [0], quitar_vacios=False)  # sin archivo nuevo se queda la del formato

    paq.forzar_recalculo()
    paq.podar_medios_sin_uso()
    paq.guardar(destino)
