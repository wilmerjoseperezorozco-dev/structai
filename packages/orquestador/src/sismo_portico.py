"""Fuerzas sísmicas de un pórtico plano derivadas del espectro (cadena A.2.4 → A.2.6 → A.4.2 → A.4.3 → B.2.4.2.1).

Supuestos declarados (no verificados como "los reales" de un edificio completo):
  - El pórtico plano representa su ancho tributario: las cargas lineales que el usuario entrega (kN/m) son las que
    llegan a ese pórtico, y su peso sísmico es el de esas cargas + el peso propio de vigas y columnas.
  - Peso sísmico = carga muerta + peso propio. La carga viva NO se incluye (la norma pide 25 % solo en depósitos y bodegas).
  - Estructura regular en planta y altura (φa = φp = 1,0) y redundante (φr = 1,0), sin torsión accidental.
  - T = Ta = Ct·hⁿ^α (A.4.2.2, permitido); se reporta además el T de Rayleigh (A.4.2-1) como comprobación.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .cargador import modulo_cortante_basal

PESO_UNIT_KN_M3 = 24.0
_cb = modulo_cortante_basal()


@dataclass(frozen=True)
class ContextoSismico:
    aa: float
    av: float
    perfil: str
    grupo_uso: str
    capacidad: str
    phi_a: float = 1.0
    phi_p: float = 1.0
    phi_r: float = 1.0


def pesos_nivel_kn(luces_m, alturas_piso_m, nx: int, carga_muerta_kn_m: float, columna_mm, b, h):
    """Peso sísmico por nivel (kN), arreglo (..., n_niveles). `b`, `h` en mm (escalares o arreglos)."""
    b, h = np.asarray(b, dtype=float), np.asarray(h, dtype=float)
    w_pp = PESO_UNIT_KN_M3 * b / 1000 * h / 1000
    vigas = (carga_muerta_kn_m + w_pp) * float(sum(luces_m))
    c1, c2 = columna_mm[0] / 1000, columna_mm[1] / 1000
    col_piso = [PESO_UNIT_KN_M3 * c1 * c2 * hp * nx for hp in alturas_piso_m]      # kN, todas las columnas de un entrepiso
    n = len(alturas_piso_m)
    pesos = []
    for i in range(n):
        mitad_abajo = 0.5 * col_piso[i]
        mitad_arriba = 0.5 * col_piso[i + 1] if i + 1 < n else 0.0
        pesos.append(vigas + mitad_abajo + mitad_arriba)
    return np.stack(pesos, axis=-1)


def alturas_nivel_m(alturas_piso_m) -> tuple[float, ...]:
    acc, out = 0.0, []
    for hp in alturas_piso_m:
        acc += hp
        out.append(acc)
    return tuple(out)


def fuerzas_escalar(ctx: ContextoSismico, pesos: tuple[float, ...], alturas: tuple[float, ...]):
    """Referencia escalar (módulo cortante_basal) → CortanteBasal."""
    return _cb.cortante_basal(aa=ctx.aa, av=ctx.av, perfil=ctx.perfil, capacidad=ctx.capacidad,
                              pesos_nivel_kn=pesos, alturas_nivel_m=alturas, grupo_uso=ctx.grupo_uso,
                              phi_a=ctx.phi_a, phi_p=ctx.phi_p, phi_r=ctx.phi_r)


def parametros_espectro(ctx: ContextoSismico, alturas: tuple[float, ...]) -> dict:
    """Constantes que no dependen de la sección (Fa, Fv, T, Sa, k, R) para la versión vectorizada."""
    ref = fuerzas_escalar(ctx, tuple(1.0 for _ in alturas), alturas)
    return {"sa": ref.sa, "sa_deriva": ref.sa_deriva, "k": ref.k, "r": ref.r, "T": ref.T, "cu_ta": ref.cu_ta,
            "fa": ref.fa, "fv": ref.fv, "I": ref.I, "tc": ref.tc, "tl": ref.tl}


def fuerzas_vectorizadas(par: dict, pesos: np.ndarray, alturas: tuple[float, ...]) -> np.ndarray:
    """E de diseño por nivel (Fs/R) para muchos pesos a la vez. pesos: (N, n_niveles). Devuelve (N, n_niveles)."""
    h = np.asarray(alturas, dtype=float) ** par["k"]
    vs = par["sa"] * pesos.sum(axis=1, keepdims=True)
    reparto = pesos * h / (pesos * h).sum(axis=1, keepdims=True)
    return vs * reparto / par["r"]


def periodo_rayleigh(pesos_kn: np.ndarray, fuerzas_kn: np.ndarray, desplazamientos_m: np.ndarray) -> float:
    """T = 2π·√(Σ mᵢδᵢ² / Σ fᵢδᵢ) (A.4.2-1). pesos en kN (m = W/g), fuerzas y desplazamientos de un mismo caso elástico."""
    m = np.asarray(pesos_kn, dtype=float) / _cb.G
    num = float((m * desplazamientos_m ** 2).sum())
    den = float((fuerzas_kn * desplazamientos_m).sum())
    if den <= 0:
        return math.nan
    return 2 * math.pi * math.sqrt(num / den)


def contexto_desde(aa: Optional[float], av: Optional[float], perfil: Optional[str], grupo: str, capacidad: str) -> ContextoSismico:
    if aa is None or av is None:
        raise ValueError("Se necesitan Aa y Av: indique municipio (Apéndice A-4) o aa y av explícitos")
    return ContextoSismico(aa=aa, av=av, perfil=perfil, grupo_uso=grupo, capacidad=capacidad)
