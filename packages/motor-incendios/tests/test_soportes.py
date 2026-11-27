"""Soportes y anclajes (#336 F8), casos a mano. Los números de NSR-10 vienen de A.9, B.2.4 y C-D. Los criterios de
separación, masas y resistencias de anclaje son ILUSTRATIVOS. Sismo: Aa = 0,25, Fa = 1,15, I = 1,0, Sa = 2,5·Aa·Fa,
hn = 30 m (heq = 22,5 m)."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import hidraulica as h  # noqa: E402
from src import soportes as sp  # noqa: E402

S = sp.Sismo(0.25, 1.15, 1.0, 2.5 * 0.25 * 1.15, 30.0, "alta", "III", "DMO")
T4 = h.Tuberia("4in", 0.1023, 120)
CR = sp.CriteriosSoporte(12.0, 24.0, 3.6, 0.065, 45.0, {"4in": 16.1, "1in": 2.5}, fuente="ilustrativo")
CAP = sp.CapacidadAnclaje(10.0, 8.0, 6.0, 9.0, "factor_04", fuente="ilustrativo")


def test_aceleracion_en_el_soporte_a9_4_2():
    assert S.a_s == pytest.approx(0.2875) and S.heq == pytest.approx(22.5)
    assert sp.ax(S, 15.0) == pytest.approx(0.575)                           # 0,2875 + 0,43125 · 15/22,5
    assert sp.ax(S, 30.0) == pytest.approx(0.71875 * 30 / 22.5)
    assert sp.ax(S, 0.0) == pytest.approx(0.25) and sp.ax(S, -4.0) == pytest.approx(0.25)   # A.9.4.8


def test_fp_y_su_minimo():
    assert sp.coef_fp(S, 15.0, 2.5, 6.0) == pytest.approx(0.575 * 2.5 / 6)          # 0,2396
    assert sp.coef_fp(S, 15.0, 2.5, 1.5) == pytest.approx(0.575 * 2.5 / 1.5)
    assert sp.coef_fp(S, 0.0, 2.5, 6.0) == pytest.approx(0.125)                     # gobierna Aa·I/2


def test_grado_y_tipo_de_anclaje():
    assert sp.grado(S) == "superior"                                                 # grupo III
    assert sp.clasificar_anclaje("expansion") == "no_ductil"
    assert sp.clasificar_anclaje("quimico", 10) == "ductil" and sp.clasificar_anclaje("quimico", 6) == "no_ductil"
    rp, obs = sp.rp_admisible(S, "tuberia_incendio", "no_ductil")
    assert rp is None and "ductil" in obs                                            # superior exige dúctil
    s2 = sp.Sismo(0.25, 1.15, 1.0, 0.72, 30.0, "alta", "II", "DMO")
    assert sp.rp_admisible(s2, "tuberia_incendio", "no_ductil")[0] == 1.5
    with pytest.raises(ValueError):
        sp.grado(S, "bueno")                                                         # menor que el mínimo


def test_exencion_a913():
    assert sp.exento(sp.Sismo(0.05, 1.0, 1.0, 0.125, 9.0, "baja", "II", "DMI"))
    assert not sp.exento(sp.Sismo(0.05, 1.0, 1.0, 0.125, 9.0, "baja", "III", "DMI"))


def test_resistencia_de_anclaje_cd33():
    assert sp.resistencia_diseno(CAP, S) == (pytest.approx(2.4), pytest.approx(2.4))   # 0,4·min(10, 0,75·8)
    with pytest.raises(ValueError, match="C-D.3.3.4"):
        sp.resistencia_diseno(sp.CapacidadAnclaje(10, 8, 6, 9, "acero_ductil", "x"), S)
    ok = sp.CapacidadAnclaje(5.0, 8.0, 4.0, 9.0, "acero_ductil", "x")               # el acero gobierna
    assert sp.resistencia_diseno(ok, S) == (5.0, 4.0)
    dmi = sp.Sismo(0.1, 1.2, 1.0, 0.3, 9.0, "intermedia", "III", "DMI")
    assert sp.resistencia_diseno(CAP, dmi) == (8.0, 6.0)                             # sin C-D.3.3


def test_interaccion_cd7():
    assert sp.interaccion(1.0, 0.1, 2.0, 2.0) == (True, 0.5)                         # V ≤ 0,2φVn
    assert sp.interaccion(1.0, 1.0, 2.0, 2.0) == (True, pytest.approx(1.0 / 1.2))
    assert sp.interaccion(1.5, 1.5, 2.0, 2.0)[0] is False                            # 1,5 > 1,2


def test_riostras_y_colgadores_de_un_tramo():
    tr = [((0, 0, 15.0), (12, 0, 15.0))]
    (s1,) = sp.arriostrar(tr, {frozenset(tr[0]): T4}, S, CR, "ductil", CAP, CAP)
    w = (16.1 + 1000 * math.pi * 0.1023 ** 2 / 4) * 9.81 / 1000                    # 0,2386 kN/m
    assert s1.w_kn_m == pytest.approx(w) and s1.coef == pytest.approx(0.2396, abs=1e-4)
    assert (s1.n_lateral, s1.n_longitudinal, s1.n_colgadores) == (1, 1, 4)
    assert s1.h_lateral_kn == pytest.approx(0.2396 * w * 12, abs=1e-3)             # 0,686 kN
    assert s1.anclaje_riostra[0] == pytest.approx(s1.anclaje_riostra[1])           # 45°: N = V
    assert s1.t_colgador_kn == pytest.approx(1.2 * w * 3 + w * 3 / 3)              # B.2.4-5 gobierna sobre 1,4D
    ok_r, ir, ok_c, ic = s1.verificacion
    assert ok_r and ir == pytest.approx(2 * 0.686 / 2.4 / 1.2, abs=1e-3) and ok_c


def test_tubo_delgado_solo_colgadores_y_anclaje_no_ductil_rechazado():
    tr = [((0, 0, 15.0), (6, 0, 15.0))]
    t1 = h.Tuberia("1in", 0.0266, 120)
    (s1,) = sp.arriostrar(tr, {frozenset(tr[0]): t1}, S, CR, "ductil", CAP, CAP)
    assert s1.n_lateral == 0 and "solo colgadores" in s1.observaciones[0]
    with pytest.raises(ValueError, match="no admisible"):
        sp.arriostrar(tr, {frozenset(tr[0]): t1}, S, CR, "no_ductil", CAP, CAP)


def test_exento_conserva_los_colgadores_por_gravedad():
    s0 = sp.Sismo(0.05, 1.0, 1.0, 0.125, 9.0, "baja", "II", "DMI")
    tr = [((0, 0, 3.0), (12, 0, 3.0))]
    (s1,) = sp.arriostrar(tr, {frozenset(tr[0]): T4}, s0, CR, "expansion", CAP, CAP)
    assert (s1.n_lateral, s1.n_colgadores) == (0, 4) and "A.9.1.3" in s1.observaciones[0]
    assert s1.t_colgador_kn == pytest.approx(1.4 * s1.w_kn_m * 3)


def test_anclaje_de_bomba_en_sotano():
    a = sp.anclar_equipo(10.0, 0.5, 0.6, 2, -4.0, S, "ductil", CAP)
    assert a.fp_kn == pytest.approx(1.25)                                           # Aa·I/2 gobierna (ap = 1, Rp = 6)
    assert a.tension_por_anclaje_kn == 0.0 and a.cortante_por_anclaje_kn == pytest.approx(0.3125)
    b = sp.anclar_equipo(2.0, 2.0, 0.6, 2, -4.0, S, "ductil", CAP)                  # alto y liviano: vuelca
    assert b.tension_por_anclaje_kn == pytest.approx((0.25 * 2.0 / 0.6 - (1.8 - 2 / 3) / 2) / 2)
