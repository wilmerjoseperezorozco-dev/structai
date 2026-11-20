"""
Pre- y posproceso de detectores ONNX para /detect (issue #217). Solo numpy: sin torch ni ultralytics en producción.

Dos formatos de salida, detectados por la forma del grafo ONNX:

  yolo   un tensor [1, 4+nc, N] (YOLOv8/v11 anchor-free): cx,cy,w,h en píxeles de la entrada + score por clase.
         Requiere NMS. Se conserva por compatibilidad mientras exista un model.onnx YOLO; Ultralytics es AGPL-3.0,
         así que NO se entrena un modelo nuevo con él (ver train_rfdetr.py).
  detr   dos tensores (RF-DETR, Apache-2.0): `dets` [1, Q, 4] cx,cy,w,h NORMALIZADOS y `labels` [1, Q, C] logits.
         Sigmoide independiente por clase, top-k global sobre los pares (consulta, clase), umbral. Sin NMS.
         Réplica de rfdetr/export/_runtime/decode.py (RF-DETR 1.12, Apache-2.0).

Todas las funciones devuelven cajas NORMALIZADAS [0, 1] como tuplas (x1, y1, x2, y2, confianza, clase_id), que es lo
que el endpoint convierte a DeteccionElemento.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

IMAGENET_MEDIA = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_DESV = np.array([0.229, 0.224, 0.225], dtype=np.float32)

Caja = tuple  # (x1, y1, x2, y2, conf, clase_id), coordenadas normalizadas


# ── Formato ──────────────────────────────────────────────────────────────────────────────────────────────────────

def formato(nombres_salida: Sequence[str]) -> str:
    """'detr' si el grafo expone dets/labels (o dos salidas); 'yolo' si expone una sola."""
    n = [s.lower() for s in nombres_salida]
    if {"dets", "labels"} <= set(n) or len(n) == 2:
        return "detr"
    if len(n) == 1:
        return "yolo"
    raise ValueError(f"Salidas ONNX no reconocidas: {list(nombres_salida)}")


def tamano_entrada(forma: Sequence, por_defecto: int = 640) -> tuple[int, int]:
    """(alto, ancho) de la entrada NCHW; si el eje es simbólico se usa `por_defecto`."""
    h = forma[2] if len(forma) == 4 and isinstance(forma[2], int) else por_defecto
    w = forma[3] if len(forma) == 4 and isinstance(forma[3], int) else por_defecto
    return h, w


# ── Preproceso ───────────────────────────────────────────────────────────────────────────────────────────────────

def _redimensionar(rgb: np.ndarray, alto: int, ancho: int) -> np.ndarray:
    """Bilineal con centros de píxel (half-pixel), sin antialias: la convención de RFDETR.predict()."""
    import cv2  # opencv-python-headless (Apache-2.0), ya en requirements-vision.txt
    return cv2.resize(rgb, (ancho, alto), interpolation=cv2.INTER_LINEAR)


def preprocesar_yolo(rgb: np.ndarray, alto: int = 640, ancho: int = 640) -> np.ndarray:
    x = _redimensionar(rgb, alto, ancho).astype(np.float32) / 255.0
    return np.ascontiguousarray(x.transpose(2, 0, 1)[None])


def preprocesar_detr(rgb: np.ndarray, alto: int, ancho: int) -> np.ndarray:
    x = _redimensionar(rgb, alto, ancho).astype(np.float32) / 255.0
    x = (x - IMAGENET_MEDIA) / IMAGENET_DESV
    return np.ascontiguousarray(x.transpose(2, 0, 1)[None].astype(np.float32))


# ── Posproceso ───────────────────────────────────────────────────────────────────────────────────────────────────

def _iou(a: Caja, b: Caja) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def decodificar_yolo(salida: np.ndarray, umbral: float = 0.4, iou_nms: float = 0.5,
                     alto: int = 640, ancho: int = 640) -> list[Caja]:
    """[1, 4+nc, N] → cajas normalizadas tras umbral y NMS por clase (lógica idéntica a la que tenía main.py)."""
    pred = np.asarray(salida)[0].T
    cand: list[Caja] = []
    for p in pred:
        scores = p[4:]
        c = int(np.argmax(scores))
        conf = float(scores[c])
        if conf < umbral:
            continue
        cx, cy, w, h = (float(v) for v in p[:4])
        cand.append((max(0.0, (cx - w / 2) / ancho), max(0.0, (cy - h / 2) / alto),
                     min(1.0, (cx + w / 2) / ancho), min(1.0, (cy + h / 2) / alto), conf, c))
    cand.sort(key=lambda k: k[4], reverse=True)
    quedan: list[Caja] = []
    for c in cand:
        if all(c[5] != k[5] or _iou(c, k) < iou_nms for k in quedan):
            quedan.append(c)
    return quedan


def decodificar_detr(cajas_cxcywh: np.ndarray, logits: np.ndarray, umbral: float = 0.4,
                     clase_fondo: int | None = -1, num_select: int | None = None) -> list[Caja]:
    """RF-DETR: cajas [Q,4] normalizadas cx,cy,w,h y logits [Q,C] (sin el eje de lote) → cajas normalizadas.

    clase_fondo: ranura que se descarta antes de seleccionar. Con categorías COCO contiguas 0..N-1 (como las que
    escribe train_rfdetr.py) la ÚLTIMA ranura es "sin objeto" sin entrenar → -1. None la conserva (pesos COCO
    oficiales, donde la última ranura es la clase real 90)."""
    b = np.asarray(cajas_cxcywh, dtype=np.float32)
    lg = np.clip(np.asarray(logits, dtype=np.float32), -88, 88)
    scores = 1.0 / (1.0 + np.exp(-lg))
    ids = np.arange(scores.shape[1])
    if clase_fondo is not None and scores.shape[1] > 1:
        quitar = clase_fondo % scores.shape[1]
        scores = np.delete(scores, quitar, axis=1)
        ids = np.delete(ids, quitar)
    plano = scores.reshape(-1)
    k = min(len(plano), scores.shape[0] if num_select is None else num_select)
    if k == 0:
        return []
    top = np.argpartition(-plano, k - 1)[:k]
    top = top[np.argsort(-plano[top], kind="stable")]
    top = top[plano[top] > umbral]
    q, c = np.divmod(top, scores.shape[1])
    salida: list[Caja] = []
    for qi, ci, s in zip(q, c, plano[top]):
        cx, cy, w, h = (float(v) for v in b[qi])
        salida.append((min(max(cx - w / 2, 0.0), 1.0), min(max(cy - h / 2, 0.0), 1.0),
                       min(max(cx + w / 2, 0.0), 1.0), min(max(cy + h / 2, 0.0), 1.0), float(s), int(ids[ci])))
    return salida


# ── Inferencia completa sobre una sesión onnxruntime ────────────────────────────────────────────────────────────

def inferir(sesion, rgb: np.ndarray, umbral: float = 0.4, clase_fondo: int | None = -1) -> list[Caja]:
    """Corre la sesión con el preproceso y el posproceso que corresponden a su formato."""
    entrada = sesion.get_inputs()[0]
    nombres = [o.name for o in sesion.get_outputs()]
    fmt = formato(nombres)
    alto, ancho = tamano_entrada(entrada.shape)
    if fmt == "yolo":
        out = sesion.run(None, {entrada.name: preprocesar_yolo(rgb, alto, ancho)})
        return decodificar_yolo(out[0], umbral, alto=alto, ancho=ancho)
    out = dict(zip(nombres, sesion.run(None, {entrada.name: preprocesar_detr(rgb, alto, ancho)})))
    dets = out.get("dets", list(out.values())[0])
    labels = out.get("labels", list(out.values())[1])
    return decodificar_detr(dets[0], labels[0], umbral, clase_fondo)
