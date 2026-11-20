"""Optimizador de pórtico (L1, #167): cantidades contra cálculo a mano, frontera exacta y puntos con nombre."""
import dataclasses
import math
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_integral as di
from src import optimizador_pareto as op
from src.diseno_portico import DERIVA_MAX, ProyectoPortico

from motor_concreto.viga import Verificacion  # noqa: E402

GRILLA = ((250.0, 300.0, 350.0), (500.0, 600.0, 700.0))
COLS = (400, 500, 600)
CALIDADES = ("3000", "4000")
ACERO = 7850.0                                   # kg/m³


def proyecto(**kw):
    base = dict(luces_m=(6.0, 6.0), alturas_piso_m=(3.2, 3.0), carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0,
                municipio="Pereira", departamento="Risaralda", perfil_suelo="D", capacidad="DES")
    base.update(kw)
    return ProyectoPortico(**base)


@pytest.fixture(scope="module")
def informe():
    return op.optimizar_portico(proyecto(), CALIDADES, columnas_mm=COLS, grilla=GRILLA)


# ------------------------------------------------------------------ Fase 1: cantidades a mano

def _a(d_mm):
    return math.pi / 4 * d_mm ** 2


def test_cantidades_de_un_portico_sintetico_coinciden_con_el_calculo_a_mano():
    """Pórtico de 1 vano de 5 m y 2 pisos de 3 m, columna 400×400 con 8 N°6 sin estribos, viga 300×500 DMI con 3+3 N°5 y E N°3 @200.

    A mano (hipótesis declaradas de cantidades_costo):
      columnas: 2 ejes × 2 pisos × 3 m = 12 m de columna → 8 × A(19,1 mm) × 12 m × 7850 kg/m³        = 215,9 kg
      viga: ln = 5 − 0,4 = 4,6 m; barras 4,6 + 2·40·15,9 mm = 5,872 m → 6 × A(15,9) × 5,872 × 7850  = 54,92 kg
            estribos DMI: ceil(4600/200) + 1 = 24; largo 2(300−80) + 2(500−80) + 2·max(6·9,5; 75) = 1430 mm
            → 24 × A(9,5) × 1,43 × 7850                                                          = 19,10 kg
      concreto: 2 niveles × 0,3 × 0,5 × 4,6 + 4 columnas × 0,4² × 3                               = 3,30 m³
    """
    p = ProyectoPortico(luces_m=(5.0,), alturas_piso_m=(3.0, 3.0), carga_muerta_kn_m=10.0, carga_viva_kn_m=5.0,
                        capacidad="DMI", recubrimiento_mm=40.0)
    col = SimpleNamespace(b=400.0, h=400.0, n_barras=8, dia="6", estribo="3", n_estribos=0)
    viga = SimpleNamespace(b=300.0, h=500.0, dia="5", n_sup=3, n_inf=3, estribo_dia="3", s_conf=100.0, s_centro=200.0,
                           n_estribos=0, nivel="DMI")
    viga_dc = dataclasses.make_dataclass("V", [(k, object) for k in vars(viga)], frozen=True)(**vars(viga))
    q = op.cantidades_portico(p, SimpleNamespace(c=400.0, viga=viga_dc, columna=col))
    col_kg = 8 * _a(19.1) * 1e-6 * 12.0 * ACERO
    long_kg = 6 * _a(15.9) * 1e-6 * (4.6 + 2 * 40 * 15.9 / 1000) * ACERO
    est_kg = 24 * _a(9.5) * 1e-6 * 1.430 * ACERO
    assert col_kg == pytest.approx(215.9, abs=0.1) and long_kg == pytest.approx(54.92, abs=0.01)
    assert q.acero_kg == pytest.approx(col_kg + 2 * (long_kg + est_kg), rel=1e-9)
    assert q.volumen_m3 == pytest.approx(2 * 0.3 * 0.5 * 4.6 + 4 * 0.16 * 3.0, rel=1e-12)


def test_co2_del_acero_es_1_322_por_kg_y_es_lineal():
    _cop, co2 = op._cc.costo_co2(op._cc.Cantidades(0.0, 100.0, 0.0), 21.0)
    assert co2 == pytest.approx(132.2, rel=1e-12)                               # Pardo 2022: 1,322 kgCO₂e/kg
    q = op._cc.Cantidades(2.0, 150.0, 10.0)
    assert op._cc.costo_co2(q + q, 21.0)[1] == pytest.approx(2 * op._cc.costo_co2(q, 21.0)[1], rel=1e-12)


