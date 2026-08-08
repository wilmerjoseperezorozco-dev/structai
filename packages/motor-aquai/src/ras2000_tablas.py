"""
AquaAI — Tablas normativas embebidas como constantes
Fuente: Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico (RAS)
        Resolución 0330 de 2017, modificada por las Resoluciones 799 y 908 de 2021.

IMPORTANTE: estos valores son fijos por norma. NO se modifican con lógica de negocio.
La recalibración regional del bucle ↻ se aplica como factor externo, no tocando estas tablas.

NOTA DE VIGENCIA (auditoría 2026-08-08): RAS 2000 (Resolución 1096 de 2000) fue
derogada en su totalidad por la Resolución 0330 de 2017. Su metodología central
de "nivel de complejidad del sistema" (bajo/medio/medio_alto/alto) — usada antes
para derivar período de diseño, dotación neta y factores de consumo — NO existe
en el texto vigente (0 ocurrencias verificadas en el reglamento actual). La ley
vigente reemplazó ese esquema por criterios directos: altura sobre el nivel del
mar (dotación), tamaño de población (factores K1/K2), y un período de diseño
único para todos los sistemas. PERIODO_DISENO_ANIOS y DOTACION_NETA_MAXIMA_MSNM
FACTORES_CONSUMO y CAUDAL_INCENDIO fueron revisados en la misma auditoría y
reemplazados por factores_consumo_maximos() y caudal_incendio_minimo(),
basados en tamaño de población (Arts. 47 y 70) en vez de nivel de complejidad.
"""

from typing import Dict, List, Tuple

# ─── Dotación neta máxima por altura s.n.m. (Res. 0330/2017 Art. 43, Tabla 1) ─
# Valores en L/habitante/día. Reemplaza la extinta Tabla RAS 2000 B.2.1
# (nivel de complejidad × clima — concepto eliminado de la norma vigente).
# La ley exige usar PRIMERO datos históricos reales de consumo (SUI o del
# prestador); estos valores son el TOPE MÁXIMO permitido, no un "recomendado".
DOTACION_NETA_MAXIMA_MSNM: List[Tuple[float, float]] = [
    # (altura_minima_m_incluida, dotacion_maxima_L_hab_dia), evaluar de mayor a menor
    (2000.0, 120.0),   # > 2000 m s.n.m.
    (1000.0, 130.0),   # 1000 - 2000 m s.n.m.
    (0.0,    140.0),   # < 1000 m s.n.m.
]


def dotacion_neta_maxima(altura_msnm: float) -> float:
    """Dotación neta máxima L/hab/día según altura de la zona atendida
    (Res. 0330/2017 Art. 43, Tabla 1)."""
    if altura_msnm > 2000.0:
        return 120.0
    if altura_msnm >= 1000.0:
        return 130.0
    return 140.0

# ─── Factores de mayoración de consumo K1/K2 (Res. 0330/2017 Art. 47, Parágrafo 2) ─
# fmd (K1): factor día máximo | fmh (K2): factor hora máxima.
# Reemplaza la extinta tabla RAS 2000 B.2.3 (por nivel de complejidad).
# La ley exige calcularlos PRIMERO con registros históricos reales de
# macromedición; estos valores son el TOPE MÁXIMO permitido para diseño,
# clasificado por tamaño de población al período de diseño — no por
# nivel de complejidad.
def factores_consumo_maximos(poblacion_diseno: int) -> Tuple[float, float]:
    """(fmd, fmh) máximos según tamaño de población al período de diseño
    (Res. 0330/2017 Art. 47, Parágrafo 2)."""
    if poblacion_diseno <= 12_500:
        return 1.30, 1.60
    return 1.20, 1.50


