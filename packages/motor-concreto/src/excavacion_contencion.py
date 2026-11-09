"""Contención temporal en voladizo (pantalla/tablestaca) con empujes de Rankine. Alcance deliberadamente limitado:
- sin nivel freático, sin anclajes ni puntales, suelo homogéneo, terreno horizontal, pared lisa (Rankine);
- el empuje pasivo se reduce con un factor de seguridad dado por el usuario (`fs_pasivo`, sin valor por defecto);
- la tensión del empuje activo se desprecia (se trunca a cero en la zona de grieta), lo cual es el lado conservador;
- no verifica la estructura (sección, flexión, deformaciones) ni el levantamiento de fondo: entrega longitud de empotramiento y momento máximo de diseño.
Si la altura supera `h_max_voladizo`, devuelve `requiere_apoyos=True` y no dimensiona (un voladizo alto no es una alternativa razonable)."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from .excavacion_estabilidad import SueloExc

N_PUNTOS = 4000


@dataclass(frozen=True)
class Pantalla:
    empotramiento_m: float | None
    longitud_total_m: float | None
    momento_max_knm_por_m: float | None
    requiere_apoyos: bool


def _presiones(suelo: SueloExc, h: float, d: float, q: float, fs_pasivo: float):
    ka = math.tan(math.radians(45.0 - suelo.phi_deg / 2.0)) ** 2
    kp = math.tan(math.radians(45.0 + suelo.phi_deg / 2.0)) ** 2
    z = np.linspace(0.0, h + d, N_PUNTOS)
    act = np.maximum(ka * (suelo.gamma * z + q) - 2.0 * suelo.c_kpa * math.sqrt(ka), 0.0)
    zp = np.maximum(z - h, 0.0)
    pas = np.where(z > h, (kp * suelo.gamma * zp + 2.0 * suelo.c_kpa * math.sqrt(kp)) / fs_pasivo, 0.0)
    return z, act, pas


def _momento_neto_base(suelo: SueloExc, h: float, d: float, q: float, fs_pasivo: float) -> float:
    z, act, pas = _presiones(suelo, h, d, q, fs_pasivo)
    brazo = (h + d) - z
    return float(np.trapezoid((pas - act) * brazo, z))


def dimensionar_voladizo(suelo: SueloExc, altura: float, sobrecarga_kpa: float, fs_pasivo: float, h_max_voladizo: float, empotramiento_min_m: float, *, factor_longitud: float) -> Pantalla:
    """`empotramiento_min_m`: piso práctico (lo da el usuario); rige cuando la cohesión anula el empuje activo y el equilibrio no pide empotramiento.
    `factor_longitud`: multiplicador OBLIGATORIO del empotramiento calculado. El equilibrio de momentos con pasivo completo hasta la punta deja la resultante horizontal sin equilibrar (empotramiento corto); la práctica de proyecto lo incrementa y el valor lo fija el usuario con su fuente. 1.0 = sin incremento."""
    if altura <= 0 or sobrecarga_kpa < 0 or fs_pasivo < 1.0 or h_max_voladizo <= 0 or factor_longitud < 1.0 or empotramiento_min_m < 0:
        raise ValueError("altura > 0, sobrecarga >= 0, fs_pasivo >= 1, h_max > 0, factor_longitud >= 1")
    if altura > h_max_voladizo:
        return Pantalla(None, None, None, True)
    def f(x): return _momento_neto_base(suelo, altura, x, sobrecarga_kpa, fs_pasivo)
    if f(1e-3) < 0:
        if f(20.0 * altura) <= 0:
            return Pantalla(None, None, None, True)        # suelo sin resistencia pasiva suficiente (p. ej. phi ~ 0): el voladizo no tiene solución
        d = brentq(f, 1e-3, 20.0 * altura)
    else:
        d = 0.0
    d = max(d, empotramiento_min_m)
    z, act, pas = _presiones(suelo, altura, d, sobrecarga_kpa, fs_pasivo)
    corte = np.concatenate([[0.0], np.cumsum(0.5 * ((act - pas)[1:] + (act - pas)[:-1]) * np.diff(z))])        # cortante (act - pas) acumulado desde la cabeza
    momento = np.concatenate([[0.0], np.cumsum(0.5 * (corte[1:] + corte[:-1]) * np.diff(z))])
    m_max = float(np.abs(momento).max())
    return Pantalla(d * factor_longitud, altura + d * factor_longitud, m_max, False)
