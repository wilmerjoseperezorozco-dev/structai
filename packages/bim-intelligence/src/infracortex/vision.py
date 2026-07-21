"""
Motor de Visión Edge-AI – InfracortexVisionSensor
==================================================
Pipeline: Foto de obra → YOLO → bounding boxes → separación real (mm) → NSR-10

Unidades: px (imagen), mm (espaciado real)
Referencia: NSR-10 Título C artículo C.21.4.4 (zona de confinamiento)
"""

import math
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Estructura de detección
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DeteccionEstribo:
    id:         int
    y_centro_px: float   # coordenada vertical en píxeles
    x1_px:      float
    x2_px:      float
    confianza:  float


@dataclass(frozen=True)
class ResultadoEspaciado:
    separacion_px:  float
    separacion_mm:  float
    cumple_nsr10:   bool
    s_max_diseno_mm: float


# ---------------------------------------------------------------------------
# Calibración geométrica (pixels → mm)
# ---------------------------------------------------------------------------
def calibrar_escala(
    longitud_referencia_px: float,
    longitud_referencia_mm: float,
) -> float:
    """
    Calcula el factor de escala mm/px a partir de un objeto de referencia
    conocido en la imagen (ej. diámetro de barra longitudinal Ø25mm visible).
    """
    return longitud_referencia_mm / longitud_referencia_px


# ---------------------------------------------------------------------------
# Cálculo de separación entre estribos detectados
# ---------------------------------------------------------------------------
def calcular_separaciones(
    detecciones: list[DeteccionEstribo],
    escala_mm_por_px: float,
    s_max_diseno_mm: float,
) -> list[ResultadoEspaciado]:
    """
    Ordena los estribos por posición Y y calcula la separación real entre
    cada par consecutivo. Compara contra s_max del diseño NSR-10.
    """
    ordenados = sorted(detecciones, key=lambda d: d.y_centro_px)
    resultados = []

    for i in range(len(ordenados) - 1):
        dy_px = abs(ordenados[i + 1].y_centro_px - ordenados[i].y_centro_px)
        dy_mm = dy_px * escala_mm_por_px
        cumple = dy_mm <= s_max_diseno_mm
        resultados.append(
            ResultadoEspaciado(
                separacion_px=dy_px,
                separacion_mm=dy_mm,
                cumple_nsr10=cumple,
                s_max_diseno_mm=s_max_diseno_mm,
            )
        )
    return resultados


# ---------------------------------------------------------------------------
# Sensor principal
# ---------------------------------------------------------------------------
class InfracortexVisionSensor:
    """
    Sensor óptico Edge-AI.

    En producción: alimentado con frames de cámara IP / drone / 360°.
    En desarrollo: acepta imagen sintética o foto real de obra.

    El modelo YOLO usado aquí es el base (yolov8n). Para detección
    real de estribos se requiere fine-tuning con dataset civil anotado
    (ver: roboflow.com/explore/datasets?q=rebar+stirrup).
    """

    def __init__(
        self,
        modelo_path: str = "yolov8n.pt",
        s_max_diseno_mm: float = 75.0,
        escala_mm_por_px: float = None,
        ref_px: float = None,
        ref_mm: float = None,
    ):
        self.modelo        = YOLO(modelo_path)
        self.s_max_mm      = s_max_diseno_mm

        if escala_mm_por_px is not None:
            self.escala = escala_mm_por_px
        elif ref_px and ref_mm:
            self.escala = calibrar_escala(ref_px, ref_mm)
        else:
            # Calibración por defecto: imagen sintética 600px de ancho = 600mm
            self.escala = 1.0

    def detectar_estribos_sinteticos(
        self,
        imagen: np.ndarray,
        posiciones_y_px: list[float],
    ) -> list[DeteccionEstribo]:
        """
        Simulación de detecciones YOLO para el prototipo.
        Entrada: posiciones Y conocidas (imagen sintética con estribos dibujados).
        En producción: reemplazar por self.modelo(imagen)[0].boxes.xyxy
        """
        detecciones = []
        w = imagen.shape[1]
        for i, y in enumerate(posiciones_y_px):
            detecciones.append(
                DeteccionEstribo(
                    id=i,
                    y_centro_px=y,
                    x1_px=10.0,
                    x2_px=float(w - 10),
                    confianza=0.92,
                )
            )
        return detecciones

    def analizar_imagen(
        self,
        imagen: np.ndarray,
        posiciones_y_px: list[float],
    ) -> tuple[list[DeteccionEstribo], list[ResultadoEspaciado]]:
        detecciones = self.detectar_estribos_sinteticos(imagen, posiciones_y_px)
        separaciones = calcular_separaciones(detecciones, self.escala, self.s_max_mm)
        return detecciones, separaciones

    def generar_reporte_visual(
        self,
        imagen: np.ndarray,
        detecciones: list[DeteccionEstribo],
        separaciones: list[ResultadoEspaciado],
        ruta_salida: str = "inspeccion_nsr10.png",
    ) -> None:
        """
        Dibuja las detecciones y el veredicto NSR-10 sobre la imagen.
        Guarda el resultado en disco.
        """
        img = imagen.copy()
        COLOR_OK    = (0, 200, 0)    # verde
        COLOR_FALLA = (0, 0, 220)    # rojo

        # Dibujar cada estribo detectado
        for det in detecciones:
            y = int(det.y_centro_px)
            cv2.line(img, (int(det.x1_px), y), (int(det.x2_px), y), (255, 200, 0), 2)
            cv2.putText(img, f"E{det.id}", (5, y - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)

        # Dibujar cotas entre pares y veredicto
        ordenados = sorted(detecciones, key=lambda d: d.y_centro_px)
        for i, sep in enumerate(separaciones):
            y1 = int(ordenados[i].y_centro_px)
            y2 = int(ordenados[i + 1].y_centro_px)
            color = COLOR_OK if sep.cumple_nsr10 else COLOR_FALLA
            estado = "OK" if sep.cumple_nsr10 else "FALLA"
            cx = imagen.shape[1] - 130
            cv2.line(img, (cx, y1), (cx, y2), color, 1)
            cy = (y1 + y2) // 2
            cv2.putText(img, f"{sep.separacion_mm:.0f}mm {estado}", (cx + 5, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)

        # Encabezado
        cv2.putText(img, "INFRACORTEX VISION – NSR-10 C.21.4.4", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1)

        cv2.imwrite(ruta_salida, img)
        print(f"Imagen de inspección guardada: {ruta_salida}")
