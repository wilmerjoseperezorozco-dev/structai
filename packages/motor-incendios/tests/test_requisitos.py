"""Requisitos NSR-10 J (#336 F1), casos calculados a mano con las tablas transcritas en src/tablas_j.py."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import requisitos as rq  # noqa: E402
from src import tablas_j as T  # noqa: E402


def _ex(xs, sistema):
    return next(x for x in xs if x.sistema == sistema)


# --- J.3.3: categoría de riesgo
def test_oficinas_de_8_pisos_y_5000_m2_son_categoria_I():
    r = rq.categoria_riesgo("C-1", 8, 5000.0)          # C-1, AT > 1500, columna ≥ 7 pisos
    assert r.valor == "I" and r.numeral == "Tabla J.3.3-1"


def test_oficinas_de_3_pisos_y_1200_m2_son_categoria_III():
    assert rq.categoria_riesgo("C-1", 3, 1200.0).valor == "III"     # AT < 1500, 3 pisos


def test_en_el_limite_de_area_se_usa_la_fila_mas_exigente():
    assert rq.categoria_riesgo("C-1", 3, 1500.0).valor == "II"      # fila AT > 1500 con 3 pisos


def test_mas_de_10_pisos_depende_de_alarmas_y_rociadores():
    assert rq.categoria_riesgo("R-2", 12, 9000.0).valor == "I"
    r = rq.categoria_riesgo("R-2", 12, 9000.0, alarmas_y_rociadores=True)
    assert r.valor == "II" and r.numeral == "J.3.3.1.2(a)"


def test_filas_sin_verificar_no_clasifican():
    assert rq.categoria_riesgo("C-2", 2, 300.0).valor is None
    r = rq.categoria_riesgo("R-2", 5, 3000.0, area_unidad_promedio_m2=80.0)
    assert r.valor is None and "sin verificar" in r.motivo


def test_fabril_por_potencial_combustible():
    assert rq.categoria_riesgo("F-1", 2, 800.0, cc_mj_m2=3000.0).valor == "II"     # 2000 < Cc < 4000, 2 pisos
    assert rq.categoria_riesgo("F-1", 2, 800.0).valor is None                     # falta Cc


def test_exenciones_j333():
    assert rq.exento_cuantificacion(rq.Edificacion("C-1", 2, 7.0, 900.0)).valor is True      # ≤ 2 pisos, 450 m²/piso
    assert rq.exento_cuantificacion(rq.Edificacion("C-1", 2, 7.0, 1200.0)).valor is False    # 600 m²/piso
    assert rq.exento_cuantificacion(rq.Edificacion("R-2", 3, 8.4, 2000.0)).numeral == "J.3.3.3.3"


# --- J.3.4-3 y J.3.5
def test_horas_requeridas_por_categoria():
    assert rq.horas_requeridas("I")["estructura_portante"] == 2.0
    assert rq.horas_requeridas("II")["estructura_portante"] == 1.5
    assert rq.horas_requeridas("III")["muro_interior_no_portante"] is None


def test_concreto_15_h_siliceo_a_mano():
    v = rq.verificar_concreto(1.5, columnas_mm=((300, 300), (200, 200)), losa_mm=100.0, recub_losa_mm=20.0,
                              vigas=((300, 40.0),))
    col_ok, col_mal, losa, rec_losa, viga = v
    assert (col_ok.requerido, col_ok.cumple) == (230, True)
    assert col_mal.cumple is False
    assert (losa.requerido, losa.cumple) == (110, False)            # J.3.5-2 silíceo 1½ h
    assert (rec_losa.requerido, rec_losa.cumple) == (20, True)      # J.3.5-3 no restringida 1½ h
    assert (viga.requerido, viga.cumple) == (20, True)              # J.3.5-5 ancho ≥ 250


def test_columna_alargada_reduce_la_dimension_minima():
    v = rq.verificar_concreto(2.0, columnas_mm=((200, 1000),))[0]
    assert v.requerido == 200 and v.cumple and "950" in v.nota


def test_recubrimiento_de_viga_interpolado():
    v = rq.verificar_concreto(1.5, vigas=((155.0, 24.0),))[0]       # entre 130 (30) y 180 (20): 25 mm
    assert v.requerido == pytest.approx(25.0) and v.cumple is False


def test_viga_angosta_sin_restriccion_no_alcanza_3_h():
    v = rq.verificar_concreto(3.0, vigas=((130.0, 50.0),))[0]
    assert v.requerido is None and v.cumple is False


# --- J.4.3
def test_multifamiliar_de_10_pisos_con_parqueadero():
    xs = rq.sistemas_exigidos(rq.Edificacion("R-2", 10, 28.0, 6000.0, estacionamiento_bajo=True))
    roc = _ex(xs, "rociadores")
    assert roc.exigido and roc.numerales == ["J.4.3.8.1(a)", "J.4.3.8.1(b)"]
    assert "zonas comunes" in roc.alcance and "estacionamiento" in roc.alcance
    assert _ex(xs, "tomas_fijas_mangueras").exigido and _ex(xs, "extintores").exigido
    assert _ex(xs, "estaciones_manguera_38mm").numerales == ["J.4.3.8.2(c)"]


def test_multifamiliar_de_5_pisos_solo_extintores():
    xs = rq.sistemas_exigidos(rq.Edificacion("R-2", 5, 14.0, 2500.0))
    assert not _ex(xs, "rociadores").exigido and not _ex(xs, "tomas_fijas_mangueras").exigido
    assert _ex(xs, "extintores").exigido


def test_oficinas_de_7_pisos_requieren_rociadores():
    xs = rq.sistemas_exigidos(rq.Edificacion("C-1", 7, 21.0, 7000.0))
    assert _ex(xs, "rociadores").numerales == ["J.4.3.2.1(d)"]
    xs6 = rq.sistemas_exigidos(rq.Edificacion("C-1", 6, 18.0, 6000.0))
    assert not _ex(xs6, "rociadores").exigido                      # ni > 6 pisos ni > 18 m


def test_uso_mixto_une_las_exigencias():
    xs = rq.sistemas_exigidos(rq.Edificacion("M", 8, 24.0, 8000.0, usos_mixtos=("C-2", "R-2")))
    roc = _ex(xs, "rociadores")
    assert roc.exigido and roc.numerales[0] == "J.4.3.6"
    assert any("uso C-2" in n for n in roc.numerales) and any("uso R-2" in n for n in roc.numerales)


def test_grupo_sin_numeral_propio_lo_dice():
    xs = rq.sistemas_exigidos(rq.Edificacion("E", 2, 6.0, 400.0))
    assert not any(x.exigido for x in xs) and "no tiene numeral propio" in xs[0].nota


def test_hay_celdas_pendientes_de_verificar():
    assert len(T.VERIFICAR) >= 4 and T.J33_1["C-2"][1][2] is None
