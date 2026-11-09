"""Optimizador conjunto zapata troncopiramidal + pedestal por costo y/o CO2, con dosificación variable y durabilidad NSR-10 C.4.

HIPÓTESIS de investigación (ver SUPUESTOS y economia_concreto.py): el modelo de mezcla, el precio de la ceniza y la geometría troncopiramidal no
están verificados contra ensayos ni contra la norma. La altura del pedestal sale del desplante: h_p = Df − h_c (el pedestal llega hasta el nivel
de desplante superior), así que una zapata más gruesa acorta el pedestal. No se suma el peso propio del pedestal a la presión sobre el suelo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from . import zapata_troncopiramidal as t
from .economia_concreto import AGUA, FE, PRECIO_ACERO, PRECIO_ENC, co2_m3, costo_m3, mezcla
from .encofrado_dxf import exportar_dxf
from .pedestal import ResultadoPedestal, disenar_pedestal
from .viga import Materiales
from .zapata import CargasZapata, Suelo

# Exposiciones NSR-10 C.4 (Tablas C.4.2.1/C.4.3.1 verificadas en imagen). x_max = tope de ceniza de diseño: NSR-10 no lo fija fuera de F3 (25 %);
# 0.25 es analogía conservadora. En S1 (agua marina) añadir ceniza exige ensayo C.4.5.1: sin ensayo x_max = 0.
EXPOSICIONES = {
    "interior_C1_S0": {"fc_min": 17.0, "amc_max": 0.50, "x_max": 0.25},
    "costa_C2_S1_sin_ensayo": {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.0},
    "costa_C2_S1_con_ensayo": {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.25},
}
FC_OPCIONES = (21.0, 28.0, 35.0)
X_OPCIONES = (0.0, 0.1, 0.2, 0.25)

SUPUESTOS = (
    "Modelo de mezcla (Abrams, k=0.4, 28 d) y precio de la ceniza no verificados.",
    "Pedestal con carga axial concéntrica; sin momentos ni cortante en la base (C.15.8.1.4).",
    "Peso del pedestal no incluido en la presión sobre el suelo.",
    "Recubrimiento de C2: NSR-10 C.7.7.6 no da un valor; se usa el parámetro recubrimiento_mm (75 mm = contra el suelo, C.7.7.1(a)).",
)


@dataclass(frozen=True)
class DisenoConjunto:
    exposicion: str
    fc: float
    x_ceniza: float
    zapata: t.ResultadoTroncopiramidal
    pedestal: ResultadoPedestal
    h_pedestal_mm: float
    costo_cop: float
    co2_kg: float
    area_encofrado_m2: float
    ruta_dxf: Optional[str] = None


def _evaluar(z: t.ResultadoTroncopiramidal, p: ResultadoPedestal, fc: float, x: float, p_ceniza: float, fe_cem: float) -> tuple[float, float]:
    vol = z.volumen_m3 + p.volumen_m3
    acero = z.masa_acero_kg + p.masa_acero_kg
    enc = z.area_encofrado_m2 + p.area_encofrado_m2
    cop = vol * costo_m3(fc, x, p_ceniza) + acero * PRECIO_ACERO + enc * PRECIO_ENC
    co2 = vol * co2_m3(fc, x, fe_cem) + acero * FE["acero"]
    return cop, co2


def optimizar_conjunto(c_mm: float, cargas: CargasZapata, suelo: Suelo, *, exposicion: str = "interior_C1_S0", objetivo: str = "costo",
                       peso_co2_cop_por_kg: float = 0.0, fy: float = 420.0, p_ceniza: float = 150.0, fe_cemento: float = 1.010,
                       recubrimiento_mm: float = t.RECUBRIMIENTO_SUELO_MM, paso_mm: float = 50.0, holgura_L_mm: float = 600.0,
                       ruta_dxf: str | Path | None = None) -> Optional[DisenoConjunto]:
    """Mínimo de `costo` (COP), `co2` (kg) o `costo + peso·co2` (objetivo="mixto") sobre geometría, f'c y ceniza admisibles por la exposición.
    Devuelve None si ninguna combinación cumple. Con `ruta_dxf` escribe el encofrado del óptimo."""
    if exposicion not in EXPOSICIONES:
        raise ValueError(f"exposición desconocida: {exposicion}; use {tuple(EXPOSICIONES)}")
    if objetivo not in ("costo", "co2", "mixto"):
        raise ValueError("objetivo debe ser 'costo', 'co2' o 'mixto'")
    ex = EXPOSICIONES[exposicion]
    df_mm = suelo.profundidad_desplante_m * 1000
    mejor: Optional[tuple[float, DisenoConjunto]] = None
    for fc in (f for f in FC_OPCIONES if f >= ex["fc_min"]):
        xs = [x for x in X_OPCIONES if x <= ex["x_max"] + 1e-9 and AGUA / sum(mezcla(fc, x)[k] for k in ("cem", "ash")) <= ex["amc_max"] + 1e-9]
        if not xs:
            continue
        m = Materiales(fc, fy, fy)
        pedestales: dict[float, ResultadoPedestal] = {}
        A_min = cargas.P_serv / suelo.q_adm_kpa
        L0 = max(math.ceil(math.sqrt(A_min) * 1000 / paso_mm) * paso_mm, c_mm + 200.0)
        primera = None
        for L in np.arange(L0, 6000.0 + 1, paso_mm):
            if primera is not None and L > primera + holgura_L_mm:
                break
            for h_c in np.arange(300.0, min(1000.0, df_mm) + 1, paso_mm):
                h_p = df_mm - float(h_c)
                if float(h_c) not in pedestales:
                    pedestales[float(h_c)] = disenar_pedestal(c_mm, h_p, cargas.P_u, fc, fy, float(h_c))
                ped = pedestales[float(h_c)]
                if not ped.cumple:
                    continue
                for h_e in np.arange(300.0, h_c + 1, paso_mm):
                    z = t.verificar(float(L), float(h_c), float(h_e), c_mm, cargas, suelo, m, recubrimiento_mm=recubrimiento_mm)
                    if not z.cumple:
                        continue
                    primera = L if primera is None else primera
                    for x in xs:
                        cop, co2 = _evaluar(z, ped, fc, x, p_ceniza, fe_cemento)
                        crit = cop if objetivo == "costo" else co2 if objetivo == "co2" else cop + peso_co2_cop_por_kg * co2
                        if mejor is None or crit < mejor[0]:
                            mejor = (crit, DisenoConjunto(exposicion, fc, x, z, ped, h_p, cop, co2, z.area_encofrado_m2 + ped.area_encofrado_m2))
    if mejor is None:
        return None
    d = mejor[1]
    if ruta_dxf is not None:
        exportar_dxf(d.zapata, c_mm, d.h_pedestal_mm, ruta_dxf, titulo=f"Zapata+pedestal {exposicion} fc={d.fc:.0f} ceniza={d.x_ceniza:.0%}")
        d = DisenoConjunto(**{**d.__dict__, "ruta_dxf": str(ruta_dxf)})
    return d
