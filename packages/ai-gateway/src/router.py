"""
Router inteligente: elige el mejor modelo según la tarea.

Reglas de enrutamiento:
  - Análisis de archivos (PDF, Excel, planos) → Gemini Pro (File API)
  - Razonamiento complejo / arquitectura → Claude Sonnet
  - Consultas rápidas / chat básico → Gemini Flash
  - Embeddings → Gemini text-embedding-004 (gratis) o OpenAI (pago, mayor calidad)
"""
from __future__ import annotations

from enum import Enum
from typing import Literal


class TaskType(str, Enum):
    CHAT_BASIC = "chat_basic"
    REASONING = "reasoning"
    FILE_ANALYSIS = "file_analysis"
    CODE = "code"
    EMBEDDING = "embedding"
    VISION = "vision"


ROUTING_TABLE: dict[TaskType, dict] = {
    TaskType.CHAT_BASIC:    {"provider": "gemini", "model": "flash"},
    TaskType.REASONING:     {"provider": "claude", "model": "claude-sonnet-4-6"},
    TaskType.FILE_ANALYSIS: {"provider": "gemini", "model": "pro"},
    TaskType.CODE:          {"provider": "claude", "model": "claude-sonnet-4-6"},
    TaskType.EMBEDDING:     {"provider": "gemini", "model": "embed"},
    TaskType.VISION:        {"provider": "gemini", "model": "pro"},
}


def ask(
    prompt: str,
    task: TaskType = TaskType.CHAT_BASIC,
    system: str = "",
    context: list[dict] | None = None,
    file_uri: str | None = None,
) -> dict:
    """
    Enruta la consulta al proveedor óptimo y retorna la respuesta.

    Returns:
        {"provider": str, "model": str, "response": str}
    """
    route = ROUTING_TABLE[task]
    provider = route["provider"]
    model = route["model"]

    sys_prompt = system or (
        "Eres un asistente experto en ingeniería civil colombiana, "
        "construcción, BIM y análisis de proyectos de infraestructura."
    )

    if provider == "gemini":
        from .providers import gemini
        if file_uri and task == TaskType.FILE_ANALYSIS:
            response = gemini.ask_with_file(prompt, file_uri, model=model)
        else:
            response = gemini.ask(prompt, model=model, system=sys_prompt, context=context)

    elif provider == "claude":
        from .providers import claude
        response = claude.ask(prompt, system=sys_prompt, model=model, context=context)

    else:
        raise ValueError(f"Proveedor desconocido: {provider}")

    return {"provider": provider, "model": model, "response": response}


def embed(text: str, provider: Literal["gemini", "openai"] = "gemini") -> list[float]:
    """Genera embedding con el proveedor elegido."""
    if provider == "gemini":
        from .providers.gemini import embed_query
        return embed_query(text)
    else:
        from .providers.openai_client import embed as oai_embed
        return oai_embed(text)
