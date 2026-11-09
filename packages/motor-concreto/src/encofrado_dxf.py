"""Exportación DXF del encofrado de zapata troncopiramidal + pedestal (planta, elevación y paneles desarrollados).

Unidades: milímetros ($INSUNITS = 4). Capas: PLANTA, ELEVACION, PANELES, TEXTO.
Es un croquis de fabricación de PANELES (qué cortar y cuánto), no un plano estructural: no incluye refuerzo, ni cimbra/arriostramiento, ni
despiece por dimensión comercial de tablero. Los paneles del talud superior solo se generan si la pendiente supera el umbral
`ANGULO_SIN_CONTRAENCOFRADO_GRADOS` (supuesto constructivo sin fuente normativa, ver zapata_troncopiramidal.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import ezdxf

from .zapata_troncopiramidal import ANGULO_SIN_CONTRAENCOFRADO_GRADOS, ResultadoTroncopiramidal

SEPARACION_MM = 600.0
ALTURA_TEXTO_MM = 60.0


@dataclass(frozen=True)
class Panel:
    nombre: str
    cantidad: int
    forma: str          # "rectangulo" | "trapecio"
    ancho_mm: float     # lado mayor
    alto_mm: float      # alto (rectángulo) o longitud inclinada (trapecio)
    ancho_menor_mm: float | None = None

    @property
    def area_m2(self) -> float:
        a = (self.ancho_mm + (self.ancho_menor_mm if self.ancho_menor_mm is not None else self.ancho_mm)) / 2
        return self.cantidad * a * self.alto_mm / 1e6


def paneles(res: ResultadoTroncopiramidal, c_mm: float, h_pedestal_mm: float) -> list[Panel]:
    """Lista de paneles de encofrado (sin fondo de zapata, que va contra el suelo/solado)."""
    L, a, H = res.L_mm, (res.L_mm - c_mm) / 2, res.h_c_mm - res.h_e_mm
    out = [Panel("Zapata - cara lateral vertical", 4, "rectangulo", L, res.h_e_mm)]
    if H > 1e-9 and math.degrees(math.atan2(H, a)) > ANGULO_SIN_CONTRAENCOFRADO_GRADOS:
        out.append(Panel("Zapata - contraencofrado talud", 4, "trapecio", L, math.hypot(a, H), c_mm))
    if h_pedestal_mm > 0:
        out.append(Panel("Pedestal - cara", 4, "rectangulo", c_mm, h_pedestal_mm))
    return out


def _rect(msp, x, y, w, h, capa):
    msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={"layer": capa})


def _texto(msp, x, y, s, altura=ALTURA_TEXTO_MM):
    msp.add_text(s, height=altura, dxfattribs={"layer": "TEXTO", "insert": (x, y)})


def exportar_dxf(res: ResultadoTroncopiramidal, c_mm: float, h_pedestal_mm: float, ruta: str | Path, *, titulo: str = "Zapata troncopiramidal") -> dict:
    """Escribe el DXF y devuelve un resumen {paneles, area_total_m2, ruta}. Lanza ValueError si el diseño no cumple."""
    if not res.cumple:
        raise ValueError(f"el diseño no cumple ({res.motivo_fallo}); no se exporta encofrado")
    if h_pedestal_mm < 0 or c_mm <= 0:
        raise ValueError("c_mm > 0 y h_pedestal_mm >= 0")
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    for capa, color in (("PLANTA", 7), ("ELEVACION", 3), ("PANELES", 5), ("TEXTO", 2)):
        if capa not in doc.layers:
            doc.layers.add(capa, color=color)
    msp = doc.modelspace()
    L, c, h_c, h_e = res.L_mm, c_mm, res.h_c_mm, res.h_e_mm
    a = (L - c) / 2

    # Planta (origen en la esquina inferior izquierda de la zapata)
    _rect(msp, 0, 0, L, L, "PLANTA")
    _rect(msp, a, a, c, c, "PLANTA")
    for (x0, y0), (x1, y1) in (((0, 0), (a, a)), ((L, 0), (a + c, a)), ((L, L), (a + c, a + c)), ((0, L), (a, a + c))):
        msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": "PLANTA"})
    _texto(msp, 0, L + 100, f"{titulo} - PLANTA  L={L:.0f}  columna/pedestal {c:.0f}x{c:.0f}")

    # Elevación (debajo de la planta): perfil de la zapata + pedestal
    ey = -SEPARACION_MM - h_c - max(h_pedestal_mm, 0)
    perfil = [(0, ey), (L, ey), (L, ey + h_e), (a + c, ey + h_c), (a, ey + h_c), (0, ey + h_e)]
    msp.add_lwpolyline(perfil, close=True, dxfattribs={"layer": "ELEVACION"})
    if h_pedestal_mm > 0:
        _rect(msp, a, ey + h_c, c, h_pedestal_mm, "ELEVACION")
    _texto(msp, 0, ey - 150, f"ELEVACION  h_c={h_c:.0f}  h_e={h_e:.0f}  pedestal h={h_pedestal_mm:.0f}  talud={res.angulo_talud_grados:.1f} grados")

    # Paneles desarrollados (a la derecha)
    lista = paneles(res, c, h_pedestal_mm)
    x0, y0 = L + SEPARACION_MM, 0.0
    for p in lista:
        y = y0
        for i in range(p.cantidad):
            if p.forma == "rectangulo":
                _rect(msp, x0, y, p.ancho_mm, p.alto_mm, "PANELES")
            else:
                dx = (p.ancho_mm - (p.ancho_menor_mm or p.ancho_mm)) / 2
                msp.add_lwpolyline([(x0, y), (x0 + p.ancho_mm, y), (x0 + p.ancho_mm - dx, y + p.alto_mm), (x0 + dx, y + p.alto_mm)], close=True,
                                   dxfattribs={"layer": "PANELES"})
            _texto(msp, x0 + p.ancho_mm + 60, y + p.alto_mm / 2 - ALTURA_TEXTO_MM / 2, f"{p.nombre} #{i + 1}: {p.ancho_mm:.0f} x {p.alto_mm:.0f}" +
                   (f" (lado menor {p.ancho_menor_mm:.0f})" if p.ancho_menor_mm is not None else ""))
            y += p.alto_mm + 100
        y0 = y + 150
    total = sum(p.area_m2 for p in lista)
    _texto(msp, x0, y0, f"AREA TOTAL DE ENCOFRADO (sin fondo): {total:.2f} m2")
    _texto(msp, x0, y0 + 120, "Croquis de paneles; no incluye refuerzo ni cimbra. Hipotesis de investigacion.")
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(ruta)
    return {"ruta": str(ruta), "paneles": [(p.nombre, p.cantidad, round(p.area_m2, 3)) for p in lista], "area_total_m2": round(total, 3)}
