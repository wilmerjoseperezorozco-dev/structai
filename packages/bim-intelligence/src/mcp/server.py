"""
MCP Server BIM — punto de entrada principal.
Expone todas las herramientas de Construdata a Claude Code.

Herramientas disponibles:
  BIM/IFC:       buscar_elementos_bim
  Normas:        buscar_norma
  Memoria:       buscar_conversaciones, buscar_codigo
  Multi-modelo:  preguntar_gemini, preguntar_claude, analizar_archivo
  Proyectos:     listar_proyectos, listar_archivos, leer_archivo, sincronizar
  Diagnóstico:   ver_errores, estado_sistema

Configurado en ~/.claude/settings.json como "construdata-bim"
"""
from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[4] / ".env")

from mcp.server.fastmcp import FastMCP

from .tools.search import (
    search_bim_elements,
    search_knowledge,
    search_conversations,
    search_codebase,
)
from .tools.multimodel import ask_gemini, ask_claude, analizar_archivo_con_gemini
from .tools.files import listar_proyectos, listar_archivos, leer_archivo, sincronizar_ahora
from .tools.diagnostics import (
    ver_errores_recientes,
    estado_sistema,
    diagnostico_rag_completo,
    extraer_elemento_ifc,
)

mcp = FastMCP(
    name="construdata-bim",
    instructions=(
        "Servidor BIM + AI para Construdata. Acceso completo a:\n"
        "• Modelos BIM/IFC (IfcOpenShell + Qdrant)\n"
        "• Normas técnicas colombianas (NSR-10, NTC, APU, RAS 2000)\n"
        "• Historial de conversaciones y código fuente indexados\n"
        "• Google Gemini (Pro/Flash) y Claude vía API directa\n"
        "• Sistema de archivos de todos los proyectos del workspace\n"
        "Todos los resultados en contexto de ingeniería civil colombiana."
    ),
)


# ── BIM / IFC ────────────────────────────────────────────────────────────────

@mcp.tool()
def buscar_elementos_bim(
    consulta: str,
    tipo_ifc: str = "",
    nivel: str = "",
    top_k: int = 10,
) -> list[dict]:
    """
    Busca elementos en el modelo BIM (IFC) por descripción semántica.

    Args:
        consulta: Descripción libre (p.e. "columnas de concreto primer piso")
        tipo_ifc: Tipo IFC: IfcColumn, IfcBeam, IfcSlab, IfcWall, IfcFoundation...
        nivel:    Piso del edificio (p.e. "Piso 1", "Sótano")
        top_k:    Número de resultados (default 10)
    """
    return search_bim_elements(
        query=consulta, ifc_type=tipo_ifc or None, storey=nivel or None, top_k=top_k
    )


# ── NORMAS ───────────────────────────────────────────────────────────────────

@mcp.tool()
def buscar_norma(
    consulta: str,
    tipo_norma: str = "",
    top_k: int = 8,
) -> list[dict]:
    """
    Busca en la base normativa: NSR-10, NTC, APU, RAS 2000.

    Args:
        consulta:   Pregunta técnica (p.e. "resistencia mínima concreto vigas sismo")
        tipo_norma: Filtro: 'NSR-10', 'NTC', 'APU', 'RAS'
        top_k:      Número de resultados
    """
    return search_knowledge(query=consulta, norm_type=tipo_norma or None, top_k=top_k)


# ── MEMORIA / HISTORIAL ──────────────────────────────────────────────────────

@mcp.tool()
def buscar_conversaciones(consulta: str, top_k: int = 6) -> list[dict]:
    """
    Busca en el historial de conversaciones Claude y decisiones de proyecto.

    Args:
        consulta: Tema, decisión o contexto buscado
        top_k:    Número de resultados
    """
    return search_conversations(query=consulta, top_k=top_k)


@mcp.tool()
def buscar_codigo(
    consulta: str,
    tipo_archivo: str = "",
    top_k: int = 8,
) -> list[dict]:
    """
    Busca en el código fuente de todos los proyectos indexados.

    Args:
        consulta:     Descripción de la funcionalidad
        tipo_archivo: Extensión: 'py', 'ts', 'tsx', 'sql'
        top_k:        Número de resultados
    """
    return search_codebase(query=consulta, file_type=tipo_archivo or None, top_k=top_k)


# ── MULTI-MODELO ─────────────────────────────────────────────────────────────

@mcp.tool()
def preguntar_gemini(
    consulta: str,
    modelo: str = "flash",
    contexto: str = "",
) -> dict:
    """
    Consulta directa a Google Gemini.
    Útil para obtener segunda opinión o aprovechar capacidades específicas de Gemini.

    Args:
        consulta: Pregunta o instrucción
        modelo:   'flash' (rápido, gratis) | 'pro' (más potente) | 'fast' (gemini-2.0)
        contexto: Contexto adicional al prompt
    """
    return ask_gemini(consulta=consulta, modelo=modelo, contexto=contexto)


