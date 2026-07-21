"""
InfracortexVisionSensor — Inspección de estribos con YOLO
Valida separación real contra NSR-10 C.21.4.4
Unidades: px (imagen), mm (espaciado real)
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import cv2


@dataclass(frozen=True)
class DeteccionEstribo:
    id:           int
    y_centro_px:  float
    x1_px:        float
    x2_px:        float
    confianza:    float


@dataclass(frozen=True)
class ResultadoEspaciado:
    par:            str
    separacion_px:  float
    separacion_mm:  float
    cumple_nsr10:   bool
    s_max_mm:       float


class InfracortexVisionSensor:
    """
    Sensor óptico Edge-AI para inspección de armadura en obra.

    En producción: inferencia con YOLOv8 entrenado en dataset civil
    (dataset rebar/stirrup en Roboflow).
    En desarrollo: acepta posiciones Y de estribos ya conocidas
    (imagen sintética / ground truth anotado).
    """

    def __init__(
        self,
        s_max_diseno_mm: float = 75.0,
        escala_mm_por_px: float = 1.0,
    ) -> None:
        self.s_max_mm = s_max_diseno_mm
        self.escala   = escala_mm_por_px

    def detectar_estribos(
        self,
        imagen: np.ndarray,
        posiciones_y_px: list[float],
    ) -> list[DeteccionEstribo]:
        """
        Acepta posiciones Y en píxeles (ground truth o inferencia YOLO).
        """
        w = imagen.shape[1]
        return [
            DeteccionEstribo(
                id=i,
                y_centro_px=float(y),
                x1_px=10.0,
                x2_px=float(w - 10),
                confianza=0.92,
            )
            for i, y in enumerate(posiciones_y_px)
        ]

    def calcular_separaciones(
        self,
        detecciones: list[DeteccionEstribo],
    ) -> list[ResultadoEspaciado]:
        ordenados = sorted(detecciones, key=lambda d: d.y_centro_px)
        resultados = []
        for i in range(len(ordenados) - 1):
            dy_px = abs(ordenados[i + 1].y_centro_px - ordenados[i].y_centro_px)
            dy_mm = dy_px * self.escala
            resultados.append(
                ResultadoEspaciado(
                    par=f"E{i}–E{i+1}",
                    separacion_px=dy_px,
                    separacion_mm=round(dy_mm, 1),
                    cumple_nsr10=dy_mm <= self.s_max_mm,
                    s_max_mm=self.s_max_mm,
                )
            )
        return resultados

    def analizar(
        self,
        imagen: np.ndarray,
        posiciones_y_px: list[float],
    ) -> tuple[list[DeteccionEstribo], list[ResultadoEspaciado]]:
        dets = self.detectar_estribos(imagen, posiciones_y_px)
        seps = self.calcular_separaciones(dets)
        return dets, seps

    def generar_imagen_anotada(
        self,
        imagen: np.ndarray,
        detecciones: list[DeteccionEstribo],
        separaciones: list[ResultadoEspaciado],
    ) -> np.ndarray:
        img = imagen.copy()
        COLOR_OK    = (0, 200, 0)
        COLOR_FALLA = (0, 0, 220)
        ordenados   = sorted(detecciones, key=lambda d: d.y_centro_px)

        for det in detecciones:
            y = int(det.y_centro_px)
            cv2.line(img, (int(det.x1_px), y), (int(det.x2_px), y), (255, 200, 0), 2)
            cv2.putText(img, f"E{det.id}", (5, y - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)

        cx = imagen.shape[1] - 140
        for i, sep in enumerate(separaciones):
            y1 = int(ordenados[i].y_centro_px)
            y2 = int(ordenados[i + 1].y_centro_px)
            color = COLOR_OK if sep.cumple_nsr10 else COLOR_FALLA
            cy    = (y1 + y2) // 2
            cv2.line(img, (cx, y1), (cx, y2), color, 1)
            estado = "OK" if sep.cumple_nsr10 else "FALLA"
            cv2.putText(img, f"{sep.separacion_mm:.0f}mm {estado}", (cx + 4, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)

        cv2.putText(img, "INFRACORTEX · NSR-10 C.21.4.4", (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (240, 240, 240), 1)
        return img
