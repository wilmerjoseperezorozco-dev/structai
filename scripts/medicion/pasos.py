"""Medición de latencia por paso (#221, fase 1, paso 2), sin tocar el código de producción.

En vez de decorar funciones en el repositorio, `instrumentar()` envuelve en tiempo de ejecución las funciones que el inventario
estático (`docs/cadenas_ejecucion.json`) declara como pasos de una cadena, y reemplaza cada referencia a la función original en
todos los módulos cargados (así también se miden los `from x import f`). `deshacer()` lo deja todo como estaba.

Por cada (cadena, paso) se registran:
  - tiempo inclusivo (con lo que el paso llama) y propio (sin los pasos instrumentados anidados);
  - llamadas por petición (frecuencia) y tasa de error (la excepción se registra y se vuelve a lanzar: nada se oculta).

`sin_red_externa()` prohíbe toda conexión que no sea a la propia máquina: la medición local nunca alcanza producción.
"""
from __future__ import annotations

import contextlib
import functools
import inspect
import os
import socket
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np


class Registro:
    def __init__(self) -> None:
        self.llamadas: list[tuple[str, str, float, float, bool]] = []     # (cadena, paso, inclusivo_s, propio_s, error)
        self.peticiones: dict[str, list[tuple[float, bool]]] = defaultdict(list)
        self._local = threading.local()
        # La cadena activa es GLOBAL, no por hilo: el endpoint corre en el hilo del servidor de pruebas (TestClient) y en el
        # threadpool de Starlette, no en el hilo que abre la petición. Por eso la medición es secuencial (una petición a la vez).
        self._cadena: Optional[str] = None

    # --- pila por hilo: el tiempo propio descuenta los pasos instrumentados anidados
    def _pila(self) -> list:
        if not hasattr(self._local, "pila"):
            self._local.pila = []
        return self._local.pila

    @property
    def cadena(self) -> Optional[str]:
        return self._cadena

    @contextlib.contextmanager
    def peticion(self, cadena: str):
        """Una petición completa de la cadena: fija la cadena activa y mide el total."""
        if self._cadena is not None:
            raise RuntimeError(f"Petición anidada ({cadena} dentro de {self._cadena}): la medición es una petición a la vez")
        self._cadena = cadena
        t0, error = time.perf_counter(), False
        try:
            yield
        except BaseException:
            error = True
            raise
        finally:
            self.peticiones[cadena].append((time.perf_counter() - t0, error))
            self._cadena = None

    def envolver(self, nombre: str, fn: Callable) -> Callable:
        reg = self

        def _medir(llamar):
            pila = reg._pila()
            pila.append(0.0)
            t0, error = time.perf_counter(), False
            try:
                return llamar()
            except BaseException:
                error = True
                raise
            finally:
                dt = time.perf_counter() - t0
                hijos = pila.pop()
                if pila:
                    pila[-1] += dt
                if reg.cadena is not None:
                    reg.llamadas.append((reg.cadena, nombre, dt, max(dt - hijos, 0.0), error))

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def envuelta(*a, **k):
                pila = reg._pila()
                pila.append(0.0)
                t0, error = time.perf_counter(), False
                try:
                    return await fn(*a, **k)
                except BaseException:
                    error = True
                    raise
                finally:
                    dt = time.perf_counter() - t0
                    hijos = pila.pop()
                    if pila:
                        pila[-1] += dt
                    if reg.cadena is not None:
                        reg.llamadas.append((reg.cadena, nombre, dt, max(dt - hijos, 0.0), error))
        else:
            @functools.wraps(fn)
            def envuelta(*a, **k):
                return _medir(lambda: fn(*a, **k))
        envuelta.__paso_original__ = fn
        return envuelta

    def resumen(self) -> dict:
        """{cadena: {"peticiones": {...}, "pasos": [{paso, llamadas_por_peticion, p50_ms, p95_ms, propio_p50_ms, ...}]}}"""
        salida = {}
        for cadena, pets in self.peticiones.items():
            tot = np.array([t for t, _ in pets]) * 1000
            n_pet = len(pets)
            grupos: dict[str, list] = defaultdict(list)
            for c, paso, inc, prop, err in self.llamadas:
                if c == cadena:
                    grupos[paso].append((inc, prop, err))
            pasos = []
            for paso, xs in grupos.items():
                inc = np.array([x[0] for x in xs]) * 1000
                prop = np.array([x[1] for x in xs]) * 1000
                pasos.append({"paso": paso, "llamadas": len(xs), "llamadas_por_peticion": round(len(xs) / n_pet, 3),
                              "tasa_error": round(sum(x[2] for x in xs) / len(xs), 4),
                              "p50_ms": _r(np.percentile(inc, 50)), "p95_ms": _r(np.percentile(inc, 95)),
                              "propio_p50_ms": _r(np.percentile(prop, 50)), "propio_p95_ms": _r(np.percentile(prop, 95)),
                              "propio_total_por_peticion_ms": _r(prop.sum() / n_pet)})
            pasos.sort(key=lambda p: -p["propio_total_por_peticion_ms"])
            salida[cadena] = {"peticiones": {"n": n_pet, "tasa_error": round(sum(e for _, e in pets) / n_pet, 4),
                                             "p50_ms": _r(np.percentile(tot, 50)), "p95_ms": _r(np.percentile(tot, 95))},
                              "pasos": pasos}
        return salida


