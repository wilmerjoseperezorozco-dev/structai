"""
Guardia de tamaño de chunk — previene que vuelva a colarse un chunk gigante
en nsr10_chunks/ntc_chunks/motor_chunks.

Contexto (2026-08-09): un chunk de 57.650 caracteres (aquai, Artículo 253) y
otro de 38.301 (NSR-10 Título G, ya documentado como pendiente desde antes)
causaban 413 de Groq (límite 8.000 TPM) al combinarse con otros 3 chunks en
el contexto de una sola pregunta. Se re-trocheraron 99 chunks (motor_chunks
91 + nsr10_chunks 5 + ntc_chunks 3) con
scripts/mantenimiento/rechunk_chunks_sobredimensionados.py. Este test es
barato (solo SQL, sin embeddings ni llamadas a Groq) — se puede correr en
cada CI para detectar si una futura ingesta reintroduce el problema, sin
esperar a que un test de regresión con LLM real falle por 413.

Ejecutar: pytest apps/api/tests/test_rag_chunk_size_guard.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
load_dotenv(API_DIR / ".env")

# Umbral con margen: con top_k=4 y ~4 chars/token, 4 chunks de 6.000 chars
# caben holgado en el límite de 8.000 TPM de Groq (limit tier gratuito/dev)
# junto con la pregunta y el system prompt.
UMBRAL_CHARS = 6000

TABLAS = [
    ("motor_chunks", "contenido"),
    ("nsr10_chunks", "texto"),
    ("ntc_chunks", "contenido"),
]


def _max_len_paginado(sb, tabla: str, columna: str) -> tuple[int, str]:
    """Recorre toda la tabla en paginas de 1000 (limite de PostgREST) y
    devuelve (longitud maxima, id de la fila mas larga)."""
    max_len, max_id = 0, None
    inicio = 0
    PAGE = 1000
    while True:
        r = sb.table(tabla).select(f"id,{columna}").range(inicio, inicio + PAGE - 1).execute()
        for row in r.data:
            largo = len(row[columna] or "")
            if largo > max_len:
                max_len, max_id = largo, row["id"]
        if len(r.data) < PAGE:
            break
        inicio += PAGE
    return max_len, max_id


@pytest.mark.parametrize("tabla,columna", TABLAS)
def test_ningun_chunk_supera_el_umbral_seguro(tabla: str, columna: str) -> None:
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    max_len, max_id = _max_len_paginado(sb, tabla, columna)

    assert max_len <= UMBRAL_CHARS, (
        f"{tabla}.id={max_id} tiene {max_len} caracteres (> {UMBRAL_CHARS}). "
        f"Esto puede causar un 413 de Groq (límite de tokens por minuto) al "
        f"combinarse con otros chunks en el contexto de una pregunta. "
        f"Correr scripts/mantenimiento/rechunk_chunks_sobredimensionados.py "
        f"--tabla {tabla} para dividirlo."
    )
