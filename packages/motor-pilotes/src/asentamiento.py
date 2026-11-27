"""Asentamiento de pilotes y grupos bajo carga permanente (NSR-10 H.4.4.2, método del CCP-14 §10.7.2.3).

La NSR-10 (H.4.4.2) exige estimar el asentamiento con la deformación propia del pilote y la de los materiales bajo la
punta, pero no fija fórmulas. Se usa el camino del CCP-14:

  Zapata equivalente (Fig. 10.7.2.3.1-1, Hannigan et al. 2006): planta = perímetro exterior del grupo, a una
  profundidad z_eq = (L − Db) + f·Db, con Db el empotramiento en la capa que da el soporte y
      f = 1     (a) pilotes de punta en arcilla dura o arena sobre arcilla blanda
      f = 2/3   (b) pilotes de fricción en arcilla
      f = 8/9   (c) pilotes de fricción en arena sobre arcilla
      f = 2/3   (d) fricción y punta en perfil por capas
  Sin reducción B' = B − 2e (§10.7.2.3.1). La presión se reparte 2V:1H bajo la zapata equivalente.

  Suelo cohesivo (§10.7.2.3.2): consolidación primaria de cimentaciones superficiales (motor-geotecnia).
  Suelo granular, SPT (Ec. 10.7.2.3.2-1 y -3, Meyerhof 1976):
      ρ [mm] = 30·q·I·√B / N1_60,  q en MPa, B en mm,  I = 1 − 0.125·D'/B ≥ 0.5,  D' = 2/3·Db
      N1_60 promediado en una profundidad B bajo la zapata equivalente (lo entrega el usuario).

  Acortamiento elástico del fuste: δe = Q·L/(A·Ep), con la carga completa en toda la longitud. Es la cota superior
  (en un pilote de fricción la carga decrece con la profundidad); la distribución real exige el reparto del fuste.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Literal, Optional, Sequence

_REF = "NSR-10 H.4.4.2 / CCP-14 §10.7.2.3"

FACTOR_PROFUNDIDAD = {"a_punta": 1.0, "b_friccion_arcilla": 2.0 / 3.0, "c_friccion_arena_sobre_arcilla": 8.0 / 9.0,
                      "d_capas": 2.0 / 3.0}
CasoZapata = Literal["a_punta", "b_friccion_arcilla", "c_friccion_arena_sobre_arcilla", "d_capas"]
I_MINIMO = 0.5


def _cargar_geotecnia(nombre: str):
    """Carga un módulo de motor-geotecnia/src por ruta (todos los paquetes se llaman `src`)."""
    ruta = Path(__file__).resolve().parents[2] / "motor-geotecnia" / "src" / f"{nombre}.py"
    spec = importlib.util.spec_from_file_location(f"motor_geotecnia_{nombre}", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ESF = _cargar_geotecnia("esfuerzos")
_CONS = _cargar_geotecnia("consolidacion")


def _falla(msg: str) -> None:
    raise ValueError(f"{msg} ({_REF}).")


def _positivo(nombre: str, v: float) -> None:
    if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
        _falla(f"{nombre} debe ser positivo y finito; se recibió {v!r}")


def acortamiento_elastico_m(carga_kn: float, longitud_m: float, area_m2: float, ep_mpa: float) -> float:
    """δe = Q·L/(A·Ep), carga completa en toda la longitud (cota superior)."""
    for n, v in (("Q", carga_kn), ("L", longitud_m), ("A", area_m2), ("Ep", ep_mpa)):
        _positivo(n, v)
    return carga_kn * longitud_m / (area_m2 * ep_mpa * 1000.0)


def planta_grupo(filas: int, columnas: int, separacion_m: float, ancho_m: float) -> tuple[float, float]:
    """Perímetro exterior del grupo (B ≤ L): (n − 1)·s + D en cada dirección."""
    if filas < 1 or columnas < 1:
        _falla("El grupo necesita al menos una fila y una columna")
    _positivo("D", ancho_m)
    if filas * columnas > 1:
        _positivo("s", separacion_m)
    a = (filas - 1) * separacion_m + ancho_m
    b = (columnas - 1) * separacion_m + ancho_m
    return (min(a, b), max(a, b))


def profundidad_zapata_equivalente(longitud_m: float, db_m: float, caso: CasoZapata) -> float:
    _positivo("L", longitud_m)
    _positivo("Db", db_m)
    if db_m > longitud_m:
        _falla("Db (empotramiento en la capa de soporte) no puede superar la longitud del pilote")
    if caso not in FACTOR_PROFUNDIDAD:
        _falla(f"Caso de zapata equivalente desconocido: {caso!r}")
    return (longitud_m - db_m) + FACTOR_PROFUNDIDAD[caso] * db_m


def asentamiento_granular_spt_mm(q_mpa: float, b_m: float, db_m: float, n1_60: float) -> tuple[float, float]:
    """Ec. 10.7.2.3.2-1 y -3. Devuelve (ρ en mm, I)."""
    for n, v in (("q", q_mpa), ("B", b_m), ("Db", db_m), ("N1_60", n1_60)):
        _positivo(n, v)
    b_mm = b_m * 1000.0
    d_mm = 2.0 / 3.0 * db_m * 1000.0
    i = max(I_MINIMO, 1.0 - 0.125 * d_mm / b_mm)
    return 30.0 * q_mpa * i * math.sqrt(b_mm) / n1_60, i


def asentamiento_cohesivo_m(q_kpa: float, b_m: float, l_m: float, estratos: Sequence[dict]) -> list[dict]:
    """Consolidación primaria de cada estrato bajo la zapata equivalente, con Δσ por 2V:1H en su punto medio.

    Cada estrato: z_tope_m (bajo la zapata equivalente), espesor_m, sigma0_kpa, sigma_p_kpa, cc, cr, e0.
    """
    _positivo("q", q_kpa)
    _positivo("B", b_m)
    _positivo("L", l_m)
    if not estratos:
        _falla("Faltan los estratos compresibles bajo la zapata equivalente")
    salida = []
    for i, e in enumerate(estratos):
        if e["z_tope_m"] < 0:
            _falla(f"Estrato {i}: z_tope_m no puede ser negativo (se mide bajo la zapata equivalente)")
        z = e["z_tope_m"] + e["espesor_m"] / 2.0
        dsig = _ESF.esfuerzo_2a1(q_kpa, b_m, l_m, z)
        s = _CONS.asentamiento_primario(cc=e["cc"], cr=e["cr"], e0=e["e0"], espesor_m=e["espesor_m"],
                                        sigma0_kpa=e["sigma0_kpa"], delta_kpa=dsig, sigma_p_kpa=e["sigma_p_kpa"])
        salida.append({"z_medio_m": z, "delta_sigma_kpa": dsig, "asentamiento_m": s})
    return salida


def asentamiento_grupo(*, carga_permanente_kn: float, filas: int, columnas: int, separacion_m: Optional[float],
                       ancho_m: float, area_m2: float, longitud_m: float, ep_mpa: float, db_m: float,
                       caso: CasoZapata, suelo_bajo_zapata: Literal["cohesivo", "granular_spt"],
                       estratos_cohesivos: Optional[Sequence[dict]] = None,
                       n1_60_bajo_zapata: Optional[float] = None) -> dict:
    """Asentamiento total = acortamiento del fuste de un pilote + asentamiento del suelo bajo la zapata equivalente."""
    _positivo("Carga permanente", carga_permanente_kn)
    n = filas * columnas
    b, l = planta_grupo(filas, columnas, separacion_m or 0.0, ancho_m)
    z_eq = profundidad_zapata_equivalente(longitud_m, db_m, caso)
    q_kpa = carga_permanente_kn / (b * l)
    delta_e = acortamiento_elastico_m(carga_permanente_kn / n, longitud_m, area_m2, ep_mpa)
    detalle: dict = {}
    if suelo_bajo_zapata == "granular_spt":
        if n1_60_bajo_zapata is None:
            _falla("Suelo granular bajo la zapata equivalente: falta N1_60 promediado en una profundidad B")
        rho_mm, i = asentamiento_granular_spt_mm(q_kpa / 1000.0, b, db_m, n1_60_bajo_zapata)
        s_suelo = rho_mm / 1000.0
        detalle = {"I": i, "n1_60": n1_60_bajo_zapata}
    elif suelo_bajo_zapata == "cohesivo":
        if not estratos_cohesivos:
            _falla("Suelo cohesivo bajo la zapata equivalente: faltan los estratos con Cc, Cr, e0, σ'0 y σ'p")
        capas = asentamiento_cohesivo_m(q_kpa, b, l, estratos_cohesivos)
        s_suelo = sum(c["asentamiento_m"] for c in capas)
        detalle = {"estratos": capas}
    else:
        _falla(f"Suelo bajo la zapata equivalente desconocido: {suelo_bajo_zapata!r}")
    return {"B_m": b, "L_m": l, "z_zapata_equivalente_m": z_eq, "q_kpa": q_kpa, "acortamiento_m": delta_e,
            "asentamiento_suelo_m": s_suelo, "asentamiento_total_m": delta_e + s_suelo, "detalle": detalle}
