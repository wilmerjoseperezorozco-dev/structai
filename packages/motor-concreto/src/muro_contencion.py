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
from dataclasses import dataclass, replace

import numpy as np

# Tabla H.6.9-1 (NSR-10), condición estática.
FS_DESLIZAMIENTO_MIN = 1.60
FS_VOLCAMIENTO_MIN = 3.00
EXCENTRICIDAD_MAX_B = 1.0 / 6.0
DESPLANTE_MIN_M = 1.0                 # H.6.7(a)
DENTELLON_EFECTIVO_M = 0.30          # HIPÓTESIS: profundidad mínima para que el dentellón lleve la falla al suelo
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
    perfil: str = "lineal"  # "lineal" o "parabolico": t(y) = t_c + (t_b - t_c)(1 - y/h)^n, n = 1 o 2 (y desde la base)
    dentellon_prof: float = 0.0    # profundidad del dentellón bajo la zapata (m); 0 = sin dentellón
    dentellon_ancho: float = 0.4   # ancho del dentellón (m)
    dentellon_x: float | None = None   # x de su cara frontal desde la punta; None = bajo la cara frontal de la pantalla
    bandeja_y: float = 0.0         # cota de la cara inferior de la bandeja sobre la cara superior de la zapata (m); 0 = sin bandeja
    bandeja_vuelo: float = 0.0     # vuelo de la bandeja hacia el relleno desde la cara posterior de la pantalla (m)
    bandeja_esp: float = 0.25      # espesor de la bandeja (m)

    @property
    def ancho_base(self) -> float:
        return self.b_puntera + self.t_base + self.b_talon

    @property
    def tiene_dentellon(self) -> bool:
        return self.dentellon_prof > 0.0

    @property
    def tiene_bandeja(self) -> bool:
        return self.bandeja_y > 0.0 and self.bandeja_vuelo > 0.0

    def espesor_pantalla(self, y):
        """Espesor de la pantalla a la altura y sobre su base (m)."""
        n = 1.0 if self.perfil == "lineal" else 2.0
        return self.t_corona + (self.t_base - self.t_corona) * (1.0 - np.asarray(y) / self.h_pantalla) ** n

    def validar(self) -> None:
        for nombre in ("h_pantalla", "h_zapata", "t_corona", "t_base", "b_puntera", "b_talon"):
            if getattr(self, nombre) <= 0:
                raise ValueError(f"{nombre} debe ser > 0")
        if self.t_corona > self.t_base:
            raise ValueError("t_corona no puede exceder t_base")
        if self.perfil not in ("lineal", "parabolico"):
            raise ValueError("perfil debe ser 'lineal' o 'parabolico'")
        if self.dentellon_prof < 0 or self.bandeja_y < 0 or self.bandeja_vuelo < 0:
            raise ValueError("dimensiones de dentellón/bandeja no pueden ser negativas")
        if self.tiene_bandeja and not (0 < self.bandeja_y + self.bandeja_esp < self.h_pantalla):
            raise ValueError("la bandeja debe quedar dentro de la altura de la pantalla")
        if self.tiene_dentellon and self.dentellon_x_efectivo + self.dentellon_ancho > self.ancho_base:
            raise ValueError("el dentellón se sale de la base")

    @property
    def dentellon_x_efectivo(self) -> float:
        return self.b_puntera if self.dentellon_x is None else self.dentellon_x


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
    mu_usado: float = 0.0
    kh: float = 0.0
    empuje_dinamico_kn_m: float = 0.0
    ph_total_kn_m: float = 0.0


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


def _perfil_trasero(g: GeometriaMuro, n: int = 41):
    ys = np.linspace(0.0, g.h_pantalla, n)
    return g.b_puntera + g.espesor_pantalla(ys), ys


def _piezas(g: GeometriaMuro, r: Relleno, gamma_c: float) -> list[tuple[str, float, float, float]]:
    """(nombre, fuerza vertical kN/m, x del centroide, y del centroide) de cada pieza: concreto y relleno sobre el talón, sin sobrecarga."""
    xf, hz = g.b_puntera, g.h_zapata
    xs, ys = _perfil_trasero(g)
    x_top = float(xs[-1])
    pant = _poligono([(xf, hz)] + [(float(x), hz + float(y)) for x, y in zip(xs, ys)] + [(xf, hz + g.h_pantalla)])
    zap = _poligono([(0, 0), (g.ancho_base, 0), (g.ancho_base, hz), (0, hz)])
    y_sup = hz + g.h_pantalla + (g.ancho_base - x_top) * math.tan(math.radians(r.beta_deg))
    tras = [(float(x), hz + float(y)) for x, y in zip(xs[::-1], ys[::-1])]
    suelo = _poligono([(float(xs[0]), hz), (g.ancho_base, hz), (g.ancho_base, y_sup)] + tras)
    out = [("pantalla", pant), ("zapata", zap), ("relleno_talon", suelo)]
    pesos = [(n, a * (gamma_c if n != "relleno_talon" else r.gamma), x, y) for n, (a, x, y) in out]
    if g.tiene_dentellon:
        xd = g.dentellon_x_efectivo
        pesos.append(("dentellon", g.dentellon_prof * g.dentellon_ancho * gamma_c, xd + g.dentellon_ancho / 2, -g.dentellon_prof / 2))
    if g.tiene_bandeja:
        xr = g.b_puntera + float(g.espesor_pantalla(g.bandeja_y))
        yb = hz + g.bandeja_y
        a = g.bandeja_vuelo * g.bandeja_esp
        pesos.append(("bandeja", a * (gamma_c - r.gamma), xr + g.bandeja_vuelo / 2, yb + g.bandeja_esp / 2))
    return pesos


