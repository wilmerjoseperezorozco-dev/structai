"""Indexación de precios con el ICOCED del DANE (base dic-2021 = 100, mensual desde 2022-01).

Lee `data/precios_elementos/icoced_series_clave.json` (generado por `scripts/precios/indices_dane.py`).
El factor entre dos fechas es índice(hasta) / índice(desde) del grupo de insumos en el dominio geográfico elegido.
Límites declarados: el ICOCED es un índice de costos de edificaciones por grupo de insumos, no el precio de un ítem; no hay serie para la ceniza,
y no se extrapola más allá del último mes publicado (se lanza ValueError).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

RUTA_JSON = Path(__file__).resolve().parents[3] / "data" / "precios_elementos" / "icoced_series_clave.json"
DOMINIO_POR_DEFECTO = "Barranquilla AM"


@lru_cache(maxsize=4)
def _cargar(ruta: str) -> dict:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))["series"]


def periodos_disponibles(dominio: str = DOMINIO_POR_DEFECTO, insumo: str = "Acero corrugado", ruta: Path | None = None) -> tuple[str, str]:
    """(primer, último) periodo AAAA-MM de la serie."""
    s = _serie(dominio, insumo, ruta)
    return min(s), max(s)


def _serie(dominio: str, insumo: str, ruta: Path | None) -> dict[str, float]:
    series = _cargar(str(ruta or RUTA_JSON))
    try:
        return series[dominio][insumo]
    except KeyError as e:
        raise ValueError(f"sin serie ICOCED para dominio={dominio!r}, insumo={insumo!r}") from e


def factor(insumo: str, desde: str, hasta: str, dominio: str = DOMINIO_POR_DEFECTO, ruta: Path | None = None) -> float:
    """Factor multiplicativo para llevar un precio de `desde` a `hasta` (AAAA-MM). Lanza ValueError si falta algún periodo."""
    s = _serie(dominio, insumo, ruta)
    for p in (desde, hasta):
        if p not in s:
            raise ValueError(f"el ICOCED de {insumo!r} en {dominio!r} no tiene el periodo {p} (disponible {min(s)} a {max(s)})")
    return s[hasta] / s[desde]
