"""
Embedder unificado: texto → vector float32 usando OpenAI text-embedding-3-small.
Maneja batches para ingesta masiva sin saturar la API.
"""
from __future__ import annotations

import os
import time
from typing import Sequence

import numpy as np
from openai import OpenAI

MODEL = "text-embedding-3-small"
BATCH_SIZE = 100
RATE_LIMIT_SLEEP = 0.5  # segundos entre batches


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY no configurada")
    return OpenAI(api_key=key)


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Convierte una lista de textos a vectores (maneja batches)."""
    client = _client()
    all_vectors: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        cleaned = [t.replace("\n", " ").strip() or "vacío" for t in batch]

        response = client.embeddings.create(input=cleaned, model=MODEL)
        vectors = [item.embedding for item in response.data]
        all_vectors.extend(vectors)

        if i + BATCH_SIZE < len(texts):
            time.sleep(RATE_LIMIT_SLEEP)

    return all_vectors


def embed_single(text: str) -> list[float]:
    return embed_texts([text])[0]
