"""
Ingesta de transcripts de chat Claude (.jsonl).
Lee la carpeta ~/.claude/projects/ y extrae bloques de texto indexables.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
MAX_CHUNK_CHARS = 1500


@dataclass
class ChatChunk:
    session_id: str
    date: str
    source: str
    role: str    # "user" | "assistant"
    content: str


def _extract_text(msg: dict) -> str:
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return ""


def iter_chat_chunks(projects_dir: Path | None = None) -> Iterator[ChatChunk]:
    """Itera sobre todos los .jsonl de Claude y emite chunks de texto."""
    base = projects_dir or CLAUDE_PROJECTS_DIR

    if not base.exists():
        return

    for jsonl_file in base.rglob("*.jsonl"):
        session_id = jsonl_file.stem
        date = ""

        try:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if not date and record.get("timestamp"):
                        date = record["timestamp"][:10]

                    role = record.get("type", "")
                    if role not in ("human", "assistant"):
                        continue

                    text = _extract_text(record.get("message", record))
                    if len(text) < 30:
                        continue

                    for chunk in _split_text(text, MAX_CHUNK_CHARS):
                        yield ChatChunk(
                            session_id=session_id,
                            date=date,
                            source=str(jsonl_file.relative_to(base.parent)),
                            role="user" if role == "human" else "assistant",
                            content=chunk,
                        )
        except Exception:
            continue


def _split_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        # Cortar en espacio para no partir palabras
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]
