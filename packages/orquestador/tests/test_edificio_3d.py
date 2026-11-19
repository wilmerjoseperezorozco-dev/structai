"""#275 F4/F0: edificio 3D → diseño de vigas y columnas → cantidades → memoria de cálculo."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_edificio_3d as de

mc = de.mc


def proyecto(**kw):
    base = dict(luces_x_m=(6.0, 6.0, 6.0), luces_y_m=(5.0, 5.0), alturas_piso_m=(3.0,) * 5, columnas_mm=(750,) * 5,
                vigas_mm=((400, 650),) * 5, carga_muerta_kpa=6.0, carga_viva_kpa=1.8, aa=0.25, av=0.25, perfil_suelo="D",
                divipola="08001")
    base.update(kw)
    return de.ProyectoEdificio3D(**base)


@pytest.fixture(scope="module")
def informe():
    return de.disenar_edificio(proyecto())


def test_reparto_45_conserva_la_carga_del_panel():
    for a, b in ((6.0, 5.0), (4.0, 7.0), (5.0, 5.0)):
        assert de._area_45(a, b) * 2 + de._area_45(b, a) * 2 == pytest.approx(a * b)


def test_equilibrio_vertical_bajo_carga_muerta():
    p = proyecto()
    m = de.construir_modelo(p)
    r = m.portico.resolver(de._p3.Caso3D("D", uniformes=m.cargas_d))
    reac = sum(v[2] for v in r.reacciones.values())
    carga = sum(-w[2] * m.portico.longitud(m.portico.elementos[k]) for k, w in m.cargas_d.items())
    assert reac == pytest.approx(carga, rel=1e-9)
    losa = p.carga_muerta_kpa * 18.0 * 10.0 * 5
    assert carga > losa                                     # losa + peso propio de vigas y columnas


def test_momento_reconstruido_coincide_con_el_extremo_j():
    """M(x) = −Mz,i + Vy,i·x + q·x²/2 debe dar Mz,j en x = L (equilibrio del elemento con carga uniforme)."""
    p = proyecto()
    m = de.construir_modelo(p)
    r = m.portico.resolver(de._p3.Caso3D("D", uniformes=m.cargas_d))
    for k, t in enumerate(m.meta):
        if t[0] not in ("vx", "vy"):
            continue
        f, L, w = r.f_extremos[k], m.portico.longitud(m.portico.elementos[k]), m.w_viga[k][0]
        assert -f[5] + f[1] * L - w * L**2 / 2 == pytest.approx(f[11], abs=1e-6 * max(1.0, abs(f[11])))
        assert f[1] - w * L == pytest.approx(-f[7], abs=1e-6)


def test_combinaciones_b242_con_ortogonal():
    nombres, C, es_e = de.combinaciones()
    assert len(nombres) == 2 + 16 * 4
    assert es_e.sum() == 64
    assert set(np.round(np.abs(C[es_e][:, 2:]).max(axis=1), 6)) == {1.0}
    assert all(sorted(np.round(np.abs(f[2:]), 6))[-2:] == [0.3, 1.0] for f in C[es_e])


def test_edificio_que_cumple(informe):
    assert informe.cumple, informe.fallas
    assert informe.deriva["uso_max"] <= 1.0
    assert all(v["diseno"] is not None for v in informe.vigas)
    assert all(c["diseno"] is not None and c["biaxial"] <= 1.0 for c in informe.columnas)
    # columnas de abajo cargan más
    assert informe.columnas[0]["demanda"]["P_max_kn"] > informe.columnas[-1]["demanda"]["P_max_kn"]


def test_axial_de_la_columna_interior_por_area_tributaria(informe):
    """Pu de la columna más cargada ≈ área tributaria × pisos × (1,2D + 1,6L) + peso propio (orden de magnitud ±25 %)."""
    p = informe.proyecto
    trib = 6.0 * 5.0 * 5
    pp = 24 * (0.4 * 0.65 * (6.0 + 5.0) / 30 + 0.75**2 * 3.0 / 30)       # kN/m² equivalentes de vigas y columna
    estimado = trib * (1.2 * (p.carga_muerta_kpa + pp) + 1.6 * p.carga_viva_kpa)
    assert informe.columnas[0]["demanda"]["P_max_kn"] == pytest.approx(estimado, rel=0.25)


def test_deriva_insuficiente_se_reporta_como_falla():
    inf = de.disenar_edificio(proyecto(columnas_mm=(450,) * 5, vigas_mm=((300, 450),) * 5))
    assert not inf.cumple
    assert any("Deriva" in f for f in inf.fallas)
    assert not inf.memoria.cumple
    assert any("NO CUMPLE" in a for a in inf.memoria.advertencias)


def test_memoria_f0(informe):
    mem = informe.memoria
    assert mem.esquema == mc.VERSION_ESQUEMA
    assert mem.cumple
    assert mem.no_verifica and mem.aviso
    estados = {l.estado for l in mem.datos_entrada + mem.cargas + mem.modelacion}
    assert {"ENTRADA", "NSR-10 (leído)", "CALCULADO", "HIPÓTESIS"} <= estados
    assert {e.tipo for e in mem.diseno} == {"viga", "columna"}
    assert sum(e.cantidad for e in mem.diseno if e.tipo == "columna") == 12 * 5
    d = json.loads(mem.a_json())
    assert d["cumple"] is True and d["cantidades"]["por_m2"]["acero_kg_m2"] > 0
    c = mem.caracteristicas
    assert c["n_pisos"] == 5 and 5 < c["acero_kg_m2"] < 80 and c["costo_cop_m2"] > 0
    assert mc.MemoriaCalculo.model_validate_json(mem.model_dump_json()).cumple


def test_memoria_html_escapa_el_nombre():
    inf = de.disenar_edificio(proyecto(nombre="<script>alert(1)</script>", alturas_piso_m=(3.0,) * 3,
                                       columnas_mm=(600,) * 3, vigas_mm=((350, 550),) * 3))
    h = inf.memoria.a_html()
    assert "<script>" not in h and "&lt;script&gt;" in h
    assert "NO verifica" in h


def test_memoria_exige_declarar_lo_no_verificado(informe):
    d = informe.memoria.model_dump()
    d["no_verifica"] = []
    with pytest.raises(ValueError):
        mc.MemoriaCalculo.model_validate(d)


def test_validaciones_de_entrada():
    with pytest.raises(ValueError):
        proyecto(columnas_mm=(750,) * 4)
    with pytest.raises(ValueError):
        proyecto(capacidad="ALTA")
