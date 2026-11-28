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


_keepalive = None


def _mantener_despierto() -> None:
    """Mientras corren las pruebas: un proceso hijo dentro de WSL (la distro se apaga ~16 s después de su último
    proceso, y con ella Ollama) y, en Windows, impedir la suspensión. Antes dependía de un keepalive externo de 8 h:
    al vencer, la corrida del 2026-11-13 pasó de ~5 h a 27 h esperando a Ollama (#178)."""
    global _keepalive
    import atexit
    import subprocess
    if _keepalive is None or _keepalive.poll() is not None:
        try:
            _keepalive = subprocess.Popen(["wsl.exe", "-d", os.environ.get("STRUCTAI_WSL_DISTRO", "Ubuntu"), "--",
                                           "sleep", "infinity"], stdin=subprocess.DEVNULL,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            atexit.register(lambda: _keepalive and _keepalive.poll() is None and _keepalive.terminate())
        except FileNotFoundError:          # sin WSL (Linux nativo): Ollama corre directo
            return
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)


def _esperar_ollama(url: str, segundos: int = 600) -> None:
    import time

    import httpx
    t = time.time()
    while time.time() - t < segundos:
        _mantener_despierto()
        try:
            if httpx.get(f"{url}/api/version", timeout=5).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(10)
    raise RuntimeError(f"Ollama sin respuesta en {url} tras {segundos} s")


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
    _mantener_despierto()

    def llamar_ollama(messages: list, max_tokens_groq: int = 700) -> str:
        _esperar_ollama(url)
        cuerpo = {
            "model": MODELO_LOCAL, "messages": messages, "stream": False,
            # num_ctx explícito: el valor por defecto de Ollama (2048) truncaría
            # en silencio el contexto del RAG. 16384 desde el hallazgo E3 (#172): con
            # 8192 los contextos > ~18.000 caracteres se recortaban a 4.098 tokens.
            "options": {"temperature": 0.1, "num_predict": max_tokens_groq,
                        "num_ctx": int(os.environ.get("STRUCTAI_NUM_CTX", "16384"))},
        }
        # Modelos con razonamiento (qwen3.5, por ejemplo): STRUCTAI_OLLAMA_THINK=false lo apaga para que el
        # razonamiento no se coma num_predict. Sin la variable no se envía nada y queda el comportamiento por defecto.
        pensar = os.environ.get("STRUCTAI_OLLAMA_THINK", "").strip().lower()
        if pensar in ("true", "false"):
            cuerpo["think"] = pensar == "true"
        r = httpx.post(f"{url}/api/chat", timeout=3600, json=cuerpo)
        r.raise_for_status()
        return r.json()["message"]["content"]

    rag_multi_norma._llamar_llm_con_respaldo = llamar_ollama
    config.issue_config_time_warning(
        __import__("pytest").PytestWarning(f"LLM local activo para las pruebas: {MODELO_LOCAL} ({url})"), stacklevel=2)
