"""Tensión, cortante y compresión de miembros formados en frío, NSR-10 F.4.3.2, F.4.3.3.2.1 y F.4.3.4.1. Issue #81."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .ancho_efectivo import E_ACERO_MPA, K_RIGIDIZADO, MU_ACERO, ancho_efectivo
from .elementos import H_T_MAX_ALMA, aleta_con_pestana, no_rigidizado_uniforme
from .seccion import GeometriaC

PHI_T_FLUENCIA = 0.90     # F.4.3.2-1
PHI_T_ROTURA = 0.75       # F.4.3.2-2
PHI_V = 0.95              # F.4.3.3.2.1
PHI_C = 0.85              # F.4.3.4.1
KV_SIN_REFUERZO = 5.34    # F.4.3.3.2.1 (1)
LAMBDA_C_LIMITE = 1.5     # F.4.3.4-2 / -3


def _pos(nombre: str, v: float, norma: str) -> None:
    if not (v > 0 and math.isfinite(v)):
        raise ValueError(f"{nombre} = {v} inválido: debe ser positivo y finito ({norma}).")


# ── Tensión (F.4.3.2) ─────────────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ResultadoTension:
    phi_Tn: float          # N, resistencia de diseño (el menor de a y b)
    Tn_fluencia: float     # N
    Tn_rotura: float       # N
    gobierna: str


def resistencia_tension(Ag: float, An: float, Fy: float, Fu: float) -> ResultadoTension:
    """a) Tn = Ag·Fy, φ = 0.90 (F.4.3.2-1); b) Tn = An·Fu, φ = 0.75 (F.4.3.2-2). El estado c) (rotura en la
    conexión, F.4.5) no se verifica aquí. An es obligatoria: no se supone igual a Ag."""
    for nombre, v in (("Ag", Ag), ("An", An), ("Fy", Fy), ("Fu", Fu)):
        _pos(nombre, v, "NSR-10 F.4.3.2")
    if An > Ag:
        raise ValueError("El área neta An no puede exceder el área bruta Ag (NSR-10 F.4.3.2).")
    tf, tr = Ag * Fy, An * Fu
    a, b = PHI_T_FLUENCIA * tf, PHI_T_ROTURA * tr
    return ResultadoTension(min(a, b), tf, tr, "fluencia_seccion_bruta" if a <= b else "rotura_seccion_neta")


# ── Cortante de almas sin huecos (F.4.3.3.2.1) ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ResultadoCortante:
    Vn: float     # N
    phi_v: float
    Fv: float     # MPa
    kv: float
    rango: str


def coeficiente_kv(a_sobre_h: float | None) -> float:
    """kv = 5.34 sin rigidizadores; con rigidizadores transversales que cumplan F.4.3.3.7: F.4.3.3-49 / -50."""
    if a_sobre_h is None:
        return KV_SIN_REFUERZO
    _pos("a/h", a_sobre_h, "NSR-10 F.4.3.3.2.1")
    if a_sobre_h <= 1.0:
        return 4.00 + 5.34 / a_sobre_h ** 2
    return 5.34 + 4.00 / a_sobre_h ** 2


def resistencia_cortante(h: float, t: float, Fy: float, kv: float = KV_SIN_REFUERZO,
                         E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> ResultadoCortante:
    """Vn = Aw·Fv (F.4.3.3-44), Aw = h·t (F.4.3.3-48). h = altura de la porción plana del alma."""
    for nombre, v in (("h", h), ("t", t), ("Fy", Fy), ("kv", kv), ("E", E)):
        _pos(nombre, v, "NSR-10 F.4.3.3.2.1")
    if h / t > H_T_MAX_ALMA and kv == KV_SIN_REFUERZO:
        raise ValueError(f"h/t = {h / t:.1f} > {H_T_MAX_ALMA:.0f} en alma no reforzada (NSR-10 F.4.2.1.2).")
    esb, lim = h / t, math.sqrt(E * kv / Fy)
    if esb <= lim:
        Fv, rango = 0.60 * Fy, "fluencia"                                         # F.4.3.3-45
    elif esb <= 1.51 * lim:
        Fv, rango = 0.60 * math.sqrt(E * kv * Fy) / esb, "pandeo_inelastico"      # F.4.3.3-46
    else:
        Fv, rango = math.pi ** 2 * E * kv / (12 * (1 - mu ** 2) * esb ** 2), "pandeo_elastico"   # F.4.3.3-47a
    return ResultadoCortante(Vn=h * t * Fv, phi_v=PHI_V, Fv=Fv, kv=kv, rango=rango)


# ── Compresión concéntrica (F.4.3.4.1) ────────────────────────────────────────────────────────────────────

def esfuerzo_nominal_compresion(Fy: float, Fe: float) -> tuple[float, float]:
    """Fn por F.4.3.4-2 (λc ≤ 1.5) o F.4.3.4-3 (λc > 1.5), con λc = √(Fy/Fe) (F.4.3.4-4). Devuelve (Fn, λc)."""
    _pos("Fy", Fy, "NSR-10 F.4.3.4.1")
    _pos("Fe", Fe, "NSR-10 F.4.3.4.1")
    lam = math.sqrt(Fy / Fe)
    Fn = (0.658 ** (lam ** 2)) * Fy if lam <= LAMBDA_C_LIMITE else (0.877 / lam ** 2) * Fy
    return Fn, lam


def fe_flexo_torsional(sigma_ex: float, sigma_t: float, xo: float, ro: float) -> float:
    """F.4.3.4-6, con β = 1 − (xo/ro)² (F.4.3.4-8). Sección de simetría sencilla con x como eje de simetría."""
    for nombre, v in (("σex", sigma_ex), ("σt", sigma_t), ("ro", ro)):
        _pos(nombre, v, "NSR-10 F.4.3.4.1.2")
    beta = 1 - (xo / ro) ** 2
    if not 0 < beta <= 1:
        raise ValueError(f"β = {beta} fuera de (0, 1] (NSR-10 F.4.3.4-8).")
    s = sigma_ex + sigma_t
    return (s - math.sqrt(s * s - 4 * beta * sigma_ex * sigma_t)) / (2 * beta)


@dataclass(frozen=True)
class ResultadoCompresion:
    Pn: float              # N
    phi_c: float
    Fn: float              # MPa
    Fe: float              # MPa
    lambda_c: float
    modo: str              # "flexion_eje_debil" | "flexo_torsional"
    Ae: float              # mm²
    A: float               # mm²
    sigma_ey: float
    sigma_ex: float
    sigma_t: float
    esbeltez_max: float


def area_efectiva_compresion_c(g: GeometriaC, f: float, E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> float:
    """Ae bajo compresión uniforme f: alma rigidizada k = 4 (F.4.2.2.1), aletas con pestaña (F.4.2.4) y pestañas
    no rigidizadas k = 0.43 (F.4.2.3.1). Para C sin pestaña, aletas no rigidizadas (F.4.2.3.1)."""
    t = g.t
    perdida = g.w_alma - ancho_efectivo(K_RIGIDIZADO, f, g.w_alma, t, E, mu)
    if g.con_pestana:
        ds_prima = no_rigidizado_uniforme(f, g.d_pestana, t, E, mu)
        al = aleta_con_pestana(f, g.w_aleta, t, g.d_pestana, g.D, ds_prima, E, mu)
        perdida += 2 * ((g.w_aleta - al.b1 - al.b2) + (g.d_pestana - al.ds))
    else:
        perdida += 2 * (g.w_aleta - no_rigidizado_uniforme(f, g.w_aleta, t, E, mu))
    return g.propiedades().A - perdida * t


def resistencia_compresion_c(g: GeometriaC, Fy: float, KxLx: float, KyLy: float, KtLt: float,
                             E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> ResultadoCompresion:
    """Pn = Ae·Fn (F.4.3.4-1). Fe = mínimo entre pandeo flector alrededor del eje débil (F.4.3.4-5) y pandeo
    flexo-torsional (F.4.3.4-6). El eje de simetría de la C (horizontal) es el «x» de la norma.
    G = E/(2(1+μ)) (el corpus no fija G para F.4). NO verifica pandeo distorsional (F.4.3.4.2)."""
    for nombre, v in (("Fy", Fy), ("KxLx", KxLx), ("KyLy", KyLy), ("KtLt", KtLt)):
        _pos(nombre, v, "NSR-10 F.4.3.4")
    p = g.propiedades()
    G = E / (2 * (1 + mu))
    sigma_ey = math.pi ** 2 * E / (KyLy / p.ry) ** 2                                       # F.4.3.4-5, eje débil
    sigma_ex = math.pi ** 2 * E / (KxLx / p.rx) ** 2
    sigma_t = (G * p.J + math.pi ** 2 * E * p.Cw / KtLt ** 2) / (p.A * p.ro ** 2)         # F.4.3.3-15
    fe_ft = fe_flexo_torsional(sigma_ex, sigma_t, p.xo, p.ro)
    Fe, modo = (sigma_ey, "flexion_eje_debil") if sigma_ey <= fe_ft else (fe_ft, "flexo_torsional")
    Fn, lam = esfuerzo_nominal_compresion(Fy, Fe)
    Ae = area_efectiva_compresion_c(g, Fn, E, mu)
    return ResultadoCompresion(Pn=Ae * Fn, phi_c=PHI_C, Fn=Fn, Fe=Fe, lambda_c=lam, modo=modo, Ae=Ae, A=p.A,
                               sigma_ey=sigma_ey, sigma_ex=sigma_ex, sigma_t=sigma_t,
                               esbeltez_max=max(KxLx / p.rx, KyLy / p.ry))
