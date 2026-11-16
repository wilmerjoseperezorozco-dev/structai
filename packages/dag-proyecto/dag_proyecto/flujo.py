"""Flujo atómico (#221, fase 2) sobre el núcleo del DAG de proyecto (#150).

Un ``Flujo`` declara sus pasos, sus entradas y su versión. Garantías:

* **Caché por contenido.** Cada paso puro produce un ``Artefacto`` con id = SHA-256 de (flujo, versión del flujo, paso, versión
  del paso, versión de la norma, parámetros, ids de entrada): el mismo esquema de #150. Una ejecución idéntica reutiliza lo
  almacenado, y un cambio de norma o de motor cambia la llave (#193), así que nunca se sirve un resultado de otra versión.
* **Idempotencia.** Un paso con efectos (escribe en BD, envía correo) no se cachea por contenido: dos pedidos iguales pueden ser
  dos pedidos. Exige una ``idempotency_key``; repetir la misma llave con las mismas entradas devuelve el resultado registrado sin
  repetir el efecto, y repetirla con entradas distintas es un error (no se reinterpreta una llave).
* **Atomicidad.** Los efectos corren al final, solo si todos los pasos puros terminaron bien; un paso puro no puede depender de
  un efecto (se valida al construir). Si algo falla no queda nada a medias: `ultima_completa` (ids de la última ejecución)
  solo cambia cuando el flujo entero termina, y los artefactos ya calculados son válidos por construcción (su id es su
  contenido), así que el reintento continúa desde el último artefacto válido. Marcar artefactos como obsoletos entre versiones
  de un mismo proyecto sigue siendo del `Orquestador` (#150): una caché de la API atiende peticiones independientes.
* **Paralelismo.** Los pasos de un mismo nivel del grafo (sin dependencias entre sí) corren en hilos. Sirve para E/S
  (recuperar varias normas, consultar varios servicios); el cómputo puro en CPU no gana por el GIL.
"""
from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from . import Almacen, Artefacto, _verificar, hash_canonico

__all__ = ["Paso", "Flujo", "ResultadoFlujo", "AlmacenAcotado", "RegistroEfectos", "ConflictoIdempotencia", "huella_de_archivos"]


def huella_de_archivos(*rutas: Path | str, patron: str = "*.py") -> str:
    """SHA-256 del contenido (y la ruta relativa) de archivos y carpetas: la versión real de un motor o de unos datos de norma.

    Una carpeta aporta sus archivos `patron` (recursivo, sin `tests/` ni `__pycache__`); un archivo se aporta tal cual. Los
    finales de línea se normalizan para que la huella no cambie entre Windows y Linux. Falta una ruta: error (una huella que
    ignora una carpeta mal escrita dejaría pasar resultados de otra versión)."""
    h = hashlib.sha256()
    for r in rutas:
        r = Path(r)
        if not r.exists():
            raise FileNotFoundError(f"huella_de_archivos: no existe {r}")
        archivos = [r] if r.is_file() else sorted(x for x in r.rglob(patron)
                                                  if "__pycache__" not in x.parts and "tests" not in x.relative_to(r).parts)
        for x in archivos:
            nombre = x.relative_to(r).as_posix() if r.is_dir() else x.name
            h.update(f"{r.name}/{nombre}\0".encode("utf-8"))
            h.update(x.read_bytes().replace(b"\r\n", b"\n"))
            h.update(b"\0")
    return h.hexdigest()


class ConflictoIdempotencia(ValueError):
    """La misma idempotency_key llegó con entradas distintas."""


@dataclass(frozen=True)
class Paso:
    nombre: str
    version: str
    entradas: tuple[str, ...]                     # pasos productores
    parametros: tuple[str, ...]                   # claves requeridas de la solicitud
    fn: Callable[[Mapping[str, Any], Mapping[str, Artefacto]], Any]
    efecto: bool = False                          # True = escribe fuera del proceso: idempotencia, no caché


@dataclass
class ResultadoFlujo:
    artefactos: dict[str, Artefacto]
    reutilizados: list[str] = field(default_factory=list)     # pasos servidos desde el almacén o el registro de efectos
    ejecutados: list[str] = field(default_factory=list)       # pasos calculados en esta ejecución


