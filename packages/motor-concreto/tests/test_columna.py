import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.columna import (DemandaColumna, FACTOR_PN_MAX, PHI_COMPRESION, PHI_TRACCION, SeccionColumna, curva, disenar_columna,
                         mn_a, mn_arr, phi_mn_a, phi_mn_arr, momentos_diseno, so_des)
from src.viga import AREA_MM2, DIAMETRO_MM, Materiales, beta1

FC, FY = 28.0, 420.0
M = Materiales(FC, FY, FY)
H = B = 400.0
REC = 40.0


def referencia_escalar(h, b, n_cara, dia, est, c, fc=FC, fy=FY):
    """Compatibilidad de deformaciones con bucles puros (independiente del código vectorizado)."""
    sec = SeccionColumna(h, b, n_cara, dia, est, REC)
    a1 = AREA_MM2[dia]
    ys = [sec.d_borde + k * (h - 2 * sec.d_borde) / (n_cara - 1) for k in range(n_cara)]
    cuenta = [n_cara if k in (0, n_cara - 1) else 2 for k in range(n_cara)]
    a = min(beta1(fc) * c, h)
    P = 0.85 * fc * b * a
    Mx = 0.85 * fc * b * a * (h / 2 - a / 2)
    for y, n in zip(ys, cuenta):
        fs = max(-fy, min(fy, 200000.0 * 0.003 * (c - y) / c))
        f = n * a1 * (fs - (0.85 * fc if y < a else 0.0))
        P += f
        Mx += f * (h / 2 - y)
    return P / 1e3, Mx / 1e6


def test_compresion_pura_coincide_con_calculo_a_mano():
    cv = curva(H, B, 3, "7", "3", REC, FC, FY)
    ast = 8 * AREA_MM2["7"]
    po = (0.85 * FC * (H * B - ast) + FY * ast) / 1e3
    assert cv.po == pytest.approx(po, rel=1e-12)
    assert cv.p_max_phi == pytest.approx(FACTOR_PN_MAX * PHI_COMPRESION * po, rel=1e-12)
    assert cv.p_min == pytest.approx(-FY * ast / 1e3, rel=1e-12)


def test_curva_vectorizada_coincide_con_referencia_escalar_en_muchos_puntos():
    cv = curva(H, B, 4, "8", "3", REC, FC, FY)
    for c in (30.0, 80.0, 150.0, 210.0, 260.0, 400.0, 600.0):
        P, Mx = referencia_escalar(H, B, 4, "8", "3", c)
        assert mn_a(cv, P) == pytest.approx(Mx, rel=0.01, abs=0.5), c


def test_punto_balanceado_con_formula_cerrada():
    """n_cara=2 (4 barras en las esquinas): ambas filas fluyen en el punto balanceado → fórmula cerrada."""
    h = b = 500.0
    cv = curva(h, b, 2, "8", "3", REC, FC, FY)
    sec = SeccionColumna(h, b, 2, "8", "3", REC)
    d, dp = h - sec.d_borde, sec.d_borde
    eps_y = FY / 200000.0
    cb = 0.003 / (0.003 + eps_y) * d
    assert 0.003 * (cb - dp) / cb > eps_y                       # la armadura en compresión también fluye
    a = beta1(FC) * cb
    a_s = 2 * AREA_MM2["8"]
    pb = (0.85 * FC * b * a + a_s * (FY - 0.85 * FC) - a_s * FY) / 1e3
    mb = (0.85 * FC * b * a * (h / 2 - a / 2) + a_s * (FY - 0.85 * FC) * (h / 2 - dp) + a_s * FY * (d - h / 2)) / 1e6
    assert mn_a(cv, pb) == pytest.approx(mb, rel=0.01)


def test_flexion_pura_y_capacidad_decrece_tras_el_punto_balanceado():
    cv = curva(H, B, 3, "7", "3", REC, FC, FY)
    m0 = mn_a(cv, 0.0)
    assert m0 > 0
    pbal = 0.4 * cv.po
    assert mn_a(cv, pbal) > m0                                   # la compresión moderada aumenta Mn
    assert mn_a(cv, 0.9 * cv.po) < mn_a(cv, pbal)               # y cerca de Po cae a cero
    assert mn_a(cv, cv.po) == pytest.approx(0.0, abs=1e-6)


def test_phi_pasa_de_065_a_090_y_phi_mn_no_excede_nominal():
    cv = curva(H, B, 3, "7", "3", REC, FC, FY)
    # en flexión pura la sección controlada por tracción usa φ = 0,90
    assert phi_mn_a(cv, 0.0) == pytest.approx(PHI_TRACCION * mn_a(cv, 0.0), rel=0.02)
    # cerca de la compresión máxima φ = 0,65
    p = 0.95 * cv.p_max_phi
    assert phi_mn_a(cv, p) <= mn_a(cv, p / PHI_COMPRESION) * PHI_COMPRESION * 1.02
    assert np.all(np.diff(cv.Pf) >= 0)


def test_limites_de_carga_axial_devuelven_nan():
    cv = curva(H, B, 3, "7", "3", REC, FC, FY)
    r = phi_mn_arr(cv, np.array([cv.p_max_phi * 1.01, 0.0, cv.Pf[0] * 0.99, cv.Pf[0] * 1.01]))
    assert np.isnan(r[0]) and not np.isnan(r[1]) and not np.isnan(r[2]) and np.isnan(r[3])
    assert np.isnan(mn_arr(cv, np.array([cv.po * 1.01]))[0])


