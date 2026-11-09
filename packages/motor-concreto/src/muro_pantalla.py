"""Pantalla, bandeja de alivio y dentellón del muro de contención en voladizo (Fase 3b): acciones por franja de 1 m y verificación de secciones.

Combinaciones (leídas en B.2.4.2, 2026-11-08): A = B.2.4-2 con sobrecarga como L: 1,2 D + 1,6 L + 1,6 H; S = B.2.4-7: 0,9 D + 1,0 E + 1,6 H, con E×1,4 porque las
fuerzas seudoestáticas parten de a_max sin reducir por R (B.2.4.2.4: «se puede usar 1.4E cuando E se basa en niveles de servicio») — interpretación mía (HIPÓTESIS).

HIPÓTESIS de investigación (no vienen de la NSR-10): empuje de Rankine y Mononobe-Okabe; el incremento dinámico se reparte en un trapecio con resultante a 0,6 h; la
bandeja «sombrea» al muro: bajo la cara inferior de la bandeja el empuje de la columna de suelo y sobrecarga situada sobre ella se anula y recupera linealmente en una
profundidad vuelo·tan(45° + φ/2); el contramomento de la carga sobre la bandeja usa 0,9 D y NO incluye sobrecarga (conservador); el dentellón se diseña como voladizo con
la fuerza que le falta a la fricción simple para alcanzar el FS exigido (H.6.7(c) lista dentellones reforzados; H.6.7(b) prohíbe contar el empuje pasivo).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .muro_contencion import (GAMMA_CONCRETO_KN_M3, GeometriaMuro, Relleno, SueloApoyo, coeficiente_activo_mononobe_okabe,
                              coeficiente_activo_rankine, mu_efectivo)
from .muro_refuerzo import Franja, franja, phi_mn_knm, phi_vc_kn, recubrimiento, suelo, as_min_flexion
from .viga import Materiales

FACTOR_H = 1.6
FACTOR_D_FAVORABLE = 0.9
FACTOR_E_SERVICIO = 1.4
N_SECCIONES = 8
N_INTEG = 201


@dataclass(frozen=True)
class SeccionPantalla:
    y_m: float
    t_mm: float
    d_mm: float
    mu_knm_m: float
    vu_kn_m: float
    phi_mn_knm_m: float
    phi_vc_kn_m: float
    cumple: bool


def _sigma(g: GeometriaMuro, r: Relleno, z, con_q: bool):
    """Presión horizontal estática [kPa] a profundidad z bajo la corona, con el sombreado de la bandeja si existe."""
    ka, cb = coeficiente_activo_rankine(r.phi_deg, r.beta_deg), math.cos(math.radians(r.beta_deg))
    q = r.sobrecarga_kpa if con_q else 0.0
    z = np.asarray(z, dtype=float)
    sig = ka * cb * (r.gamma * z + q)
    if g.tiene_bandeja:
        z_b = g.h_pantalla - g.bandeja_y
        z_t = z_b - g.bandeja_esp
        y_sh = g.bandeja_vuelo * math.tan(math.radians(45.0 + r.phi_deg / 2.0))
        recup = np.clip(1.0 - (z - z_b) / y_sh, 0.0, 1.0) * (z >= z_b)
        sig = sig - ka * cb * (r.gamma * z_t + q) * recup
    return sig


def _mv(sigma_fn, z_k: float, cortes: tuple[float, ...] = ()) -> tuple[float, float]:
    """(V, M respecto de la sección a profundidad z_k) de una presión sigma(z) de la corona a z_k; integra por tramos entre las discontinuidades `cortes`."""
    if z_k <= 0:
        return 0.0, 0.0
    puntos = [0.0] + sorted(c for c in cortes if 0.0 < c < z_k) + [z_k]
    eps = 1e-9
    v = m = 0.0
    for a, b in zip(puntos[:-1], puntos[1:]):
        z = np.linspace(a, b, N_INTEG)
        s = sigma_fn(np.clip(z, a + eps, b - eps))
        v += float(np.trapezoid(s, z))
        m += float(np.trapezoid(s * (z_k - z), z))
    return v, m


def _cortes(g: GeometriaMuro) -> tuple[float, ...]:
    return (g.h_pantalla - g.bandeja_y,) if g.tiene_bandeja else ()


def _dinamico(g: GeometriaMuro, r: Relleno, kh: float):
    """Presión dinámica trapezoidal (σ_top = 4 σ_base, resultante a 0,6 h desde la base) sobre la pantalla y su incremento ΔP [kN/m]."""
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    kae = coeficiente_activo_mononobe_okabe(r.phi_deg, r.beta_deg, kh)
    if math.isinf(kae):
        return None
    h = g.h_pantalla
    dp = 0.5 * r.gamma * (kae - ka) * h * h * math.cos(math.radians(r.beta_deg))
    s1 = 0.4 * dp / h
    return lambda z: 4.0 * s1 + (s1 - 4.0 * s1) * np.asarray(z) / h


def _inercia(g: GeometriaMuro, kh: float, y_k: float, gamma_c: float) -> tuple[float, float]:
    """(V, M) de la inercia horizontal kh·γc·t(y) de la pantalla por encima de la sección y_k."""
    if y_k >= g.h_pantalla:
        return 0.0, 0.0
    y = np.linspace(y_k, g.h_pantalla, N_INTEG)
    dw = kh * gamma_c * g.espesor_pantalla(y)
    return float(np.trapezoid(dw, y)), float(np.trapezoid(dw * (y - y_k), y))


def _contramomento(g: GeometriaMuro, r: Relleno, y_k: float, gamma_c: float) -> float:
    """Momento favorable de la carga permanente sobre la bandeja respecto del eje de la sección y_k (kN·m/m, sin factor)."""
    if not g.tiene_bandeja or y_k >= g.bandeja_y:
        return 0.0
    z_t = g.h_pantalla - g.bandeja_y - g.bandeja_esp
    carga = (r.gamma * z_t + gamma_c * g.bandeja_esp) * g.bandeja_vuelo
    x_carga = g.b_puntera + float(g.espesor_pantalla(g.bandeja_y)) + g.bandeja_vuelo / 2.0
    x_eje = g.b_puntera + float(g.espesor_pantalla(y_k)) / 2.0
    return carga * (x_carga - x_eje)


def acciones_pantalla(g: GeometriaMuro, r: Relleno, y_k: float, kh: float | None, gamma_c: float = GAMMA_CONCRETO_KN_M3) -> tuple[float, float]:
    """(Mu, Vu) de la sección a altura y_k sobre la base de la pantalla: envolvente de A (estática) y S (sísmica, si kh no es None)."""
    z_k = g.h_pantalla - y_k
    v_a, m_a = _mv(lambda z: _sigma(g, r, z, True), z_k, _cortes(g))
    contra = FACTOR_D_FAVORABLE * _contramomento(g, r, y_k, gamma_c)
    mu = max(FACTOR_H * m_a - contra, 0.0)
    vu = FACTOR_H * v_a
    if kh is not None:
        din = _dinamico(g, r, kh)
        if din is None:
            return math.inf, math.inf
        v_s, m_s = _mv(lambda z: _sigma(g, r, z, False), z_k, _cortes(g))
        v_d, m_d = _mv(din, z_k)
        v_i, m_i = _inercia(g, kh, y_k, gamma_c)
        mu = max(mu, FACTOR_H * m_s + FACTOR_E_SERVICIO * (m_d + m_i) - contra)
        vu = max(vu, FACTOR_H * v_s + FACTOR_E_SERVICIO * (v_d + v_i))
    return mu, vu


def disenar_pantalla(g: GeometriaMuro, r: Relleno, m: Materiales, kh: float | None = None) -> tuple[Franja, list[SeccionPantalla]]:
    """Refuerzo vertical de la base (toda la altura, sin cortar barras) y verificación de las secciones superiores con ese refuerzo."""
    mu0, vu0 = acciones_pantalla(g, r, 0.0, kh)
    if math.isinf(mu0):
        f = Franja("pantalla", mu0, vu0, g.t_base * 1000.0, 0.0, "-", 0.0, math.inf, math.inf, 0.0, 0.0, 0.0, False, ("pantalla: Mononobe-Okabe sin solución",))
        return f, []
    base = franja("pantalla", mu0, vu0, g.t_base * 1000.0, recubrimiento, m)
    if not base.cumple and base.dia == "-":
        return base, []
    from .viga import DIAMETRO_MM
    secciones: list[SeccionPantalla] = []
    motivos = list(base.motivos)
    for k in range(N_SECCIONES):
        y = g.h_pantalla * k / N_SECCIONES
        mu, vu = acciones_pantalla(g, r, y, kh)
        t_mm = float(g.espesor_pantalla(y)) * 1000.0
        d = t_mm - recubrimiento(base.dia) - DIAMETRO_MM[base.dia] / 2.0
        pmn, eps = phi_mn_knm(base.as_prov_mm2_m, d, m)
        pvc = phi_vc_kn(d, m)
        ok = mu <= pmn * 1.0001 and vu <= pvc and eps >= 0.005 and base.as_prov_mm2_m >= as_min_flexion(d, m.fc, m.fy) * 0.9999
        secciones.append(SeccionPantalla(y, t_mm, d, mu, vu, pmn, pvc, ok))
        if not ok and k > 0:
            motivos.append(f"pantalla y = {y:.2f} m: Mu {mu:.1f} / φMn {pmn:.1f} kN·m/m, Vu {vu:.1f} / φVc {pvc:.1f} kN/m")
    return Franja(base.nombre, base.mu_knm_m, base.vu_kn_m, base.h_mm, base.d_mm, base.dia, base.sep_mm, base.as_req_mm2_m, base.as_prov_mm2_m,
                  base.as_min_mm2_m, base.eps_t, base.phi_vc_kn_m, not motivos, tuple(motivos)), secciones


def disenar_bandeja(g: GeometriaMuro, r: Relleno, m: Materiales, gamma_c: float = GAMMA_CONCRETO_KN_M3) -> Franja | None:
    """Losa en voladizo desde la pantalla, tracción en la cara superior: wu = 1,2 (γ·z + γc·e) + 1,6 q."""
    if not g.tiene_bandeja:
        return None
    z_t = g.h_pantalla - g.bandeja_y - g.bandeja_esp
    wu = 1.2 * (r.gamma * z_t + gamma_c * g.bandeja_esp) + 1.6 * r.sobrecarga_kpa
    h_mm = g.bandeja_esp * 1000.0
    d_est = h_mm - 50.0 - 8.0
    mu = wu * g.bandeja_vuelo**2 / 2.0
    vu = wu * max(g.bandeja_vuelo - d_est / 1000.0, 0.0)
    return franja("bandeja", mu, vu, h_mm, recubrimiento, m, 0.0018 * h_mm * 1000.0)


def disenar_dentellon(g: GeometriaMuro, ph_servicio: float, v_servicio: float, ph_sismico: float | None, v_sismico: float | None,
                      s: SueloApoyo, m: Materiales) -> Franja | None:
    """Voladizo de profundidad d_k cargado por la fuerza que la fricción simple (tan 2φ/3) no alcanza a dar para el FS exigido."""
    if not g.tiene_dentellon:
        return None
    mu_simple = s.mu
    b = g.ancho_base
    fk = max(1.60 * ph_servicio - (v_servicio * mu_simple + s.c_kpa * b), 0.0)
    if ph_sismico is not None and v_sismico is not None:
        fk = max(fk, 1.05 * ph_sismico - (v_sismico * mu_simple + s.c_kpa * b))
    mu_k = fk * g.dentellon_prof / 2.0
    return franja("dentellon", mu_k, fk, g.dentellon_ancho * 1000.0, suelo, m, 0.0018 * g.dentellon_ancho * 1e6)
