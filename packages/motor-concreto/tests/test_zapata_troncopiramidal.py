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
