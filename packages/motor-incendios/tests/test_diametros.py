"""Optimización de diámetros con tanque subterráneo (#336 F6). Los datos son ILUSTRATIVOS, no normativos ni precios
reales: catálogo de 1" a 2" a 30–75 mil por metro, K = 80, P_min = 50 kPa, v_max = 3 m/s, duración de 30 min, agua mínima
a −3,0 m y 10 kPa de succión. La referencia es la búsqueda exhaustiva (4⁵ = 1024 combinaciones)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import diametros as dm  # noqa: E402
from src import hidraulica as h  # noqa: E402

D = h.Demanda(80.0, 50.0, 0.0, 0.0, fuente="ilustrativo")
CAT = [dm.Opcion(h.Tuberia("1in", 0.0266, 120), 30000), dm.Opcion(h.Tuberia("1-1/4in", 0.0351, 120), 45000),
       dm.Opcion(h.Tuberia("1-1/2in", 0.0409, 120), 55000), dm.Opcion(h.Tuberia("2in", 0.0525, 120), 75000)]
LE = {(a, o.tuberia.dn): v for o in CAT for a, v in (("codo90", 0.6), ("te_lateral", 1.5))}
TR = [((0, 0, 0), (5, 0, 0)), ((5, 0, 0), (5, 2, 0)), ((5, 0, 0), (5, -6, 0)), ((5, -6, 0), (9, -6, 0)),
      ((5, 2, 0), (5, 4, 0))]
OP = [(5, 4, 0), (9, -6, 0), (5, 2, 0), (5, -6, 0)]
R = dm.Restricciones(3.0, None, True, fuente="ilustrativo")


def _tq(vol=None, c3=0.0):
    return dm.Tanque(30.0, -3.0, vol, c3, 10.0, fuente="ilustrativo")


def _par(tq, r=R):
    return (TR, (0, 0, 0), OP, D, CAT, LE, tq, r)


def test_solo_tuberia_iguala_al_exhaustivo():
    s, ex = dm.optimizar(*_par(_tq())), dm.exhaustivo(*_par(_tq()))
    assert s.mejor.costo == pytest.approx(ex.costo) == pytest.approx(875000.0)
    assert s.mejor.volumen_m3 == pytest.approx(7.028, abs=1e-3)


def test_el_recocido_corrige_al_voraz_cuando_pesa_el_tanque():
    tq = _tq(c3=2e7)
    s, ex = dm.optimizar(*_par(tq)), dm.exhaustivo(*_par(tq))
    assert s.voraz.costo > s.mejor.costo + 1e5                         # el voraz queda en un óptimo local
    assert s.mejor.costo == pytest.approx(ex.costo)
    assert s.mejor.volumen_m3 < 7.0                                    # red más balanceada: menos agua


def test_tanque_existente_obliga_a_subir_diametros():
    libre = dm.optimizar(*_par(_tq())).mejor
    s, ex = dm.optimizar(*_par(_tq(vol=7.0))), dm.exhaustivo(*_par(_tq(vol=7.0)))
    assert libre.volumen_m3 > 7.0
    assert s.mejor.volumen_m3 <= 7.0 and s.mejor.costo == pytest.approx(ex.costo) == pytest.approx(935000.0)


def test_tanque_insuficiente_aun_con_el_diametro_mayor():
    s = dm.optimizar(*_par(_tq(vol=5.0)))
    assert s.mejor is None and "tanque" in s.motivo


def test_presion_de_bomba_desde_el_nivel_minimo_del_tanque():
    e = dm.optimizar(*_par(_tq())).mejor
    assert e.p_bomba_kpa == pytest.approx(e.p_alimentacion_kpa + 9.81 * 3.0 + 10.0)
    r = dm.Restricciones(3.0, e.p_bomba_kpa - 1.0, True, fuente="ilustrativo")   # bomba que no alcanza
    s = dm.optimizar(*_par(_tq(), r))
    assert s.mejor.p_bomba_kpa <= e.p_bomba_kpa - 1.0 and s.mejor.costo > e.costo


def test_regla_telescopica_y_su_costo():
    s = dm.optimizar(*_par(_tq()))
    pb = dm._Problema(*_par(_tq()))
    a = s.mejor.asignacion
    assert all(p is None or a[k] <= a[p] for k, p in enumerate(pb.padre))
    libre = dm.exhaustivo(*_par(_tq(), dm.Restricciones(3.0, None, False, fuente="ilustrativo")))
    assert libre.costo <= s.mejor.costo


def test_la_solucion_pasa_el_verificador_hidraulico():
    s = dm.optimizar(*_par(_tq()))
    res = h.calcular(TR, (0, 0, 0), OP, D, s.tuberias(), LE)
    assert h.verificar(res, D, v_max_m_s=3.0) == []


def test_velocidad_inalcanzable_y_datos_sin_fuente():
    s = dm.optimizar(*_par(_tq(), dm.Restricciones(0.3, None, True, fuente="ilustrativo")))
    assert s.mejor is None and "velocidad" in s.motivo
    with pytest.raises(ValueError):
        dm.Tanque(30.0, -3.0, None, 0.0, 10.0, fuente="")
