"""Anchos efectivos de los elementos de un perfil C (NSR-10 F.4.2), issue #81.

Cada función devuelve las porciones efectivas de un elemento plano dados sus esfuerzos (MPa, compresión positiva).
Todas fallan con ValueError fuera de su dominio; ninguna asume valores.

Notas sobre la transcripción del corpus (verificadas el 2026-11-22):
- F.4.2.2-19 aparece como «b1 = be/(1+ψ) − b1». Se lee b2 = be/(1+ψ) − b1: la ecuación anterior (F.4.2.2-18) ya
  define b1 y la estructura es la de F.4.2.2-15/-17.
- F.4.2.3-1 aparece como «ψ = |f1/f2|» con f1 ≥ f2. Se usa ψ = |f2/f1| ∈ (0, 1]: con f1 ≥ f2 el cociente f1/f2 sería
  ≥ 1 y F.4.2.3-2 daría k < 0.43 bajo gradiente, menor que el de compresión uniforme (F.4.2.3.1), lo cual es
  físicamente imposible (el gradiente reduce el esfuerzo medio y no puede bajar k). Con ψ = 1 ambas lecturas coinciden.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .ancho_efectivo import (
    E_ACERO_MPA,
    K_NO_RIGIDIZADO,
    K_RIGIDIZADO,
    LAMBDA_LIMITE,
    MU_ACERO,
    ancho_efectivo,
    esfuerzo_pandeo_critico,
    factor_esbeltez,
)

W_T_MAX_ALETA_PESTANA = 60.0     # F.4.2.1.1.1 (1)
W_T_MAX_NO_RIGIDIZADO = 60.0     # F.4.2.1.1.1 (3)
H_T_MAX_ALMA = 200.0             # F.4.2.1.2 (a), alma no reforzada
D_W_MAX_TABLA = 0.80             # Tabla F.4.2.4-1


def _positivo(nombre: str, v: float, norma: str) -> None:
    if not (v > 0 and math.isfinite(v)):
        raise ValueError(f"{nombre} = {v} inválido: debe ser positivo y finito ({norma}).")


# ── Almas y elementos rigidizados bajo gradiente (F.4.2.2.3) ──────────────────────────────────────────────

@dataclass(frozen=True)
class AnchosGradiente:
    b1: float            # desde el borde más comprimido
    b2: float            # caso (1): junto al eje neutro; caso (2): desde el borde menos comprimido
    comprimida: float    # longitud comprimida del elemento
    totalmente_efectiva: bool


def alma_gradiente(f1: float, f2: float, w: float, t: float, ho: float, bo: float,
                   E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> AnchosGradiente:
    """F.4.2.2.3(a). f1 > 0 en el borde más comprimido; f2 con signo (negativo = tensión). w = ancho plano del alma."""
    _positivo("f1", f1, "NSR-10 F.4.2.2.3")
    _positivo("w", w, "NSR-10 F.4.2.2.3")
    _positivo("t", t, "NSR-10 F.4.2.2.3")
    if f2 > f1:
        raise ValueError("Debe cumplirse f1 ≥ f2 (NSR-10 F.4.2.2.3).")
    if w / t > H_T_MAX_ALMA:
        raise ValueError(f"h/t = {w / t:.1f} > {H_T_MAX_ALMA:.0f} en alma no reforzada (NSR-10 F.4.2.1.2).")
    psi = abs(f2 / f1)
    if f2 < 0:                                                   # caso (1): f1 compresión, f2 tensión
        k = 4 + 2 * (1 + psi) ** 3 + 2 * (1 + psi)               # F.4.2.2-14
        be = ancho_efectivo(k, f1, w, t, E, mu)
        comprimida = w / (1 + psi)
        b1 = be / (3 + psi)                                      # F.4.2.2-15 / -18
        if ho / bo <= 4:
            b2 = be / 2 if psi > 0.236 else be - b1              # F.4.2.2-16 / -17
        else:
            b2 = be / (1 + psi) - b1                             # F.4.2.2-19 (ver nota del módulo)
        llena = b1 + b2 >= comprimida
        if llena:
            b1, b2 = comprimida / 2, comprimida / 2
        return AnchosGradiente(b1, b2, comprimida, llena)
    # caso (2): f1 y f2 en compresión
    k = 4 + 2 * (1 - psi) ** 2 + 2 * (1 - psi)                   # F.4.2.2-20
    be = ancho_efectivo(k, f1, w, t, E, mu)
    b1 = be / (3 - psi)                                          # F.4.2.2-21
    b2 = be - b1                                                 # F.4.2.2-22
    llena = be >= w
    if llena:
        b1, b2 = w / 2, w / 2
    return AnchosGradiente(b1, b2, w, llena)


# ── Elementos no rigidizados y pestañas (F.4.2.3) ─────────────────────────────────────────────────────────

def no_rigidizado_gradiente(f1: float, f2: float, w: float, t: float,
                            E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """F.4.2.3.2(a) con f1 en el borde soportado (≥ f2) y el esfuerzo decreciendo hacia el borde libre.

    Devuelve el ancho efectivo medido desde el borde soportado. Cubre:
      f2 ≥ 0 (ambos en compresión, figura F.4.2.3-2(a)): k = 0.578/(ψ + 0.34), F.4.2.3-2;
      f2 < 0 (borde soportado comprimido, libre en tensión, figura F.4.2.3-3(b)): F.4.2.3-6 y -7.
    """
    _positivo("f1", f1, "NSR-10 F.4.2.3.2")
    _positivo("w", w, "NSR-10 F.4.2.3.2")
    _positivo("t", t, "NSR-10 F.4.2.3.2")
    if f2 > f1:
        raise ValueError("Este caso exige que el esfuerzo decrezca hacia el borde libre (f1 ≥ f2), NSR-10 F.4.2.3.2.")
    if w / t > W_T_MAX_NO_RIGIDIZADO:
        raise ValueError(f"w/t = {w / t:.1f} > {W_T_MAX_NO_RIGIDIZADO:.0f} en elemento no rigidizado (NSR-10 F.4.2.1.1.1).")
    psi = abs(f2 / f1)
    if f2 >= 0:
        k = 0.578 / (psi + 0.34)                                 # F.4.2.3-2
        return ancho_efectivo(k, f1, w, t, E, mu)
    if psi >= 1.0:
        return w                                                 # F.4.2.3.2(a)(2)(b), ψ ≥ 1: ρ = 1
    k = 1.70 + 5 * psi + 17.1 * psi ** 2                         # F.4.2.3-7
    lam = factor_esbeltez(f1, esfuerzo_pandeo_critico(k, w, t, E, mu))
    rho = 1.0 if lam <= LAMBDA_LIMITE else (1 - psi) * (1 - 0.22 / lam) / lam + psi   # F.4.2.3-6
    return min(rho, 1.0) * w


def no_rigidizado_uniforme(f: float, w: float, t: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """F.4.2.3.1: k = 0.43."""
    if w / t > W_T_MAX_NO_RIGIDIZADO:
        raise ValueError(f"w/t = {w / t:.1f} > {W_T_MAX_NO_RIGIDIZADO:.0f} en elemento no rigidizado (NSR-10 F.4.2.1.1.1).")
    return ancho_efectivo(K_NO_RIGIDIZADO, f, w, t, E, mu)


# ── Aleta con pestaña simple como rigidizador de borde (F.4.2.4) ─────────────────────────────────────────

@dataclass(frozen=True)
class AnchosAletaPestana:
    b1: float      # junto al alma
    b2: float      # junto a la pestaña
    ds: float      # ancho efectivo reducido de la pestaña
    R1: float
    k: float
    Is: float
    Ia: float
    S: float


def aleta_con_pestana(f: float, w: float, t: float, d: float, D: float, ds_prima: float,
                      E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> AnchosAletaPestana:
    """F.4.2.4(a), pestaña a 90° (sen θ = 1). w = ancho plano de la aleta, d = ancho plano de la pestaña,
    D = longitud total de la pestaña, ds_prima = d's (F.4.2.3.2). f = esfuerzo de compresión en la aleta."""
    for nombre, v in (("f", f), ("w", w), ("t", t), ("d", d), ("D", D)):
        _positivo(nombre, v, "NSR-10 F.4.2.4")
    if not (0 < ds_prima <= d + 1e-9):
        raise ValueError(f"d's = {ds_prima} debe estar en (0, d] (NSR-10 F.4.2.4).")
    if w / t > W_T_MAX_ALETA_PESTANA:
        raise ValueError(f"w/t = {w / t:.1f} > {W_T_MAX_ALETA_PESTANA:.0f} en aleta con pestaña simple (NSR-10 F.4.2.1.1.1).")
    S = 1.28 * math.sqrt(E / f)                                  # F.4.2.4-7
    Is = d ** 3 * t / 12                                         # F.4.2.4-10 con θ = 90°
    if w / t <= 0.328 * S:
        return AnchosAletaPestana(w / 2, w / 2, ds_prima, 1.0, K_RIGIDIZADO, Is, 0.0, S)   # F.4.2.4-1 a -3
    Ia = min(399 * t ** 4 * ((w / t) / S - 0.328) ** 3, t ** 4 * (115 * (w / t) / S + 5))  # F.4.2.4-8
    R1 = min(Is / Ia, 1.0)                                       # F.4.2.4-9
    n = max(0.582 - (w / t) / (4 * S), 1 / 3)                    # F.4.2.4-11
    if D / w <= 0.25:
        k = 3.57 * R1 ** n + 0.43
    elif D / w < D_W_MAX_TABLA:
        k = (4.82 - 5 * D / w) * R1 ** n + 0.43
    else:
        raise ValueError(f"D/w = {D / w:.3f} ≥ {D_W_MAX_TABLA} está fuera de la Tabla F.4.2.4-1.")
    k = min(k, K_RIGIDIZADO)
    b = ancho_efectivo(k, f, w, t, E, mu)
    b1 = b / 2 * R1                                              # F.4.2.4-4
    return AnchosAletaPestana(b1, b - b1, ds_prima * R1, R1, k, Is, Ia, S)   # F.4.2.4-5 y -6
