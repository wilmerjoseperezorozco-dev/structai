"""Números de las tablas del Título J de la NSR-10 (solo valores y numerales, nunca el texto; #336 F0).

Transcritos del PDF oficial local con `pdftotext -table` y cotejados fila por fila. Las filas cuya extracción es ambigua
(celdas combinadas o vacías) valen None y están en VERIFICAR: el motor no clasifica con ellas hasta que Wilmer las
verifique visualmente en el PDF (docs/incendios/HOJA_VERIFICACION_TABLAS_J.md).
"""
from __future__ import annotations

FUENTE = "NSR-10 Título J (PDF oficial local, dev/descargas/nsr10)"

# --- Tabla J.3.3-1: categoría por grupo, área total construida AT (m²) y número de pisos (1, 2, 3, 4, 5, 6, ≥7)
# Cada fila: (AT_min exclusivo, AT_max exclusivo, categorías). En el límite exacto se usa la fila más exigente (HIPÓTESIS
# declarada: la tabla usa > y <, sin definir la igualdad).
J33_1: dict[str, list[tuple[float, float, tuple | None]]] = {
    "C-1": [(1500.0, float("inf"), ("III", "III", "II", "II", "II", "I", "I")),
            (0.0, 1500.0, ("III", "III", "III", "II", "II", "II", "I"))],
    "C-2": [(500.0, float("inf"), ("II", "I", "I", "I", "I", "I", "I")),
            (0.0, 500.0, None)],                                   # 5 valores para 7 columnas: VERIFICAR
    "E": [(0.0, float("inf"), ("III", "III", "III", "II", "II", "II", "I"))],
    "I-2": [(1000.0, float("inf"), ("III", "II", "II", "I", "I", "I", "I")),
            (500.0, 1000.0, ("III", "III", "II", "II", "I", "I", "I")),
            (0.0, 500.0, ("III", "III", "III", "II", "II", "II", "I"))],
    "I-3": [(1000.0, float("inf"), ("II", "II", "I", "I", "I", "I", "I")),
            (0.0, 1000.0, None)],                                  # 6 valores para 7 columnas: VERIFICAR
    "L": [(1000.0, float("inf"), ("II", "I", "I", "I", "I", "I", "I")),
          (500.0, 1000.0, ("II", "II", "I", "I", "I", "I", "I")),
          (0.0, 500.0, ("III", "III", "II", "II", "I", "I", "I"))],
    "R-3": [(5000.0, float("inf"), ("III", "II", "I", "I", "I", "I", "I")),
            (0.0, 5000.0, ("III", "II", "II", "II", "I", "I", "I"))],
}
J33_1["I-4"] = J33_1["I-2"]
for _g in ("L-1", "L-2", "L-3", "L-4", "L-5", "I-1", "I-5"):
    J33_1[_g] = J33_1["L"]
# (R-1), (R-2): por área promedio de unidad (> 140 m² / ≤ 140 m², nota 1); 4 valores para 7 columnas: VERIFICAR
J33_1_RESIDENCIAL_UNIDAD = {"mayor_140": None, "hasta_140": None}

# --- Tabla J.3.3-2: por potencial combustible Cc (MJ/m²) y pisos (1, 2, 3, 4, ≥5). Filas: (Cc_min, Cc_max, categorías)
J33_2: dict[str, list[tuple[float, float, tuple]]] = {
    "A": [(8000.0, float("inf"), ("II", "II", "I", "I", "I")),
          (4000.0, 8000.0, ("III", "II", "II", "I", "I")),
          (0.0, 4000.0, ("III", "III", "III", "II", "I"))],
    "F": [(8000.0, float("inf"), ("I", "I", "I", "I", "I")),
          (4000.0, 8000.0, ("II", "II", "I", "I", "I")),
          (2000.0, 4000.0, ("III", "II", "II", "I", "I")),
          (0.0, 2000.0, ("III", "III", "II", "II", "I"))],
    "P": [(8000.0, float("inf"), ("I", "I", "I", "I", "I")),
          (4000.0, 8000.0, ("II", "I", "I", "I", "I")),
          (0.0, 4000.0, ("III", "II", "II", "I", "I"))],
}

