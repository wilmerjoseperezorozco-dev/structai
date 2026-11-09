"""Estabilidad de taludes de excavación por equilibrio límite (Bishop simplificado), por metro de frente (deformación plana). Fase 1a del frente de excavaciones.

Qué hace: dado el perfil del talud (altura, ángulo, bermas), un suelo homogéneo (c, φ, γ), el nivel freático, una sobrecarga en la corona y un coeficiente sísmico
seudoestático, busca la superficie circular más crítica y entrega su factor de seguridad; con él halla el ángulo máximo que cumple el factor exigido por la NSR-10.

Norma (leída del PDF fuente el 2026-11-09):
- H.5.1.2.1: la estabilidad de excavaciones sin soporte se revisa con un método de equilibrio límite con superficies cinemáticamente posibles, considerando agua,
  profundidad, inclinación, agrietamiento cerca de la corona y sobrecargas. La norma NO da un ángulo ni una tabla de inclinaciones. La cohesión de las arcillas puede
  disminuir hasta 30 % en un mes (parámetro `reducir_cohesion`).
- Tabla H.2.4-1 (FSBM, esfuerzos efectivos): taludes estáticos 1,50 (diseño) y 1,25 (construcción); seudoestáticos 1,05 y 1,00, con parámetros sísmicos de construcción
  iguales al 50 % de los de diseño. FSBUM (resistencia no drenada Su): 1,80 y 1,40 estáticos; con sismo no se permite. H.2.4.2 admite Su solo para taludes TEMPORALES
  en cohesivos saturados y no fisurados, y no para taludes permanentes, materiales no saturados o fisurados, ni análisis seudoestáticos.

HIPÓTESIS DE INVESTIGACIÓN (no están en la norma): (1) Bishop simplificado con búsqueda de círculos (rejilla y refinamiento); (2) suelo homogéneo; (3) freática
horizontal, con presión de poros hidrostática limitada a la superficie del terreno (sin red de flujo): si queda sobre el fondo de la excavación hay flujo y se marca `requiere_abatimiento`; (4) grieta de tracción SECA (sin empuje hidrostático: no conservador con agua alta) de
profundidad 2c/(γ√Ka) (conservadora respecto de una grieta inexistente); (5) sobrecarga en franja uniforme sin dispersión (la parte que cae sobre la masa trasera que corta la grieta se descarta junto con ella); (5b) la superficie de falla no baja más de 1,2·H bajo el pie salvo que se dé `prof_estrato_firme` (hipótesis de estrato firme, no dato: ver `en_borde_dominio`); (6) sismo como fuerza horizontal kh·W en el
centroide de cada dovela. No cubre falla de fondo, flujo, suelos estratificados ni superficies no circulares. No es un estudio geotécnico (H.1): los parámetros son del sitio.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np
from scipy.optimize import minimize

GAMMA_AGUA_KN_M3 = 9.81
FS_BASICO = {                        # Tabla H.2.4-1: (estado, sismo) -> (FSBM efectivos, FSBUM no drenado)
    ("diseno", False): (1.50, 1.80),
    ("construccion", False): (1.25, 1.40),
    ("diseno", True): (1.05, None),
    ("construccion", True): (1.00, None),
}
FRACCION_SISMO_CONSTRUCCION = 0.50   # nota (*) de la Tabla H.2.4-1
N_MALLA, N_DOVELAS, FS_INVALIDO = 400, 60, 1.0e3
PROF_BASE = (-0.05, 0.0, 0.1, 0.25, 0.5, 0.8, 1.2)        # profundidad del punto más bajo bajo el pie, fracción de la altura
N_PULIDOS = 6
FACTOR_RADIO_MAX = 15.0      # R máximo = 15 x max(H, retiro de la corona)


@dataclass(frozen=True)
class SueloExc:
    gamma: float                    # peso unitario sobre el nivel freático (kN/m3)
    c_kpa: float                    # cohesión efectiva (o Su si phi = 0 en análisis no drenado)
    phi_deg: float                  # fricción efectiva
    gamma_sat: float | None = None  # peso unitario saturado; si None, igual a gamma

    def __post_init__(self) -> None:
        if self.gamma <= 0 or self.c_kpa < 0 or not 0.0 <= self.phi_deg < 60.0:
            raise ValueError("suelo: gamma > 0, c >= 0 y 0 <= phi < 60°")
        if self.gamma_sat is not None and self.gamma_sat <= 0:
            raise ValueError("suelo: gamma_sat > 0")

    @property
    def gamma_saturado(self) -> float:
        return self.gamma if self.gamma_sat is None else self.gamma_sat


def reducir_cohesion(suelo: SueloExc, fraccion: float = 0.30) -> SueloExc:
    """H.5.1.2.1: la cohesión de arcillas puede disminuir hasta 30 % en un mes de excavación abierta."""
    if not 0.0 <= fraccion < 1.0:
        raise ValueError("fraccion en [0, 1)")
    return replace(suelo, c_kpa=suelo.c_kpa * (1.0 - fraccion))


@dataclass(frozen=True)
class Perfil:
    xs: tuple[float, ...]
    ys: tuple[float, ...]
    altura: float
    x_cresta: float

    def terreno(self, x):
        return np.interp(x, self.xs, self.ys)


def perfil_talud(altura: float, angulo_deg: float, bermas: tuple[tuple[float, float], ...] = ()) -> Perfil:
    """Pie en (0, 0), fondo de la excavación a la izquierda, corona a la derecha. `bermas`: ((cota sobre el pie, ancho), ...) con 0 < cota < altura, en orden ascendente."""
    if altura <= 0 or not 0.0 < angulo_deg <= 90.0:
        raise ValueError("altura > 0 y ángulo en (0°, 90°]")
    cots = [y for y, _ in bermas]
    if any(not 0.0 < y < altura for y in cots) or cots != sorted(cots) or any(a <= 0 for _, a in bermas):
        raise ValueError("bermas: cota entre 0 y la altura, ascendentes y de ancho > 0")
    cot = 1.0 / math.tan(math.radians(angulo_deg)) if angulo_deg < 90.0 else 0.0
    x, y, pts = 0.0, 0.0, [(0.0, 0.0)]
    for yb, ancho in list(bermas) + [(altura, 0.0)]:
        x += max((yb - y) * cot, 1e-6)
        y = yb
        pts.append((x, y))
        if ancho > 0:
            x += ancho
            pts.append((x, y))
    ext = 100.0 * altura
    pts = [(-ext, 0.0)] + pts + [(x + ext, altura)]
    return Perfil(tuple(p[0] for p in pts), tuple(p[1] for p in pts), altura, x)


def factor_seguridad_requerido(estado: str, sismo: bool, analisis: str = "efectivo") -> float:
    """Tabla H.2.4-1. `analisis`: 'efectivo' (c', φ'; FSBM) o 'no_drenado' (Su; FSBUM, solo taludes temporales de cohesivos saturados no fisurados, sin sismo)."""
    if estado not in ("diseno", "construccion") or analisis not in ("efectivo", "no_drenado"):
        raise ValueError("estado: 'diseno'|'construccion'; analisis: 'efectivo'|'no_drenado'")
    basico, no_drenado = FS_BASICO[(estado, bool(sismo))]
    if analisis == "efectivo":
        return basico
    if no_drenado is None:
        raise ValueError("H.2.4.2/Tabla H.2.4-1: con sismo seudoestático no se permite el análisis con resistencia no drenada")
    return no_drenado


def kh_construccion(kh_diseno: float) -> float:
    """Nota (*) de la Tabla H.2.4-1: los parámetros sísmicos de construcción son el 50 % de los de diseño."""
    return FRACCION_SISMO_CONSTRUCCION * kh_diseno


def altura_critica_vertical_rankine(suelo: SueloExc) -> float:
    """4c/(γ√Ka) = 4c/γ · tan(45° + φ/2): altura del corte vertical sin soporte con empuje activo de Rankine (cierre planar con grieta de tracción; el mejor círculo sin grieta da una altura mayor, ver tests)."""
    return 4.0 * suelo.c_kpa / suelo.gamma * math.tan(math.radians(45.0 + suelo.phi_deg / 2.0))


@dataclass(frozen=True)
class ResultadoTalud:
    fs: float
    xc: float
    yc: float
    radio: float
    profundidad_grieta_m: float
    requiere_abatimiento: bool
    en_borde_dominio: bool = False          # el óptimo toca la cota de radio o de profundidad: el FS depende de esa cota (ver prof_estrato_firme)


def _fs_circulo(xc, yc, radio, perfil: Perfil, suelo: SueloExc, y_agua, q, q_x, kh, z_grieta) -> float:
    xs = np.linspace(xc - radio, xc + radio, N_MALLA)
    y_bot = yc - np.sqrt(np.maximum(radio**2 - (xs - xc) ** 2, 0.0))
    f = perfil.terreno(xs) - y_bot
    dentro = f > 0
    if not dentro.any() or dentro[0] or dentro[-1]:
        return FS_INVALIDO             # el círculo no aflora a ambos lados: no es un mecanismo de talud
    i0 = int(np.argmax(dentro))
    i1 = len(dentro) - 1 - int(np.argmax(dentro[::-1]))
    if not dentro[i0:i1 + 1].all():
        return FS_INVALIDO             # tramos fuera del terreno en medio: círculo atravesado por la superficie
    x_izq = xs[i0 - 1] + (xs[i0] - xs[i0 - 1]) * (-f[i0 - 1]) / (f[i0] - f[i0 - 1])
    x_der = xs[i1] + (xs[i1 + 1] - xs[i1]) * f[i1] / (f[i1] - f[i1 + 1])
    b = (x_der - x_izq) / N_DOVELAS
    xm = x_izq + b * (np.arange(N_DOVELAS) + 0.5)
    yb = yc - np.sqrt(np.maximum(radio**2 - (xm - xc) ** 2, 1e-12))
    yt = perfil.terreno(xm)
    if z_grieta > 0.0:
        quedan = ~((yb > perfil.terreno(x_der) - z_grieta) & (xm > xc))        # la grieta seca vertical separa la parte posterior (a la derecha del punto más bajo): esa masa no desliza
        if quedan.sum() < 5:
            return FS_INVALIDO
        xm, yb, yt = xm[quedan], yb[quedan], yt[quedan]
    h = yt - yb
    sin_a = (xm - xc) / radio
    cos_a = np.sqrt(np.maximum(1.0 - sin_a**2, 1e-12))
    if y_agua is None:
        w = suelo.gamma * h * b
        u = np.zeros_like(h)
    else:
        arriba = np.maximum(yt - np.maximum(yb, y_agua), 0.0)
        abajo = np.maximum(np.minimum(yt, y_agua) - yb, 0.0)
        w = (suelo.gamma * arriba + suelo.gamma_saturado * abajo) * b
        u = GAMMA_AGUA_KN_M3 * np.maximum(np.minimum(y_agua, yt) - yb, 0.0)        # carga piezométrica limitada a la superficie del terreno
    if q > 0.0:
        w = w + q * b * ((xm >= q_x[0]) & (xm <= q_x[1]))
    tan_phi = math.tan(math.radians(suelo.phi_deg))
    motor = float((w * sin_a).sum()) + (float((kh * w * (yc - 0.5 * (yt + yb))).sum()) / radio if kh > 0 else 0.0)
    if motor <= 1e-9:
        return FS_INVALIDO
    fs = 1.0
    for _ in range(60):
        m_alfa = cos_a + sin_a * tan_phi / fs
        if (m_alfa <= 0.2).any():
            return FS_INVALIDO
        nuevo = float(((suelo.c_kpa * b + np.maximum(w - u * b, 0.0) * tan_phi) / m_alfa).sum()) / motor
        if abs(nuevo - fs) < 1e-7:
            fs = nuevo
            break
        fs = nuevo
    else:
        return FS_INVALIDO             # Bishop no convergió en 60 iteraciones: se descarta el círculo (no se acepta un FS sin converger)
    return fs if fs > 0 else FS_INVALIDO


def factor_seguridad_talud(perfil: Perfil, suelo: SueloExc, prof_freatico: float | None = None, sobrecarga_kpa: float = 0.0,
                           sobrecarga_x: tuple[float, float] | None = None, kh: float = 0.0, grieta_traccion: bool = True,
                           prof_estrato_firme: float | None = None) -> ResultadoTalud:
    """FS mínimo de Bishop simplificado. `prof_freatico`: profundidad del agua bajo la corona (m); None = sin agua. `sobrecarga_x`: (x_ini, x_fin) de la franja en el sistema del perfil.
    `prof_estrato_firme`: profundidad (m, bajo el pie) de un estrato firme que limita la superficie de falla. Si es None se ASUME 1,2·H (cota de búsqueda, no un dato
    del sitio): en φ = 0 con sismo el FS decrece sin límite al agrandar el círculo, así que el resultado depende de esa cota y `en_borde_dominio` lo señala."""
    if sobrecarga_kpa < 0 or kh < 0 or (prof_freatico is not None and prof_freatico < 0):
        raise ValueError("sobrecarga, kh y profundidad freática deben ser >= 0")
    if sobrecarga_kpa > 0 and sobrecarga_x is None:
        sobrecarga_x = (perfil.x_cresta, perfil.x_cresta + 5.0 * perfil.altura)
    y_agua = None if prof_freatico is None else perfil.altura - prof_freatico
    z_grieta = 0.0
    if grieta_traccion and suelo.c_kpa > 0:
        ka = math.tan(math.radians(45.0 - suelo.phi_deg / 2.0)) ** 2
        z_grieta = min(2.0 * suelo.c_kpa / (suelo.gamma * math.sqrt(ka)), 0.9 * perfil.altura)
    args = (perfil, suelo, y_agua, sobrecarga_kpa, sobrecarga_x or (0.0, 0.0), kh, z_grieta)
    s = max(perfil.altura, perfil.x_cresta)
    if prof_estrato_firme is not None and prof_estrato_firme <= 0:
        raise ValueError("prof_estrato_firme debe ser > 0")
    r_max = FACTOR_RADIO_MAX * s
    y_min = prof_estrato_firme if prof_estrato_firme is not None else PROF_BASE[-1] * perfil.altura        # dominio de búsqueda: sin círculos gigantes ni más profundos que 1,2 H bajo el pie

    def fs_acotado(xc, yc, r):
        if r <= 0.0 or r > r_max or yc - r < -y_min:
            return FS_INVALIDO
        return _fs_circulo(xc, yc, r, *args)
    cx, cy, ff = np.linspace(-0.6 * perfil.altura, perfil.x_cresta + 1.5 * s, 12), np.linspace(0.3 * perfil.altura, 4.0 * s, 11), np.linspace(0.5, 2.5, 11)
    candidatos = []
    for x in cx:
        for y in cy:
            d = math.hypot(x, y)
            radios = [f * d for f in ff] + [y + pr * perfil.altura for pr in PROF_BASE]        # familia 2: parametrizada por el punto más bajo del círculo
            for r_c in radios:
                v = fs_acotado(x, y, r_c)
                if v < FS_INVALIDO:
                    candidatos.append((v, x, y, r_c))
    if not candidatos:
        raise ValueError("no se halló ninguna superficie de falla circular válida para este perfil y suelo (FS indeterminado)")
    candidatos.sort()
    mejor = candidatos[0]
    for v0, x0, y0, r0 in candidatos[:N_PULIDOS]:
        r = minimize(lambda p: fs_acotado(p[0], p[1], p[2]), [x0, y0, r0], method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-6, "maxiter": 250})
        if r.fun < mejor[0]:
            mejor = (float(r.fun), *map(float, r.x))
    en_borde = bool(mejor[3] >= 0.98 * r_max or (prof_estrato_firme is None and mejor[2] - mejor[3] <= -0.98 * y_min))
    return ResultadoTalud(mejor[0], mejor[1], mejor[2], mejor[3], z_grieta, bool(y_agua is not None and y_agua > 0), en_borde)


def altura_critica_bishop(suelo: SueloExc, angulo_deg: float = 90.0, h_max: float = 200.0, tol: float = 1e-3, **kw) -> float:
    """Altura para FS = 1 con el ángulo dado (bisección; el FS decrece con la altura)."""
    if factor_seguridad_talud(perfil_talud(h_max, angulo_deg), suelo, **kw).fs > 1.0:
        return float("inf")
    lo, hi = 0.05, h_max
    while hi - lo > tol * hi:
        mid = 0.5 * (lo + hi)
        if factor_seguridad_talud(perfil_talud(mid, angulo_deg), suelo, **kw).fs > 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def angulo_maximo_seguro(altura: float, suelo: SueloExc, fs_requerido: float, angulo_min_deg: float = 10.0, resolucion_deg: float = 0.1, **kw) -> float | None:
    """Mayor ángulo de talud (grados desde la horizontal, 90 = vertical) con FS >= fs_requerido; None si ni el ángulo mínimo cumple. El FS decrece con el ángulo (bisección); esto deja de valer si `sobrecarga_x` se da en coordenadas absolutas (la corona se desplaza al cambiar el ángulo): use el valor por defecto, que sigue a la corona."""
    if factor_seguridad_talud(perfil_talud(altura, 90.0), suelo, **kw).fs >= fs_requerido:
        return 90.0
    if factor_seguridad_talud(perfil_talud(altura, angulo_min_deg), suelo, **kw).fs < fs_requerido:
        return None
    lo, hi = angulo_min_deg, 90.0
    while hi - lo > resolucion_deg:
        mid = 0.5 * (lo + hi)
        if factor_seguridad_talud(perfil_talud(altura, mid), suelo, **kw).fs >= fs_requerido:
            lo = mid
        else:
            hi = mid
    return math.floor(lo / resolucion_deg) * resolucion_deg


@dataclass(frozen=True)
class DecisionExcavacion:
    """Resultado del selector: talud libre cuando cabe en el predio, contención temporal en caso contrario."""
    alternativa: str                      # "talud" | "contencion"
    angulo_deg: float | None              # ángulo máximo seguro (None si ninguno cumple)
    retiro_horizontal_m: float | None     # H / tan(beta): distancia en planta que ocupa el talud
    area_excavada_m2_por_m: float | None  # sección de corte por metro de longitud, ancho de fondo `ancho_fondo`
    fs_requerido: float
    advertencia: str | None = None


def decidir_talud_o_contencion(altura: float, suelo: SueloExc, distancia_lindero: float, estado: str = "construccion", sismo: bool = False,
                               analisis: str = "efectivo", ancho_fondo: float = 0.0, **kw) -> DecisionExcavacion:
    """Compara el talud más empinado que cumple la Tabla H.2.4-1 con el espacio disponible hasta el lindero. No dimensiona la contención ni calcula costos."""
    req = factor_seguridad_requerido(estado, sismo, analisis)
    kh = kw.get("kh", 0.0)
    if sismo and kh <= 0.0:
        raise ValueError("sismo=True exige kh > 0 (use kh_construccion(kh_diseno) para la condición de construcción): el FS requerido seudoestático no es comparable con un análisis estático")
    if kh > 0.0 and not sismo:
        raise ValueError("kh > 0 exige sismo=True para aplicar el FS requerido seudoestático de la Tabla H.2.4-1")
    ang = angulo_maximo_seguro(altura, suelo, req, **kw)
    if ang is None:
        return DecisionExcavacion("contencion", None, None, None, req)
    if "prof_estrato_firme" not in kw and factor_seguridad_talud(perfil_talud(altura, ang), suelo, **kw).en_borde_dominio:
        return DecisionExcavacion("contencion", ang, None, None, req, "el FS del talud depende de la cota de búsqueda (estrato firme supuesto a 1,2 H): sin dato de sitio no se acepta el talud; pase prof_estrato_firme")
    retiro = 0.0 if ang >= 90.0 else altura / math.tan(math.radians(ang))
    area = altura * (ancho_fondo + 0.5 * retiro)
    alt = "talud" if retiro <= distancia_lindero else "contencion"
    return DecisionExcavacion(alt, ang, retiro, area, req)
