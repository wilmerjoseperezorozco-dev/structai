"""Verificaciones del Título H de la NSR-10 (#136), cotejadas con la impresa (págs. H-17 a H-19).

Tabla H.4.7-1 (FS 3,0 / 2,5 / 1,5), H.4.8.4 (total = inmediato + consolidación + secundario), H.4.9.2 (30 / 15 cm a
20 años), Tabla H.4.9-1 (ℓ/1000, ℓ/500, ℓ/300, ℓ/160), H.4.9.4 (giro ≤ ℓ/250) y H.4.10 (excentricidad). Los valores
esperados se calculan a mano o con fórmulas reescritas aquí, no con las funciones del motor.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.contrato_api import (
    DIVISOR_DIFERENCIAL, FS_MINIMO, HORIZONTE_DIAS, LIMITES_ASENT_TOTAL_MM, Apoyo, CapaMulticapa, EstratoTotal,
    SolicitudAsentamientoTotal, SolicitudDiferencial, SolicitudMonteCarlo, SolicitudMulticapa, SolicitudPortante,
    SolicitudPortanteExcentrica, asentamiento_total_contrato, diferencial_contrato, montecarlo_contrato,
    multicapa_contrato, portante_contrato, portante_excentrica_contrato,
)
from src.portante import capacidad_portante_excentrica_inclinada, capacidad_portante_general


# ── Valores de la norma impresa ─────────────────────────────────────────────────────────────────────────────────────
def test_constantes_transcritas_de_la_nsr10_impresa():
    assert FS_MINIMO == {"muerta_viva_normal": 3.0, "muerta_viva_maxima": 2.5, "muerta_viva_normal_sismo": 1.5}
    assert LIMITES_ASENT_TOTAL_MM == {"aislada": 300.0, "medianera": 150.0}
    assert DIVISOR_DIFERENCIAL == {"muros_acabados_susceptibles": 1000.0, "muros_de_carga": 500.0,
                                   "porticos_concreto": 300.0, "estructura_metalica": 160.0}
    assert HORIZONTE_DIAS == pytest.approx(7305.0)


# ── Capacidad portante con excentricidad e inclinación ──────────────────────────────────────────────────────────────
SUELO = dict(c_kpa=0.0, phi_deg=30.0, gamma_kn_m3=18.0, Df_m=1.0, nivel_freatico_m=None)


def test_sin_excentricidad_ni_horizontal_coincide_con_la_centrada():
    g = capacidad_portante_general(B_m=2.0, L_m=3.0, **SUELO)
    e = capacidad_portante_excentrica_inclinada(B_m=2.0, L_m=3.0, V_kn=500.0, H_kn=0.0, eB_m=0.0, eL_m=0.0, **SUELO)
    assert e["q_ult_kpa"] == pytest.approx(g["q_ult_kpa"], rel=1e-12)
    assert e["Q_ult_kn"] == pytest.approx(g["q_ult_kpa"] * 6.0, rel=1e-12)
    assert (e["ic"], e["iq"], e["ig"]) == (1.0, 1.0, 1.0)


def test_corrida_excentrica_reescrita_a_mano():
    """φ = 30°, c = 0, B = 2 m, e = 0,3 m → B' = 1,4 m; forma = 1; dq con Df/B real."""
    r = capacidad_portante_excentrica_inclinada(B_m=2.0, L_m=None, V_kn=300.0, H_kn=0.0, eB_m=0.3, eL_m=0.0, **SUELO)
    t = math.tan(math.radians(30))
    nq = math.exp(math.pi * t) * math.tan(math.radians(60)) ** 2          # 18,401
    ng = 2 * (nq + 1) * t                                                 # 22,402
    dq = 1 + 2 * t * (1 - math.sin(math.radians(30))) ** 2 * (1.0 / 2.0)
    q_ult = 18.0 * 1.0 * nq * dq + 0.5 * 18.0 * 1.4 * ng
    assert nq == pytest.approx(18.401, abs=1e-3) and ng == pytest.approx(22.402, abs=1e-3)
    assert r["B_ef_m"] == pytest.approx(1.4) and r["q_ult_kpa"] == pytest.approx(q_ult, rel=1e-12)
    assert r["Q_ult_kn"] == pytest.approx(q_ult * 1.4, rel=1e-12)


def test_inclinacion_vesic_phi_cero_a_mano():
    """φ = 0, corrida (m = 2): ic = 1 − m·H/(A'·c·Nc) = 1 − 2·30/(2·50·5,1416) = 0,88331."""
    r = capacidad_portante_excentrica_inclinada(c_kpa=50.0, phi_deg=0.0, gamma_kn_m3=18.0, B_m=2.0, L_m=None,
                                                Df_m=1.0, nivel_freatico_m=None, V_kn=300.0, H_kn=30.0,
                                                eB_m=0.0, eL_m=0.0)
    assert r["m"] == pytest.approx(2.0)
    assert r["ic"] == pytest.approx(1 - 2 * 30 / (2 * 50 * (math.pi + 2)), rel=1e-12)
    assert r["ic"] == pytest.approx(0.88331, abs=1e-5)


