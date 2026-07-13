"""
Esquemas de colecciones Qdrant para Construdata BIM Intelligence.

Colecciones:
  bim_elements   — Elementos IFC con embedding semántico + coordenadas
  knowledge_base — NSR-10, NTC, normas técnicas
  conversations  — Transcripts de chat (Claude .jsonl)
  codebase       — Archivos de código fuente
  cowork         — Contenido colaborativo (docs, notas)
"""
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
    TextIndexParams,
    TokenizerType,
)

VECTOR_SIZE = 1536  # text-embedding-3-small de OpenAI

COLLECTIONS: dict[str, dict] = {
    "bim_elements": {
        "description": "Elementos IFC — estructurales, arquitectónicos, MEP",
        "payload_indexes": ["ifc_type", "storey", "project_id"],
    },
    "knowledge_base": {
        "description": "Normas NSR-10, NTC, RAS 2000, APU",
        "payload_indexes": ["norm_type", "section", "title"],
    },
    "conversations": {
        "description": "Transcripts de chat Claude y conversaciones de proyecto",
        "payload_indexes": ["session_id", "date", "source"],
    },
    "codebase": {
        "description": "Archivos de código fuente indexados",
        "payload_indexes": ["file_type", "package", "path"],
    },
    "cowork": {
        "description": "Contenido colaborativo: docs, notas, decisiones",
        "payload_indexes": ["doc_type", "project", "date"],
    },
}


def setup_collections(client: QdrantClient) -> None:
    """Crea todas las colecciones si no existen."""
    existing = {c.name for c in client.get_collections().collections}

    for name, meta in COLLECTIONS.items():
        if name in existing:
            continue

        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

        for field_name in meta.get("payload_indexes", []):
            client.create_payload_index(
                collection_name=name,
                field_name=field_name,
                field_schema=TextIndexParams(
                    type="text",
                    tokenizer=TokenizerType.WORD,
                    min_token_len=2,
                    lowercase=True,
                ),
            )

        print(f"[Qdrant] Colección '{name}' creada — {meta['description']}")