def _r(x: float) -> float:
    return round(float(x), 3)


def _modulos_de(ruta: Path) -> list:
    ruta = ruta.resolve()
    salida = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        try:
            if Path(f).resolve() == ruta:
                salida.append(m)
        except OSError:
            continue
    return salida


class Instrumentacion:
    """Plan de reemplazos calculado UNA vez (recorrer todos los módulos es caro); `aplicar()`/`deshacer()` lo alternan barato."""

    def __init__(self, registro: Registro, pasos: Iterable[str], raiz: Path) -> None:
        self.cambios: list[tuple[object, str, object, object]] = []         # (objeto, atributo, original, envuelta)
        self.hechos: list[str] = []
        self.omitidos: list[str] = []
        self.aplicada = False
        originales: dict[int, tuple[object, Callable]] = {}                 # id(función) -> (función, envuelta)
        for paso in dict.fromkeys(pasos):
            ruta_txt, sep, nombre = paso.partition("::")
            if not sep or not ruta_txt.endswith(".py"):
                self.omitidos.append(paso)
                continue
            hecho = False
            for m in _modulos_de(raiz / ruta_txt):
                partes = nombre.split(".")
                dueno = m
                for parte in partes[:-1]:
                    dueno = getattr(dueno, parte, None)
                original = getattr(dueno, partes[-1], None) if dueno is not None else None
                if original is None or not callable(original) or isinstance(original, type):
                    continue
                original = getattr(original, "__paso_original__", original)
                if inspect.isclass(dueno):
                    crudo = inspect.getattr_static(dueno, partes[-1])
                    if isinstance(crudo, (staticmethod, classmethod)):
                        continue                                  # no se envuelven (cambia el enlace); quedan como omitidos
                    _f, envuelta = originales.setdefault(id(original), (original, registro.envolver(paso, original)))
                    self.cambios.append((dueno, partes[-1], crudo, envuelta))
                else:
                    originales.setdefault(id(original), (original, registro.envolver(paso, original)))
                hecho = True
            (self.hechos if hecho else self.omitidos).append(paso)
        # toda referencia a una función original en cualquier módulo cargado (cubre los `from x import f`): un solo recorrido
        for otro in list(sys.modules.values()):
            d = getattr(otro, "__dict__", None)
            if not isinstance(d, dict):
                continue
            for k, v in list(d.items()):
                par = originales.get(id(v))
                if par is not None and par[0] is v:
                    self.cambios.append((otro, k, v, par[1]))

    def aplicar(self) -> None:
        if not self.aplicada:
            for obj, k, _orig, env in self.cambios:
                setattr(obj, k, env)
            self.aplicada = True

    def deshacer(self) -> None:
        if self.aplicada:
            for obj, k, orig, _env in reversed(self.cambios):
                setattr(obj, k, orig)
            self.aplicada = False


def instrumentar(registro: Registro, pasos: Iterable[str], raiz: Path) -> tuple[Callable[[], None], list[str], list[str]]:
    """Envuelve cada paso «ruta.py::funcion» o «ruta.py::Clase.metodo» ya importado. Devuelve (deshacer, instrumentados, omitidos)."""
    inst = Instrumentacion(registro, pasos, raiz)
    inst.aplicar()
    return inst.deshacer, inst.hechos, inst.omitidos


_LOCALES = {"localhost", "127.0.0.1", "::1", "testserver"}


@contextlib.contextmanager
def sin_red_externa():
    """Prohíbe conexiones fuera de la máquina durante la medición (Supabase, LLM, APIs públicas). Lanza ConnectionRefusedError."""
    original_connect = socket.socket.connect
    original_cc = socket.create_connection
    original_gai = socket.getaddrinfo

    def _local(host) -> bool:
        h = host[0] if isinstance(host, tuple) else host
        if isinstance(h, bytes):
            h = h.decode("ascii", "replace")
        return isinstance(h, str) and (h in _LOCALES or h.startswith("127."))

    def connect(self, addr):
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _local(addr):
            raise ConnectionRefusedError(f"medición local: conexión externa bloqueada ({addr})")
        return original_connect(self, addr)

    def create_connection(addr, *a, **k):
        if not _local(addr):
            raise ConnectionRefusedError(f"medición local: conexión externa bloqueada ({addr})")
        return original_cc(addr, *a, **k)

    def getaddrinfo(host, *a, **k):
        if host is not None and not _local(host):
            raise socket.gaierror(f"medición local: resolución externa bloqueada ({host})")
        return original_gai(host, *a, **k)

    socket.socket.connect, socket.create_connection, socket.getaddrinfo = connect, create_connection, getaddrinfo
    try:
        yield
    finally:
        socket.socket.connect, socket.create_connection, socket.getaddrinfo = original_connect, original_cc, original_gai


def raiz_repo() -> Path:
    return Path(os.environ.get("STRUCTAI_RAIZ", Path(__file__).resolve().parents[2]))
