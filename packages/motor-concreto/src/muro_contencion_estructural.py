"""Muro de contención en voladizo, por metro de longitud: diseño estructural completo (Fases 2 y 3b) + costo APU y CO₂.

Verificado en el corpus `nsr10_chunks` el 2026-11-08: B.2.4.2 (B.2.4-2 y B.2.4-7, 1,6 H, 0,9 D), C.14.1.2, C.14.3.2-3-4, C.10.5.1, C.7.7.1, C.11.1.3, C.11.2.1.1, C.9.3.2,
C.10.5.4/C.7.12.2.1, H.5.2.5 (K_ST/a_max ≥ 0,80), H.6.7 (dentellones reforzados, sin empuje pasivo), H.6.8 (empujes sísmicos).

Combinaciones de la puntera y el talón: A = B.2.4-2 (1,2 D + 1,6 H + 1,6 L, sobrecarga como L); S = B.2.4-7 (0,9 D + 1,0 E + 1,6 H, E×1,4: HIPÓTESIS, ver `muro_pantalla`);
B = 0,9 D + 1,6 H sin W ni E es una verificación ADICIONAL conservadora que B.2.4 no trae literalmente.

NO verificado (se devuelve en `SUPUESTOS`): longitud de desarrollo y empalmes (C.12), corte de barras, cortante por fricción pantalla-zapata, fisuración, drenaje, estabilidad
general, asentamientos, peso propio excéntrico de la pantalla, efecto axial del peso sobre la flexión de la pantalla.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .economia_concreto import Economia, co2_m3, costo_m3
from .muro_anclaje import DisenoAnclaje, costo_co2_anclaje, disenar_anclaje
from .muro_contrafuerte import DisenoContrafuerte, disenar_contrafuerte
from .muro_contencion import (GAMMA_CONCRETO_KN_M3, GeometriaMuro, Relleno, ResultadoEstabilidad, SueloApoyo, _empuje_estatico, _piezas,
                              coeficiente_activo_mononobe_okabe, fuerza_anclaje, verificar_estabilidad, verificar_estabilidad_sismica)
from .muro_pantalla import SeccionPantalla, disenar_bandeja, disenar_dentellon, disenar_pantalla
from .muro_refuerzo import COBERTURA_SUELO_MM, Franja, franja, recubrimiento, suelo
from .viga import AREA_MM2, DIAMETRO_MM, Materiales

FACTOR_H = 1.6                       # B.2.4-2 / B.2.4-7
FACTOR_D_A, FACTOR_D_B = 1.2, 0.9
FACTOR_Q = 1.6
FACTOR_E = 1.4                       # HIPÓTESIS (B.2.4.2.4)
DENSIDAD_ACERO_KG_M3 = 7850.0
RHO_ZAPATA_MIN = 0.0018              # C.10.5.4 / C.7.12.2.1 con fy 420
SEP_MAX_ABS_MM = 450.0
N_INTEG = 401
_franja, _recubrimiento = franja, recubrimiento      # nombres históricos usados por las pruebas

SUPUESTOS = (
    "Combinaciones A (B.2.4-2) y S (B.2.4-7) leídas; la combinación B (0,9D+1,6H) es un chequeo adicional conservador; E×1,4 en S es HIPÓTESIS.",
    "Longitud de desarrollo, empalmes y ganchos (C.12) NO verificados; sin corte de barras en la pantalla (conservador en cantidad de acero).",
    "Cortante de la pantalla en cada sección sin reducción a d; cortante del talón en la cara de la pantalla; de la puntera a d de la cara.",
    "El relleno sobre la puntera, el peso del dentellón y el de la bandeja no se descuentan en la flexión de la zapata.",
    "Bandeja: modelo de sombreado del empuje y contramomento con 0,9D son HIPÓTESIS; no se verifica el anclaje de la bandeja en la pantalla.",
    "Dentellón: fuerza de diseño = déficit de la fricción simple tan(2φ/3) para el FS exigido; la fricción plena tan φ con dentellón ≥ 0,30 m es HIPÓTESIS.",
    "Sin fisuración, juntas, drenaje, estabilidad general ni asentamientos.",
    "Contrafuertes: losas continuas con M = wL'²/12 (cota superior), momento vertical de la pantalla = mitad del horizontal sin calibrar con placa, contrafuerte rectangular de ancho "
    "esp con barra inclinada, sin corte de barras ni torsión (ver muro_contrafuerte).",
    "Anclajes: preesfuerzo, adherencia τ supuesta, longitud libre hasta la superficie de falla de Rankine + 1,5 m; la pantalla se diseña SIN el alivio del tirante y NO se verifica "
    "el punzonamiento ni la flexión local en la cabeza del anclaje; precios de perforación y cabeza SUPUESTOS (ver muro_anclaje).",
)


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
    estabilidad_sismica: ResultadoEstabilidad | None = None
    bandeja: Franja | None = None
    dentellon: Franja | None = None
    secciones_pantalla: tuple[SeccionPantalla, ...] = ()
    contrafuerte: DisenoContrafuerte | None = None
    anclaje: DisenoAnclaje | None = None
    supuestos: tuple[str, ...] = SUPUESTOS


# --------------------------------------------------------------------------------------------- presiones de contacto mayoradas
def _equilibrio(g: GeometriaMuro, v: float, m_est: float, m_vol: float):
    """Presión q(x) [kPa] desde la punta y (q_punta, q_talon, V). None si la resultante cae fuera de la base."""
    B = g.ancho_base
    x_r = (m_est - m_vol) / v
    if x_r <= 0.0:
        return None
    if B / 2.0 - x_r <= B / 6.0:
        e = B / 2.0 - x_r
        qa, qb = v / B * (1 + 6 * e / B), v / B * (1 - 6 * e / B)
        return (lambda x: qa + (qb - qa) * np.asarray(x) / B), qa, qb, v
    q_max = 2.0 * v / (3.0 * x_r)
    return (lambda x: np.clip(q_max * (1 - np.asarray(x) / (3.0 * x_r)), 0.0, None)), q_max, 0.0, v


def _presion(g: GeometriaMuro, r: Relleno, gamma_c: float, f_d: float, f_q: float, f_anc: float = 0.0):
    """Combinación estática mayorada: f_d·D + 1,6 H + f_q·Q."""
    ka, h, pa_s, pa_q, br_s, br_q = _empuje_estatico(g, r)
    sb, cb = math.sin(math.radians(r.beta_deg)), math.cos(math.radians(r.beta_deg))
    B = g.ancho_base
    x_top = g.b_puntera + g.t_corona
    pesos = _piezas(g, r, gamma_c)
    q_tal = f_q * r.sobrecarga_kpa * (B - x_top)
    x_q = x_top + (B - x_top) / 2.0
    th, tv, x_a, y_a = fuerza_anclaje(g)
    v = f_d * sum(f for _, f, _, _ in pesos) + FACTOR_H * pa_s * sb + f_q * pa_q * sb + q_tal + f_anc * tv
    m_est = f_d * sum(f * x for _, f, x, _ in pesos) + (FACTOR_H * pa_s + f_q * pa_q) * sb * B + q_tal * x_q + f_anc * tv * x_a
    m_vol = FACTOR_H * pa_s * cb * br_s + f_q * pa_q * cb * br_q - f_anc * th * y_a
    return _equilibrio(g, v, m_est, m_vol)


def _presion_sismica(g: GeometriaMuro, r: Relleno, gamma_c: float, kh: float, f_anc: float = 0.0):
    """Combinación S: 0,9 D + 1,6 H(estático) + 1,4 E (incremento dinámico M-O a 0,6 h + inercia kh·W)."""
    ka, h, pa_s, _, br_s, _ = _empuje_estatico(g, r)
    kae = coeficiente_activo_mononobe_okabe(r.phi_deg, r.beta_deg, kh)
    if math.isinf(kae):
        return None
    sb, cb = math.sin(math.radians(r.beta_deg)), math.cos(math.radians(r.beta_deg))
    B = g.ancho_base
    d_pae = max(0.5 * kae * r.gamma * h * h - pa_s, 0.0)
    pesos = _piezas(g, r, gamma_c)
    pv = (FACTOR_H * pa_s + FACTOR_E * d_pae) * sb
    th, tv, x_a, y_a = fuerza_anclaje(g)
    v = FACTOR_D_B * sum(f for _, f, _, _ in pesos) + pv + f_anc * tv
    m_est = FACTOR_D_B * sum(f * x for _, f, x, _ in pesos) + pv * B + f_anc * tv * x_a
    m_vol = (FACTOR_H * pa_s * br_s + FACTOR_E * d_pae * 0.6 * h) * cb + FACTOR_E * kh * sum(f * y for _, f, _, y in pesos) - f_anc * th * y_a
    return _equilibrio(g, v, m_est, m_vol)


def _integral(f, a: float, b: float) -> float:
    if b <= a:
        return 0.0
    x = np.linspace(a, b, N_INTEG)
    return float(np.trapezoid(f(x), x))


def _combinaciones(g: GeometriaMuro, r: Relleno, gamma_c: float, kh: float | None):
    """(factor_D, presión) de cada combinación; la presión es None si no hay equilibrio."""
    out = []
    for f_anc in ((1.0,) if g.tiene_anclaje else (0.0,)):      # el tirante preesforzado es una acción permanente: se incluye con factor 1,0
        out += [(FACTOR_D_A, _presion(g, r, gamma_c, FACTOR_D_A, FACTOR_Q, f_anc)), (FACTOR_D_B, _presion(g, r, gamma_c, FACTOR_D_B, 0.0, f_anc))]
        if kh is not None:
            out.append((FACTOR_D_B, _presion_sismica(g, r, gamma_c, kh, f_anc)))
    return out


def _momentos_zapata(g: GeometriaMuro, r: Relleno, gamma_c: float, d_punt: float, kh: float | None = None) -> dict[str, float]:
    """Envolvente de Mu y Vu de la puntera (a d de la cara) y del talón (en la cara posterior de la pantalla)."""
    x_h = g.b_puntera + g.t_base
    B, bp = g.ancho_base, g.b_puntera
    x_top = g.b_puntera + g.t_corona
    tan_b = math.tan(math.radians(r.beta_deg))
    sal = {"mu_p": 0.0, "vu_p": 0.0, "mu_t": 0.0, "vu_t": 0.0, "mu_t_inf": 0.0, "w_t": 0.0}
    luz = g.contrafuerte_sep - g.contrafuerte_esp
    for f_d, p in _combinaciones(g, r, gamma_c, kh):
        if p is None:
            return {**sal, "sin_equilibrio": 1.0}
        q = p[0]
        f_q = FACTOR_Q if f_d == FACTOR_D_A else 0.0
        propio = f_d * gamma_c * g.h_zapata
        w = lambda x: propio + f_d * r.gamma * (g.h_pantalla + (np.asarray(x) - x_top) * tan_b) + f_q * r.sobrecarga_kpa
        sal["mu_p"] = max(sal["mu_p"], _integral(lambda x: (q(x) - propio) * (bp - x), 0.0, bp))
        sal["vu_p"] = max(sal["vu_p"], _integral(lambda x: q(x) - propio, 0.0, max(bp - d_punt, 0.0)))
        neto = lambda x: w(x) - q(x)
        if g.tiene_contrafuerte:        # losa continua entre contrafuertes con la carga neta máxima (HIPÓTESIS, ver muro_contrafuerte)
            nx = neto(np.linspace(x_h, B, 41))
            n_dn, n_up = max(float(nx.max()), 0.0), max(-float(nx.min()), 0.0)
            sal["mu_t"] = max(sal["mu_t"], n_dn * luz**2 / 12.0)
            sal["mu_t_inf"] = max(sal["mu_t_inf"], n_up * luz**2 / 12.0)
            sal["vu_t"] = max(sal["vu_t"], max(n_dn, n_up) * luz / 2.0)
            sal["w_t"] = max(sal["w_t"], n_dn, n_up)
            continue
        mt = _integral(lambda x: neto(x) * (x - x_h), x_h, B)
        sal["mu_t"] = max(sal["mu_t"], mt)
        sal["mu_t_inf"] = max(sal["mu_t_inf"], -mt)
        sal["vu_t"] = max(sal["vu_t"], abs(_integral(neto, x_h, B)))
    return sal


def _pantalla(g: GeometriaMuro, r: Relleno, m: Materiales) -> Franja:
    """Pantalla en la base, solo combinación estática (nombre histórico)."""
    return disenar_pantalla(g, r, m)[0]


# --------------------------------------------------------------------------------------------- acero secundario y cantidades
def _acero_pantalla_secundario(g: GeometriaMuro, m: Materiales) -> tuple[str, str, float, float]:
    """(texto horizontal, texto vertical frontal, As_h total mm²/m de altura, As_v frontal mm²/m) con C.14.3.2-3-4."""
    t_prom = float(np.mean(g.espesor_pantalla(np.linspace(0.0, g.h_pantalla, 41)))) * 1000.0
    cap = 2 if t_prom > 250.0 else 1                                            # C.14.3.4
    rho_h = 0.0020 if m.fy >= 420 else 0.0025                                   # C.14.3.3, ≤ #5 con fy ≥ 420
    rho_v = 0.0012 if m.fy >= 420 else 0.0015                                   # C.14.3.2
    a_h, a_v = rho_h * t_prom * 1000.0, rho_v * t_prom * 1000.0 / cap
    s_max = min(3 * t_prom, SEP_MAX_ABS_MM)

    def texto(a_total: float, capas: int) -> str:
        s = min(math.floor(1000.0 * AREA_MM2["4"] / (a_total / capas) / 10.0) * 10.0, s_max)
        return f"#4 c/{int(s)} mm × {capas} capa(s)"
    return texto(a_h, cap), texto(a_v * cap, cap), a_h, a_v * cap


def _kg_acero(g: GeometriaMuro, pant: Franja, punt: Franja, tal: Franja, a_h: float, a_v_front: float, band: Franja | None, dent: Franja | None,
              cf: DisenoContrafuerte | None = None) -> float:
    B = g.ancho_base
    if cf is not None:      # pantalla y contrafuertes ya cuantificados en muro_contrafuerte (kg por metro de muro)
        v = cf.kg_m / DENSIDAD_ACERO_KG_M3
    else:
        v = pant.as_prov_mm2_m * 1e-6 * (g.h_pantalla + g.h_zapata) + a_v_front * 1e-6 * g.h_pantalla + a_h * 1e-6 * g.h_pantalla
    as_inf = max(punt.as_prov_mm2_m, RHO_ZAPATA_MIN * g.h_zapata * 1e6)
    as_sup = max(tal.as_prov_mm2_m, RHO_ZAPATA_MIN * g.h_zapata * 1e6)
    v += (as_inf + as_sup) * 1e-6 * B + RHO_ZAPATA_MIN * B * g.h_zapata
    if band is not None:
        v += band.as_prov_mm2_m * 1e-6 * (g.bandeja_vuelo + 0.4) + 0.0018 * g.bandeja_esp * g.bandeja_vuelo
    if dent is not None:
        v += dent.as_prov_mm2_m * 1e-6 * (g.dentellon_prof + g.h_zapata) + 0.0018 * g.dentellon_ancho * g.dentellon_prof
    return v * DENSIDAD_ACERO_KG_M3


def _invalido(motivos, est, sis, pant, punt, tal, txt_h, txt_v, secs, band=None, dent=None, cf=None, anc=None):
    return DisenoMuro(False, tuple(motivos), est, pant, punt, tal, txt_h, txt_v, math.inf, est.volumen_concreto_m3_m, est.area_encofrado_m2_m, math.inf,
                      math.inf, sis, band, dent, tuple(secs), cf, anc)


def disenar_estructura(g: GeometriaMuro, r: Relleno, s: SueloApoyo, m: Materiales, eco: Economia | None = None, *, a_max_g: float | None = None,
                       ratio_kst: float = 0.80, x_ceniza: float = 0.0, gamma_concreto: float = GAMMA_CONCRETO_KN_M3) -> DisenoMuro:
    """Estabilidad (estática y, si a_max_g, seudoestática) + flexión y cortante de pantalla, puntera, talón, bandeja y dentellón + costo y CO₂ por metro."""
    eco = eco or Economia()
    est = verificar_estabilidad(g, r, s, gamma_concreto=gamma_concreto)
    sis = verificar_estabilidad_sismica(g, r, s, a_max_g, ratio_kst=ratio_kst, gamma_concreto=gamma_concreto) if a_max_g is not None else None
    kh = None if a_max_g is None else ratio_kst * a_max_g
    motivos = list(est.motivos) + ([f"sismo: {x}" for x in sis.motivos] if sis else [])
    anc = disenar_anclaje(g, r)
    if anc is not None:
        motivos.extend(anc.motivos)
    pant, secs = disenar_pantalla(g, r, m, kh)
    h_zap = g.h_zapata * 1000.0
    d_ref = h_zap - COBERTURA_SUELO_MM - DIAMETRO_MM["6"] / 2.0
    z = _momentos_zapata(g, r, gamma_concreto, d_ref / 1000.0, kh)
    txt_h, txt_v, a_h, a_vf = _acero_pantalla_secundario(g, m)
    if z.get("sin_equilibrio"):
        motivos.append("combinación mayorada: la resultante cae fuera de la base (volcamiento)")
        return _invalido(motivos, est, sis, pant, None, None, txt_h, txt_v, secs, anc=anc)
    cf = disenar_contrafuerte(g, r, m, kh, z["w_t"], gamma_concreto) if g.tiene_contrafuerte else None
    if cf is not None:
        motivos.extend(cf.motivos)
        pant = cf.pantalla
    ph_s = sis.ph_total_kn_m if sis else None
    v_s = sis.sum_v_kn_m if sis else None
    band = disenar_bandeja(g, r, m, gamma_concreto)
    dent = disenar_dentellon(g, est.ph_total_kn_m, est.sum_v_kn_m, ph_s, v_s, s, m)
    punt = franja("puntera", z["mu_p"], z["vu_p"], h_zap, suelo, m, RHO_ZAPATA_MIN * h_zap * 1000.0)
    cob_tal = recubrimiento if z["mu_t"] >= z["mu_t_inf"] else suelo
    tal = franja("talon", max(z["mu_t"], z["mu_t_inf"]), z["vu_t"], h_zap, cob_tal, m, RHO_ZAPATA_MIN * h_zap * 1000.0)
    for f in (punt, tal, band, dent) + (() if cf is not None else (pant,)):
        if f is not None:
            motivos.extend(f.motivos)
    ok = all(f.cumple for f in (pant, punt, tal, band, dent) if f is not None and not (cf is not None and f is pant)) and (cf is None or cf.cumple)         and (anc is None or anc.cumple)
    if not ok:
        return _invalido(motivos, est, sis, pant, punt, tal, txt_h, txt_v, secs, band, dent, cf, anc)
    kg = _kg_acero(g, pant, punt, tal, a_h, a_vf, band, dent, cf)
    vol, enc = est.volumen_concreto_m3_m, est.area_encofrado_m2_m
    costo = vol * costo_m3(m.fc, x_ceniza, eco.p_ceniza, eco.mult_concreto) + kg * eco.p_acero + enc * eco.p_encofrado
    co2 = vol * co2_m3(m.fc, x_ceniza, eco.fe_cemento) + kg * eco.fe_acero
    if anc is not None:
        c_a, co2_a = costo_co2_anclaje(anc, eco)
        costo, co2, kg = costo + c_a, co2 + co2_a, kg + anc.kg_cordon_m
    return DisenoMuro(not motivos, tuple(motivos), est, pant, punt, tal, txt_h, txt_v, kg, vol, enc, costo, co2, sis, band, dent, tuple(secs), cf, anc)
