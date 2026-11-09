"""Figuras de acero y verificaciones NSR-10: valores a mano."""
import math

import pytest

from src.despiece_proyecto import comparar_escenarios
from src.figuras_acero import (barra_C, barra_L, barra_S, diametro_doblado_mm, dovela, estribo_cerrado, extension_135_mm,
                               gancho_suplementario, longitud_desarrollo_traccion_mm, longitud_gancho_ldh_mm, traslapo_compresion_mm,
                               traslapo_traccion_mm, verificar_diametro_doblado, verificar_gancho, verificar_traslapo)


def test_diametro_doblado_estribo_y_barra():
    assert diametro_doblado_mm("3", estribo=True) == pytest.approx(4 * 9.5)
    assert diametro_doblado_mm("5", estribo=True) == pytest.approx(4 * 15.9)
    assert diametro_doblado_mm("6", estribo=True) == pytest.approx(6 * 19.1)
    assert diametro_doblado_mm("5") == pytest.approx(6 * 15.9)


def test_barra_mayor_que_8_no_soportada():
    with pytest.raises(ValueError):
        diametro_doblado_mm("9")


def test_barra_L_descuenta_un_doblez_de_90():
    db = 15.9
    ro, rc = 3 * db + db, (6 * db + db) / 2
    ded = (2 * ro - math.pi / 2 * rc) / 1000
    assert barra_L("5", 1.0, 0.3).longitud_corte_m == pytest.approx(1.3 - ded)


def test_barra_C_dos_dobleces():
    ded = 1.3 - barra_L("5", 1.0, 0.3).longitud_corte_m
    assert barra_C("5", 1.0, 0.3, 0.3).longitud_corte_m == pytest.approx(1.6 - 2 * ded)


def test_estribo_cerca_del_perimetro_mas_ganchos():
    f = estribo_cerrado("3", 300, 600)
    bruto = (2 * (220 + 520) + 2 * extension_135_mm("3")) / 1000
    ded = (2 * 28.5 - math.pi / 2 * 23.75) / 1000                           # D = 4·9,5 = 38; ro = 28,5; rc = 23,75
    assert f.longitud_corte_m == pytest.approx(bruto - 4 * ded)
    assert extension_135_mm("3") == 75.0                                   # 6·9,5 = 57 < 75


def test_S_pendiente_fuerte_advierte():
    assert barra_S("6", 1.0, 1.0, 0.10, 0.30).advertencias
    assert not barra_S("6", 1.0, 1.0, 0.05, 0.60).advertencias


def test_gancho_suplementario_y_dovela():
    assert gancho_suplementario("3", 220).longitud_corte_m > 0.25
    assert dovela("6", 0.5, 0.8).longitud_corte_m == pytest.approx(1.3 + 12 * 19.1 / 1000, abs=0.05)


def test_ld_y_traslapos_c12():
    ld = longitud_desarrollo_traccion_mm("5", 28.0, 420.0)
    assert ld == pytest.approx(420 / (1.4 * math.sqrt(28)) * 15.9)
    assert traslapo_traccion_mm("5", 28.0, 420.0) == pytest.approx(1.3 * ld)
    assert traslapo_traccion_mm("5", 28.0, 420.0, clase="A") < traslapo_traccion_mm("5", 28.0, 420.0)
    assert traslapo_compresion_mm("6", 28.0, 420.0) == pytest.approx(0.071 * 420 * 19.1)
    assert traslapo_compresion_mm("6", 18.0, 420.0) == pytest.approx(0.071 * 420 * 19.1 * 4 / 3)
    assert longitud_gancho_ldh_mm("5", 28.0, 420.0) >= max(8 * 15.9, 150)


def test_recomendacion_nunca_baja_del_minimo():
    h = verificar_traslapo("5", 400.0, 28.0, 420.0)
    assert not h.cumple and h.valor_recomendado >= traslapo_traccion_mm("5", 28.0, 420.0)
    assert verificar_traslapo("5", 2000.0, 28.0, 420.0).cumple


def test_gancho_y_doblado_incumplidos():
    h = verificar_gancho("5", 90, 100.0)
    assert not h.cumple and h.valor_recomendado == 195.0                    # 12·15,9 = 190,8 → 195
    assert verificar_gancho("3", 135, 75.0, estribo=True).cumple
    assert not verificar_gancho("3", 120, 80.0).cumple
    assert not verificar_diametro_doblado("5", 4 * 15.9).cumple
    assert verificar_diametro_doblado("5", 4 * 15.9, estribo=True).cumple


def test_escenarios_orden_esperado():
    barras = [("5", 5.6)] * 20 + [("5", 14.0)] * 4 + [("3", 1.6)] * 100
    esc = {e.nombre[0]: e for e in comparar_escenarios(barras, 4000.0, largo_maximo_pedido_m=18.0)}
    assert esc["B"].comprada_m <= esc["A"].comprada_m + 1e-9
    assert esc["C"].comprada_m <= esc["B"].comprada_m + 1e-9
    assert esc["C"].comprada_m <= esc["D"].comprada_m + 1e-9
    assert esc["E"].comprada_m <= esc["C"].comprada_m + 1e-9