# ─── Caudal mínimo contra incendio (Res. 0330/2017 Art. 70) ──────────────────
# Reemplaza la extinta tabla RAS B.7 (por nivel de complejidad, sin sustento
# en la norma vigente). El caudal real depende de: caudal mínimo por hidrante
# (según tamaño de población) × número de hidrantes exigidos en uso
# simultáneo (según tamaño de población y tipo de zona).
CAUDAL_POR_HIDRANTE_LS: Dict[str, float] = {
    "menor_12500":  5.0,    # Art. 70 num. 1
    "mayor_12500": 10.0,
}

# Número de hidrantes en uso simultáneo exigidos, por tramo de población y zona.
# zona: "unifamiliar" | "densa_multifamiliar_comercial_industrial"
N_HIDRANTES_SIMULTANEOS: Dict[str, Dict[str, int]] = {
    "menor_12500":            {"unifamiliar": 1, "densa_multifamiliar_comercial_industrial": 1},  # Art. 70 num. 2 — 1 hidrante, sin distinción de zona
    "entre_12500_y_60000":    {"unifamiliar": 1, "densa_multifamiliar_comercial_industrial": 3},   # Art. 70 num. 3
    "mayor_60000":            {"unifamiliar": 2, "densa_multifamiliar_comercial_industrial": 3},   # Art. 70 num. 4
}


def caudal_incendio_minimo(poblacion_diseno: int, zona: str) -> float:
    """Caudal mínimo contra incendio (L/s) = caudal por hidrante × hidrantes
    simultáneos exigidos, según tamaño de población y tipo de zona
    (Res. 0330/2017 Art. 70). No es un caudal adicional al Qmh de diseño de
    la red — se debe verificar que la red pueda entregarlo durante el
    período de diseño (Art. 70, definición de "Caudal de incendio")."""
    tramo_hidrante = "menor_12500" if poblacion_diseno < 12_500 else "mayor_12500"
    caudal_hidrante = CAUDAL_POR_HIDRANTE_LS[tramo_hidrante]

    if poblacion_diseno < 12_500:
        tramo_zona = "menor_12500"
    elif poblacion_diseno <= 60_000:
        tramo_zona = "entre_12500_y_60000"
    else:
        tramo_zona = "mayor_60000"
    n_hidrantes = N_HIDRANTES_SIMULTANEOS[tramo_zona][zona]

    return caudal_hidrante * n_hidrantes

# ─── Período de diseño (Res. 0330/2017 Art. 40) ──────────────────────────────
# Uniforme para TODOS los componentes de acueducto, alcantarillado y aseo,
# sin distinción por nivel de complejidad (a diferencia de la extinta tabla
# RAS 2000 B.1.4, que variaba entre 15 y 25 años según complejidad).
PERIODO_DISENO_ANIOS: int = 25

# ─── Tasas de crecimiento por defecto (cuando no hay dato censal) ─────────────
TASA_CRECIMIENTO_DEFAULT: Dict[str, float] = {
    "bajo":       0.025,   # 2.5% — municipios rurales dispersos
    "medio":      0.030,
    "medio_alto": 0.035,
    "alto":       0.040,
}

# ─── Coeficientes C de Hazen-Williams por material ───────────────────────────
COEF_HAZEN_WILLIAMS: Dict[str, int] = {
    "PVC":      150,
    "HDPE":     150,
    "ACERO":    120,
    "AC":       110,   # Asbesto-cemento (histórico, no se usa nuevo)
    "CONCRETO": 100,
    "HIERRO":   100,
    "GRP":      150,
}

# ─── Diámetros nominales comerciales disponibles en Colombia (mm) ─────────────
DIAMETROS_NOMINALES_MM = [
    25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160,
    200, 250, 315, 355, 400, 450, 500, 630, 710, 800, 1000
]

# ─── Límites de velocidad RAS B.6.3 ──────────────────────────────────────────
VELOCIDAD_MIN_MS = 0.45   # m/s — evitar sedimentación
VELOCIDAD_MAX_MS = 5.00   # m/s — evitar erosión (PVC/HDPE), golpe de ariete

