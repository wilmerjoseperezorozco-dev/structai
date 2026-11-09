"""Balance de tierras por programación lineal (transporte con capacidades). Todos los volúmenes están en m³ EN BANCO y los rellenos ya expresados
como volumen en banco equivalente (la conversión por compactación la hace quien llama: depende del material y del ensayo Proctor del proyecto).

Variables: x[i,j] corte i -> relleno j; y[i,l] corte i -> botadero l; z[k,j] préstamo k -> relleno j.
Restricciones: todo corte se coloca (x + y = V_i); solo la fracción aprovechable del corte puede ir a rellenos (sum_j x[i,j] <= r_i V_i);
cada relleno se cubre (sum_i x + sum_k z = D_j); capacidades de botaderos y préstamos.
Costo: costo_cop_m3_km * distancia por cada m³ movido + tarifa de botadero + precio de préstamo. El costo por m³-km, el esponjamiento y el
rendimiento son datos del usuario (sin valores por defecto). Combustible: gal/m³-km = 2 * (1+esponjamiento) / (capacidad_suelta_m3 * km_gal)
(viaje cargado de ida y vacío de retorno al mismo rendimiento, supuesto conservador de `flota_construccion`)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class Problema:
    cortes_m3: tuple[float, ...]
    aprovechable: tuple[float, ...]                 # fracción 0-1 del corte i que sirve para relleno
    demandas_m3: tuple[float, ...]
    d_corte_relleno_km: tuple[tuple[float, ...], ...]
    botaderos_cap_m3: tuple[float, ...]
    d_corte_botadero_km: tuple[tuple[float, ...], ...]
    tarifa_botadero_cop_m3: tuple[float, ...]
    prestamos_cap_m3: tuple[float, ...]
    d_prestamo_relleno_km: tuple[tuple[float, ...], ...]
    precio_prestamo_cop_m3: tuple[float, ...]
    costo_cop_m3_km: float


@dataclass(frozen=True)
class Plan:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    costo_cop: float
    reutilizacion_pct: float
    m3_km: float


def _validar(p: Problema) -> None:
    ni, nj, nl, nk = len(p.cortes_m3), len(p.demandas_m3), len(p.botaderos_cap_m3), len(p.prestamos_cap_m3)
    if min(p.cortes_m3, default=0) < 0 or min(p.demandas_m3, default=0) < 0 or p.costo_cop_m3_km < 0 or not all(0 <= r <= 1 for r in p.aprovechable):
        raise ValueError("volúmenes y costos >= 0; aprovechable en [0, 1]")
    if len(p.aprovechable) != ni or np.shape(p.d_corte_relleno_km) != (ni, nj) or np.shape(p.d_corte_botadero_km) != (ni, nl) or np.shape(p.d_prestamo_relleno_km) != (nk, nj):
        raise ValueError("dimensiones de distancias inconsistentes")
    if len(p.tarifa_botadero_cop_m3) != nl or len(p.precio_prestamo_cop_m3) != nk:
        raise ValueError("tarifas/precios inconsistentes con botaderos/préstamos")
    todas = np.concatenate([np.ravel(p.d_corte_relleno_km), np.ravel(p.d_corte_botadero_km), np.ravel(p.d_prestamo_relleno_km),
                            p.tarifa_botadero_cop_m3, p.precio_prestamo_cop_m3, p.botaderos_cap_m3, p.prestamos_cap_m3]).astype(float)
    if (todas < 0).any() or not np.isfinite(todas).all():
        raise ValueError("distancias, tarifas, precios y capacidades deben ser finitos y >= 0 (use un valor grande para 'sin límite')")


def _resolver(p: Problema, c: np.ndarray, extra_ub=None):
    ni, nj, nl, nk = len(p.cortes_m3), len(p.demandas_m3), len(p.botaderos_cap_m3), len(p.prestamos_cap_m3)
    nx, ny, nz = ni * nj, ni * nl, nk * nj
    n = nx + ny + nz

    def ix(i, j): return i * nj + j
    def iy(i, l): return nx + i * nl + l
    def iz(k, j): return nx + ny + k * nj + j

    a_eq, b_eq, a_ub, b_ub = [], [], [], []
    for i in range(ni):
        f = np.zeros(n)
        f[[ix(i, j) for j in range(nj)]] = 1
        f[[iy(i, l) for l in range(nl)]] = 1
        a_eq.append(f)
        b_eq.append(p.cortes_m3[i])
        g = np.zeros(n)
        g[[ix(i, j) for j in range(nj)]] = 1
        a_ub.append(g)
        b_ub.append(p.aprovechable[i] * p.cortes_m3[i])
    for j in range(nj):
        f = np.zeros(n)
        f[[ix(i, j) for i in range(ni)]] = 1
        f[[iz(k, j) for k in range(nk)]] = 1
        a_eq.append(f)
        b_eq.append(p.demandas_m3[j])
    for l in range(nl):
        g = np.zeros(n)
        g[[iy(i, l) for i in range(ni)]] = 1
        a_ub.append(g)
        b_ub.append(p.botaderos_cap_m3[l])
    for k in range(nk):
        g = np.zeros(n)
        g[[iz(k, j) for j in range(nj)]] = 1
        a_ub.append(g)
        b_ub.append(p.prestamos_cap_m3[k])
    if extra_ub is not None:
        a_ub.append(extra_ub[0])
        b_ub.append(extra_ub[1])
    r = linprog(c, A_ub=np.array(a_ub) if a_ub else None, b_ub=b_ub or None, A_eq=np.array(a_eq), b_eq=b_eq, bounds=(0, None), method="highs")
    return r, (nx, ny, nz, ni, nj, nl, nk)


def _costos(p: Problema) -> np.ndarray:
    k = p.costo_cop_m3_km
    cx = k * np.array(p.d_corte_relleno_km, float).ravel()
    cy = (k * np.array(p.d_corte_botadero_km, float) + np.array(p.tarifa_botadero_cop_m3, float)).ravel()
    cz = (k * np.array(p.d_prestamo_relleno_km, float) + np.array(p.precio_prestamo_cop_m3, float)[:, None]).ravel()
    return np.concatenate([cx, cy, cz])


def _a_plan(p: Problema, r, dims) -> Plan:
    nx, ny, nz, ni, nj, nl, nk = dims
    x, y, z = r.x[:nx].reshape(ni, nj), r.x[nx:nx + ny].reshape(ni, nl), r.x[nx + ny:].reshape(nk, nj)
    km = float((x * np.array(p.d_corte_relleno_km)).sum() + (y * np.array(p.d_corte_botadero_km)).sum() + (z * np.array(p.d_prestamo_relleno_km)).sum())
    total = float(sum(p.cortes_m3))
    return Plan(x, y, z, float(_costos(p) @ r.x), 100.0 * float(x.sum()) / total if total > 0 else 0.0, km)


def resolver_balance(p: Problema, objetivo: str = "costo") -> Plan:
    """objetivo 'costo': mínimo costo. 'reutilizacion': máxima reutilización y, entre los planes que la alcanzan, el de menor costo."""
    _validar(p)
    if objetivo not in ("costo", "reutilizacion"):
        raise ValueError("objetivo: 'costo' | 'reutilizacion'")
    c = _costos(p)
    if objetivo == "costo":
        r, dims = _resolver(p, c)
        if not r.success:
            raise ValueError(f"balance infactible: {r.message}")
        return _a_plan(p, r, dims)
    sel = np.zeros(len(c))
    sel[:len(p.cortes_m3) * len(p.demandas_m3)] = 1
    r1, dims = _resolver(p, -sel)
    if not r1.success:
        raise ValueError(f"balance infactible: {r1.message}")
    r2, dims = _resolver(p, c, extra_ub=(-sel, -(float(sel @ r1.x) - 1e-7)))
    if not r2.success:
        raise ValueError(f"balance infactible: {r2.message}")
    return _a_plan(p, r2, dims)


def combustible_gal_por_m3_km(capacidad_suelta_m3: float, km_gal: float, esponjamiento: float) -> float:
    """gal por m³ en banco y por km de distancia (ida cargado + vuelta vacío)."""
    if capacidad_suelta_m3 <= 0 or km_gal <= 0 or esponjamiento < 0:
        raise ValueError("capacidad y km/gal > 0; esponjamiento >= 0")
    return 2.0 * (1.0 + esponjamiento) / (capacidad_suelta_m3 * km_gal)
