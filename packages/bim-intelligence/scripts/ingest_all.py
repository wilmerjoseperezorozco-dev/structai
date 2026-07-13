"""
Ingesta completa: chat + código + cowork → Qdrant.
Ajustar COWORK_DIR antes de ejecutar.

    python scripts/ingest_all.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[2] / ".env")

# ── Configurar rutas aquí ─────────────────────────────────────────────────────
MONOREPO_ROOT = Path(__file__).parents[3]          # tubara/construdata/
COWORK_DIR = Path(r"C:\Users\HP\Desktop\optimizacion para negocios en el atlantico")

# ─────────────────────────────────────────────────────────────────────────────

from bim_intelligence.ingest.pipeline import (
    _ingest_chat,
    _ingest_code,
    _ingest_cowork,
)
from bim_intelligence.qdrant.client import get_client
from bim_intelligence.qdrant.collections import setup_collections
from rich.console import Console

console = Console()


if __name__ == "__main__":
    console.print("[bold blue]Ingesta masiva — Construdata BIM[/]")

    client = get_client()
    setup_collections(client)

    _ingest_chat(None)            # ~/.claude/projects/ automático
    _ingest_code(MONOREPO_ROOT)   # todo el monorepo
    _ingest_cowork(COWORK_DIR)    # carpeta maestra del proyecto

    console.print("\n[bold green]Todo indexado en Qdrant.[/]")
