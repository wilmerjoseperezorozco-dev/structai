"""
Cliente Google Gemini con soporte para:
- Chat (gemini-1.5-pro / gemini-1.5-flash / gemini-2.0-flash)
- Embeddings (text-embedding-004)
- Visión (multimodal con imágenes)
- Archivos (File API para PDFs, Excel, etc.)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import google.generativeai as genai

_configured = False

MODELS = {
    "pro":   "gemini-1.5-pro",
    "flash": "gemini-1.5-flash",
    "fast":  "gemini-2.0-flash-exp",  # más reciente
    "embed": "models/text-embedding-004",
}


def _configure() -> None:
    global _configured
    if _configured:
        return
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise EnvironmentError("GEMINI_API_KEY o GOOGLE_API_KEY no configurada")
    genai.configure(api_key=key)
    _configured = True


def ask(
    prompt: str,
    model: str = "flash",
    system: str = "Eres un asistente experto en ingeniería civil colombiana, BIM y construcción.",
    temperature: float = 0.3,
    context: list[dict] | None = None,
) -> str:
    """
    Envía un prompt a Gemini y retorna la respuesta.

    Args:
        prompt:      Pregunta del usuario.
        model:       'pro' | 'flash' | 'fast' (alias) o ID completo.
        system:      Instrucción de sistema.
        temperature: Creatividad (0=determinista, 1=creativo).
        context:     Historial [{"role": "user"|"model", "content": "..."}]
    """
    _configure()
    model_id = MODELS.get(model, model)

    generation_config = genai.GenerationConfig(temperature=temperature)
    gemini_model = genai.GenerativeModel(
        model_name=model_id,
        generation_config=generation_config,
        system_instruction=system,
    )

    history = []
    if context:
        for msg in context:
            role = "model" if msg["role"] == "assistant" else "user"
            history.append({"role": role, "parts": [msg["content"]]})

    chat = gemini_model.start_chat(history=history)
    response = chat.send_message(prompt)
    return response.text


def embed(text: str) -> list[float]:
    """
    Genera embedding con text-embedding-004 de Google.
    Dimensión: 768. Alternativa gratuita a OpenAI embeddings.
    """
    _configure()
    result = genai.embed_content(
        model=MODELS["embed"],
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def embed_query(text: str) -> list[float]:
    """Embedding optimizado para búsqueda (retrieval_query)."""
    _configure()
    result = genai.embed_content(
        model=MODELS["embed"],
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


def upload_file(path: Path, mime_type: str | None = None) -> str:
    """
    Sube un archivo a la File API de Gemini (PDFs, Excel, imágenes, video).
    Retorna el URI del archivo para usar en prompts multimodales.
    Límite: 2 GB por archivo, 20 GB total por proyecto.
    """
    _configure()
    uploaded = genai.upload_file(path=str(path), mime_type=mime_type)
    return uploaded.uri


def ask_with_file(
    prompt: str,
    file_uri: str,
    model: str = "pro",
) -> str:
    """Envía prompt + archivo subido a Gemini (análisis de PDFs, planos, etc.)."""
    _configure()
    model_id = MODELS.get(model, model)
    gemini_model = genai.GenerativeModel(model_name=model_id)
    file_ref = genai.get_file(file_uri)
    response = gemini_model.generate_content([prompt, file_ref])
    return response.text
