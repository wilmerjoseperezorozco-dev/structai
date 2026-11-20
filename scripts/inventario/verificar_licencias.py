"""
Guardián de licencias de dependencias (issues #217 y #219).

StructAI es un producto comercial de código cerrado: ninguna dependencia declarada puede ser AGPL/GPL "fuerte" ni
llevar a que un modelo entrenado herede esa licencia. Este script revisa, SIN instalar nada, todos los
requirements*.txt y pyproject.toml del repositorio contra una lista de paquetes vetados con su motivo.

La verificación de licencias del entorno instalado (pip-licenses) corre aparte, en el job test-api del CI.

Uso: python scripts/inventario/verificar_licencias.py      # código de salida 1 si hay un paquete vetado
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
IGNORAR = {"node_modules", ".venv", ".venv-motores", "venv", ".git", "terceros"}

# paquete (nombre normalizado PEP 503) → motivo
VETADOS = {
    "ultralytics": "AGPL-3.0; los modelos entrenados con su código también quedan en AGPL (#217). Usar RF-DETR (Apache-2.0).",
    "yolov5": "AGPL-3.0 (Ultralytics).",
    "ultralyticsplus": "Envoltorio de Ultralytics (AGPL-3.0).",
    "pymupdf": "AGPL-3.0 salvo licencia comercial de Artifex. Usar pdfplumber/pypdf.",
    "fitz": "Alias de PyMuPDF (AGPL-3.0).",
    "ghostscript": "AGPL-3.0.",
    "itext": "AGPL-3.0.",
}


def normalizar(nombre: str) -> str:
    return re.sub(r"[-_.]+", "-", nombre).lower()


def _nombre_req(linea: str) -> str | None:
    linea = linea.split("#", 1)[0].strip()
    if not linea or linea.startswith(("-", "git+", "http")):
        return None
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", linea)
    return normalizar(m.group(1)) if m else None


def archivos():
    for p in RAIZ.rglob("*"):
        if any(parte in IGNORAR for parte in p.relative_to(RAIZ).parts):
            continue
        if p.is_file() and (re.fullmatch(r"requirements.*\.txt", p.name) or p.name == "pyproject.toml"):
            yield p


def dependencias(p: Path) -> list[str]:
    if p.suffix == ".txt":
        return [n for n in map(_nombre_req, p.read_text(encoding="utf-8").splitlines()) if n]
    datos = tomllib.loads(p.read_text(encoding="utf-8"))
    proy = datos.get("project", {})
    reqs = list(proy.get("dependencies", []))
    for extra in proy.get("optional-dependencies", {}).values():
        reqs += extra
    return [n for n in map(_nombre_req, reqs) if n]


def hallazgos() -> list[tuple[str, str, str]]:
    vetados = {normalizar(k): v for k, v in VETADOS.items()}
    return [(str(p.relative_to(RAIZ)).replace("\\", "/"), d, vetados[d])
            for p in archivos() for d in dependencias(p) if d in vetados]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # consola Windows cp1252
    h = hallazgos()
    for ruta, dep, motivo in h:
        print(f"✗ {ruta}: {dep} — {motivo}")
    if not h:
        print(f"✓ Ninguna dependencia vetada ({len(VETADOS)} paquetes revisados en requirements*.txt y pyproject.toml).")
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(main())
