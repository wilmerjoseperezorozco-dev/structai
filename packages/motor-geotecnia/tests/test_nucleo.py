"""Núcleo geotécnico: esfuerzos, consolidación y capacidad portante contra soluciones cerradas / integración independiente."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from scipy import integrate

from contrato_motor.propiedades import verificar_homogeneidad, verificar_monotonia
from src.consolidacion import asentamiento_primario, factor_tiempo, grado_consolidacion, tiempo_para_grado
from src.esfuerzos import (esfuerzo_2a1, esfuerzo_boussinesq_centro_rect, esfuerzo_boussinesq_esquina_rect,
                           esfuerzo_efectivo_vertical)
from src.portante import capacidad_portante_general, factores_capacidad


# ── Esfuerzos ────────────────────────────────────────────────────────────────
def _boussinesq_numerico(q, B, L, z):
    """Integra la carga puntual de Boussinesq (3Q z^3 / 2 pi R^5) sobre el rectángulo, esquina en el origen."""
    f = lambda y, x: 3 * q * z ** 3 / (2 * math.pi * (x * x + y * y + z * z) ** 2.5)
    return integrate.dblquad(f, 0, B, 0, L, epsabs=1e-10, epsrel=1e-10)[0]


@pytest.mark.parametrize("B,L,z", [(2.0, 3.0, 1.5), (4.0, 4.0, 4.0), (1.0, 8.0, 2.0)])
def test_boussinesq_esquina_coincide_con_la_integral_numerica(B, L, z):
    assert esfuerzo_boussinesq_esquina_rect(100.0, B, L, z) == pytest.approx(_boussinesq_numerico(100.0, B, L, z), rel=1e-7)


def test_boussinesq_esquina_valor_tabulado_m_n_igual_a_1():
    # Factor de influencia de Newmark para m = n = 1: 0,1752 (valor tabulado clásico)
    assert esfuerzo_boussinesq_esquina_rect(1.0, 3.0, 3.0, 3.0) == pytest.approx(0.1752, abs=5e-4)


def test_boussinesq_centro_es_cuatro_esquinas_de_la_mitad():
    assert esfuerzo_boussinesq_centro_rect(80.0, 4.0, 6.0, 3.0) == pytest.approx(4 * esfuerzo_boussinesq_esquina_rect(80.0, 2.0, 3.0, 3.0))


def test_boussinesq_tiende_a_q_cerca_de_la_superficie_bajo_el_centro():
    assert esfuerzo_boussinesq_centro_rect(100.0, 50.0, 50.0, 0.01) == pytest.approx(100.0, rel=1e-3)


def test_metodo_2_a_1_solucion_cerrada():
    # delta = q*B*L / ((B+z)(L+z))
    assert esfuerzo_2a1(150.0, 2.0, 3.0, 2.0) == pytest.approx(150.0 * 2 * 3 / (4 * 5))


def test_esfuerzo_efectivo_con_nivel_freatico():
    # 2 m secos (g=17) y 3 m saturados (gsat=19); z = 5 m, NF a 2 m: sigma'v = 17*2 + (19-9,81)*3
    estratos = [(2.0, 17.0, 17.0), (10.0, 19.0, 19.0)]
    assert esfuerzo_efectivo_vertical(estratos, 5.0, 2.0) == pytest.approx(17 * 2 + (19 - 9.81) * 3)


def test_esfuerzo_efectivo_sin_agua_es_el_total():
    assert esfuerzo_efectivo_vertical([(10.0, 18.0, 20.0)], 4.0, None) == pytest.approx(72.0)


# ── Consolidación ────────────────────────────────────────────────────────────
BASE_C = dict(cc=0.3, cr=0.03, e0=1.0, espesor_m=4.0, sigma0_kpa=100.0, delta_kpa=50.0, sigma_p_kpa=100.0)


def test_asentamiento_normalmente_consolidado_formula_cerrada():
    assert asentamiento_primario(**BASE_C) == pytest.approx(0.3 * 4.0 / 2.0 * math.log10(1.5))


def test_asentamiento_sobreconsolidado_dentro_del_rango_usa_cr():
    s = asentamiento_primario(**{**BASE_C, "sigma_p_kpa": 200.0})
    assert s == pytest.approx(0.03 * 4.0 / 2.0 * math.log10(1.5))


def test_asentamiento_sobreconsolidado_que_cruza_la_preconsolidacion():
    s = asentamiento_primario(**{**BASE_C, "delta_kpa": 150.0, "sigma_p_kpa": 200.0})
    assert s == pytest.approx(4.0 / 2.0 * (0.03 * math.log10(2.0) + 0.3 * math.log10(250.0 / 200.0)))


def test_asentamiento_sin_incremento_es_cero():
    assert asentamiento_primario(**{**BASE_C, "delta_kpa": 0.0}) == 0.0


def test_asentamiento_monotono_en_carga_e_indice_de_compresion():
    f = lambda d: asentamiento_primario(**{**BASE_C, "delta_kpa": d, "sigma_p_kpa": 150.0})
    verificar_monotonia(f, [0, 10, 40, 80, 160, 320])
    g = lambda cc: asentamiento_primario(**{**BASE_C, "cc": cc, "delta_kpa": 80.0})
    verificar_monotonia(g, [0.1, 0.2, 0.3, 0.5], estricta=True)


def test_asentamiento_es_homogeneo_de_grado_1_en_el_espesor_y_0_en_los_esfuerzos():
    verificar_homogeneidad(lambda **k: asentamiento_primario(**k), BASE_C, "espesor_m", 1.0)
    escalado = {**BASE_C, "sigma0_kpa": 300.0, "delta_kpa": 150.0, "sigma_p_kpa": 300.0}
    assert asentamiento_primario(**escalado) == pytest.approx(asentamiento_primario(**BASE_C))


@pytest.mark.parametrize("malo", [dict(e0=0.0), dict(cc=-0.1), dict(espesor_m=0.0), dict(sigma0_kpa=0.0), dict(delta_kpa=-1.0)])
def test_consolidacion_rechaza_datos_fuera_de_dominio(malo):
    with pytest.raises(ValueError, match="Terzaghi|NSR-10"):
        asentamiento_primario(**{**BASE_C, **malo})


def test_preconsolidacion_menor_que_el_esfuerzo_inicial_es_rechazada():
    with pytest.raises(ValueError, match="preconsolidaci"):
        asentamiento_primario(**{**BASE_C, "sigma_p_kpa": 50.0})


# ── Tiempo de consolidación (Terzaghi) ───────────────────────────────────────
def test_grado_de_consolidacion_valores_clasicos():
    assert grado_consolidacion(0.197) == pytest.approx(0.50, abs=2e-3)
    assert grado_consolidacion(0.848) == pytest.approx(0.90, abs=2e-3)
    assert grado_consolidacion(0.0) == 0.0


def test_grado_cerca_de_cero_sigue_la_raiz_de_tv():
    tv = 1e-3
    assert grado_consolidacion(tv) == pytest.approx(math.sqrt(4 * tv / math.pi), rel=1e-6)


def test_tiempo_para_grado_90_por_ciento_y_su_inversa():
    tv = factor_tiempo(cv_m2_dia=0.002, t_dias=100.0, hdr_m=2.0)
    assert tv == pytest.approx(0.002 * 100.0 / 4.0)
    t90 = tiempo_para_grado(0.90, cv_m2_dia=0.002, hdr_m=2.0)
    assert t90 == pytest.approx(0.848 * 4.0 / 0.002, rel=2e-3)
    assert grado_consolidacion(factor_tiempo(0.002, t90, 2.0)) == pytest.approx(0.90, abs=1e-8)


def test_grado_monotono_creciente_en_el_tiempo():
    verificar_monotonia(grado_consolidacion, [0.0, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0])


def test_tiempo_escala_con_el_cuadrado_de_la_trayectoria_de_drenaje():
    verificar_homogeneidad(lambda **k: tiempo_para_grado(**k), dict(grado=0.5, cv_m2_dia=0.002, hdr_m=2.0), "hdr_m", 2.0, rel=1e-9)


def test_grado_fuera_de_0_1_es_rechazado():
    with pytest.raises(ValueError, match="Terzaghi"):
        tiempo_para_grado(1.0, cv_m2_dia=0.002, hdr_m=2.0)


# ── Capacidad portante (Vesić) ───────────────────────────────────────────────
BASE_P = dict(c_kpa=10.0, phi_deg=25.0, gamma_kn_m3=18.0, B_m=2.0, L_m=2.0, Df_m=1.0, nivel_freatico_m=None)


def test_factores_de_capacidad_phi_30_tabulados():
    assert factores_capacidad(30.0) == pytest.approx((30.14, 18.40, 22.40), abs=0.01)


def test_factor_nc_para_phi_cero_es_pi_mas_2():
    nc, nq, ng = factores_capacidad(0.0)
    assert nc == pytest.approx(math.pi + 2) and nq == pytest.approx(1.0) and ng == pytest.approx(0.0)


def test_factores_crecen_con_phi():
    for i in range(3):
        verificar_monotonia(lambda p, i=i: factores_capacidad(p)[i], [0, 10, 20, 30, 40])


def test_zapata_corrida_en_arcilla_saturada_solucion_cerrada():
    # phi = 0, c = 50 kPa, Df = 0: q_ult = c*Nc = 5,14*50 (corrida, sin factores de forma ni profundidad)
    r = capacidad_portante_general(c_kpa=50.0, phi_deg=0.0, gamma_kn_m3=18.0, B_m=2.0, L_m=None, Df_m=0.0, nivel_freatico_m=None)
    assert r["q_ult_kpa"] == pytest.approx(50.0 * (math.pi + 2), rel=1e-9)


def test_zapata_corrida_en_arena_vesic():
    # c = 0, phi = 30, g = 18, B = 2, Df = 1,5 (corrida): q_ult = q*Nq*dq + 0,5*g*B*Ng, dq = 1+2 tan(phi)(1-sin(phi))^2 (Df/B)
    nc, nq, ng = factores_capacidad(30.0)
    t, s = math.tan(math.radians(30)), math.sin(math.radians(30))
    dq = 1 + 2 * t * (1 - s) ** 2 * (1.5 / 2.0)
    esperado = 18 * 1.5 * nq * dq + 0.5 * 18 * 2.0 * ng
    r = capacidad_portante_general(c_kpa=0.0, phi_deg=30.0, gamma_kn_m3=18.0, B_m=2.0, L_m=None, Df_m=1.5, nivel_freatico_m=None)
    assert r["q_ult_kpa"] == pytest.approx(esperado, rel=1e-9)


def test_el_nivel_freatico_superficial_reduce_la_capacidad():
    base = {**BASE_P, "c_kpa": 0.0, "phi_deg": 30.0, "gamma_sat_kn_m3": 20.0}
    seco = capacidad_portante_general(**base)
    humedo = capacidad_portante_general(**{**base, "nivel_freatico_m": 0.0})
    assert humedo["q_ult_kpa"] < seco["q_ult_kpa"]


def test_cuadrada_rinde_mas_que_la_corrida_en_arcilla():
    arc = {**BASE_P, "c_kpa": 50.0, "phi_deg": 0.0}
    corrida = capacidad_portante_general(**{**arc, "L_m": None})
    cuadrada = capacidad_portante_general(**arc)
    assert cuadrada["q_ult_kpa"] > corrida["q_ult_kpa"]


def test_capacidad_monotona_en_cohesion_phi_ancho_y_desplante():
    for var, vals in (("c_kpa", [0, 10, 30, 60]), ("phi_deg", [0, 10, 20, 30, 40]), ("Df_m", [0.0, 0.5, 1.0, 2.0])):
        verificar_monotonia(lambda v, var=var: capacidad_portante_general(**{**BASE_P, var: v})["q_ult_kpa"], vals)
    # Con el ancho se verifica la carga última TOTAL (q_ult·B·L), zapata cuadrada para no violar L ≥ B. La presión q_ult puede
    # bajar al crecer B porque el factor de profundidad depende de Df/B (comportamiento conocido de Hansen/Vesić): ver la
    # prueba siguiente, que lo deja registrado como limitación y no como propiedad.
    verificar_monotonia(lambda b: capacidad_portante_general(**{**BASE_P, "B_m": b, "L_m": b})["q_ult_kpa"] * b * b, [1.0, 2.0, 3.0, 4.0], estricta=True)


def test_la_presion_ultima_puede_bajar_al_ensanchar_la_zapata_por_el_factor_de_profundidad():
    """Limitación documentada (supuestos del contrato): q_ult(B=2) < q_ult(B=1) con c=10, phi=25, Df=1 por d = f(Df/B)."""
    q1 = capacidad_portante_general(**{**BASE_P, "B_m": 1.0, "L_m": 1.0})["q_ult_kpa"]
    q2 = capacidad_portante_general(**{**BASE_P, "B_m": 2.0, "L_m": 2.0})["q_ult_kpa"]
    assert q2 < q1


def test_homogeneidad_de_grado_1_al_escalar_c_y_gamma():
    a = capacidad_portante_general(**BASE_P)["q_ult_kpa"]
    b = capacidad_portante_general(**{**BASE_P, "c_kpa": 30.0, "gamma_kn_m3": 54.0})["q_ult_kpa"]
    assert b == pytest.approx(3 * a, rel=1e-9)


@pytest.mark.parametrize("malo", [dict(phi_deg=50.0), dict(phi_deg=-1.0), dict(B_m=0.0), dict(c_kpa=-1.0), dict(Df_m=-0.1)])
def test_capacidad_rechaza_datos_fuera_de_dominio(malo):
    with pytest.raises(ValueError, match="NSR-10|Vesi"):
        capacidad_portante_general(**{**BASE_P, **malo})


# ── Revisión adversaria (2026-11-09): validación de borde y ramas sin cubrir ──────────────────────────────────────────
NAN, INF = float("nan"), float("inf")


def test_peso_saturado_menor_que_el_del_agua_o_que_el_seco_es_rechazado():
    for gsat in (5.0, 17.0):
        with pytest.raises(ValueError, match="saturado"):
            capacidad_portante_general(**{**BASE_P, "nivel_freatico_m": 0.5, "gamma_sat_kn_m3": gsat})


def test_la_capacidad_crece_con_la_profundidad_del_nivel_freatico_y_se_satura_en_df_mas_b():
    base = {**BASE_P, "c_kpa": 0.0, "phi_deg": 30.0, "gamma_kn_m3": 17.0, "gamma_sat_kn_m3": 20.0}
    verificar_monotonia(lambda n: capacidad_portante_general(**{**base, "nivel_freatico_m": n})["q_ult_kpa"], [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
    seco = capacidad_portante_general(**{**base, "nivel_freatico_m": None})["q_ult_kpa"]
    assert capacidad_portante_general(**{**base, "nivel_freatico_m": 5.0})["q_ult_kpa"] == pytest.approx(seco)  # agua a >= Df+B no influye


def test_el_factor_de_profundidad_tiene_un_salto_en_df_igual_a_b_documentado():
    """Limitación de la formulación de Hansen/Vesić (k = Df/B hasta 1, atan(Df/B) después): q_ult cae al cruzar Df = B."""
    base = {**BASE_P, "c_kpa": 0.0, "phi_deg": 30.0, "B_m": 2.0, "L_m": 2.0}
    justo_antes = capacidad_portante_general(**{**base, "Df_m": 2.0})["q_ult_kpa"]
    justo_despues = capacidad_portante_general(**{**base, "Df_m": 2.0001})["q_ult_kpa"]
    assert justo_despues < justo_antes
    verificar_monotonia(lambda d: capacidad_portante_general(**{**base, "Df_m": d})["q_ult_kpa"], [2.5, 3.0, 4.0, 6.0])  # estable pasado el salto


@pytest.mark.parametrize("malo", [dict(c_kpa=NAN), dict(phi_deg=NAN), dict(gamma_kn_m3=INF), dict(B_m=NAN), dict(Df_m=NAN), dict(L_m=NAN)])
def test_capacidad_rechaza_no_finitos(malo):
    with pytest.raises(ValueError, match="NSR-10|Vesi"):
        capacidad_portante_general(**{**BASE_P, **malo})


def test_capacidad_nula_se_rechaza_en_vez_de_devolver_cero():
    with pytest.raises(ValueError, match="nula|capacidad"):
        capacidad_portante_general(**{**BASE_P, "c_kpa": 0.0, "phi_deg": 0.0, "Df_m": 0.0})


@pytest.mark.parametrize("args", [
    dict(estratos=[(2.0, 17.0, 19.0)], z_m=NAN, nivel_freatico_m=None),
    dict(estratos=[(2.0, 17.0, 5.0)], z_m=1.0, nivel_freatico_m=0.0),
    dict(estratos=[(2.0, 17.0, 19.0)], z_m=1.0, nivel_freatico_m=-1.0),
    dict(estratos=[(2.0, NAN, 19.0)], z_m=1.0, nivel_freatico_m=None),
])
def test_esfuerzo_efectivo_rechaza_datos_invalidos(args):
    with pytest.raises(ValueError, match="NSR-10|Boussinesq"):
        esfuerzo_efectivo_vertical(args["estratos"], args["z_m"], args["nivel_freatico_m"])


@pytest.mark.parametrize("q,z", [(-5.0, 2.0), (NAN, 2.0), (100.0, NAN), (INF, 2.0)])
def test_2a1_valida_igual_que_boussinesq(q, z):
    with pytest.raises(ValueError, match="NSR-10|Boussinesq"):
        esfuerzo_2a1(q, 2.0, 3.0, z)


def test_tiempo_para_grado_diminuto_converge_con_la_raiz_de_tv():
    t = tiempo_para_grado(1e-6, cv_m2_dia=0.002, hdr_m=2.0)
    assert t == pytest.approx(math.pi / 4 * (1e-6) ** 2 * 4.0 / 0.002, rel=1e-6)
