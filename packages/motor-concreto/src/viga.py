"""Verificación de una viga rectangular de concreto reforzado (NSR-10 Título C).

Alcance del prototipo (declarado, no ocultar):
  - Viga simplemente apoyada, carga gravitacional uniforme, sección rectangular.
  - Una sola capa de barras longitudinales, estribos uniformes, concreto de peso normal (λ = 1).
  - Cortante crítico a d de la cara del apoyo (C.11.1.3.1); aquí se usa Vu = wu·(L/2 − d).
  - NO incluye detallado sísmico del Capítulo C.21 (DES/DMO), torsión, ni deflexiones a largo plazo.
Unidades: mm, MPa, kN, kN·m.

Fórmulas verificadas contra el corpus nsr10_chunks (numerales entre paréntesis).
NO recuperados del corpus (marcados): φ de cortante = 0,75 (C.9.3.2.3) y l/16 de la Tabla C.9.5(a).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# Diámetros nominales de barra (mm) por designación #3..#8 y área (mm²)
DIAMETRO_MM = {"3": 9.5, "4": 12.7, "5": 15.9, "6": 19.1, "7": 22.2, "8": 25.4}
AREA_MM2 = {k: math.pi / 4 * d**2 for k, d in DIAMETRO_MM.items()}

PHI_FLEXION = 0.90          # C.9.3.2.1, sección controlada por tensión
PHI_CORTANTE = 0.75         # C.9.3.2.3 — verificado en el corpus (2026-11-08)
EPS_CU = 0.003              # C.10.2.3
EPS_T_MIN = 0.005           # sección controlada por tensión (C.10.3.4); el límite 0,004 de C.10.3.5 es menos exigente
ALTURA_MIN_SIMPLE_L_SOBRE = 16.0   # Tabla C.9.5(a) — verificado en el corpus (etapa 1, 2026-11)
PESO_UNIT_CONCRETO_KN_M3 = 24.0


def beta1(fc: float) -> float:
    """C.10.2.7.3."""
    return min(0.85, max(0.65, 0.85 - 0.05 * (fc - 28.0) / 7.0))


@dataclass(frozen=True)
class Materiales:
    fc: float = 21.0     # MPa
    fy: float = 420.0    # MPa longitudinal
    fyt: float = 420.0   # MPa estribos


@dataclass(frozen=True)
class Seccion:
    b: float                  # mm
    h: float                  # mm
    barras_n: int
    barras_dia: str           # "5" = #5
    estribo_dia: str          # "3" = #3
    estribo_s: float          # mm
    ramas: int = 2
    recubrimiento: float = 40.0   # mm libres al estribo (C.7.7)
    barras_sup_n: int = 0         # barras superiores del mismo diámetro (diseño sísmico: refuerzo simétrico); solo afecta cantidades/costo y separación

    @property
    def d(self) -> float:
        return self.h - self.recubrimiento - DIAMETRO_MM[self.estribo_dia] - DIAMETRO_MM[self.barras_dia] / 2

    @property
    def As(self) -> float:
        return self.barras_n * AREA_MM2[self.barras_dia]

    @property
    def Av(self) -> float:
        return self.ramas * AREA_MM2[self.estribo_dia]


@dataclass(frozen=True)
class Cargas:
    """Cargas de servicio distribuidas en kN/m, SIN peso propio (se calcula aquí)."""
    muerta: float
    viva: float
    luz_m: float


@dataclass(frozen=True)
class Verificacion:
    nombre: str
    demanda: float
    capacidad: float
    unidad: str
    cumple: bool
    norma: str
    nota: str = ""

    @property
    def razon(self) -> float:
        return self.demanda / self.capacidad if self.capacidad else math.inf


@dataclass(frozen=True)
class Resultado:
    cumple: bool
    wu: float
    Mu: float
    Vu: float
    verificaciones: tuple[Verificacion, ...] = field(default_factory=tuple)

    def fallas(self) -> list[Verificacion]:
        return [v for v in self.verificaciones if not v.cumple]


def peso_propio_kn_m(b_mm: float, h_mm: float) -> float:
    return PESO_UNIT_CONCRETO_KN_M3 * b_mm / 1000 * h_mm / 1000


def combinacion_ultima(c: Cargas, b_mm: float, h_mm: float) -> tuple[float, float, float]:
    """wu = 1,2 D + 1,6 L (B.2.4-2), D incluye el peso propio. Devuelve (wu, Mu, V en el eje del apoyo)."""
    D = c.muerta + peso_propio_kn_m(b_mm, h_mm)
    wu = 1.2 * D + 1.6 * c.viva
    return wu, wu * c.luz_m**2 / 8, wu * c.luz_m / 2


def momento_nominal(s: Seccion, m: Materiales) -> tuple[float, float, float]:
    """(φMn en kN·m, a en mm, εt)."""
    a = s.As * m.fy / (0.85 * m.fc * s.b)
    Mn = s.As * m.fy * (s.d - a / 2) / 1e6
    c = a / beta1(m.fc)
    eps_t = EPS_CU * (s.d - c) / c if c > 0 else math.inf
    return PHI_FLEXION * Mn, a, eps_t


def as_minimo(s: Seccion, m: Materiales) -> float:
    """C.10.5.1."""
    return max(math.sqrt(m.fc) / (4 * m.fy), 1.4 / m.fy) * s.b * s.d


def espaciamiento_libre(s: Seccion) -> tuple[float, float]:
    """(libre disponible entre barras, mínimo exigido) en mm. C.7.6.1: máx(db, 25 mm)."""
    db = DIAMETRO_MM[s.barras_dia]
    ancho = s.b - 2 * (s.recubrimiento + DIAMETRO_MM[s.estribo_dia])
    libre = (ancho - s.barras_n * db) / (s.barras_n - 1) if s.barras_n > 1 else math.inf
    return libre, max(db, 25.0)


def verificar(s: Seccion, m: Materiales, c: Cargas) -> Resultado:
    wu, Mu, _ = combinacion_ultima(c, s.b, s.h)
    Vu = wu * (c.luz_m / 2 - s.d / 1000)
    v: list[Verificacion] = []

    phiMn, _, eps_t = momento_nominal(s, m)
    v.append(Verificacion("Flexión φMn ≥ Mu", Mu, phiMn, "kN·m", phiMn >= Mu, "C.10.2 / C.9.3.2.1"))
    v.append(Verificacion("Ductilidad εt ≥ 0,005", EPS_T_MIN, eps_t, "-", eps_t >= EPS_T_MIN,
                          "C.10.3.4 / C.10.3.5", "exigencia conservadora: sección controlada por tensión"))
    v.append(Verificacion("As ≥ As,mín", as_minimo(s, m), s.As, "mm²", s.As >= as_minimo(s, m), "C.10.5.1"))

    libre, minimo = espaciamiento_libre(s)
    v.append(Verificacion("Separación libre entre barras", minimo, libre, "mm", libre >= minimo, "C.7.6.1"))

    raiz = math.sqrt(m.fc)
    Vc = 0.17 * raiz * s.b * s.d / 1000                           # C.11.2.1.1
    Vs = s.Av * m.fyt * s.d / s.estribo_s / 1000                  # C.11.4.7.2
    phiVn = PHI_CORTANTE * (Vc + Vs)
    v.append(Verificacion("Cortante φ(Vc+Vs) ≥ Vu", Vu, phiVn, "kN", phiVn >= Vu, "C.11.2.1.1 / C.11.4.7.2",
                          "φ=0,75 verificado (C.9.3.2.3)"))
    Vs_max = 0.66 * raiz * s.b * s.d / 1000                       # C.11.4.7.9
    v.append(Verificacion("Vs ≤ 0,66√f'c·b·d", Vs, Vs_max, "kN", Vs <= Vs_max, "C.11.4.7.9"))
    s_max = min(s.d / 2, 600.0) if Vs <= 0.33 * raiz * s.b * s.d / 1000 else min(s.d / 4, 300.0)   # C.11.4.5.1
    v.append(Verificacion("Separación de estribos s ≤ s,máx", s.estribo_s, s_max, "mm", s.estribo_s <= s_max, "C.11.4.5.1"))
    if Vu > PHI_CORTANTE * Vc / 2:                                # C.11.4.6.1
        av_min = max(0.062 * raiz * s.b * s.estribo_s / m.fyt, 0.35 * s.b * s.estribo_s / m.fyt)   # C.11.4.6.3
        v.append(Verificacion("Av ≥ Av,mín", av_min, s.Av, "mm²", s.Av >= av_min, "C.11.4.6.3"))

    h_min = c.luz_m * 1000 / ALTURA_MIN_SIMPLE_L_SOBRE
    v.append(Verificacion("Altura mínima h ≥ l/16 (sin verificar deflexiones)", h_min, s.h, "mm", s.h >= h_min,
                          "Tabla C.9.5(a)", "l/16 vigas simplemente apoyadas, fy=420 MPa (verificado en el corpus)"))
    return Resultado(all(x.cumple for x in v), wu, Mu, Vu, tuple(v))