def test_inclinacion_vesic_suelo_granular_cuadrada_a_mano():
    """c = 0, cuadrada: m = (2+1)/(1+1) = 1,5; H/V = 0,1 → iq = 0,9^1,5 = 0,85381, iγ = 0,9^2,5 = 0,76843."""
    r = capacidad_portante_excentrica_inclinada(B_m=2.0, L_m=2.0, V_kn=1000.0, H_kn=100.0, eB_m=0.0, eL_m=0.0, **SUELO)
    assert r["m"] == pytest.approx(1.5)
    assert r["iq"] == pytest.approx(0.85381, abs=1e-5) and r["ig"] == pytest.approx(0.76843, abs=1e-5)
    t = math.tan(math.radians(30))
    assert r["ic"] == pytest.approx(r["iq"] - (1 - r["iq"]) / (r["Nc"] * t), rel=1e-12)


def test_m_usa_la_dimension_paralela_a_h_aunque_se_intercambien_b_y_l_efectivos():
    """B = 2, L = 2,2, eL = 0,5 → L' = 1,2 < B' = 2: B' y L' se intercambian; H sigue paralela a B (2 m)."""
    r = capacidad_portante_excentrica_inclinada(B_m=2.0, L_m=2.2, V_kn=800.0, H_kn=50.0, eB_m=0.0, eL_m=0.5, **SUELO)
    assert r["B_ef_m"] == pytest.approx(1.2) and r["L_ef_m"] == pytest.approx(2.0)
    razon = 2.0 / 1.2
    assert r["m"] == pytest.approx((2 + razon) / (1 + razon), rel=1e-12)


def test_excentricidad_y_horizontal_reducen_la_carga_ultima():
    Q = lambda **kw: capacidad_portante_excentrica_inclinada(B_m=2.0, L_m=3.0, V_kn=800.0, **{**dict(H_kn=0.0, eB_m=0.0, eL_m=0.0), **kw}, **SUELO)["Q_ult_kn"]
    assert Q() > Q(eB_m=0.2) > Q(eB_m=0.5) > Q(eB_m=0.8)
    assert Q() > Q(H_kn=50.0) > Q(H_kn=150.0)
    assert Q() > Q(eL_m=0.4)


@pytest.mark.parametrize("kw,msg", [(dict(eB_m=1.0), "fuera de la base"), (dict(H_kn=900.0), "carga horizontal"),
                                    (dict(H_kn=-1.0), "negativa"), (dict(eB_m=float("nan")), "finito")])
def test_excentrica_rechaza_casos_fuera_de_dominio(kw, msg):
    base = dict(B_m=2.0, L_m=3.0, V_kn=800.0, H_kn=0.0, eB_m=0.0, eL_m=0.0)
    with pytest.raises(ValueError, match=msg):
        capacidad_portante_excentrica_inclinada(**{**base, **kw}, **SUELO)


def _sol_exc(**kw):
    base = dict(c_kpa=10.0, phi_deg=30.0, gamma_kn_m3=18.0, B_m=2.0, L_m=3.0, Df_m=1.0, nivel_freatico_m=None,
                V_kn=900.0, H_kn=60.0, eB_m=0.2, eL_m=0.0, factor_seguridad=3.0, condicion_carga="muerta_viva_normal")
    return SolicitudPortanteExcentrica(**{**base, **kw})


def test_contrato_excentrico_aplica_fs_y_tabla_h471():
    r = portante_excentrica_contrato(_sol_exc())
    assert r.valor["Q_adm_kn"] == pytest.approx(r.valor["Q_ult_kn"] / 3.0)
    assert r.valor["utilizacion"] == pytest.approx(900.0 / r.valor["Q_adm_kn"])
    assert r.valor["fs_minimo_tabla"] == 3.0 and "H.4.10" in r.referencia_normativa
    with pytest.raises(ValueError, match="Tabla H.4.7-1"):
        portante_excentrica_contrato(_sol_exc(factor_seguridad=2.4, condicion_carga="muerta_viva_maxima"))
    assert portante_excentrica_contrato(_sol_exc(factor_seguridad=1.5, condicion_carga="muerta_viva_normal_sismo")).valor["cumple"] in (True, False)


def test_resultante_fuera_del_nucleo_central_advierte_y_marca_borde():
    r = portante_excentrica_contrato(_sol_exc(eB_m=0.5))            # 0,5 > B/6 = 0,333
    assert r.en_borde_dominio is True and any("núcleo central" in a for a in r.advertencias)


