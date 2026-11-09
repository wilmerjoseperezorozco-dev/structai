"""Frontera de Pareto costo APU vs. kg CO₂e de un caso de muro: se barre el precio sombra del carbono λ (COP por kg CO₂e) con el optimizador de referencia."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .muro_optimizador import CasoMuro, Solucion, optimizar_todas

LAMBDAS = (0.0, 50.0, 150.0, 400.0, 1000.0, 2500.0, 6000.0, 15000.0)


@dataclass(frozen=True)
class PuntoPareto:
    lam: float
    tipologia: str
    costo_cop_m: float
    co2_kg_m: float
    solucion: Solucion


def frontera(caso: CasoMuro, lambdas=LAMBDAS) -> list[PuntoPareto]:
    """Puntos no dominados (ordenados por costo creciente): para cada λ, la mejor tipología por objetivo costo + λ·CO₂."""
    pts: list[PuntoPareto] = []
    for lam in lambdas:
        sols = optimizar_todas(replace(caso, lam_co2=lam), perfiles=("lineal",))
        cand = [s for k, s in sols.items() if k != "tradicional" and s is not None]
        if cand:
            s = min(cand, key=lambda x: x.objetivo)
            pts.append(PuntoPareto(lam, s.tipologia, s.diseno.costo_cop_m, s.diseno.co2_kg_m, s))
    nd = [p for p in pts if not any(q.costo_cop_m <= p.costo_cop_m and q.co2_kg_m <= p.co2_kg_m and (q.costo_cop_m < p.costo_cop_m or q.co2_kg_m < p.co2_kg_m) for q in pts)]
    vistos: set[tuple[int, int]] = set()
    unicos = []
    for p in sorted(nd, key=lambda x: x.costo_cop_m):
        k = (round(p.costo_cop_m), round(p.co2_kg_m * 100))
        if k not in vistos:
            vistos.add(k)
            unicos.append(p)
    return unicos


def elegir(puntos: list[PuntoPareto]) -> dict[str, PuntoPareto]:
    """«minimo_costo», «minima_huella» y «equilibrio» (rodilla: mayor distancia normalizada a la recta que une los extremos)."""
    if not puntos:
        return {}
    a, b = puntos[0], puntos[-1]
    out = {"minimo_costo": a, "minima_huella": b}
    if len(puntos) < 3:
        out["equilibrio"] = a
        return out
    dc, de = (b.costo_cop_m - a.costo_cop_m) or 1.0, (b.co2_kg_m - a.co2_kg_m) or 1.0

    def dist(p: PuntoPareto) -> float:
        x, y = (p.costo_cop_m - a.costo_cop_m) / dc, (p.co2_kg_m - a.co2_kg_m) / de
        return abs(x + y - 1.0) / 2 ** 0.5          # distancia a la recta x + y = 1 (extremos normalizados)

    out["equilibrio"] = max(puntos[1:-1], key=dist)
    return out