@mcp.tool()
def preguntar_claude(
    consulta: str,
    modelo: str = "claude-sonnet-4-6",
    contexto: str = "",
) -> dict:
    """
    Consulta a Claude vía API (útil para sub-agentes o análisis paralelo).

    Args:
        consulta: Pregunta compleja o tarea de razonamiento
        modelo:   Modelo Anthropic (claude-sonnet-4-6, claude-haiku-4-5-20251001...)
        contexto: Contexto adicional
    """
    return ask_claude(consulta=consulta, modelo=modelo, contexto=contexto)


@mcp.tool()
def analizar_archivo(
    ruta_archivo: str,
    pregunta: str = "Resume y analiza este archivo en contexto de ingeniería civil colombiana.",
) -> dict:
    """
    Analiza un archivo local con Gemini Pro (File API).
    Soporta: PDF, Excel, Word, HTML, imágenes.
    Ideal para normas, planos, presupuestos, memorias.

    Args:
        ruta_archivo: Ruta absoluta al archivo (p.e. C:/Users/HP/Desktop/.../NSR10.pdf)
        pregunta:     Qué quieres saber del archivo
    """
    return analizar_archivo_con_gemini(ruta_archivo=ruta_archivo, pregunta=pregunta)


# ── PROYECTOS / ARCHIVOS ─────────────────────────────────────────────────────

@mcp.tool()
def listar_todos_proyectos() -> list[dict]:
    """
    Lista todos los proyectos detectados en el workspace con tipo y metadata.
    Escanea: tubara/, carpeta maestra, ~/.claude/projects/
    """
    return listar_proyectos()


@mcp.tool()
def explorar_carpeta(
    carpeta: str,
    extension: str = "",
    max_resultados: int = 50,
) -> list[dict]:
    """
    Lista archivos en una carpeta específica.

    Args:
        carpeta:        Ruta de la carpeta
        extension:      Filtro por extensión (.py, .ifc, .xlsx, .pdf...)
        max_resultados: Límite de archivos
    """
    return listar_archivos(carpeta=carpeta, extension=extension, max_resultados=max_resultados)


@mcp.tool()
def leer_archivo_proyecto(ruta: str, max_chars: int = 3000) -> dict:
    """
    Lee el contenido de un archivo de texto del proyecto.
    Para binarios (PDF, Excel) usa analizar_archivo() en su lugar.

    Args:
        ruta:      Ruta absoluta al archivo
        max_chars: Máximo de caracteres a retornar
    """
    return leer_archivo(ruta=ruta, max_chars=max_chars)


@mcp.tool()
def sincronizar_indices() -> dict:
    """
    Ejecuta sincronización delta: re-indexa solo archivos modificados desde el último sync.
    Llama a esto después de hacer cambios en el proyecto para mantener Qdrant actualizado.
    """
    return sincronizar_ahora()


# ── DIAGNÓSTICO ──────────────────────────────────────────────────────────────

@mcp.tool()
def ver_errores(max_lineas: int = 30) -> list[dict]:
    """
    Lee los últimos errores del Veedor de Fallas (WPM Logger JSON — módulo Gemini).
    Cada entrada incluye: timestamp, módulo, función, línea, mensaje y traceback.

    Args:
        max_lineas: Cuántos registros de error mostrar (default 30)
    """
    return ver_errores_recientes(max_lineas)


@mcp.tool()
def diagnostico_rag() -> dict:
    """
    Auto-diagnóstico RAG completo (módulo de Gemini integrado).

    Lee la última falla, busca contexto en Qdrant (NSR-10, código, conversaciones)
    y genera un paquete de diagnóstico con sugerencia de acción.
    Llamar después de cualquier error para contexto automático.
    """
    return diagnostico_rag_completo()


@mcp.tool()
def extraer_ifc(
    ruta_ifc: str,
    tipo_ifc: str = "IfcBeam",
) -> dict:
    """
    Extrae elementos de un modelo IFC con captura de errores estructurada.
    Si falla, el sensor WPM registra el error y diagnostico_rag() puede recuperarlo.

    Args:
        ruta_ifc:  Ruta absoluta al archivo .ifc
        tipo_ifc:  Tipo: IfcBeam, IfcColumn, IfcSlab, IfcWall, IfcFoundation...
    """
    return extraer_elemento_ifc(ruta_ifc=ruta_ifc, tipo_ifc=tipo_ifc)


@mcp.tool()
def estado_sistema_completo() -> dict:
    """
    Verifica el estado de todos los componentes:
    Qdrant (colecciones + puntos), Gemini, Claude, OpenAI.
    Retorna healthy=True si todo está operativo.
    """
    return estado_sistema()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
