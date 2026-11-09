"""Muro de contrafuertes: pantalla y talón como losas continuas entre contrafuertes, y contrafuerte como voladizo de sección rectangular atado a la zapata.

Por metro de muro. La estabilidad externa (peso del contrafuerte incluido) está en `muro_contencion`; aquí se dimensiona el refuerzo.

HIPÓTESIS de investigación (el corpus NSR-10 no trae el método; se usan las combinaciones B.2.4-2 / B.2.4-7 y las secciones del Título C ya leídas):
- Pantalla: franjas horizontales de 1 m con luz libre L' = sep − esp y M = w·L'²/12 en ambas caras (cota superior de losa continua), w = presión mayorada a esa profundidad.
  Refuerzo horizontal por sección (8 niveles) integrado en altura, en dos caras. Vertical: M_v = w_base·L'²/24 (mitad del horizontal, SIN calibrar con una placa de Czerny/Bares),
  extendido L' + 0,6 m sobre la base, y cuantía mínima vertical arriba.
- Talón: losa continua entre contrafuertes con la carga neta máxima del talón (sin acción en voladizo desde la pantalla).
- Contrafuerte: viga en voladizo de ancho = esp con profundidad horizontal que crece linealmente hasta b_talon + t_base; Mu = sep·Mu_pantalla(y), Vu = sep·Vu_pantalla(y); barra
  principal inclinada con la arista (As = As_vertical/cosψ, la componente horizontal de la barra NO se acredita al cortante); sección rectangular de ancho esp (sin aporte de ala).
- Estribos horizontales: máximo entre el amarre de la presión w·sep/(φ·fy) por metro de altura, el cortante C.11.4.7 y el mínimo; cortante de tope 0,66·√f'c·bw·d (C.11.4.7.9).
  Amarres verticales del talón al contrafuerte con la carga neta del talón.
NO verificado: desarrollo y empalmes, fisuración, corte de barras del contrafuerte, torsión, efecto del peso propio del contrafuerte en su flexión.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .muro_contencion import GAMMA_CONCRETO_KN_M3, GeometriaMuro, Relleno, coeficiente_activo_rankine
from .muro_pantalla import FACTOR_E_SERVICIO, FACTOR_H, N_SECCIONES, _dinamico, _sigma, acciones_pantalla
from .muro_refuerzo import Franja, franja, phi_vc_kn, recubrimiento
from .viga import PHI_CORTANTE, PHI_FLEXION, Materiales
from .zapata import _as_flexion

DENSIDAD_ACERO_KG_M3 = 7850.0
BARRAS_CF = {"6": (19.1, 285.0), "7": (22.2, 387.0), "8": (25.4, 510.0), "9": (28.7, 645.0), "10": (32.3, 819.0), "11": (35.8, 1006.0)}
COBERTURA_CF_MM = 100.0              # recubrimiento 75 mm (suelo) + estribo y media barra, hasta el eje del acero principal
ANCLAJE_ESTRIBO_M = 0.5
PROLONGACION_VERTICAL_M = 0.6        # barra vertical de la pantalla más allá de la luz L'
RHO_H_MIN, RHO_V_MIN = 0.0020, 0.0012   # C.14.3.3 y C.14.3.2 con fy ≥ 420


@dataclass(frozen=True)
class DisenoContrafuerte:
    cumple: bool
    motivos: tuple[str, ...]
    pantalla: Franja              # franja horizontal de la base (la más cargada)
    vertical: Franja              # franja vertical de la base de la pantalla
    as_h_prom_mm2_m: float        # refuerzo horizontal promedio en altura por cara
    luz_libre_m: float
    mu_cf_knm: float              # momento de diseño del contrafuerte en la base
    vu_cf_kn: float
    d_cf_mm: float                # profundidad útil horizontal en la base
    as_req_cf_mm2: float
    dia_cf: str
    n_barras_cf: int
    as_prov_cf_mm2: float
    estribos_mm2_m: float         # área de estribos horizontales por metro de altura (máxima)
    kg_m: float                   # kg de acero de la pantalla + contrafuertes por metro de muro


def _w_mayorada(g: GeometriaMuro, r: Relleno, z, kh: float | None, gamma_c: float):
    """Presión horizontal mayorada [kPa] a profundidad z: A = 1,6 (suelo + sobrecarga); S = 1,6 suelo + 1,4 (dinámico + inercia de la pantalla)."""
    z = np.asarray(z, dtype=float)
    w = FACTOR_H * _sigma(g, r, z, True)
    if kh is not None:
        din = _dinamico(g, r, kh)
        if din is None:
            return np.full_like(z, math.inf)
        w = np.maximum(w, FACTOR_H * _sigma(g, r, z, False) + FACTOR_E_SERVICIO * (din(z) + kh * gamma_c * g.t_base))
    return w


def _elegir_barra_cf(as_req: float, esp_mm: float):
    """(dia, n, As_prov) con el menor As que cabe en una o dos hileras en el ancho del contrafuerte, o None."""
    mejor = None
    ancho_util = esp_mm - 2.0 * 75.0 - 2.0 * 12.7
    for dia, (db, a1) in BARRAS_CF.items():
        n = max(math.ceil(as_req / a1 - 1e-9), 2)
        por_hilera = math.floor((ancho_util + 25.0) / (db + max(db, 25.0)))
        if por_hilera < 2 or n > 2 * por_hilera:
            continue
        if mejor is None or n * a1 < mejor[2]:
            mejor = (dia, n, n * a1)
    return mejor


def disenar_contrafuerte(g: GeometriaMuro, r: Relleno, m: Materiales, kh: float | None, w_talon_kpa: float,
                         gamma_c: float = GAMMA_CONCRETO_KN_M3) -> DisenoContrafuerte:
    L, esp, h, bt, t = g.contrafuerte_sep, g.contrafuerte_esp, g.h_pantalla, g.b_talon, g.t_base
    luz = L - esp
    t_mm = t * 1000.0
    motivos: list[str] = []
    # ---- pantalla: franjas horizontales y vertical
    zs = h * np.arange(1, N_SECCIONES + 1) / N_SECCIONES
    w = _w_mayorada(g, r, zs, kh, gamma_c)
    if np.isinf(w).any():
        vacia = Franja("pantalla", math.inf, math.inf, t_mm, 0.0, "-", 0.0, math.inf, math.inf, 0.0, 0.0, 0.0, False, ("pantalla: Mononobe-Okabe sin solución",))
        return DisenoContrafuerte(False, vacia.motivos, vacia, vacia, math.inf, luz, math.inf, math.inf, 0.0, math.inf, "-", 0, math.inf, math.inf, math.inf)
    as_min_h = RHO_H_MIN * t_mm * 1000.0
    franjas_h = [franja("pantalla", float(wk) * luz**2 / 12.0, float(wk) * luz / 2.0, t_mm, recubrimiento, m, as_min_h) for wk in w]
    base_h = franjas_h[-1]
    mu_v = float(w[-1]) * luz**2 / 24.0
    as_min_v = RHO_V_MIN * t_mm * 1000.0
    vert = franja("pantalla vertical", mu_v, 0.0, t_mm, recubrimiento, m, as_min_v)
    for f in (*franjas_h, vert):
        if not f.cumple:
            motivos.extend(f.motivos)
    as_h = np.array([f.as_prov_mm2_m if math.isfinite(f.as_prov_mm2_m) else 0.0 for f in franjas_h])
    as_h_prom = float(np.mean(as_h))          # cada nivel representa el tramo que termina en él (cota superior: la presión crece con la profundidad)
    kg = 2.0 * as_h_prom * 1e-6 * h * DENSIDAD_ACERO_KG_M3                                   # dos caras
    as_v = vert.as_prov_mm2_m if math.isfinite(vert.as_prov_mm2_m) else 0.0
    h_flex = min(h, luz + PROLONGACION_VERTICAL_M)
    kg += (as_v * h_flex + as_min_v * (h - h_flex) + as_min_v * h) * 1e-6 * DENSIDAD_ACERO_KG_M3
    # ---- contrafuerte
    cos_psi = h / math.hypot(h, bt)
    mu_max = vu_max = d_base = as_req = 0.0
    at_max = 0.0
    n_y = N_SECCIONES
    ys = h * np.arange(0, n_y) / n_y
    kg_estribos = 0.0
    for k, y in enumerate(ys):
        mu, vu = acciones_pantalla(g, r, float(y), kh)
        mu_cf, vu_cf = L * mu, L * vu
        d = (t + bt * (1.0 - y / h)) * 1000.0 - COBERTURA_CF_MM
        if d <= 0:
            motivos.append("contrafuerte: profundidad útil nula")
            continue
        a_req = _as_flexion(mu_cf, esp * 1000.0, d, m.fc, m.fy) / cos_psi
        if math.isinf(a_req):
            motivos.append(f"contrafuerte y = {y:.2f} m: sección insuficiente para Mu {mu_cf:.0f} kN·m")
            continue
        if a_req > as_req:
            mu_max, vu_max, d_base, as_req = mu_cf, vu_cf, d, a_req
        vc = PHI_CORTANTE * 0.17 * math.sqrt(m.fc) * esp * 1000.0 * d / 1000.0
        vs = max(vu_cf / PHI_CORTANTE - vc / PHI_CORTANTE, 0.0)
        if vs > 0.66 * math.sqrt(m.fc) * esp * 1000.0 * d / 1000.0:
            motivos.append(f"contrafuerte y = {y:.2f} m: cortante Vu {vu_cf:.0f} kN excede el máximo con estribos (C.11.4.7.9)")
        avs_cortante = vs * 1000.0 / (m.fy * d) * 1000.0                                      # mm²/m de altura
        avs_min = max(0.062 * math.sqrt(m.fc), 0.35) * esp * 1000.0 / m.fy * 1000.0
        amarre = float(_w_mayorada(g, r, h - y, kh, gamma_c)) * L * 1000.0 / (PHI_FLEXION * m.fy)
        at = max(avs_cortante, avs_min, amarre)
        at_max = max(at_max, at)
        kg_estribos += at * 1e-6 * ((t + bt * (1.0 - y / h)) + ANCLAJE_ESTRIBO_M) * (h / n_y)
    sel = _elegir_barra_cf(as_req, esp * 1000.0) if as_req > 0 else ("6", 2, 2 * BARRAS_CF["6"][1])
    if sel is None:
        motivos.append("contrafuerte: el acero principal no cabe en el espesor del contrafuerte (máx. dos hileras)")
        sel = ("-", 0, math.inf)
    dia_cf, n_cf, as_prov_cf = sel
    kg_principal = as_prov_cf * 1e-6 * (math.hypot(h, bt) + 0.8) * DENSIDAD_ACERO_KG_M3 if math.isfinite(as_prov_cf) else math.inf
    # amarres verticales talón–contrafuerte con la carga neta máxima del talón
    xs = np.linspace(0.0, bt, 9)
    a_vert = w_talon_kpa * L * 1000.0 / (PHI_FLEXION * m.fy)                                  # mm² por m de longitud en x
    largo_v = h * (1.0 - xs / bt) + ANCLAJE_ESTRIBO_M
    kg_v = a_vert * 1e-6 * float(np.trapezoid(largo_v, xs)) * DENSIDAD_ACERO_KG_M3
    kg += (kg_principal + kg_estribos * DENSIDAD_ACERO_KG_M3 + kg_v) / L
    return DisenoContrafuerte(not motivos, tuple(dict.fromkeys(motivos)), base_h, vert, as_h_prom, luz, mu_max, vu_max, d_base, as_req, dia_cf, n_cf, as_prov_cf,
                              at_max, kg)
