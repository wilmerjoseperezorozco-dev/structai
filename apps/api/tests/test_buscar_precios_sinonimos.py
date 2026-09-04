"""
Regresión de la expansión de sinónimos regionales en
packages/construdata/rag_multi_norma.py (buscar_precios_apu).

Hallazgo real (2026-09-03): buscar "pañete" en apu_precios_referencia
traía 24 filas, pero "revoque" traía 3 y "friso" 1 -- mismo concepto de
obra guardado con 3 palabras distintas por proveedores/regiones
distintas. Una búsqueda por un solo término perdía las otras dos
terceras partes de los resultados reales, tanto en la capa regional
(apu_precios_referencia) como en la nacional (apu_items_nacional).
Corregido ampliando la consulta con SINONIMOS_CONSTRUCCION antes de
llamar al RPC -- como las 4 ramas de buscar_precios_apu comparten el
mismo tsquery, se benefician todas con un solo cambio en Python, sin
tocar la función SQL.

Golpea Supabase real (RPC real), no mocks -- mismo criterio que el
resto de tests de integración de este proyecto.
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

import rag_multi_norma as r  # noqa: E402


def test_expandir_sinonimos_agrega_variantes_conocidas() -> None:
    ampliada = r._expandir_sinonimos_precios("pañete")
    ampliada_norm = r._sin_tildes(ampliada.lower())
    for variante in ["revoque", "friso", "aplanado", "enlucido"]:
        assert variante in ampliada_norm, f"'{variante}' no se agregó a la consulta ampliada"


def test_expandir_sinonimos_no_toca_consulta_sin_termino_conocido() -> None:
    original = "excavacion manual en material comun"
    assert r._expandir_sinonimos_precios(original) == original


def test_buscar_pañete_encuentra_filas_guardadas_como_revoque() -> None:
    """Caso real: antes del fix, buscar 'pañete' nunca traía las filas
    de insumos/actividades guardadas literalmente como 'revoque' o
    'friso' -- son el mismo concepto de obra con nombres distintos."""
    resultados = r.buscar_precios_apu("pañete", top_k=15)
    assert resultados, "buscar_precios_apu('pañete') no devolvió nada"
    nombres = " | ".join(res.nombre.lower() for res in resultados)
    assert "revoque" in nombres, (
        "La búsqueda de 'pañete' no encontró ninguna fila con 'revoque' en el nombre -- "
        "¿volvió a perderse la expansión de sinónimos?"
    )
