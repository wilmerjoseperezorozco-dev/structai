"""
Pipeline de ingesta masiva: chat + cowork + code → Qdrant.

Uso:
    python -m bim_intelligence.ingest.pipeline --chat --code --cowork
    python -m bim_intelligence.ingest.pipeline --ifc ruta/modelo.ifc
    python -m bim_intelligence.ingest.pipeline --all --cowork-dir /ruta/carpeta
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from qdrant_client.models import PointStruct

load_dotenv()

from ..qdrant.client import get_client
from ..qdrant.collections import setup_collections
from ..qdrant.embedder import embed_texts

from .chat import iter_chat_chunks, CLAUDE_PROJECTS_DIR
from .code import iter_code_chunks
from .cowork import iter_cowork_chunks

console = Console()
app = typer.Typer(add_completion=False)

BATCH_UPSERT = 50  # puntos por batch a Qdrant


def _upsert_batch(collection: str, items: list[tuple[str, dict]]) -> None:
    """Embedea y sube un batch a Qdrant."""
    if not items:
        return

    texts = [text for text, _ in items]
    vectors = embed_texts(texts)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload=payload,
        )
        for vec, (_, payload) in zip(vectors, items)
    ]

    get_client().upsert(collection_name=collection, points=points)


@app.command()
def main(
    chat: bool = typer.Option(False, "--chat", help="Indexar transcripts Claude"),
    code: bool = typer.Option(False, "--code", help="Indexar código fuente"),
    cowork: bool = typer.Option(False, "--cowork", help="Indexar contenido cowork"),
    ifc: Optional[Path] = typer.Option(None, "--ifc", help="Archivo IFC a indexar"),
    all_sources: bool = typer.Option(False, "--all", help="Indexar todo"),
    code_dir: Path = typer.Option(
        Path(__file__).parents[5],
        "--code-dir",
        help="Raíz del código fuente",
    ),
    cowork_dir: Optional[Path] = typer.Option(
        None, "--cowork-dir", help="Carpeta contenido cowork"
    ),
    chat_dir: Optional[Path] = typer.Option(
        None, "--chat-dir", help="Carpeta proyectos Claude (default: ~/.claude/projects)"
    ),
):
    """Ingesta masiva de contenido hacia Qdrant."""
    console.print("[bold blue]Construdata BIM Intelligence — Ingesta[/]")

    client = get_client()
    setup_collections(client)
    console.print("[green]Colecciones Qdrant listas[/]")

    if all_sources or chat:
        _ingest_chat(chat_dir)

    if all_sources or code:
        _ingest_code(code_dir)

    if (all_sources or cowork) and cowork_dir:
        _ingest_cowork(cowork_dir)
    elif (all_sources or cowork) and not cowork_dir:
        console.print("[yellow]--cowork-dir no especificado, omitiendo cowork[/]")

    if ifc:
        _ingest_ifc(ifc)

    console.print("[bold green]Ingesta completada[/]")


def _ingest_chat(chat_dir: Optional[Path]) -> None:
    console.print("\n[cyan]Indexando conversaciones Claude...[/]")
    base = chat_dir or CLAUDE_PROJECTS_DIR

    batch: list[tuple[str, dict]] = []
    total = 0

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:
        task = progress.add_task("Chat", total=None)

        for chunk in iter_chat_chunks(base):
            payload = {
                "session_id": chunk.session_id,
                "date": chunk.date,
                "source": chunk.source,
                "role": chunk.role,
                "content": chunk.content,
            }
            batch.append((chunk.content, payload))

            if len(batch) >= BATCH_UPSERT:
                _upsert_batch("conversations", batch)
                total += len(batch)
                batch = []
                progress.update(task, description=f"Chat — {total} chunks")

        if batch:
            _upsert_batch("conversations", batch)
            total += len(batch)

    console.print(f"[green]Chat: {total} chunks indexados[/]")


def _ingest_code(root: Path) -> None:
    console.print("\n[cyan]Indexando código fuente...[/]")

    batch: list[tuple[str, dict]] = []
    total = 0

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:
        task = progress.add_task("Código", total=None)

        for chunk in iter_code_chunks(root):
            payload = {
                "path": chunk.path,
                "file_type": chunk.file_type,
                "package": chunk.package,
                "content": chunk.content,
            }
            batch.append((chunk.content, payload))

            if len(batch) >= BATCH_UPSERT:
                _upsert_batch("codebase", batch)
                total += len(batch)
                batch = []
                progress.update(task, description=f"Código — {total} chunks")

        if batch:
            _upsert_batch("codebase", batch)
            total += len(batch)

    console.print(f"[green]Código: {total} chunks indexados[/]")


def _ingest_cowork(cowork_dir: Path) -> None:
    console.print(f"\n[cyan]Indexando cowork desde {cowork_dir}...[/]")

    batch: list[tuple[str, dict]] = []
    total = 0

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:
        task = progress.add_task("Cowork", total=None)

        for chunk in iter_cowork_chunks(cowork_dir):
            payload = {
                "path": chunk.path,
                "doc_type": chunk.doc_type,
                "project": chunk.project,
                "date": chunk.date,
                "content": chunk.content,
            }
            batch.append((chunk.content, payload))

            if len(batch) >= BATCH_UPSERT:
                _upsert_batch("cowork", batch)
                total += len(batch)
                batch = []
                progress.update(task, description=f"Cowork — {total} chunks")

        if batch:
            _upsert_batch("cowork", batch)
            total += len(batch)

    console.print(f"[green]Cowork: {total} chunks indexados[/]")


def _ingest_ifc(ifc_path: Path) -> None:
    from ..ifc.parser import parse_ifc

    console.print(f"\n[cyan]Indexando IFC: {ifc_path.name}...[/]")

    batch: list[tuple[str, dict]] = []
    total = 0

    for elem in parse_ifc(ifc_path):
        payload = {
            "global_id": elem.global_id,
            "ifc_type": elem.ifc_type,
            "name": elem.name,
            "storey": elem.storey,
            "material": elem.material,
            "centroid": elem.centroid,
            "properties": elem.properties,
            "content": elem.text_for_embedding,
        }
        batch.append((elem.text_for_embedding, payload))

        if len(batch) >= BATCH_UPSERT:
            _upsert_batch("bim_elements", batch)
            total += len(batch)
            batch = []
            console.print(f"  {total} elementos BIM indexados...")

    if batch:
        _upsert_batch("bim_elements", batch)
        total += len(batch)

    console.print(f"[green]IFC: {total} elementos indexados[/]")


if __name__ == "__main__":
    app()
