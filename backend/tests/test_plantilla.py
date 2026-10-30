"""El Excel llenado debe recalcular (en LibreOffice) los mismos numeros que el dominio y salir en 11 paginas."""
import os
import re
import shutil
import subprocess

import pytest

from app.domain import calculo, plantillas
from app.infrastructure import conversor_pdf, plantilla_avaluo
from app.services.empresa import DEFECTO

hay_soffice = shutil.which("soffice") is not None
pytestmark = pytest.mark.skipif(not hay_soffice, reason="LibreOffice no esta instalado")


@pytest.fixture(scope="module")
def generado(tmp_path_factory):
    d = tmp_path_factory.mktemp("plantilla")
    xlsx, pdf = str(d / "a.xlsx"), str(d / "a.pdf")
    plantilla_avaluo.generar(plantillas.ejemplo(), DEFECTO, {"anexo": []}, xlsx)
    conversor_pdf.xlsx_a_pdf(xlsx, pdf)
    return d, xlsx, pdf


def _texto_pdf(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout


def test_pdf_de_11_paginas(generado):
    _, _, pdf = generado
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    assert re.search(r"Pages:\s+11", info)


def test_pdf_trae_el_valor_de_conclusion(generado):
    _, _, pdf = generado
    calc = calculo.calcular(plantillas.ejemplo())
    assert f"{calc['conclusion']['valor']:,.0f}" in _texto_pdf(pdf)


def test_excel_recalculado_coincide_con_el_dominio(generado):
    from openpyxl import load_workbook
    d, xlsx, _ = generado
    perfil = str(d / "perfil")
    subprocess.run(["soffice", f"-env:UserInstallation=file://{perfil}", "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                    "--outdir", str(d / "recalc"), xlsx], capture_output=True, timeout=180, check=True)
    wb = load_workbook(str(d / "recalc" / "a.xlsx"), data_only=True)
    calc = calculo.calcular(plantillas.ejemplo())
    assert wb["Conclusión"]["D29"].value == calc["conclusion"]["valor"]


@pytest.mark.parametrize("modo", ["mercado", "fisico", "promedio"])
def test_modos_de_conclusion_y_menos_comparables(tmp_path, modo):
    from openpyxl import load_workbook
    data = plantillas.ejemplo()
    data["conclusion"]["valor_conclusion"] = modo
    data["comparables_terreno"]["items"] = data["comparables_terreno"]["items"][:3]
    data["comparables_inmuebles"]["items"] = data["comparables_inmuebles"]["items"][:2]
    xlsx = str(tmp_path / "m.xlsx")
    plantilla_avaluo.generar(data, DEFECTO, {"anexo": []}, xlsx)
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path / 'p'}", "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                    "--outdir", str(tmp_path / "r"), xlsx], capture_output=True, timeout=180, check=True)
    wb = load_workbook(str(tmp_path / "r" / "m.xlsx"), data_only=True)
    assert wb["Conclusión"]["D29"].value == calculo.calcular(data)["conclusion"]["valor"]
