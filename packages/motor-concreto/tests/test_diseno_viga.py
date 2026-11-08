import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.diseno_viga import DemandaViga, disenar
from src.viga import AREA_MM2, DIAMETRO_MM, Materiales

M = Materiales(21.0, 420.0, 420.0)
DEM = DemandaViga(luz_libre_m=5.6, M_neg_apoyo=180.0, M_pos_apoyo=90.0, M_pos_vano=100.0,
                  V_max=150.0, V_gravedad=100.0, w_grav=36.0, V_centro=90.0)


def mn(As, b, d, fy):
    a = As * fy / (0.85 * 21.0 * b)
    return As * fy * (d - a / 2) / 1e6


def test_todos_los_diseños_devueltos_cumplen_y_hay_alguno():
    for nivel in ("DMI", "DMO", "DES"):
        r = disenar(300, 600, DEM, nivel, M, columna_c1=400, columna_c2=400)
        assert r and all(x.cumple for x in r)


def test_cortante_por_capacidad_des_coincide_con_calculo_independiente():
    x = disenar(300, 600, DEM, "DES", M)[0]
    d = 600 - 40 - DIAMETRO_MM[x.estribo_dia] - DIAMETRO_MM[x.dia] / 2
    m_sup = mn(x.n_sup * AREA_MM2[x.dia], 300, d, 525.0)
    m_inf = mn(x.n_inf * AREA_MM2[x.dia], 300, d, 525.0)
    ve = (m_sup + m_inf) / 5.6 + 36.0 * 5.6 / 2
    v = next(v for v in x.verificaciones if v.nombre.startswith("Cortante por capacidad"))
    assert v.demanda == pytest.approx(max(ve, 150.0), rel=1e-9)


def test_dmo_usa_mn_y_des_usa_mpr_asi_que_des_pide_mas_cortante():
    des = next(v for v in disenar(300, 600, DEM, "DES", M)[0].verificaciones if v.nombre.startswith("Cortante por capacidad"))
    dmo = next(v for v in disenar(300, 600, DEM, "DMO", M)[0].verificaciones if v.nombre.startswith("Cortante por capacidad"))
    assert des.demanda > dmo.demanda


def test_dmi_no_exige_confinamiento_ni_cuantia_sismica():
    nombres = [v.nombre for v in disenar(300, 600, DEM, "DMI", M)[0].verificaciones]
    assert not any("confinamiento" in n for n in nombres)
    assert not any("0,025" in n for n in nombres)


def test_ancho_minimo_dmo_200():
    assert disenar(190, 600, DEM, "DMO", M) == []
    assert disenar(200, 600, DEM, "DMO", M) != []


def test_ancho_minimo_des_es_el_menor_entre_0_3h_y_250():
    # h=1200 -> min(360; 250) = 250: b=240 no cumple ; h=600 -> min(180; 250) = 180: b=190 pasa la geometria
    assert disenar(240, 1200, DEM, "DES", M) == []
    assert disenar(190, 600, DEM, "DES", M) != []


def test_ancho_maximo_por_la_columna_c_21_5_1_4():
    # c1=c2=250 -> bmax = 250 + 2*min(250; 187,5) = 625
    assert disenar(700, 600, DEM, "DES", M, columna_c1=250, columna_c2=250) == []
    assert disenar(600, 600, DEM, "DES", M, columna_c1=250, columna_c2=250) != []


def test_luz_libre_menor_de_4d_no_admite_diseno_sismico():
    corta = DemandaViga(2.0, 180, 90, 100, 150, 100, 36, 90)
    assert disenar(300, 600, corta, "DES", M) == []
    assert disenar(300, 600, corta, "DMI", M) != []


def test_demanda_imposible_devuelve_vacio_por_cuantia_o_espacio():
    enorme = DemandaViga(5.6, 5000, 2000, 2000, 150, 100, 36, 90)
    assert disenar(300, 600, enorme, "DES", M) == []


def test_relacion_momento_positivo_negativo_se_respeta_en_des_y_dmo():
    for nivel, k in (("DES", 0.5), ("DMO", 1 / 3)):
        for x in disenar(300, 600, DEM, nivel, M):
            d = 600 - 40 - DIAMETRO_MM[x.estribo_dia] - DIAMETRO_MM[x.dia] / 2
            assert mn(x.n_inf * AREA_MM2[x.dia], 300, d, 420.0) >= k * mn(x.n_sup * AREA_MM2[x.dia], 300, d, 420.0) - 1e-9


def test_confinamiento_es_mas_cerrado_que_la_zona_central_en_sismico():
    x = disenar(300, 600, DEM, "DES", M)[0]
    assert x.s_conf <= x.s_centro


def test_nivel_invalido():
    with pytest.raises(ValueError):
        disenar(300, 600, DEM, "DXX", M)