# --- Tabla J.3.4-3: resistencia requerida al fuego (NTC 1480 / ISO 834), horas, por categoría (I, II, III).
# None = la tabla no exige ("-"). Los "1 ½" separados en la extracción se leen como 1,5 (única lectura con 3 columnas,
# salvo "Cubiertas", donde se usa la monotonía I ≥ II ≥ III; VERIFICAR).
J34_3: dict[str, tuple] = {
    "muro_cortafuego": (3.0, 2.5, 2.0),
    "muro_cerramiento_escaleras_ascensores_ductos_evacuacion": (2.0, 2.0, 1.5),
    "muro_divisorio_entre_unidades": (2.0, 1.5, 1.0),
    "muro_interior_no_portante": (0.5, 0.25, None),
    "estructura_portante": (2.0, 1.5, 1.0),          # columnas, vigas, viguetas, losas, muros portantes, celosías
    "cubierta": (1.0, 1.0, 0.5),
    "escalera_interior_no_encerrada": (2.0, 1.5, 1.0),
}

HORAS = (1.0, 1.5, 2.0, 3.0, 4.0)

# --- Tabla J.3.5-1: dimensión mínima de columnas de concreto (mm). Notas: con dos lados paralelos ≥ 950 mm, se reduce a
# 200 mm para 2 y 3 h (nota 1) y a 250 mm para 4 h (nota 2).
J35_1 = {"siliceo": (200, 230, 250, 310, 360), "carbonato": (200, 230, 250, 300, 310), "liviano": (200, 220, 230, 270, 310)}
J35_1_LADO_REDUCCION_MM = 950.0
J35_1_REDUCIDA = {2.0: 200, 3.0: 200, 4.0: 250}

# --- Tabla J.3.5-2: espesor mínimo de muros y losas de concreto (mm)
J35_2 = {"siliceo": (90, 110, 130, 160, 180), "carbonato": (80, 100, 120, 150, 170),
         "finos_livianos": (70, 80, 100, 120, 140), "gruesos_livianos": (60, 80, 90, 110, 130)}

# --- Tabla J.3.5-3: recubrimiento mínimo de losas de concreto reforzado (mm)
J35_3 = {"restringida": {"siliceo": (20,) * 5, "carbonato": (20,) * 5, "liviano": (20,) * 5},
         "no_restringida": {"siliceo": (20, 20, 30, 30, 40), "carbonato": (20, 20, 20, 30, 30), "liviano": (20, 20, 20, 30, 30)}}

# --- Tabla J.3.5-5: recubrimiento mínimo de vigas de concreto reforzado (mm) por ancho (130, 180, ≥ 250 mm); interpolación
# lineal para anchos intermedios (nota 1). None = no permitido ("--").
J35_5_ANCHOS = (130.0, 180.0, 250.0)
J35_5 = {"restringida": ((20, 20, 20, 30, 30), (20, 20, 20, 20, 20), (20, 20, 20, 20, 20)),
         "no_restringida": ((20, 30, 30, None, None), (20, 20, 20, 40, 80), (20, 20, 20, 30, 40))}

VERIFICAR = [
    "J.3.3-1 (C-2) AT < 500: 5 valores para 7 columnas de pisos",
    "J.3.3-1 (I-3) AT < 1000: 6 valores para 7 columnas",
    "J.3.3-1 (R-1),(R-2) unidades > 140 m²: 4 valores para 7 columnas",
    "J.3.3-1 (R-1),(R-2) unidades ≤ 140 m²: 4 valores para 7 columnas",
    "J.3.4-3 Cubiertas: '1 1 ½' leído como (1; 1; ½) por monotonía",
    "J.3.3-1 igualdad en los límites de AT (la tabla usa > y <)",
]
