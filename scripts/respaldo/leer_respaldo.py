"""Lectura de las tablas que salieron de Supabase por espacio (plan gratuito, 2026-11-16) y viven como respaldo JSONL.gz.

La carpeta se toma de ``STRUCTAI_RESPALDOS`` (por defecto ``C:/Users/wilme/dev/respaldos/supabase`` o ``~/structai-respaldos``).
Se usa el respaldo más reciente de la tabla y se verifica su sha256 contra el manifiesto ANTES de leer: un archivo
alterado o truncado falla en vez de entregar datos a medias. Los ``numeric`` vienen como texto decimal exacto.

    from leer_respaldo import filas
    for f in filas("invias_actividad_insumos", periodo="2026-1", provincia_codigo="0501"): ...
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Iterator

_CANDIDATAS = [Path("C:/Users/wilme/dev/respaldos/supabase"), Path.home() / "structai-respaldos"]


def carpeta() -> Path:
    if os.environ.get("STRUCTAI_RESPALDOS"):
        return Path(os.environ["STRUCTAI_RESPALDOS"])
    for c in _CANDIDATAS:
        if c.exists():
            return c
    return _CANDIDATAS[-1]


def manifiesto(tabla: str) -> tuple[dict, Path]:
    mans = sorted(carpeta().glob(f"{tabla}_*.manifiesto.json"))
    if not mans:
        raise FileNotFoundError(f"No hay respaldo de {tabla} en {carpeta()} (defina STRUCTAI_RESPALDOS)")
    man = json.loads(mans[-1].read_text(encoding="utf-8"))
    return man, mans[-1].parent / man["archivo"]


def filas(tabla: str, **igual_a) -> Iterator[dict]:
    """Filas del respaldo más reciente que cumplen todos los filtros de igualdad."""
    man, archivo = manifiesto(tabla)
    sha = hashlib.sha256(archivo.read_bytes()).hexdigest()
    if sha != man["sha256"]:
        raise ValueError(f"El respaldo {archivo.name} no coincide con su manifiesto (sha256): no se usa.")
    with gzip.open(archivo, "rt", encoding="utf-8") as gz:
        for linea in gz:
            f = json.loads(linea)
            if all(f.get(k) == v for k, v in igual_a.items()):
                yield f
