"""
Espesor de losa de pavimento rígido (JPCP) con la ecuación de diseño de la Guía AASHTO 1993 (issue #106).

    log10(W18) = ZR·So + 7,35·log10(D+1) − 0,06
                 + log10(ΔPSI/(4,5−1,5)) / (1 + 1,624·10⁷/(D+1)^8,46)
                 + (4,22 − 0,32·pt)·log10[ S'c·Cd·(D^0,75 − 1,132) / (215,63·J·(D^0,75 − 18,42/(Ec/k)^0,25)) ]

Unidades del método original (EE. UU.): D en pulgadas, S'c y Ec en psi y k en pci. Las funciones públicas reciben SI
(cm, MPa, MPa/m) y convierten. D se despeja con `brentq`, sin pasos fijos.

El Manual INVIAS de pavimentos de concreto (2008) usa AASHTO-93 y PCA-84 para su catálogo de espesores. Este módulo
implementa solo la ecuación AASHTO-93 y NO reproduce el catálogo: sus tablas no están en el corpus. La comparación con
ese catálogo queda pendiente para la validación de un ingeniero de pavimentos.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import NormalDist
from typing import List

from scipy.optimize import brentq, minimize_scalar

CM_POR_PULGADA = 2.54
PSI_POR_MPA = 145.037738
MPA_M_POR_PCI = 0.271447          # 1 pci = 1 lbf/in³ = 0,271447 MPa/m

# Ec por defecto cuando no hay datos de resistencia: 4 000 000 psi (≈ 27 580 MPa), valor usual con la Guía AASHTO-93.
EC_POR_DEFECTO_MPA = 4.0e6 / PSI_POR_MPA

D_MAX_PULG = 40.0                 # cota superior de búsqueda (≈ 1 m): más allá no es una losa de carretera


def z_r(confiabilidad_pct: float) -> float:
    """Desviación normal estándar ZR para la confiabilidad R (%). R = 90 % → −1,2816."""
    if not 50.0 <= confiabilidad_pct < 100.0:
        raise ValueError(f"Confiabilidad {confiabilidad_pct} % fuera de [50, 100) (AASHTO-93, Parte I, cap. 4)")
    return NormalDist().inv_cdf(1.0 - confiabilidad_pct / 100.0)


def _d_min_pulg(Ec_psi: float, k_pci: float) -> float:
    """Menor D con argumento del logaritmo positivo: D^0,75 > máx(1,132; 18,42/(Ec/k)^0,25)."""
    umbral = max(1.132, 18.42 / (Ec_psi / k_pci) ** 0.25)
    return umbral ** (1 / 0.75) * (1 + 1e-9) + 1e-9


def log10_w18(D_pulg: float, *, ZR: float, So: float, p0: float, pt: float, Sc_psi: float, Cd: float, J: float,
              Ec_psi: float, k_pci: float) -> float:
    """Lado derecho de la ecuación AASHTO-93 para pavimento rígido, en unidades del método original."""
    dpsi = p0 - pt
    d75 = D_pulg ** 0.75
    termino_serv = math.log10(dpsi / (4.5 - 1.5)) / (1.0 + 1.624e7 / (D_pulg + 1.0) ** 8.46)
    termino_esf = (4.22 - 0.32 * pt) * math.log10(
        Sc_psi * Cd * (d75 - 1.132) / (215.63 * J * (d75 - 18.42 / (Ec_psi / k_pci) ** 0.25)))
    return ZR * So + 7.35 * math.log10(D_pulg + 1.0) - 0.06 + termino_serv + termino_esf


@dataclass
class ResultadoLosa:
    D_cm: float                       # espesor exacto que satisface la ecuación
    D_pulg: float
    W18_millones: float
    ZR: float
    entradas_psi_pci: dict
    supuestos: List[str] = field(default_factory=list)


def espesor_losa(W18_millones: float, *, k_MPa_m: float, Sc_MPa: float, Ec_MPa: float = EC_POR_DEFECTO_MPA,
                 J: float = 3.2, Cd: float = 1.0, confiabilidad_pct: float = 90.0, So: float = 0.35,
                 p0: float = 4.5, pt: float = 2.5) -> ResultadoLosa:
    """Espesor de losa D que hace que la ecuación AASHTO-93 iguale W18 (ESAL rígidos de 80 kN en el carril de diseño)."""
    for nombre, v in (("W18_millones", W18_millones), ("k_MPa_m", k_MPa_m), ("Sc_MPa", Sc_MPa), ("Ec_MPa", Ec_MPa),
                      ("J", J), ("Cd", Cd), ("So", So)):
        if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
            raise ValueError(f"{nombre} debe ser un número finito y positivo (AASHTO-93, ecuación de pavimento rígido)")
    if not (0 < pt < p0 <= 5.0):
        raise ValueError("Se requiere 0 < pt < p0 ≤ 5 (índices de serviciabilidad, AASHTO-93)")

    ZR = z_r(confiabilidad_pct)
    entradas = dict(ZR=ZR, So=So, p0=p0, pt=pt, Sc_psi=Sc_MPa * PSI_POR_MPA, Cd=Cd, J=J,
                    Ec_psi=Ec_MPa * PSI_POR_MPA, k_pci=k_MPa_m / MPA_M_POR_PCI)
    objetivo = math.log10(W18_millones * 1e6)
    d_lo = _d_min_pulg(entradas["Ec_psi"], entradas["k_pci"])

    def f(D: float) -> float:
        return log10_w18(D, **entradas) - objetivo

    # Junto a d_lo el término de esfuerzos tiende a +∞ (D^0,75 → 18,42/(Ec/k)^0,25): esa rama de losas delgadas es un
    # artefacto matemático. La rama física empieza en el mínimo de f, donde la capacidad crece con D; solo ahí se busca.
    d_fis = minimize_scalar(f, bounds=(d_lo, D_MAX_PULG), method="bounded", options={"xatol": 1e-9}).x
    if f(D_MAX_PULG) < 0:
        raise ValueError(f"Ninguna losa de hasta {D_MAX_PULG * CM_POR_PULGADA:.0f} cm cumple la ecuación AASHTO-93 "
                         "con estos datos: revise el tránsito, k y S'c o considere otra estructura")
    if f(d_fis) >= 0:         # tránsito muy bajo: basta el inicio de la rama física; manda el espesor mínimo del motor
        D = d_fis
    else:
        D = brentq(f, d_fis, D_MAX_PULG, xtol=1e-10, rtol=1e-12)

    supuestos = [
        f"Ecuación AASHTO-93 para pavimento rígido: R = {confiabilidad_pct:g} % (ZR = {ZR:.4f}), So = {So:g}, "
        f"p0 = {p0:g}, pt = {pt:g}, J = {J:g}, Cd = {Cd:g}",
        f"S'c = {Sc_MPa:g} MPa, Ec = {Ec_MPa:.0f} MPa, k = {k_MPa_m:g} MPa/m (k efectivo sobre el soporte de la losa)",
        "W18 se interpreta como ESAL de 80 kN con factores de equivalencia para pavimento rígido, en el carril de diseño",
    ]
    return ResultadoLosa(D_cm=D * CM_POR_PULGADA, D_pulg=D, W18_millones=W18_millones, ZR=ZR,
                         entradas_psi_pci=entradas, supuestos=supuestos)


def w18_admisible_millones(D_cm: float, **kw) -> float:
    """ESAL (millones) que admite una losa de espesor D_cm con las mismas entradas de `espesor_losa`."""
    r = espesor_losa(1.0, **kw)            # reutiliza la validación y la conversión de unidades
    e = r.entradas_psi_pci
    D = D_cm / CM_POR_PULGADA
    if D <= _d_min_pulg(e["Ec_psi"], e["k_pci"]):
        raise ValueError("Espesor de losa por debajo del dominio de la ecuación AASHTO-93")
    # En la rama espuria (losa más delgada que el inicio de la rama física) la ecuación no da una capacidad con sentido
    d_fis = minimize_scalar(lambda x: log10_w18(x, **e), bounds=(_d_min_pulg(e["Ec_psi"], e["k_pci"]), D_MAX_PULG),
                            method="bounded", options={"xatol": 1e-9}).x
    if D < d_fis:
        raise ValueError("Espesor de losa en la rama espuria de la ecuación AASHTO-93 (demasiado delgada para estos k y Ec)")
    return 10 ** log10_w18(D, **e) / 1e6
