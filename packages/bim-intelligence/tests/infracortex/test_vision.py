"""Tests InfraCortex — sensor de visión (vision.py) contra una imagen sintética real.

Detecciones sintéticas (posiciones Y conocidas), no inferencia YOLO real —
mismo estado documentado en vision.py: requiere fine-tuning para producción.
Valores esperados verificados corriendo el prototipo original antes del port
(6 estribos, separaciones 70/70/80/110/70 mm, 2 fuera de norma con s_max=75mm).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.infracortex.vision import (
    InfracortexVisionSensor,
    calcular_separaciones,
    calibrar_escala,
    DeteccionEstribo,
)

ANCHO_PX = 600
ALTO_PX = 500
ANCHO_MM = 600  # calibración 1:1 (1 px = 1 mm)

POSICIONES_ESTRIBOS_PX = [60, 130, 200, 280, 390, 460]
SEPARACIONES_ESPERADAS_MM = [70.0, 70.0, 80.0, 110.0, 70.0]
S_MAX_DISENO_MM = 75.0


@pytest.fixture
def imagen_sintetica():
    return np.full((ALTO_PX, ANCHO_PX, 3), 45, dtype=np.uint8)


@pytest.fixture
def sensor():
    return InfracortexVisionSensor(
        s_max_diseno_mm=S_MAX_DISENO_MM,
        escala_mm_por_px=ANCHO_MM / ANCHO_PX,
    )


def test_calibrar_escala_devuelve_mm_por_px():
    escala = calibrar_escala(longitud_referencia_px=100.0, longitud_referencia_mm=25.0)
    assert escala == pytest.approx(0.25)


def test_analizar_imagen_detecta_los_seis_estribos(sensor, imagen_sintetica):
    detecciones, _ = sensor.analizar_imagen(imagen_sintetica, POSICIONES_ESTRIBOS_PX)
    assert len(detecciones) == 6
    assert all(isinstance(d, DeteccionEstribo) for d in detecciones)


def test_separaciones_calculadas_coinciden_con_valores_reales(sensor, imagen_sintetica):
    """Escala 1:1 → separación en mm debe ser exactamente la diferencia en px."""
    _, separaciones = sensor.analizar_imagen(imagen_sintetica, POSICIONES_ESTRIBOS_PX)

    assert len(separaciones) == 5
    obtenidas_mm = [s.separacion_mm for s in separaciones]
    assert obtenidas_mm == pytest.approx(SEPARACIONES_ESPERADAS_MM)


def test_veredicto_nsr10_marca_dos_fallas_de_seis_espaciamientos(sensor, imagen_sintetica):
    """s_max=75mm: separaciones de 80mm y 110mm deben marcarse como FALLA; el resto OK."""
    _, separaciones = sensor.analizar_imagen(imagen_sintetica, POSICIONES_ESTRIBOS_PX)

    fallos = [s for s in separaciones if not s.cumple_nsr10]
    aciertos = [s for s in separaciones if s.cumple_nsr10]

    assert len(fallos) == 2
    assert len(aciertos) == 3
    assert {round(f.separacion_mm) for f in fallos} == {80, 110}


def test_calcular_separaciones_ordena_por_posicion_y_no_por_orden_de_entrada():
    """Si las detecciones llegan desordenadas, el cálculo debe ordenarlas por Y antes de restar."""
    detecciones_desordenadas = [
        DeteccionEstribo(id=0, y_centro_px=200.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=1, y_centro_px=60.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=2, y_centro_px=130.0, x1_px=0, x2_px=100, confianza=0.9),
    ]

    resultados = calcular_separaciones(detecciones_desordenadas, escala_mm_por_px=1.0, s_max_diseno_mm=75.0)

    assert [r.separacion_mm for r in resultados] == pytest.approx([70.0, 70.0])
