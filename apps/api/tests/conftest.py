"""
Generador LLM local opcional para las pruebas marcadas con @pytest.mark.llm
(issues #172 y #178).

El modelo local NO va a producción: solo sirve para que estas pruebas corran
en el PC de desarrollo o en el proceso nocturno local, sin gastar la cuota de
Groq de producción ni depender del crédito de OpenAI.

Activación (solo si se define la variable; sin ella no cambia nada):
    STRUCTAI_LLM_LOCAL=qwen2.5:7b  pytest -m llm
    STRUCTAI_OLLAMA_URL=http://127.0.0.1:11434   (opcional)

Qué hace: reemplaza rag_multi_norma._llamar_llm_con_respaldo, el único punto
del código que llama a un LLM, por una llamada a Ollama con los mismos
mensajes. Enrutamiento, recuperación y prompts quedan idénticos. También
apaga el caché de respuestas, que vive en el Supabase de producción: sin
eso, ask() devolvería respuestas viejas de Groq y no se mediría el modelo
local (el mismo criterio que el CI con RAG_CACHE_DISABLED).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

MODELO_LOCAL = os.environ.get("STRUCTAI_LLM_LOCAL", "").strip()

if MODELO_LOCAL:
    os.environ["RAG_CACHE_DISABLED"] = "true"


def pytest_configure(config):
    if not MODELO_LOCAL:
        return
    import httpx
    from dotenv import load_dotenv

    api_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(api_dir))
    sys.path.insert(0, str(api_dir.parents[1] / "packages" / "construdata"))
    load_dotenv(api_dir / ".env")
    import rag_multi_norma

    url = os.environ.get("STRUCTAI_OLLAMA_URL", "http://127.0.0.1:11434")

    def llamar_ollama(messages: list, max_tokens_groq: int = 700) -> str:
        r = httpx.post(f"{url}/api/chat", timeout=3600, json={
            "model": MODELO_LOCAL, "messages": messages, "stream": False,
            # num_ctx explícito: el valor por defecto de Ollama (2048) truncaría
            # en silencio el contexto del RAG. 16384 desde el hallazgo E3 (#172): con
            # 8192 los contextos > ~18.000 caracteres se recortaban a 4.098 tokens.
            "options": {"temperature": 0.1, "num_predict": max_tokens_groq,
                        "num_ctx": int(os.environ.get("STRUCTAI_NUM_CTX", "16384"))},
        })
        r.raise_for_status()
        return r.json()["message"]["content"]

    rag_multi_norma._llamar_llm_con_respaldo = llamar_ollama
    config.issue_config_time_warning(
        __import__("pytest").PytestWarning(f"LLM local activo para las pruebas: {MODELO_LOCAL} ({url})"), stacklevel=2)
