"""El calculo debe reproducir el Excel original (avaluo Jose Mariano Jimenez 614)."""
import pytest

from app.domain import calculo, plantillas
from app.domain.numero_letras import pesos_a_letras


@pytest.fixture(scope="module")
def r():
    return calculo.calcular(plantillas.ejemplo())


def test_terreno(r):
    assert [round(f["homologado"]) for f in r["terreno"]["filas"]] == [32225, 34707, 31573, 38378]
    assert round(r["terreno"]["valor_homologado"]) == 34221
    assert r["terreno"]["vnr"] == 34200


def test_costos(r):
    assert r["costos"]["terreno_sub"] == pytest.approx(4_833_144.00)
    assert r["costos"]["construccion_sub"] == pytest.approx(2_360_637.972)
    assert r["costos"]["valor_fisico"] == pytest.approx(7_193_781.972)


def test_mercado_y_conclusion(r):
    assert [round(f["homologado"]) for f in r["inmuebles"]["filas"]] == [34439, 24006, 35509, 29419]
    assert r["inmuebles"]["en_nr"] == 30840
    assert r["inmuebles"]["subtotal"] == 7_648_320
    assert r["conclusion"]["valor"] == 7_648_000
    assert r["conclusion"]["valor_fisico"] == 7_194_000
    assert r["conclusion"]["letras"] == "SIETE MILLONES SEISCIENTOS CUARENTA Y OCHO MIL PESOS 00/100 M.N."
    assert r["conclusion"]["fecha_texto"] == "15 de octubre 2026"


def test_modos_de_conclusion():
    d = plantillas.ejemplo()
    d["conclusion"]["valor_conclusion"] = "fisico"
    assert calculo.calcular(d)["conclusion"]["valor"] == 7_194_000
    d["conclusion"]["valor_conclusion"] = "promedio"
    assert calculo.calcular(d)["conclusion"]["valor"] == 7_421_000


def test_avaluo_vacio_no_truena():
    r = calculo.calcular(plantillas.vacio())
    assert r["conclusion"]["valor"] == 0


def test_redondeo_como_excel():
    assert calculo.xround(2.5) == 3 and calculo.xround(-2.5) == -3 and calculo.xround(34221, -2) == 34200


@pytest.mark.parametrize("n,txt", [
    (1, "UN PESOS"), (21_000, "VEINTIUN MIL PESOS"), (100, "CIEN PESOS"), (115_000, "CIENTO QUINCE MIL PESOS"),
    (1_000_000, "UN MILLON DE PESOS"), (2_500_000, "DOS MILLONES QUINIENTOS MIL PESOS"), (0, "CERO PESOS"),
])
def test_letras(n, txt):
    assert pesos_a_letras(n) == f"{txt} 00/100 M.N."
