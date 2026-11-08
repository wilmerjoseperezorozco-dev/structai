import dataclasses
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_integral as di
from src import diseno_portico as dp
from src.diseno_portico import ProyectoPortico

GRILLA = ((250.0, 300.0, 350.0), (500.0, 600.0, 700.0, 800.0))
COLS = (400, 500, 600)


def proyecto(**kw):
    base = dict(luces_m=(6.0, 6.0), alturas_piso_m=(3.2, 3.0), carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0,
                municipio="Pereira", departamento="Risaralda", perfil_suelo="D", capacidad="DES")
    base.update(kw)
    return ProyectoPortico(**base)


@pytest.fixture(scope="module")
def informe():
    return di.diseno_integral(proyecto(), grilla=GRILLA, columnas_mm=COLS)


def _lote(p, b=300.0, h=600.0, c=500.0):
    pc = dataclasses.replace(p, columna_mm=(c, c))
    cap, info = dp._capacidad(pc)
    ctx = dp._ctx_sismico(pc, cap, info)
    return pc, ctx, dp._lote_vectorizado(pc, ctx, np.array([b]), np.array([h]), con_columnas=True)


def test_equilibrio_vertical_compresion_positiva():
    p = proyecto()
    pc, ctx, (lote, tpl, nid, nx, ny, pesos, fz) = _lote(p)
    f = lote.col_f[0]
    story0 = [ic for ic, (st, *_r) in enumerate(tpl.columnas) if st == 0]
    w_pp = dp.PESO_UNIT_KN_M3 * 0.3 * 0.6
    carga_D = (p.carga_muerta_kn_m + w_pp) * sum(p.luces_m) * len(p.alturas_piso_m)
    carga_L = p.carga_viva_kn_m * sum(p.luces_m) * len(p.alturas_piso_m)
    assert f[story0, 0, 0].sum() == pytest.approx(carga_D, rel=1e-9)          # P en la base bajo D
    assert f[story0, 0, 1].sum() == pytest.approx(carga_L, rel=1e-9)


def test_cortante_basal_se_reparte_entre_las_columnas_de_la_base():
    p = proyecto()
    pc, ctx, (lote, tpl, nid, nx, ny, pesos, fz) = _lote(p)
    f = lote.col_f[0]
    story0 = [ic for ic, (st, *_r) in enumerate(tpl.columnas) if st == 0]
    assert abs(f[story0, 1, 2].sum()) == pytest.approx(fz[0].sum(), rel=1e-9)


def test_momentos_de_columna_equilibran_el_nudo_interior_bajo_sismo():
    """Nudo interior del piso 1 bajo E (sin gravedad): M de extremo de columnas + M de extremo de vigas = 0."""
    p = proyecto()
    pc, ctx, (lote, tpl, nid, nx, ny, pesos, fz) = _lote(p)
    f = lote.col_f[0]
    inf, sup = 0 * nx + 1, 1 * nx + 1                       # columnas del eje interior, entrepisos 0 y 1
    m_cols = f[inf, 5, 2] + f[sup, 2, 2]
    assert abs(m_cols) > 1.0
    modelo, vigas, res, _w = dp._analizar(pc, 300.0, 600.0, tuple(float(x) for x in fz[0]))
    nodo = nid(1, 1)
    m_vigas = 0.0
    for k in vigas:
        e = modelo.elementos[k]
        if e.i == nodo:
            m_vigas += res["E"].f_extremos[k][2]
        elif e.j == nodo:
            m_vigas += res["E"].f_extremos[k][5]
    assert (m_cols + m_vigas) == pytest.approx(0.0, abs=1e-8)


def test_fuerzas_de_columna_vectorizadas_coinciden_con_el_resolver_escalar():
    p = proyecto()
    pc, ctx, (lote, tpl, nid, nx, ny, pesos, fz) = _lote(p, b=250.0, h=700.0, c=450.0)
    modelo, vigas, res, w_pp = dp._analizar(pc, 250.0, 700.0, tuple(float(x) for x in fz[0]))
    for ic, (st, i, _g, _kt) in enumerate(tpl.columnas):
        for ci, caso in enumerate(("D", "L", "E")):
            ref = res[caso].f_extremos[st * nx + i]
            assert np.allclose(lote.col_f[0, ic, :, ci], ref, rtol=1e-9, atol=1e-8), (st, i, caso)


