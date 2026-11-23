"""Arrugamiento del alma sin huecos y su interacción con la flexión, NSR-10 F.4.3.3.4.1 y F.4.3.3.5.1(a). Issue #81.

Pn = C·t²·Fy·senθ·(1 − CR·√(R/t))·(1 + CN·√(N/t))·(1 − Ch·√(h/t)) (F.4.3.3-56).

Los coeficientes C, CR, CN, Ch y φw salen de la Tabla F.4.3.3-2 (C de alma sencilla) según la condición de apoyo, la
de la aleta y el caso de carga. El corpus del proyecto describe la tabla pero no trae sus valores. Por eso este módulo
no trae coeficientes de memoria: los recibe como entrada, con la fila de la tabla citada. Cuando la tabla esté
transcrita de la norma impresa, se carga en TABLA_F_4_3_3_2 y la entrada pasa a ser solo la fila.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

N_MIN_MM = 19.0            # F.4.3.3.4.1: longitud de apoyo mínima
H_T_MAX = 200.0            # Tabla F.4.3.3-2
N_T_MAX = 210.0
N_H_MAX = 2.0
PHI_INTERACCION = 0.90     # F.4.3.3-61

# Tabla F.4.3.3-2, pendiente de transcribir de la NSR-10 impresa (fila → CoeficientesArrugamiento).
TABLA_F_4_3_3_2: dict = {}


@dataclass(frozen=True)
class CoeficientesArrugamiento:
    C: float
    CR: float
    CN: float
    Ch: float
    phi_w: float
    R_t_max: float
    fila: str          # cita de la fila de la Tabla F.4.3.3-2 (apoyo, aleta, caso de carga)

    def __post_init__(self) -> None:
        for nombre in ("C", "CR", "CN", "Ch", "R_t_max"):
            v = getattr(self, nombre)
            if not (v >= 0 and math.isfinite(v)):
                raise ValueError(f"{nombre} = {v} inválido (Tabla F.4.3.3-2).")
        if not self.C > 0:
            raise ValueError("C debe ser positivo (Tabla F.4.3.3-2).")
        if not 0 < self.phi_w <= 1:
            raise ValueError(f"φw = {self.phi_w} fuera de (0, 1] (Tabla F.4.3.3-2).")
        if not self.fila.strip():
            raise ValueError("Cite la fila de la Tabla F.4.3.3-2 de donde salen los coeficientes.")


@dataclass(frozen=True)
class ResultadoArrugamiento:
    Pn: float        # N
    phi_w: float
    alfa: float      # F.4.3.3-58 (1 si no aplica el voladizo)
    relaciones: dict


def alfa_voladizo(Lo: float, h: float, t: float) -> float:
    """α de F.4.3.3-58 para carga de extremo sobre una aleta con voladizo. Vale 1 fuera de 0,5 ≤ Lo/h ≤ 1,5 o con
    h/t > 154 (F.4.3.3.4.1)."""
    for nombre, v in (("Lo", Lo), ("h", h), ("t", t)):
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido (F.4.3.3-58).")
    if not (0.5 <= Lo / h <= 1.5) or h / t > 154:
        return 1.0
    return max(1.0, 1.34 * (Lo / h) ** 0.26 / (0.009 * (h / t) + 0.3))


def arrugamiento_alma(h: float, t: float, Fy: float, N: float, R: float, coef: CoeficientesArrugamiento,
                      theta_grados: float = 90.0, Lo: float | None = None) -> ResultadoArrugamiento:
    """F.4.3.3-56 (y F.4.3.3-57 si se da Lo, para reacción de extremo sobre una aleta con voladizo).

    h = porción plana del alma; R = radio interior de doblez; N = longitud de apoyo. θ = 90° en la Tabla F.4.3.3-2.
    Con Lo, quien llama responde por que la fila sea de carga de extremo sobre una aleta y por que Pnc no supere el
    valor de carga interior (F.4.3.3.4.1)."""
    norma = "NSR-10 F.4.3.3.4.1"
    for nombre, v in (("h", h), ("t", t), ("Fy", Fy), ("N", N)):
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido: debe ser positivo ({norma}).")
    if not (R >= 0 and math.isfinite(R)):
        raise ValueError(f"R = {R} inválido ({norma}).")
    if theta_grados != 90.0:
        raise ValueError("La Tabla F.4.3.3-2 (C de alma sencilla) exige θ = 90°.")
    rel = {"h_t": h / t, "N_t": N / t, "N_h": N / h, "R_t": R / t}
    if N < N_MIN_MM:
        raise ValueError(f"N = {N} mm < {N_MIN_MM:.0f} mm, la longitud de apoyo mínima ({norma}).")
    for clave, lim, nombre in (("h_t", H_T_MAX, "h/t"), ("N_t", N_T_MAX, "N/t"), ("N_h", N_H_MAX, "N/h"),
                               ("R_t", coef.R_t_max, "R/t")):
        if rel[clave] > lim:
            raise ValueError(f"{nombre} = {rel[clave]:.2f} > {lim:g}: fuera de la Tabla F.4.3.3-2 ({coef.fila}).")
    Pn = (coef.C * t * t * Fy * math.sin(math.radians(theta_grados)) * (1 - coef.CR * math.sqrt(R / t))
          * (1 + coef.CN * math.sqrt(N / t)) * (1 - coef.Ch * math.sqrt(h / t)))
    if not Pn > 0:
        raise ValueError(f"Pn = {Pn} no positivo: coeficientes incompatibles con la geometría ({coef.fila}).")
    alfa = alfa_voladizo(Lo, h, t) if Lo is not None else 1.0
    return ResultadoArrugamiento(Pn=alfa * Pn, phi_w=coef.phi_w, alfa=alfa, relaciones=rel)


def interaccion_flexion_arrugamiento(Pu: float, Mu: float, Pn: float, Mnxo: float) -> float:
    """0,91·(P̄/Pn) + M̄/Mnxo ≤ 1,33·φ, φ = 0,90 (F.4.3.3-61), alma sencilla no reforzada. Devuelve la razón respecto
    a 1,33·φ (≤ 1 cumple)."""
    for nombre, v in (("Pu", Pu), ("Mu", Mu)):
        if not (v >= 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido: use la magnitud (F.4.3.3-61).")
    for nombre, v in (("Pn", Pn), ("Mnxo", Mnxo)):
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido (F.4.3.3-61).")
    return (0.91 * Pu / Pn + Mu / Mnxo) / (1.33 * PHI_INTERACCION)