def test_portante_centrada_con_condicion_de_carga_verifica_la_tabla():
    base = dict(c_kpa=10.0, phi_deg=30.0, gamma_kn_m3=18.0, B_m=2.0, L_m=2.0, Df_m=1.0, nivel_freatico_m=None,
                q_aplicada_kpa=150.0)
    with pytest.raises(ValueError, match="Tabla H.4.7-1"):
        portante_contrato(SolicitudPortante(**base, factor_seguridad=2.0, condicion_carga="muerta_viva_normal"))
    ok = portante_contrato(SolicitudPortante(**base, factor_seguridad=2.0, condicion_carga="muerta_viva_normal_sismo"))
    assert any("≥ 1.5" in x for x in ok.supuestos) and ok.advertencias == []
    sin = portante_contrato(SolicitudPortante(**base, factor_seguridad=2.0))           # compatibilidad: sin condición
    assert any("no se contrasta" in x for x in sin.supuestos) and any("< 3,0" in a for a in sin.advertencias)


# ── Asentamiento total a 20 años ────────────────────────────────────────────────────────────────────────────────────
def _estrato(**kw):
    base = dict(espesor_m=4.0, z_medio_m=3.0, sigma0_kpa=60.0, sigma_p_kpa=60.0, cc=0.3, cr=0.05, e0=1.0,
                cv_m2_dia=0.05, hdr_m=2.0, c_alfa=0.01)
    return EstratoTotal(**{**base, **kw})


def _total(**kw):
    base = dict(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, estratos=[_estrato()], metodo="2a1",
                tipo_cimentacion="aislada")
    return SolicitudAsentamientoTotal(**{**base, **kw})


def test_total_suma_inmediato_primario_y_secundario_a_mano():
    """cv alto: U(20 años) ≈ 1. Si = q·B·(1−ν²)/Es·1,1222; Sc NC con Δσ 2:1; Ss = Cα·H/(1+e0)·log10(t20/tp)."""
    r = asentamiento_total_contrato(_total())
    v = r.valor
    si = 100 * 2 * (1 - 0.09) / 10000 * 1.1222 * 1e3
    delta = 100 * 2 * 2 / (5 * 5)
    sc = 4 / 2 * 0.3 * math.log10((60 + delta) / 60) * 1e3
    tp = v["estratos"][0]["tp95_dias"]
    ss = 0.01 * 4 / 2 * math.log10(7305 / tp) * 1e3
    assert v["inmediato_mm"] == pytest.approx(si, rel=2e-3)
    assert v["estratos"][0]["grado_20_anios"] == pytest.approx(1.0, abs=1e-9)
    assert v["primario_20_anios_mm"] == pytest.approx(sc, rel=1e-9)
    assert v["secundario_20_anios_mm"] == pytest.approx(ss, rel=1e-9)
    assert v["asentamiento_total_20_anios_mm"] == pytest.approx(v["inmediato_mm"] + sc + ss, rel=1e-12)
    # tp95 = Tv95·Hdr²/cv con Tv95 = 1,129 (Terzaghi)
    assert tp == pytest.approx(1.129 * 4 / 0.05, rel=2e-3)


def test_arcilla_lenta_solo_cuenta_lo_consolidado_a_20_anios_y_advierte_el_ultimo():
    r = asentamiento_total_contrato(_total(q_kpa=250.0, tipo_cimentacion="medianera",
                                           estratos=[_estrato(cv_m2_dia=0.0002, espesor_m=10.0, z_medio_m=5.5,
                                                              hdr_m=5.0, cc=0.6)]))
    v = r.valor
    assert 0 < v["estratos"][0]["grado_20_anios"] < 0.5
    assert v["secundario_20_anios_mm"] == 0.0                     # tp95 > 20 años
    assert v["asentamiento_total_ultimo_mm"] > v["asentamiento_total_20_anios_mm"]
    if v["asentamiento_total_ultimo_mm"] > 150 >= v["asentamiento_total_20_anios_mm"]:
        assert any("último" in a for a in r.advertencias)


def test_total_contra_el_limite_de_h492_y_sin_calpha_queda_declarado():
    r = asentamiento_total_contrato(_total(estratos=[_estrato(c_alfa=None)]))
    assert r.valor["secundario_20_anios_mm"] == 0.0 and any("Sin Cα" in x for x in r.supuestos)
    malo = asentamiento_total_contrato(_total(q_kpa=400.0, es_kpa=2000.0, tipo_cimentacion="medianera"))
    assert malo.valor["cumple_asentamiento_total"] is (malo.valor["asentamiento_total_20_anios_mm"] <= 150.0)
    with pytest.raises(ValueError, match="L ≥ B"):
        asentamiento_total_contrato(_total(B_m=3.0, L_m=2.0))


