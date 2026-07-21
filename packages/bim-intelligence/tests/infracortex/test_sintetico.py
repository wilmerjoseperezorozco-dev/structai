"""Tests InfraCortex — motor central (core.py) contra un IFC sintético real.

Mismo patrón que motor-vias/motor-gerencia: cada aserción se verifica
contra el valor real observado al correr el motor (no un número supuesto).
Genera nudo_test.ifc en tiempo de ejecución con ifcopenshell.api, igual
que el prototipo original.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ifcopenshell
import ifcopenshell.api
import numpy as np
import pytest

from src.infracortex.core import InfracortexEngine


@pytest.fixture
def nudo_ifc_path(tmp_path):
    """Columna en el origen P(0,0,0), viga a 3 m de altura en Z (mismo layout que el prototipo)."""
    model = ifcopenshell.api.run("project.create_file")
    ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Infracortex_Test")
    ifcopenshell.api.run("unit.assign_unit", model)

    columna = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcColumn", name="Col_Principal")
    viga = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBeam", name="Viga_Principal")

    ifcopenshell.api.run("geometry.edit_object_placement", model, product=columna, matrix=np.eye(4))

    matriz_viga = np.eye(4)
    matriz_viga[2, 3] = 3.0
    ifcopenshell.api.run("geometry.edit_object_placement", model, product=viga, matrix=matriz_viga)

    ruta = tmp_path / "nudo_test.ifc"
    model.write(str(ruta))
    return str(ruta), columna.GlobalId, viga.GlobalId


def test_extraer_topologia_nudo_retorna_tupla_de_tres(nudo_ifc_path):
    """BUG CORREGIDO: la versión original descartaba la rotación de la columna
    (llamaba get_local_placement sin asignar) y devolvía solo 2 valores."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)

    resultado = motor.extraer_topologia_nudo(guid_viga, guid_col)

    assert len(resultado) == 3
    rotacion_viga, rotacion_columna, posicion_nudo = resultado
    assert rotacion_viga.shape == (3, 3)
    assert rotacion_columna.shape == (3, 3)
    assert posicion_nudo.shape == (3,)


def test_posicion_nudo_coincide_con_la_viga_a_3m(nudo_ifc_path):
    """Viga colocada en Z=3.0 (unidad de proyecto = mm por defecto en ifcopenshell.api) → 3000 mm."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)

    _, _, posicion_nudo = motor.extraer_topologia_nudo(guid_viga, guid_col)

    assert np.allclose(posicion_nudo, [0.0, 0.0, 3000.0])


def test_rotaciones_identidad_cuando_ambos_placements_son_eye4(nudo_ifc_path):
    """Columna y viga se colocaron con np.eye(4) (sin rotación) → ambas rotaciones deben ser I."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)

    rotacion_viga, rotacion_columna, _ = motor.extraer_topologia_nudo(guid_viga, guid_col)

    assert np.allclose(rotacion_viga, np.eye(3))
    assert np.allclose(rotacion_columna, np.eye(3))


def test_ensamblar_rigidez_local_produce_matriz_12x12_block_diagonal(nudo_ifc_path):
    """4 bloques de rotación 3x3 (2 nodos x 6 GDL) → matriz de transformación 12x12."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)
    rotacion_viga, rotacion_columna, _ = motor.extraer_topologia_nudo(guid_viga, guid_col)

    T12_viga = motor.ensamblar_rigidez_local(rotacion_viga)
    T12_columna = motor.ensamblar_rigidez_local(rotacion_columna)

    assert T12_viga.shape == (12, 12)
    assert T12_columna.shape == (12, 12)
    # Bloques fuera de la diagonal deben ser cero (block_diag real, no una matriz densa)
    assert np.allclose(T12_viga[:3, 3:], 0.0)
    assert np.allclose(T12_viga[:3, :3], rotacion_viga)


def test_viga_y_columna_producen_matrices_de_transformacion_independientes():
    """Cada miembro (viga, columna) debe ensamblar su propia matriz — no se debe
    reusar una sola matriz para ambos (ese era justamente el efecto del bug original:
    al descartar la rotación de la columna, cualquier código downstream terminaba
    usando la rotación de la viga para ambos miembros)."""
    rotacion_viga = np.eye(3)
    rotacion_columna = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])  # rotación 90° en Z

    # ensamblar_rigidez_local no usa atributos de instancia — se llama sin
    # instanciar el motor completo (evita depender de un IFC en este caso).
    T12_viga = InfracortexEngine.ensamblar_rigidez_local(None, rotacion_viga)
    T12_columna = InfracortexEngine.ensamblar_rigidez_local(None, rotacion_columna)

    assert not np.allclose(T12_viga, T12_columna)
