"""Cuarto de bombas (#336 F7), casos a mano. Bombas, criterios, holguras y geometría son ILUSTRATIVOS, no normativos ni de
fabricante. Succión: tubo de 4" (d = 102,3 mm, C = 120, 8 m equivalentes), agua a 20 °C."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import bombas as b  # noqa: E402
from src import hidraulica as h  # noqa: E402

EF = ((200, 0.40), (1000, 0.70), (1500, 0.65))
NP = ((0, 2.0), (1000, 3.0), (1500, 5.0))
B1 = b.Bomba("B1", 1000, 500, ((0, 600), (1000, 500), (1500, 340)), NP, EF, 1.8, 0.8, 50e6)
B2 = b.Bomba("B2", 1000, 700, ((0, 840), (1000, 700), (1500, 470)), NP, EF, 1.9, 0.8, 60e6)
B3 = b.Bomba("B3", 750, 550, ((0, 650), (750, 550), (1125, 380)), NP, EF, 1.6, 0.7, 40e6)
JK = b.Bomba("J", 40, 720, ((0, 800), (40, 720), (80, 600)), ((0, 1.0), (80, 1.5)), ((10, 0.3), (80, 0.5)), 1.0, 0.5, 5e6)
C = b.CriteriosBomba((b.CriterioCurva(0.0, None, 1.4), b.CriterioCurva(1.5, 0.65, None)), (0.5, 1.5), (1.0, 1.5), 1.0,
                     (7.5, 11, 15, 18.5, 22, 30), 1.15, 40.0, 70.0, fuente="ilustrativo")
TUB = h.Tuberia("4in", 0.1023, 120)
HOLG = b.Holguras(0.9, 1.0, 1.2, 0.6, fuente="ilustrativo")


def _succ(altitud=2600.0, z_eje=-3.5, admite=False):
    return b.Succion(altitud, 20.0, -3.0, z_eje, TUB, 8.0, admite, fuente="ilustrativo")


def test_atmosfera_y_presion_de_vapor():
    assert b.presion_atmosferica_kpa(0) == pytest.approx(101.325)
    assert b.presion_atmosferica_kpa(2600) == pytest.approx(73.749, abs=1e-3)
    assert b.presion_vapor_kpa(20) == pytest.approx(2.3296, abs=1e-3)
    assert b.presion_vapor_kpa(100) == pytest.approx(101.33, abs=0.05)      # hierve a 1 atm: comprobación de Antoine


def test_npsh_con_succion_positiva_a_2600_m():
    s = _succ()                                                             # agua 0,5 m sobre el eje
    assert b.npsh_disponible_m(s, 1000) == pytest.approx(7.3731, abs=1e-3)
    assert b.npsh_disponible_m(s, 1500) == pytest.approx(6.9175, abs=1e-3)


def test_seleccion_de_la_principal_y_motor():
    cb = b.disenar(1100, 450, [B3, B2, B1], _succ(), C, JK, HOLG)
    assert cb.principal.bomba == "B1"                                       # la más barata que cumple
    assert cb.principal.dp_en_diseno_kpa == pytest.approx(468.0)            # 500 − 160·100/500
    assert cb.principal.p_eje_max_kw == pytest.approx(13.077, abs=1e-3)     # 1500 L/min · 340 kPa / 0,65
    assert cb.principal.motor_kw == 18.5                                    # 13,08 · 1,15 = 15,04 → 18,5
    b3 = next(v for v in cb.candidatas if v.bomba == "B3")
    assert not b3.cumple and any("no entrega" in m for m in b3.motivos)    # 391 kPa < 450


def test_criterios_de_curva():
    v = b.verificar_bomba(b.Bomba("X", 1000, 500, ((0, 750), (1000, 500), (1500, 300)), NP, EF, 1, 1, 1), 1000, 450,
                          _succ(), C)
    assert any("> 1.4" in m for m in v.motivos) and any("< 0.65" in m for m in v.motivos)   # 1,5 y 0,60


def test_tanque_subterraneo_con_succion_negativa():
    s = _succ(z_eje=0.0)                                                     # agua 3 m bajo el eje
    with pytest.raises(ValueError, match="succión negativa"):
        b.disenar(1100, 450, [B1], s, C, JK, HOLG)
    v = b.verificar_bomba(B1, 1100, 450, _succ(z_eje=0.0, admite=True), C)
    assert v.npsha_m[1.5] == pytest.approx(3.4175, abs=1e-3) and not v.cumple   # 3,42 < 5,0 + 1,0


def test_la_altitud_decide_el_npsh():
    # La misma succión negativa sí alcanza a nivel del mar: (101,325 − 2,33)/9,81 − 3 − 0,863 = 6,23 ≥ 6,0.
    v = b.verificar_bomba(B1, 1100, 450, _succ(altitud=0.0, z_eje=0.0, admite=True), C)
    assert v.npsha_m[1.5] == pytest.approx(6.228, abs=1e-3) and v.cumple


def test_jockey_y_cuarto():
    cb = b.disenar(1100, 450, [B1], _succ(), C, JK, HOLG)
    assert cb.p_jockey_kpa == pytest.approx(670.0)                          # cierre 600 + 70
    assert (cb.largo_m, cb.ancho_m) == (pytest.approx(7.8), pytest.approx(2.8))
    assert cb.area_m2 == pytest.approx(21.84)
    jk_debil = b.Bomba("J2", 40, 600, ((0, 650), (40, 620), (80, 500)), JK.npshr_m, JK.eficiencia, 1, 0.5, 1)
    with pytest.raises(ValueError, match="jockey"):
        b.disenar(1100, 450, [B1], _succ(), C, jk_debil, HOLG)


def test_tanque_por_volumen_de_f6():
    t = b.dimensionar_tanque(1100 * 60 / 1000, b.GeometriaTanque(2.5, 0.3, 0.3, 2.0, fuente="ilustrativo"))
    assert t.volumen_util_m3 == pytest.approx(66.0)
    assert (t.ancho_m, t.largo_m, t.altura_total_m) == (pytest.approx(3.633, abs=1e-3), pytest.approx(7.266, abs=1e-3),
                                                         pytest.approx(3.1))
    assert t.largo_m * t.ancho_m * t.altura_util_m == pytest.approx(66.0)


def test_curvas_invalidas_y_criterios_sin_fuente():
    with pytest.raises(ValueError):
        b.Bomba("Z", 1, 1, ((100, 5), (0, 6)), NP, EF, 1, 1, 1)
    with pytest.raises(ValueError):
        b.CriteriosBomba((), (0.5, 1.5), (1.0,), 1.0, (10,), 1.15, 40, 70, fuente="")
