"""
AquaAI — Tablas normativas RAS 2000 embebidas como constantes
Fuente: Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico
        Resolución 0330 de 2017 (actualización) + RAS 2000 Título B

IMPORTANTE: estos valores son fijos por norma. NO se modifican con lógica de negocio.
La recalibración regional del bucle ↻ se aplica como factor externo, no tocando estas tablas.
"""

from typing import Dict, Tuple

# ─── Tabla B.2.1 — Dotación neta por nivel de complejidad y clima ─────────────
# Valores en L/habitante/día
# Estructura: {nivel_complejidad: {clima: (min, max, recomendado)}}
DOTACION_RAS: Dict[str, Dict[str, Tuple[float, float, float]]] = {
    "bajo": {
        "frio":     (90,  120, 100),
        "templado": (100, 130, 110),
        "calido":   (110, 150, 130),
    },
    "medio": {
        "frio":     (110, 140, 120),
        "templado": (120, 155, 135),
        "calido":   (130, 170, 150),
    },
    "medio_alto": {
        "frio":     (120, 160, 140),
        "templado": (135, 175, 155),
        "calido":   (150, 200, 170),
    },
    "alto": {
        "frio":     (140, 200, 160),
        "templado": (150, 225, 175),
        "calido":   (170, 250, 200),
    },
}

# ─── Factores de variación de consumo (RAS B.2.3) ────────────────────────────
# fmd: factor máximo día | fmh: factor máxima hora
FACTORES_CONSUMO: Dict[str, Dict[str, float]] = {
    "bajo":       {"fmd": 1.30, "fmh": 2.00},
    "medio":      {"fmd": 1.25, "fmh": 1.90},
    "medio_alto": {"fmd": 1.20, "fmh": 1.80},
    "alto":       {"fmd": 1.15, "fmh": 1.60},
}

# ─── Caudal contra incendio (RAS B.7) ────────────────────────────────────────
# Según nivel de complejidad, en L/s
CAUDAL_INCENDIO: Dict[str, float] = {
    "bajo":       0.0,    # No aplica (< 1000 hab)
    "medio":      4.0,    # Mínimo 4 L/s por 2 horas
    "medio_alto": 8.0,
    "alto":       16.0,
}

# ─── Períodos de diseño por nivel de complejidad (RAS B.1.4) ─────────────────
# en años
PERIODO_DISENO: Dict[str, int] = {
    "bajo":       15,
    "medio":      20,
    "medio_alto": 25,
    "alto":       25,
}

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
