"""Velocidad básica de viento V por municipio (DIVIPOLA) desde la Fig. B.6.4-1 de la NSR-10, v1 (#320).

ESTADO: SIN VALIDAR. La validación ciega prerregistrada de #320 está pendiente. No se usa por defecto en el diseño (#321
fase 2 espera la validación).

Fuente: data/viento/v_municipio.csv, generado por scripts/viento/asignar_municipios.py desde la figura digitalizada
(scripts/viento/digitalizar_fig_b641.py) y la cabecera municipal del DANE. Regla:
  - V máxima a menos de 0,10° de la cabecera (conservador);
  - 'frontera' = hay otra V a menos de 0,15°, o la cara es ambigua → verificar en la figura.
Exposición y Kzt NO dependen del municipio: son datos del sitio.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ESTADO_VALIDACION = "SIN VALIDAR (validación ciega de #320 pendiente)"
RUTA = Path(__file__).resolve().parents[3] / "data" / "viento" / "v_municipio.csv"


@dataclass(frozen=True)
class VientoMunicipio:
    divipola: str
    municipio: str
    departamento: str
    v_m_s: float              # V asignada (máxima en el radio de asignación)
    v_cabecera_m_s: float
    frontera: bool
    estado: str


@lru_cache(maxsize=1)
def _tabla(ruta: str = str(RUTA)) -> dict[str, VientoMunicipio]:
    with open(ruta, encoding="utf-8") as f:
        return {r["divipola"]: VientoMunicipio(r["divipola"], r["municipio"], r["departamento"], float(r["v_asignada"]),
                                               float(r["v_cabecera"]), r["frontera"] == "True", r["estado"])
                for r in csv.DictReader(f)}


def v_basica(divipola: str) -> VientoMunicipio:
    """V de la Fig. B.6.4-1 para un municipio. KeyError si el código no existe."""
    cod = str(divipola).strip().zfill(5)
    return _tabla()[cod]
