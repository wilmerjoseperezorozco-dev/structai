"""Golpe de ariete por el método de las características (MOC), tubería simple con embalse aguas arriba y válvula aguas abajo.

Ecuaciones (Wylie y Streeter; Chaudhry), con B = a/(g·A) y R = f·Δx/(2g·D·A²):
    C+:  H_P = C_P − B·Q_P,   C_P = H_{i−1} + B·Q_{i−1} − R·Q_{i−1}·|Q_{i−1}|
    C−:  H_P = C_M + B·Q_P,   C_M = H_{i+1} − B·Q_{i+1} + R·Q_{i+1}·|Q_{i+1}|
Malla con Courant = 1 (Δt = Δx/a). Fricción de Darcy-Weisbach cuasi-permanente concentrada al inicio del tramo (primer orden).
Válvula: Q_P = τ(t)·Q0·√(H_P/H0v), cierre lineal τ = 1 − t/Tc. No se modela separación de columna: ante cavitación se avisa y los
resultados posteriores a ella dejan de ser válidos."""
import math
from typing import Any, Dict

import numpy as np

from .gradiente import _finito

_G = 9.80665
_K_AGUA_PA = 2.07e9
_RHO_AGUA = 1000.0
_P_ATM_PA = 101325.0
_P_VAPOR_PA = 2339.0                                  # agua a 20 °C
H_VAPOR_M = -(_P_ATM_PA - _P_VAPOR_PA) / (_RHO_AGUA * _G)     # carga manométrica de vapor al nivel del mar, ≈ −10,09 m
_MAX_TRAMOS = 2000
_MAX_PASOS_TIEMPO = 200_000
_MAX_OPERACIONES = 60_000_000
_MAX_PUNTOS_SERIE = 2000


def celeridad_korteweg(diametro_m: float, espesor_m: float, e_tuberia_pa: float, k_fluido_pa: float = _K_AGUA_PA,
                       rho: float = _RHO_AGUA) -> float:
    """a = √(K/ρ)/√(1 + K·D/(E·e)): tubería de pared delgada, anclada, sin aire disuelto."""
    for nombre, v in (("diametro_m", diametro_m), ("espesor_m", espesor_m), ("e_tuberia_pa", e_tuberia_pa),
                      ("k_fluido_pa", k_fluido_pa), ("rho", rho)):
        if _finito(v, nombre) <= 0:
            raise ValueError(f"{nombre} debe ser positivo")
    return math.sqrt(k_fluido_pa / rho) / math.sqrt(1.0 + k_fluido_pa * diametro_m / (e_tuberia_pa * espesor_m))


