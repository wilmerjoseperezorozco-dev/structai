"""Carga axial y momento combinados, NSR-10 F.4.3.5 (DCCR). Issue #81.

Solo flexión alrededor del eje fuerte (M̄y = 0): el motor todavía no calcula Mny. Las ecuaciones de la norma se
evalúan con ese término nulo, y la función lo deja explícito en su nombre (uniaxial).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

PHI_T_COMBINADA = 0.95      # F.4.3.5.1.1
UMBRAL_EC6 = 0.15           # F.4.3.5-6


def _no_neg(nombre: str, v: float, norma: str) -> None:
    if not (v >= 0 and math.isfinite(v)):
        raise ValueError(f"{nombre} = {v} inválido: use la magnitud de la solicitación ({norma}).")


def _pos(nombre: str, v: float, norma: str) -> None:
    if not (v > 0 and math.isfinite(v)):
        raise ValueError(f"{nombre} = {v} inválido: debe ser positivo ({norma}).")


def coeficiente_cm(M1_sobre_M2: float | None, *, traslacion_nudos: bool, carga_transversal: str | None = None) -> float:
    """Cm de F.4.3.5.2.1.

    - Pórtico con traslación de nudos: 0.85 (a).
    - Arriostrado, sin carga transversal entre apoyos: 0.6 − 0.4·M1/M2 (F.4.3.5-11, b); M1/M2 > 0 en curvatura doble.
    - Arriostrado con carga transversal (c), sin análisis racional: «extremos_restringidos» → 0.85;
      «extremos_libres» → 1.00.
    """
    if traslacion_nudos:
        return 0.85
    if carga_transversal is not None:
        valores = {"extremos_restringidos": 0.85, "extremos_libres": 1.00}
        if carga_transversal not in valores:
            raise ValueError("carga_transversal debe ser 'extremos_restringidos' o 'extremos_libres' (F.4.3.5.2.1 c).")
        return valores[carga_transversal]
    if M1_sobre_M2 is None or not (math.isfinite(M1_sobre_M2) and -1.0 <= M1_sobre_M2 <= 1.0):
        raise ValueError(f"M1/M2 = {M1_sobre_M2} inválido: debe estar en [−1, 1] (F.4.3.5-11).")
    return 0.6 - 0.4 * M1_sobre_M2


@dataclass(frozen=True)
class ResultadoCombinada:
    razon: float            # la mayor de las ecuaciones que aplican; ≤ 1.0 para cumplir
    ecuaciones: dict        # valor de cada ecuación evaluada
    razones_individuales: dict
    gobierna: str


def flexo_compresion_uniaxial(Pu: float, Mux: float, phi_Pn: float, phi_Pno: float, phi_Mnx: float,
                              PEX: float, Cmx: float) -> ResultadoCombinada:
    """F.4.3.5-4 y -5 (o -6 si P̄/φcPn ≤ 0.15), con αx = 1 − P̄/PEX > 0 (F.4.3.5-7). Unidades coherentes (N, N·mm).

    Cada razón individual tampoco puede exceder 1 (F.4.3.5.2.1)."""
    norma = "NSR-10 F.4.3.5.2"
    _no_neg("Pu", Pu, norma)
    _no_neg("Mux", Mux, norma)
    for nombre, v in (("φcPn", phi_Pn), ("φcPno", phi_Pno), ("φbMnx", phi_Mnx), ("PEX", PEX), ("Cmx", Cmx)):
        _pos(nombre, v, norma)
    alfa = 1 - Pu / PEX
    if alfa <= 0:
        raise ValueError(f"αx = 1 − P̄/PEX = {alfa:.3f} ≤ 0: la carga supera la de Euler alrededor de x (F.4.3.5-7).")
    rp, rm = Pu / phi_Pn, Mux / phi_Mnx
    if rp <= UMBRAL_EC6:
        ec = {"F.4.3.5-6": rp + rm}
    else:
        ec = {"F.4.3.5-4": rp + Cmx * Mux / (phi_Mnx * alfa), "F.4.3.5-5": Pu / phi_Pno + rm}
    indiv = {"axial": rp, "flexion": rm}
    todo = {**ec, **{f"individual_{k}": v for k, v in indiv.items()}}
    gobierna = max(todo, key=todo.get)
    return ResultadoCombinada(razon=todo[gobierna], ecuaciones=ec, razones_individuales=indiv, gobierna=gobierna)


def flexo_tension_uniaxial(Tu: float, Mux: float, phi_Tn: float, phi_b_Mnx: float, phi_b_Mnxt: float
                           ) -> ResultadoCombinada:
    """F.4.3.5-1 (fibra a tensión, Mnxt = Sft·Fy) y F.4.3.5-2 (fibra a compresión). φt = 0.95 en ambas."""
    norma = "NSR-10 F.4.3.5.1"
    _no_neg("Tu", Tu, norma)
    _no_neg("Mux", Mux, norma)
    for nombre, v in (("φtTn", phi_Tn), ("φbMnx", phi_b_Mnx), ("φbMnxt", phi_b_Mnxt)):
        _pos(nombre, v, norma)
    ec = {"F.4.3.5-1": Mux / phi_b_Mnxt + Tu / phi_Tn, "F.4.3.5-2": Mux / phi_b_Mnx - Tu / phi_Tn}
    gobierna = max(ec, key=ec.get)
    return ResultadoCombinada(razon=ec[gobierna], ecuaciones=ec,
                              razones_individuales={"tension": Tu / phi_Tn, "flexion": Mux / phi_b_Mnx},
                              gobierna=gobierna)
