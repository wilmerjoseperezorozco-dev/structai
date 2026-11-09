"""Muro de contención en voladizo, por metro de longitud: estabilidad externa (Fase 1).

Verifica volcamiento, deslizamiento sin empuje pasivo, excentricidad y presión de contacto con los valores de la Tabla H.6.9-1 y H.6.7 de la
NSR-10 (leídos del corpus el 2026-11-08). NO es un diseño completo: no verifica flexión ni cortante de la pantalla ni de la zapata (Fase 2), no
incluye sismo (Fase 3), ni estabilidad general del talud, asentamientos o socavación.

HIPÓTESIS de investigación (no están en la NSR-10 del corpus): empuje activo de Rankine con relleno plano inclinado un ángulo β, aplicado en el plano
vertical virtual que pasa por el extremo del talón y paralelo a la superficie del relleno; la sobrecarga se trata como una altura equivalente de
relleno q/γ; el rozamiento de la base es tan(2φ/3) salvo que se dé `mu_base`. El relleno se supone drenado (H.6.5 exige drenaje).

Coordenadas (m): x desde la punta de la puntera hacia el relleno, y desde la cara inferior de la zapata hacia arriba. La cara frontal de la pantalla es
vertical; la cara posterior se inclina de t_b (base) a t_c (corona).
Combinación: servicio (sin mayorar), como exigen los factores indirectos de la Tabla H.6.9-1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# Tabla H.6.9-1 (NSR-10), condición estática.
FS_DESLIZAMIENTO_MIN = 1.60
FS_VOLCAMIENTO_MIN = 3.00
EXCENTRICIDAD_MAX_B = 1.0 / 6.0
DESPLANTE_MIN_M = 1.0                 # H.6.7(a)
GAMMA_CONCRETO_KN_M3 = 24.0           # supuesto de peso unitario del concreto reforzado


@dataclass(frozen=True)
class GeometriaMuro:
    h_pantalla: float     # altura de la pantalla sobre la zapata (m)
    h_zapata: float       # espesor de la zapata (m)
    t_corona: float       # espesor de la pantalla en la corona (m)
    t_base: float         # espesor de la pantalla en la base (m)
    b_puntera: float      # longitud de la puntera, hasta la cara frontal de la pantalla (m)
    b_talon: float        # longitud del talón, desde la cara posterior de la pantalla en la base (m)
    desplante: float = 1.0  # profundidad de la cara inferior de la zapata bajo el terreno frente al muro (m)

    @property
    def ancho_base(self) -> float:
        return self.b_puntera + self.t_base + self.b_talon

    def validar(self) -> None:
        for nombre in ("h_pantalla", "h_zapata", "t_corona", "t_base", "b_puntera", "b_talon"):
            if getattr(self, nombre) <= 0:
                raise ValueError(f"{nombre} debe ser > 0")
        if self.t_corona > self.t_base:
            raise ValueError("t_corona no puede exceder t_base")


@dataclass(frozen=True)
class Relleno:
    gamma: float          # kN/m3
    phi_deg: float        # ángulo de fricción efectivo
    beta_deg: float = 0.0  # inclinación de la superficie del relleno
    sobrecarga_kpa: float = 0.0


@dataclass(frozen=True)
class SueloApoyo:
    phi_deg: float
    q_adm_kpa: float
    c_kpa: float = 0.0
    mu_base: float | None = None   # si None: tan(2/3 φ) (HIPÓTESIS)

    @property
    def mu(self) -> float:
        return self.mu_base if self.mu_base is not None else math.tan(math.radians(2.0 * self.phi_deg / 3.0))


@dataclass(frozen=True)
class ResultadoEstabilidad:
    cumple: bool
    motivos: tuple[str, ...]
    ka: float
    empuje_kn_m: float             # resultante del empuje activo (kN/m, paralela a la superficie)
    h_empuje_m: float              # altura del plano virtual medida desde la cara inferior de la zapata
    fs_volcamiento: float
    fs_deslizamiento: float
    excentricidad_m: float
    q_max_kpa: float
    q_min_kpa: float
    sum_v_kn_m: float
    volumen_concreto_m3_m: float
    area_encofrado_m2_m: float


def coeficiente_activo_rankine(phi_deg: float, beta_deg: float = 0.0) -> float:
    """K_A de Rankine para relleno plano inclinado β: cosβ·(cosβ − √(cos²β − cos²φ)) / (cosβ + √(cos²β − cos²φ))."""
    if not 0.0 < phi_deg < 90.0:
        raise ValueError("phi_deg debe estar en (0, 90)")
    if not 0.0 <= beta_deg <= phi_deg:
        raise ValueError("beta_deg debe estar en [0, phi_deg]")
    b, p = math.radians(beta_deg), math.radians(phi_deg)
    raiz = math.sqrt(max(math.cos(b) ** 2 - math.cos(p) ** 2, 0.0))
    return math.cos(b) * (math.cos(b) - raiz) / (math.cos(b) + raiz)


def _poligono(vertices: list[tuple[float, float]]) -> tuple[float, float, float]:
    """(área, x del centroide, y del centroide) de un polígono simple por la fórmula del topógrafo."""
    v = np.asarray(vertices, dtype=float)
    x, y = v[:, 0], v[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cruz = x * y1 - x1 * y
    area = cruz.sum() / 2.0
    if abs(area) < 1e-12:
        return 0.0, 0.0, 0.0
    return abs(area), float(((x + x1) * cruz).sum() / (6 * area)), float(((y + y1) * cruz).sum() / (6 * area))


def _cargas_verticales(g: GeometriaMuro, r: Relleno, gamma_c: float) -> list[tuple[str, float, float]]:
    """Lista (nombre, fuerza vertical kN/m, brazo x desde la punta) de concreto y relleno sobre el talón, sin sobrecarga."""
    xf, xb_base, xb_top = g.b_puntera, g.b_puntera + g.t_base, g.b_puntera + g.t_corona
    pieza_pant = _poligono([(xf, g.h_zapata), (xb_base, g.h_zapata), (xb_top, g.h_zapata + g.h_pantalla), (xf, g.h_zapata + g.h_pantalla)])
    pieza_zap = _poligono([(0, 0), (g.ancho_base, 0), (g.ancho_base, g.h_zapata), (0, g.h_zapata)])
    y_sup_talon = g.h_zapata + g.h_pantalla + (g.ancho_base - xb_top) * math.tan(math.radians(r.beta_deg))
    pieza_suelo = _poligono([(xb_base, g.h_zapata), (g.ancho_base, g.h_zapata), (g.ancho_base, y_sup_talon),
                             (xb_top, g.h_zapata + g.h_pantalla)])
    return [("pantalla", pieza_pant[0] * gamma_c, pieza_pant[1]), ("zapata", pieza_zap[0] * gamma_c, pieza_zap[1]),
            ("relleno_talon", pieza_suelo[0] * r.gamma, pieza_suelo[1])]


def verificar_estabilidad(g: GeometriaMuro, r: Relleno, s: SueloApoyo, *, gamma_concreto: float = GAMMA_CONCRETO_KN_M3) -> ResultadoEstabilidad:
    """Verificación de estabilidad externa en servicio. Devuelve los factores y las razones de incumplimiento."""
    g.validar()
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    beta = math.radians(r.beta_deg)
    B = g.ancho_base
    x_top = g.b_puntera + g.t_corona
    h_virtual = g.h_zapata + g.h_pantalla + (B - x_top) * math.tan(beta)
    h_eq = r.sobrecarga_kpa / r.gamma
    pa = 0.5 * ka * r.gamma * h_virtual * (h_virtual + 2.0 * h_eq)
    brazo_pa = h_virtual * (h_virtual + 3.0 * h_eq) / (3.0 * (h_virtual + 2.0 * h_eq))
    ph, pv = pa * math.cos(beta), pa * math.sin(beta)

    cargas = _cargas_verticales(g, r, gamma_concreto)
    v_est = sum(f for _, f, _ in cargas) + pv
    m_est = sum(f * x for _, f, x in cargas) + pv * B
    m_vuelco = ph * brazo_pa
    # presión de contacto: incluye la sobrecarga sobre el talón (sección crítica para la capacidad portante)
    q_talon = r.sobrecarga_kpa * (B - x_top)
    x_q = x_top + (B - x_top) / 2.0
    v_b, m_b = v_est + q_talon, m_est + q_talon * x_q
    x_r = (m_b - m_vuelco) / v_b
    e = B / 2.0 - x_r
    q_max, q_min = v_b / B * (1.0 + 6.0 * e / B), v_b / B * (1.0 - 6.0 * e / B)
    fs_v = m_est / m_vuelco
    fs_d = (v_est * s.mu + s.c_kpa * B) / ph if ph > 0 else math.inf

    motivos = []
    if fs_v < FS_VOLCAMIENTO_MIN:
        motivos.append(f"volcamiento {fs_v:.2f} < {FS_VOLCAMIENTO_MIN} (H.6.9-1)")
    if fs_d < FS_DESLIZAMIENTO_MIN:
        motivos.append(f"deslizamiento {fs_d:.2f} < {FS_DESLIZAMIENTO_MIN} (H.6.9-1)")
    if e > EXCENTRICIDAD_MAX_B * B:
        motivos.append(f"excentricidad {e:.3f} m > B/6 = {B / 6:.3f} m (H.6.9-1)")
    if q_max > s.q_adm_kpa:
        motivos.append(f"presión máxima {q_max:.1f} kPa > q_adm {s.q_adm_kpa:.1f} kPa")
    if g.desplante < DESPLANTE_MIN_M:
        motivos.append(f"desplante {g.desplante:.2f} m < {DESPLANTE_MIN_M} m (H.6.7a)")
    vol = sum(f for n, f, _ in cargas if n != "relleno_talon") / gamma_concreto
    enc = g.h_pantalla + math.hypot(g.h_pantalla, g.t_base - g.t_corona) + 2.0 * g.h_zapata + g.t_corona
    return ResultadoEstabilidad(not motivos, tuple(motivos), ka, pa, h_virtual, fs_v, fs_d, e, q_max, q_min, v_est, vol, enc)
