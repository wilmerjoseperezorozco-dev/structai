"""
Módulo de Diagnóstico RAG — diseño de Gemini, integrado al sistema.

Flujo completo:
  1. Lee la última falla del veedor_fallas.jsonl (lectura eficiente desde el final)
  2. Usa el embedding del mensaje de error para buscar en Qdrant:
     - knowledge_base (NSR-10, NTC, APU) → contexto normativo
     - codebase → código similar que resolvió el problema antes
     - conversations → si hubo una conversación donde se discutió este error
  3. Devuelve un paquete de diagnóstico consolidado para que Claude lo resuelva

La diferencia con el módulo original de Gemini:
  - Usa embedding real (no scroll por keyword) para búsqueda semántica
  - Busca en 3 colecciones simultáneamente
  - Enriquece con contexto de conversaciones previas
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .sensor import LOG_FILE, inicializar_sensor  # type: ignore[import]

sensor = inicializar_sensor(__name__)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))


def leer_ultima_falla(ruta_logs: str = LOG_FILE) -> Optional[dict]:
    """
    Lee la última línea del JSONL de fallas de forma eficiente.
    Busca desde el final del archivo — O(1) en archivos grandes.
    Diseño original de Gemini.
    """
    path = Path(ruta_logs)
    if not path.exists() or path.stat().st_size == 0:
        return None

    with open(path, "rb") as f:
        try:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)  # archivo de una sola línea

        ultima_linea = f.readline().decode("utf-8").strip()
        if not ultima_linea:
            return None
        try:
            return json.loads(ultima_linea)
        except json.JSONDecodeError:
            return None


def consultar_contexto_solucion(
    mensaje_error: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Busca en Qdrant documentación técnica relacionada con el error.
    Usa embedding semántico real (no keyword matching).
    Busca en: knowledge_base + codebase + conversations.
    """
    try:
        from qdrant_client import QdrantClient
        from ..qdrant.embedder import embed_single

        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        vector = embed_single(mensaje_error)

        resultados: list[dict] = []

        for coleccion in ("knowledge_base", "codebase", "conversations"):
            try:
                hits = client.search(
                    collection_name=coleccion,
                    query_vector=vector,
                    limit=top_k,
                    with_payload=True,
                )
                for h in hits:
                    resultados.append({
                        "fuente": coleccion,
                        "score": round(h.score, 4),
                        "contenido": h.payload.get("content", "")[:300],
                        "titulo": h.payload.get("title") or h.payload.get("path") or "",
                    })
            except Exception:
                continue  # colección vacía o no existe aún

        # Ordenar por score descendente
        return sorted(resultados, key=lambda x: x["score"], reverse=True)[:top_k * 2]

    except Exception as e:
        sensor.error("Error de conexión o consulta con Qdrant en diagnóstico", exc_info=True)
        return []


def ejecutar_diagnostico(ruta_logs: str = LOG_FILE) -> dict:
    """
    Pipeline completo de diagnóstico RAG.
    Lee la última falla, busca contexto en Qdrant, devuelve paquete consolidado.

    Retorna un dict listo para ser consumido por Claude como tool result.
    """
    falla = leer_ultima_falla(ruta_logs)

    if not falla:
        return {"estado": "limpio", "mensaje": "No se detectaron fallas en el sistema."}

    print(f"[Diagnóstico] Analizando falla en módulo: '{falla.get('modulo', '?')}'")
    print(f"[Diagnóstico] Error: {falla.get('mensaje', '')}")

    contexto = consultar_contexto_solucion(falla.get("mensaje", ""))

    return {
        "timestamp_falla": falla.get("timestamp"),
        "origen": f"Línea {falla.get('linea')} en {falla.get('funcion')}()",
        "modulo": falla.get("modulo"),
        "nivel": falla.get("nivel"),
        "error_crudo": falla.get("mensaje"),
        "tiene_traceback": "traceback" in falla,
        "traceback_resumen": (falla.get("traceback", [""])[-1] if falla.get("traceback") else None),
        "contexto_qdrant": contexto if contexto else (
            "No se encontró documentación exacta. Requiere inferencia lógica."
        ),
        "accion_sugerida": _sugerir_accion(falla.get("mensaje", ""), contexto),
    }


def _sugerir_accion(mensaje: str, contexto: list[dict]) -> str:
    """Genera sugerencia de acción basada en el tipo de error."""
    msg_lower = mensaje.lower()

    if "ifcbeam" in msg_lower or "ifcslab" in msg_lower or "ifccolumn" in msg_lower:
        return "Verificar que el modelo IFC contiene elementos del tipo solicitado. Usar Revit/ArchiCAD para validar."
    if "qdrant" in msg_lower or "connection" in msg_lower:
        return "Verificar que Qdrant está corriendo: docker-compose up qdrant -d"
    if "openai" in msg_lower or "gemini" in msg_lower or "api_key" in msg_lower:
        return "Verificar variables de entorno en .env: OPENAI_API_KEY, GEMINI_API_KEY"
    if "embedding" in msg_lower:
        return "Error de embedding — verificar OPENAI_API_KEY o cambiar EMBEDDING_PROVIDER=gemini en .env"
    if contexto:
        return f"Revisar contexto normativo recuperado ({len(contexto)} fuentes encontradas en Qdrant)."
    return "Revisar el traceback completo en logs/veedor_fallas.jsonl"


if __name__ == "__main__":
    resultado = ejecutar_diagnostico()
    print("\nPAQUETE DE DIAGNÓSTICO:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
