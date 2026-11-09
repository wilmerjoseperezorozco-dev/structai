"""Golpe de ariete por el método de las características (MOC), tubería simple: embalse aguas arriba, válvula aguas abajo.
Referencias independientes: Joukowsky (cierre instantáneo, onda cuadrada exacta sin fricción: Wylie y Streeter), fórmula de
Korteweg para la celeridad calculada a mano, consistencia (estado permanente que no cambia si la válvula no se mueve),
monotonicidad con el tiempo de cierre y balance de energía."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.ariete import celeridad_korteweg, simular_ariete

G = 9.80665


def _caso(**kw):
    base = dict(longitud_m=1000.0, diametro_m=0.5, celeridad_ms=1000.0, f_darcy=0.0, caudal_m3s=0.3, carga_embalse_m=100.0,
                t_cierre_s=0.0, t_fin_s=8.0, n_tramos=50)
    base.update(kw)
    return base


def _v0(c):
    return c["caudal_m3s"] / (math.pi * c["diametro_m"] ** 2 / 4)


def test_celeridad_de_korteweg_coincide_con_el_calculo_a_mano():
    d, e, E, K, rho = 0.5, 0.01, 210e9, 2.07e9, 1000.0
    esperado = math.sqrt(K / rho) / math.sqrt(1 + K * d / (E * e))
    assert celeridad_korteweg(d, e, E, K, rho) == pytest.approx(esperado, rel=1e-12)
    assert 1100 < esperado < 1450       # orden de magnitud conocido para acero de pared delgada


def test_cierre_instantaneo_da_joukowsky_exacto_en_la_valvula():
    c = _caso()
    s = simular_ariete(**c)
    dh = c["celeridad_ms"] * _v0(c) / G
    h0 = c["carga_embalse_m"]
    assert s["joukowsky_m"] == pytest.approx(dh, rel=1e-12)
    assert s["valvula"]["h_max_m"] == pytest.approx(h0 + dh, rel=1e-9)
    assert s["valvula"]["h_min_m"] == pytest.approx(h0 - dh, rel=1e-9)


def test_onda_cuadrada_sin_friccion_en_los_instantes_conocidos():
    c = _caso(t_fin_s=8.0)
    s = simular_ariete(**c)
    L, a = c["longitud_m"], c["celeridad_ms"]
    dh, h0 = a * _v0(c) / G, c["carga_embalse_m"]
    t, h = s["tiempos_s"], s["valvula"]["carga_m"]
    for ti, hi in zip(t, h):
        fase = (ti % (4 * L / a))
        if 1e-9 < fase < 2 * L / a - 1e-6:
            assert hi == pytest.approx(h0 + dh, rel=1e-9)
        elif 2 * L / a + 1e-6 < fase < 4 * L / a - 1e-6:
            assert hi == pytest.approx(h0 - dh, rel=1e-9)


def test_estado_permanente_con_friccion_no_cambia_si_la_valvula_no_se_cierra():
    c = _caso(f_darcy=0.02, t_cierre_s=1e9, t_fin_s=10.0)         # cierre «en el infinito»: la apertura sigue en 1
    s = simular_ariete(**c)
    assert s["valvula"]["h_max_m"] - s["valvula"]["h_min_m"] < 1e-6 * c["carga_embalse_m"]
    h_valv = c["carga_embalse_m"] - 0.02 * c["longitud_m"] * c["caudal_m3s"] ** 2 / (2 * G * c["diametro_m"] * (math.pi * c["diametro_m"] ** 2 / 4) ** 2)
    assert s["valvula"]["carga_m"][0] == pytest.approx(h_valv, rel=1e-9)


def test_cierre_lento_amortigua_el_pico_y_es_monotono_con_el_tiempo_de_cierre():
    picos = []
    for tc in (0.0, 1.0, 3.0, 9.0):
        picos.append(simular_ariete(**_caso(t_cierre_s=tc, t_fin_s=20.0))["valvula"]["h_max_m"])
    assert picos[0] >= picos[1] - 1e-9 >= picos[2] - 2e-9 >= picos[3] - 3e-9     # Tc ≤ 2L/a da el mismo pico de Joukowsky (igualdad hasta redondeo)
    assert picos[3] < picos[0] * 0.95


def test_el_pico_con_friccion_no_supera_la_carga_del_embalse_mas_joukowsky():
    # Con fricción el pico puede pasar de H0_válvula + ΔH (al detenerse el flujo, la línea piezométrica sube hacia la carga del embalse),
    # pero la cota física es H_embalse + ΔH (Wylie y Streeter): es lo que se verifica.
    for tc in (0.0, 0.5, 2.0):
        c = _caso(f_darcy=0.015, t_cierre_s=tc)
        s = simular_ariete(**c)
        assert s["valvula"]["h_max_m"] <= c["carga_embalse_m"] + s["joukowsky_m"] + 1e-6


def test_la_friccion_amortigua_la_oscilacion_con_el_tiempo():
    s = simular_ariete(**_caso(f_darcy=0.03, t_fin_s=40.0))
    h = s["valvula"]["carga_m"]
    mitad = len(h) // 2
    amp1 = max(h[:mitad]) - min(h[:mitad])
    amp2 = max(h[mitad:]) - min(h[mitad:])
    assert amp2 < amp1


def test_cavitacion_se_detecta_y_se_declara():
    # Cierre instantáneo con carga de embalse baja: la depresión h0 − ΔH baja de la presión de vapor
    s = simular_ariete(**_caso(carga_embalse_m=30.0))
    assert s["cavitacion"] is True and s["valvula"]["h_min_m"] < s["h_vapor_m"] + 1e-9


def test_sin_cavitacion_con_embalse_alto():
    s = simular_ariete(**_caso(carga_embalse_m=400.0))
    assert s["cavitacion"] is False


def test_clasificacion_cierre_rapido_y_lento():
    L, a = 1000.0, 1000.0                                           # 2L/a = 2 s
    assert simular_ariete(**_caso(t_cierre_s=1.0))["cierre"] == "rápido"
    assert simular_ariete(**_caso(t_cierre_s=5.0, t_fin_s=12.0))["cierre"] == "lento"


@pytest.mark.parametrize("cambio", [dict(longitud_m=0.0), dict(diametro_m=-1.0), dict(celeridad_ms=0.0), dict(f_darcy=-0.01),
                                    dict(caudal_m3s=0.0), dict(carga_embalse_m=float("nan")), dict(t_cierre_s=-1.0), dict(t_fin_s=0.0),
                                    dict(n_tramos=1), dict(n_tramos=100000), dict(t_fin_s=1e9)])
def test_entradas_invalidas_se_rechazan(cambio):
    with pytest.raises(ValueError):
        simular_ariete(**_caso(**cambio))


def test_carga_de_embalse_insuficiente_para_el_caudal_se_rechaza():
    with pytest.raises(ValueError, match="carga"):
        simular_ariete(**_caso(f_darcy=0.05, carga_embalse_m=1.0))
