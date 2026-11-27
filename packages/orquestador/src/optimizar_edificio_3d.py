"""Edificio de pórticos 3D más barato que cumple (#275, F1): búsqueda sobre secciones con el diseño completo de F4 como juez.

Variables (rejilla declarada, no un óptimo continuo):
  h de viga ∈ ALTURAS_VIGA (todas las vigas iguales), b = máx(300; ⌈h/2⌉₅₀) mm;
  columna cuadrada c ∈ COLUMNAS en la mitad inferior y c − Δ (≥ 300) en la superior, Δ ∈ REDUCCIONES.
Algoritmo:
  1. Para cada (h, Δ), la menor c que cumple la deriva (A.6.4), por bisección: la deriva baja al crecer c (chequeo barato,
     sin diseño de elementos).
  2. Con esa c y hasta PASOS_EXTRA tamaños mayores, el diseño completo (vigas, columnas, columna fuerte–viga débil,
     biaxial); se queda el primero que cumple todo.
  3. El edificio elegido es el de menor costo directo (vigas + columnas) entre los (h, Δ) factibles.
El resultado es el óptimo de esta rejilla con esta heurística, no el diseño que haría un ingeniero.
"""
from __future__ import annotations

import dataclasses
import math
import time
from dataclasses import dataclass, field
from typing import Optional

from . import diseno_edificio_3d as de

ALTURAS_VIGA = tuple(range(400, 851, 50))
COLUMNAS = tuple(range(300, 1501, 50))
REDUCCIONES = (0, 150)
PASOS_EXTRA = 4


@dataclass
class ResultadoOptimizacion:
    mejor: Optional[de.InformeEdificio3D]
    evaluaciones_deriva: int = 0
    evaluaciones_diseno: int = 0
    segundos: float = 0.0
    candidatos: list[dict] = field(default_factory=list)
    motivo_sin_solucion: str = ""


def _secciones(n: int, c: float, delta: float, h: float):
    b = max(300.0, 50.0 * math.ceil(h / 2 / 50.0))
    abajo = math.ceil(n / 2)
    cols = tuple(c if i < abajo else max(300.0, c - delta) for i in range(n))
    return cols, tuple((b, float(h)) for _ in range(n))


def _uso_deriva(p: de.ProyectoEdificio3D) -> float:
    m = de.construir_modelo(p)
    s = de.analisis_sismico(p, m)
    d = de._s3.analizar_fhe(m.portico, m.pisos, s["x"]["Fs_deriva_kn"], s["y"]["Fs_deriva_kn"], "general", True)
    return float(d["uso_max_limite"])


def optimizar(base: de.ProyectoEdificio3D, alturas_viga: tuple = ALTURAS_VIGA) -> ResultadoOptimizacion:
    """`base` da geometría, cargas y sitio; sus secciones se ignoran. `alturas_viga` restringe la rejilla de h (p. ej. una
    sola h para comparar contra un diseño que solo crece en columnas, #333 H7)."""
    t0 = time.time()
    r = ResultadoOptimizacion(None)
    n = len(base.alturas_piso_m)
    mejor_costo = math.inf
    for h in alturas_viga:
        for delta in REDUCCIONES:
            b = _secciones(n, 300.0, 0.0, h)[1][0][0]
            validas = [c for c in COLUMNAS if c >= b and c - delta >= b]
            if not validas:
                continue

            def prueba(c):
                cols, vigas = _secciones(n, c, delta, h)
                r.evaluaciones_deriva += 1
                return _uso_deriva(dataclasses.replace(base, columnas_mm=cols, vigas_mm=vigas))
            lo, hi = 0, len(validas) - 1
            if prueba(validas[hi]) > 1.0:
                r.candidatos.append({"h": h, "delta": delta, "c": None, "motivo": "deriva con la columna máxima"})
                continue
            while lo < hi:
                mid = (lo + hi) // 2
                if prueba(validas[mid]) <= 1.0:
                    hi = mid
                else:
                    lo = mid + 1
            for c in validas[lo:lo + PASOS_EXTRA + 1]:
                cols, vigas = _secciones(n, c, delta, h)
                inf = de.disenar_edificio(dataclasses.replace(base, columnas_mm=cols, vigas_mm=vigas))
                r.evaluaciones_diseno += 1
                if inf.cumple:
                    costo = inf.cantidades["costo_cop"]
                    r.candidatos.append({"h": h, "delta": delta, "c": c, "costo_cop": costo})
                    if costo < mejor_costo:
                        mejor_costo, r.mejor = costo, inf
                    break
            else:
                r.candidatos.append({"h": h, "delta": delta, "c": None, "motivo": "diseño de elementos (" + "; ".join(inf.fallas[:2]) + ")"})
    if r.mejor is None:
        r.motivo_sin_solucion = "ninguna combinación de la rejilla cumple: " + "; ".join(
            sorted({c["motivo"].split(" (")[0] for c in r.candidatos if c.get("motivo")}))
    r.segundos = time.time() - t0
    return r
