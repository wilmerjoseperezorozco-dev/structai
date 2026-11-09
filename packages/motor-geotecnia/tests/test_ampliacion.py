"""Ampliación #136: asentamiento inmediato, secundario, multicapa (diferencias finitas) y Monte Carlo."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.consolidacion import asentamiento_primario, grado_consolidacion
from src.inmediato import asentamiento_inmediato_flexible, asentamiento_secundario
from src.montecarlo import simular_asentamiento_primario
from src.multicapa import consolidacion_multicapa


# ── Inmediato (elasticidad) ─────────────────────────────────────────────────────────────────────────────────────────
def test_inmediato_centro_cuadrado_flexible_usa_iw_1_122():
    # Referencia independiente: Iw(centro, cuadrado flexible) = 1,122 (Bowles / Harr), Si = q·B·(1-ν²)/Es·Iw
    s = asentamiento_inmediato_flexible(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, ubicacion="centro")
    assert s == pytest.approx(100.0 * 2.0 * (1 - 0.09) / 10000.0 * 1.1222, rel=2e-3)


def test_inmediato_esquina_es_la_mitad_del_centro():
    c = asentamiento_inmediato_flexible(q_kpa=100.0, B_m=2.0, L_m=3.0, es_kpa=8000.0, nu=0.3, ubicacion="centro")
    e = asentamiento_inmediato_flexible(q_kpa=100.0, B_m=2.0, L_m=3.0, es_kpa=8000.0, nu=0.3, ubicacion="esquina")
    assert e == pytest.approx(c / 2.0, rel=1e-9)


def test_inmediato_lineal_en_q_e_inverso_en_es():
    base = asentamiento_inmediato_flexible(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, ubicacion="centro")
    assert asentamiento_inmediato_flexible(q_kpa=200.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, ubicacion="centro") == pytest.approx(2 * base)
    assert asentamiento_inmediato_flexible(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=20000.0, nu=0.3, ubicacion="centro") == pytest.approx(base / 2)


@pytest.mark.parametrize("kw", [dict(es_kpa=0.0), dict(es_kpa=float("nan")), dict(nu=0.5), dict(nu=-1.0), dict(q_kpa=-1.0),
                                dict(B_m=0.0), dict(L_m=1.0), dict(ubicacion="borde")])
def test_inmediato_rechaza_entradas_invalidas(kw):
    base = dict(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, ubicacion="centro")
    base.update(kw)
    with pytest.raises(ValueError):
        asentamiento_inmediato_flexible(**base)


# ── Secundario ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_secundario_formula_directa():
    s = asentamiento_secundario(c_alfa=0.01, e0=1.0, espesor_m=4.0, t_fin_dias=7300.0, t_primaria_dias=730.0)
    assert s == pytest.approx(0.01 * 4.0 / 2.0 * math.log10(10.0))


def test_secundario_es_cero_si_la_primaria_no_ha_terminado_antes_del_horizonte():
    assert asentamiento_secundario(c_alfa=0.01, e0=1.0, espesor_m=4.0, t_fin_dias=100.0, t_primaria_dias=100.0) == 0.0


def test_secundario_rechaza_horizonte_menor_que_la_primaria():
    with pytest.raises(ValueError, match="horizonte"):
        asentamiento_secundario(c_alfa=0.01, e0=1.0, espesor_m=4.0, t_fin_dias=50.0, t_primaria_dias=100.0)


@pytest.mark.parametrize("kw", [dict(c_alfa=-0.1), dict(e0=0.0), dict(espesor_m=0.0), dict(t_primaria_dias=0.0), dict(c_alfa=float("inf"))])
def test_secundario_rechaza_entradas_invalidas(kw):
    base = dict(c_alfa=0.01, e0=1.0, espesor_m=4.0, t_fin_dias=7300.0, t_primaria_dias=730.0)
    base.update(kw)
    with pytest.raises(ValueError):
        asentamiento_secundario(**base)


# ── Multicapa por diferencias finitas ───────────────────────────────────────────────────────────────────────────────
def _capa(espesor=4.0, cv=0.01, mv=1e-3, delta=100.0):
    return dict(espesor_m=espesor, cv_m2_dia=cv, mv_kpa_inv=mv, delta_sigma_kpa=delta)


def test_multicapa_una_capa_reproduce_terzaghi_doble_drenaje():
    cv, h = 0.01, 4.0
    hdr = h / 2.0
    for tv in (0.05, 0.2, 0.5, 1.0):
        t = tv * hdr ** 2 / cv
        r = consolidacion_multicapa([_capa(h, cv)], tiempos_dias=[t], drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=80)
        assert r["grado"][0] == pytest.approx(grado_consolidacion(tv), abs=1e-3)


def test_multicapa_una_capa_un_drenaje_equivale_a_hdr_igual_al_espesor():
    cv, h, tv = 0.01, 4.0, 0.3
    t = tv * h ** 2 / cv
    r = consolidacion_multicapa([_capa(h, cv)], tiempos_dias=[t], drenaje_superior=True, drenaje_inferior=False, nodos_por_capa=80)
    assert r["grado"][0] == pytest.approx(grado_consolidacion(tv), abs=1e-3)


def test_multicapa_dos_capas_identicas_equivalen_a_una_capa_del_doble_de_espesor():
    t = [50.0, 200.0, 800.0]
    una = consolidacion_multicapa([_capa(8.0)], tiempos_dias=t, drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=120)
    dos = consolidacion_multicapa([_capa(4.0), _capa(4.0)], tiempos_dias=t, drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=60)
    assert np.allclose(una["grado"], dos["grado"], atol=5e-3)


def test_multicapa_asentamiento_final_es_mv_delta_h_y_crece_monotonicamente_con_t():
    capas = [_capa(3.0, 0.02, 2e-3, 80.0), _capa(5.0, 0.005, 1e-3, 50.0)]
    r = consolidacion_multicapa(capas, tiempos_dias=[1.0, 10.0, 100.0, 1000.0, 1e6], drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=60)
    final = 2e-3 * 80.0 * 3.0 + 1e-3 * 50.0 * 5.0
    assert r["asentamiento_final_m"] == pytest.approx(final)
    s = r["asentamiento_m"]
    assert all(b >= a - 1e-12 for a, b in zip(s, s[1:]))
    assert s[-1] == pytest.approx(final, rel=1e-3)


def test_multicapa_capa_poco_permeable_retrasa_la_consolidacion():
    t = [300.0]
    rapida = consolidacion_multicapa([_capa(4.0, 0.02), _capa(4.0, 0.02)], tiempos_dias=t, drenaje_superior=True, drenaje_inferior=False, nodos_por_capa=60)
    lenta = consolidacion_multicapa([_capa(4.0, 0.02), _capa(4.0, 0.0005)], tiempos_dias=t, drenaje_superior=True, drenaje_inferior=False, nodos_por_capa=60)
    assert lenta["grado"][0] < rapida["grado"][0]


def test_multicapa_exige_al_menos_un_borde_drenante():
    with pytest.raises(ValueError, match="drenaje"):
        consolidacion_multicapa([_capa()], tiempos_dias=[10.0], drenaje_superior=False, drenaje_inferior=False, nodos_por_capa=40)


@pytest.mark.parametrize("capa", [dict(espesor_m=0.0), dict(cv_m2_dia=-1.0), dict(mv_kpa_inv=float("nan")), dict(delta_sigma_kpa=-5.0)])
def test_multicapa_rechaza_capas_invalidas(capa):
    c = _capa(); c.update(capa)
    with pytest.raises(ValueError):
        consolidacion_multicapa([c], tiempos_dias=[10.0], drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=40)


def test_multicapa_rechaza_tiempos_no_crecientes_o_negativos():
    with pytest.raises(ValueError, match="tiempos"):
        consolidacion_multicapa([_capa()], tiempos_dias=[10.0, 5.0], drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=40)
    with pytest.raises(ValueError, match="tiempos"):
        consolidacion_multicapa([_capa()], tiempos_dias=[-1.0], drenaje_superior=True, drenaje_inferior=True, nodos_por_capa=40)


# ── Monte Carlo ─────────────────────────────────────────────────────────────────────────────────────────────────────
_ESTRATO = dict(espesor_m=4.0, sigma0_kpa=100.0, delta_kpa=80.0, sigma_p_kpa=100.0, cr=0.03)


def _mc(**kw):
    base = dict(estrato=_ESTRATO, cc_mediana=0.3, cc_cv=0.2, e0_mediana=1.0, e0_cv=0.0, rho_cc_e0=0.0,
                n=20000, semilla=7, limite_m=0.2)
    base.update(kw)
    return simular_asentamiento_primario(**base)


def test_mc_es_reproducible_con_la_misma_semilla_y_distinto_con_otra():
    assert _mc()["p50_m"] == _mc()["p50_m"]
    assert _mc(semilla=8)["p50_m"] != _mc()["p50_m"]


def test_mc_con_cv_cero_es_el_calculo_determinista():
    r = _mc(cc_cv=0.0, e0_cv=0.0, n=100)
    det = asentamiento_primario(cc=0.3, cr=0.03, e0=1.0, espesor_m=4.0, sigma0_kpa=100.0, delta_kpa=80.0, sigma_p_kpa=100.0)
    assert r["p5_m"] == pytest.approx(det) and r["p95_m"] == pytest.approx(det) and r["media_m"] == pytest.approx(det)


def test_mc_mediana_cercana_al_calculo_en_la_mediana_cuando_solo_varia_cc():
    det = asentamiento_primario(cc=0.3, cr=0.03, e0=1.0, espesor_m=4.0, sigma0_kpa=100.0, delta_kpa=80.0, sigma_p_kpa=100.0)
    assert _mc()["p50_m"] == pytest.approx(det, rel=0.02)


def test_mc_percentiles_ordenados_y_probabilidad_en_rango():
    r = _mc()
    assert r["p5_m"] < r["p50_m"] < r["p95_m"]
    assert 0.0 <= r["prob_exceder_limite"] <= 1.0


def test_mc_probabilidad_de_exceder_responde_al_limite():
    r = _mc()
    assert _mc(limite_m=r["p95_m"] * 10)["prob_exceder_limite"] == 0.0
    assert _mc(limite_m=r["p5_m"] / 10)["prob_exceder_limite"] == 1.0
    assert _mc(limite_m=r["p50_m"])["prob_exceder_limite"] == pytest.approx(0.5, abs=0.03)


def test_mc_mayor_incertidumbre_ensancha_el_intervalo():
    a, b = _mc(cc_cv=0.1), _mc(cc_cv=0.4)
    assert (b["p95_m"] - b["p5_m"]) > (a["p95_m"] - a["p5_m"])


def test_mc_correlacion_positiva_cc_e0_reduce_la_dispersion():
    # S ∝ Cc/(1+e0): Cc y e0 positivamente correlacionados se compensan
    sin = _mc(e0_cv=0.15, rho_cc_e0=0.0)
    con = _mc(e0_cv=0.15, rho_cc_e0=0.9)
    assert (con["p95_m"] - con["p5_m"]) < (sin["p95_m"] - sin["p5_m"])


@pytest.mark.parametrize("kw", [dict(n=10), dict(n=10_000_000), dict(cc_cv=-0.1), dict(cc_cv=3.0), dict(rho_cc_e0=1.5),
                                dict(cc_mediana=0.0), dict(limite_m=0.0), dict(semilla=-1)])
def test_mc_rechaza_parametros_invalidos(kw):
    with pytest.raises(ValueError):
        _mc(**kw)
