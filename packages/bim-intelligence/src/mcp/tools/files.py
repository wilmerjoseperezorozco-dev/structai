"""
Herramientas MCP de gestión de archivos y proyectos.
Permiten a Claude ver la estructura real del sistema.
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Optional

from ...ingest.projects import discover_projects, SCAN_ROOTS


def listar_proyectos() -> list[dict]:
    """
    Lista todos los proyectos del workspace con tipo, tamaño y última modificación.
    Escanea: tubara/, optimizacion para negocios en el atlantico/, ~/.claude/projects/
    """
    projects = discover_projects()
    return [
        {
            "nombre": p.name,
            "tipo": p.type,
            "ultima_modificacion": p.last_modified,
            "archivos": p.file_count,
            "size_mb": p.size_mb,
            "ruta": p.path,
        }
        for p in projects
    ]


def listar_archivos(
    carpeta: str,
    extension: str = "",
    max_resultados: int = 50,
) -> list[dict]:
    """
    Lista archivos en una carpeta con metadatos básicos.

    Args:
        carpeta:        Ruta de la carpeta a explorar.
        extension:      Filtro por extensión (p.e. '.py', '.ifc', '.xlsx'). Vacío = todos.
        max_resultados: Límite de archivos retornados.
    """
    root = Path(carpeta)
    if not root.exists():
        return [{"error": f"Carpeta no encontrada: {carpeta}"}]

    results = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if extension and path.suffix.lower() != extension.lower():
            continue
        if any(part in {"node_modules", ".git", "__pycache__", ".next"} for part in path.parts):
            continue
        try:
            stat = path.stat()
            results.append({
                "nombre": path.name,
                "ruta": str(path),
                "extension": path.suffix,
                "size_kb": round(stat.st_size / 1024, 1),
                "modificado": str(path.stat().st_mtime),
            })
        except Exception:
            continue
        if len(results) >= max_resultados:
            break

    return results


def leer_archivo(ruta: str, max_chars: int = 3000) -> dict:
    """
    Lee el contenido de un archivo de texto.

    Args:
        ruta:      Ruta absoluta al archivo.
        max_chars: Máximo de caracteres a retornar (default 3000).
    """
    path = Path(ruta)
    if not path.exists():
        return {"error": f"Archivo no encontrado: {ruta}"}

    BINARY_EXTENSIONS = {".pdf", ".xlsx", ".docx", ".jpg", ".jpeg", ".png", ".mp4", ".zip"}
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return {
            "ruta": ruta,
            "tipo": "binario",
            "nota": "Usar analizar_archivo_con_gemini() para archivos binarios",
        }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        truncated = len(content) > max_chars
        return {
            "ruta": ruta,
            "contenido": content[:max_chars],
            "truncado": truncated,
            "total_chars": len(content),
        }
    except Exception as e:
        return {"error": str(e), "ruta": ruta}


def sincronizar_ahora() -> dict:
    """
    Ejecuta un ciclo de sincronización delta: re-indexa solo archivos modificados.
    Útil para actualizar Qdrant después de trabajar en el proyecto.
    """
    from ...ingest.sync import run_delta_sync

    count = run_delta_sync(SCAN_ROOTS)
    return {
        "archivos_actualizados": count,
        "estado": "ok" if count >= 0 else "error",
        "mensaje": f"{count} archivos re-indexados en Qdrant",
    }
