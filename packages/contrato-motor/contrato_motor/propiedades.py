"""Pruebas de propiedad reutilizables para los motores (regla 7): monotonicidad y homogeneidad de escala."""
from __future__ import annotations

import math
from typing import Callable, Sequence


def verificar_monotonia(f: Callable[[float], float], valores: Sequence[float], *, creciente: bool = True, estricta: bool = False) -> None:
    """Falla (AssertionError) si f no es monótona sobre `valores` (ordenados de menor a mayor)."""
    ys = [f(v) for v in valores]
    for (x0, y0), (x1, y1) in zip(zip(valores, ys), zip(valores[1:], ys[1:])):
        malo = (y1 < y0 if creciente else y1 > y0) if not estricta else (y1 <= y0 if creciente else y1 >= y0)
        if malo:
            raise AssertionError(f"f no es monótona {'creciente' if creciente else 'decreciente'}: f({x0})={y0}, f({x1})={y1}")


def verificar_homogeneidad(f: Callable[..., float], args: dict, variable: str, exponente: float, *, factor: float = 3.0, rel: float = 1e-9) -> None:
    """Comprueba f(..., variable·k, ...) = k^exponente · f(...) (leyes de potencia como Hazen-Williams o Manning)."""
    base = f(**args)
    escalado = f(**{**args, variable: args[variable] * factor})
    esperado = base * factor ** exponente
    if not math.isclose(escalado, esperado, rel_tol=rel):
        raise AssertionError(f"Homogeneidad violada en '{variable}': esperado {esperado}, obtenido {escalado}")
