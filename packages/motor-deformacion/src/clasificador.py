"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — PUENTE CLASIFICACIÓN → ANÁLISIS
Conecta la salida del detector YOLO (apps/api/main.py → /detect, mismas
clases que CLASE_APU_MAP) con una plantilla de ElementoEstructural para
poder correr el análisis de deformación inmediatamente después de
clasificar un objeto en una foto.

Las dimensiones por defecto son solo un punto de partida razonable
(consistentes con el catálogo APU de Construdata) — deben reemplazarse por
las dimensiones reales medidas/especificadas del elemento cuando se
conozcan, porque la geometría real es el mayor factor de incertidumbre.
══════════════════════════════════════════════════════════════
"""
from typing import Optional

from .models import CondicionApoyo, ElementoEstructural, TipoElemento
from .geometry import seccion_rectangular
from .catalogue import MATERIALES

# clase_detectada → (tipo_elemento, fabricante_seccion, condicion_apoyo_tipica, longitud_defecto_m)
_PLANTILLAS: dict[str, dict] = {
    "columna":         {"tipo": TipoElemento.COLUMNA, "b": 0.40, "h": 0.30, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.EMPOTRADA_EMPOTRADA, "longitud": 3.0},
    "viga":            {"tipo": TipoElemento.VIGA,    "b": 0.30, "h": 0.40, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.SIMPLE, "longitud": 5.0},
    "placa_aligerada": {"tipo": TipoElemento.LOSA,     "b": 1.00, "h": 0.20, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.SIMPLE, "longitud": 4.0},
    "muro_bloque_15":  {"tipo": TipoElemento.MURO,     "b": 1.00, "h": 0.15, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.CANTILEVER, "longitud": 2.5},
    "muro_bloque_10":  {"tipo": TipoElemento.MURO,     "b": 1.00, "h": 0.10, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.CANTILEVER, "longitud": 2.5},
    "muro_concreto":   {"tipo": TipoElemento.MURO,     "b": 1.00, "h": 0.10, "material": "CONCRETO_21MPA", "apoyo": CondicionApoyo.CANTILEVER, "longitud": 2.5},
}


def elemento_desde_deteccion(
    clase: str, elemento_id: Optional[str] = None, longitud: Optional[float] = None,
    b: Optional[float] = None, h: Optional[float] = None,
) -> Optional[ElementoEstructural]:
    """
    Construye un ElementoEstructural de partida a partir de la clase que
    devolvió /detect. Retorna None si la clase no corresponde a un elemento
    analizable por deformación (p.ej. "excavacion", "acero_refuerzo" sueltos).
    """
    plantilla = _PLANTILLAS.get(clase)
    if plantilla is None:
        return None

    return ElementoEstructural(
        id=elemento_id or f"{clase}-auto",
        tipo_elemento=plantilla["tipo"],
        material=MATERIALES[plantilla["material"]],
        seccion=seccion_rectangular(b=b or plantilla["b"], h=h or plantilla["h"]),
        longitud=longitud or plantilla["longitud"],
        condicion_apoyo=plantilla["apoyo"],
    )


def estimar_longitud_desde_bbox(bbox_norm: list[float], alto_imagen_m: float, alto_imagen_px: int) -> float:
    """
    Aproxima la longitud real del elemento a partir de su bbox normalizada
    [x1,y1,x2,y2] y una escala de referencia conocida (p.ej. altura de piso
    a piso, o un objeto de tamaño conocido en la escena).

    LIMITACIÓN: una sola imagen monocular no tiene escala intrínseca — este
    valor es una aproximación de orden de magnitud y debe verificarse contra
    una medición real antes de usarse en un cálculo definitivo.
    """
    if alto_imagen_px <= 0 or alto_imagen_m <= 0:
        raise ValueError("Se requiere una escala de referencia válida (alto_imagen_m, alto_imagen_px)")
    x1, y1, x2, y2 = bbox_norm
    alto_bbox_px = (y2 - y1) * alto_imagen_px
    escala_m_por_px = alto_imagen_m / alto_imagen_px
    return round(alto_bbox_px * escala_m_por_px, 3)
