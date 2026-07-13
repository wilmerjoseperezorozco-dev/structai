"""
START ALL — Arranca el sistema completo BIM Intelligence.

Lo que hace:
  1. Verifica que Qdrant esté corriendo
  2. Crea colecciones si no existen
  3. Ejecuta sync delta inicial (archivos modificados)
  4. Arranca el file watcher (detección de cambios en tiempo real)
  5. Arranca el scheduler de sync periódico (cada 15 min)
  6. Arranca el MCP server en stdio

Uso desde Claude Code settings.json:
  "command": "python",
  "args": ["scripts/start_all.py"]

Uso manual (para probar):
  cd packages/bim-intelligence
  python scripts/start_all.py --no-mcp    # solo watcher + sync
  python scripts/start_all.py             # todo

Nota: el MCP en modo stdio es bloqueante; el watcher y scheduler
corren como hilos daemon en segundo plano.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Agregar src al path
_SRC = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(_SRC))

# Agregar ai-gateway al path
_GATEWAY = Path(__file__).parents[3] / "ai-gateway" / "src"
if _GATEWAY.exists():
    sys.path.insert(0, str(_GATEWAY))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[2] / ".env")

import typer
from rich.console import Console

console = Console()
app = typer.Typer(add_completion=False)


@app.command()
def main(
    mcp: bool = typer.Option(True, "--mcp/--no-mcp", help="Arrancar MCP server"),
    watch: bool = typer.Option(True, "--watch/--no-watch", help="File watcher"),
    sync_interval: int = typer.Option(15, "--sync-interval", help="Minutos entre sync delta"),
    initial_sync: bool = typer.Option(True, "--initial-sync/--no-initial-sync", help="Sync al arrancar"),
):
    """Sistema completo BIM Intelligence — Construdata."""
    console.rule("[bold blue]Construdata BIM Intelligence[/]")

    # 1. Verificar Qdrant
    console.print("\n[cyan]1. Verificando Qdrant...[/]")
    try:
        from qdrant.client import get_client
        from qdrant.collections import setup_collections
        client = get_client()
        setup_collections(client)
        collections = client.get_collections().collections
        console.print(f"[green]Qdrant OK — {len(collections)} colecciones[/]")
    except Exception as e:
        console.print(f"[red]Qdrant no disponible: {e}[/]")
        console.print("[yellow]Ejecuta: docker-compose up qdrant -d[/]")
        if mcp:
            raise SystemExit(1)

    # 2. Sync inicial
    if initial_sync:
        console.print("\n[cyan]2. Sincronización inicial...[/]")
        try:
            from ingest.sync import run_delta_sync, SCAN_ROOTS
            count = run_delta_sync(SCAN_ROOTS)
            console.print(f"[green]{count} archivos actualizados en Qdrant[/]")
        except Exception as e:
            console.print(f"[yellow]Sync inicial omitido: {e}[/]")

    # 3. File watcher (hilo daemon)
    if watch:
        console.print("\n[cyan]3. Iniciando file watcher...[/]")
        try:
            from watcher.file_watcher import run_watcher, WATCH_PATHS
            import threading
            watcher_thread = threading.Thread(
                target=run_watcher, daemon=True, name="file-watcher"
            )
            watcher_thread.start()
        except Exception as e:
            console.print(f"[yellow]File watcher omitido: {e}[/]")

    # 4. Scheduler (hilo daemon)
    console.print(f"\n[cyan]4. Sync scheduler cada {sync_interval} min...[/]")
    try:
        from watcher.scheduler import SyncScheduler
        scheduler = SyncScheduler(interval_minutes=sync_interval)
        scheduler.start()
    except Exception as e:
        console.print(f"[yellow]Scheduler omitido: {e}[/]")

    # 5. MCP server (bloqueante — va al final)
    if mcp:
        console.print("\n[cyan]5. Iniciando MCP server (stdio)...[/]")
        console.rule("[bold green]Sistema listo[/]")
        from mcp_server.server import main as run_mcp
        run_mcp()
    else:
        console.rule("[bold green]Watcher + Scheduler activos[/]")
        console.print("Ctrl+C para detener")
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            console.print("\n[yellow]Detenido[/]")


if __name__ == "__main__":
    app()
