"""Muestreo de escenarios de precio para el diseño generativo.

Los precios son entradas con incertidumbre, no etiquetas que el modelo aprenda. Cada escenario multiplica los precios base de `Economia`
por exp(sigma·z), lognormal que conserva la mediana. Acero y cordón comparten el mismo z (el cordón es factor × p_acero).
Los sigma salen de data/precios_elementos/distribuciones_precios.json (scripts/precios/calibrar_distribuciones.py): localización (rango
intercuartil entre 140 provincias INVIAS), fuente (contratos locales), tiempo (ICOCED Barranquilla) y, solo para el anclaje, un
sigma de especificación SUPUESTO (receta en roca, uso en suelo).
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from .economia_concreto import Economia

RUTA_JSON = Path(__file__).resolve().parents[3] / "data" / "precios_elementos" / "distribuciones_precios.json"
SIGMAS_POR_DEFECTO = {"acero": 0.1198, "concreto": 0.0904, "perforacion_anclaje": 0.2825}   # copia de la calibración 2026-11


def cargar_sigmas(ruta: Path | None = None) -> dict[str, float]:
    """Sigma total por familia; si el JSON no existe (instalación sin datos) usa la copia de la calibración."""
    r = ruta or RUTA_JSON
    if not r.exists():
        return dict(SIGMAS_POR_DEFECTO)
    familias = json.loads(r.read_text(encoding="utf-8"))["familias"]
    return {k: float(v["sigma_total"]) for k, v in familias.items()}


def muestrear(base: Economia, rng: np.random.Generator, sigmas: dict[str, float] | None = None) -> Economia:
    """Un escenario de precios: copia de `base` con acero, concreto y perforación perturbados (lognormal, mediana conservada)."""
    s = sigmas or cargar_sigmas()
    z = rng.standard_normal(3)
    return replace(base,
                   p_acero=base.p_acero * float(np.exp(s["acero"] * z[0])),
                   mult_concreto=base.mult_concreto * float(np.exp(s["concreto"] * z[1])),
                   p_perforacion_m=base.p_perforacion_m * float(np.exp(s["perforacion_anclaje"] * z[2])))
