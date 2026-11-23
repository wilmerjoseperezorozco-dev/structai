"""Pandeo distorsional de perfiles C con pestaña, NSR-10 F.4.3.3.1.4(b) (flexión) y F.4.3.4.2(b) (compresión). Issue #81.

Se usa el método general (b) y no la disposición simplificada (a). En el corpus, (a) exige 45° ≤ θ < 90°, lo que
excluye la pestaña a 90° de este motor. El método (b) cubre cualquier pestaña simple.

Propiedades de la aleta comprimida más su pestaña, en el sistema de la norma: origen en la unión aleta-alma, x positivo
hacia la punta de la aleta e y positivo hacia abajo, es decir, hacia donde apunta la pestaña. Se calculan con el mismo
método lineal de seccion.py sobre la poligonal [unión → esquina → punta de la pestaña].

Lecturas del corpus documentadas (se prueban contra las formas cerradas del comentario de AISI S100 para la pestaña
simple, que es una referencia independiente):
- F.4.3.3-42 escribe «ho²» dentro de K̃φfg. Dimensional y físicamente el término es hx², parte del momento polar de la
  aleta respecto a la unión aleta-alma. Con ho² (la altura del alma) K̃φfg crecería con la altura de la viga, algo que la
  aleta no «ve». Se usa hx².
- yo se toma como y_unión − y_centroide de la aleta (= −d²/(2(b+d)) en la pestaña simple). Para la aleta con pestaña,
  la unión y el centro de cortante de la aleta están a la misma altura, así que coincide con la definición de AISI
  (centroide → centro de cortante).
- F.4.3.3-41 da kφwe = E·t³/(12(1−μ²)·ho) en flexión. Se usa tal cual: es menor que el término principal de la
  expresión de AISI S100-07 (3·E·t³/(12(1−μ²)·ho)), así que el resultado queda del lado seguro.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .ancho_efectivo import E_ACERO_MPA, MU_ACERO
from .seccion import GeometriaC, propiedades_brutas

PHI_B_DISTORSIONAL = 0.90        # F.4.3.3.1.4
PHI_C_DISTORSIONAL = 0.85        # F.4.3.4.2
LAMBDA_D_FLEXION = 0.673         # F.4.3.3-28 / -29
LAMBDA_D_COMPRESION = 0.561      # F.4.3.4-12 / -13


@dataclass(frozen=True)
class PropiedadesAleta:
    """Aleta comprimida + pestaña en el sistema de la norma (unión aleta-alma en el origen, y hacia abajo)."""
    Af: float      # mm²
    Ixf: float     # mm⁴
    Iyf: float     # mm⁴
    Ixyf: float    # mm⁴
    Jf: float      # mm⁴
    Cwf: float     # mm⁶
    xo: float      # mm, centroide → centro de cortante de la aleta
    hx: float      # mm, centroide → unión aleta-alma
    yo: float      # mm, centroide → unión (= centroide → centro de cortante)


def propiedades_aleta(g: GeometriaC) -> PropiedadesAleta:
    if not g.con_pestana:
        raise ValueError("El pandeo distorsional de F.4.3.3.1.4 y F.4.3.4.2 aplica a aletas con rigidizador de borde; "
                         "esta C no tiene pestaña.")
    p = propiedades_brutas([(0.0, 0.0), (g.bc, 0.0), (g.bc, g.dc)], g.t)
    return PropiedadesAleta(Af=p.A, Ixf=p.Ix, Iyf=p.Iy, Ixyf=p.Ixy, Jf=p.J, Cwf=p.Cw,
                            xo=p.xs - p.xc, hx=0.0 - p.xc, yo=0.0 - p.yc)


def _termino_rigidez_aleta(a: PropiedadesAleta) -> float:
    """Ixf(xo−hx)² + Cwf − (Ixyf²/Iyf)(xo−hx)², común a kφfe y a Lcr (mm⁶)."""
    d = a.xo - a.hx
    return a.Ixf * d * d + a.Cwf - (a.Ixyf ** 2 / a.Iyf) * d * d


def _kphi_fe(a: PropiedadesAleta, L: float, E: float, G: float) -> float:
    """F.4.3.3-40 (N·mm/mm/rad)."""
    return (math.pi / L) ** 4 * E * _termino_rigidez_aleta(a) + (math.pi / L) ** 2 * G * a.Jf


def _kphi_fg(a: PropiedadesAleta, L: float) -> float:
    """F.4.3.3-42 con hx² (ver la nota del módulo), dividido por Fd (mm²)."""
    d, r = a.xo - a.hx, a.Ixyf / a.Iyf
    return (math.pi / L) ** 2 * (a.Af * (d * d * r * r - 2 * a.yo * d * r + a.hx ** 2 + a.yo ** 2) + a.Ixf + a.Iyf)


def factor_beta(Lm: float, Lcr: float) -> float:
    """F.4.3.3-34 / F.4.3.4-18: 1 si Lm ≥ Lcr; (Lm/Lcr)^ln(Lm/Lcr) si Lm < Lcr."""
    if Lm >= Lcr:
        return 1.0
    r = Lm / Lcr
    return r ** math.log(r)


@dataclass(frozen=True)
class ResultadoDistorsional:
    Fd: float           # MPa, esfuerzo elástico de pandeo distorsional
    Lcr: float          # mm
    L: float            # mm, mín(Lcr, Lm)
    beta: float
    lambda_d: float
    nominal: float      # Mn (N·mm) o Pn (N)
    phi: float
    fluencia: float     # My (N·mm) o Py (N)
    critico: float      # Mcrd (N·mm) o Pcrd (N)
    rigideces: dict


def _validar(Lm: float, kphi: float, Fy: float) -> None:
    if not (Lm > 0 and math.isfinite(Lm)):
        raise ValueError(f"Lm = {Lm} inválido: distancia positiva entre restricciones al pandeo distorsional "
                         "(NSR-10 F.4.3.3.1.4(a)).")
    if not (kphi >= 0 and math.isfinite(kphi)):
        raise ValueError(f"kφ = {kphi} inválido: rigidez rotacional ≥ 0, cero si la aleta no está restringida "
                         "(NSR-10 F.4.3.3.1.4(b)).")
    if not (Fy > 0 and math.isfinite(Fy)):
        raise ValueError(f"Fy = {Fy} inválido (NSR-10 F.4.1.6.1).")


def distorsional_flexion_c(g: GeometriaC, Fy: float, Lm: float, kphi: float = 0.0,
                           E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> ResultadoDistorsional:
    """Mn distorsional de una C en flexión alrededor del eje fuerte con la aleta superior comprimida.

    Fd por F.4.3.3-37 a -43 (método b); Mn por F.4.3.3-28/-29 con My = Sfy·Fy y Mcrd = Sf·Fd (sección bruta).
    kφ = 0 es el valor de la norma para una aleta comprimida sin restricción."""
    _validar(Lm, kphi, Fy)
    a = propiedades_aleta(g)
    G = E / (2 * (1 + mu))
    t, ho = g.t, g.H
    Lcr = ((6 * math.pi ** 4 * ho * (1 - mu ** 2) / t ** 3) * _termino_rigidez_aleta(a)
           + math.pi ** 4 * ho ** 4 / 720) ** 0.25                                        # F.4.3.3-39bis
    L = min(Lcr, Lm)
    p = g.propiedades()
    y_sup, y_inf = g.hc, 0.0                                                            # extremos del alma (línea media)
    xi = (y_sup - y_inf) / (y_sup - p.yc)                                               # (f1 − f2)/f1, sección bruta
    kfe = _kphi_fe(a, L, E, G)
    kwe = E * t ** 3 / (12 * (1 - mu ** 2) * ho)                                        # F.4.3.3-41
    kfg = _kphi_fg(a, L)
    r = L / ho
    kwg = (ho * t * math.pi ** 2 / 13440) * (
        ((45360 * (1 - xi) + 62160) * r ** 2 + 448 * math.pi ** 2 + (1 / r) ** 2 * (53 + 3 * (1 - xi)) * math.pi ** 4)
        / (math.pi ** 4 + 28 * math.pi ** 2 * r ** 2 + 420 * r ** 4))                  # F.4.3.3-43
    if kfg + kwg <= 0:
        raise ValueError("Rigidez geométrica no positiva: la aleta no se comprime (F.4.3.3-37).")
    beta = factor_beta(Lm, Lcr)
    Fd = beta * (kfe + kwe + kphi) / (kfg + kwg)                                        # F.4.3.3-37
    if not Fd > 0:
        raise ValueError(f"Fd = {Fd} no positivo (F.4.3.3-37).")
    y_ext_sup, y_ext_inf = g.hc + t / 2, -t / 2
    Sf = p.Ix / (y_ext_sup - p.yc)                                                       # fibra extrema comprimida
    Sfy = p.Ix / max(y_ext_sup - p.yc, p.yc - y_ext_inf)                                 # primera fluencia
    My, Mcrd = Sfy * Fy, Sf * Fd                                                         # F.4.3.3-31, -32
    lam = math.sqrt(My / Mcrd)                                                           # F.4.3.3-30
    if lam <= LAMBDA_D_FLEXION:
        Mn = My                                                                          # F.4.3.3-28
    else:
        q = math.sqrt(Mcrd / My)
        Mn = (1 - 0.22 * q) * q * My                                                     # F.4.3.3-29
    return ResultadoDistorsional(Fd=Fd, Lcr=Lcr, L=L, beta=beta, lambda_d=lam, nominal=Mn, phi=PHI_B_DISTORSIONAL,
                                 fluencia=My, critico=Mcrd,
                                 rigideces={"kphi_fe": kfe, "kphi_we": kwe, "kphi": kphi, "Kphi_fg": kfg,
                                            "Kphi_wg": kwg, "xi_web": xi})


def distorsional_compresion_c(g: GeometriaC, Fy: float, Lm: float, kphi: float = 0.0,
                              E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> ResultadoDistorsional:
    """Pn distorsional de una C en compresión: Fd por F.4.3.4-21 a -24; Pn por F.4.3.4-12/-13 con Py = Ag·Fy."""
    _validar(Lm, kphi, Fy)
    a = propiedades_aleta(g)
    G = E / (2 * (1 + mu))
    t, ho = g.t, g.H
    Lcr = ((6 * math.pi ** 4 * ho * (1 - mu ** 2) / t ** 3) * _termino_rigidez_aleta(a)) ** 0.25   # F.4.3.4-24
    L = min(Lcr, Lm)
    kfe = _kphi_fe(a, L, E, G)
    kwe = E * t ** 3 / (6 * ho * (1 - mu ** 2))                                          # F.4.3.4-22
    kfg = _kphi_fg(a, L)
    kwg = (math.pi / L) ** 2 * t * ho ** 3 / 60                                          # F.4.3.4-23
    beta = factor_beta(Lm, Lcr)
    Fd = beta * (kfe + kwe + kphi) / (kfg + kwg)                                         # F.4.3.4-21
    Ag = g.propiedades().A
    Py, Pcrd = Ag * Fy, Ag * Fd                                                          # F.4.3.4-15, -16
    lam = math.sqrt(Py / Pcrd)                                                           # F.4.3.4-14
    if lam <= LAMBDA_D_COMPRESION:
        Pn = Py                                                                          # F.4.3.4-12
    else:
        q = (Pcrd / Py) ** 0.6
        Pn = (1 - 0.25 * q) * q * Py                                                     # F.4.3.4-13
    return ResultadoDistorsional(Fd=Fd, Lcr=Lcr, L=L, beta=beta, lambda_d=lam, nominal=Pn, phi=PHI_C_DISTORSIONAL,
                                 fluencia=Py, critico=Pcrd,
                                 rigideces={"kphi_fe": kfe, "kphi_we": kwe, "kphi": kphi, "Kphi_fg": kfg,
                                            "Kphi_wg": kwg})
