"""Optimizador conjunto zapata (prismática o troncopiramidal) + pedestal por costo y/o CO2, con dosificación variable, durabilidad NSR-10 C.4,
momentos biaxiales, balasto y verificación de la base del pedestal (C.11.6).

HIPÓTESIS de investigación (ver SUPUESTOS): el modelo de mezcla, el precio de la ceniza, la geometría troncopiramidal y el cortante en la base derivado
de H_col no están verificados contra ensayos ni contra la norma. La altura del pedestal sale del desplante: h_p = Df − h_c. La geometría "prismática"
es el caso h_e = h_c; la escalonada NO está implementada.
Cargas: Pu, Mux, Muy en la base de la COLUMNA (kN, kN·m). Cortante supuesto V = M/(H_col/2); en la base del pedestal (cara superior de la zapata)
M_base = M_col + V·h_p, y esa es la solicitación de la zapata y de la junta pedestal–zapata. Servicio = última / `razon_ultima_servicio`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from . import zapata_troncopiramidal as t
from .economia_concreto import AGUA, Economia, co2_m3, costo_m3, mezcla
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
    "Cortante en la base de la columna V = M/(H_col/2) con H_col supuesto; servicio = última / razón supuesta.",
    "Flexión biaxial del pedestal por suma lineal (conservadora); sin acreditar compresión permanente en la fricción por cortante.",
    "Zapata cuadrada; punzonamiento sin transferencia de momento (C.11.11.7 no modelado).",
    "Peso del pedestal no incluido en la presión sobre el suelo.",
    "Recubrimiento de C2: NSR-10 C.7.7.6 no da un valor; se usa el parámetro recubrimiento_mm (75 mm = contra el suelo, C.7.7.1(a)).",
    "Límite de asentamiento (suelo.asentamiento_max_mm) es un parámetro del proyecto, sin fuente en el corpus.",
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

    @property
    def tipo(self) -> str:
        return "prismatica" if abs(self.zapata.h_c_mm - self.zapata.h_e_mm) < 1e-9 else "troncopiramidal"


def _evaluar(z: t.ResultadoTroncopiramidal, p: ResultadoPedestal, fc: float, x: float, eco: Economia) -> tuple[float, float]:
    vol = z.volumen_m3 + p.volumen_m3
    acero = z.masa_acero_kg + p.masa_acero_kg
    enc = z.area_encofrado_m2 + p.area_encofrado_m2
    cop = vol * costo_m3(fc, x, eco.p_ceniza, eco.mult_concreto) + acero * eco.p_acero + enc * eco.p_encofrado
    co2 = vol * co2_m3(fc, x, eco.fe_cemento) + acero * eco.fe_acero
    return cop, co2


def cargas_en_base(Pu: float, Mux: float, Muy: float, h_p_m: float, *, H_col_m: float = 3.0, razon_us: float = 1.35) -> tuple[CargasZapata, float, float, float, float]:
    """(cargas de la zapata, Mux_base, Muy_base, Vux, Vuy). Mux causa excentricidad en y y se acompaña del cortante Vuy = |Mux|/(H/2)."""
    Vuy, Vux = abs(Mux) / (H_col_m / 2), abs(Muy) / (H_col_m / 2)
    Mxb, Myb = abs(Mux) + Vuy * h_p_m, abs(Muy) + Vux * h_p_m
    c = CargasZapata(P_serv=Pu / razon_us, P_u=Pu, Mx_serv=Mxb / razon_us, My_serv=Myb / razon_us, Mx_u=Mxb, My_u=Myb)
    return c, Mxb, Myb, Vux, Vuy


def _buscar_para_c(c_mm: float, cargas: CargasZapata, suelo: Suelo, *, exposicion: str = "interior_C1_S0", objetivo: str = "costo",
                       peso_co2_cop_por_kg: float = 0.0, fy: float = 420.0, p_ceniza: float | None = None, fe_cemento: float | None = None,
                       recubrimiento_mm: float = t.RECUBRIMIENTO_SUELO_MM, paso_mm: float = 50.0, holgura_L_mm: float = 600.0,
                       ruta_dxf: str | Path | None = None, fc: float | None = None, economia: Economia | None = None,
                       momentos_columna: tuple[float, float] | None = None, H_col_m: float = 3.0, razon_ultima_servicio: float = 1.35,
                       junta_rugosa: bool = False, h_max_mm: float = 1000.0) -> Optional[tuple[float, DisenoConjunto]]:
    """Mínimo de `costo` (COP), `co2` (kg) o `costo + peso·co2` (objetivo="mixto"; con `economia.lam_co2` si peso = 0) sobre geometría, f'c y ceniza
    admisibles por la exposición. `fc` fija la resistencia (se eleva a la mínima de la exposición si es menor); si es None se elige entre FC_OPCIONES.
    `momentos_columna` = (Mux, Muy) en la base de la columna: entonces `cargas` aporta solo P_u y se calculan momentos en la base del pedestal
    para cada espesor (h_p = Df − h_c). Devuelve None si ninguna combinación cumple. Con `ruta_dxf` escribe el encofrado del óptimo."""
    if exposicion not in EXPOSICIONES:
        raise ValueError(f"exposición desconocida: {exposicion}; use {tuple(EXPOSICIONES)}")
    if objetivo not in ("costo", "co2", "mixto"):
        raise ValueError("objetivo debe ser 'costo', 'co2' o 'mixto'")
    eco = economia or Economia()
    if p_ceniza is not None or fe_cemento is not None:
        eco = Economia(**{**eco.__dict__, **({"p_ceniza": p_ceniza} if p_ceniza is not None else {}),
                          **({"fe_cemento": fe_cemento} if fe_cemento is not None else {})})
    lam = peso_co2_cop_por_kg or eco.lam_co2
    ex = EXPOSICIONES[exposicion]
    df_mm = suelo.profundidad_desplante_m * 1000
    fcs = (max(fc, ex["fc_min"]),) if fc is not None else tuple(f for f in FC_OPCIONES if f >= ex["fc_min"])
    mejor: Optional[tuple[float, DisenoConjunto]] = None
    for f in fcs:
        xs = [x for x in X_OPCIONES if x <= ex["x_max"] + 1e-9 and AGUA / sum(mezcla(f, x)[k] for k in ("cem", "ash")) <= ex["amc_max"] + 1e-9]
        if not xs:
            continue
        m = Materiales(f, fy, fy)
        base: dict[float, tuple] = {}
        A_min = cargas.P_serv / suelo.q_adm_kpa
        L0 = max(math.ceil(math.sqrt(A_min) * 1000 / paso_mm) * paso_mm, c_mm + 200.0)
        primera = None
        for L in np.arange(L0, 6000.0 + 1, paso_mm):
            if primera is not None and L > primera + holgura_L_mm:
                break
            for h_c in np.arange(300.0, min(h_max_mm, df_mm) + 1, paso_mm):
                hc = float(h_c)
                h_p = df_mm - hc
                if hc not in base:
                    if momentos_columna is None:
                        cg, Mxb, Myb, Vx, Vy = cargas, cargas.Mx_u, cargas.My_u, 0.0, 0.0
                    else:
                        cg, Mxb, Myb, Vx, Vy = cargas_en_base(cargas.P_u, momentos_columna[0], momentos_columna[1], h_p / 1000,
                                                              H_col_m=H_col_m, razon_us=razon_ultima_servicio)
                        cg = CargasZapata(P_serv=cargas.P_serv, P_u=cargas.P_u, Mx_serv=cg.Mx_serv, My_serv=cg.My_serv, Mx_u=cg.Mx_u, My_u=cg.My_u)
                    ped = disenar_pedestal(c_mm, h_p, cargas.P_u, f, fy, hc, Mux_kNm=Mxb, Muy_kNm=Myb, Vux_kN=Vx, Vuy_kN=Vy, junta_rugosa=junta_rugosa)
                    base[hc] = (cg, ped)
                cg, ped = base[hc]
                if not ped.cumple:
                    continue
                for h_e in np.arange(300.0, h_c + 1, paso_mm):
                    z = t.verificar(float(L), hc, float(h_e), c_mm, cg, suelo, m, recubrimiento_mm=recubrimiento_mm)
                    if not z.cumple:
                        continue
                    primera = L if primera is None else primera
                    for x in xs:
                        cop, co2 = _evaluar(z, ped, f, x, eco)
                        crit = cop if objetivo == "costo" else co2 if objetivo == "co2" else cop + lam * co2
                        if mejor is None or crit < mejor[0]:
                            mejor = (crit, DisenoConjunto(exposicion, f, x, z, ped, h_p, cop, co2, z.area_encofrado_m2 + ped.area_encofrado_m2))
    return mejor


def optimizar_conjunto(c_mm: float, cargas: CargasZapata, suelo: Suelo, *, c_max_mm: float | None = None, ruta_dxf: str | Path | None = None,
                       **kw) -> Optional[DisenoConjunto]:
    """Como `_buscar_para_c`, pero el lado del pedestal/columna es una variable: arranca en `c_mm` (columna) y sube de 50 en 50 hasta `c_max_mm`
    (por defecto c_mm si no hay momentos y 900 si los hay). Se toma el primer lado factible y se evalúan los dos siguientes. Con `ruta_dxf` escribe
    el DXF del óptimo (el lado óptimo queda en `diseno.pedestal.c_mm`)."""
    tope = c_max_mm if c_max_mm is not None else (900.0 if kw.get("momentos_columna") or cargas.Mx_u or cargas.My_u else c_mm)
    mejor: Optional[tuple[float, DisenoConjunto]] = None
    extra = 0
    for c in np.arange(c_mm, tope + 1, 50.0):
        r = _buscar_para_c(float(c), cargas, suelo, **kw)
        if r is not None:
            if mejor is None or r[0] < mejor[0]:
                mejor = r
            extra += 1
            if extra > 2:
                break
        elif mejor is not None:
            extra += 1
            if extra > 2:
                break
    if mejor is None:
        return None
    d = mejor[1]
    if ruta_dxf is not None:
        exportar_dxf(d.zapata, d.pedestal.c_mm, d.h_pedestal_mm, ruta_dxf, titulo=f"Zapata+pedestal {d.exposicion} fc={d.fc:.0f} ceniza={d.x_ceniza:.0%}")
        d = DisenoConjunto(**{**d.__dict__, "ruta_dxf": str(ruta_dxf)})
    return d
