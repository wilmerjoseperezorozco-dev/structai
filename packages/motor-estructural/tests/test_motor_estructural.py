"""Tests motor-estructural (InfraCortex) — IFC → PINN → NSR-10 Títulos A/B/C.

Mismo patrón que el resto de motores: cada aserción verifica contra el
valor real observado al correr el motor, no un número supuesto. Los
valores esperados se verificaron antes corriendo el pipeline completo
end-to-end vía TestClient contra /estructural/analizar-nudo e
/estructural/inspeccion-estribos.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ifcopenshell
import ifcopenshell.api
import numpy as np
import pytest

from src.infracortex_core import InfracortexEngine
from src.load_engine import calcular_demanda_cortante_nudo, chequeo_nsr10_nudo, ZONA_SISMICA_ATLANTICO, CARGAS_GRAVEDAD_DEFAULT
from src.vision_engine import InfracortexVisionSensor, DeteccionEstribo, ResultadoEspaciado

PROPS_CONCRETO = {"fc": 28.0, "fy": 420.0, "b": 300.0, "h": 300.0, "d": 265.0, "Av": 56.5, "s": 75.0}


@pytest.fixture
def nudo_ifc_path(tmp_path):
    """Columna en el origen P(0,0,0), viga a 3 m de altura en Z."""
    model = ifcopenshell.api.run("project.create_file")
    ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Infracortex_Test")
    ifcopenshell.api.run("unit.assign_unit", model)

    columna = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcColumn", name="Col")
    viga = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBeam", name="Viga")

    ifcopenshell.api.run("geometry.edit_object_placement", model, product=columna, matrix=np.eye(4))
    matriz_viga = np.eye(4)
    matriz_viga[2, 3] = 3.0
    ifcopenshell.api.run("geometry.edit_object_placement", model, product=viga, matrix=matriz_viga)

    ruta = tmp_path / "nudo_test.ifc"
    model.write(str(ruta))
    return str(ruta), columna.GlobalId, viga.GlobalId


# ── InfracortexEngine — topología del nudo ──────────────────────────────────

def test_extraer_topologia_nudo_retorna_tupla_de_tres(nudo_ifc_path):
    """BUG CORREGIDO: la versión original descartaba la rotación de la
    columna (get_local_placement calculado sin asignar) y retornaba solo
    2 valores — una función que por nombre extrae la topología del NUDO
    (viga + columna) en realidad ignoraba la columna por completo."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)

    resultado = motor.extraer_topologia_nudo(guid_viga, guid_col)

    assert len(resultado) == 3
    rotacion_viga, rotacion_columna, posicion_nudo = resultado
    assert rotacion_viga.shape == (3, 3)
    assert rotacion_columna.shape == (3, 3)
    assert np.allclose(rotacion_viga, np.eye(3))
    assert np.allclose(rotacion_columna, np.eye(3))
    assert np.allclose(posicion_nudo, [0.0, 0.0, 3000.0])


def test_ensamblar_rigidez_local_produce_matriz_12x12_por_miembro(nudo_ifc_path):
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)
    rot_viga, rot_columna, _ = motor.extraer_topologia_nudo(guid_viga, guid_col)

    T12_viga = motor.ensamblar_rigidez_local(rot_viga)
    T12_columna = motor.ensamblar_rigidez_local(rot_columna)

    assert T12_viga.shape == (12, 12)
    assert T12_columna.shape == (12, 12)


# ── load_engine — demanda sísmica/gravedad + chequeo NSR-10 ─────────────────

def test_calcular_demanda_cortante_nudo_valores_reales():
    """Valores verificados end-to-end (TestClient /estructural/analizar-nudo)."""
    resultado = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD_DEFAULT, ZONA_SISMICA_ATLANTICO, altura_piso_mm=3000.0
    )

    assert resultado["T_seg"] == pytest.approx(0.3396, abs=1e-3)
    assert resultado["Sa"] == pytest.approx(0.45, abs=1e-3)
    assert resultado["Vs_basal_N"] / 1000 == pytest.approx(8.96, abs=0.01)
    assert resultado["Vu_gravedad_N"] / 1000 == pytest.approx(43.04, abs=0.01)
    assert resultado["Vu_sismo_N"] / 1000 == pytest.approx(47.20, abs=0.01)
    assert resultado["combinacion_governa"] == "1.2D+1.0E+1.0L"
    # El caso sísmico gobierna sobre el de solo gravedad — Vu_diseno debe ser el máximo
    assert resultado["Vu_diseno_N"] == max(resultado["Vu_gravedad_N"], resultado["Vu_sismo_N"])


def test_chequeo_nsr10_nudo_valores_reales():
    """Vu=47.20kN < phi*Vn=116.52kN → cumple, margen 59.5%."""
    resultado = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD_DEFAULT, ZONA_SISMICA_ATLANTICO, altura_piso_mm=3000.0
    )
    chequeo = chequeo_nsr10_nudo(PROPS_CONCRETO, resultado["Vu_diseno_N"])

    assert chequeo["Vc_kN"] == pytest.approx(71.51, abs=0.01)
    assert chequeo["Vs_kN"] == pytest.approx(83.85, abs=0.01)
    assert chequeo["Vn_max_kN"] == pytest.approx(809.6, abs=0.1)
    assert chequeo["phi_Vn_kN"] == pytest.approx(116.52, abs=0.01)
    assert chequeo["margen_pct"] == pytest.approx(59.5, abs=0.1)
    assert chequeo["cumple"] is True


def test_chequeo_nsr10_nudo_falla_cuando_demanda_supera_capacidad():
    """Comportamiento inverso: una demanda mayor que phi*Vn debe marcar cumple=False."""
    chequeo = chequeo_nsr10_nudo(PROPS_CONCRETO, Vu_N=200_000.0)  # 200 kN >> 116.52 kN disponibles
    assert chequeo["cumple"] is False
    assert chequeo["margen_pct"] < 0


# ── vision_engine — inspección de estribos ───────────────────────────────────

def test_inspeccion_estribos_detecta_seis_y_marca_dos_fallas():
    """Mismo layout verificado end-to-end: separaciones 70/70/80/110/70mm,
    s_max=75mm → 2 fallas (80 y 110), 3 OK."""
    imagen = np.full((500, 600, 3), 45, dtype=np.uint8)
    posiciones_px = [60, 130, 200, 280, 390, 460]

    sensor = InfracortexVisionSensor(s_max_diseno_mm=75.0, escala_mm_por_px=1.0)
    detecciones, separaciones = sensor.analizar(imagen, posiciones_px)

    assert len(detecciones) == 6
    assert len(separaciones) == 5
    obtenidas = [s.separacion_mm for s in separaciones]
    assert obtenidas == pytest.approx([70.0, 70.0, 80.0, 110.0, 70.0])

    fallos = [s for s in separaciones if not s.cumple_nsr10]
    assert len(fallos) == 2
    assert {round(f.separacion_mm) for f in fallos} == {80, 110}


def test_calcular_separaciones_ordena_por_y_no_por_orden_de_llegada():
    sensor = InfracortexVisionSensor(s_max_diseno_mm=75.0, escala_mm_por_px=1.0)
    detecciones_desordenadas = [
        DeteccionEstribo(id=0, y_centro_px=200.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=1, y_centro_px=60.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=2, y_centro_px=130.0, x1_px=0, x2_px=100, confianza=0.9),
    ]

    resultados = sensor.calcular_separaciones(detecciones_desordenadas)

    assert [r.separacion_mm for r in resultados] == pytest.approx([70.0, 70.0])
