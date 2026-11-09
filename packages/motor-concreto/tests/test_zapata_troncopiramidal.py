import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import zapata as z
from src import zapata_troncopiramidal as t
from src.viga import Materiales

M = Materiales(21.0, 420.0, 420.0)
CARGAS = z.CargasZapata(P_serv=800.0, P_u=1100.0)
SUELO = z.Suelo(q_adm_kpa=200.0)


def test_volumen_del_tronco_se_reduce_al_prisma_cuando_no_hay_taludes():
    assert t.volumen_m3(2200, 400, 450, 450) == pytest.approx(2.2 * 2.2 * 0.45)


def test_volumen_del_tronco_es_el_de_la_formula_del_tronco_de_piramide():
    # L=2 m, c=0,4 m, H=0,3 m sobre un prisma de 0,3 m: 4·0,3 + 0,3/3·(4+0,16+0,8)
    assert t.volumen_m3(2000, 400, 600, 300) == pytest.approx(4 * 0.3 + 0.1 * (4 + 0.16 + 0.8))


def test_encofrado_sin_talud_es_perimetro_por_espesor():
    assert t.area_encofrado_m2(2000, 400, 450, 450) == pytest.approx(4 * 2.0 * 0.45)


@pytest.mark.parametrize("L,h", [(2200, 450), (2000, 350), (2400, 500), (1800, 300)])
def test_con_espesor_constante_coincide_con_la_zapata_prismatica(L, h):
    base = z.verificar(L / 1000, L / 1000, float(h), 400.0, 400.0, CARGAS, SUELO, M)
    var = t.verificar(float(L), float(h), float(h), 400.0, CARGAS, SUELO, M)
    assert var.cumple == base.cumple
    if base.cumple:
        assert var.volumen_m3 == pytest.approx(base.volumen_concreto_m3)
        assert var.masa_acero_kg == pytest.approx(base.masa_acero_kg, rel=0.02)


def test_el_optimo_troncopiramidal_nunca_usa_mas_que_el_prismatico():
    base = z.disenar(400, 400, CARGAS, SUELO, M)[0]
    opt = t.optimizar(400.0, CARGAS, SUELO, M)
    assert opt is not None and opt.cumple
    assert opt.volumen_m3 + opt.masa_acero_kg / 7850 <= base.volumen_concreto_m3 + base.masa_acero_kg / 7850 + 1e-9


def test_espesor_de_borde_menor_a_d_minima_se_rechaza():
    r = t.verificar(2200.0, 450.0, 200.0, 400.0, CARGAS, SUELO, M)
    assert not r.cumple and "C.15.7" in r.motivo_fallo


def test_mayor_recubrimiento_no_reduce_el_volumen_optimo():
    from src import zapata as z
    from src import zapata_troncopiramidal as t
    from src.viga import Materiales
    cargas = z.CargasZapata(P_serv=1000.0, P_u=1350.0)
    suelo = z.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5)
    m = Materiales(35.0, 420.0, 420.0)
    base = t.optimizar(400.0, cargas, suelo, m, recubrimiento_mm=75.0)
    mayor = t.optimizar(400.0, cargas, suelo, m, recubrimiento_mm=125.0)
    assert base is not None and mayor is not None
    assert mayor.volumen_m3 >= base.volumen_m3 - 1e-9


def _entorno(**kw):
    from src import zapata as z
    from src.viga import Materiales
    return z.CargasZapata(P_serv=1500.0, P_u=2025.0, **{k: v for k, v in kw.items() if k.startswith(("M",))}), \
        z.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5, ks_kn_m3=kw.get("ks", 0.0)), Materiales(28.0, 420.0, 420.0)


def test_el_optimo_concentrico_no_cambia():
    from src import zapata_troncopiramidal as t
    cargas, suelo, m = _entorno()
    r = t.optimizar(400.0, cargas, suelo, m)
    assert (r.L_mm, r.h_c_mm, r.h_e_mm) == (3000.0, 600.0, 300.0)


def test_el_momento_no_reduce_la_zapata_ni_el_acero():
    from src import zapata_troncopiramidal as t
    c0, suelo, m = _entorno()
    c1, _, _ = _entorno(Mx_serv=150.0, My_serv=150.0, Mx_u=200.0, My_u=200.0)
    a, b = t.optimizar(400.0, c0, suelo, m), t.optimizar(400.0, c1, suelo, m)
    assert b is not None and b.L_mm >= a.L_mm and b.volumen_m3 >= a.volumen_m3 - 1e-9


def test_excentricidad_con_despegue_se_rechaza():
    from src import zapata_troncopiramidal as t
    cargas, suelo, m = _entorno(Mx_serv=900.0, My_serv=0.0, Mx_u=1200.0, My_u=0.0)   # e = 0.6 m > L/6 = 0.5 m
    r = t.verificar(3000.0, 600.0, 600.0, 400.0, cargas, suelo, m)
    assert not r.cumple and "despegue" in r.motivo_fallo


def test_balasto_blando_rechaza_por_asentamiento():
    from src import zapata_troncopiramidal as t
    cargas, suelo, m = _entorno(ks=2000.0)    # (q - 25.5)/2000 m > 25 mm
    r = t.verificar(3000.0, 600.0, 300.0, 400.0, cargas, suelo, m)
    assert not r.cumple and "asentamiento" in r.motivo_fallo
