"""Métricas de calidad del detallado de refuerzo (viga) para comparar alternativas y alimentar un optimizador.

Métricas puras, sin estado:
- eficiencia de acero η = As_prov / As_req (flexión, sección rectangular simplemente armada);
- separación libre entre barras frente a max(db, 25 mm, 4/3·TMN) (C.7.6.1 y C.3.3.2: el TMN no excede 3/4 del espaciamiento libre);
- holgura de confinamiento sísmico respecto del límite normativo de C.21.5.3.2;
- desperdicio de corte 1D (primer ajuste decreciente) con longitudes comerciales declaradas por quien llama;
- costo de mano de obra con una tarifa por kg suministrada por quien llama (no se inventa un valor por defecto).
Hipótesis: el 4/3·TMN es la lectura de C.3.3.2 (TMN ≤ 3/4 del libre); el texto del numeral en el corpus llega truncado, verificar en la fuente.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .diseno_viga import DisenoViga
from .viga import AREA_MM2, DIAMETRO_MM

PHI_FLEXION = 0.90
FACTOR_TMN = 4.0 / 3.0
LIBRE_MIN_MM = 25.0


def as_requerida(mu_knm: float, b: float, d: float, fc: float, fy: float) -> float:
    """Área de acero (mm²) que da φMn = Mu en sección rectangular simplemente armada; inf si no existe solución."""
    if mu_knm <= 0:
        return 0.0
    k = fy * fy / (1.7 * fc * b)
    disc = (fy * d) ** 2 - 4.0 * k * mu_knm * 1e6 / PHI_FLEXION
    if disc < 0:
        return math.inf
    return (fy * d - math.sqrt(disc)) / (2.0 * k)


def eficiencia_acero(as_prov_mm2: float, as_req_mm2: float) -> float:
    """η = As_prov / As_req (≥ 1 si cumple por flexión; cercano a 1 = detallado ajustado)."""
    if as_req_mm2 <= 0:
        return math.inf
    return as_prov_mm2 / as_req_mm2


def libre_exigido_mm(db_mm: float, tmn_mm: float | None = None) -> float:
    """max(db, 25 mm, 4/3·TMN); sin TMN se reduce a la regla que hoy usa el motor."""
    base = max(db_mm, LIBRE_MIN_MM)
    return base if tmn_mm is None else max(base, FACTOR_TMN * tmn_mm)


def libre_disponible_mm(b: float, n: int, dia: str, estribo: str, rec: float = 40.0) -> float:
    """Separación libre entre barras de una capa."""
    if n < 2:
        return math.inf
    ancho = b - 2.0 * (rec + DIAMETRO_MM[estribo])
    return (ancho - n * DIAMETRO_MM[dia]) / (n - 1)


def holgura_libre(d: DisenoViga, tmn_mm: float | None, rec: float = 40.0) -> float:
    """Mínimo de (libre disponible − exigido) en mm entre capa superior e inferior; negativo = no cumple con ese TMN."""
    exigido = libre_exigido_mm(DIAMETRO_MM[d.dia], tmn_mm)
    return min(libre_disponible_mm(d.b, n, d.dia, d.estribo_dia, rec) - exigido for n in (d.n_sup, d.n_inf))


def eficiencia_confinamiento(s_conf: float, d: float, dia: str, estribo: str) -> float:
    """s_conf / límite de C.21.5.3.2 = min(d/4, 8db, 24·d_est, 300). ≤ 1 cumple; cerca de 1 = aprovecha el límite sin pasarse."""
    limite = min(d / 4.0, 8.0 * DIAMETRO_MM[dia], 24.0 * DIAMETRO_MM[estribo], 300.0)
    return s_conf / limite


@dataclass(frozen=True)
class ResultadoCorte:
    barras_compradas: int
    longitud_comprada_m: float
    longitud_util_m: float

    @property
    def desperdicio(self) -> float:
        return 1.0 - self.longitud_util_m / self.longitud_comprada_m if self.longitud_comprada_m else 0.0


def corte_1d(piezas_m: Sequence[float], longitudes_comerciales_m: Sequence[float]) -> ResultadoCorte:
    """Primer ajuste decreciente. Cada barra nueva usa la longitud comercial más corta que aloja la pieza más larga pendiente.

    Es una cota superior del desperdicio óptimo (el 1D-CSP exacto se resuelve con ILP; ver issue de despiece a nivel de proyecto).
    """
    comerciales = sorted(longitudes_comerciales_m)
    mayor = comerciales[-1]
    if any(p <= 0 or p > mayor + 1e-9 for p in piezas_m):
        raise ValueError("pieza no positiva o más larga que la barra comercial máxima (requiere traslapo, no modelado)")
    barras: list[list[float]] = []          # [capacidad, restante]
    for p in sorted(piezas_m, reverse=True):
        for b in barras:
            if b[1] + 1e-9 >= p:
                b[1] -= p
                break
        else:
            cap = next(c for c in comerciales if c + 1e-9 >= p)
            barras.append([cap, cap - p])
    return ResultadoCorte(len(barras), sum(b[0] for b in barras), sum(piezas_m))


def costo_mano_obra(acero_kg: float, n_estribos: int, tarifa_cop_kg: float, tarifa_cop_estribo: float = 0.0) -> float:
    """COP de figuración y amarre: tarifa por kg instalado más, opcional, por estribo. Las tarifas las aporta quien llama (INVIAS/ICOCED)."""
    if tarifa_cop_kg < 0 or tarifa_cop_estribo < 0:
        raise ValueError("tarifas no negativas")
    return acero_kg * tarifa_cop_kg + n_estribos * tarifa_cop_estribo


def area_longitudinal_mm2(d: DisenoViga) -> tuple[float, float]:
    """(As superior, As inferior) provista."""
    a = AREA_MM2[d.dia]
    return d.n_sup * a, d.n_inf * a
