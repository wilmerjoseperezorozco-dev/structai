"""Despiece 1D de barras a nivel de proyecto: traslapos + mínimo de longitud comprada (ILP) por diámetro.

Para cada diámetro se reúnen todas las piezas de todos los elementos y se resuelve un problema de corte unidimensional:
minimizar la longitud total comprada con longitudes comerciales dadas (el precio es proporcional a la longitud, así que minimizar
longitud = minimizar kg y COP). Formulación por patrones (todos los patrones maximales de cada longitud comercial) + milp de scipy.

HIPÓTESIS declaradas (no verificadas contra la norma ni contra el mercado):
- las longitudes comerciales las aporta quien llama (6, 9 y 12 m son valores usuales, no fijados aquí);
- longitud de traslapo = `traslapo_diametros` × db (40 por defecto; la norma exige calcularla según C.12.15 y la clase de empalme);
- las piezas se redondean hacia arriba al centímetro; no se modelan ganchos de despiece ni mermas de obra.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

from .metricas_refuerzo import corte_1d
from .viga import AREA_MM2, DIAMETRO_MM

DENSIDAD_ACERO_KG_M3 = 7850.0
RESOLUCION_M = 0.01
MAX_PATRONES = 200_000


@dataclass(frozen=True)
class ResultadoDiametro:
    dia: str
    longitud_util_m: float
    comprada_ffd_m: float
    comprada_ilp_m: float
    barras_ilp: dict[float, int]       # longitud comercial -> cantidad
    optimo_probado: bool

    @property
    def desperdicio_ffd(self) -> float:
        return 1.0 - self.longitud_util_m / self.comprada_ffd_m

    @property
    def desperdicio_ilp(self) -> float:
        return 1.0 - self.longitud_util_m / self.comprada_ilp_m

    @property
    def kg_ahorrados(self) -> float:
        return (self.comprada_ffd_m - self.comprada_ilp_m) * AREA_MM2[self.dia] * 1e-6 * DENSIDAD_ACERO_KG_M3


def dividir_con_traslapo(largo_m: float, max_barra_m: float, traslapo_m: float) -> list[float]:
    """Piezas necesarias para una barra continua de `largo_m`; cada empalme suma un traslapo. Sin empalme devuelve [largo]."""
    if largo_m <= 0 or max_barra_m <= traslapo_m:
        raise ValueError("largo positivo y barra máxima mayor que el traslapo")
    if largo_m <= max_barra_m + 1e-9:
        return [largo_m]
    k = math.ceil((largo_m - traslapo_m) / (max_barra_m - traslapo_m) - 1e-9)
    total = largo_m + (k - 1) * traslapo_m
    return [max_barra_m] * (k - 1) + [total - (k - 1) * max_barra_m]


def _patrones(longitudes: Sequence[int], cap: int, maxima: list[int]) -> list[tuple[int, ...]]:
    """Patrones maximales (cuántas piezas de cada longitud caben en `cap`, sin exceder la demanda)."""
    n, res = len(longitudes), []

    def rec(i: int, resto: int, actual: list[int]) -> None:
        if len(res) > MAX_PATRONES:
            raise ValueError("demasiados patrones: agrupar longitudes (aumentar RESOLUCION_M)")
        if i == n:
            if all(resto < l for l, c, m in zip(longitudes, actual, maxima) if c < m):
                res.append(tuple(actual))
            return
        for c in range(min(resto // longitudes[i], maxima[i]), -1, -1):
            actual.append(c)
            rec(i + 1, resto - c * longitudes[i], actual)
            actual.pop()

    rec(0, cap, [])
    return res


def resolver_ilp(piezas_m: Iterable[float], comerciales_m: Sequence[float]) -> tuple[dict[float, int], bool]:
    """({longitud comercial: cantidad}, óptimo_probado) con mínima longitud comprada."""
    unidades = lambda x: int(math.ceil(x / RESOLUCION_M - 1e-9))        # noqa: E731
    demanda = Counter(unidades(p) for p in piezas_m)
    comerc = sorted({unidades(c) for c in comerciales_m})
    if max(demanda) > comerc[-1]:
        raise ValueError("pieza más larga que la barra comercial máxima; usar dividir_con_traslapo")
    longs = sorted(demanda, reverse=True)
    dem = [demanda[l] for l in longs]
    cols, costo, origen = [], [], []
    for cap in comerc:
        for p in _patrones(longs, cap, dem):
            if any(p):
                cols.append(p); costo.append(cap); origen.append(cap)
    a = np.array(cols, dtype=float).T
    res = milp(c=np.array(costo, dtype=float), constraints=LinearConstraint(a, lb=np.array(dem, dtype=float)),
               integrality=np.ones(len(cols)), bounds=Bounds(0, np.inf))
    if not res.success:
        raise RuntimeError(f"ILP sin solución: {res.message}")
    x = np.rint(res.x).astype(int)
    barras: Counter = Counter()
    for xi, cap in zip(x, origen):
        if xi:
            barras[cap * RESOLUCION_M] += int(xi)
    return {round(k, 2): v for k, v in sorted(barras.items())}, res.status == 0


def despiece_por_diametro(barras: Iterable[tuple[str, float]], comerciales_m: Sequence[float],
                          traslapo_diametros: float = 40.0) -> list[ResultadoDiametro]:
    """`barras` = (diámetro "4".."8", longitud continua en m) de todos los elementos del proyecto."""
    por_dia: dict[str, list[float]] = {}
    maxb = max(comerciales_m)
    for dia, largo in barras:
        piezas = dividir_con_traslapo(largo, maxb, traslapo_diametros * DIAMETRO_MM[dia] / 1000.0)
        por_dia.setdefault(dia, []).extend(piezas)
    salida = []
    for dia in sorted(por_dia):
        p = por_dia[dia]
        ffd = corte_1d(p, comerciales_m)
        barras_ilp, ok = resolver_ilp(p, comerciales_m)
        comprada = sum(l * n for l, n in barras_ilp.items())
        salida.append(ResultadoDiametro(dia, sum(p), ffd.longitud_comprada_m, comprada, barras_ilp, ok))
    return salida
