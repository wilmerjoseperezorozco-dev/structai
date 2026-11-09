"""Pantalla apoyada en UN nivel (puntal o anclaje) por el método de apoyo libre en el pie ("free earth support") con empujes de Rankine.
Alcance: sin agua, suelo homogéneo, terreno horizontal, pared lisa, un solo nivel de apoyo a la profundidad `prof_apoyo` bajo la cabeza;
empuje pasivo reducido por `fs_pasivo` (dado por el usuario); tensión del empuje activo despreciada (truncada a cero).
Equilibrio: momentos respecto del apoyo = 0 define el empotramiento D; la reacción del apoyo cierra las fuerzas horizontales; el momento máximo sale del
diagrama de cortante (reacción incluida). No verifica sección, deformaciones (asentamientos de vecinos, H.5.1.3.2), levantamiento de fondo ni la
capacidad del anclaje. En apoyo libre el pie puede girar: el momento es una cota razonable, no un diseño de pantalla."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from .excavacion_contencion import _presiones
from .excavacion_estabilidad import SueloExc


@dataclass(frozen=True)
class PantallaApoyada:
    empotramiento_m: float | None
    longitud_total_m: float | None
    reaccion_apoyo_kn_por_m: float | None
    momento_max_knm_por_m: float | None
    sin_solucion: bool


def _momento_neto_apoyo(suelo: SueloExc, h: float, d: float, a: float, q: float, fs_pasivo: float) -> float:
    z, act, pas = _presiones(suelo, h, d, q, fs_pasivo)
    return float(np.trapezoid((act - pas) * (z - a), z))           # >0: el activo vence al pasivo (la pantalla gira hacia la excavación)


def dimensionar_apuntalada(suelo: SueloExc, altura: float, prof_apoyo: float, sobrecarga_kpa: float, fs_pasivo: float, *, factor_longitud: float) -> PantallaApoyada:
    if altura <= 0 or not 0.0 <= prof_apoyo < altura or sobrecarga_kpa < 0 or fs_pasivo < 1.0 or factor_longitud < 1.0:
        raise ValueError("altura > 0, 0 <= prof_apoyo < altura, sobrecarga >= 0, fs_pasivo >= 1, factor_longitud >= 1")

    def f(d): return _momento_neto_apoyo(suelo, altura, d, prof_apoyo, sobrecarga_kpa, fs_pasivo)
    lo, hi = 1e-3, 20.0 * altura
    if f(lo) <= 0:
        d = lo                                                       # el activo no mueve el apoyo: basta el empotramiento mínimo del tramo numérico
    elif f(hi) >= 0:
        return PantallaApoyada(None, None, None, None, True)         # sin resistencia pasiva suficiente (p. ej. phi ~ 0)
    else:
        d = brentq(f, lo, hi)
    d_total = d * factor_longitud
    z, act, pas = _presiones(suelo, altura, d, sobrecarga_kpa, fs_pasivo)
    dz = np.diff(z)
    carga = 0.5 * ((act - pas)[1:] + (act - pas)[:-1]) * dz
    reaccion = float(carga.sum())                                    # equilibrio horizontal: fuerza neta que toma el apoyo
    corte = np.concatenate([[0.0], np.cumsum(carga)])
    corte = corte - reaccion * (z >= prof_apoyo)
    momento = np.concatenate([[0.0], np.cumsum(0.5 * (corte[1:] + corte[:-1]) * dz)])
    return PantallaApoyada(d_total, altura + d_total, reaccion, float(np.abs(momento).max()), False)