def test_razon_dc_solo_cuenta_resistencia():
    d = SimpleNamespace(verificaciones=(
        Verificacion("Ancho b ≥ 200 mm", 200.0, 100.0, "mm", False, "C.21.3.4.1"),          # razón 2: geometría, no entra
        Verificacion("Flexión negativa φMn ≥ Mu", 80.0, 100.0, "kN·m", True, "C.10.2"),
        Verificacion("Cortante φ(Vc+Vs) ≥ Vu", 90.0, 100.0, "kN", True, "C.11.2.1.1")))
    assert op.razon_dc(d) == pytest.approx(0.9)
    with pytest.raises(ValueError):
        op.razon_dc(SimpleNamespace(verificaciones=()))


# ------------------------------------------------------------------ Fase 2: frontera

def test_no_dominados_contra_un_conjunto_a_mano():
    F = np.array([[1, 5], [2, 2], [5, 1], [3, 3], [2, 2], [6, 6], [1, 6]])
    assert op.no_dominados(F).tolist() == [True, True, True, False, True, False, False]
    with pytest.raises(ValueError):
        op.no_dominados(np.array([[1.0, math.nan]]))


def test_frontera_es_exacta(informe):
    F = np.array([c.vector() for c in informe.frontera])
    assert op.no_dominados(F).all()                                             # nadie en la frontera se domina entre sí
    for c in informe.factibles:                                                 # todo factible queda dominado o en la frontera
        v = np.array(c.vector())
        assert any((f <= v).all() for f in F)


def test_min_costo_es_la_linea_base_b1_del_motor_actual(informe):
    b1 = min(di.diseno_integral(dataclasses.replace(proyecto(), calidad_concreto=k), columnas_mm=COLS, grilla=GRILLA).optimo.costo_directo
             for k in CALIDADES)
    assert informe.puntos["min_costo"].costo_directo_cop == pytest.approx(b1, rel=1e-12)


def test_puntos_nombrados_estan_en_la_frontera_y_cumplen(informe):
    assert set(informe.puntos) == set(op.PUNTOS_NOMBRADOS)
    ids = {id(c) for c in informe.frontera}
    for nombre, c in informe.puntos.items():
        assert id(c) in ids, nombre
        assert informe.paridad[nombre] < di.PARIDAD_MAX
    assert informe.puntos["min_co2e"].co2e_kg == min(c.co2e_kg for c in informe.factibles)
    assert informe.puntos["mayor_holgura"].razon_dc_max == min(c.razon_dc_max for c in informe.factibles)


def test_todo_factible_cumple_resistencia_y_deriva(informe):
    for c in informe.factibles:
        assert 0 < c.razon_dc_max <= 1.0 + 1e-9
        assert c.deriva_relativa <= DERIVA_MAX + 1e-12
        assert c.volumen_concreto_m3 == pytest.approx(
            2 * sum(c.b_mm * c.h_mm * 1e-6 * (L - c.c_mm / 1000) for L in (6.0, 6.0)) + 3 * (c.c_mm / 1000) ** 2 * 6.2, rel=1e-12)


def test_monotonicidad_mas_carga_no_abarata(informe):
    mas = op.optimizar_portico(proyecto(carga_muerta_kn_m=30.0), CALIDADES, columnas_mm=COLS, grilla=GRILLA)
    assert mas.puntos["min_costo"].costo_directo_cop >= informe.puntos["min_costo"].costo_directo_cop
    assert mas.puntos["min_co2e"].co2e_kg >= informe.puntos["min_co2e"].co2e_kg


def test_fallo_explicito():
    with pytest.raises(ValueError):
        op.optimizar_portico(proyecto(), ("9999",), columnas_mm=COLS, grilla=GRILLA)
    with pytest.raises(ValueError):
        op.optimizar_portico(proyecto(), (), columnas_mm=COLS, grilla=GRILLA)
    with pytest.raises(ValueError):
        op.optimizar_portico(proyecto(carga_muerta_kn_m=400.0, carga_viva_kn_m=200.0), ("3000",), columnas_mm=(300,),
                             grilla=((250.0,), (300.0,)))
