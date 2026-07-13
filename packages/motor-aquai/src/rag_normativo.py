"""
AquaAI — RAG Normativo
Busqueda semantica sobre normas vigentes usando pgvector

Flujo:
  1. LLM recibe pregunta del usuario
  2. Este modulo genera el embedding de la pregunta (OpenAI)
  3. pgvector busca las normas mas similares (solo vigentes)
  4. LLM usa los resultados como contexto para responder

El LLM NUNCA cita normas que no vengan de esta funcion.
"""

import os
import httpx
from openai import AsyncOpenAI

SUPABASE_URL     = os.getenv("SUPABASE_URL", "")
SUPABASE_SRV_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
MODELO_EMBEDDING = "text-embedding-3-small"

_HEADERS_SB = {
    "apikey":        SUPABASE_SRV_KEY,
    "Authorization": f"Bearer {SUPABASE_SRV_KEY}",
    "Content-Type":  "application/json",
}

_oai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def _embedding(texto: str) -> list[float]:
    resp = await _oai_client.embeddings.create(
        model=MODELO_EMBEDDING,
        input=texto,
        encoding_format="float",
    )
    return resp.data[0].embedding


async def buscar_normas_rag(
    pregunta: str,
    threshold: float = 0.70,
    limite: int = 5,
    tipo_norma: str | None = None,
) -> dict:
    """
    Genera el embedding de la pregunta y busca las normas mas relevantes.
    Devuelve los resultados con similitud y referencia normativa para que
    el LLM los cite correctamente en su respuesta.
    """
    if not OPENAI_API_KEY:
        return {
            "error": "OPENAI_API_KEY no configurada",
            "normas": [],
            "advertencia": "Sin API Key de OpenAI no es posible hacer busqueda semantica."
        }

    # 1. Embedding de la pregunta
    query_vector = await _embedding(pregunta)

    # 2. Busqueda semantica en pgvector (solo normas vigentes)
    payload = {
        "query_embedding":  query_vector,
        "match_threshold":  threshold,
        "match_count":      limite,
    }
    if tipo_norma:
        payload["p_tipo_norma"] = tipo_norma

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_normas_vigentes",
            headers=_HEADERS_SB,
            json=payload,
        )
    r.raise_for_status()
    resultados = r.json()

    # 3. Formatear para el LLM
    return {
        "pregunta": pregunta,
        "normas_encontradas": len(resultados),
        "threshold_usado": threshold,
        "normas": [
            {
                "referencia": f"{r['tipo_norma'].capitalize()} {r['numero']} de {r['anio']}",
                "entidad":    r.get("entidad_emisora", ""),
                "titulo":     r["titulo"],
                "resumen":    r.get("resumen", ""),
                "estado":     r["estado"],
                "url":        r.get("url_oficial", ""),
                "articulos_subsistentes": r.get("articulos_subsistentes"),
                "notas_vigencia": r.get("notas_vigencia", ""),
                "similitud":  round(r["similitud"], 4),
            }
            for r in resultados
        ],
        "instruccion_llm": (
            "Cita SOLO las normas de esta lista. "
            "Menciona siempre el estado de vigencia. "
            "Si una norma tiene articulos_subsistentes, especifica cuales articulos aplican. "
            "Nunca inventes normas adicionales."
        ),
    }
