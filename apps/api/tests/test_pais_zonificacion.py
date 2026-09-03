"""
Regresión de packages/construdata/pais_zonificacion.py.

Hallazgo real (2026-09-03, investigando el sismo M6.7/7.2 de Ayacucho del
2026-08-20): `_cargar_cache_peru()` usaba `.select("*").execute()` sin
paginar contra `peru_e030_zonificacion_distrital` (1.884 filas reales) --
PostgREST trunca en silencio esa consulta a 1.000 filas, sin lanzar error.
El distrito de Coracora (provincia de Parinacochas, Ayacucho -- el
epicentro real del sismo, según el IGP) caía fuera de esas primeras 1.000
filas y por lo tanto NUNCA se detectaba, pese a estar cargado
correctamente en Supabase desde el 2026-08-26. Corregido con
`_fetch_paginado()` (paginación real vía `.range()`).

Golpea Supabase real, no mocks -- mismo criterio que el resto de tests de
integración de este proyecto (ver test_rag_nsr10_regresion.py).
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

import pais_zonificacion as pz  # noqa: E402


def test_cache_peru_carga_mas_de_1000_filas() -> None:
    """La tabla real tiene 1.884 filas -- si el caché se queda en <=1000,
    `.select('*').execute()` volvió a truncarse en silencio (regresión del
    bug de paginación real encontrado 2026-09-03)."""
    sb = pz._get_supabase_client()
    assert sb is not None, "Supabase no configurado -- no se puede correr este test"
    filas = pz._fetch_paginado(sb, "peru_e030_zonificacion_distrital")
    assert len(filas) > 1000, (
        f"Solo se cargaron {len(filas)} filas de peru_e030_zonificacion_distrital -- "
        "PostgREST truncó la consulta sin paginar, mismo bug de 2026-09-03."
    )


def test_detecta_coracora_parinacochas_zona_3() -> None:
    """Coracora (Parinacochas, Ayacucho) es el distrito real del epicentro
    del sismo M6.7/7.2 del 2026-08-20 -- caso real que expuso el bug de
    paginación (caía fuera de las primeras 1.000 filas devueltas sin
    paginar). Debe seguir detectándose correctamente en zona sísmica 3."""
    dato = pz.detectar_distrito_peru_en_texto(
        "Segun la norma E.030 de Peru, en que zona sismica esta el distrito de Coracora?"
    )
    assert dato is not None, "No se detectó Coracora -- ¿volvió el bug de paginación?"
    assert dato["distrito"] == "Coracora"
    assert dato["provincia"] == "Parinacochas"
    assert dato["zona_sismica"] == 3


def test_formatear_dato_peru_incluye_zona() -> None:
    dato = {
        "distrito": "Coracora",
        "provincia": "Parinacochas",
        "region": "Ayacucho",
        "zona_sismica": 3,
        "ambito": None,
    }
    texto = pz.formatear_dato_peru(dato)
    assert "Coracora" in texto
    assert "Parinacochas" in texto
    assert "zona sísmica 3" in texto or "zona sismica 3" in texto.lower()
