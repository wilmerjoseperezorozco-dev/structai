"""
DEMO — Construdata BIM Intelligence
Muestra el sistema completo funcionando:
  ✓ Qdrant in-memory (sin Docker)
  ✓ Indexado de archivos reales del proyecto
  ✓ Búsqueda semántica con vectores
  ✓ WPM Veedor de Fallas (sensor Gemini)
  ✓ Diagnóstico RAG
  ✓ Auto-discovery de proyectos
  (!) Gemini / Claude: muestra estructura, requiere API keys en .env

Ejecutar:
    python scripts/demo.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# ── Bootstrap de paths ────────────────────────────────────────────────────────
_SRC = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(_SRC))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich import box

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1 — Qdrant in-memory
# ─────────────────────────────────────────────────────────────────────────────

def demo_qdrant():
    console.print(Rule("[bold cyan]PASO 1 — Qdrant In-Memory[/]"))

    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

    # In-memory: no necesita Docker
    client = QdrantClient(":memory:")
    console.print("[green]✓ Qdrant en memoria iniciado[/]")

    # Crear colecciones del sistema
    COLLECTIONS = ["bim_elements", "knowledge_base", "conversations", "codebase", "cowork"]
    for name in COLLECTIONS:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=8, distance=Distance.COSINE),  # dim 8 para demo
        )

    console.print(f"[green]✓ {len(COLLECTIONS)} colecciones creadas:[/] {', '.join(COLLECTIONS)}")
    return client


# ─────────────────────────────────────────────────────────────────────────────
# PASO 2 — Indexar datos reales del proyecto (sin embeddings reales)
# ─────────────────────────────────────────────────────────────────────────────

def demo_indexar(client):
    console.print(Rule("[bold cyan]PASO 2 — Indexando Proyectos Reales[/]"))

    import hashlib
    import uuid
    from qdrant_client.models import PointStruct

    def fake_vector(text: str) -> list[float]:
        """Vector determinista basado en hash del texto (demo sin API)."""
        h = hashlib.md5(text.encode()).digest()
        return [((b / 255.0) * 2 - 1) for b in h[:8]]

    # Leer archivos Python reales del proyecto
    root = Path(__file__).parents[3]
    py_files = [f for f in root.rglob("*.py")
                if "node_modules" not in str(f) and "__pycache__" not in str(f)][:10]

    code_points = []
    for fp in py_files:
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")[:400]
            code_points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=fake_vector(content),
                payload={
                    "path": str(fp.relative_to(root)),
                    "file_type": "py",
                    "package": fp.parent.name,
                    "content": content[:200],
                }
            ))
        except Exception:
            pass

    client.upsert(collection_name="codebase", points=code_points)
    console.print(f"[green]✓ {len(code_points)} archivos Python indexados en 'codebase'[/]")

    # Indexar normas BIM simuladas (datos reales de NSR-10 que conocemos)
    normas = [
        ("NSR-10 Título D-2.5.1",
         "Vigas de concreto reforzado: ancho mínimo 250mm, relación altura/ancho ≤ 4. "
         "Zona sísmica Intermedia (Aa=0.15g) Barranquilla. Estribos cada 100mm en zonas confinadas."),
        ("NSR-10 Título C-21.5",
         "Columnas con carga axial mayor al 10% de Ag*f'c deben cumplir cuantía 1-8%. "
         "Resistencia mínima concreto columnas: f'c=21 MPa."),
        ("APU Barranquilla — CONC-002",
         "Concreto ciclópeo 3000 PSI. Precio unitario Construdata Ed.187: $485.000/m3. "
         "Factor ciudad Barranquilla: 1.12. Incluye mano de obra, material y herramienta."),
        ("NTC 3318 — Acero Grado 60",
         "Acero de refuerzo Gr.60 (fy=420 MPa). Diámetros disponibles: #3, #4, #5, #6, #7, #8. "
         "Precio referencia Barranquilla 2026: $3.850/kg con desperdicios."),
        ("NSR-10 Título A-2.4 — Cargas sísmicas Barranquilla",
         "Barranquilla: Zona de Amenaza Sísmica Intermedia. Aa=0.15g, Av=0.15g. "
         "Grupo de uso II para edificaciones residenciales. Fa=1.2 para suelo tipo C."),
    ]

    norma_points = []
    for titulo, texto in normas:
        norma_points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=fake_vector(texto),
            payload={
                "title": titulo,
                "norm_type": "NSR-10" if "NSR" in titulo else ("NTC" if "NTC" in titulo else "APU"),
                "section": titulo.split("—")[0].strip(),
                "content": texto,
            }
        ))

    client.upsert(collection_name="knowledge_base", points=norma_points)
    console.print(f"[green]✓ {len(norma_points)} normas indexadas en 'knowledge_base'[/]")

    # Indexar elementos BIM simulados
    bim_elements = [
        ("V-01", "IfcBeam",   "Viga principal eje A",  "Piso 1", "Concreto f'c=28MPa"),
        ("C-04", "IfcColumn", "Columna 40x40 eje B-3",  "Piso 1", "Concreto f'c=35MPa"),
        ("L-02", "IfcSlab",   "Losa alivianada e=20cm", "Piso 2", "Concreto f'c=21MPa"),
        ("M-07", "IfcWall",   "Muro bloque 15cm eje C", "Piso 1", "Mampostería NTC 4026"),
        ("Z-01", "IfcFoundation", "Zapata 120x120 eje A-1", "Cimientos", "Concreto f'c=21MPa"),
    ]

    bim_points = []
    for gid, ifc_type, name, storey, material in bim_elements:
        texto = f"Tipo: {ifc_type} | Nombre: {name} | Nivel: {storey} | Material: {material}"
        bim_points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=fake_vector(texto),
            payload={
                "global_id": gid,
                "ifc_type": ifc_type,
                "name": name,
                "storey": storey,
                "material": material,
                "centroid": [1.0, 2.0, 3.5],
                "content": texto,
            }
        ))

    client.upsert(collection_name="bim_elements", points=bim_points)
    console.print(f"[green]✓ {len(bim_points)} elementos BIM indexados[/]")

    return fake_vector


# ─────────────────────────────────────────────────────────────────────────────
# PASO 3 — Búsqueda semántica
# ─────────────────────────────────────────────────────────────────────────────

def demo_busqueda(client, fake_vector):
    console.print(Rule("[bold cyan]PASO 3 — Búsqueda Semántica[/]"))

    queries = [
        ("knowledge_base", "resistencia mínima concreto vigas sismo Barranquilla"),
        ("bim_elements",   "columnas concreto primer piso"),
        ("codebase",       "parser IFC elementos estructurales"),
    ]

    for coleccion, query in queries:
        console.print(f"\n[yellow]Consulta:[/] {query!r}")
        result = client.query_points(
            collection_name=coleccion,
            query=fake_vector(query),
            limit=2,
            with_payload=True,
        )

        table = Table(box=box.SIMPLE, show_header=True)
        table.add_column("Score", style="cyan", width=6)
        table.add_column("Resultado", style="white")

        for r in result.points:
            payload = r.payload or {}
            label = (
                payload.get("title")
                or payload.get("name")
                or payload.get("path")
                or "—"
            )
            content = payload.get("content", "")[:80]
            table.add_row(
                f"{r.score:.3f}",
                f"[bold]{label}[/]\n{content}",
            )

        console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# PASO 4 — WPM Veedor de Fallas (módulo Gemini)
# ─────────────────────────────────────────────────────────────────────────────

def demo_sensor():
    console.print(Rule("[bold cyan]PASO 4 — WPM Veedor de Fallas (Gemini)[/]"))

    from observabilidad.sensor import inicializar_sensor, VeedorEventos, leer_logs_recientes

    sensor = inicializar_sensor("demo_bim", nivel=10)  # nivel DEBUG para demo

    # Simular un error que registraría el sistema real
    try:
        raise ValueError("El modelo demo.ifc no contiene elementos tipo IfcBeam.")
    except Exception:
        sensor.error("Fallo crítico al procesar IfcBeam en: demo.ifc", exc_info=True)

    console.print("[green]✓ Error capturado por el sensor[/]")

    # Registrar evento de negocio
    veedor = VeedorEventos()
    veedor.consulta_bim("IfcBeam", 0)
    veedor.consulta_gemini("gemini-1.5-flash", 150)
    console.print("[green]✓ Eventos de negocio registrados[/]")

    # Leer los logs
    logs = leer_logs_recientes(5)
    if logs:
        console.print(f"\n[cyan]Último error registrado:[/]")
        ultimo = logs[-1]
        console.print(Panel(
            f"[red]Módulo:[/] {ultimo.get('modulo')}\n"
            f"[red]Función:[/] {ultimo.get('funcion')}() línea {ultimo.get('linea')}\n"
            f"[red]Mensaje:[/] {ultimo.get('mensaje')}\n"
            f"[red]Timestamp:[/] {ultimo.get('timestamp')}",
            title="veedor_fallas.jsonl",
            border_style="red",
        ))


# ─────────────────────────────────────────────────────────────────────────────
# PASO 5 — Diagnóstico RAG
# ─────────────────────────────────────────────────────────────────────────────

def demo_diagnostico():
    console.print(Rule("[bold cyan]PASO 5 — Diagnóstico RAG (Gemini)[/]"))

    from observabilidad.diagnostico import leer_ultima_falla, _sugerir_accion

    falla = leer_ultima_falla()
    if falla:
        console.print(f"[cyan]Última falla detectada:[/] {falla.get('mensaje', '')}")
        accion = _sugerir_accion(falla.get("mensaje", ""), [])
        console.print(Panel(
            f"[yellow]Origen:[/] línea {falla.get('linea')} en {falla.get('funcion')}()\n"
            f"[yellow]Error:[/] {falla.get('mensaje')}\n"
            f"[green]Acción sugerida:[/] {accion}",
            title="Diagnóstico RAG",
            border_style="yellow",
        ))
    else:
        console.print("[green]Sin fallas registradas[/]")


# ─────────────────────────────────────────────────────────────────────────────
# PASO 6 — Auto-discovery de proyectos
# ─────────────────────────────────────────────────────────────────────────────

def demo_proyectos():
    console.print(Rule("[bold cyan]PASO 6 — Auto-Discovery de Proyectos[/]"))

    from ingest.projects import discover_projects

    proyectos = discover_projects()

    table = Table(title="Proyectos detectados en el workspace", box=box.ROUNDED)
    table.add_column("Proyecto", style="bold cyan")
    table.add_column("Tipo", style="yellow")
    table.add_column("Archivos", justify="right")
    table.add_column("Tamaño", justify="right")
    table.add_column("Modificado", style="dim")

    for p in proyectos[:12]:
        table.add_row(
            p.name,
            p.type,
            str(p.file_count),
            f"{p.size_mb} MB",
            p.last_modified,
        )

    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# PASO 7 — Tools MCP (qué ve Claude)
# ─────────────────────────────────────────────────────────────────────────────

def demo_mcp_tools():
    console.print(Rule("[bold cyan]PASO 7 — Tools MCP Disponibles para Claude[/]"))

    tools = [
        ("buscar_elementos_bim",   "BIM/IFC",     "Búsqueda semántica en modelo IFC"),
        ("buscar_norma",           "Normas",       "NSR-10, NTC, APU, RAS 2000"),
        ("buscar_conversaciones",  "Memoria",      "Historial de chats Claude"),
        ("buscar_codigo",          "Código",       "Código fuente del proyecto"),
        ("preguntar_gemini",       "Multi-modelo", "Google Gemini Flash/Pro/2.0"),
        ("preguntar_claude",       "Multi-modelo", "Anthropic Claude vía API"),
        ("analizar_archivo",       "Gemini File",  "PDFs, Excel, planos con Gemini"),
        ("listar_todos_proyectos", "Proyectos",    "Auto-discovery workspace"),
        ("explorar_carpeta",       "Archivos",     "Listar cualquier carpeta"),
        ("leer_archivo_proyecto",  "Archivos",     "Leer contenido de archivos"),
        ("sincronizar_indices",    "Sync",         "Re-indexar archivos modificados"),
        ("extraer_ifc",            "IFC+Sensor",   "Extractor con WPM Veedor (Gemini)"),
        ("diagnostico_rag",        "RAG Diagnos.", "Auto-diagnóstico con Qdrant (Gemini)"),
        ("ver_errores",            "Logs",         "Últimos errores del Veedor de Fallas"),
        ("estado_sistema_completo","Health",       "Estado Qdrant + APIs"),
    ]

    table = Table(title="15 tools MCP → disponibles en Claude Code", box=box.ROUNDED)
    table.add_column("Tool", style="bold green")
    table.add_column("Categoría", style="cyan")
    table.add_column("Función", style="white")

    for tool, cat, desc in tools:
        table.add_row(tool, cat, desc)

    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# PASO 8 — Próximos pasos
# ─────────────────────────────────────────────────────────────────────────────

def demo_proximos_pasos():
    console.print(Rule("[bold cyan]PRÓXIMOS PASOS[/]"))

    env_path = Path(__file__).parents[2] / ".env"

    console.print(Panel(
        "[bold]1. Crear archivo .env con tus API keys:[/]\n"
        f"   {env_path}\n\n"
        "[cyan]GEMINI_API_KEY=[/]AIzaSy...    ← [link=https://aistudio.google.com/app/apikey]aistudio.google.com/app/apikey[/link]\n"
        "[cyan]ANTHROPIC_API_KEY=[/]sk-ant-... ← ya la tienes en Claude Code\n"
        "[cyan]OPENAI_API_KEY=[/]sk-...        ← opcional (embeddings fallback)\n"
        "[cyan]QDRANT_URL=[/]http://localhost:6333\n\n"
        "[bold]2. Levantar Qdrant (una vez):[/]\n"
        "   [green]docker-compose up qdrant -d[/]\n"
        "   (abre Docker Desktop primero)\n\n"
        "[bold]3. Ingestar todo el workspace:[/]\n"
        "   [green]python scripts/ingest_all.py[/]\n\n"
        "[bold]4. Reiniciar Claude Code[/]\n"
        "   El MCP 'construdata-bim' se activa automáticamente\n"
        "   con 15 tools disponibles en esta conversación",
        title="[bold yellow]Para activar el sistema completo[/]",
        border_style="yellow",
    ))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.print(Panel(
        "[bold blue]Construdata BIM Intelligence — Sistema de Demostración[/]\n"
        "IfcOpenShell + MCP + Qdrant + Claude + Gemini\n"
        "Módulos Gemini: WPM Veedor de Fallas + IFC Extractor + Diagnóstico RAG",
        box=box.DOUBLE,
        border_style="blue",
    ))

    t0 = time.monotonic()

    client = demo_qdrant()
    fake_vector = demo_indexar(client)
    demo_busqueda(client, fake_vector)
    demo_sensor()
    demo_diagnostico()
    demo_proyectos()
    demo_mcp_tools()
    demo_proximos_pasos()

    elapsed = round(time.monotonic() - t0, 2)
    console.print(f"\n[bold green]Demo completada en {elapsed}s ✓[/]")