def test_optimo_cumple_todo_y_el_costo_total_es_la_suma(informe):
    o = informe.optimo
    assert o is not None and informe.diagnostico["paridad_escalar_max_dif_rel"] < 1e-6
    assert o.viga.cumple and o.columna.cumple
    assert o.costo_directo == pytest.approx(o.costo_vigas + o.costo_columnas)
    assert o.deriva <= dp.DERIVA_MAX and o.q_max <= 1 / 3
    assert o.razon_scwb >= 1.0                                                    # DES: columna fuerte–viga débil
    costos = [c.costo_directo for c in informe.ranking]
    assert costos == sorted(costos)


def test_scwb_del_optimo_se_recalcula_de_forma_independiente(informe):
    """Recalcula ΣMnc/(1,2ΣMnb) con indexación propia de columnas y las combinaciones con E escritas a mano."""
    o = informe.optimo
    p = proyecto()
    pc, ctx, (lote, tpl, nid, nx, ny, pesos, fz) = _lote(p, b=o.b, h=o.h, c=o.c)
    f = lote.col_f[0]                                         # (columnas, 6, [D, L, E])
    mat = di._viga.Materiales(fc=dp.FC_MPA_POR_CALIDAD["3000"], fy=420.0, fyt=420.0)
    mneg, mpos = di._mn_viga(o.viga, mat)
    cv = di._col.curva(o.c, o.c, o.columna.n_cara, o.columna.dia, o.columna.estribo, 40.0, mat.fc, mat.fy)
    combos = [(1.2, 1.0, 1.0), (1.2, 1.0, -1.0), (0.9, 0.0, 1.0), (0.9, 0.0, -1.0)]
    peor = math.inf
    for j in range(1, ny):
        for i in range(nx):
            interior = 0 < i < nx - 1
            mnb = (mneg + mpos) if interior else max(mneg, mpos)
            for cd, cl, ce in combos:
                pu = lambda col: cd * f[col, 0, 0] + cl * f[col, 0, 1] + ce * f[col, 0, 2]
                suma = di._col.mn_a(cv, pu((j - 1) * nx + i))
                if j < ny - 1:
                    suma += di._col.mn_a(cv, pu(j * nx + i))
                peor = min(peor, suma / (1.2 * mnb))
    assert peor == pytest.approx(o.razon_scwb, rel=1e-9)
    assert peor >= 1.0


def test_quitar_scwb_nunca_encarece(informe, monkeypatch):
    monkeypatch.setattr(di._col, "_scwb", lambda *a, **k: math.inf)
    sin = di.diseno_integral(proyecto(), grilla=GRILLA, columnas_mm=COLS)
    assert sin.optimo.costo_directo <= informe.optimo.costo_directo + 1e-6


def test_suelo_mas_blando_no_baja_el_costo():
    a = di.diseno_integral(proyecto(perfil_suelo="B"), grilla=GRILLA, columnas_mm=COLS).optimo
    e = di.diseno_integral(proyecto(perfil_suelo="E"), grilla=GRILLA, columnas_mm=COLS).optimo
    assert a is not None and (e is None or e.costo_directo >= a.costo_directo - 1e-6)


def test_solo_gravedad_dmi_sin_sismo_disena_columnas():
    p = ProyectoPortico(luces_m=(5.0, 5.0), alturas_piso_m=(3.0, 3.0), carga_muerta_kn_m=20.0, carga_viva_kn_m=6.0, capacidad="DMI")
    r = di.diseno_integral(p, grilla=GRILLA, columnas_mm=COLS)
    assert r.optimo is not None and r.optimo.columna.nivel == "DMI" and math.isnan(r.optimo.razon_scwb)


def test_columnas_mas_grandes_reducen_la_deriva():
    p = proyecto()
    d = []
    for c in (400.0, 600.0):
        pc, ctx, (lote, *_r) = _lote(p, c=c)
        d.append(float(lote.deriva_max[0]))
    assert d[1] < d[0]


def test_error_con_calidad_no_soportada():
    with pytest.raises(ValueError):
        di.diseno_integral(proyecto(calidad_concreto="9999"), grilla=GRILLA, columnas_mm=COLS)


def test_los_k_de_jackson_moreland_estan_entre_1_y_3():
    p = proyecto()
    k_lu, lu_min, lu_max = di._ks(p, 500.0, 300.0, 600.0, 3, 21.0)
    assert lu_min == pytest.approx(2.4) and lu_max == pytest.approx(2.6)
    assert 1.0 * lu_max <= k_lu <= 3.0 * lu_max