def simular_ariete(*, longitud_m: float, diametro_m: float, celeridad_ms: float, f_darcy: float, caudal_m3s: float,
                   carga_embalse_m: float, t_cierre_s: float, t_fin_s: float, n_tramos: int = 50,
                   h_vapor_m: float = H_VAPOR_M) -> Dict[str, Any]:
    """Cierre lineal de una válvula en el extremo aguas abajo. Cargas manométricas sobre el eje de la tubería (horizontal)."""
    for nombre, v in (("longitud_m", longitud_m), ("diametro_m", diametro_m), ("celeridad_ms", celeridad_ms),
                      ("caudal_m3s", caudal_m3s), ("t_fin_s", t_fin_s)):
        if _finito(v, nombre) <= 0:
            raise ValueError(f"{nombre} debe ser positivo")
    if _finito(f_darcy, "f_darcy") < 0:
        raise ValueError("f_darcy no puede ser negativo")
    if _finito(t_cierre_s, "t_cierre_s") < 0:
        raise ValueError("t_cierre_s no puede ser negativo")
    _finito(carga_embalse_m, "carga_embalse_m")
    _finito(h_vapor_m, "h_vapor_m")
    if isinstance(n_tramos, bool) or not isinstance(n_tramos, int) or not (2 <= n_tramos <= _MAX_TRAMOS):
        raise ValueError(f"n_tramos debe ser un entero entre 2 y {_MAX_TRAMOS}")

    n = n_tramos
    dx = longitud_m / n
    dt = dx / celeridad_ms
    pasos = int(math.ceil(t_fin_s / dt))
    if pasos > _MAX_PASOS_TIEMPO or pasos * (n + 1) > _MAX_OPERACIONES:
        raise ValueError(f"la simulación pide {pasos} pasos de tiempo con {n} tramos: reduzca t_fin_s o n_tramos "
                         f"(máximo {_MAX_PASOS_TIEMPO} pasos)")
    area = math.pi * diametro_m ** 2 / 4.0
    v0 = caudal_m3s / area
    b = celeridad_ms / (_G * area)
    r = f_darcy * dx / (2.0 * _G * diametro_m * area ** 2)
    perdida_total = r * n * caudal_m3s ** 2
    h0_valvula = carga_embalse_m - perdida_total
    if h0_valvula <= 0:
        raise ValueError(f"la carga del embalse ({carga_embalse_m:g} m) no alcanza para el caudal pedido: la pérdida por fricción "
                         f"({perdida_total:.2f} m) deja una carga en la válvula de {h0_valvula:.2f} m ≤ 0")
    cv = caudal_m3s ** 2 / h0_valvula          # Q² = Cv·H a apertura total

    h = carga_embalse_m - r * caudal_m3s ** 2 * np.arange(n + 1)
    q = np.full(n + 1, caudal_m3s)
    h_max, h_min = h.copy(), h.copy()
    paso_salida = max(1, int(math.ceil(pasos / _MAX_PUNTOS_SERIE)))
    tiempos, serie_h, serie_q = [0.0], [float(h[-1])], [float(q[-1])]

    for k in range(1, pasos + 1):
        t = k * dt
        tau = max(0.0, 1.0 - t / t_cierre_s) if t_cierre_s > 0 else 0.0
        cp = h[:-1] + b * q[:-1] - r * q[:-1] * np.abs(q[:-1])          # llega por C+ a los nodos 1..n
        cm = h[1:] - b * q[1:] + r * q[1:] * np.abs(q[1:])              # llega por C− a los nodos 0..n−1
        h_n, q_n = np.empty_like(h), np.empty_like(q)
        h_n[1:-1] = 0.5 * (cp[:-1] + cm[1:])
        q_n[1:-1] = (cp[:-1] - cm[1:]) / (2.0 * b)
        h_n[0] = carga_embalse_m                                        # embalse de nivel constante
        q_n[0] = (carga_embalse_m - cm[0]) / b
        c_v = tau * tau * cv                                            # válvula: Q² = (τ²·Cv)·H
        q_n[-1] = 0.5 * (-b * c_v + math.sqrt((b * c_v) ** 2 + 4.0 * c_v * cp[-1])) if c_v > 0 else 0.0
        h_n[-1] = cp[-1] - b * q_n[-1]
        h, q = h_n, q_n
        np.maximum(h_max, h, out=h_max)
        np.minimum(h_min, h, out=h_min)
        if k % paso_salida == 0 or k == pasos:
            tiempos.append(t)
            serie_h.append(float(h[-1]))
            serie_q.append(float(q[-1]))
        if not (math.isfinite(float(h[-1])) and math.isfinite(float(q[-1]))):
            raise ValueError("el cálculo del transitorio divergió (resultado no finito)")

    t_critico = 2.0 * longitud_m / celeridad_ms
    return {
        "joukowsky_m": celeridad_ms * v0 / _G,
        "velocidad_inicial_ms": v0,
        "carga_valvula_inicial_m": h0_valvula,
        "tiempo_critico_s": t_critico,
        "periodo_s": 2.0 * t_critico,
        "cierre": "rápido" if t_cierre_s < t_critico else "lento",
        "paso_tiempo_s": dt,
        "valvula": {"h_max_m": float(h_max[-1]), "h_min_m": float(h_min[-1]), "carga_m": serie_h, "caudal_m3s": serie_q},
        "envolvente": {"x_m": [float(i * dx) for i in range(n + 1)], "h_max_m": [float(v) for v in h_max],
                       "h_min_m": [float(v) for v in h_min]},
        "tiempos_s": tiempos,
        "h_vapor_m": float(h_vapor_m),
        "cavitacion": bool(float(h_min.min()) < h_vapor_m),
    }