# ─── Curvas IDF regionales Colombia ──────────────────────────────────────────
# Fórmula: I = a / (t^n + b)   donde t = tiempo de concentración en minutos, I en mm/h
# Coeficientes calibrados por región del IDEAM / estudios UNGRD
# Estructura: {region: {TR_años: {"a": float, "b": float, "n": float}}}
CURVAS_IDF: Dict[str, Dict[int, Dict[str, float]]] = {
    "caribe": {
        2:   {"a": 735,  "b": 8,  "n": 0.68},
        5:   {"a": 980,  "b": 8,  "n": 0.68},
        10:  {"a": 1180, "b": 8,  "n": 0.68},
        25:  {"a": 1450, "b": 8,  "n": 0.68},
        50:  {"a": 1680, "b": 8,  "n": 0.68},
        100: {"a": 1920, "b": 8,  "n": 0.68},
    },
    "andina_norte": {
        2:   {"a": 820,  "b": 10, "n": 0.71},
        5:   {"a": 1060, "b": 10, "n": 0.71},
        10:  {"a": 1260, "b": 10, "n": 0.71},
        25:  {"a": 1550, "b": 10, "n": 0.71},
        50:  {"a": 1790, "b": 10, "n": 0.71},
        100: {"a": 2040, "b": 10, "n": 0.71},
    },
    "andina_sur": {
        2:   {"a": 760,  "b": 9,  "n": 0.69},
        5:   {"a": 990,  "b": 9,  "n": 0.69},
        10:  {"a": 1180, "b": 9,  "n": 0.69},
        25:  {"a": 1450, "b": 9,  "n": 0.69},
        50:  {"a": 1680, "b": 9,  "n": 0.69},
        100: {"a": 1920, "b": 9,  "n": 0.69},
    },
    "pacifico": {
        # Región más lluviosa — Chocó biogeográfico
        2:   {"a": 1400, "b": 12, "n": 0.73},
        5:   {"a": 1820, "b": 12, "n": 0.73},
        10:  {"a": 2160, "b": 12, "n": 0.73},
        25:  {"a": 2650, "b": 12, "n": 0.73},
        50:  {"a": 3060, "b": 12, "n": 0.73},
        100: {"a": 3490, "b": 12, "n": 0.73},
    },
    "orinoquia": {
        2:   {"a": 680,  "b": 7,  "n": 0.66},
        5:   {"a": 890,  "b": 7,  "n": 0.66},
        10:  {"a": 1060, "b": 7,  "n": 0.66},
        25:  {"a": 1300, "b": 7,  "n": 0.66},
        50:  {"a": 1510, "b": 7,  "n": 0.66},
        100: {"a": 1720, "b": 7,  "n": 0.66},
    },
    "amazonia": {
        2:   {"a": 720,  "b": 8,  "n": 0.67},
        5:   {"a": 940,  "b": 8,  "n": 0.67},
        10:  {"a": 1120, "b": 8,  "n": 0.67},
        25:  {"a": 1370, "b": 8,  "n": 0.67},
        50:  {"a": 1590, "b": 8,  "n": 0.67},
        100: {"a": 1810, "b": 8,  "n": 0.67},
    },
}

PERIODOS_RETORNO_DISPONIBLES = [2, 5, 10, 25, 50, 100]

NOTAS_REGIONALES: Dict[str, str] = {
    "caribe":       "Régimen bimodal (abr–jun / sep–nov). Zona seca en Guajira (TR corregido +15%).",
    "andina_norte": "Cuencas Magdalena medio y bajo Cauca. Lluvias orográficas intensas.",
    "andina_sur":   "Macizo colombiano, alto Cauca y Patía. Alta variabilidad altitudinal.",
    "pacifico":     "Mayor precipitación media del mundo (Chocó). Usar valores con precaución; calibrar con IDEAM local.",
    "orinoquia":    "Régimen unimodal (may–nov). Grandes llanuras; pendientes muy bajas.",
    "amazonia":     "Régimen ecuatorial casi uniforme. Cobertura vegetal alta, infiltración elevada.",
}
