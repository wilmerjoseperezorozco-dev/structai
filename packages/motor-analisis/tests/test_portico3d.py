"""Pruebas del pórtico 3D con diafragma rígido y de la FHE 3D con torsión y derivas (#274, F1).

Referencias sin ETABS: soluciones cerradas, invariantes del método de rigidez y PyNite (MIT) como verificador
independiente (solo en pruebas; se salta si no está instalado).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import numpy as np
import pytest
from pydantic import ValidationError

from src.contrato_3d import SolicitudEdificio3D, edificio_3d_fhe_contrato
from src.portico3d import Caso3D, Diafragma, Elemento3D, Nodo3D, Portico3D
from src.sismo3d import Piso, analizar_fhe

E, G = 2.5e7, 1.0e7
EMP = (True,) * 6


def _col(i, j, I=0.002, A=0.16, J=0.003, Iy=None):
    return Elemento3D(i, j, E, G, A, Iy if Iy is not None else I, I, J)


# ── soluciones cerradas ─────────────────────────────────────────────────────────────────────────────────────────────

def test_voladizo_flexion_en_ambos_planos_y_torsion():
    L, P, T = 3.0, 10.0, 5.0
    el = Elemento3D(0, 1, E, G, 0.1, 0.001, 0.004, 0.002)
    m = Portico3D([Nodo3D(0, 0, 0), Nodo3D(L, 0, 0)], [el], {0: EMP})
    u = m.resolver(Caso3D("c", nodales={1: (0, P, P, T, 0, 0)})).u[1]
    # viga horizontal: y_local = Z global (Iz resiste la flexión vertical), z_local = −Y global (Iy, flexión lateral)
    assert u[2] == pytest.approx(P * L**3 / (3 * E * el.Iz))
    assert u[1] == pytest.approx(P * L**3 / (3 * E * el.Iy))
    assert u[3] == pytest.approx(T * L / (G * el.J))


def test_columna_vertical_ejes_documentados():
    # en una columna, Iz resiste el desplazamiento en X global e Iy en Y global
    h, P = 3.0, 10.0
    el = Elemento3D(0, 1, E, G, 0.1, 0.001, 0.004, 0.002)
    m = Portico3D([Nodo3D(0, 0, 0), Nodo3D(0, 0, h)], [el], {0: EMP})
    u = m.resolver(Caso3D("c", nodales={1: (P, P, 0, 0, 0, 0)})).u[1]
    assert u[0] == pytest.approx(P * h**3 / (3 * E * el.Iz))
    assert u[1] == pytest.approx(P * h**3 / (3 * E * el.Iy))


def _un_piso(xs=(0.0, 6.0), ys=(0.0, 4.0), h=3.0, I=0.002, Is=None, x_cm=None, y_cm=None):
    """Columnas empotradas abajo, unidas arriba solo por un diafragma rígido, con uz, rx y ry de cabeza restringidos:
    edificio de cortante exacto, cada columna aporta k = 12EI/h³ en ambas direcciones."""
    nodos, els, apoyos = [], [], {}
    cabezas = []
    for a, x in enumerate(xs):
        for b, y in enumerate(ys):
            k0 = len(nodos)
            nodos += [Nodo3D(x, y, 0), Nodo3D(x, y, h)]
            Ii = (Is or {}).get((a, b), I)
            els.append(_col(k0, k0 + 1, I=Ii))
            apoyos[k0] = EMP
            cabezas.append(k0 + 1)
            apoyos[k0 + 1] = (False, False, True, True, True, False)
    xc = x_cm if x_cm is not None else sum(xs) / len(xs)
    yc = y_cm if y_cm is not None else sum(ys) / len(ys)
    return Portico3D(nodos, els, apoyos, [Diafragma("P1", tuple(cabezas), xc, yc)]), cabezas


def test_un_piso_simetrico_rigidez_lateral_12EI_h3():
    m, _ = _un_piso()
    k = 12 * E * 0.002 / 3.0**3
    ux, uy, th = m.resolver(Caso3D("x", maestros={"P1": (100.0, 0, 0)})).maestros["P1"]
    assert ux == pytest.approx(100.0 / (4 * k), rel=1e-3) and abs(th) < 1e-12 and abs(uy) < 1e-12


def test_un_piso_rotacion_torsional_analitica():
    m, _ = _un_piso()
    k = 12 * E * 0.002 / 3.0**3
    Kt = sum(k * ((x - 3) ** 2 + (y - 2) ** 2) for x in (0, 6) for y in (0, 4))   # Σ k·r² (columnas cuadradas)
    Kt += 4 * G * 0.003 / 3.0                                                     # + torsión propia GJ/h
    th = m.resolver(Caso3D("t", maestros={"P1": (0, 0, 50.0)})).maestros["P1"][2]
    assert th == pytest.approx(50.0 / Kt, rel=2e-3)


def test_excentricidad_de_rigidez_genera_giro_con_el_signo_correcto():
    # columnas de la línea x = 6 cuatro veces más rígidas → centro de rigidez a la derecha del de masa;
    # Fy en el centro de masa (x = 3) hace girar el piso en sentido horario (θ < 0)
    m, _ = _un_piso(Is={(1, 0): 0.008, (1, 1): 0.008})
    th = m.resolver(Caso3D("y", maestros={"P1": (0, 100.0, 0)})).maestros["P1"][2]
    xr = (0.002 * 0 + 0.008 * 6) / 0.010                   # centro de rigidez en x
    k1, k2 = 12 * E * 0.002 / 27, 12 * E * 0.008 / 27
    Kt = 2 * k1 * xr**2 + 2 * k2 * (6 - xr) ** 2           # rigidez torsional respecto al centro de rigidez (Y)
    Kt += (2 * k1 + 2 * k2) * 2.0**2                        # aporte de la rigidez en X (brazos ±2 m)
    Kt += 4 * G * 0.003 / 3.0                               # torsión propia de las columnas GJ/h
    assert th < 0
    assert th == pytest.approx(-100.0 * (xr - 3.0) / Kt, rel=5e-3)


# ── invariantes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def _edificio(npisos=3, xs=(0.0, 5.0, 10.0), ys=(0.0, 6.0), h=3.0, vigas=True, diafragma=True):
    nodos, els, apoyos, dia = [], [], {}, []
    idx = {}
    for nv in range(npisos + 1):
        for x in xs:
            for y in ys:
                idx[(nv, x, y)] = len(nodos)
                nodos.append(Nodo3D(x, y, nv * h))
                if nv == 0:
                    apoyos[idx[(nv, x, y)]] = EMP
    for nv in range(1, npisos + 1):
        for x in xs:
            for y in ys:
                els.append(_col(idx[(nv - 1, x, y)], idx[(nv, x, y)], I=0.0027, A=0.16, J=0.0045))
        if vigas:
            for y in ys:
                for a, b in zip(xs, xs[1:]):
                    els.append(Elemento3D(idx[(nv, a, y)], idx[(nv, b, y)], E, G, 0.12, 0.0016, 0.0016, 0.002))
            for x in xs:
                for a, b in zip(ys, ys[1:]):
                    els.append(Elemento3D(idx[(nv, x, a)], idx[(nv, x, b)], E, G, 0.12, 0.0016, 0.0016, 0.002))
        if diafragma:
            dia.append(Diafragma(f"P{nv}", tuple(idx[(nv, x, y)] for x in xs for y in ys),
                                 sum(xs) / len(xs), sum(ys) / len(ys)))
    return Portico3D(nodos, els, apoyos, dia), idx


def test_matriz_simetrica_y_equilibrio_global():
    m, idx = _edificio()
    assert np.allclose(m._K, m._K.T)
    r = m.resolver(Caso3D("c", maestros={"P3": (30.0, -20.0, 15.0), "P1": (10.0, 0, 0)},
                          nodales={idx[(2, 0.0, 0.0)]: (0, 0, -50.0, 0, 0, 0)}))
    R = sum(r.reacciones.values())
    assert R[0] == pytest.approx(-40.0, abs=1e-6) and R[1] == pytest.approx(20.0, abs=1e-6)
    assert R[2] == pytest.approx(50.0, abs=1e-6)


def test_maxwell_betti():
    m, idx = _edificio(diafragma=False)
    a, b = idx[(3, 10.0, 6.0)], idx[(1, 5.0, 0.0)]
    ua = m.resolver(Caso3D("a", nodales={a: (1.0, 0, 0, 0, 0, 0)})).u
    ub = m.resolver(Caso3D("b", nodales={b: (0, 1.0, 0, 0, 0, 0)})).u
    assert ua[b, 1] == pytest.approx(ub[a, 0], rel=1e-9)


def test_rotar_el_edificio_90_grados_rota_la_respuesta():
    m, _ = _un_piso(xs=(0.0, 6.0), ys=(0.0, 4.0))
    m2, _ = _un_piso(xs=(0.0, 4.0), ys=(0.0, 6.0))
    ux = m.resolver(Caso3D("x", maestros={"P1": (100.0, 0, 0)})).maestros["P1"][0]
    uy = m2.resolver(Caso3D("y", maestros={"P1": (0, 100.0, 0)})).maestros["P1"][1]
    assert ux == pytest.approx(uy, rel=1e-9)


def test_diafragma_equivale_a_losa_muy_rigida_en_su_plano():
    m, idx = _edificio(npisos=2)
    libre, idx2 = _edificio(npisos=2, diafragma=False)
    # misma estructura con vigas diagonales muy rígidas axialmente en cada piso (losa rígida en su plano)
    extra = []
    for nv in (1, 2):
        extra += [Elemento3D(idx2[(nv, 0.0, 0.0)], idx2[(nv, 10.0, 6.0)], E, G, 100.0, 1e-6, 1e-6, 1e-6),
                  Elemento3D(idx2[(nv, 10.0, 0.0)], idx2[(nv, 0.0, 6.0)], E, G, 100.0, 1e-6, 1e-6, 1e-6),
                  Elemento3D(idx2[(nv, 0.0, 0.0)], idx2[(nv, 5.0, 6.0)], E, G, 100.0, 1e-6, 1e-6, 1e-6),
                  Elemento3D(idx2[(nv, 10.0, 0.0)], idx2[(nv, 5.0, 6.0)], E, G, 100.0, 1e-6, 1e-6, 1e-6)]
    rigida = Portico3D(libre.nodos, libre.elementos + extra, libre.apoyos)
    ux = m.resolver(Caso3D("x", maestros={"P2": (100.0, 0, 0)})).maestros["P2"][0]
    nodos_p2 = [idx2[(2, x, y)] for x in (0.0, 5.0, 10.0) for y in (0.0, 6.0)]
    carga = {k: (100.0 / 6, 0, 0, 0, 0, 0) for k in nodos_p2}
    u2 = rigida.resolver(Caso3D("x", nodales=carga)).u
    assert np.mean(u2[nodos_p2, 0]) == pytest.approx(ux, rel=0.01)


def test_modelo_sin_apoyos_suficientes_falla():
    with pytest.raises(ValueError):
        Portico3D([Nodo3D(0, 0, 0), Nodo3D(0, 0, 3)], [_col(0, 1)], {0: (True, True, True, False, False, False)})


# ── PyNite (MIT) como verificador independiente ─────────────────────────────────────────────────────────────────────

def test_coincide_con_pynite_en_un_portico_espacial():
    Pynite = pytest.importorskip("Pynite")
    m, idx = _edificio(npisos=2, diafragma=False)
    carga = {idx[(2, 10.0, 6.0)]: (12.0, -7.0, -30.0, 0, 0, 0), idx[(1, 5.0, 0.0)]: (0, 9.0, 0, 0, 0, 0)}
    u = m.resolver(Caso3D("c", nodales=carga)).u
    f = Pynite.FEModel3D()
    f.add_material("c", E, G, 0.2, 0.0)
    for k, n in enumerate(m.nodos):
        f.add_node(f"N{k}", n.x, n.y, n.z)
    for k in m.apoyos:
        f.def_support(f"N{k}", True, True, True, True, True, True)
    for t, e in enumerate(m.elementos):
        assert e.Iy == e.Iz                                    # secciones simétricas: la orientación no importa
        f.add_section(f"S{t}", e.A, e.Iy, e.Iz, e.J)
        f.add_member(f"M{t}", f"N{e.i}", f"N{e.j}", "c", f"S{t}")
    for k, v in carga.items():
        for d, val in zip(("FX", "FY", "FZ"), v[:3]):
            if val:
                f.add_node_load(f"N{k}", d, val)
    f.analyze_linear()
    for k in range(len(m.nodos)):
        n = f.nodes[f"N{k}"]
        ref = [n.DX["Combo 1"], n.DY["Combo 1"], n.DZ["Combo 1"], n.RX["Combo 1"], n.RY["Combo 1"], n.RZ["Combo 1"]]
        assert np.allclose(u[k], ref, rtol=1e-6, atol=1e-10)


# ── FHE 3D, torsión accidental y derivas ────────────────────────────────────────────────────────────────────────────

def _pisos(m, h=3.0, dx=10.0, dy=6.0, w=800.0):
    return [Piso(d.nombre, h, dx, dy, w) for d in m.diafragmas]


def test_torsion_accidental_un_piso_coincide_con_mano():
    m, cab = _un_piso()
    p = [Piso("P1", 3.0, 6.0, 4.0, 1000.0)]
    r = analizar_fhe(m, p, [100.0], [100.0], "general", False)
    k = 12 * E * 0.002 / 27
    Kt = sum(k * ((x - 3) ** 2 + (y - 2) ** 2) for x in (0, 6) for y in (0, 4)) + 4 * G * 0.003 / 3.0
    u = 100.0 / (4 * k)
    th_x = 100.0 * 0.05 * 4.0 / Kt                        # Ex: Mz = F·0,05·dim_y; brazo a los bordes 2 m
    th_y = 100.0 * 0.05 * 6.0 / Kt                        # Ey: Mz = F·0,05·dim_x; brazo 3 m
    razon = max((u + 2 * th_x) / u, (u + 3 * th_y) / u)   # extremo / promedio de extremos (Tabla A.3-6)
    assert r["razon_torsional_max"] == pytest.approx(razon, rel=1e-6)
    assert r["irregularidad_torsional"] == "ninguna"
    assert max(f["deriva_cm_m"] for f in r["derivas"]) == pytest.approx(u, rel=1e-9)
    assert r["sin_limite_un_piso"] and r["cumple_deriva"]


def test_edificio_simetrico_regular_sin_irregularidad_ni_Ax():
    m, _ = _edificio()
    r = analizar_fhe(m, _pisos(m), [40.0, 80.0, 120.0], [40.0, 80.0, 120.0], "general", False)
    assert r["irregularidad_torsional"] == "ninguna" and all(a == 1.0 for d in r["Ax"].values() for a in d)
    assert {f["regla"] for f in r["derivas"]} == {"A.6.3.1.1 (centro de masa)"}


def test_irregularidad_torsional_activa_Ax_y_deriva_en_ejes():
    m, _ = _un_piso(Is={(1, 0): 0.02, (1, 1): 0.02}, xs=(0.0, 12.0), ys=(0.0, 2.0))
    m2 = Portico3D(m.nodos, m.elementos, m.apoyos, [Diafragma("P1", m.diafragmas[0].nodos, 6.0, 1.0)])
    pisos = [Piso("P1", 3.0, 12.0, 2.0, 500.0)]
    r = analizar_fhe(m2, pisos + [], [0.0], [100.0], "general", False)
    assert r["irregularidad_torsional"] in ("1aP", "1bP")
    assert r["Ax"]["y"][0] > 1.0 and r["Ax"]["y"][0] <= 3.0


def test_fisuradas_multiplica_por_0_7():
    m, _ = _edificio()
    a = analizar_fhe(m, _pisos(m), [40.0, 80.0, 120.0], [40.0, 80.0, 120.0], "general", False)
    b = analizar_fhe(m, _pisos(m), [40.0, 80.0, 120.0], [40.0, 80.0, 120.0], "general", True)
    assert b["uso_max_limite"] == pytest.approx(0.7 * a["uso_max_limite"])


def test_limite_mamposteria_cortante_es_la_mitad():
    m, _ = _edificio()
    a = analizar_fhe(m, _pisos(m), [40.0, 80.0, 120.0], [40.0, 80.0, 120.0], "general", False)
    b = analizar_fhe(m, _pisos(m), [40.0, 80.0, 120.0], [40.0, 80.0, 120.0], "mamposteria_cortante", False)
    assert b["uso_max_limite"] == pytest.approx(2 * a["uso_max_limite"])


def test_indice_de_estabilidad_Qi():
    m, _ = _edificio(npisos=1)
    r = analizar_fhe(m, _pisos(m, w=1000.0), [100.0], [100.0], "general", False)
    f = next(x for x in r["derivas"] if x["caso"] == "Ex+e")
    assert f["Qi"] == pytest.approx(1000.0 * f["deriva_cm_m"] / (100.0 * 3.0))


# ── contrato y sabotaje ─────────────────────────────────────────────────────────────────────────────────────────────

def _solicitud(**kw):
    m, idx = _edificio(npisos=2)
    base = dict(
        nodos=[(n.x, n.y, n.z) for n in m.nodos],
        elementos=[dict(i=e.i, j=e.j, E=e.E, G=e.G, A=e.A, Iy=e.Iy, Iz=e.Iz, J=e.J) for e in m.elementos],
        apoyos={k: EMP for k in m.apoyos},
        pisos=[dict(nombre=d.nombre, nodos=list(d.nodos), x_cm=d.x_cm, y_cm=d.y_cm, altura_entrepiso_m=3.0,
                    dim_x_m=10.0, dim_y_m=6.0, carga_vertical_kn=900.0, fs_x_kn=60.0 * (i + 1), fs_y_kn=60.0 * (i + 1))
               for i, d in enumerate(m.diafragmas)],
        sistema_deriva="general", secciones_fisuradas=False)
    base.update(kw)
    return SolicitudEdificio3D(**base)


def test_contrato_completo():
    r = edificio_3d_fhe_contrato(_solicitud())
    assert r.aviso_responsabilidad_profesional and r.supuestos and "A.6.4" in r.referencia_normativa
    assert len(r.valor["derivas"]) == 4 * 2
    r.model_dump_json()


@pytest.mark.parametrize("campo,valor", [("sistema_deriva", "concreto"), ("secciones_fisuradas", "si")])
def test_contrato_rechaza_entradas_invalidas(campo, valor):
    with pytest.raises(ValidationError):
        _solicitud(**{campo: valor})


def test_fuerza_negativa_o_nan_falla():
    s = _solicitud().model_dump()
    s["pisos"][0]["fs_x_kn"] = -1.0
    with pytest.raises(ValidationError):
        SolicitudEdificio3D(**s)
    s["pisos"][0]["fs_x_kn"] = float("nan")
    with pytest.raises(ValidationError):
        SolicitudEdificio3D(**s)


def test_pisos_fuera_de_orden_fallan():
    m, _ = _edificio()
    p = _pisos(m)[::-1]
    with pytest.raises(ValueError):
        analizar_fhe(m, p, [1.0] * 3, [1.0] * 3, "general", False)


def test_nodo_de_diafragma_no_puede_ser_apoyo():
    with pytest.raises(ValueError):
        Portico3D([Nodo3D(0, 0, 0), Nodo3D(0, 0, 3)], [_col(0, 1)], {0: EMP, 1: EMP}, [Diafragma("P", (1,), 0, 0)])
