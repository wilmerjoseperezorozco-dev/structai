"""
Herramienta MCP: búsqueda semántica sobre colecciones Qdrant.
"""
from __future__ import annotations

from typing import Optional

from qdrant_client.models import Filter, FieldCondition, MatchValue

from ...qdrant.client import get_client
from ...qdrant.embedder import embed_single


def search_bim_elements(
    query: str,
    ifc_type: Optional[str] = None,
    storey: Optional[str] = None,
    top_k: int = 10,
) -> list[dict]:
    """
    Busca elementos BIM en Qdrant por similitud semántica.

    Args:
        query:    Descripción libre del elemento buscado.
        ifc_type: Filtrar por tipo IFC (p.e. 'IfcColumn').
        storey:   Filtrar por nivel/piso del edificio.
        top_k:    Número de resultados.
    """
    vector = embed_single(query)
    filters = []

    if ifc_type:
        filters.append(FieldCondition(key="ifc_type", match=MatchValue(value=ifc_type)))
    if storey:
        filters.append(FieldCondition(key="storey", match=MatchValue(value=storey)))

    qdrant_filter = Filter(must=filters) if filters else None

    results = get_client().search(
        collection_name="bim_elements",
        query_vector=vector,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "score": round(r.score, 4),
            "global_id": r.payload.get("global_id"),
            "ifc_type": r.payload.get("ifc_type"),
            "name": r.payload.get("name"),
            "storey": r.payload.get("storey"),
            "material": r.payload.get("material"),
            "centroid": r.payload.get("centroid"),
        }
        for r in results
    ]


def search_knowledge(
    query: str,
    norm_type: Optional[str] = None,
    top_k: int = 8,
) -> list[dict]:
    """
    Busca en la base de conocimiento: NSR-10, NTC, APU.

    Args:
        query:     Pregunta técnica sobre normas o especificaciones.
        norm_type: Filtrar por tipo ('NSR-10', 'NTC', 'APU', 'RAS').
        top_k:     Número de resultados.
    """
    vector = embed_single(query)
    filters = []

    if norm_type:
        filters.append(FieldCondition(key="norm_type", match=MatchValue(value=norm_type)))

    qdrant_filter = Filter(must=filters) if filters else None

    results = get_client().search(
        collection_name="knowledge_base",
        query_vector=vector,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "score": round(r.score, 4),
            "title": r.payload.get("title"),
            "norm_type": r.payload.get("norm_type"),
            "section": r.payload.get("section"),
            "content": r.payload.get("content", "")[:500],
        }
        for r in results
    ]


def search_conversations(query: str, top_k: int = 6) -> list[dict]:
    """Busca en transcripts de chat indexados."""
    vector = embed_single(query)
    results = get_client().search(
        collection_name="conversations",
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "score": round(r.score, 4),
            "date": r.payload.get("date"),
            "source": r.payload.get("source"),
            "snippet": r.payload.get("content", "")[:400],
        }
        for r in results
    ]


def search_codebase(
    query: str,
    file_type: Optional[str] = None,
    top_k: int = 8,
) -> list[dict]:
    """Busca en el código fuente indexado."""
    vector = embed_single(query)
    filters = []

    if file_type:
        filters.append(FieldCondition(key="file_type", match=MatchValue(value=file_type)))

    qdrant_filter = Filter(must=filters) if filters else None

    results = get_client().search(
        collection_name="codebase",
        query_vector=vector,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "score": round(r.score, 4),
            "path": r.payload.get("path"),
            "file_type": r.payload.get("file_type"),
            "snippet": r.payload.get("content", "")[:400],
        }
        for r in results
    ]