class AlmacenAcotado(Almacen):
    """Almacén en memoria con tope (LRU) y seguro entre hilos: para la caché de un proceso de la API, que no debe crecer sin
    límite. Verifica el hash de contenido al leer, como todos los almacenes."""

    def __init__(self, max_artefactos: int = 256) -> None:
        super().__init__()
        self._datos: OrderedDict[str, Artefacto] = OrderedDict()
        self._max = max_artefactos
        self._lock = threading.Lock()
        self.aciertos = 0
        self.fallos = 0

    def obtener(self, id_: str) -> Artefacto | None:
        with self._lock:
            a = self._datos.get(id_)
            if a is None:
                self.fallos += 1
                return None
            self._datos.move_to_end(id_)
            self.aciertos += 1
        return _verificar(a)

    def guardar(self, a: Artefacto) -> None:
        with self._lock:
            self._datos[a.id] = a
            self._datos.move_to_end(a.id)
            while len(self._datos) > self._max:
                self._datos.popitem(last=False)

    def __len__(self) -> int:
        return len(self._datos)


class RegistroEfectos:
    """idempotency_key → artefacto del efecto ya hecho. En memoria; en producción debe ser durable y compartido (tabla con
    restricción única sobre la llave), decisión aparte que depende de #193."""

    def __init__(self) -> None:
        self._datos: dict[str, Artefacto] = {}
        self._lock = threading.Lock()

    def obtener(self, llave: str) -> Artefacto | None:
        with self._lock:
            return self._datos.get(llave)

    def registrar(self, llave: str, a: Artefacto, flujo: str = "") -> Artefacto:
        """Registra si no existe; si otro hilo ya lo hizo, devuelve el existente (gana el primero)."""
        with self._lock:
            return self._datos.setdefault(llave, a)


def _niveles(pasos: Mapping[str, Paso]) -> list[list[str]]:
    pendientes = {n: set(p.entradas) for n, p in pasos.items()}
    niveles: list[list[str]] = []
    while pendientes:
        listos = sorted(n for n, deps in pendientes.items() if not deps)
        if not listos:
            raise ValueError(f"El flujo contiene un ciclo entre: {sorted(pendientes)}.")
        niveles.append(listos)
        for n in listos:
            del pendientes[n]
        for deps in pendientes.values():
            deps.difference_update(listos)
    return niveles


def _a_dict(res: Any) -> Any:
    return res.model_dump(mode="json") if hasattr(res, "model_dump") else res


