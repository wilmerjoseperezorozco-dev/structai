"""
Contrato de integración entre el enrutador y el contenido (issue #169).

Bug que lo motivó (2026-11-10): el dominio vulnerabilidad_vivienda era
enrutable (palabras clave + enrutador contrastivo + prompt propio), pero su
rama del chat solo buscaba en motor_chunks, que tenía 0 filas. Mientras
tanto, 426 chunks propios del dominio (AIS 2004, AIS 410-23, Build Change,
NSR-10 Título E y A.10) vivían en nsr10_chunks. Toda pregunta del dominio
terminaba en "ese corpus todavía no tiene contenido cargado". Ningún test lo
detectaba porque cada pieza, por separado, funcionaba.

Este archivo verifica la unión entre las piezas, sin llamar al LLM:
  1. Todo dominio al que se puede enrutar declara sus fuentes en FUENTES_DOMINIO.
  2. Cada fuente declarada tiene filas reales en Supabase (conteo exacto,
     nunca list_tables: ver CLAUDE.md).
  3. Una pregunta canónica de cada dominio con fuentes en nsr10_chunks
     recupera al menos un chunk propio.
  4. Ningún dominio del enrutador contrastivo queda sin fuentes.

Ejecutar: pytest apps/api/tests/test_integridad_dominios.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
load_dotenv(API_DIR / ".env")

import rag_multi_norma as r  # noqa: E402

PREGUNTA_CANONICA = {
    "vulnerabilidad_vivienda": "tengo una casa de ladrillo de dos pisos, ¿qué tan vulnerable es a un sismo?",
}


def test_todo_dominio_enrutable_declara_fuentes():
    sin_fuentes = sorted(set(r.MOTOR_LABEL) - set(r.FUENTES_DOMINIO))
    assert not sin_fuentes, f"dominios enrutables sin FUENTES_DOMINIO: {sin_fuentes}"
    vacios = sorted(d for d, f in r.FUENTES_DOMINIO.items() if not f)
    assert not vacios, f"dominios con lista de fuentes vacía: {vacios}"


def test_dominios_del_contrastivo_tienen_fuentes():
    import motor_router_contrastivo as mrc
    huerfanos = sorted(set(mrc.EJEMPLOS_POR_DOMINIO) - set(r.FUENTES_DOMINIO) - {"normativa_general"})
    assert not huerfanos, f"el contrastivo puede enrutar a dominios sin fuentes: {huerfanos}"


def _casos_fuente():
    for dominio, fuentes in r.FUENTES_DOMINIO.items():
        for tipo, valor in fuentes:
            if tipo == "nsr10_prefijos":
                for p in valor:
                    yield pytest.param(dominio, tipo, p, id=f"{dominio}-{p}")
            else:
                yield pytest.param(dominio, tipo, valor, id=f"{dominio}-{tipo}")


@pytest.mark.parametrize("dominio,tipo,valor", list(_casos_fuente()))
def test_fuente_declarada_tiene_contenido(dominio, tipo, valor):
    if tipo == "motor_chunks":
        n = r.sb.table("motor_chunks").select("id", count="exact").eq("motor", valor).limit(1).execute().count
        assert n and n > 0, f"{dominio}: motor_chunks[motor={valor}] tiene {n} filas"
    elif tipo == "nsr10_prefijos":
        n = r.sb.table("nsr10_chunks").select("id", count="exact").like("id", f"{valor}%").limit(1).execute().count
        assert n and n > 0, f"{dominio}: nsr10_chunks con prefijo {valor} tiene {n} filas"
    elif tipo == "rama_propia":
        if valor == "checklist_ais_motor_vulnerabilidad_vivienda":
            assert "15 criterios" in r._bloque_checklist_ais(), "el checklist AIS no carga desde el motor"
        else:
            assert callable(getattr(r, valor, None)), f"{dominio}: la rama propia {valor} no existe en rag_multi_norma"
    else:
        pytest.fail(f"tipo de fuente desconocido: {tipo}")


@pytest.mark.parametrize("dominio,pregunta", list(PREGUNTA_CANONICA.items()))
def test_pregunta_canonica_recupera_chunks_propios(dominio, pregunta):
    prefijos = r._prefijos_nsr10(dominio)
    assert prefijos, f"{dominio} no declara prefijos en nsr10_chunks"
    chunks = r._buscar_por_prefijos(pregunta, prefijos, top_k=r.TOP_K_DEFAULT_RAG)
    assert chunks, f"{dominio}: la pregunta canónica no recuperó ningún chunk propio"
    assert all(str(c.chunk_id).startswith(prefijos) for c in chunks)


@pytest.mark.skipif(not os.environ.get("SUPABASE_URL"), reason="requiere Supabase")
def test_vivienda_no_se_abstiene_por_corpus_vacio(monkeypatch):
    """Recorre la rama real del dominio hasta antes del LLM: si se abstuviera
    por falta de contenido, devolvería sin llamar a _generar_respuesta."""
    llamado = {}

    def falso_llm(contexto, question, system_prompt=None):
        llamado["contexto"] = contexto
        return "ok"

    monkeypatch.setattr(r, "_generar_respuesta", falso_llm)
    res = r._ask_delegado_interno(PREGUNTA_CANONICA["vulnerabilidad_vivienda"], ["vulnerabilidad_vivienda"], r.TOP_K_DEFAULT_RAG)
    assert "contexto" in llamado, f"se abstuvo: {res.get('respuesta')}"
    assert "CHECKLIST AIS 2004" in llamado["contexto"]
    assert res["chunks_usados"] > 0
