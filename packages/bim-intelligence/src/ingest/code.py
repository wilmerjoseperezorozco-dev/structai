"""
Ingesta de código fuente → Qdrant colección 'codebase'.
Indexa .py, .ts, .tsx, .sql, .json con chunking por función/clase.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".sql", ".json", ".md"}
EXCLUDED_DIRS = {
    "node_modules", ".next", "__pycache__", ".git",
    "dist", "build", ".turbo", "venv", ".venv",
}
MAX_CHUNK_CHARS = 1200


@dataclass
class CodeChunk:
    path: str
    file_type: str
    package: str
    content: str
    start_line: int


def iter_code_chunks(root: Path) -> Iterator[CodeChunk]:
    """Recorre el árbol de directorios y emite chunks de código."""
    for file_path in root.rglob("*"):
        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue
        if any(excl in file_path.parts for excl in EXCLUDED_DIRS):
            continue
        if file_path.stat().st_size > 500_000:  # omitir archivos >500KB
            continue

        package = _infer_package(file_path, root)

        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        chunks = _split_code(text, MAX_CHUNK_CHARS)
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:
                continue
            yield CodeChunk(
                path=str(file_path.relative_to(root)),
                file_type=file_path.suffix.lstrip("."),
                package=package,
                content=chunk,
                start_line=i * 40,  # estimado
            )


def _infer_package(path: Path, root: Path) -> str:
    try:
        parts = path.relative_to(root).parts
        if len(parts) >= 3 and parts[0] in ("packages", "apps"):
            return f"{parts[0]}/{parts[1]}"
        return parts[0] if parts else "root"
    except ValueError:
        return "unknown"


def _split_code(text: str, max_chars: int) -> list[str]:
    """Divide código intentando respetar funciones/clases."""
    if len(text) <= max_chars:
        return [text]

    # Intentar dividir en bloques por líneas vacías dobles
    blocks = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current = ""

    for block in blocks:
        if len(current) + len(block) + 2 <= max_chars:
            current = (current + "\n\n" + block).strip()
        else:
            if current:
                chunks.append(current)
            if len(block) <= max_chars:
                current = block
            else:
                # bloque muy largo → dividir por líneas
                for line_chunk in _chunk_by_lines(block, max_chars):
                    chunks.append(line_chunk)
                current = ""

    if current:
        chunks.append(current)

    return chunks


def _chunk_by_lines(text: str, max_chars: int) -> list[str]:
    lines = text.splitlines()
    chunks = []
    current_lines: list[str] = []
    current_len = 0

    for line in lines:
        if current_len + len(line) + 1 > max_chars and current_lines:
            chunks.append("\n".join(current_lines))
            current_lines = []
            current_len = 0
        current_lines.append(line)
        current_len += len(line) + 1

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks
