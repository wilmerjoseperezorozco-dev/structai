"""
Herramientas MCP de consulta multi-modelo: Claude y Gemini.
Claude para razonamiento / código. Gemini para análisis de archivos / visión.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Agregar ai-gateway al path
_GATEWAY = Path(__file__).parents[6] / "ai-gateway" / "src"
if str(_GATEWAY) not in sys.path:
    sys.path.insert(0, str(_GATEWAY))


def ask_gemini(
    consulta: str,
    modelo: str = "flash",
    contexto: str = "",
) -> dict:
    """
    Consulta a Google Gemini directamente.

    Args:
        consulta: Pregunta o instrucción.
        modelo:   'flash' (rápido) | 'pro' (más potente) | 'fast' (gemini-2.0)
        contexto: Contexto adicional a incluir en el prompt.
    """
    from providers.gemini import ask

    prompt = f"{contexto}\n\n{consulta}" if contexto else consulta
    response = ask(prompt, model=modelo)
    return {"provider": "gemini", "model": modelo, "response": response}


def ask_claude(
    consulta: str,
    modelo: str = "claude-sonnet-4-6",
    contexto: str = "",
) -> dict:
    """
    Consulta a Claude (Anthropic) directamente.

    Args:
        consulta: Pregunta o instrucción compleja.
        modelo:   ID del modelo Anthropic.
        contexto: Contexto adicional.
    """
    from providers.claude import ask

    prompt = f"{contexto}\n\n{consulta}" if contexto else consulta
    response = ask(prompt, model=modelo)
    return {"provider": "claude", "model": modelo, "response": response}


def analizar_archivo_con_gemini(
    ruta_archivo: str,
    pregunta: str = "Resume y analiza este archivo en contexto de ingeniería civil.",
) -> dict:
    """
    Sube un archivo a la File API de Gemini y lo analiza.
    Soporta PDF, Excel, Word, imágenes, HTML.

    Args:
        ruta_archivo: Ruta absoluta al archivo local.
        pregunta:     Qué quieres saber del archivo.
    """
    from providers.gemini import upload_file, ask_with_file

    path = Path(ruta_archivo)
    if not path.exists():
        return {"error": f"Archivo no encontrado: {ruta_archivo}"}

    MIME_MAP = {
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".html": "text/html",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    mime = MIME_MAP.get(path.suffix.lower())

    try:
        file_uri = upload_file(path, mime_type=mime)
        response = ask_with_file(pregunta, file_uri, model="pro")
        return {
            "archivo": path.name,
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "response": response,
        }
    except Exception as e:
        return {"error": str(e), "archivo": path.name}
