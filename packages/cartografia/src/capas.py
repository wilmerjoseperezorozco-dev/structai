"""
Catálogo estándar de capas y validador (issue #211).

- `catalogo()` carga data/catalogo_capas.json (versionado: cambiar una capa = cambiar la versión).
- `aplicar_catalogo(doc)` crea las capas estándar en un DXF con color, tipo de línea y grosor.
- `mapear(nombre)` propone la capa estándar para una capa de entrada (por nombre exacto o alias regex).
- `validar_dxf(doc)` reporta las capas del dibujo: estándar, mapeables (con la propuesta) y sin mapear.

El mapeo es una PROPUESTA para revisión humana: nunca se renombran capas de un plano de entrada sin confirmación.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

RUTA_CATALOGO = Path(__file__).resolve().parents[1] / "data" / "catalogo_capas.json"
_RX_NOMBRE = re.compile(r"^[A-Z]{3,6}-[A-Z0-9]+(-[A-Z0-9]+)*$")


@dataclass(frozen=True)
class Capa:
    nombre: str
    disciplina: str
    descripcion: str
    color: int
    tipo_linea: str
    grosor_mm: float
    alias: tuple[str, ...]


@lru_cache(maxsize=1)
def catalogo() -> dict:
    datos = json.loads(RUTA_CATALOGO.read_text(encoding="utf-8"))
    capas = [Capa(**{**c, "alias": tuple(c.get("alias", ()))}) for c in datos["capas"]]
    return {"version": datos["version"], "capas": capas, "por_nombre": {c.nombre: c for c in capas},
            "sistema": set(datos.get("capas_sistema", [])), "estados": datos.get("estados", [])}


def normalizar(nombre: str) -> str:
    """Minúsculas, sin tildes, separadores → '_' (para comparar con los alias)."""
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"[\s\-\.]+", "_", s)


def nombre_valido(nombre: str) -> bool:
    return bool(_RX_NOMBRE.match(nombre))


def mapear(nombre: str) -> str | None:
    """Capa estándar propuesta para `nombre`, o None. El orden del catálogo desempata (primero gana)."""
    cat = catalogo()
    if nombre in cat["por_nombre"]:
        return nombre
    n = normalizar(nombre)
    for c in cat["capas"]:
        if any(re.search(a, n) for a in c.alias):
            return c.nombre
    return None


def _grosor_dxf(mm: float) -> int:
    """ezdxf/AutoCAD usan centésimas de mm con valores fijos; se toma el permitido más cercano."""
    permitidos = (0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211)
    v = round(mm * 100)
    return min(permitidos, key=lambda p: abs(p - v))


def aplicar_catalogo(doc, disciplinas: set[str] | None = None) -> list[str]:
    """Crea (o actualiza) las capas estándar en el documento. Devuelve los nombres creados/actualizados."""
    hechas = []
    for c in catalogo()["capas"]:
        if disciplinas and c.disciplina not in disciplinas:
            continue
        tipo = c.tipo_linea if c.tipo_linea in doc.linetypes else "CONTINUOUS"
        atr = {"color": c.color, "linetype": tipo, "lineweight": _grosor_dxf(c.grosor_mm)}
        if c.nombre in doc.layers:
            capa = doc.layers.get(c.nombre)
            for k, v in atr.items():
                capa.dxf.set(k, v)
        else:
            capa = doc.layers.add(c.nombre, **atr)
        capa.description = c.descripcion
        hechas.append(c.nombre)
    return hechas


def validar_capas(nombres) -> dict:
    """Clasifica nombres de capas: estándar / mapeables (→ propuesta) / sin mapear. Las capas de sistema se omiten."""
    cat = catalogo()
    estandar, mapeables, sin_mapear = [], {}, []
    for nombre in sorted(set(nombres)):
        if nombre in cat["sistema"] or nombre.upper() in cat["sistema"]:
            continue
        if nombre in cat["por_nombre"]:
            estandar.append(nombre)
        elif (p := mapear(nombre)) is not None:
            mapeables[nombre] = p
        else:
            sin_mapear.append(nombre)
    total = len(estandar) + len(mapeables) + len(sin_mapear)
    return {"version_catalogo": cat["version"], "total": total, "estandar": estandar, "mapeables": mapeables,
            "sin_mapear": sin_mapear,
            "cobertura": round((len(estandar) + len(mapeables)) / total, 4) if total else 1.0}


def validar_dxf(doc) -> dict:
    """Valida las capas con entidades en el espacio modelo + las declaradas en la tabla de capas."""
    usadas = {e.dxf.layer for e in doc.modelspace()}
    declaradas = {l.dxf.name for l in doc.layers}
    rep = validar_capas(usadas | declaradas)
    rep["capas_vacias"] = sorted((declaradas - usadas) - catalogo()["sistema"] - set(catalogo()["por_nombre"]))
    return rep
