import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import diseno_portico as dp

BASE = dict(luces_m=(6.0, 6.0), alturas_piso_m=(3.2, 3.0, 3.0), carga_muerta_kn_m=18.0, carga_viva_kn_m=8.0,
            columna_mm=(450.0, 450.0))
FUERZAS = (60.0, 110.0, 150.0)


def informe(**kw):
    return dp.diseno_portico(dp.ProyectoPortico(**BASE, **kw))


@pytest.fixture(scope="module")
def pereira():
    return informe(municipio="Pereira", fuerzas_laterales_kn=FUERZAS)


def test_equilibrio_del_caso_sismico_las_reacciones_igualan_las_fuerzas():
    p = dp.ProyectoPortico(**BASE, capacidad="DES", fuerzas_laterales_kn=FUERZAS)
    modelo, vigas, res, _ = dp._analizar(p, 250.0, 600.0)
    assert sum(r[0] for r in res["E"].reacciones.values()) == pytest.approx(-sum(FUERZAS))


def test_equilibrio_vertical_de_la_carga_muerta():
    p = dp.ProyectoPortico(**BASE, capacidad="DMI")
    modelo, vigas, res, w_pp = dp._analizar(p, 250.0, 600.0)
    esperado = len(p.alturas_piso_m) * sum(p.luces_m) * (18.0 + w_pp)
    assert sum(r[1] for r in res["D"].reacciones.values()) == pytest.approx(esperado)


def test_pereira_aplica_des_y_la_seccion_elegida_cumple_todo(pereira):
    assert pereira.capacidad == "DES" and pereira.sismo["zona_calculada"] == "Alta"
    d = pereira.optimo.diseno
    assert d.cumple and d.nivel == "DES"
    assert pereira.optimo.b >= min(0.3 * pereira.optimo.h, 250.0)
    assert d.s_conf <= d.s_centro


def test_el_sismo_cuesta_mas_que_solo_gravedad():
    grav = informe(capacidad="DES")
    sism = informe(capacidad="DES", fuerzas_laterales_kn=FUERZAS)
    assert sism.optimo.costo_directo >= grav.optimo.costo_directo
    assert sism.optimo.demanda.M_neg_apoyo > grav.optimo.demanda.M_neg_apoyo or sism.optimo.h != grav.optimo.h


def test_mas_exigencia_sismica_nunca_abarata():
    dmi, dmo, des = (informe(capacidad=c, fuerzas_laterales_kn=FUERZAS).optimo.costo_directo for c in ("DMI", "DMO", "DES"))
    assert dmi <= dmo <= des


def test_mas_fuerza_sismica_no_baja_el_costo():
    suave = informe(capacidad="DES", fuerzas_laterales_kn=(20.0, 35.0, 50.0)).optimo.costo_directo
    fuerte = informe(capacidad="DES", fuerzas_laterales_kn=(90.0, 165.0, 225.0)).optimo.costo_directo
    assert fuerte >= suave


def test_la_envolvente_tiene_momento_positivo_y_negativo_en_el_apoyo_con_sismo(pereira):
    e = pereira.envolvente_gobernante
    assert min(e["M_min"]) < 0 < max(e["M_max"])
    assert len(e["x"]) == len(e["M_max"]) == len(e["combo_V"])


def test_capacidad_obligatoria_sin_municipio():
    with pytest.raises(ValueError, match="municipio"):
        informe()


def test_no_se_permite_bajar_la_capacidad():
    with pytest.raises(ValueError, match="no se permite bajarla"):
        informe(municipio="Pereira", capacidad="DMO", fuerzas_laterales_kn=FUERZAS)


def test_fuerzas_con_longitud_incorrecta():
    with pytest.raises(ValueError, match="un valor por nivel"):
        informe(capacidad="DES", fuerzas_laterales_kn=(10.0, 20.0))


def test_columnas_muy_angostas_limitan_el_ancho_de_la_viga_c_21_5_1_4():
    # c1=c2=200 -> bmax = 200 + 2*min(200; 150) = 500 ; con 550 mm no se admite
    i = dp.diseno_portico(dp.ProyectoPortico(**{**BASE, "columna_mm": (200.0, 200.0)}, capacidad="DES", fuerzas_laterales_kn=FUERZAS))
    assert all(c.b <= 500.0 for c in i.ranking)


def test_resumen_menciona_capacidad_y_demanda(pereira):
    t = dp.resumen(pereira)
    assert "DES" in t and "Demanda de diseño" in t