def _cargas_verticales(g: GeometriaMuro, r: Relleno, gamma_c: float) -> list[tuple[str, float, float]]:
    return [(n, f, x) for n, f, x, _ in _piezas(g, r, gamma_c)]


def mu_efectivo(g: GeometriaMuro, s: SueloApoyo) -> float:
    """Coeficiente de fricción en la base. HIPÓTESIS: con dentellón de profundidad >= DENTELLON_EFECTIVO_M la superficie de falla pasa por suelo (tan φ)."""
    if g.tiene_dentellon and g.dentellon_prof >= DENTELLON_EFECTIVO_M and s.mu_base is None:
        return math.tan(math.radians(s.phi_deg))
    return s.mu


def coeficiente_activo_mononobe_okabe(phi_deg: float, beta_deg: float, kh: float, kv: float = 0.0) -> float:
    """K_AE de Mononobe-Okabe (muro vertical, rugosidad δ = β en el plano virtual). Devuelve inf si no hay solución (φ - θ - β < 0)."""
    phi, b = math.radians(phi_deg), math.radians(beta_deg)
    th = math.atan(kh / (1.0 - kv))
    d = b
    if phi - th - b < 0:
        return math.inf
    raiz = math.sqrt(math.sin(phi + d) * math.sin(phi - th - b) / (math.cos(d + th) * math.cos(b)))
    return math.cos(phi - th) ** 2 / (math.cos(th) * math.cos(d + th) * (1.0 + raiz) ** 2)


def _encofrado_y_volumen(g: GeometriaMuro, pesos, gamma_c: float) -> tuple[float, float]:
    xs, ys = _perfil_trasero(g)
    largo_trasero = float(np.hypot(np.diff(xs), np.diff(ys)).sum())
    vol = sum(f for n, f, _, _ in pesos if n in ("pantalla", "zapata", "dentellon")) / gamma_c
    if g.tiene_bandeja:
        vol += g.bandeja_vuelo * g.bandeja_esp
    enc = g.h_pantalla + largo_trasero + 2.0 * g.h_zapata + g.t_corona
    if g.tiene_bandeja:
        enc += 2.0 * g.bandeja_vuelo + g.bandeja_esp
    return vol, enc


def _empuje_estatico(g: GeometriaMuro, r: Relleno) -> tuple[float, float, float, float, float, float]:
    """(ka, h_virtual, pa_suelo, pa_sobrecarga, brazo_suelo, brazo_sobrecarga) sobre el plano virtual del talón."""
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    x_top = g.b_puntera + g.t_corona
    h = g.h_zapata + g.h_pantalla + (g.ancho_base - x_top) * math.tan(math.radians(r.beta_deg))
    h_eq = r.sobrecarga_kpa / r.gamma
    return ka, h, 0.5 * ka * r.gamma * h * h, ka * r.gamma * h * h_eq, h / 3.0, h / 2.0


