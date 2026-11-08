"""Reglas de referencia internacional (issue #110): convención de norma_ref, etiqueta en contexto y regla de prompt.
No usa red ni base de datos. Ejecutar: pytest apps/api/tests/test_referencia_internacional.py -v"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
load_dotenv(API_DIR / ".env")

import referencia_internacional as ri  # noqa: E402
from rag_multi_norma import ChunkResult, _format_chunk_context  # noqa: E402


def test_construir_norma_ref_canonico():
    assert ri.construir_norma_ref("US", 1980, "USBM RI 8507") == "INT/US/1980 — USBM RI 8507"


@pytest.mark.parametrize("pais,anio,nombre", [("us", 1980, "x"), ("USA", 1980, "x"), ("US", 1800, "x"), ("US", 1980, "  ")])
def test_construir_norma_ref_rechaza_datos_invalidos(pais, anio, nombre):
    with pytest.raises(ValueError):
        ri.construir_norma_ref(pais, anio, nombre)


def test_reconoce_solo_la_convencion():
    assert ri.es_referencia_internacional("INT/PE/2016 — DS 024-2016-EM")
    assert not ri.es_referencia_internacional("Resolución 0330 de 2017")
    assert not ri.es_referencia_internacional("INT/PE/2016 DS sin guion")
    assert not ri.es_referencia_internacional(None)
    assert ri.analizar_norma_ref("INT/PE/2016 — DS 024-2016-EM")["pais"] == "PE"


def test_contexto_marca_fragmento_internacional_y_no_el_colombiano():
    ext = ChunkResult("a", "INT/US/1980 — USBM RI 8507", "criterios", "texto", 0.5)
    col = ChunkResult("b", "Resolución 0330 de 2017", "Art. 135", "texto", 0.5)
    assert ri.AVISO_CONTEXTO in _format_chunk_context(ext)
    assert ri.AVISO_CONTEXTO not in _format_chunk_context(col)


def test_regla_de_prompt_solo_si_hay_referencia_internacional():
    ctx = _format_chunk_context(ChunkResult("a", "INT/US/1980 — USBM RI 8507", "s", "t", 0.5))
    assert ri.contexto_tiene_referencia_internacional(ctx)
    assert not ri.contexto_tiene_referencia_internacional("[Resolución 0330 — Art. 135]\ntexto")
    assert "NO es exigencia" in ri.REGLA_PROMPT and "la norma colombiana consultada no" in ri.REGLA_PROMPT
