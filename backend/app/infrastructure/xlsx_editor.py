"""Edicion directa de un .xlsx (OOXML) sin pasar por openpyxl.

openpyxl descarta imagenes, formas, graficas y validaciones de datos al guardar, asi que para
usar el Excel de la inmobiliaria como plantilla se modifica el XML de las hojas tal cual.
"""
import io
import posixpath
import re
import zipfile

from lxml import etree

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _col_a_num(letras: str) -> int:
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def _partir(ref: str):
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    return _col_a_num(m.group(1)), int(m.group(2))


def _q(ns, tag):
    return f"{{{ns}}}{tag}"


class Hoja:
    def __init__(self, paquete, parte):
        self.paquete = paquete
        self.parte = parte
        self.raiz = paquete.xml(parte)
        self.datos = self.raiz.find(_q(M, "sheetData"))

    # ---- localizar / crear
    def _fila(self, n, crear=True):
        previa = None
        for fila in self.datos.findall(_q(M, "row")):
            r = int(fila.get("r"))
            if r == n:
                return fila
            if r > n:
                break
            previa = fila
        if not crear:
            return None
        nueva = etree.Element(_q(M, "row"), r=str(n))
        if previa is None:
            self.datos.insert(0, nueva)
        else:
            previa.addnext(nueva)
        return nueva

    def celda(self, ref, crear=True):
        col, n = _partir(ref)
        fila = self._fila(n, crear)
        if fila is None:
            return None
        previa = None
        for c in fila.findall(_q(M, "c")):
            cc, _ = _partir(c.get("r"))
            if cc == col:
                return c
            if cc > col:
                break
            previa = c
        if not crear:
            return None
        nueva = etree.Element(_q(M, "c"), r=ref)
        if previa is None:
            fila.insert(0, nueva)
        else:
            previa.addnext(nueva)
        return nueva

    @staticmethod
    def _limpiar(c):
        for hijo in list(c):
            c.remove(hijo)
        if "t" in c.attrib:
            del c.attrib["t"]

    def copiar_estilo(self, destino, origen):
        o = self.celda(origen, crear=False)
        if o is not None and o.get("s"):
            self.celda(destino).set("s", o.get("s"))

    # ---- escribir
    def texto(self, ref, valor):
        c = self.celda(ref)
        self._limpiar(c)
        if valor is None or valor == "":
            return
        c.set("t", "inlineStr")
        is_ = etree.SubElement(c, _q(M, "is"))
        t = etree.SubElement(is_, _q(M, "t"))
        t.text = str(valor)
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    def numero(self, ref, valor):
        c = self.celda(ref)
        self._limpiar(c)
        if valor is None:
            return
        etree.SubElement(c, _q(M, "v")).text = repr(float(valor)) if not float(valor).is_integer() else str(int(valor))

    def formula(self, ref, expr):
        c = self.celda(ref)
        self._limpiar(c)
        etree.SubElement(c, _q(M, "f")).text = expr.lstrip("=")

    def vaciar(self, ref):
        c = self.celda(ref, crear=False)
        if c is not None:
            self._limpiar(c)

    def poner(self, ref, valor):
        """Escribe numero o texto segun el tipo de Python."""
        if isinstance(valor, bool) or valor is None:
            self.texto(ref, "" if valor is None else str(valor))
        elif isinstance(valor, (int, float)):
            self.numero(ref, valor)
        else:
            self.texto(ref, valor)

    def quitar_hipervinculos(self):
        hl = self.raiz.find(_q(M, "hyperlinks"))
        if hl is not None:
            self.raiz.remove(hl)
        rels = self.paquete.rels_de(self.parte)
        if rels is not None:
            for r in list(rels.getroot()):
                if r.get("Type", "").endswith("/hyperlink"):
                    rels.getroot().remove(r)

    def ruta_dibujo(self):
        """Parte del drawing asociado a la hoja (o None)."""
        d = self.raiz.find(_q(M, "drawing"))
        if d is None:
            return None
        rels = self.paquete.rels_de(self.parte)
        for r in rels.getroot():
            if r.get("Id") == d.get(_q(R, "id")):
                return posixpath.normpath(posixpath.join(posixpath.dirname(self.parte), r.get("Target")))
        return None


class Paquete:
    def __init__(self, origen):
        with zipfile.ZipFile(origen) as z:
            self.orden = [i.filename for i in z.infolist()]
            self.partes = {n: z.read(n) for n in self.orden}
        self._xml = {}
        self._hojas = None

    # ---- xml cacheado
    def xml(self, nombre):
        if nombre not in self._xml:
            self._xml[nombre] = etree.fromstring(self.partes[nombre])
        return self._xml[nombre]

    def rels_de(self, parte):
        nombre = posixpath.join(posixpath.dirname(parte), "_rels", posixpath.basename(parte) + ".rels")
        if nombre not in self.partes:
            return None
        if ("rels", nombre) not in self._xml:
            self._xml[("rels", nombre)] = etree.ElementTree(etree.fromstring(self.partes[nombre]))
        return self._xml[("rels", nombre)]

    def _nombre_rels(self, parte):
        return posixpath.join(posixpath.dirname(parte), "_rels", posixpath.basename(parte) + ".rels")

    # ---- hojas por nombre
    def _cargar_hojas(self):
        if self._hojas is None:
            wb = self.xml("xl/workbook.xml")
            rels = {r.get("Id"): r.get("Target") for r in self.rels_de("xl/workbook.xml").getroot()}
            self._hojas = {s.get("name"): "xl/" + rels[s.get(_q(R, "id"))].lstrip("/").replace("xl/", "")
                           for s in wb.find(_q(M, "sheets"))}

    def hoja(self, nombre):
        self._cargar_hojas()
        return Hoja(self, self._hojas[nombre])

    def hojas(self):
        self._cargar_hojas()
        return list(self._hojas)

    # ---- limpieza global
    def congelar_vinculos_externos(self):
        """Formulas que apuntan a otros libros ([1]Hoja!A1) pasan a valor fijo (el cache que ya traen)
        y se eliminan los vinculos externos: asi Excel no pide actualizar vinculos al abrir."""
        for nombre in self.hojas():
            h = self.hoja(nombre)
            for c in h.datos.iter(_q(M, "c")):
                f = c.find(_q(M, "f"))
                if f is not None and re.search(r"\[\d+\]", f.text or ""):
                    v = c.find(_q(M, "v"))
                    valor = v.text if v is not None else ""
                    tipo = c.get("t")
                    c.remove(f)
                    for hijo in list(c):
                        c.remove(hijo)
                    if tipo == "str":
                        c.set("t", "inlineStr")
                        t = etree.SubElement(etree.SubElement(c, _q(M, "is")), _q(M, "t"))
                        t.text = valor
                        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                    elif valor not in (None, ""):
                        if "t" in c.attrib:
                            del c.attrib["t"]
                        etree.SubElement(c, _q(M, "v")).text = valor
        wb = self.xml("xl/workbook.xml")
        ext = wb.find(_q(M, "externalReferences"))
        if ext is not None:
            wb.remove(ext)
        nombres = wb.find(_q(M, "definedNames"))
        if nombres is not None:
            for dn in list(nombres):
                if re.search(r"\[\d+\]", dn.text or "") or dn.get("name") == "_xlnm.Recorder":
                    nombres.remove(dn)
        rels = self.rels_de("xl/workbook.xml").getroot()
        for r in list(rels):
            if r.get("Type", "").endswith("/externalLink"):
                rels.remove(r)
        for n in [n for n in self.partes if n.startswith("xl/externalLinks/")]:
            self._quitar_parte(n)

    def forzar_recalculo(self):
        """Quita los valores en cache de las formulas: Excel y LibreOffice las recalculan al abrir."""
        for nombre in self.hojas():
            for c in self.hoja(nombre).datos.iter(_q(M, "c")):
                f = c.find(_q(M, "f"))
                if f is not None:
                    v = c.find(_q(M, "v"))
                    if v is not None:
                        c.remove(v)
                    if c.get("t") in ("str", "e", "b"):
                        del c.attrib["t"]
        wb = self.xml("xl/workbook.xml")
        calc = wb.find(_q(M, "calcPr"))
        if calc is None:
            calc = etree.SubElement(wb, _q(M, "calcPr"))
        calc.set("fullCalcOnLoad", "1")
        # calcChain obsoleta: Excel la reconstruye
        if "xl/calcChain.xml" in self.partes:
            self._quitar_parte("xl/calcChain.xml")
            rels = self.rels_de("xl/workbook.xml").getroot()
            for r in list(rels):
                if r.get("Type", "").endswith("/calcChain"):
                    rels.remove(r)

    def quitar_textos_fijos_de_graficas(self):
        """Etiquetas de datos con texto escrito a mano (de un avaluo anterior): se vuelven automaticas."""
        C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
        for nombre in [n for n in self.partes if re.fullmatch(r"xl/charts/chart\d+\.xml", n)]:
            for dlbl in self.xml(nombre).iter(f"{{{C}}}dLbl"):
                for tx in dlbl.findall(f"{{{C}}}tx"):
                    dlbl.remove(tx)

    def _quitar_parte(self, nombre):
        self.partes.pop(nombre, None)
        if nombre in self.orden:
            self.orden.remove(nombre)
        self._xml.pop(nombre, None)
        ct = self.xml("[Content_Types].xml")
        for o in list(ct):
            if o.get("PartName") == "/" + nombre:
                ct.remove(o)

    # ---- imagenes
    def reemplazar_imagen(self, parte_dibujo, indice, contenido: bytes):
        """Cambia el archivo de la imagen n-esima (en orden de aparicion) del dibujo."""
        destino = self._media_de(parte_dibujo, indice)
        self.partes[destino] = contenido
        # sin efectos artisticos ni copia HD de la foto anterior (si no, Excel la mezclaria con la nueva)
        blip = self._anclas(parte_dibujo)[indice].find(".//" + _q(A, "blip"))
        for ext in blip.findall(_q(A, "extLst")):
            blip.remove(ext)
        rels = self.rels_de(parte_dibujo).getroot()
        for r in list(rels):
            if r.get("Target", "").endswith(".wdp"):
                rels.remove(r)
        return destino

    def _anclas(self, parte_dibujo):
        raiz = self.xml(parte_dibujo)
        return [a for a in raiz if a.tag in (_q(XDR, "twoCellAnchor"), _q(XDR, "oneCellAnchor"))
                and a.find(".//" + _q(A, "blip")) is not None]

    def _media_de(self, parte_dibujo, indice):
        ancla = self._anclas(parte_dibujo)[indice]
        rid = ancla.find(".//" + _q(A, "blip")).get(_q(R, "embed"))
        for r in self.rels_de(parte_dibujo).getroot():
            if r.get("Id") == rid:
                return posixpath.normpath(posixpath.join(posixpath.dirname(parte_dibujo), r.get("Target")))
        raise KeyError(rid)

    def dimensiones_imagen(self, parte_dibujo, indice):
        from PIL import Image
        return Image.open(io.BytesIO(self.partes[self._media_de(parte_dibujo, indice)])).size

    def quitar_imagenes(self, parte_dibujo, indices):
        """Elimina del dibujo las imagenes indicadas (se usa para los espacios de foto que quedan sin usar)."""
        anclas = self._anclas(parte_dibujo)
        rels = self.rels_de(parte_dibujo).getroot()
        for i in sorted(indices, reverse=True):
            a = anclas[i]
            rid = a.find(".//" + _q(A, "blip")).get(_q(R, "embed"))
            a.getparent().remove(a)
            for r in list(rels):
                if r.get("Id") == rid:
                    rels.remove(r)

    def podar_medios_sin_uso(self):
        """Borra imagenes que ya nadie referencia (por ejemplo las fotos del avaluo de muestra)."""
        usados = set()
        for nombre in list(self.partes):
            if nombre.endswith(".rels"):
                base = posixpath.dirname(posixpath.dirname(nombre))
                raiz = etree.fromstring(self.partes[nombre]) if ("rels", nombre) not in self._xml else self._xml[("rels", nombre)].getroot()
                for r in raiz:
                    if r.get("TargetMode") != "External":
                        usados.add(posixpath.normpath(posixpath.join(base, r.get("Target"))))
        for nombre in [n for n in self.partes if n.startswith("xl/media/") and n not in usados]:
            self._quitar_parte(nombre)

    # ---- guardar
    def guardar(self, destino):
        for nombre, raiz in self._xml.items():
            if isinstance(nombre, tuple):
                clave = nombre[1]
                self.partes[clave] = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)
            else:
                self.partes[nombre] = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            for n in self.orden:
                if n in self.partes:
                    z.writestr(n, self.partes[n])
