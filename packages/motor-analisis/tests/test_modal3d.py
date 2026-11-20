"""Pruebas de F2 (#274): modal y espectral con soluciones analíticas (edificio de cortante de 1 y 2 grados de libertad
por dirección), propiedades de la combinación CQC y el ajuste A.5.4.5."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import numpy as np
import pytest
from pydantic import ValidationError

from src.contrato_3d import SolicitudEspectral3D, edificio_3d_espectral_contrato
from src.modal3d import G, cqc, espectral, masas_piso, modos
from src.portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D
from src.sismo3d import Piso

E, Gm = 2.5e7, 1.0e7
EMP = (True,) * 6
CABEZA = (False, False, True, True, True, False)     # edificio de cortante: solo ux, uy, rz libres
I0, J0, h = 0.002, 0.003, 3.0
k = 12 * E * I0 / h**3


def _cortante(npisos=1, xs=(0.0, 6.0), ys=(0.0, 4.0)):
    nodos, els, apoyos, dia = [], [], {}, []
    prev = None
    for nv in range(npisos + 1):
        fila = []
        for x in xs:
            for y in ys:
                fila.append(len(nodos))
                nodos.append(Nodo3D(x, y, nv * h))
        if nv == 0:
            apoyos.update({q: EMP for q in fila})
        else:
            apoyos.update({q: CABEZA for q in fila})
            els += [Elemento3D(a, b, E, Gm, 0.16, I0, I0, J0) for a, b in zip(prev, fila)]
            dia.append(Diafragma(f"P{nv}", tuple(fila), sum(xs) / 2, sum(ys) / 2))
        prev = fila
    return Portico3D(nodos, els, apoyos, dia)


def _pisos(n, W=1000.0, dx=6.0, dy=4.0):
    return [Piso(f"P{i + 1}", h, dx, dy, W) for i in range(n)]


def test_un_piso_periodos_traslacional_y_torsional():
    m = _cortante()
    p = _pisos(1)
    md = modos(m, masas_piso(p))
    masa, J = masas_piso(p)[0]
    T_tr = 2 * math.pi * math.sqrt(masa / (4 * k))
    Kt = sum(k * ((x - 3) ** 2 + (y - 2) ** 2) for x in (0, 6) for y in (0, 4)) + 4 * Gm * J0 / h
    T_t = 2 * math.pi * math.sqrt(J / Kt)
    assert sorted(md.periodos, reverse=True)[:2] == pytest.approx([T_tr, T_tr], rel=1e-9)
    assert min(md.periodos) == pytest.approx(T_t, rel=1e-9)


def test_dos_pisos_frecuencias_cerradas():
    m = _cortante(2)
    md = modos(m, masas_piso(_pisos(2)))
    masa = 1000.0 / G
    K4 = 4 * k
    esperadas = sorted([K4 / masa * (3 - math.sqrt(5)) / 2, K4 / masa * (3 + math.sqrt(5)) / 2])
    w2x = sorted(md.omega[np.argsort(-md.masa_efectiva[:, 0])[:2]] ** 2)
    assert w2x == pytest.approx(esperadas, rel=1e-9)


def test_masa_participante_completa_suma_la_masa_total():
    m = _cortante(3)
    md = modos(m, masas_piso(_pisos(3)))
    assert md.masa_efectiva.sum(axis=0) == pytest.approx([md.masa_total, md.masa_total], rel=1e-9)


def test_un_grado_espectral_igual_a_sa_por_W_y_ajuste():
    m = _cortante()
    p = _pisos(1)
    sa = lambda T: 0.5  # noqa: E731  meseta
    r = espectral(m, p, sa, (500.0, 500.0), "regular", "general", False)
    d = r["direcciones"]["x"]
    assert d["Vt_sin_ajuste_kn"] == pytest.approx(0.5 * 1000.0, rel=1e-9)     # Vt = Sa·W en 1 GDL
    assert d["factor_ajuste"] == 1.0
    ux = 0.5 * G / (4 * k / (1000.0 / G))                                    # Sa·g/ω²
    assert d["pisos"][0]["deriva_cm_m"] == pytest.approx(ux, rel=1e-9)
    r2 = espectral(m, p, sa, (1000.0, 1000.0), "regular", "general", False)   # 0,8·1000 > 500 → escala 1,6
    assert r2["direcciones"]["x"]["factor_ajuste"] == pytest.approx(1.6)
    assert r2["direcciones"]["x"]["pisos"][0]["deriva_cm_m"] == pytest.approx(1.6 * ux)
    r3 = espectral(m, p, sa, (1000.0, 1000.0), "irregular", "general", False)
    assert r3["direcciones"]["x"]["factor_ajuste"] == pytest.approx(1.8)


def test_cqc_propiedades():
    w = np.array([1.0, 50.0])
    v = np.array([3.0, 4.0])
    assert cqc(v, w) == pytest.approx(5.0, rel=1e-3)                    # modos separados → SRSS
    assert cqc(v, np.array([2.0, 2.0])) == pytest.approx(7.0)           # frecuencias iguales → suma absoluta
    assert cqc(np.array([3.0, -4.0]), np.array([2.0, 2.0])) == pytest.approx(1.0)


def test_torsion_accidental_aumenta_la_deriva_de_borde():
    m = _cortante(2)
    p = _pisos(2)
    sa = lambda T: 0.4  # noqa: E731
    a = espectral(m, p, sa, (1.0, 1.0), "regular", "general", False, torsion_accidental=False)
    b = espectral(m, p, sa, (1.0, 1.0), "regular", "general", False, torsion_accidental=True)
    assert b["uso_max_punto"] > a["uso_max_punto"]
    assert a["uso_max_punto"] == pytest.approx(a["uso_max_cm"], rel=1e-6)   # simétrico sin torsión: borde = centro


def test_masa_insuficiente_o_entradas_invalidas():
    m = _cortante(2)
    with pytest.raises(ValueError):
        modos(m, masas_piso(_pisos(1)))
    with pytest.raises(ValueError):
        espectral(m, _pisos(2), lambda T: 0.3, (1.0, 1.0), "casi_regular", "general", False)


# ── contrato F2 con espectro NSR-10 (motor-geopot) ──────────────────────────────────────────────────────────────────

def _solicitud(**kw):
    m = _cortante(3, xs=(0.0, 5.0, 10.0), ys=(0.0, 6.0))
    edif = dict(nodos=[(n.x, n.y, n.z) for n in m.nodos],
                elementos=[dict(i=e.i, j=e.j, E=e.E, G=e.G, A=e.A, Iy=e.Iy, Iz=e.Iz, J=e.J) for e in m.elementos],
                apoyos={q: tuple(v) for q, v in m.apoyos.items()},
                pisos=[dict(nombre=d.nombre, nodos=list(d.nodos), x_cm=d.x_cm, y_cm=d.y_cm, altura_entrepiso_m=h,
                            dim_x_m=10.0, dim_y_m=6.0, carga_vertical_kn=600.0, fs_x_kn=0.0, fs_y_kn=0.0)
                       for d in m.diafragmas],
                sistema_deriva="general", secciones_fisuradas=False)
    base = dict(edificio=edif, sitio=dict(aa=0.25, av=0.25, perfil="D", grupo_uso="I", sistema_periodo="porticos_concreto"),
                otras_irregularidades=False, torsion_accidental=True, deriva_con_I_unitario=False)
    base.update(kw)
    return SolicitudEspectral3D(**base)


def test_contrato_espectral_completo():
    r = edificio_3d_espectral_contrato(_solicitud())
    assert set(r) == {"modal", "espectral", "fhe_referencia"}
    v = r["espectral"].valor
    for d in ("x", "y"):
        dd = v["direcciones"][d]
        assert dd["Vt_sin_ajuste_kn"] * dd["factor_ajuste"] >= 0.8 * dd["Vs_kn"] - 1e-6
    assert r["modal"].valor["masa_participante"]["x"] >= 0.9
    for t in r["modal"].valor["periodo_por_direccion"]:
        assert t["T_usado_s"] <= t["CuTa_s"] + 1e-12
    for x in r.values():
        x.model_dump_json()


def test_contrato_espectral_rechaza_sitio_invalido():
    with pytest.raises(ValidationError):
        _solicitud(sitio=dict(aa=0.25, av=0.25, perfil="F", grupo_uso="I", sistema_periodo="porticos_concreto"))


def test_condensacion_estatica_reproduce_la_flexibilidad_del_modelo_completo():
    # pórtico con vigas (muchos GDL internos): K* condensada debe dar los mismos desplazamientos de maestros
    sys.path.insert(0, os.path.dirname(__file__))
    from test_portico3d import _edificio
    from src.portico3d import Caso3D
    m, _ = _edificio(npisos=3)
    idx = [g for d in m.diafragmas for g in m._maestro_idx[d.nombre]]
    otros = np.setdiff1d(np.arange(m._nred), idx)
    K = m._Kr
    Kc = K[np.ix_(idx, idx)] - K[np.ix_(idx, otros)] @ np.linalg.solve(K[np.ix_(otros, otros)], K[np.ix_(otros, idx)])
    F = np.zeros(len(idx))
    F[[0, 4, 8]] = (10.0, -5.0, 7.0)                    # Fx en P1, Fy en P2, Mz en P3
    u = np.linalg.solve(Kc, F)
    r = m.resolver(Caso3D("c", maestros={"P1": (10.0, 0, 0), "P2": (0, -5.0, 0), "P3": (0, 0, 7.0)}))
    completo = [v for d in m.diafragmas for v in r.maestros[d.nombre]]
    assert np.allclose(u, completo, rtol=1e-9, atol=1e-14)
