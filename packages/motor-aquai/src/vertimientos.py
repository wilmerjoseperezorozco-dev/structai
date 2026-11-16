"""Límites de vertimiento de aguas residuales domésticas: Resolución 0631 de 2015 (MADS), artículo 8.

Verificado el 2026-11-16 contra la compilación oficial publicada por la CRA (normas.cra.gov.co, Resolución 631 de 2015):
- La resolución aplica a vertimientos puntuales a cuerpos de agua superficiales y al alcantarillado público. **No
  distingue río, quebrada o lago**, y su artículo 1, parágrafo, excluye los vertimientos al suelo y a aguas marinas.
- Para prestadores del servicio de alcantarillado, el límite depende de la carga de DBO5 (kg/día):
  ≤ 625 y > 625–3.000: DBO5 90, SST 90, DQO 180 mg/L · > 3.000: DBO5 70, SST 70, DQO 150 mg/L. pH 6 a 9 en todos.

Solo se transcriben los números de la tabla, no el texto de la norma.
"""
from __future__ import annotations

NORMA = "Resolución 0631 de 2015 (MADS), art. 8"
CUERPOS_SUPERFICIALES = ("rio", "quebrada", "lago")

# (carga DBO5 máxima del tramo en kg/día, límites en mg/L)
_TRAMOS_PRESTADOR: tuple[tuple[float, dict[str, float]], ...] = (
    (625.0, {"DBO5": 90.0, "SST": 90.0, "DQO": 180.0}),
    (3000.0, {"DBO5": 90.0, "SST": 90.0, "DQO": 180.0}),
    (float("inf"), {"DBO5": 70.0, "SST": 70.0, "DQO": 150.0}),
)
PH_MIN, PH_MAX = 6.0, 9.0


def limites_art8(carga_dbo_kg_dia: float, cuerpo_receptor: str) -> dict[str, float]:
    """Límites máximos del art. 8 para un prestador de alcantarillado según su carga de DBO5 (sin valores supuestos)."""
    if cuerpo_receptor == "suelo":
        raise ValueError(
            f"La {NORMA.split(',')[0]} no aplica a vertimientos al suelo (art. 1, parágrafo): el permiso de "
            "vertimiento al suelo se rige por otra norma, que este motor no implementa. No se asume ningún límite."
        )
    if cuerpo_receptor not in CUERPOS_SUPERFICIALES:
        raise ValueError(f"Cuerpo receptor '{cuerpo_receptor}' no reconocido ({NORMA}). "
                         f"Valores válidos: {', '.join(CUERPOS_SUPERFICIALES)}.")
    if not carga_dbo_kg_dia > 0:
        raise ValueError(f"La carga de DBO5 debe ser positiva para elegir el tramo del {NORMA}.")
    for tope, limites in _TRAMOS_PRESTADOR:
        if carga_dbo_kg_dia <= tope:
            return dict(limites)
    raise AssertionError("tramo no encontrado")  # inalcanzable: el último tramo es infinito


def en_borde_de_tramo(carga_dbo_kg_dia: float, tolerancia: float = 0.05) -> bool:
    """True si la carga está a menos del 5 % de un cambio de tramo en el que **cambian los límites** (solo 3.000 kg/d:
    los tramos de 625 y 3.000 tienen los mismos valores)."""
    cambios = [t for (t, lim), (_, sig) in zip(_TRAMOS_PRESTADOR, _TRAMOS_PRESTADOR[1:]) if lim != sig]
    return any(abs(carga_dbo_kg_dia - t) <= tolerancia * t for t in cambios)