def test_mpr_con_125fy_es_mayor_que_mn_nominal():
    cv = curva(H, B, 3, "7", "3", REC, FC, FY)
    cp = curva(H, B, 3, "7", "3", REC, FC, FY, 1.25, False)
    assert mn_a(cp, 500.0) > mn_a(cv, 500.0) * 1.05


def _dem(P=(600.0,), Mns=((20.0, 20.0),), Ms=((60.0, 60.0),), V=60.0, V_sismo=60.0, delta_s=1.0, k_lu=2.6,
         nudos=None, **kw):
    P = np.array(P)
    return DemandaColumna(P=P, M_ns=np.array(Mns), M_s=np.array(Ms), V=V, V_sismo=V_sismo, delta_s=delta_s, k_lu_max_m=k_lu,
                          lu_min_m=2.6, lu_max_m=2.6, beta_dns=0.7, nudos=nudos if nudos is not None else (), P_sismo=P, **kw)


def test_todos_los_disenos_devueltos_cumplen_y_hay_alguno():
    for nivel in ("DMI", "DMO", "DES"):
        r = disenar_columna(450, 450, _dem(), nivel, M, mnb_int=100.0, mnb_ext=60.0)
        assert r and all(d.cumple for d in r)


def test_geometria_minima_por_nivel():
    assert disenar_columna(280, 280, _dem(), "DES", M) == []
    assert disenar_columna(240, 240, _dem(), "DMO", M) == []
    assert disenar_columna(250, 250, _dem(P=(100,), Mns=((2.0, 2.0),), Ms=((5.0, 5.0),), V=10, V_sismo=10), "DMO", M)


def test_demanda_mayor_que_la_capacidad_maxima_no_tiene_diseno():
    assert disenar_columna(300, 300, _dem(Ms=((900.0, 900.0),)), "DES", M) == []


def test_columna_fuerte_viga_debil_exige_mas_columna_cuando_la_viga_es_mas_fuerte():
    nudos = ((True, np.array([800.0, 500.0]), np.array([600.0, 400.0])), (False, np.array([800.0]), None))
    ratios = []
    for mnb in (50.0, 700.0, 2500.0):
        r = disenar_columna(500, 500, _dem(P=(800.0, 500.0), Mns=((20.0, 20.0),) * 2, Ms=((60.0, 60.0),) * 2, nudos=nudos), "DES", M,
                            mnb_int=mnb, mnb_ext=mnb / 2)
        ratios.append(len(r))
    assert ratios[0] >= ratios[1] >= ratios[2]
    assert ratios[0] > 0 and ratios[2] < ratios[0]


def test_scwb_cumplida_se_verifica_con_calculo_independiente():
    cv = curva(500, 500, 3, "7", "3", REC, FC, FY)
    p_inf, p_sup = 800.0, 600.0
    nudos = ((True, np.array([p_inf]), np.array([p_sup])),)
    mnb = 120.0
    r = disenar_columna(500, 500, _dem(P=(p_inf,), nudos=nudos), "DES", M, mnb_int=mnb, mnb_ext=mnb)
    d = next(x for x in r if (x.n_cara, x.dia, x.estribo) == (3, "7", "3"))
    esperado = (mn_a(cv, p_inf) + mn_a(cv, p_sup)) / (1.2 * mnb)
    v = next(x for x in d.verificaciones if x.norma == "C.21.6.2.2")
    assert v.capacidad == pytest.approx(esperado, rel=1e-9) and v.capacidad >= 1.0


def test_esbeltez_mayor_a_100_se_rechaza_y_la_magnificacion_aumenta_el_momento():
    assert momentos_diseno(300, 300, _dem(k_lu=0.3 * 300 * 101 / 1000), M) is None
    mu_corta, esb_c = momentos_diseno(450, 450, _dem(P=(1200.0,), k_lu=2.0), M)
    mu_esb, esb_e = momentos_diseno(450, 450, _dem(P=(1200.0,), k_lu=4.0), M)
    assert esb_c < 22 < esb_e and mu_esb[0] > mu_corta[0]


def test_delta_s_amplifica_solo_los_momentos_de_sismo():
    a, _ = momentos_diseno(450, 450, _dem(delta_s=1.0), M)
    b, _ = momentos_diseno(450, 450, _dem(delta_s=1.25), M)
    assert a[0] == pytest.approx(80.0) and b[0] == pytest.approx(20.0 + 1.25 * 60.0)


def test_so_des_limites_de_la_ecuacion_c215():
    assert so_des(350.0) == 100.0 and so_des(100.0) == 150.0 and so_des(200.0) == pytest.approx(150.0)
    assert so_des(300.0) == pytest.approx(100.0 + 50.0 / 3.0)


def test_espaciamiento_de_confinamiento_cumple_ash_en_des():
    r = disenar_columna(500, 500, _dem(), "DES", M, mnb_int=80.0, mnb_ext=40.0)
    for d in r:
        assert d.s_conf <= 150.0 and d.s_conf >= 50.0
        assert d.s_fuera <= 150.0 and d.s_fuera >= d.s_conf
        ash = next(v for v in d.verificaciones if v.nombre.startswith("Ash"))
        assert ash.cumple
