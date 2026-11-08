"""Combinaciones de carga NSR-10 (B.2.4.2) y envolventes a lo largo de los elementos.

Casos esperados: "D" (muerta), "L" (viva), "E" (sismo reducido, sentido +x). El sentido contrario de E se obtiene con factor -1.
Combinaciones del método de resistencia usadas (verificadas en el corpus: B.2.4-2, B.2.4-5, B.2.4-7; B.2.4-1 es 1.4D):
  1.4D · 1.2D+1.6L · 1.2D+1.0L±1.0E · 0.9D±1.0E
Se omiten viento, lluvia, empuje de suelos y fluidos (no modelados).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .portico import Portico, ResultadoCaso

COMBINACIONES_NSR10 = {
    "1.4D": {"D": 1.4},
    "1.2D+1.6L": {"D": 1.2, "L": 1.6},
    "1.2D+1.0L+1.0E": {"D": 1.2, "L": 1.0, "E": 1.0},
    "1.2D+1.0L-1.0E": {"D": 1.2, "L": 1.0, "E": -1.0},
    "0.9D+1.0E": {"D": 0.9, "E": 1.0},
    "0.9D-1.0E": {"D": 0.9, "E": -1.0},
}


@dataclass(frozen=True)
class Envolvente:
    x: np.ndarray            # posiciones (m) desde el nodo i
    M_max: np.ndarray        # momento positivo máximo (sagging) en cada x
    M_min: np.ndarray        # momento mínimo (negativo, hogging)
    V_max: np.ndarray
    V_min: np.ndarray
    combo_M_max: list[str]
    combo_M_min: list[str]
    combo_V: list[str]       # combinación que gobierna |V| en cada x

    def en(self, x: float) -> dict[str, float]:
        """Valores de la envolvente en la posición x (interpolación lineal)."""
        return {"M_max": float(np.interp(x, self.x, self.M_max)), "M_min": float(np.interp(x, self.x, self.M_min)),
                "V_max": float(np.interp(x, self.x, self.V_max)), "V_min": float(np.interp(x, self.x, self.V_min))}


def envolvente(modelo: Portico, resultados: dict[str, ResultadoCaso], idx: int,
               combinaciones: dict[str, dict[str, float]] = COMBINACIONES_NSR10, n: int = 41,
               posiciones_extra: tuple[float, ...] = ()) -> Envolvente:
    """Envolvente de M y V del elemento `idx` sobre todas las combinaciones que solo usan casos disponibles."""
    L = modelo.longitud(modelo.elementos[idx])
    xs = np.unique(np.concatenate([np.linspace(0.0, L, n), np.clip(np.array(posiciones_extra, dtype=float), 0.0, L)]))
    por_caso = {c: modelo.diagrama(r, idx, xs) for c, r in resultados.items()}
    M, V, nombres = [], [], []
    for nombre, factores in combinaciones.items():
        if any(c not in por_caso for c in factores):
            continue
        M.append(sum(f * por_caso[c]["M"] for c, f in factores.items()))
        V.append(sum(f * por_caso[c]["V"] for c, f in factores.items()))
        nombres.append(nombre)
    if not M:
        raise ValueError("Ninguna combinación es aplicable a los casos entregados")
    M, V = np.array(M), np.array(V)
    iabsV = np.argmax(np.abs(V), axis=0)
    return Envolvente(xs, M.max(axis=0), M.min(axis=0), V.max(axis=0), V.min(axis=0),
                      [nombres[i] for i in M.argmax(axis=0)], [nombres[i] for i in M.argmin(axis=0)],
                      [nombres[i] for i in iabsV])
