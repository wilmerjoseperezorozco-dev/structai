"""Muro de contención en voladizo, por metro de longitud: diseño estructural de pantalla, puntera y talón (Fase 2) + costo APU y CO₂.

Verificado en el corpus `nsr10_chunks` el 2026-11-08: C.9.2.1 (1,6 H), C.14.1.2 (muro en voladizo por flexión C.10), C.14.3.2-3-4 (cuantías mínimas
vertical/horizontal y dos capas si t > 250 mm), C.10.5.1 (As mín de flexión), C.7.7.1 (recubrimientos), C.11.1.3 (sección crítica de cortante), C.11.2.1.1
(Vc = 0,17 λ √f'c b d), C.9.3.2 (φ flexión 0,90, cortante 0,75), C.10.5.4/C.7.12.2.1 (ρ 0,0018 en zapata).

HIPÓTESIS (no son numerales leídos): las combinaciones A = 1,2 D + 1,6 H + 1,6 Q y B = 0,9 D + 1,6 H (sin sobrecarga) aplicadas a las presiones de contacto;
el empuje activo y su separación en parte de suelo (H) y de sobrecarga (Q, viva) vienen de Rankine (ver `muro_contencion`).

NO verificado (se devuelve en `SUPUESTOS`): longitud de desarrollo y empalmes (C.12), corte de barras en altura (se arma toda la altura con el As de la base),
punzonamiento/cortante por fricción en la unión pantalla-zapata, fisuración y control de grietas, juntas, drenaje, estabilidad general, asentamientos.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .economia_concreto import Economia, co2_m3, costo_m3
from .muro_contencion import (GAMMA_CONCRETO_KN_M3, GeometriaMuro, Relleno, ResultadoEstabilidad, SueloApoyo, _cargas_verticales,
                              coeficiente_activo_rankine, verificar_estabilidad)
from .viga import AREA_MM2, DIAMETRO_MM, EPS_T_MIN, PHI_CORTANTE, PHI_FLEXION, Materiales, beta1
from .zapata import _as_flexion

FACTOR_H = 1.6                       # C.9.2.1
FACTOR_D_A, FACTOR_D_B = 1.2, 0.9
FACTOR_Q = 1.6
COBERTURA_SUELO_MM = 75.0            # C.7.7.1(a)
DENSIDAD_ACERO_KG_M3 = 7850.0
RHO_ZAPATA_MIN = 0.0018              # C.10.5.4 / C.7.12.2.1 con fy 420
SEP_MAX_ABS_MM = 450.0
N_INTEG = 401

SUPUESTOS = (
    "Combinaciones A (1,2D+1,6H+1,6Q) y B (0,9D+1,6H) son HIPÓTESIS de aplicación de C.9.2.1; no se leyó B.2.",
    "Longitud de desarrollo, empalmes y ganchos (C.12) NO verificados; solo se informa el largo disponible.",
    "La pantalla se arma en toda su altura con el refuerzo de la base (sin corte de barras): conservador en cantidad de acero.",
    "Cortante de la pantalla en la cara de la zapata (no a d); cortante del talón en la cara de la pantalla; cortante de la puntera a d de la cara.",
    "El relleno sobre la puntera no se descuenta (conservador para el momento de la puntera).",
    "Sin verificación de fisuración, juntas de contracción, drenaje, estabilidad general ni asentamientos.",
)


@dataclass(frozen=True)
class Franja:
    """Refuerzo de una franja de 1 m."""
    nombre: str
    mu_knm_m: float
    vu_kn_m: float
    h_mm: float
    d_mm: float
    dia: str
    sep_mm: float
    as_req_mm2_m: float
    as_prov_mm2_m: float
    as_min_mm2_m: float
    eps_t: float
    phi_vc_kn_m: float
    cumple: bool
    motivos: tuple[str, ...]


@dataclass(frozen=True)
class DisenoMuro:
    cumple: bool
    motivos: tuple[str, ...]
    estabilidad: ResultadoEstabilidad
    pantalla: Franja | None
    puntera: Franja | None
    talon: Franja | None
    acero_horizontal_pantalla: str
    acero_vertical_frontal_pantalla: str
    acero_kg_m: float
    concreto_m3_m: float
    encofrado_m2_m: float
    costo_cop_m: float
    co2_kg_m: float
    supuestos: tuple[str, ...] = SUPUESTOS


# --------------------------------------------------------------------------------------------- acciones
def _empujes(g: GeometriaMuro, r: Relleno) -> dict[str, float]:
    """Componentes horizontales/verticales del empuje (kN/m) separados en suelo (H) y sobrecarga (Q), con sus brazos desde la base de la zapata."""
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    b = math.radians(r.beta_deg)
    B = g.ancho_base
    h = g.h_zapata + g.h_pantalla + (B - g.b_puntera - g.t_corona) * math.tan(b)
    h_eq = r.sobrecarga_kpa / r.gamma
    pa_s = 0.5 * ka * r.gamma * h * h
    pa_q = ka * r.gamma * h * h_eq
    return {"ka": ka, "h": h, "ph_s": pa_s * math.cos(b), "pv_s": pa_s * math.sin(b), "ph_q": pa_q * math.cos(b),
            "pv_q": pa_q * math.sin(b), "arm_s": h / 3.0, "arm_q": h / 2.0}


def _presion(g: GeometriaMuro, r: Relleno, gamma_c: float, f_d: float, f_q: float):
    """Presión de contacto mayorada q(x) [kPa] en x desde la punta, y (q_punta, q_talon). None si la resultante cae fuera de la base."""
    e = _empujes(g, r)
    B = g.ancho_base
    x_top = g.b_puntera + g.t_corona
    cargas = _cargas_verticales(g, r, gamma_c)
    q_tal = f_q * r.sobrecarga_kpa * (B - x_top)
    x_q = x_top + (B - x_top) / 2.0
    v = f_d * sum(f for _, f, _ in cargas) + FACTOR_H * e["pv_s"] + f_q * e["pv_q"] + q_tal
    m_est = (f_d * sum(f * x for _, f, x in cargas) + FACTOR_H * e["pv_s"] * B + f_q * e["pv_q"] * B + q_tal * x_q)
    m_vol = FACTOR_H * e["ph_s"] * e["arm_s"] + f_q * e["ph_q"] * e["arm_q"]
    x_r = (m_est - m_vol) / v
    if x_r <= 0.0:
        return None
    if B / 2.0 - x_r <= B / 6.0:
        e_exc = B / 2.0 - x_r
        qa, qb = v / B * (1 + 6 * e_exc / B), v / B * (1 - 6 * e_exc / B)
        return (lambda x: qa + (qb - qa) * np.asarray(x) / B), qa, qb, v
    q_max = 2.0 * v / (3.0 * x_r)
    return (lambda x: np.clip(q_max * (1 - np.asarray(x) / (3.0 * x_r)), 0.0, None)), q_max, 0.0, v


# --------------------------------------------------------------------------------------------- flexión
def _recubrimiento(dia: str) -> float:
    return 40.0 if dia in ("3", "4", "5") else 50.0       # C.7.7.1(b)


def _as_min_flexion(d_mm: float, fc: float, fy: float, b_mm: float = 1000.0) -> float:
    return max(0.25 * math.sqrt(fc) / fy, 1.4 / fy) * b_mm * d_mm            # C.10.5.1 (C.10-3)


def _elegir_barras(mu_knm: float, h_mm: float, cobertura, fc: float, fy: float, as_min_extra: float = 0.0):
    """Menor As provisto (por m) que cumple flexión, εt ≥ 0,005, As mín y separación; devuelve (dia, s, As_prov, d, As_req, As_min, eps_t) o None."""
    s_max = min(3 * h_mm, SEP_MAX_ABS_MM)
    mejor = None
    for dia in ("4", "5", "6", "7", "8"):
        db, a1 = DIAMETRO_MM[dia], AREA_MM2[dia]
        d = h_mm - cobertura(dia) - db / 2.0
        if d <= 0:
            continue
        as_req = _as_flexion(mu_knm, 1000.0, d, fc, fy)
        as_min = max(_as_min_flexion(d, fc, fy), as_min_extra)
        if math.isinf(as_req):
            continue
        as_need = max(as_req, as_min)
        s = min(math.floor(1000.0 * a1 / as_need / 10.0) * 10.0, s_max)
        if s < db + max(db, 25.0):
            continue
        as_prov = 1000.0 * a1 / s
        a = as_prov * fy / (0.85 * fc * 1000.0)
        c = a / beta1(fc)
        eps = 0.003 * (d - c) / c
        if eps < EPS_T_MIN:
            continue
        if mejor is None or as_prov < mejor[2]:
            mejor = (dia, s, as_prov, d, as_req, as_min, eps)
    return mejor


def _franja(nombre: str, mu: float, vu: float, h_mm: float, cobertura, m: Materiales, as_min_extra: float = 0.0) -> Franja:
    sel = _elegir_barras(mu, h_mm, cobertura, m.fc, m.fy, as_min_extra)
    if sel is None:
        return Franja(nombre, mu, vu, h_mm, 0.0, "-", 0.0, math.inf, math.inf, 0.0, 0.0, 0.0, False, (f"{nombre}: no hay arreglo de barras que cumpla (espesor insuficiente)",))
    dia, s, as_prov, d, as_req, as_min, eps = sel
    phi_vc = PHI_CORTANTE * 0.17 * math.sqrt(m.fc) * 1000.0 * d / 1000.0
    motivos = (() if vu <= phi_vc else (f"{nombre}: cortante Vu {vu:.1f} kN/m > φVc {phi_vc:.1f} kN/m (C.11.2.1.1)",))
    return Franja(nombre, mu, vu, h_mm, d, dia, s, as_req, as_prov, as_min, eps, phi_vc, not motivos, motivos)


# --------------------------------------------------------------------------------------------- secciones
def _pantalla(g: GeometriaMuro, r: Relleno, m: Materiales) -> Franja:
    """Pantalla en la base: Mu = 1,6 [Ph_s·h/3 + Ph_q·h/2] con h = altura de la pantalla (profundidad medida desde la corona)."""
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    cb = math.cos(math.radians(r.beta_deg))
    h = g.h_pantalla
    ph_s = 0.5 * ka * r.gamma * h * h * cb
    ph_q = ka * r.sobrecarga_kpa * h * cb
    vu = FACTOR_H * (ph_s + ph_q)
    mu = FACTOR_H * (ph_s * h / 3.0 + ph_q * h / 2.0)
    return _franja("pantalla", mu, vu, g.t_base * 1000.0, _recubrimiento, m)


def _integral(f, a: float, b: float) -> float:
    if b <= a:
        return 0.0
    x = np.linspace(a, b, N_INTEG)
    return float(np.trapezoid(f(x), x))


def _cargas_zapata(g: GeometriaMuro, r: Relleno, gamma_c: float, f_d: float, f_q: float):
    """Presión q(x), carga descendente w(x) sobre el talón y propio de la zapata. None si no hay equilibrio."""
    p = _presion(g, r, gamma_c, f_d, f_q)
    if p is None:
        return None
    q, _, _, _ = p
    x_top = g.b_puntera + g.t_corona
    tan_b = math.tan(math.radians(r.beta_deg))
    propio = f_d * gamma_c * g.h_zapata

    def w_talon(x):
        x = np.asarray(x)
        return propio + f_d * r.gamma * (g.h_pantalla + (x - x_top) * tan_b) + f_q * r.sobrecarga_kpa

    return q, w_talon, propio


def _momentos_zapata(g: GeometriaMuro, r: Relleno, gamma_c: float, d_punt: float) -> dict[str, float]:
    """Envolvente (A y B) de Mu y Vu de puntera (cara de pantalla, cortante a d) y talón (cara posterior de la pantalla)."""
    x_h = g.b_puntera + g.t_base
    B = g.ancho_base
    sal = {"mu_p": 0.0, "vu_p": 0.0, "mu_t": 0.0, "vu_t": 0.0, "mu_t_inf": 0.0}
    for f_d, f_q in ((FACTOR_D_A, FACTOR_Q), (FACTOR_D_B, 0.0)):
        c = _cargas_zapata(g, r, gamma_c, f_d, f_q)
        if c is None:
            return {**sal, "sin_equilibrio": 1.0}
        q, w_talon, propio = c
        bp = g.b_puntera
        sal["mu_p"] = max(sal["mu_p"], _integral(lambda x: (q(x) - propio) * (bp - x), 0.0, bp))
        sal["vu_p"] = max(sal["vu_p"], _integral(lambda x: q(x) - propio, 0.0, max(bp - d_punt, 0.0)))
        neto = lambda x: w_talon(x) - q(x)
        mt = _integral(lambda x: neto(x) * (x - x_h), x_h, B)
        sal["mu_t"] = max(sal["mu_t"], mt)
        sal["mu_t_inf"] = max(sal["mu_t_inf"], -mt)
        sal["vu_t"] = max(sal["vu_t"], abs(_integral(neto, x_h, B)))
    return sal


def _acero_pantalla_secundario(g: GeometriaMuro, m: Materiales) -> tuple[str, str, float, float]:
    """(texto horizontal, texto vertical frontal, As_h total mm²/m de altura, As_v frontal mm²/m) con C.14.3.2-3-4."""
    t_prom = (g.t_corona + g.t_base) / 2.0 * 1000.0
    cap = 2 if t_prom > 250.0 else 1                                            # C.14.3.4
    rho_h = 0.0020 if m.fy >= 420 else 0.0025                                   # C.14.3.3, ≤ #5 con fy ≥ 420
    rho_v = 0.0012 if m.fy >= 420 else 0.0015                                   # C.14.3.2
    a_h, a_v = rho_h * t_prom * 1000.0, rho_v * t_prom * 1000.0 / cap
    s_max = min(3 * t_prom, SEP_MAX_ABS_MM)

    def texto(a_total: float, capas: int) -> str:
        a_capa = a_total / capas
        s = min(math.floor(1000.0 * AREA_MM2["4"] / a_capa / 10.0) * 10.0, s_max)
        return f"#4 c/{int(s)} mm × {capas} capa(s)"
    return texto(a_h, cap), texto(a_v * cap, cap), a_h, a_v * cap


# --------------------------------------------------------------------------------------------- diseño completo
def _kg_acero(g: GeometriaMuro, pant: Franja, punt: Franja, tal: Franja, a_h: float, a_v_front: float) -> float:
    B = g.ancho_base
    v_pant = pant.as_prov_mm2_m * 1e-6 * (g.h_pantalla + g.h_zapata) + a_v_front * 1e-6 * g.h_pantalla
    v_h = a_h * 1e-6 * g.h_pantalla
    as_inf = max(punt.as_prov_mm2_m, RHO_ZAPATA_MIN * g.h_zapata * 1e6)
    as_sup = max(tal.as_prov_mm2_m, RHO_ZAPATA_MIN * g.h_zapata * 1e6)
    v_zap = (as_inf + as_sup) * 1e-6 * B
    v_long = RHO_ZAPATA_MIN * B * g.h_zapata                                    # barras longitudinales de la zapata, m³ por m
    return (v_pant + v_h + v_zap + v_long) * DENSIDAD_ACERO_KG_M3


def disenar_estructura(g: GeometriaMuro, r: Relleno, s: SueloApoyo, m: Materiales, eco: Economia | None = None, *, x_ceniza: float = 0.0,
                       gamma_concreto: float = GAMMA_CONCRETO_KN_M3) -> DisenoMuro:
    """Estabilidad (Fase 1) + flexión y cortante de pantalla, puntera y talón + costo y CO₂ por metro de muro."""
    eco = eco or Economia()
    est = verificar_estabilidad(g, r, s, gamma_concreto=gamma_concreto)
    pant = _pantalla(g, r, m)
    h_zap = g.h_zapata * 1000.0
    cob_inf = lambda dia: COBERTURA_SUELO_MM
    cob_sup = _recubrimiento
    d_ref = h_zap - COBERTURA_SUELO_MM - DIAMETRO_MM["6"] / 2.0
    z = _momentos_zapata(g, r, gamma_concreto, d_ref / 1000.0)
    motivos = list(est.motivos)
    if z.get("sin_equilibrio"):
        motivos.append("combinación mayorada: la resultante cae fuera de la base (volcamiento)")
        return DisenoMuro(False, tuple(motivos), est, pant, None, None, "-", "-", math.inf, est.volumen_concreto_m3_m, est.area_encofrado_m2_m, math.inf, math.inf)
    punt = _franja("puntera", z["mu_p"], z["vu_p"], h_zap, cob_inf, m, RHO_ZAPATA_MIN * h_zap * 1000.0)
    tal = _franja("talon", max(z["mu_t"], z["mu_t_inf"]), z["vu_t"], h_zap, cob_sup if z["mu_t"] >= z["mu_t_inf"] else cob_inf, m, RHO_ZAPATA_MIN * h_zap * 1000.0)
    for f in (pant, punt, tal):
        motivos.extend(f.motivos)
    txt_h, txt_v, a_h, a_vf = _acero_pantalla_secundario(g, m)
    if not (pant.cumple and punt.cumple and tal.cumple):
        return DisenoMuro(False, tuple(motivos), est, pant, punt, tal, txt_h, txt_v, math.inf, est.volumen_concreto_m3_m, est.area_encofrado_m2_m, math.inf, math.inf)
    kg = _kg_acero(g, pant, punt, tal, a_h, a_vf)
    vol, enc = est.volumen_concreto_m3_m, est.area_encofrado_m2_m
    costo = vol * costo_m3(m.fc, x_ceniza, eco.p_ceniza, eco.mult_concreto) + kg * eco.p_acero + enc * eco.p_encofrado
    co2 = vol * co2_m3(m.fc, x_ceniza, eco.fe_cemento) + kg * eco.fe_acero
    return DisenoMuro(not motivos, tuple(motivos), est, pant, punt, tal, txt_h, txt_v, kg, vol, enc, costo, co2)
