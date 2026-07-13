"""
Ingesta de contenido cowork: carpetas con docs, notas, decisiones.
Soporta .md, .txt, .html, .pdf (texto plano extraído).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".rst"}
MAX_CHUNK_CHARS = 1500


@dataclass
class CoworkChunk:
    path: str
    doc_type: str
    project: str
    date: str
    content: str


def iter_cowork_chunks(root: Path) -> Iterator[CoworkChunk]:
    """Recorre una carpeta de contenido colaborativo y emite chunks."""
    for file_path in root.rglob("*"):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if file_path.stat().st_size > 200_000:
            continue

        try:
            raw = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        text = _clean_text(raw, file_path.suffix)
        if len(text) < 50:
            continue

        project = _infer_project(file_path, root)
        date = _infer_date(file_path)

        for chunk in _split_text(text, MAX_CHUNK_CHARS):
            if len(chunk.strip()) < 30:
                continue
            yield CoworkChunk(
                path=str(file_path.relative_to(root)),
                doc_type=file_path.suffix.lstrip("."),
                project=project,
                date=date,
                content=chunk,
            )


def _clean_text(text: str, ext: str) -> str:
    if ext == ".html":
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _infer_project(path: Path, root: Path) -> str:
    try:
        parts = path.relative_to(root).parts
        return parts[0] if len(parts) > 1 else "general"
    except ValueError:
        return "unknown"


def _infer_date(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        return ""


def _split_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para[:max_chars]
    if current:
        chunks.append(current)
    return chunks