def test_total_crece_con_la_carga_y_baja_con_el_modulo():
    t = lambda **kw: asentamiento_total_contrato(_total(**kw)).valor["asentamiento_total_20_anios_mm"]
    assert t(q_kpa=50.0) < t() < t(q_kpa=200.0)
    assert t(es_kpa=20000.0) < t() < t(es_kpa=5000.0)


# ── Diferencial y giro ──────────────────────────────────────────────────────────────────────────────────────────────
def _dif(asent, tipo="porticos_concreto", xs=(0.0, 6.0, 12.0)):
    return diferencial_contrato(SolicitudDiferencial(apoyos=[Apoyo(x_m=x, asentamiento_mm=s) for x, s in zip(xs, asent)],
                                                     tipo_construccion=tipo))


def test_diferencial_y_giro_a_mano():
    """ℓ = 6 m, pórticos: Δmax = 6000/300 = 20 mm. Giro: pendiente de mínimos cuadrados = 30 000/72·10⁶ = 4,1667·10⁻⁴."""
    r = _dif([20.0, 35.0, 25.0])
    t1, t2 = r.valor["tramos"]
    assert t1["limite_mm"] == pytest.approx(20.0) and t1["diferencial_mm"] == pytest.approx(15.0) and t1["cumple"]
    assert t2["diferencial_mm"] == pytest.approx(10.0)
    assert r.valor["giro"] == pytest.approx(30000 / 72e6, rel=1e-9)
    assert r.valor["utilizacion_giro"] == pytest.approx(250 * 30000 / 72e6, rel=1e-9)
    assert r.valor["cumple"] is True and r.valor["asentamiento_maximo_mm"] == 35.0


@pytest.mark.parametrize("tipo,divisor", list(DIVISOR_DIFERENCIAL.items()))
def test_cada_tipo_de_la_tabla_h491(tipo, divisor):
    lim = 6000.0 / divisor
    assert _dif([0.0, lim * 0.99, 0.0], tipo).valor["cumple_diferencial"] is True
    assert _dif([0.0, lim * 1.01, 0.0], tipo).valor["cumple_diferencial"] is False


def test_giro_de_cuerpo_rigido_se_limita_a_l_250_aunque_no_haya_distorsion():
    """Edificio inclinado sin distorsión (S lineal en x): el diferencial por tramo de metálica (ℓ/160) pasa y el giro no."""
    r = _dif([0.0, 30.0, 60.0], "estructura_metalica")      # pendiente 30/6000 = 1/200 > 1/250
    assert r.valor["cumple_diferencial"] is True and r.valor["cumple_giro"] is False and r.valor["cumple"] is False


def test_diferencial_rechaza_apoyos_en_la_misma_posicion():
    with pytest.raises(ValueError, match="Tabla H.4.9-1"):
        _dif([10.0, 20.0], xs=(3.0, 3.0))


# ── Multicapa y Monte Carlo expuestos ───────────────────────────────────────────────────────────────────────────────
def test_multicapa_una_capa_reproduce_terzaghi():
    """Doble drenaje, H = 4 m (Hdr = 2), cv = 0,01 m²/día; Tv = 0,2 → U = 0,504 (tabla de Terzaghi)."""
    t = 0.2 * 4 / 0.01
    r = multicapa_contrato(SolicitudMulticapa(capas=[CapaMulticapa(espesor_m=4.0, cv_m2_dia=0.01, mv_kpa_inv=1e-3,
                                                                     delta_sigma_kpa=100.0)],
                                              tiempos_dias=[t], drenaje_superior=True, drenaje_inferior=True,
                                              nodos_por_capa=80))
    assert r.valor["grado"][0] == pytest.approx(0.504, abs=3e-3)
    assert r.valor["asentamiento_final_mm"] == pytest.approx(1e-3 * 100 * 4 * 1e3)


def test_montecarlo_sin_variabilidad_da_el_determinista_y_es_reproducible():
    base = dict(espesor_m=4.0, sigma0_kpa=60.0, delta_kpa=40.0, sigma_p_kpa=60.0, cr=0.05, cc_mediana=0.3, cc_cv=0.0,
                e0_mediana=1.0, e0_cv=0.0, rho_cc_e0=0.0, n=500, semilla=7, tipo_cimentacion="aislada")
    r = montecarlo_contrato(SolicitudMonteCarlo(**base))
    det = 4 / 2 * 0.3 * math.log10(100 / 60) * 1e3
    assert r.valor["p5_mm"] == pytest.approx(det) and r.valor["p95_mm"] == pytest.approx(det)
    a = montecarlo_contrato(SolicitudMonteCarlo(**{**base, "cc_cv": 0.3, "e0_cv": 0.1})).valor
    b = montecarlo_contrato(SolicitudMonteCarlo(**{**base, "cc_cv": 0.3, "e0_cv": 0.1})).valor
    assert a == b and a["p5_mm"] < a["p50_mm"] < a["p95_mm"]
