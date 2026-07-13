"""
Observador de sistema de archivos con watchdog.
Detecta creación/modificación de archivos en carpetas monitoreadas
y re-indexa el archivo afectado en Qdrant automáticamente.

Uso:
    python -m bim_intelligence.watcher.file_watcher
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from rich.console import Console

console = Console()

# Carpetas que el watcher monitorea
WATCH_PATHS: list[Path] = [
    Path(r"C:\Users\HP\Desktop\optimizacion para negocios en el atlantico"),
    Path.home() / ".claude" / "projects",
]

IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe",
    ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3",
    ".zip", ".tar", ".gz", ".rar",
}

REINDEX_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".sql",
    ".md", ".txt", ".html", ".rst",
    ".json", ".jsonl", ".xlsx", ".pdf",
    ".ifc",
}


class ReindexHandler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[Path], None]) -> None:
        self._on_change = on_change
        self._pending: set[str] = set()

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def _handle(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(str(event.src_path))
        if path.suffix.lower() in IGNORED_EXTENSIONS:
            return
        if path.suffix.lower() not in REINDEX_EXTENSIONS:
            return
        # Evitar duplicados en ráfagas de eventos
        key = str(path)
        if key not in self._pending:
            self._pending.add(key)
            try:
                self._on_change(path)
            finally:
                self._pending.discard(key)


def _reindex_file(path: Path) -> None:
    """Callback: re-indexa un archivo específico en Qdrant."""
    console.print(f"[cyan]Cambio detectado:[/] {path.name}")

    try:
        if path.suffix.lower() == ".ifc":
            _reindex_ifc(path)
        elif path.suffix.lower() == ".jsonl":
            _reindex_chat(path)
        else:
            _reindex_generic(path)
    except Exception as e:
        console.print(f"[red]Error re-indexando {path.name}: {e}[/]")


def _reindex_generic(path: Path) -> None:
    from ..ingest.code import iter_code_chunks, SUPPORTED_EXTENSIONS
    from ..ingest.cowork import iter_cowork_chunks
    from ..ingest.pipeline import _upsert_batch

    suffix = path.suffix.lower()
    root = path.parent

    if suffix in {".py", ".ts", ".tsx", ".js", ".sql"}:
        # Re-indexar como código
        from ..ingest.code import CodeChunk
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            chunk = CodeChunk(
                path=str(path),
                file_type=suffix.lstrip("."),
                package=path.parent.name,
                content=text[:1200],
                start_line=0,
            )
            _upsert_batch("codebase", [(chunk.content, {
                "path": chunk.path,
                "file_type": chunk.file_type,
                "package": chunk.package,
                "content": chunk.content,
                "auto_synced": True,
            })])
        except Exception:
            pass

    elif suffix in {".md", ".txt", ".html"}:
        from ..ingest.cowork import CoworkChunk
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:1500]
            _upsert_batch("cowork", [(text, {
                "path": str(path),
                "doc_type": suffix.lstrip("."),
                "project": path.parent.name,
                "date": "",
                "content": text,
                "auto_synced": True,
            })])
        except Exception:
            pass


def _reindex_ifc(path: Path) -> None:
    from ..ifc.parser import parse_ifc
    from ..ingest.pipeline import _upsert_batch
    batch = []
    for elem in parse_ifc(path):
        batch.append((elem.text_for_embedding, {
            "global_id": elem.global_id,
            "ifc_type": elem.ifc_type,
            "name": elem.name,
            "storey": elem.storey,
            "material": elem.material,
            "centroid": elem.centroid,
            "content": elem.text_for_embedding,
        }))
        if len(batch) >= 50:
            _upsert_batch("bim_elements", batch)
            batch = []
    if batch:
        _upsert_batch("bim_elements", batch)


def _reindex_chat(path: Path) -> None:
    from ..ingest.chat import iter_chat_chunks
    from ..ingest.pipeline import _upsert_batch
    batch = []
    for chunk in iter_chat_chunks(path.parent):
        batch.append((chunk.content, {
            "session_id": chunk.session_id,
            "date": chunk.date,
            "source": chunk.source,
            "role": chunk.role,
            "content": chunk.content,
        }))
    if batch:
        _upsert_batch("conversations", batch)


def run_watcher(paths: list[Path] | None = None) -> None:
    """Inicia el observador de archivos. Bloqueante."""
    targets = paths or WATCH_PATHS
    observer = Observer()
    handler = ReindexHandler(on_change=_reindex_file)

    for path in targets:
        if path.exists():
            observer.schedule(handler, str(path), recursive=True)
            console.print(f"[green]Observando:[/] {path}")
        else:
            console.print(f"[yellow]No existe (ignorada):[/] {path}")

    observer.start()
    console.print("[bold blue]File watcher activo — Ctrl+C para detener[/]")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    run_watcher()
