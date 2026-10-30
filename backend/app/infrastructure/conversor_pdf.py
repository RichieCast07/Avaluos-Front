"""PDF del avaluo: se imprime el mismo Excel con LibreOffice (sin ventana).

Solo se imprimen las hojas que forman el documento; las de trabajo (Resumen, I-Espec, Medidas...) se
ocultan en una copia temporal, asi el PDF sale igual que el que se obtiene al imprimir desde Excel.
"""
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

NO_IMPRIMIR = ["Resumen", "I-Espec", "A3.Medidas", "Hoja1", "listas"]


class ErrorConversion(RuntimeError):
    pass


def _ocultar_hojas(origen, destino):
    with zipfile.ZipFile(origen) as zin, zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            datos = zin.read(item.filename)
            if item.filename == "xl/workbook.xml":
                txt = datos.decode("utf-8")

                def ocultar(m):
                    tag = m.group(0)
                    nombre = re.search(r'name="([^"]*)"', tag).group(1).strip()
                    if nombre in NO_IMPRIMIR and "state=" not in tag:
                        tag = tag.replace("<sheet ", '<sheet state="hidden" ', 1)
                    return tag

                txt = re.sub(r"<sheet [^>]*/>", ocultar, txt)
                # LibreOffice imprime hojas ocultas que tengan area de impresion: se quita en la copia
                for n in NO_IMPRIMIR:
                    txt = re.sub(r'<definedName name="_xlnm.Print_Area"[^>]*>\'?' + re.escape(n) + r" ?'?![^<]*</definedName>", "", txt)
                datos = txt.encode("utf-8")
            zout.writestr(item, datos)


def _soffice():
    """`soffice` del PATH (Docker/Linux); en Windows, la instalacion por defecto de LibreOffice."""
    encontrado = shutil.which("soffice")
    if encontrado:
        return encontrado
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            ruta = os.path.join(base, "LibreOffice", "program", "soffice.exe")
            if os.path.exists(ruta):
                return ruta
    raise ErrorConversion("No se encontro LibreOffice (soffice). Instalalo para generar el PDF.")


def xlsx_a_pdf(xlsx, pdf):
    tmp = tempfile.mkdtemp()
    try:
        copia = os.path.join(tmp, "avaluo.xlsx")
        _ocultar_hojas(xlsx, copia)
        perfil = Path(tmp, "perfil").as_uri()   # perfil propio: evita choques si hay dos conversiones a la vez
        r = subprocess.run([_soffice(), f"-env:UserInstallation={perfil}", "--headless", "--convert-to", "pdf",
                            "--outdir", tmp, copia], capture_output=True, text=True, timeout=180)
        salida = os.path.join(tmp, "avaluo.pdf")
        if r.returncode != 0 or not os.path.exists(salida):
            raise ErrorConversion(f"LibreOffice no pudo generar el PDF: {r.stderr[-300:]}")
        shutil.move(salida, pdf)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