class Flujo:
    def __init__(self, nombre: str, version: str, pasos: list[Paso], norma_version: str, *, almacen: Optional[Almacen] = None,
                 registro_efectos: Optional[RegistroEfectos] = None, max_hilos: int = 4) -> None:
        mapa: dict[str, Paso] = {}
        for p in pasos:
            if p.nombre in mapa:
                raise ValueError(f"Paso duplicado en el flujo {nombre!r}: {p.nombre!r}.")
            mapa[p.nombre] = p
        for p in pasos:
            for dep in p.entradas:
                if dep not in mapa:
                    raise ValueError(f"El paso {p.nombre!r} consume {dep!r}, que no tiene productor en el flujo.")
                if mapa[dep].efecto and not p.efecto:
                    raise ValueError(f"El paso puro {p.nombre!r} no puede depender del efecto {dep!r}: los efectos van al final "
                                     "para que un fallo no deje el flujo a medias.")
        self.nombre, self.version, self.norma_version = nombre, version, norma_version
        self._pasos = mapa
        niveles = _niveles(mapa)
        self._niveles_puros = [[n for n in nv if not mapa[n].efecto] for nv in niveles]
        self._niveles_puros = [nv for nv in self._niveles_puros if nv]
        self._efectos = [n for nv in niveles for n in nv if mapa[n].efecto]
        self.almacen = almacen if almacen is not None else Almacen()
        self.registro_efectos = registro_efectos if registro_efectos is not None else RegistroEfectos()
        self._max_hilos = max(1, max_hilos)
        self.ultima_completa: dict[str, str] = {}             # paso -> id, de la última ejecución que terminó entera
        self._lock_commit = threading.Lock()

    # ----------------------------------------------------------------------------------------------- llaves
    def _params(self, paso: Paso, solicitud: Mapping[str, Any]) -> dict:
        faltan = [k for k in paso.parametros if k not in solicitud]
        if faltan:
            raise ValueError(f"Falta el parámetro {faltan[0]!r} requerido por el paso {paso.nombre!r} del flujo {self.nombre!r}; "
                             "no se asume ningún valor por defecto.")
        return {k: solicitud[k] for k in paso.parametros}

    def _llaves(self, paso: Paso, params: dict, arts: Mapping[str, Artefacto]) -> tuple[str, str, tuple[str, ...]]:
        ids_in = tuple(arts[d].id for d in paso.entradas)
        h_in = hash_canonico({"params": params, "entradas": list(ids_in)})
        id_ = hash_canonico({"flujo": self.nombre, "version_flujo": self.version, "paso": paso.nombre, "version": paso.version,
                             "norma": self.norma_version, "h": h_in})
        return id_, h_in, ids_in

    def _artefacto(self, paso: Paso, id_: str, h_in: str, ids_in: tuple[str, ...], res: Any) -> Artefacto:
        dump = _a_dict(res)
        return Artefacto(id_, paso.nombre, paso.version, self.norma_version, h_in, hash_canonico(dump), ids_in, dump)

    # ----------------------------------------------------------------------------------------------- ejecución
    def _puro(self, nombre: str, solicitud: Mapping[str, Any], arts: Mapping[str, Artefacto]) -> tuple[Artefacto, bool]:
        paso = self._pasos[nombre]
        id_, h_in, ids_in = self._llaves(paso, self._params(paso, solicitud), arts)
        a = self.almacen.obtener(id_)
        if a is not None:
            return a, True
        a = self._artefacto(paso, id_, h_in, ids_in, paso.fn(self._params(paso, solicitud), {d: arts[d] for d in paso.entradas}))
        self.almacen.guardar(a)                    # válido por construcción: sirve para reintentar aunque el flujo falle después
        return a, False

    def ejecutar(self, solicitud: Mapping[str, Any], *, idempotency_key: Optional[str] = None) -> ResultadoFlujo:
        if self._efectos and not idempotency_key:
            raise ValueError(f"El flujo {self.nombre!r} tiene pasos con efectos ({', '.join(self._efectos)}): exige idempotency_key.")
        arts: dict[str, Artefacto] = {}
        out = ResultadoFlujo(arts)
        for nivel in self._niveles_puros:
            if len(nivel) > 1 and self._max_hilos > 1:
                with ThreadPoolExecutor(max_workers=min(self._max_hilos, len(nivel))) as ex:
                    futuros = {n: ex.submit(self._puro, n, solicitud, dict(arts)) for n in nivel}
                    resultados = {n: f.result() for n, f in futuros.items()}     # el primer error se relanza aquí
            else:
                resultados = {n: self._puro(n, solicitud, arts) for n in nivel}
            for n in nivel:
                arts[n], reusado = resultados[n]
                (out.reutilizados if reusado else out.ejecutados).append(n)
        for nombre in self._efectos:               # solo si todo lo puro terminó bien
            paso = self._pasos[nombre]
            params = self._params(paso, solicitud)
            id_, h_in, ids_in = self._llaves(paso, params, arts)
            llave = hash_canonico({"flujo": self.nombre, "paso": nombre, "idempotency_key": idempotency_key})
            previo = self.registro_efectos.obtener(llave)
            if previo is not None:
                if previo.hash_entrada != h_in:
                    raise ConflictoIdempotencia(f"La idempotency_key ya se usó en {self.nombre!r}/{nombre!r} con otras entradas.")
                arts[nombre] = previo
                out.reutilizados.append(nombre)
                continue
            a = self._artefacto(paso, id_, h_in, ids_in, paso.fn(params, {d: arts[d] for d in paso.entradas}))
            arts[nombre] = self.registro_efectos.registrar(llave, a, flujo=self.nombre)
            out.ejecutados.append(nombre)
        with self._lock_commit:                    # commit: solo con el flujo completo
            self.ultima_completa = {n: a.id for n, a in arts.items()}
        return out
