"""Ubicación de rociadores (#336 F3), casos a mano. Los criterios son NÚMEROS ILUSTRATIVOS redondos, no normativos:
s_max 4,0 m · s_min 2,0 m · muro 0,1–2,0 m · área 12 m² · deflector 0,10 m."""
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import geometria as g  # noqa: E402
from src import rociadores as r  # noqa: E402

C = r.Criterios(4.0, 2.0, 2.0, 0.1, 12.0, 0.10, fuente="ilustrativo (prueba)")


def _pano(lx, ly):
    return r.Pano(0.0, 0.0, lx, ly, 3.0, "T")


def test_pano_cuadrado_5x5_lleva_2x2():
    m, _ = r.malla(_pano(5, 5), C)
    assert (m.nx, m.ny) == (2, 2) and m.sx == pytest.approx(2.5)
    assert sorted(m.puntos)[0] == pytest.approx((1.25, 1.25, 2.9))


def test_area_justo_en_el_limite_se_acepta():
    m, _ = r.malla(_pano(8, 3), C)                     # 2 × 1: S = 4,0 y área 4 × 3 = 12
    assert (m.nx, m.ny) == (2, 1) and m.area_por_rociador_m2 == pytest.approx(12.0)


def test_el_area_maxima_obliga_a_enumerar():
    m, _ = r.malla(_pano(7.5, 3.9), C)                 # 2 × 1 da 14,6 m² > 12; 3 × 1 da 9,75 m²
    assert (m.nx, m.ny) == (3, 1)
    d = r.distribuir([_pano(7.5, 3.9)], C)
    assert d.n == 3 and d.cota_inferior == 3           # ceil(29,25 / 12)


def test_separacion_minima_hace_inviable_el_pano():
    c = r.Criterios(4.0, 2.0, 1.2, 0.1, 12.0, 0.10, fuente="ilustrativo")
    m, motivo = r.malla(_pano(3, 3), c)                # muro ≤ 1,2 exige n ≥ 2, pero S = 1,5 < 2,0
    assert m is None and "separación" in motivo


def test_pano_angosto_no_cumple_la_distancia_minima_a_muro():
    m, _ = r.malla(_pano(0.15, 3), C)
    assert m is None


def test_criterios_sin_fuente_o_incoherentes():
    with pytest.raises(ValueError):
        r.Criterios(4.0, 2.0, 2.0, 0.1, 12.0, 0.1, fuente=" ")
    with pytest.raises(ValueError):
        r.Criterios(2.0, 4.0, 2.0, 0.1, 12.0, 0.1, fuente="x")      # s_min > s_max


def _porticos(luces_x=(5.0,)):
    return SimpleNamespace(luces_x_m=luces_x, luces_y_m=(5.0,), alturas_piso_m=(3.0,), columnas_mm=(400,),
                           vigas_mm=((300, 500),))


def test_panos_entre_vigas_de_un_portico():
    p = _porticos()
    (pn,) = r.panos_entre_vigas(p, 0, 0.12)
    assert (pn.lx, pn.z_techo) == (pytest.approx(4.7), pytest.approx(2.88))
    d = r.distribuir([pn], C)
    assert d.n == 4 and sorted(d.puntos)[0] == pytest.approx((1.325, 1.325, 2.78))
    assert r.verificar(d, C) == []


def test_dos_vanos_respetan_la_separacion_a_traves_de_la_viga():
    p = _porticos((5.0, 5.0))
    d = r.distribuir(r.panos_entre_vigas(p, 0, 0.12), C)
    assert d.n == 8 and r.verificar(d, C) == []        # 3,675 → 6,325: 2,65 m ≥ 2,0


def test_ducto_bajo_un_rociador_queda_para_revision():
    p = _porticos()
    e = g.desde_porticos(p, 0.12)
    e.agregar([g.Caja(1.0, 1.0, 2.2, 1.6, 1.6, 2.6, "ducto", "D1")])
    d = r.distribuir(r.panos_entre_vigas(p, 0, 0.12), C, e)
    assert len(d.observaciones) == 1 and "D1" in d.observaciones[0]


def test_verificar_detecta_una_malla_alterada():
    m, _ = r.malla(_pano(5, 5), C)
    m.puntos[0] = (0.05, 1.25, 2.9)                    # a 0,05 m del borde
    m.puntos[1] = (1.25, 2.6, 2.9)                     # a 1,80 m del punto anterior: < s_min 2,0
    err = r.verificar(r.Distribucion([m], [], 4), C)
    assert any("< mínima" in e and "borde" in e for e in err)
    assert any("separación" in e for e in err)
