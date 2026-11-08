"""Cortante sísmico en la base y fuerzas por nivel (NSR-10, método de la fuerza horizontal equivalente, Cap. A.4).

Cadena: Aa, Av (Apéndice A-4) + perfil de suelo → Fa, Fv (A.2.4-3/-4) → espectro Sa (A.2.6) → período Ta (A.4.2-3)
→ Vs = Sa·g·M (A.4.3-1) → Fx = Cvx·Vs (A.4.3-2/-3) → E = Fx / R (B.2.4.2.1, R = φa·φp·φr·R0, A.3.3-1).

Cada tabla y ecuación se verificó en el corpus nsr10_chunks (2026-11-08):
  Fa, Fv ........ NSR10-A-A_2_4_5_5_a_5_7_coeficientes_fa_fv_p1..p8 (interpolación lineal entre columnas, A.2.4.5.5/.6)
  Sa, Tc, TL .... NSR10-A-A_2_6_1_espectro_aceleraciones_p1..p9 (A.2.6-1 a A.2.6-5)
  I ............. NSR10-A-A_2_5_coeficiente_importancia_p14 (Tabla A.2.5-1)
  Ta, Ct, α, Cu . NSR10-A-A_4_2_periodo_fundamental_p4..p11 (A.4.2-2, A.4.2-3, A.4.2-5, Tabla A.4.2-1)
  Vs, k, Cvx .... NSR10-A-A_4_3_fuerzas_sismicas_horizontales_p1..p4 (A.4.3-1 a A.4.3-3)
  R0, Ω0 ........ NSR10-A-A3T3-1a / 2a / 3a (Tabla A.3-3, pórticos de concreto DES / DMO / DMI)
  φr ............ NSR10-A-A_3_3_8 (DMI = 1,0; DMO/DES = 1,0 solo si se cumplen las condiciones de redundancia, si no 0,75)
  Deriva ........ NSR10-A-A_6_4_limites_deriva_p1..p3 (Δ ≤ 1,0 % hpi para concreto, A.6.4-1)

NO incluido (declarado, no inventado): irregularidades φa y φp (se asumen estructura regular, φ = 1,0), efectos
torsionales (A.3.6.7), P-Delta (A.6.2.3), cortante basal mínimo, interacción suelo-estructura (A.7), perfil F.
Módulo autónomo (solo biblioteca estándar) para cargarse desde otros paquetes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

G = 9.8                                  # m/s², valor de la nomenclatura A.4.0
PERFILES = ("A", "B", "C", "D", "E")     # el perfil F exige estudio geotécnico particular (A.2.10)
COEF_COLUMNAS = (0.1, 0.2, 0.3, 0.4, 0.5)   # Aa o Av: ≤0,1 | 0,2 | 0,3 | 0,4 | ≥0,5

TABLA_FA = {"A": (0.8, 0.8, 0.8, 0.8, 0.8), "B": (1.0, 1.0, 1.0, 1.0, 1.0), "C": (1.2, 1.2, 1.1, 1.0, 1.0),
            "D": (1.6, 1.4, 1.2, 1.1, 1.0), "E": (2.5, 1.7, 1.2, 0.9, 0.9)}
TABLA_FV = {"A": (0.8, 0.8, 0.8, 0.8, 0.8), "B": (1.0, 1.0, 1.0, 1.0, 1.0), "C": (1.7, 1.6, 1.5, 1.4, 1.3),
            "D": (2.4, 2.0, 1.8, 1.6, 1.5), "E": (3.5, 3.2, 2.8, 2.4, 2.4)}

COEF_IMPORTANCIA = {"I": 1.00, "II": 1.10, "III": 1.25, "IV": 1.50}

# Tabla A.3-3, pórticos de concreto resistentes a momentos: (R0, Ω0)
R0_PORTICO_CONCRETO = {"DES": (7.0, 3.0), "DMO": (5.0, 3.0), "DMI": (2.5, 3.0)}

# Tabla A.4.2-1 (Ct, α)
CT_ALFA = {"porticos_concreto": (0.047, 0.9), "porticos_acero": (0.072, 0.8),
           "arriostrados_excentricos": (0.073, 0.75), "muros": (0.049, 0.75)}

DERIVA_MAX_CONCRETO = 0.010              # Tabla A.6.4-1, fracción de la altura de piso


def _interpolar(valor: float, tabla_fila: tuple[float, ...]) -> float:
    if valor <= COEF_COLUMNAS[0]:
        return tabla_fila[0]
    if valor >= COEF_COLUMNAS[-1]:
        return tabla_fila[-1]
    for k in range(len(COEF_COLUMNAS) - 1):
        x0, x1 = COEF_COLUMNAS[k], COEF_COLUMNAS[k + 1]
        if x0 <= valor <= x1:
            return tabla_fila[k] + (tabla_fila[k + 1] - tabla_fila[k]) * (valor - x0) / (x1 - x0)
    raise AssertionError("inalcanzable")


def _verificar_perfil(perfil: str) -> str:
    p = perfil.strip().upper()
    if p == "F":
        raise ValueError("Perfil F: requiere investigación geotécnica particular y análisis de amplificación de onda (A.2.10)")
    if p not in PERFILES:
        raise ValueError(f"perfil de suelo '{perfil}' no válido: {PERFILES}")
    return p


def coef_fa(aa: float, perfil: str) -> float:
    """Tabla A.2.4-3, interpolación lineal en Aa dentro del mismo tipo de perfil (A.2.4.5.5)."""
    return _interpolar(aa, TABLA_FA[_verificar_perfil(perfil)])


def coef_fv(av: float, perfil: str) -> float:
    """Tabla A.2.4-4, interpolación lineal en Av dentro del mismo tipo de perfil (A.2.4.5.6)."""
    return _interpolar(av, TABLA_FV[_verificar_perfil(perfil)])


def periodos_espectro(aa: float, av: float, fa: float, fv: float) -> tuple[float, float]:
    """(TC, TL) por A.2.6-2 y A.2.6-4."""
    if aa <= 0 or fa <= 0:
        raise ValueError("Aa y Fa deben ser positivos")
    return 0.48 * av * fv / (aa * fa), 2.4 * fv


def sa_espectro(T: float, aa: float, av: float, fa: float, fv: float, I: float = 1.0) -> float:
    """Ordenada del espectro elástico de diseño Sa/g para un período T ≥ 0 (A.2.6-1 con la meseta de A.2.6.1.1).

    Se usa la rama 1,2·Av·Fv·I/T también para T > TL (más alta que el mínimo de A.2.6-5, por tanto conservadora).
    """
    if T < 0:
        raise ValueError("T no puede ser negativo")
    plateau = 2.5 * aa * fa * I
    tc, _ = periodos_espectro(aa, av, fa, fv)
    if T <= tc:
        return plateau
    return min(plateau, 1.2 * av * fv * I / T)


def periodo_aproximado(h_total_m: float, sistema: str = "porticos_concreto") -> float:
    """Ta = Ct·h^α (A.4.2-3, Tabla A.4.2-1); h = altura desde la base hasta el piso más alto."""
    ct, alfa = CT_ALFA[sistema]
    return ct * h_total_m ** alfa


def cu(av: float, fv: float) -> float:
    """Cu = 1,75 − 1,2·Av·Fv, no menor de 1,2 (A.4.2-2)."""
    return max(1.2, 1.75 - 1.2 * av * fv)


def exponente_k(T: float) -> float:
    """A.4.3.2: k = 1 (T ≤ 0,5 s); 0,75 + 0,5·T (0,5 < T ≤ 2,5 s); 2 (T > 2,5 s)."""
    if T <= 0.5:
        return 1.0
    if T <= 2.5:
        return 0.75 + 0.5 * T
    return 2.0


def r_reducido(capacidad: str, *, phi_a: float = 1.0, phi_p: float = 1.0, phi_r: float = 1.0) -> float:
    """R = φa·φp·φr·R0 (A.3.3-1) para pórticos de concreto."""
    if capacidad not in R0_PORTICO_CONCRETO:
        raise ValueError(f"capacidad '{capacidad}' no válida: {tuple(R0_PORTICO_CONCRETO)}")
    for nombre, f in (("φa", phi_a), ("φp", phi_p), ("φr", phi_r)):
        if not 0 < f <= 1.0:
            raise ValueError(f"{nombre} debe estar en (0, 1]")
    return phi_a * phi_p * phi_r * R0_PORTICO_CONCRETO[capacidad][0]


def distribuir_fuerzas(vs: float, masas: tuple[float, ...], alturas_m: tuple[float, ...], T: float) -> tuple[float, ...]:
    """Fx = Cvx·Vs con Cvx = mx·hx^k / Σ mi·hi^k (A.4.3-2/-3). `alturas_m`: altura de cada nivel sobre la base."""
    if len(masas) != len(alturas_m) or not masas:
        raise ValueError("masas y alturas deben tener la misma longitud (≥ 1)")
    k = exponente_k(T)
    pesos = [m * h ** k for m, h in zip(masas, alturas_m)]
    s = sum(pesos)
    return tuple(vs * w / s for w in pesos)


@dataclass(frozen=True)
class CortanteBasal:
    aa: float
    av: float
    perfil: str
    grupo_uso: str
    capacidad: str
    fa: float
    fv: float
    I: float
    T: float
    cu_ta: float
    tc: float
    tl: float
    sa: float
    k: float
    r: float
    peso_total_kn: float
    vs_kn: float                      # cortante basal elástico (sin dividir por R)
    fuerzas_elasticas_kn: tuple[float, ...]   # Fx por nivel (Fs)
    fuerzas_diseno_kn: tuple[float, ...]      # E = Fs / R por nivel
    sa_deriva: float                  # Sa con I = 1,0 permitido para deriva (A.6.2.1.2)


def cortante_basal(*, aa: float, av: float, perfil: str, capacidad: str, pesos_nivel_kn: tuple[float, ...],
                   alturas_nivel_m: tuple[float, ...], grupo_uso: str = "I", phi_a: float = 1.0, phi_p: float = 1.0,
                   phi_r: float = 1.0, sistema: str = "porticos_concreto") -> CortanteBasal:
    """Vs, fuerzas por nivel y E de diseño. T = Ta (A.4.2.2); `alturas_nivel_m[-1]` es hn.

    pesos_nivel_kn: peso sísmico de cada nivel (kN) = masa·g, de abajo hacia arriba.
    """
    if grupo_uso not in COEF_IMPORTANCIA:
        raise ValueError(f"grupo de uso '{grupo_uso}' no válido: {tuple(COEF_IMPORTANCIA)}")
    if any(w <= 0 for w in pesos_nivel_kn):
        raise ValueError("Los pesos por nivel deben ser positivos")
    fa, fv = coef_fa(aa, perfil), coef_fv(av, perfil)
    I = COEF_IMPORTANCIA[grupo_uso]
    T = periodo_aproximado(alturas_nivel_m[-1], sistema)
    tc, tl = periodos_espectro(aa, av, fa, fv)
    sa = sa_espectro(T, aa, av, fa, fv, I)
    r = r_reducido(capacidad, phi_a=phi_a, phi_p=phi_p, phi_r=phi_r)
    w = float(sum(pesos_nivel_kn))
    vs = sa * w                                   # Vs = Sa·g·M = Sa·W
    fx = distribuir_fuerzas(vs, pesos_nivel_kn, alturas_nivel_m, T)
    return CortanteBasal(aa, av, perfil.upper(), grupo_uso, capacidad, fa, fv, I, T, cu(av, fv) * T, tc, tl, sa,
                         exponente_k(T), r, w, vs, fx, tuple(f / r for f in fx),
                         sa_espectro(T, aa, av, fa, fv, 1.0))
