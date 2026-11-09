import itertools
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_integral as di
from src import diseno_por_pisos as pp
from src import diseno_portico as dp
from src.diseno_portico import ProyectoPortico
from src.diseno_inverso import FC_MPA_POR_CALIDAD

COLS, BASES, ALTS = (450, 550, 650), (250.0, 300.0), (600.0, 800.0)


def proyecto(pisos=3, **kw):
    base = dict(luces_m=(6.0, 6.0), alturas_piso_m=(3.2,) + (3.0,) * (pisos - 1), carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0,
                municipio="Pereira", departamento="Risaralda", perfil_suelo="D", capacidad="DES")
    base.update(kw)
    return ProyectoPortico(**base)


def contexto(p):
    cap, info = dp._capacidad(p)
    ctx = dp._ctx_sismico(p, cap, info)
    mat = di._viga.Materiales(fc=FC_MPA_POR_CALIDAD[p.calidad_concreto], fy=p.fy_mpa, fyt=p.fy_mpa)
    return cap, ctx, mat


def test_pesos_por_piso_coinciden_con_el_calculo_uniforme():
    p = proyecto()
    sec = pp.Seccion(500.0, 300.0, 700.0)
    nx = 3
    ref = dp._sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, p.carga_muerta_kn_m, (500.0, 500.0), 300.0, 700.0)
    assert np.allclose(pp._pesos(p, (sec,) * 3, nx), ref, rtol=1e-12)


def test_deriva_del_porticos_uniforme_coincide_con_el_nucleo_vectorizado():
    p = proyecto()
    cap, ctx, mat = contexto(p)
    sec = pp.Seccion(550.0, 250.0, 700.0)
    ev = pp.evaluar_asignacion(p, (sec,) * 3, cap, ctx, mat)
    pc = p.__class__(**{**p.__dict__, "columna_mm": (550.0, 550.0)})
    lote = dp._lote_vectorizado(pc, ctx, np.array([250.0]), np.array([700.0]))[0]
    assert max(x.deriva for x in ev.pisos) == pytest.approx(float(lote.deriva_max[0]), rel=1e-9)


def test_diseno_por_piso_no_cuesta_mas_que_el_uniforme_del_integral():
    p = proyecto()
    cap, ctx, mat = contexto(p)
    sec = pp.Seccion(550.0, 250.0, 800.0)
    ev = pp.evaluar_asignacion(p, (sec,) * 3, cap, ctx, mat)
    ref = di.diseno_integral(p, grilla=((250.0,), (800.0,)), columnas_mm=(550,)).optimo
    if ref is None or not ev.factible:
        pytest.skip("sección no factible en este caso")
    assert ev.costo <= ref.costo_directo * (1 + 1e-9)


def test_columnas_muy_pequenas_se_reportan_con_motivo():
    p = proyecto()
    cap, ctx, mat = contexto(p)
    ev = pp.evaluar_asignacion(p, (pp.Seccion(250.0, 250.0, 500.0),) * 3, cap, ctx, mat)
    assert not ev.factible and any(x.motivo for x in ev.pisos) or not ev.deriva_ok


def test_milp_unitario_elige_lo_mas_barato_y_respeta_columna_no_creciente():
    secs = [pp.Seccion(500.0, 250.0, 600.0), pp.Seccion(600.0, 250.0, 600.0)]
    costos = [[10.0, 12.0], [9.0, 8.0], [7.0, 6.0]]            # la columna grande abarata los pisos 2 y 3
    perm = [[True, True]] * 3
    sel, obj = pp._resolver_milp(costos, perm, secs, 3, None, None, True, [])
    # no creciente hacia arriba: si el piso 1 es 500 los demás deben ser 500; si es 600, cualquiera
    mejor = min(itertools.product(range(2), repeat=3),
                key=lambda a: sum(costos[j][s] for j, s in enumerate(a)) if all(secs[a[j]].c >= secs[a[j + 1]].c for j in range(2)) else 1e9)
    assert tuple(sel) == mejor and obj == pytest.approx(sum(costos[j][s] for j, s in enumerate(mejor)))


def test_milp_unitario_tope_de_secciones_distintas_y_cortes():
    secs = [pp.Seccion(500.0, 250.0, 600.0), pp.Seccion(500.0, 300.0, 700.0), pp.Seccion(500.0, 350.0, 800.0)]
    costos = [[5.0, 9.0, 9.0], [9.0, 5.0, 9.0], [9.0, 9.0, 5.0]]
    perm = [[True] * 3] * 3
    libre, _ = pp._resolver_milp(costos, perm, secs, 3, None, None, True, [])
    assert libre == [0, 1, 2]
    una, obj = pp._resolver_milp(costos, perm, secs, 3, None, 1, True, [])
    assert len(set(una)) == 1 and obj == pytest.approx(23.0)
    otra, _ = pp._resolver_milp(costos, perm, secs, 3, None, None, True, [(0, 1, 2)])
    assert otra != [0, 1, 2]


@pytest.fixture(scope="module")
def informe():
    return pp.diseno_por_pisos(proyecto(), columnas_mm=COLS, bases_mm=BASES, alturas_mm=ALTS)


def test_resultado_verificado_cumple_todo_y_no_supera_al_uniforme(informe):
    o, u = informe.optimo, informe.uniforme
    assert o is not None and o.factible and u is not None
    assert o.costo <= u.costo * (1 + 1e-9) and informe.ahorro_pct >= -1e-9
    for x in o.pisos:
        assert x.viga.cumple and x.columna.cumple and x.deriva <= dp.DERIVA_MAX
        assert x.seccion.c >= o.pisos[min(x.piso + 1, len(o.pisos) - 1)].seccion.c        # columna no crece hacia arriba


def test_contra_fuerza_bruta_la_brecha_es_pequena_y_nunca_negativa(informe):
    p = proyecto()
    cap, ctx, mat = contexto(p)
    secs = [pp.Seccion(float(c), b, h) for c in COLS for b in BASES for h in ALTS]
    mejor = math.inf
    for a in itertools.product(secs, repeat=3):
        if not all(a[j].c >= a[j + 1].c for j in range(2)):
            continue
        ev = pp.evaluar_asignacion(p, a, cap, ctx, mat)
        if ev.factible:
            mejor = min(mejor, ev.costo)
    assert informe.optimo.costo >= mejor - 1e-6               # nunca "mejor" que el verdadero mínimo
    # heurística con verificación exacta: no se afirma el óptimo global; brecha medida frente a la fuerza bruta ≤ 2 %
    assert informe.optimo.costo <= mejor * 1.02


def test_topes_de_secciones_distintas_se_respetan():
    r = pp.diseno_por_pisos(proyecto(), columnas_mm=COLS, bases_mm=BASES, alturas_mm=ALTS, max_columnas_distintas=1)
    if r.optimo is not None:
        assert len({x.seccion.c for x in r.optimo.pisos}) == 1


def test_error_con_calidad_no_soportada():
    with pytest.raises(ValueError):
        pp.diseno_por_pisos(proyecto(calidad_concreto="9999"), columnas_mm=COLS)
