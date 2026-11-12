"""Pruebas del módulo de unidades (#207). Cada valor esperado se puede verificar a mano."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.unidades import (FaltaDato, convertir, convertir_precio, equivalencia_fc, expansion_suelo, formatear,  # noqa: E402
                          formatear_precio, normalizar, regla_de_tres)


# ── Capa 1: normalización (reglas de práctica colombiana) ────────────────────────────────────────────────
@pytest.mark.parametrize("texto", ["m", "M", "mt", "Mts", "metro", "ml", "ML", "Ml", "metros lineales"])
def test_metro_es_metro_lineal(texto):
    assert normalizar(texto).unidad == "ml"


@pytest.mark.parametrize("texto,esperada", [("m2", "m2"), ("M²", "m2"), ("mts2", "m2"), ("m^3", "m3"), ("M3", "m3"),
                                            ("und", "un"), ("UND", "un"), ("Unidad", "un"), ("lts", "L"),
                                            ("Galón", "gal"), ("Kg", "kg"), ("hr", "h"), ("Global", "gl"), ("GLB", "gl")])
def test_alias(texto, esperada):
    assert normalizar(texto).unidad == esperada


@pytest.mark.parametrize("seccion", ["transporte", "mano_obra", "equipo"])
def test_gl_en_transporte_mano_obra_equipo_es_global(seccion):
    assert normalizar("gl", seccion=seccion).unidad == "gl"


def test_gl_en_materiales_es_galon():
    assert normalizar("gl", seccion="materiales", descripcion="Imprimacion antioxidante").unidad == "gal"
    assert normalizar("GL", seccion="materiales", descripcion="Pegante PVC").unidad == "gal"


def test_gl_por_descripcion_sin_seccion():
    assert normalizar("gl", descripcion="Descapote y limpieza del lote").unidad == "gl"
    assert normalizar("gl", descripcion="Pintura vinilo tipo 1").unidad == "gal"


def test_gl_sin_contexto_es_ambigua_y_no_se_adivina():
    r = normalizar("gl")
    assert r.unidad is None and r.ambigua


def test_presentacion_comercial_no_se_convierte_sola():
    r = normalizar("Bulto")
    assert r.unidad is None and r.presentacion == "bulto"


def test_basura_es_ambigua():
    assert normalizar("Fecha de Finalización (DD/MM/AAAA)").ambigua
    assert normalizar("").ambigua


# ── Capa 2A: misma dimensión (factores exactos) ──────────────────────────────────────────────────────────
def test_psi_a_mpa_exacto():
    assert convertir(3000, "psi", "MPa").valor == pytest.approx(20.684271879, rel=1e-9)


def test_equivalencia_nominal_fc_distinta_de_la_exacta():
    e = equivalencia_fc(21.0)
    assert e["psi_nominal"] == 3000
    assert e["psi_exacto"] == pytest.approx(3045.8, abs=0.1)


@pytest.mark.parametrize("valor,de,a,esperado", [
    (1, "gal", "L", 3.785411784), (1, "ha", "m2", 10_000), (1, "pulg", "mm", 25.4), (1, "kgf/cm2", "kPa", 98.0665),
    (1, "tf", "kN", 9.80665), (1, "HP", "kW", 0.74569987), (100, "L/s", "m3/h", 360), (10, "mca", "kPa", 98.0665),
    (0.25, "gn", "m/s2", 2.4516625),
])
def test_factores(valor, de, a, esperado):
    assert convertir(valor, de, a).valor == pytest.approx(esperado, rel=1e-8)


@pytest.mark.parametrize("de,a", [("psi", "MPa"), ("gal", "L"), ("tf", "kN"), ("gpm", "L/s"), ("pie2", "m2")])
def test_ida_y_vuelta(de, a):
    v = 123.456
    assert convertir(convertir(v, de, a).valor, a, de).valor == pytest.approx(v, rel=1e-12)


def test_galon_con_contenido_del_envase():
    r = convertir(1, "gal", "L", contenido_L=3.74)
    assert r.valor == pytest.approx(3.74) and "declarado" in r.formula


# ── Capa 2B: cambio de dimensión SOLO con dato puente ────────────────────────────────────────────────────
def test_m3_a_m2_sin_espesor_pide_el_dato():
    with pytest.raises(FaltaDato) as e:
        convertir(1, "m3", "m2")
    assert e.value.dato == "espesor_m"


def test_m3_a_m2_con_espesor():
    r = convertir(1, "m3", "m2", espesor_m=0.10)
    assert r.valor == pytest.approx(10) and "espesor" in r.formula


def test_m2_a_ml_con_ancho():
    assert convertir(3, "m2", "ml", ancho_m=1.5).valor == pytest.approx(2)


def test_ml_de_barra_a_kg():
    # barra #4 (1/2"): π/4 · 0,0127² · 7850 = 0,9944 kg/m
    r = convertir(100, "ml", "kg", diametro_barra="4")
    assert r.valor == pytest.approx(99.44, abs=0.05) and r.advertencias


def test_m3_a_t_con_densidad():
    assert convertir(2, "m3", "t", densidad_t_m3=1.8).valor == pytest.approx(3.6)


def test_horas_a_dias_requiere_jornada():
    with pytest.raises(FaltaDato):
        convertir(16, "h", "dia")
    assert convertir(16, "h", "dia", jornada_h=8).valor == pytest.approx(2)


def test_tubos_se_redondean_hacia_arriba():
    r = convertir(25, "ml", "un", longitud_pieza_m=6)
    assert r.valor == 5 and not r.exacta


def test_global_no_se_convierte():
    with pytest.raises(ValueError):
        convertir(1, "gl", "un")


def test_expansion_suelo():
    assert expansion_suelo(10, 1.25).valor == pytest.approx(12.5)


# ── Precios: la conversión va al revés que la cantidad ───────────────────────────────────────────────────
def test_precio_m3_a_m2_plantilla():
    # $600.000/m³ con 10 cm de espesor → 1 m³ = 10 m² → $60.000/m²
    r = convertir_precio(600_000, "m3", "m2", espesor_m=0.10)
    assert r.valor == pytest.approx(60_000)
    assert formatear_precio(r.valor, "m2") == "$ 60.000 / m²"


def test_precio_no_admite_redondeo_de_piezas():
    with pytest.raises(ValueError):
        convertir_precio(1000, "ml", "un", longitud_pieza_m=6)


# ── Regla de tres ────────────────────────────────────────────────────────────────────────────────────────
def test_regla_de_tres_simple():
    r = regla_de_tres(2, 50, 7)
    assert r.valor == pytest.approx(175) and "X =" in r.formula and not r.advertencias


def test_regla_de_tres_con_costo_fijo():
    # 10 m³ cuestan 1.000.000 incluyendo 200.000 de movilización: 25 m³ = 800.000·2,5 + 200.000
    r = regla_de_tres(10, 1_000_000, 25, costo_fijo=200_000)
    assert r.valor == pytest.approx(2_200_000) and r.advertencias


def test_regla_de_tres_advierte_anios_y_no_lineal():
    assert not regla_de_tres(1, 1, 1, anios_distintos=True).exacta
    assert not regla_de_tres(1, 1, 1, no_lineal=True).exacta


# ── Formato colombiano ───────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("x,s", [(12500.5, "12.500"), (60000, "60.000"), (3.785411784, "3,79"), (0.0254, "0,0254"),
                                 (1, "1")])
def test_formato(x, s):
    assert formatear(x) == s


def test_formato_no_pierde_signo():
    assert formatear(-1500) == "-1.500"
    assert not math.isnan(convertir(0, "m2", "m2").valor)


# ── Transporte compuesto (INVIAS) ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("texto,esperada", [("m3-km", "m3-km"), ("KG-KM", "kg-km"), ("l- km", "L-km"), ("H/H", "h"),
                                            ("UNID", "un")])
def test_alias_nuevos(texto, esperada):
    assert normalizar(texto).unidad == esperada


def test_precio_m3km_a_m3_con_distancia():
    # acarreo a $1.500 por m³-km; con 12 km de distancia cuesta $18.000 por m³
    r = convertir_precio(1500, "m3-km", "m3", distancia_km=12)
    assert r.valor == pytest.approx(18_000)


def test_m3km_sin_distancia_pide_el_dato():
    with pytest.raises(FaltaDato) as e:
        convertir(50, "m3-km", "m3")
    assert e.value.dato == "distancia_km"
