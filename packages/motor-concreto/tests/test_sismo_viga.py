import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.sismo_viga import DemandaSismica, momento_probable, verificar_sismico
from src.viga import Cargas, Materiales, Seccion

M = Materiales(21.0, 420.0, 420.0)
CARGAS = Cargas(18.0, 10.0, 6.0)


def sec(**kw):
    base = dict(b=250, h=700, barras_n=3, barras_dia="6", estribo_dia="3", estribo_s=150, barras_sup_n=3)
    base.update(kw)
    return Seccion(**base)


def por_nombre(vs, prefijo):
    return next(v for v in vs if v.nombre.startswith(prefijo))


def test_momento_probable_a_mano():
    s = sec()
    As = 3 * math.pi / 4 * 19.1**2
    fy = 525.0
    a = As * fy / (0.85 * 21 * 250)
    assert momento_probable(s, M) == pytest.approx(As * fy * (s.d - a / 2) / 1e6)


def test_cortante_por_capacidad_a_mano():
    vs = verificar_sismico(sec(), M, CARGAS, DemandaSismica(5.6))
    v = por_nombre(vs, "Cortante por capacidad")
    # Mpr = 266.4 kN.m ; 2*Mpr/ln = 95.1 ; wu_grav=1.2*(18+4.2)+10=36.64 -> 102.6 ; Ve=197.7
    assert v.demanda == pytest.approx(197.74, abs=0.1)
    assert v.cumple


def test_vc_se_conserva_si_el_cortante_sismico_es_menos_de_la_mitad_de_ve():
    # 95,1 kN sismico < 0,5 * 197,7 = 98,9 kN -> C.21.5.4.2 no permite Vc = 0
    v = por_nombre(verificar_sismico(sec(), M, CARGAS, DemandaSismica(5.6)), "Cortante por capacidad")
    s = sec()
    vc = 0.17 * math.sqrt(21) * s.b * s.d / 1000
    vs_kn = s.Av * 420 * s.d / 150 / 1000
    assert v.capacidad == pytest.approx(0.75 * (vc + vs_kn), rel=1e-6)


def test_vc_se_anula_si_el_cortante_sismico_es_la_mitad_o_mas_de_ve():
    # sin cargas de servicio: 95,1 kN sismico >= 0,5 * Ve -> Vc = 0 (C.21.5.4.2)
    v = por_nombre(verificar_sismico(sec(), M, Cargas(0.0, 0.0, 6.0), DemandaSismica(5.6)), "Cortante por capacidad")
    s = sec()
    vs_kn = s.Av * 420 * s.d / 150 / 1000
    assert v.capacidad == pytest.approx(0.75 * vs_kn, rel=1e-6)


def test_ancho_menor_de_250_con_h_grande_falla():
    # mín(0,3h; 250) = 250 si h >= 833 ; con b=200 y h=700 -> 0,3h=210 > 200 falla
    v = por_nombre(verificar_sismico(sec(b=200), M, CARGAS, DemandaSismica(5.6)), "Ancho b")
    assert not v.cumple


def test_luz_libre_menor_de_4d_falla():
    v = por_nombre(verificar_sismico(sec(), M, CARGAS, DemandaSismica(2.0)), "Luz libre")
    assert not v.cumple


def test_estribos_muy_separados_fallan_confinamiento():
    v = por_nombre(verificar_sismico(sec(estribo_s=250), M, CARGAS, DemandaSismica(5.6)), "Separación de confinamiento")
    assert not v.cumple


def test_sin_barras_superiores_incumple_continuidad():
    v = por_nombre(verificar_sismico(sec(barras_sup_n=0), M, CARGAS, DemandaSismica(5.6)), "≥ 2 barras")
    assert not v.cumple


def test_momento_de_apoyo_del_analisis_se_verifica_solo_si_se_entrega():
    sin = verificar_sismico(sec(), M, CARGAS, DemandaSismica(5.6))
    con = verificar_sismico(sec(), M, CARGAS, DemandaSismica(5.6, momento_apoyo_kn_m=400.0))
    assert not any(v.nombre.startswith("Flexión en el apoyo") for v in sin)
    assert not por_nombre(con, "Flexión en el apoyo").cumple
