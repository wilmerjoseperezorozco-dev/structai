import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import zapata as z
from src.viga import Materiales

M = Materiales(21.0, 420.0, 420.0)
SUELO = z.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5)
CAR = z.CargasZapata(P_serv=800.0, P_u=1150.0)


def test_presion_concentrica_a_mano():
    qmax, qmin = z.presiones_servicio(CAR, SUELO, 2.2, 2.2, 0.5)
    esperado = 800 / 4.84 + 24 * 0.5 + 17 * 1.0
    assert qmax == pytest.approx(esperado) and qmin == pytest.approx(esperado)


def test_presion_con_momento_trapecio():
    c = z.CargasZapata(P_serv=800.0, P_u=1150.0, My_serv=100.0)
    qmax, qmin = z.presiones_servicio(c, z.Suelo(200.0, 1.0), 2.0, 2.0, 0.5)
    p = 800 / 4.0
    assert qmax - qmin == pytest.approx(2 * 6 * 100 / (2.0 * 2.0**2))
    assert (qmax + qmin) / 2 == pytest.approx(p + 24 * 0.5 + 17 * 0.5)


def test_flexion_a_mano_en_la_cara():
    # Mu = p·B·((L-c)/2)²/2 con presión uniforme
    p = 1150 / (2.2 * 2.2)
    esperado = p * 2.2 * ((2.2 - 0.4) / 2) ** 2 / 2
    assert z._momento_cara(p, 0.0, 2.2, 2.2, 0.4) == pytest.approx(esperado, rel=1e-6)


def test_as_flexion_cumple_equilibrio():
    As = z._as_flexion(150.0, 2200.0, 400.0, 21.0, 420.0)
    a = As * 420 / (0.85 * 21 * 2200)
    Mn = 0.9 * As * 420 * (400 - a / 2) / 1e6
    assert Mn == pytest.approx(150.0, rel=1e-9)
    assert math.isinf(z._as_flexion(1e5, 300.0, 200.0, 21.0, 420.0))


def test_rho_minimo_ntc():
    assert z._rho_min(420) == 0.0018 and z._rho_min(280) == 0.0020
    assert z._rho_min(500) == pytest.approx(0.0018 * 420 / 500) and z._rho_min(1000) == 0.0014


def test_disenar_devuelve_solo_zapatas_que_cumplen():
    r = z.disenar(400, 400, CAR, SUELO, M)
    assert r and all(d.cumple and d.q_max_serv <= SUELO.q_adm_kpa for d in r)
    assert all(d.d >= 150 for d in r)
    vols = [d.volumen_concreto_m3 + d.masa_acero_kg / 7850 for d in r]
    assert vols == sorted(vols)


def test_punzonamiento_recalculado_a_mano():
    d = z.verificar(2.2, 2.2, 500.0, 400, 400, CAR, SUELO, M)
    dp = (500 - 75 - 10 + 500 - 75 - 10 - 19.1) / 2
    bo = 4 * (400 + dp)
    vc = min(0.17 * 3, 0.083 * (40 * dp / bo + 2), 0.33) * math.sqrt(21)
    Vc = 0.75 * vc * bo * dp / 1000
    Vu = 1150 - 1150 / 4.84 * ((400 + dp) / 1000) ** 2
    v = next(x for x in d.verificaciones if x.norma == "C.11.11.2.1")
    assert v.capacidad == pytest.approx(Vc, rel=1e-9) and v.demanda == pytest.approx(Vu, rel=1e-9)


def test_mas_carga_no_baja_el_volumen():
    a = z.disenar(400, 400, CAR, SUELO, M)[0]
    b = z.disenar(400, 400, z.CargasZapata(1600.0, 2300.0), SUELO, M)[0]
    assert b.volumen_concreto_m3 >= a.volumen_concreto_m3


def test_suelo_peor_agranda_la_zapata():
    a = z.disenar(400, 400, CAR, z.Suelo(300.0), M)[0]
    b = z.disenar(400, 400, CAR, z.Suelo(150.0), M)[0]
    assert b.Lx * b.Ly > a.Lx * a.Ly


def test_columna_circular_equivale_a_cuadrado_de_igual_area():
    assert z._lado_equivalente(500, 0, True)[0] == pytest.approx(math.sqrt(math.pi * 250**2))


def test_momento_alto_hace_fallar_por_despegue():
    c = z.CargasZapata(P_serv=800.0, P_u=1150.0, My_serv=900.0)
    d = z.verificar(2.2, 2.2, 600.0, 400, 400, c, SUELO, M)
    assert not d.cumple and any(v.norma == "H.4 (contacto)" and not v.cumple for v in d.verificaciones)


def test_asentamientos_limites_h49():
    ok = z.comprobar_asentamientos(25.0, 10.0, 6.0)
    assert all(v.cumple for v in ok)
    mal = z.comprobar_asentamientos(25.0, 25.0, 6.0)      # ℓ/300 = 20 mm
    assert not next(v for v in mal if v.norma == "H.4.9.3").cumple
    assert z.comprobar_asentamientos(160.0, 0, 6, tipo="medianera")[0].cumple is False


def test_fs_menor_a_3_se_rechaza_y_q_adm():
    assert z.q_adm_desde_q_ult(600.0) == 200.0
    with pytest.raises(ValueError):
        z.q_adm_desde_q_ult(600.0, 2.0)


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        z.disenar(400, 400, z.CargasZapata(0.0, 100.0), SUELO, M)
    with pytest.raises(ValueError):
        z.disenar(400, 400, CAR, z.Suelo(0.0), M)
    with pytest.raises(ValueError):
        z.comprobar_asentamientos(1, 1, 6, tipo="x")


def test_exceso_de_aplastamiento_se_reporta_para_dovelas():
    d = z.verificar(3.2, 3.2, 800.0, 400, 400, z.CargasZapata(1600.0, 2300.0), SUELO, M)
    assert any("exceso" in a and "dovelas" in a.lower() for a in d.advertencias)
    assert d.cumple
