"""
Regresión de packages/construdata/sgc_amenaza_sismica.py — paginación.

Hallazgo real (2026-09-03, mismo audit que encontró el bug gemelo en
pais_zonificacion.py para Perú): `_cargar_desde_supabase()` usaba
`.select("*").execute()` sin paginar contra
`sgc_amenaza_sismica_municipios`. Esa tabla tiene 1.121 municipios reales
de Colombia (confirmado con `select count(*)`), pero PostgREST trunca esa
consulta sin paginar a 1.000 filas, sin ningún error -- ~121 municipios
(~11%) del catálogo de amenaza sísmica (Aa/Av) de Colombia nunca se
cargaban en el caché en memoria. Corregido paginando con `.range()`.

Golpea Supabase real, no mocks -- mismo criterio que el resto de tests de
integración de este proyecto.
"""
from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

PACKAGES_DIR = API_DIR.parents[1] / "packages" / "construdata"
sys.path.insert(0, str(PACKAGES_DIR))

from dotenv import load_dotenv

load_dotenv(API_DIR / ".env")

import sgc_amenaza_sismica as sgc  # noqa: E402


def test_carga_mas_de_1000_municipios() -> None:
    """La tabla real tiene 1.121 municipios -- si el cache se queda en
    <=1000, `.select('*').execute()` volvió a truncarse en silencio
    (regresión del bug de paginación real encontrado 2026-09-03)."""
    cache = sgc._cargar_desde_supabase()
    total = sum(len(v) for v in cache.values())
    assert total > 1000, (
        f"Solo se cargaron {total} municipios de sgc_amenaza_sismica_municipios -- "
        "PostgREST truncó la consulta sin paginar, mismo bug de 2026-09-03."
    )
