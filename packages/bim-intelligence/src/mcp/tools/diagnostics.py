"""
Tools MCP de diagnóstico: logs, estado del sistema, diagnóstico RAG.
Permite a Claude auto-diagnosticar errores sin salir de la conversación.

Módulos de Gemini integrados:
  - WPM Veedor de Fallas (sensor.py) → ver_errores_recientes()
  - IFC Extractor con sensor → extraer_elemento_ifc()
  - Diagnóstico RAG → diagnostico_rag_completo()
"""
from __future__ import annotations

from ...observabilidad.sensor import leer_logs_recientes


def ver_errores_recientes(max_lineas: int = 30) -> list[dict]:
    """
    Lee los últimos errores del Veedor de Fallas (WPM Logger JSON).
    Permite a Claude ver exactamente qué falló, en qué línea y con qué traceback.

    Args:
        max_lineas: Número de entradas de log a retornar (default 30)
    """
    logs = leer_logs_recientes(max_lineas)
    if not logs:
        return [{"estado": "sin_errores", "mensaje": "No hay errores registrados"}]
    return logs


def diagnostico_rag_completo() -> dict:
    """
    Pipeline completo de auto-diagnóstico RAG (módulo de Gemini).

    Flujo:
      1. Lee la última falla del veedor_fallas.jsonl
      2. Genera embedding del mensaje de error
      3. Busca en Qdrant: knowledge_base (NSR-10/NTC) + codebase + conversations
      4. Retorna paquete consolidado con contexto normativo y sugerencia de acción

    Llama a esto cuando ocurre un error para obtener contexto automático.
    """
    from ...observabilidad.diagnostico import ejecutar_diagnostico
    return ejecutar_diagnostico()


def extraer_elemento_ifc(ruta_ifc: str, tipo_ifc: str = "IfcBeam") -> dict:
    """
    Extrae elementos de un modelo IFC con captura de errores estructurada.
    Si falla, el sensor registra el error exacto y diagnóstico_rag puede recuperarlo.

    Args:
        ruta_ifc:  Ruta absoluta al archivo .ifc
        tipo_ifc:  Tipo de elemento: IfcBeam, IfcColumn, IfcSlab, IfcWall...
    """
    import json
    from ...ifc.extractor import extraer_elemento
    result_str = extraer_elemento(ruta_ifc, tipo_ifc)
    try:
        return json.loads(result_str)
    except Exception:
        return {"estado": "error", "raw": result_str}


def estado_sistema() -> dict:
    """
    Verifica el estado de todos los componentes:
    Qdrant, Gemini, Claude, OpenAI. Retorna healthy=True/False.
    """
    estado: dict = {
        "qdrant": _check_qdrant(),
        "gemini": _check_gemini(),
        "claude": _check_claude(),
        "openai": _check_openai(),
    }
    estado["healthy"] = all(v.get("ok") for v in estado.values())
    return estado


# ── Checks internos ───────────────────────────────────────────────────────────

def _check_qdrant() -> dict:
    try:
        from ...qdrant.client import get_client
        client = get_client()
        collections = client.get_collections().collections
        counts = {}
        for c in collections:
            try:
                info = client.get_collection(c.name)
                counts[c.name] = info.points_count
            except Exception:
                counts[c.name] = "?"
        return {"ok": True, "colecciones": counts}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _check_gemini() -> dict:
    import os
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return {"ok": False, "error": "GEMINI_API_KEY no configurada"}
    return {"ok": True, "modelos": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]}


def _check_claude() -> dict:
    import os
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"ok": False, "error": "ANTHROPIC_API_KEY no configurada"}
    return {"ok": True, "modelo_default": "claude-sonnet-4-6"}


def _check_openai() -> dict:
    import os
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return {"ok": False, "error": "OPENAI_API_KEY no configurada"}
    return {"ok": True, "uso": "embeddings text-embedding-3-small"}
