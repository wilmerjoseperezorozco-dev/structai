"""
Sincronización delta: re-indexa solo archivos modificados desde el último sync.
Usa un archivo de estado (.sync_state.json) con hashes MD5.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Iterator

STATE_FILE = Path(__file__).parents[4] / ".sync_state.json"

SYNC_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".sql",
    ".md", ".txt", ".html", ".jsonl", ".json",
}
IGNORED_DIRS = {
    "node_modules", ".next", "__pycache__", ".git",
    "dist", "build", ".turbo", "venv", ".venv",
}


def _load_state() -> dict[str, str]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_state(state: dict[str, str]) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _md5(path: Path) -> str:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def iter_changed_files(roots: list[Path]) -> Iterator[Path]:
    """
    Itera sobre archivos que cambiaron desde el último sync.
    Actualiza el estado al finalizar.
    """
    state = _load_state()
    new_state = dict(state)
    changed: list[Path] = []

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in SYNC_EXTENSIONS:
                continue
            if path.stat().st_size > 500_000:
                continue

            key = str(path)
            current_hash = _md5(path)

            if state.get(key) != current_hash:
                new_state[key] = current_hash
                changed.append(path)

    for path in changed:
        yield path

    _save_state(new_state)


def run_delta_sync(roots: list[Path]) -> int:
    """Ejecuta un ciclo de sync delta. Retorna número de archivos re-indexados."""
    from ..ingest.code import iter_code_chunks
    from ..ingest.cowork import iter_cowork_chunks
    from ..ingest.pipeline import _upsert_batch

    total = 0
    code_batch: list[tuple[str, dict]] = []
    cowork_batch: list[tuple[str, dict]] = []

    for path in iter_changed_files(roots):
        suffix = path.suffix.lower()

        if suffix in {".py", ".ts", ".tsx", ".js", ".sql"}:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")[:1200]
                code_batch.append((text, {
                    "path": str(path),
                    "file_type": suffix.lstrip("."),
                    "package": path.parent.name,
                    "content": text,
                }))
            except Exception:
                pass

        elif suffix in {".md", ".txt", ".html"}:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")[:1500]
                cowork_batch.append((text, {
                    "path": str(path),
                    "doc_type": suffix.lstrip("."),
                    "project": path.parent.name,
                    "date": "",
                    "content": text,
                }))
            except Exception:
                pass

        total += 1

    if code_batch:
        _upsert_batch("codebase", code_batch)
    if cowork_batch:
        _upsert_batch("cowork", cowork_batch)

    return total
