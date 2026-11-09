"""Núcleo del DAG de proyecto (#150).

Cada motor es un ``Nodo``; produce un ``Artefacto`` versionado y con hash que otros nodos consumen.
El id del artefacto depende de la versión del motor, la versión de la norma, los parámetros que el nodo
declara y los ids de los artefactos de entrada; por eso un cambio aguas arriba invalida solo a los
dependientes y una reejecución idéntica reutiliza lo almacenado.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping

__all__ = ["Nodo", "Artefacto", "Almacen", "AlmacenJSON", "Orquestador", "hash_canonico", "texto_canonico"]


def texto_canonico(obj: Any) -> str:
    """Serialización JSON canónica (claves ordenadas, sin espacios, sin NaN)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def hash_canonico(obj: Any) -> str:
    """SHA-256 de la serialización JSON canónica."""
    return hashlib.sha256(texto_canonico(obj).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Nodo:
    nombre: str
    version: str
    entradas: tuple[str, ...]          # nombres de nodos productores
    parametros: tuple[str, ...]        # claves requeridas del proyecto
    fn: Callable[[Mapping[str, Any], Mapping[str, "Artefacto"]], Any]


@dataclass(frozen=True)
class Artefacto:
    id: str
    nodo: str
    version_motor: str
    norma_version: str
    hash_entrada: str
    hash_contenido: str
    entradas: tuple[str, ...]          # ids de artefactos consumidos
    resultado: dict
    estado: str = "vigente"

    def a_dict(self) -> dict:
        return {
            "id": self.id, "nodo": self.nodo, "version_motor": self.version_motor,
            "norma_version": self.norma_version, "hash_entrada": self.hash_entrada,
            "hash_contenido": self.hash_contenido, "entradas": list(self.entradas),
            "resultado": self.resultado, "estado": self.estado,
        }

    @staticmethod
    def desde_dict(d: dict) -> "Artefacto":
        return Artefacto(d["id"], d["nodo"], d["version_motor"], d["norma_version"], d["hash_entrada"],
                         d["hash_contenido"], tuple(d["entradas"]), d["resultado"], d["estado"])


def _verificar(a: Artefacto) -> Artefacto:
    if hash_canonico(a.resultado) != a.hash_contenido:
        raise ValueError(f"El hash de contenido del artefacto {a.id[:12]} ({a.nodo}) no coincide: "
                         "el resultado almacenado fue alterado.")
    return a


class Almacen:
    """Almacén en memoria."""

    def __init__(self) -> None:
        self._datos: dict[str, Artefacto] = {}

    def obtener(self, id_: str) -> Artefacto | None:
        a = self._datos.get(id_)
        return _verificar(a) if a is not None else None

    def guardar(self, a: Artefacto) -> None:
        self._datos[a.id] = a

    def marcar_obsoleto(self, id_: str) -> None:
        a = self._datos.get(id_)
        if a is not None and a.estado != "obsoleto":
            self.guardar(replace(a, estado="obsoleto"))


class AlmacenJSON(Almacen):
    """Almacén persistente: un archivo ``<id>.json`` por artefacto, verificado por hash al leer."""

    def __init__(self, carpeta: Path | str) -> None:
        super().__init__()
        self._dir = Path(carpeta)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _ruta(self, id_: str) -> Path:
        return self._dir / f"{id_}.json"

    def obtener(self, id_: str) -> Artefacto | None:
        ruta = self._ruta(id_)
        if not ruta.exists():
            return None
        return _verificar(Artefacto.desde_dict(json.loads(ruta.read_text(encoding="utf-8"))))

    def guardar(self, a: Artefacto) -> None:
        texto = json.dumps(a.a_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self._ruta(a.id).write_text(texto, encoding="utf-8")

    def marcar_obsoleto(self, id_: str) -> None:
        a = self.obtener(id_)
        if a is not None and a.estado != "obsoleto":
            self.guardar(replace(a, estado="obsoleto"))


def _orden_topologico(nodos: Mapping[str, Nodo]) -> list[str]:
    pendientes = {n: set(nodo.entradas) for n, nodo in nodos.items()}
    orden: list[str] = []
    while pendientes:
        listos = sorted(n for n, deps in pendientes.items() if not deps)
        if not listos:
            raise ValueError(f"El grafo de motores contiene un ciclo entre: {sorted(pendientes)}.")
        for n in listos:
            orden.append(n)
            del pendientes[n]
        for deps in pendientes.values():
            deps.difference_update(listos)
    return orden


class Orquestador:
    def __init__(self, nodos: list[Nodo], norma_version: str, almacen: Almacen | None = None) -> None:
        mapa: dict[str, Nodo] = {}
        for n in nodos:
            if n.nombre in mapa:
                raise ValueError(f"Nombre de nodo duplicado: {n.nombre!r}.")
            mapa[n.nombre] = n
        for n in nodos:
            for dep in n.entradas:
                if dep not in mapa:
                    raise ValueError(f"El nodo {n.nombre!r} consume {dep!r}, que no tiene productor en el grafo.")
        self._nodos = mapa
        self._orden = _orden_topologico(mapa)
        self.norma_version = norma_version
        self.almacen = almacen if almacen is not None else Almacen()
        self._vigente: dict[str, str] = {}

    def ejecutar(self, proyecto: Mapping[str, Any]) -> dict[str, Artefacto]:
        arts: dict[str, Artefacto] = {}
        for nombre in self._orden:
            nodo = self._nodos[nombre]
            faltan = [k for k in nodo.parametros if k not in proyecto]
            if faltan:
                raise ValueError(f"Falta el parámetro {faltan[0]!r} requerido por el motor {nombre!r}; "
                                 "no se asume ningún valor por defecto.")
            params = {k: proyecto[k] for k in nodo.parametros}
            ids_in = tuple(arts[d].id for d in nodo.entradas)
            h_in = hash_canonico({"params": params, "entradas": list(ids_in)})
            id_ = hash_canonico({"nodo": nombre, "version": nodo.version, "norma": self.norma_version, "h": h_in})
            art = self.almacen.obtener(id_)
            if art is None:
                res = nodo.fn(params, {d: arts[d] for d in nodo.entradas})
                dump = res.model_dump(mode="json") if hasattr(res, "model_dump") else res
                art = Artefacto(id_, nombre, nodo.version, self.norma_version, h_in,
                                hash_canonico(dump), ids_in, dump)
                self.almacen.guardar(art)
            previo = self._vigente.get(nombre)
            if previo is not None and previo != id_:
                self.almacen.marcar_obsoleto(previo)
            self._vigente[nombre] = id_
            arts[nombre] = art
        return arts
