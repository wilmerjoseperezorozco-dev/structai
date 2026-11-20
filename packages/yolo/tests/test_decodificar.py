"""Tests de packages/yolo/src/decodificar.py (issue #217). Valores esperados calculados a mano."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest

import decodificar as d


def logit(p):
    return math.log(p / (1 - p))


# ── Formato ──
def test_formato_por_salidas():
    assert d.formato(["dets", "labels"]) == "detr"
    assert d.formato(["boxes", "scores"]) == "detr"
    assert d.formato(["output0"]) == "yolo"
    with pytest.raises(ValueError):
        d.formato(["a", "b", "c"])


def test_tamano_entrada_fijo_y_simbolico():
    assert d.tamano_entrada([1, 3, 384, 384]) == (384, 384)
    assert d.tamano_entrada(["batch", 3, "h", "w"], 560) == (560, 560)


# ── DETR ──
def test_detr_ejemplo_de_referencia_rfdetr():
    # Caso documentado en rfdetr/export/_runtime/decode.py: caja que cubre toda la imagen, clase 0.
    cajas = d.decodificar_detr(np.array([[0.5, 0.5, 1.0, 1.0]]), np.array([[9.0, -9.0]]), umbral=0.3, clase_fondo=None)
    assert len(cajas) == 1
    x1, y1, x2, y2, conf, c = cajas[0]
    assert (x1, y1, x2, y2, c) == (0.0, 0.0, 1.0, 1.0, 0)
    assert conf == pytest.approx(1 / (1 + math.exp(-9.0)))


def test_detr_excluye_ranura_sin_objeto():
    # 2 clases reales + ranura de fondo al final con score alto: no debe aparecer.
    lg = np.array([[logit(0.2), logit(0.9), logit(0.99)]])
    cajas = d.decodificar_detr(np.array([[0.5, 0.5, 0.2, 0.2]]), lg, umbral=0.5, clase_fondo=-1)
    assert [c[5] for c in cajas] == [1]
    assert cajas[0][4] == pytest.approx(0.9)


def test_detr_una_consulta_puede_dar_dos_clases():
    # Sigmoides independientes: una misma consulta con dos clases altas da dos detecciones (no argmax).
    # El tope de pares por defecto es Q (nº de consultas, 300 en los modelos reales), igual que en rfdetr.
    lg = np.array([[logit(0.8), logit(0.7), -20.0], [-20.0, -20.0, -20.0]])
    cajas = d.decodificar_detr(np.array([[0.3, 0.3, 0.2, 0.2], [0.5, 0.5, 0.1, 0.1]]), lg, umbral=0.5)
    assert sorted(c[5] for c in cajas) == [0, 1]
    assert {c[:4] for c in cajas} == {cajas[0][:4]}       # misma caja, dos clases
    assert cajas[0][4] >= cajas[1][4]


def test_detr_umbral_y_recorte_a_la_imagen():
    b = np.array([[0.95, 0.05, 0.3, 0.3], [0.5, 0.5, 0.1, 0.1]])
    lg = np.array([[logit(0.6), -20.0], [logit(0.3), -20.0]])
    cajas = d.decodificar_detr(b, lg, umbral=0.5)
    assert len(cajas) == 1
    x1, y1, x2, y2, *_ = cajas[0]
    assert (x1, y1) == pytest.approx((0.8, 0.0)) and (x2, y2) == pytest.approx((1.0, 0.2))


def test_detr_orden_por_confianza_y_num_select():
    b = np.tile([0.5, 0.5, 0.1, 0.1], (4, 1))
    lg = np.array([[logit(p), -20.0] for p in (0.6, 0.95, 0.7, 0.8)])
    cajas = d.decodificar_detr(b, lg, umbral=0.5, num_select=2)
    assert [round(c[4], 2) for c in cajas] == [0.95, 0.8]


def test_detr_sin_detecciones():
    assert d.decodificar_detr(np.zeros((3, 4)), np.full((3, 3), -20.0), umbral=0.4) == []


# ── YOLO (comportamiento heredado de main.py) ──
def _yolo(filas, nc=2):
    return np.array(filas, dtype=np.float32).T[None]   # [1, 4+nc, N]


def test_yolo_nms_por_clase():
    salida = _yolo([
        [320, 320, 100, 100, 0.9, 0.1],
        [322, 318, 100, 100, 0.8, 0.1],   # misma clase, IoU alto → se suprime
        [320, 320, 100, 100, 0.1, 0.7],   # otra clase, misma caja → se conserva
        [100, 100, 50, 50, 0.3, 0.2],     # bajo umbral
    ])
    cajas = d.decodificar_yolo(salida, umbral=0.4)
    assert [(c[5], round(c[4], 1)) for c in cajas] == [(0, 0.9), (1, 0.7)]
    assert cajas[0][:4] == pytest.approx((270 / 640, 270 / 640, 370 / 640, 370 / 640))


# ── Preproceso ──
def test_preproceso_detr_normaliza_con_imagenet():
    pytest.importorskip("cv2")
    rgb = np.full((10, 20, 3), 255, dtype=np.uint8)
    x = d.preprocesar_detr(rgb, 4, 6)
    assert x.shape == (1, 3, 4, 6) and x.dtype == np.float32
    assert x[0, :, 0, 0] == pytest.approx((1 - d.IMAGENET_MEDIA) / d.IMAGENET_DESV, rel=1e-5)


def test_inferir_con_sesion_falsa_detr():
    pytest.importorskip("cv2")

    class T:
        def __init__(self, name, shape=None):
            self.name, self.shape = name, shape

    class Sesion:
        def get_inputs(self):
            return [T("input", [1, 3, 32, 32])]

        def get_outputs(self):
            return [T("dets"), T("labels")]

        def run(self, _, feeds):
            assert feeds["input"].shape == (1, 3, 32, 32)
            return [np.array([[[0.5, 0.5, 0.5, 0.5]]]), np.array([[[logit(0.9), -20.0]]])]

    cajas = d.inferir(Sesion(), np.zeros((64, 48, 3), dtype=np.uint8), umbral=0.5)
    assert len(cajas) == 1 and cajas[0][5] == 0 and cajas[0][:4] == pytest.approx((0.25, 0.25, 0.75, 0.75))
