"""
Cliente OpenAI — solo embeddings (text-embedding-3-small).
Mantener como fallback/opción alternativa a Gemini embeddings.
"""
from __future__ import annotations

import os
from openai import OpenAI

_client: OpenAI | None = None


def _get() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise EnvironmentError("OPENAI_API_KEY no configurada")
        _client = OpenAI(api_key=key)
    return _client


def embed(text: str, model: str = "text-embedding-3-small") -> list[float]:
    response = _get().embeddings.create(
        input=text.replace("\n", " ")[:8000],
        model=model,
    )
    return response.data[0].embedding
