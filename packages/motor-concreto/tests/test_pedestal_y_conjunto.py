import math

import ezdxf
import pytest

from src import zapata as z
from src.diseno_zapata_pedestal import EXPOSICIONES, optimizar_conjunto
from src.pedestal import disenar_pedestal

A8 = math.pi / 4 * 25.4**2


def test_capacidad_axial_coincide_con_el_calculo_a_mano():
    r = disenar_pedestal(400.0, 900.0, 2025.0, 28.0, 420.0, 600.0)
    assert r.cumple and r.barras == "4#8"
    esperado = 0.65 * 0.75 * (0.85 * 28 * (160000 - 4 * A8) + 420 * 4 * A8) / 1000
    assert r.phi_Pn_max_kN == pytest.approx(esperado, rel=1e-9)
    assert r.phi_Pn_max_kN >= 2025.0
    assert 0.01 <= r.rho <= 0.04


def test_pedestal_esbelto_se_rechaza():
    r = disenar_pedestal(300.0, 3000.0, 500.0, 28.0, 420.0, 600.0)   # 3000/(0.3*300) = 33 > 22
    assert not r.cumple and "esbeltez" in r.motivo_fallo


def test_carga_excesiva_se_rechaza_por_aplastamiento():
    r = disenar_pedestal(300.0, 600.0, 5000.0, 21.0, 420.0, 600.0)
    assert not r.cumple and "aplastamiento" in r.motivo_fallo


def test_pasador_que_no_cabe_en_la_zapata_se_rechaza():
    r = disenar_pedestal(400.0, 900.0, 2025.0, 28.0, 420.0, 350.0)  # 350-75 = 275 mm < ldc
    assert not r.cumple and "no cabe" in r.motivo_fallo


@pytest.fixture(scope="module")
def entorno():
    return z.CargasZapata(P_serv=1500.0, P_u=2025.0), z.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5)


def test_conjunto_altura_del_pedestal_y_costo_aditivo(entorno):
    cargas, suelo = entorno
    d = optimizar_conjunto(400.0, cargas, suelo)
    assert d is not None
    assert d.h_pedestal_mm == pytest.approx(1500.0 - d.zapata.h_c_mm)
    assert d.pedestal.cumple and d.zapata.cumple
    assert d.area_encofrado_m2 == pytest.approx(d.zapata.area_encofrado_m2 + d.pedestal.area_encofrado_m2)


def test_objetivo_co2_nunca_emite_mas_que_el_de_costo(entorno):
    cargas, suelo = entorno
    a = optimizar_conjunto(400.0, cargas, suelo, objetivo="costo")
    b = optimizar_conjunto(400.0, cargas, suelo, objetivo="co2")
    assert b.co2_kg <= a.co2_kg + 1e-6 and a.costo_cop <= b.costo_cop + 1e-6


def test_costa_exige_fc_35_y_sin_ensayo_no_usa_ceniza(entorno, tmp_path):
    cargas, suelo = entorno
    d = optimizar_conjunto(400.0, cargas, suelo, exposicion="costa_C2_S1_sin_ensayo", ruta_dxf=tmp_path / "c.dxf")
    assert d.fc >= EXPOSICIONES["costa_C2_S1_sin_ensayo"]["fc_min"] and d.x_ceniza == 0.0
    doc = ezdxf.readfile(tmp_path / "c.dxf")
    assert any(e.dxf.layer == "PANELES" for e in doc.modelspace())


def test_exposicion_desconocida_falla(entorno):
    with pytest.raises(ValueError):
        optimizar_conjunto(400.0, *entorno, exposicion="marte")
