"""Carga motores hermanos como paquetes reales vía importlib (mismo patrón que apps/api/main.py).

Los motores usan el nombre genérico `src`, por eso no se pueden importar con sys.path sin colisionar.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

PAQUETES = Path(__file__).resolve().parents[2]


def cargar_motor(carpeta: str, alias: str) -> ModuleType:
    """Carga packages/<carpeta>/src como paquete `alias` (idempotente)."""
    if alias in sys.modules:
        return sys.modules[alias]
    init = PAQUETES / carpeta / "src" / "__init__.py"
    if not init.exists():
        raise FileNotFoundError(f"Motor no encontrado: {init}")
    spec = importlib.util.spec_from_file_location(alias, init, submodule_search_locations=[str(init.parent)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def motor_apu_cantidades() -> ModuleType:
    cargar_motor("motor-apu", "motor_apu")
    return importlib.import_module("motor_apu.cantidades")


def modulo_a4() -> ModuleType:
    """Apéndice A-4 (módulo autónomo de motor-geopot; no se importa el paquete completo para no exigir pydantic)."""
    alias = "motor_geopot_a4"
    if alias in sys.modules:
        return sys.modules[alias]
    ruta = PAQUETES / "motor-geopot" / "src" / "a4.py"
    spec = importlib.util.spec_from_file_location(alias, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def motor_concreto_sismo() -> ModuleType:
    cargar_motor("motor-concreto", "motor_concreto")
    return importlib.import_module("motor_concreto.sismo_viga")


def motor_concreto_viga() -> ModuleType:
    cargar_motor("motor-concreto", "motor_concreto")
    return importlib.import_module("motor_concreto.viga")
