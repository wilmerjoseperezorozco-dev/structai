"""
Cliente Claude (Anthropic) con streaming y tool use.
Modelo por defecto: claude-sonnet-4-6 (mejor balance costo/calidad).
"""
from __future__ import annotations

import os
from typing import Optional

import anthropic

_client: Optional[anthropic.Anthropic] = None


def _get() -> anthropic.Anthropic:
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise EnvironmentError("ANTHROPIC_API_KEY no configurada")
        _client = anthropic.Anthropic(api_key=key)
    return _client


def ask(
    prompt: str,
    system: str = "Eres un asistente experto en ingeniería civil colombiana, BIM y construcción.",
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 2048,
    context: list[dict] | None = None,
) -> str:
    """
    Envía un prompt a Claude y retorna la respuesta como texto.

    Args:
        prompt:     Pregunta o instrucción del usuario.
        system:     Prompt de sistema.
        model:      ID del modelo Anthropic.
        max_tokens: Límite de tokens de respuesta.
        context:    Historial previo [{"role": "user"|"assistant", "content": "..."}]
    """
    messages = list(context or [])
    messages.append({"role": "user", "content": prompt})

    response = _get().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )

    return response.content[0].text


def embed(text: str) -> list[float]:
    """Embeddings via OpenAI (Anthropic no tiene API de embeddings propia)."""
    from .openai_client import embed as oai_embed
    return oai_embed(text)