def _resolver(g, r, s, gamma_c, pesos, fuerzas_h, pv, kh, con_sobrecarga, lim) -> ResultadoEstabilidad:
    """Equilibrio de cuerpo rígido en servicio. `fuerzas_h` = [(F horizontal kN/m, brazo sobre la base)]; kh aplica inercia a las piezas."""
    B = g.ancho_base
    x_top = g.b_puntera + g.t_corona
    q_tal = r.sobrecarga_kpa * (B - x_top) if con_sobrecarga else 0.0
    inercia = [(kh * f, y) for _, f, _, y in pesos] if kh > 0 else []
    v_est = sum(f for _, f, _, _ in pesos) + pv
    m_est = sum(f * x for _, f, x, _ in pesos) + pv * B
    ph = sum(f for f, _ in fuerzas_h) + sum(f for f, _ in inercia)
    m_vuelco = sum(f * a for f, a in fuerzas_h) + sum(f * a for f, a in inercia)
    v_b, m_b = v_est + q_tal, m_est + q_tal * (x_top + (B - x_top) / 2.0)
    x_r = (m_b - m_vuelco) / v_b
    e = B / 2.0 - x_r
    q_max, q_min = v_b / B * (1.0 + 6.0 * e / B), v_b / B * (1.0 - 6.0 * e / B)
    mu = mu_efectivo(g, s)
    fs_v = m_est / m_vuelco
    fs_d = (v_est * mu + s.c_kpa * B) / ph if ph > 0 else math.inf
    motivos = []
    if fs_v < lim["vol"]:
        motivos.append(f"volcamiento {fs_v:.2f} < {lim['vol']} (H.6.9-1)")
    if fs_d < lim["des"]:
        motivos.append(f"deslizamiento {fs_d:.2f} < {lim['des']} (H.6.9-1)")
    if e > lim["exc"] * B:
        motivos.append(f"excentricidad {e:.3f} m > {lim['exc'] * B:.3f} m (H.6.9-1)")
    if q_max > s.q_adm_kpa * lim["q"]:
        motivos.append(f"presión máxima {q_max:.1f} kPa > {s.q_adm_kpa * lim['q']:.1f} kPa")
    if g.desplante < DESPLANTE_MIN_M:
        motivos.append(f"desplante {g.desplante:.2f} m < {DESPLANTE_MIN_M} m (H.6.7a)")
    vol, enc = _encofrado_y_volumen(g, pesos, gamma_c)
    ka = coeficiente_activo_rankine(r.phi_deg, r.beta_deg)
    return ResultadoEstabilidad(not motivos, tuple(motivos), ka, ph, 0.0, fs_v, fs_d, e, q_max, q_min, v_est, vol, enc, mu, kh, 0.0, ph)


LIM_ESTATICO = {"vol": FS_VOLCAMIENTO_MIN, "des": FS_DESLIZAMIENTO_MIN, "exc": EXCENTRICIDAD_MAX_B, "q": 1.0}
# Tabla H.6.9-1 seudoestático; la presión se compara con 2·q_adm porque F_SICP baja de 3,0 a 1,5 (Tabla H.4.7-1) si q_adm = q_ult/3 (HIPÓTESIS)
LIM_SISMICO = {"vol": 2.0, "des": 1.05, "exc": 0.25, "q": 2.0}


def verificar_estabilidad(g: GeometriaMuro, r: Relleno, s: SueloApoyo, *, gamma_concreto: float = GAMMA_CONCRETO_KN_M3) -> ResultadoEstabilidad:
    """Verificación de estabilidad externa estática en servicio. Devuelve los factores y las razones de incumplimiento."""
    g.validar()
    ka, h, pa_s, pa_q, br_s, br_q = _empuje_estatico(g, r)
    beta = math.radians(r.beta_deg)
    pesos = _piezas(g, r, gamma_concreto)
    pv = (pa_s + pa_q) * math.sin(beta)
    res = _resolver(g, r, s, gamma_concreto, pesos, [(pa_s * math.cos(beta), br_s), (pa_q * math.cos(beta), br_q)], pv, 0.0, True, LIM_ESTATICO)
    return replace(res, empuje_kn_m=pa_s + pa_q, h_empuje_m=h)


def verificar_estabilidad_sismica(g: GeometriaMuro, r: Relleno, s: SueloApoyo, a_max_g: float, *, ratio_kst: float = 0.80,
                                  gamma_concreto: float = GAMMA_CONCRETO_KN_M3) -> ResultadoEstabilidad:
    """Seudoestático: K_ST = ratio_kst·a_max (H.5.2.5/H.6.8; 0,80 mínimo para suelos sin análisis de amplificación), empuje de Mononobe-Okabe con
    incremento dinámico a 0,6 h (Seed y Whitman), inercia kh·W de concreto y relleno del talón. Sin sobrecarga viva simultánea (HIPÓTESIS)."""
    g.validar()
    kh = ratio_kst * a_max_g
    ka, h, pa_s, _, br_s, _ = _empuje_estatico(g, r)
    kae = coeficiente_activo_mononobe_okabe(r.phi_deg, r.beta_deg, kh)
    if math.isinf(kae):
        return ResultadoEstabilidad(False, ("Mononobe-Okabe sin solución (φ - θ - β < 0)",), ka, math.inf, h, 0.0, 0.0, math.inf, math.inf, 0.0, 0.0, 0.0, 0.0, 0.0, kh)
    pae = 0.5 * kae * r.gamma * h * h
    d_pae = max(pae - pa_s, 0.0)
    beta = math.radians(r.beta_deg)
    pesos = _piezas(g, r, gamma_concreto)
    pv = pae * math.sin(beta)
    res = _resolver(g, r, s, gamma_concreto, pesos, [(pa_s * math.cos(beta), br_s), (d_pae * math.cos(beta), 0.6 * h)], pv, kh, False, LIM_SISMICO)
    return replace(res, empuje_kn_m=pae, h_empuje_m=h, empuje_dinamico_kn_m=d_pae)
