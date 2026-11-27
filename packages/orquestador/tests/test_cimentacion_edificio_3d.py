"""Medición de zapatas bajo el edificio 3D (#324-C): reacciones, combinaciones B.2.3/B.2.4 y gobierno."""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import cimentacion_edificio_3d as ci, diseno_edificio_3d as de  # noqa: E402


def proyecto(**kw):
    base = dict(luces_x_m=(5.0, 5.0), luces_y_m=(5.0, 5.0), alturas_piso_m=(3.0, 3.0), columnas_mm=(350, 350),
                vigas_mm=((300, 400), (300, 400)), carga_muerta_kpa=5.0, carga_viva_kpa=2.0, aa=0.05, av=0.05,
                perfil_suelo="D", divipola="08001")
    base.update(kw)
    return de.ProyectoEdificio3D(**base)


def test_reacciones_de_d_suman_el_peso_y_hay_casos_de_viento():
    p = proyecto(viento=de.VientoB6(v_m_s=36.0, exposicion="D"))
    nodos, r = ci.reacciones_por_caso(p)
    assert len(nodos) == 9
    m = de.construir_modelo(p)
    peso = de.analisis_sismico(p, m)["W_kn"]
    # W sísmico no incluye la mitad inferior de las columnas del primer piso; la reacción sí
    medio_piso = 9 * 0.35 ** 2 * de.GAMMA_CONCRETO * 3.0 / 2
    assert sum(r["D"][n["k"]][0] for n in nodos) == pytest.approx(peso + medio_piso, rel=1e-6)
    assert sum(abs(r["Ex+e"][n["k"]][0]) for n in nodos) < 1e9 and any(c.startswith("W") for c in r)


def test_combinaciones_de_servicio_y_ultimas_de_la_nsr10():
    cs = {n: (s, u) for n, s, u in ci.combinaciones(["D", "L", "Ex+e", "Ex-e", "Ey+e", "Ey-e", "Wx+,GCpi+"])}
    assert cs["D+W[Wx+,GCpi+]"] == ({"D": 1, "Wx+,GCpi+": 1}, {"D": 1.2, "L": 1.0, "Wx+,GCpi+": 1.6})       # B.2.3-5 / B.2.4-4
    assert cs["0.6D+W[Wx+,GCpi+]"] == ({"D": 0.6, "Wx+,GCpi+": 1}, {"D": 0.9, "Wx+,GCpi+": 1.6})            # B.2.3-9 / B.2.4-6
    s, u = cs["0.6D+0.7E[Ex+e+0.3Ey+e+]"]
    assert s == pytest.approx({"D": 0.6, "Ex+e": 0.7, "Ey+e": 0.21}) and u == {"D": 0.9, "Ex+e": 1, "Ey+e": 0.3}  # B.2.3-10


def test_momento_grande_hace_gobernar_la_excentricidad():
    p = proyecto()
    nodos = [{"k": 0, "x": 0.0, "y": 0.0}]
    r = {"D": {0: np.array([1000.0, 0.0, 0.0])}, "L": {0: np.zeros(3)}, "Wx+,GCpi+": {0: np.array([0.0, 0.0, 500.0])}}
    res = ci.disenar_zapatas(p, 500.0, reac=(nodos, r))
    z = res.zapatas[0]
    # 0,6D+W: P = 600 kN, My = 500 kN·m → e = 0,83 m → núcleo L ≥ 6e = 5,0 m (el peso propio y del relleno lo bajan)
    assert z.cumple and z.gobierna == "excentricidad" and z.L_nucleo_mm > z.L_portante_mm
    assert 3000 <= z.L_nucleo_mm <= 5000 and z.L_mm >= z.L_nucleo_mm


def test_sin_momento_gobierna_la_capacidad_portante():
    p = proyecto()
    nodos = [{"k": 0, "x": 0.0, "y": 0.0}]
    r = {"D": {0: np.array([1500.0, 0.0, 0.0])}, "L": {0: np.array([500.0, 0.0, 0.0])}}
    z = ci.disenar_zapatas(p, 200.0, reac=(nodos, r)).zapatas[0]
    assert z.cumple and z.gobierna in ("portante", "estructural") and z.L_nucleo_mm <= z.L_portante_mm
    assert z.L_portante_mm == pytest.approx(math.ceil(math.sqrt(2000 / (200 - 25)) * 20) * 50, abs=150)
