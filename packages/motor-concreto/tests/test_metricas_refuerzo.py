"""Métricas de detallado: valores a mano y propiedades."""
import math

import pytest

from src.diseno_viga import DisenoViga
from src.metricas_refuerzo import (as_requerida, corte_1d, costo_mano_obra, eficiencia_acero, eficiencia_confinamiento,
                                   holgura_libre, libre_disponible_mm, libre_exigido_mm)
from src.viga import AREA_MM2

VIGA = DisenoViga(b=300, h=600, dia="6", n_sup=3, n_inf=3, estribo_dia="3", s_conf=100, s_centro=200, n_estribos=40, nivel="DMO", verificaciones=())


def test_as_requerida_reproduce_el_momento():
    fc, fy, b, d, mu = 28.0, 420.0, 300.0, 540.0, 200.0
    a_s = as_requerida(mu, b, d, fc, fy)
    a = a_s * fy / (0.85 * fc * b)
    assert 0.9 * a_s * fy * (d - a / 2) / 1e6 == pytest.approx(mu, rel=1e-9)


def test_as_requerida_sin_solucion_y_sin_demanda():
    assert as_requerida(1e6, 300, 540, 28, 420) == math.inf
    assert as_requerida(0.0, 300, 540, 28, 420) == 0.0


def test_eficiencia_acero():
    assert eficiencia_acero(1200.0, 1000.0) == pytest.approx(1.2)
    assert eficiencia_acero(100.0, 0.0) == math.inf


def test_libre_exigido_incluye_4_3_tmn():
    assert libre_exigido_mm(19.1) == 25.0
    assert libre_exigido_mm(28.7) == pytest.approx(28.7)
    assert libre_exigido_mm(19.1, 25.0) == pytest.approx(100.0 / 3.0)        # 4/3·25 = 33,3 > 25
    assert libre_exigido_mm(19.1, 19.0) == pytest.approx(76.0 / 3.0)          # 4/3·19 = 25,33 > 25


def test_libre_disponible_a_mano():
    ancho = 300 - 2 * (40 + 9.5)
    assert libre_disponible_mm(300, 3, "6", "3") == pytest.approx((ancho - 3 * 19.1) / 2)
    assert libre_disponible_mm(300, 1, "6", "3") == math.inf


def test_holgura_cambia_de_signo_con_tmn_grande():
    assert holgura_libre(VIGA, None) > 0
    assert holgura_libre(VIGA, 80.0) < 0


def test_confinamiento_en_el_limite():
    d = 540.0
    limite = min(d / 4, 8 * 19.1, 24 * 9.5, 300.0)
    assert eficiencia_confinamiento(limite, d, "6", "3") == pytest.approx(1.0)


def test_corte_1d_exacto_y_desperdicio():
    r = corte_1d([6.0, 6.0, 3.0, 3.0], [6.0, 9.0, 12.0])
    assert r.longitud_util_m == 18.0
    assert r.barras_compradas == 3 and r.longitud_comprada_m == 6.0 + 6.0 + 6.0     # 6 | 6 | 3+3
    assert r.desperdicio == pytest.approx(0.0)


def test_corte_1d_pieza_demasiado_larga():
    with pytest.raises(ValueError):
        corte_1d([13.0], [6.0, 9.0, 12.0])


def test_corte_1d_nunca_pierde_material():
    piezas = [5.6, 5.6, 4.1, 3.3, 2.8, 2.8, 1.2]
    r = corte_1d(piezas, [6.0, 9.0, 12.0])
    assert r.longitud_comprada_m >= sum(piezas)


def test_mano_de_obra():
    assert costo_mano_obra(100.0, 40, 1500.0, 200.0) == pytest.approx(158_000.0)
    with pytest.raises(ValueError):
        costo_mano_obra(1.0, 1, -1.0)


def test_areas_coherentes():
    assert AREA_MM2["6"] == pytest.approx(math.pi / 4 * 19.1**2, rel=0.02)
