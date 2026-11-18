"""Grupo de pilotes a compresión (NSR-10 H.4.4.1 b): la carga de falla es la menor de
  1) la suma de las capacidades individuales;
  2) la capacidad de un bloque de terreno con la envolvente del grupo;
  3) la suma por subgrupos con la «posible» reducción por eficiencia. Aquí se aplica al grupo completo y solo si el
     usuario la pide; para subdividir la cimentación se llama una vez por subgrupo.

Eficiencia de Converse-Labarre:  E = 1 − θ·[(n−1)·m + (m−1)·n] / (90·m·n),  θ = atan(D/s) en grados.
Bloque en arcilla (Terzaghi y Peck):  Qb = 2(Bg+Lg)·Σ Su·Δz + Bg·Lg·Nc·Su,punta,
  Nc = 5(1 + 0.2·L/Bg)(1 + 0.2·Bg/Lg) si L/Bg ≤ 2.5, y 7.5(1 + 0.2·Bg/Lg) si no (Skempton, 1951).
La NSR-10 no da estas fórmulas: son las convencionales que pide H.4.4. El bloque en suelo drenado está próximamente.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from contrato_motor import exigir

from .axial import FS_FRICCION_NO_DRENADO, FS_PUNTA, Combinacion, Estrato, Pilote, _falla, _tramos, capacidad_individual

SEPARACION_MIN_REL = 2.5   # s/D usual en la práctica; por debajo se marca borde de dominio (no es de la NSR-10)


def eficiencia_converse_labarre(filas: int, columnas: int, separacion_m: float, ancho_m: float) -> float:
    if filas < 1 or columnas < 1:
        _falla("El grupo necesita al menos una fila y una columna")
    if filas * columnas == 1:
        return 1.0
    if not (separacion_m > ancho_m > 0):
        _falla("La separación entre ejes debe ser mayor que el ancho del pilote")
    theta = math.degrees(math.atan(ancho_m / separacion_m))
    m, n = filas, columnas
    return 1.0 - theta * ((n - 1) * m + (m - 1) * n) / (90.0 * m * n)


def nc_skempton(prof_m: float, b_m: float, l_m: float) -> float:
    b, l = min(b_m, l_m), max(b_m, l_m)
    r = prof_m / b
    return 5.0 * (1 + 0.2 * r) * (1 + 0.2 * b / l) if r <= 2.5 else 7.5 * (1 + 0.2 * b / l)


def capacidad_bloque_arcilla(estratos: Sequence[Estrato], pilote: Pilote, *, filas: int, columnas: int,
                             separacion_m: float, nivel_freatico_m: Optional[float], combinacion: Combinacion) -> dict:
    tramos = _tramos(estratos, nivel_freatico_m, pilote.longitud_m)
    if any(estratos[i].comportamiento != "no_drenado" for i, *_ in tramos):
        _falla("Falla en bloque implementada solo en arcilla no drenada en toda la longitud y en la punta; "
               "en suelo drenado está próximamente")
    fsl = exigir(combinacion, FS_FRICCION_NO_DRENADO, "NSR-10 H.2.4.2 y Tabla H.2.4-1 (FSBUM)",
                 "Combinación con Su (no se permite en análisis seudo-estático)")
    fsp = exigir(combinacion, FS_PUNTA, "NSR-10 Tabla H.4.7-1", "Combinación de carga")
    bg = (columnas - 1) * separacion_m + pilote.ancho_m
    lg = (filas - 1) * separacion_m + pilote.ancho_m
    fuste = 2.0 * (bg + lg) * sum(estratos[i].su_kpa * (z1 - z0) for i, z0, z1, *_ in tramos)
    nc = nc_skempton(pilote.longitud_m, bg, lg)
    base = bg * lg * nc * estratos[tramos[-1][0]].su_kpa
    return {"q_ult_kn": fuste + base, "q_adm_kn": fuste / fsl + base / fsp, "fuste_kn": fuste, "base_kn": base,
            "nc": nc, "bg_m": bg, "lg_m": lg}


METODOS_EFICIENCIA = ("converse_labarre", "ninguna")


def capacidad_grupo(estratos: Sequence[Estrato], pilote: Pilote, *, filas: int, columnas: int, separacion_m: float,
                    nivel_freatico_m: Optional[float], combinacion: Combinacion, eficiencia: str) -> dict:
    """`eficiencia` es obligatoria: la NSR-10 habla de la «posible» reducción por eficiencia (H.4.4.1 b-3) y la decide el
    ingeniero. En arcilla, Converse-Labarre suele quedar por debajo del bloque y lo vuelve irrelevante."""
    if eficiencia not in METODOS_EFICIENCIA:
        _falla(f"Método de eficiencia '{eficiencia}' no reconocido; válidos: {', '.join(METODOS_EFICIENCIA)}")
    ind = capacidad_individual(estratos, pilote, nivel_freatico_m=nivel_freatico_m, combinacion=combinacion)
    n = filas * columnas
    e = eficiencia_converse_labarre(filas, columnas, separacion_m, pilote.ancho_m) if eficiencia == "converse_labarre" else None
    modos_adm = {"suma_individuales": n * ind["q_adm_kn"]}
    modos_ult = {"suma_individuales": n * ind["q_ult_kn"]}
    if e is not None:
        modos_adm["eficiencia"], modos_ult["eficiencia"] = e * n * ind["q_adm_kn"], e * n * ind["q_ult_kn"]
    bloque = None
    if n > 1:
        try:
            bloque = capacidad_bloque_arcilla(estratos, pilote, filas=filas, columnas=columnas, separacion_m=separacion_m,
                                              nivel_freatico_m=nivel_freatico_m, combinacion=combinacion)
        except ValueError as err:
            if "próximamente" not in str(err):
                raise
            bloque = {"no_evaluado": str(err)}
        if "q_adm_kn" in bloque:
            modos_adm["bloque"] = bloque["q_adm_kn"]
            modos_ult["bloque"] = bloque["q_ult_kn"]
    gobierna = min(modos_adm, key=modos_adm.get)
    return {"n_pilotes": n, "eficiencia": e, "individual": ind, "bloque": bloque, "modos_adm_kn": modos_adm,
            "modos_ult_kn": modos_ult, "q_adm_grupo_kn": modos_adm[gobierna], "gobierna": gobierna,
            "separacion_relativa": separacion_m / pilote.ancho_m if n > 1 else None}
