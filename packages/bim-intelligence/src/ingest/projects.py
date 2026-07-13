"""
Auto-discovery de proyectos en el árbol de carpetas.
Escanea la carpeta maestra y registra qué proyectos existen,
cuándo fueron modificados por última vez, y sus tipos.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator

# Raíces a escanear (orden de prioridad)
SCAN_ROOTS: list[Path] = [
    Path(r"C:\Users\HP\Desktop\optimizacion para negocios en el atlantico\tubara"),
    Path(r"C:\Users\HP\Desktop\optimizacion para negocios en el atlantico"),
    Path.home() / ".claude" / "projects",
]

PROJECT_MARKERS = {
    "node":    {"package.json", "pnpm-workspace.yaml"},
    "python":  {"pyproject.toml", "requirements.txt", "setup.py"},
    "jupyter": {".ipynb"},
    "n8n":     {".json"},
    "ifc":     {".ifc"},
}

IGNORED_DIRS = {
    "node_modules", ".next", "__pycache__", ".git",
    "dist", "build", ".turbo", "venv", ".venv", ".cache",
}


@dataclass
class ProjectInfo:
    name: str
    path: str
    type: str          # node | python | jupyter | mixed | unknown
    last_modified: str  # ISO date
    file_count: int
    size_mb: float


def discover_projects(roots: list[Path] | None = None) -> list[ProjectInfo]:
    """Escanea raíces y retorna lista de proyectos detectados."""
    targets = roots or SCAN_ROOTS
    found: list[ProjectInfo] = []
    seen: set[str] = set()

    for root in targets:
        if not root.exists():
            continue
        for entry in root.iterdir():
            if not entry.is_dir() or entry.name in IGNORED_DIRS:
                continue
            if str(entry) in seen:
                continue
            seen.add(str(entry))
            info = _analyze_dir(entry)
            if info:
                found.append(info)

    return sorted(found, key=lambda p: p.last_modified, reverse=True)


def _analyze_dir(path: Path) -> ProjectInfo | None:
    files = list(path.rglob("*"))
    if not files:
        return None

    # Detectar tipo
    all_names: set[str] = set()
    all_extensions: set[str] = set()
    total_size = 0
    latest_mtime = 0.0

    for f in files:
        if f.is_file():
            all_names.add(f.name)
            all_extensions.add(f.suffix.lower())
            try:
                stat = f.stat()
                total_size += stat.st_size
                if stat.st_mtime > latest_mtime:
                    latest_mtime = stat.st_mtime
            except Exception:
                pass

    proj_type = _infer_type(all_names, all_extensions)
    last_mod = datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d") if latest_mtime else ""

    return ProjectInfo(
        name=path.name,
        path=str(path),
        type=proj_type,
        last_modified=last_mod,
        file_count=sum(1 for f in files if f.is_file()),
        size_mb=round(total_size / 1_048_576, 2),
    )


def _infer_type(names: set[str], extensions: set[str]) -> str:
    types: list[str] = []
    if names & {"package.json", "pnpm-workspace.yaml", "turbo.json"}:
        types.append("node")
    if names & {"pyproject.toml", "requirements.txt", "setup.py"}:
        types.append("python")
    if ".ipynb" in extensions:
        types.append("jupyter")
    if ".ifc" in extensions:
        types.append("ifc")
    if ".json" in extensions and not types:
        types.append("data")
    return "+".join(types) if types else "mixed"


def save_project_registry(output: Path) -> None:
    """Guarda un JSON con todos los proyectos descubiertos."""
    projects = discover_projects()
    output.write_text(
        json.dumps([asdict(p) for p in projects], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
