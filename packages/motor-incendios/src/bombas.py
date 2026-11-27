"""Cuarto de bombas (#336 F7): bomba principal, jockey, NPSH desde el tanque subterráneo, tanque y espacio del cuarto.

Física en código (no normativa):
  - presión atmosférica según la altitud (atmósfera estándar): P = 101,325 · (1 − 2,25577e-5 · h)^5,25588 kPa;
  - presión de vapor del agua (Antoine, 1–100 °C): log10 P[mmHg] = 8,07131 − 1730,63 / (233,426 + T);
  - NPSH_disponible = (P_atm − P_vapor)/γ + (z_agua_mín − z_eje) − h_f,succión, en metros de columna de agua;
  - potencia en el eje = Q · ΔP / η.
Datos del proyecto, sin valores por defecto y con fuente:
  - catálogo de bombas con sus curvas (ΔP, NPSH requerido y eficiencia contra Q), su punto nominal, sus dimensiones
    y su costo;
  - criterios de curva (fracciones de Q y P nominal que exige la norma aplicable, p. ej. NFPA 20), rango admisible
    del caudal de diseño respecto al nominal, caudales en que se revisa el NPSH y margen de NPSH;
  - tamaños comerciales de motor y factor de servicio;
  - caudal de la jockey y su margen de presión sobre la principal;
  - geometría del tanque (altura útil máxima, altura no útil bajo la succión, borde libre, relación de lados) y
    holguras del cuarto;
  - si la norma aplicable admite succión negativa (agua bajo el eje de la bomba). Si no la admite, la bomba
    horizontal sobre un tanque subterráneo se rechaza y se informa: la alternativa es una bomba vertical tipo turbina
    o bajar el cuarto, y eso lo decide el diseñador.
El motor NO aprueba la selección: entrega la propuesta y sus verificaciones.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from typing import Optional

from . import hidraulica as h

G = h.GAMMA_AGUA_KPA_M


def presion_atmosferica_kpa(altitud_m: float) -> float:
    return 101.325 * (1 - 2.25577e-5 * altitud_m) ** 5.25588


def presion_vapor_kpa(t_c: float) -> float:
    if not 1 <= t_c <= 100:
        raise ValueError("Antoine (agua) válida entre 1 y 100 °C")
    return 10 ** (8.07131 - 1730.63 / (233.426 + t_c)) * 0.133322


def _interp(pts: list, q: float) -> Optional[float]:
    """Interpolación lineal en una curva [(Q, y)] ordenada; None fuera del rango (no se extrapola)."""
    qs = [p[0] for p in pts]
    if q < qs[0] - 1e-9 or q > qs[-1] + 1e-9:
        return None
    i = min(max(bisect.bisect_left(qs, q), 1), len(qs) - 1)
    (q0, y0), (q1, y1) = pts[i - 1], pts[i]
    return y0 if q1 == q0 else y0 + (y1 - y0) * (q - q0) / (q1 - q0)


@dataclass(frozen=True)
class Bomba:
    id: str
    q_nominal_lpm: float
    p_nominal_kpa: float
    curva_kpa: tuple            # ((Q L/min, ΔP kPa), ...) desde Q = 0 (cierre)
    npshr_m: tuple              # ((Q, NPSH requerido m), ...)
    eficiencia: tuple           # ((Q, η), ...)
    largo_m: float              # huella del grupo bomba-motor
    ancho_m: float
    costo: float

    def __post_init__(self):
        for c in (self.curva_kpa, self.npshr_m, self.eficiencia):
            if list(c) != sorted(c) or len(c) < 2:
                raise ValueError(f"{self.id}: curva sin ordenar o con menos de 2 puntos")
        if self.curva_kpa[0][0] != 0:
            raise ValueError(f"{self.id}: la curva debe empezar en Q = 0 (cierre)")


@dataclass(frozen=True)
class CriterioCurva:
    fraccion_q_nominal: float          # p. ej. 0 (cierre) o 1,5
    p_min_frac: Optional[float]        # ΔP mínima como fracción de la nominal en ese caudal
    p_max_frac: Optional[float]


@dataclass(frozen=True)
class Succion:
    altitud_m: float
    temperatura_c: float
    z_agua_min_m: float                # nivel mínimo útil del tanque
    z_eje_bomba_m: float
    tuberia: h.Tuberia
    largo_m: float                     # largo real + equivalente de accesorios de la succión
    admite_succion_negativa: bool      # lo que diga la norma aplicable
    fuente: str


@dataclass(frozen=True)
class CriteriosBomba:
    curva: tuple                       # (CriterioCurva, ...)
    q_diseno_frac_nominal: tuple       # (mín, máx) admisibles para Q_diseño / Q_nominal
    q_npsh_frac_nominal: tuple         # fracciones del Q nominal donde se revisa NPSH (p. ej. (1.0, 1.5))
    margen_npsh_m: float
    motores_kw: tuple                  # tamaños comerciales
    factor_servicio: float
    q_jockey_lpm: float
    margen_jockey_kpa: float           # presión de la jockey sobre la de cierre de la principal
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de los criterios de bomba")


@dataclass
class Verificacion:
    bomba: str
    cumple: bool
    motivos: list
    dp_en_diseno_kpa: Optional[float] = None
    npsha_m: dict = field(default_factory=dict)
    npshr_m: dict = field(default_factory=dict)
    p_eje_max_kw: Optional[float] = None
    motor_kw: Optional[float] = None


def npsh_disponible_m(s: Succion, q_lpm: float) -> float:
    hf_m = h.perdida_hw_kpa(q_lpm, s.tuberia.d_int_m, s.tuberia.c_hw, s.largo_m) / G
    return (presion_atmosferica_kpa(s.altitud_m) - presion_vapor_kpa(s.temperatura_c)) / G \
        + (s.z_agua_min_m - s.z_eje_bomba_m) - hf_m


def verificar_bomba(b: Bomba, q_d: float, p_d: float, s: Succion, c: CriteriosBomba) -> Verificacion:
    v = Verificacion(b.id, True, [])
    if s.z_agua_min_m < s.z_eje_bomba_m and not s.admite_succion_negativa:
        v.motivos.append("succión negativa (agua bajo el eje) no admitida: bomba vertical tipo turbina o bajar el cuarto")
    r = q_d / b.q_nominal_lpm
    if not c.q_diseno_frac_nominal[0] - 1e-9 <= r <= c.q_diseno_frac_nominal[1] + 1e-9:
        v.motivos.append(f"Q_diseño = {r:.2f} · Q_nominal, fuera de {c.q_diseno_frac_nominal}")
    v.dp_en_diseno_kpa = _interp(list(b.curva_kpa), q_d)
    if v.dp_en_diseno_kpa is None or v.dp_en_diseno_kpa < p_d - 1e-9:
        v.motivos.append(f"no entrega {p_d:.1f} kPa a {q_d:.0f} L/min")
    for cc in c.curva:
        q = cc.fraccion_q_nominal * b.q_nominal_lpm
        dp = _interp(list(b.curva_kpa), q)
        if dp is None:
            v.motivos.append(f"la curva no llega a {cc.fraccion_q_nominal:.2f} · Q_nominal")
            continue
        f = dp / b.p_nominal_kpa
        if cc.p_min_frac is not None and f < cc.p_min_frac - 1e-9:
            v.motivos.append(f"a {cc.fraccion_q_nominal:.2f}·Q_nom da {f:.2f}·P_nom < {cc.p_min_frac}")
        if cc.p_max_frac is not None and f > cc.p_max_frac + 1e-9:
            v.motivos.append(f"a {cc.fraccion_q_nominal:.2f}·Q_nom da {f:.2f}·P_nom > {cc.p_max_frac}")
    for fr in c.q_npsh_frac_nominal:
        q = fr * b.q_nominal_lpm
        a, rq = npsh_disponible_m(s, q), _interp(list(b.npshr_m), q)
        v.npsha_m[fr], v.npshr_m[fr] = a, rq
        if rq is None or a < rq + c.margen_npsh_m - 1e-9:
            v.motivos.append(f"NPSH a {fr:.2f}·Q_nom: disponible {a:.2f} m < requerido {rq} + margen {c.margen_npsh_m}")
    # Potencia máxima en el eje sobre el tramo de curva con datos de eficiencia (sin sobrecarga en ese rango).
    qmax = min(b.curva_kpa[-1][0], b.eficiencia[-1][0])
    qs = [q for q, _ in b.curva_kpa if b.eficiencia[0][0] <= q <= qmax] + [qmax]
    pots = [(q / 60000.0) * _interp(list(b.curva_kpa), q) / _interp(list(b.eficiencia), q) for q in qs
            if _interp(list(b.eficiencia), q)]
    v.p_eje_max_kw = max(pots) if pots else None
    if v.p_eje_max_kw is not None:
        req = v.p_eje_max_kw * c.factor_servicio
        v.motor_kw = next((m for m in sorted(c.motores_kw) if m >= req - 1e-9), None)
        if v.motor_kw is None:
            v.motivos.append(f"ningún motor del catálogo cubre {req:.1f} kW")
    v.cumple = not v.motivos
    return v


@dataclass(frozen=True)
class GeometriaTanque:
    altura_util_max_m: float
    altura_no_util_m: float            # bajo la boca de succión (incluida la sumergencia antivórtice declarada)
    borde_libre_m: float
    relacion_lados: float              # largo / ancho
    fuente: str


@dataclass
class Tanque:
    volumen_util_m3: float
    largo_m: float
    ancho_m: float
    altura_total_m: float
    altura_util_m: float

    @property
    def volumen_bruto_m3(self) -> float:
        return self.largo_m * self.ancho_m * self.altura_total_m


def dimensionar_tanque(volumen_util_m3: float, g: GeometriaTanque) -> Tanque:
    """Planta con la relación de lados declarada y la altura útil máxima. El tanque es subterráneo, así que se busca
    la menor huella."""
    hu = g.altura_util_max_m
    area = volumen_util_m3 / hu
    ancho = math.sqrt(area / g.relacion_lados)
    return Tanque(volumen_util_m3, g.relacion_lados * ancho, ancho, hu + g.altura_no_util_m + g.borde_libre_m, hu)


@dataclass(frozen=True)
class Holguras:
    entre_equipos_m: float
    perimetral_m: float
    tablero_largo_m: float             # tableros de control (principal y jockey) en la misma fila
    tablero_ancho_m: float
    fuente: str


@dataclass
class CuartoBombas:
    principal: Verificacion
    candidatas: list
    p_jockey_kpa: float
    q_jockey_lpm: float
    largo_m: float
    ancho_m: float

    @property
    def area_m2(self) -> float:
        return self.largo_m * self.ancho_m


def disenar(q_d: float, p_d: float, catalogo: list, s: Succion, c: CriteriosBomba, jockey: Bomba,
            holg: Holguras) -> CuartoBombas:
    """Elige la bomba principal más barata que cumple todas las verificaciones, y dimensiona la jockey y el cuarto.
    q_d y p_d vienen de F6 (caudal total con mangueras y P_bomba)."""
    ver = [verificar_bomba(b, q_d, p_d, s, c) for b in catalogo]
    ok = [(b, v) for b, v in zip(catalogo, ver) if v.cumple]
    if not ok:
        raise ValueError("ninguna bomba del catálogo cumple: " + "; ".join(f"{v.bomba}: {v.motivos}" for v in ver))
    b, v = min(ok, key=lambda bv: bv[0].costo)
    p_jockey = b.curva_kpa[0][1] + c.margen_jockey_kpa     # sobre la presión de cierre de la principal
    if _interp(list(jockey.curva_kpa), c.q_jockey_lpm) is None or _interp(list(jockey.curva_kpa), c.q_jockey_lpm) < p_jockey:
        raise ValueError(f"la jockey {jockey.id} no entrega {p_jockey:.0f} kPa a {c.q_jockey_lpm:.0f} L/min")
    largo = b.largo_m + jockey.largo_m + holg.tablero_largo_m + 2 * holg.entre_equipos_m + 2 * holg.perimetral_m
    ancho = max(b.ancho_m, jockey.ancho_m, holg.tablero_ancho_m) + 2 * holg.perimetral_m
    return CuartoBombas(v, ver, p_jockey, c.q_jockey_lpm, largo, ancho)
