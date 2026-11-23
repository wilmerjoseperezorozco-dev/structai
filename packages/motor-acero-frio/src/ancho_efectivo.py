"""
Ancho efectivo de elementos planos en compresión, metodo de Winter --
NSR-10 F.4.2.2 (elementos rigidizados) y F.4.2.3.1 (no rigidizados),
equivalente a AISI S100 SS B2.1/B3.1. Issue #81 -- primer paso de la
cadena de calculo de acero formado en frio (988 chunks en el corpus,
~210 subsecciones solo en F.4 -- ver el issue para el mapa completo).

Formulas verbatim (verificadas contra nsr10_chunks, ids
NSR10-F-F_4_2_2_1_a_2_anchos_efectivos_rigidizados_huecos_* y
NSR10-F-F_4_2_3_anchos_efectivos_no_rigidizados_*, 2026-09-30):

    lambda = sqrt(f / Fcr)                                    (F.4.2.2-4)
    Fcr = k * pi^2 * E / [12 * (1 - mu^2) * (w/t)^2]          (F.4.2.2-5)
    b = w                    si lambda <= 0.673               (F.4.2.2-1)
    b = rho * w              si lambda > 0.673                (F.4.2.2-2)
    rho = (1 - 0.22/lambda) / lambda                          (F.4.2.2-3)

k = 4 para elementos rigidizados (apoyados por un alma en cada borde
longitudinal); k = 0.43 para no rigidizados (F.4.2.3.1 remite a la misma
formula con este unico cambio).

E = 203000 MPa: valor que el propio Capitulo F.4 fija para el acero
formado en frio (F.4.4.6.1.3). Corregido el 2026-11-22: el MVP inicial
usaba 200000 MPa, que es el de otros capitulos, no el de F.4.
mu = 0.3: F.4.3.3.2.1. Ambos son parametros sobreescribibles.

Alcance deliberado de este modulo: SOLO el calculo de ancho efectivo
dado un esfuerzo f conocido. El proceso real de diseno es iterativo (f
depende de la seccion efectiva, que depende de f) -- esa iteracion vive
en los modulos de flexion/compresion que se construyan sobre este,
fuera del alcance de este primer paso (ver issue #81)."""
from __future__ import annotations

import math

E_ACERO_MPA = 203000.0  # F.4.4.6.1.3
MU_ACERO = 0.3

K_RIGIDIZADO = 4.0
K_NO_RIGIDIZADO = 0.43

LAMBDA_LIMITE = 0.673


def esfuerzo_pandeo_critico(k: float, w: float, t: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """Fcr, ecuacion F.4.2.2-5. w, t en las mismas unidades (mm), E en MPa."""
    return k * math.pi**2 * E / (12 * (1 - mu**2) * (w / t) ** 2)


def factor_esbeltez(f: float, fcr: float) -> float:
    """lambda, ecuacion F.4.2.2-4."""
    return math.sqrt(f / fcr)


def factor_reduccion(lam: float) -> float:
    """rho, ecuacion F.4.2.2-3. Valido solo para lambda > 0.673 -- para
    lambda <= 0.673, rho no aplica (b=w directamente, ver F.4.2.2-1)."""
    return (1 - 0.22 / lam) / lam


def _validar(k: float, f: float, w: float, t: float, E: float, mu: float) -> None:
    for nombre, v in (("k", k), ("f", f), ("w", w), ("t", t), ("E", E)):
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} invalido: debe ser positivo y finito (NSR-10 F.4.2.2.1).")
    if not (0 <= mu < 0.5):
        raise ValueError(f"mu = {mu} fuera de rango fisico [0; 0.5) (NSR-10 F.4.3.3.2.1).")


def ancho_efectivo(k: float, f: float, w: float, t: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """Ancho efectivo b (F.4.2.2-1/-2) con el coeficiente de pandeo k que corresponda al elemento."""
    return _ancho_efectivo(k, f, w, t, E, mu)


def _ancho_efectivo(k: float, f: float, w: float, t: float, E: float, mu: float) -> float:
    _validar(k, f, w, t, E, mu)
    fcr = esfuerzo_pandeo_critico(k, w, t, E, mu)
    lam = factor_esbeltez(f, fcr)
    if lam <= LAMBDA_LIMITE:
        return w
    return factor_reduccion(lam) * w


def ancho_efectivo_rigidizado(f: float, w: float, t: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """Ancho efectivo b de un elemento rigidizado bajo compresion uniforme
    (F.4.2.2.1) -- apoyado por un alma en cada borde longitudinal, ej. el
    alma de una seccion C o Z. f = esfuerzo de compresion real en el
    elemento [MPa]. w = ancho plano, t = espesor [mm]."""
    return _ancho_efectivo(K_RIGIDIZADO, f, w, t, E, mu)


def ancho_efectivo_no_rigidizado(f: float, w: float, t: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """Ancho efectivo b de un elemento no rigidizado bajo compresion
    uniforme (F.4.2.3.1) -- ej. el ala libre de una seccion C sin
    pestana. Misma formula que el rigidizado, unicamente cambia k a
    0.43 (remision explicita del propio numeral)."""
    return _ancho_efectivo(K_NO_RIGIDIZADO, f, w, t, E, mu)
