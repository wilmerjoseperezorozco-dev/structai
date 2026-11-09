"""Transporte del acero de refuerzo: ¿cabe en mi vehículo, cuánto combustible y CO₂, y qué pasa si empalmo para que quepa?

Caso de uso: la ferretería vende varillas de 6 m; el plano pide piezas (p. ej. 185 cm) y el comprador tiene un vehículo con un largo de carga limitado
(moto, camioneta, camión). Opciones para cada pieza: (a) cortarla en la tienda si cabe en el vehículo; (b) llevar la varilla completa en un vehículo
más grande; (c) empalmar con traslapo NSR-10 para que cada tramo quepa, lo que gasta más acero y debe aprobarlo el ingeniero diseñador.

Datos con fuente (verificados en esta sesión; ver docs):
- Rendimiento diésel por tipología (ANDI 2018 vía UPME 2020, Tabla 6.1): camión 2 ejes 12,70 / 10,01 / 7,81 km/gal en terreno plano / ondulado /
  montañoso; tractocamión 2 ejes 8,76 / 6,76 / 5,07; 3 ejes 6,64 / 4,92 / 3,34. Carga liviana < 10 t, rutas urbanas de tres empresas (MinTransporte
  2019): 19,3 / 23,1 / 26,4 km/gal en diésel.
- Factores de CO₂ de combustión: diésel 10,2765 kgCO₂/gal (FECOC, tabla de la herramienta MVC, edición 2016, mezcla B10); EPA: 8,887 kg/gal gasolina y
  10,180 kg/gal diésel (combustible fósil puro; la gasolina colombiana es E10, así que el valor real es algo menor: sin ajustar).
SIN FUENTE (los aporta quien llama; no se inventan): rendimiento de moto/camioneta/NHR, largo de carga de cada vehículo, límites legales de carga
sobresaliente, precio del combustible y tarifa de flete.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .despiece_proyecto import dividir_con_traslapo, resolver_ilp
from .economia_concreto import FE
from .figuras_acero import traslapo_traccion_mm
from .viga import AREA_MM2

KG_CO2_GAL = {"diesel_fecoc": 10.2765, "diesel_epa": 10.180, "gasolina_epa": 8.887}
RENDIMIENTO_ANDI_KM_GAL = {
    "camion_2_ejes": {"plano": 12.70, "ondulado": 10.01, "montanoso": 7.81},
    "tractocamion_2_ejes": {"plano": 8.76, "ondulado": 6.76, "montanoso": 5.07},
    "tractocamion_3_ejes": {"plano": 6.64, "ondulado": 4.92, "montanoso": 3.34},
}
DENSIDAD_ACERO_KG_M3 = 7850.0


@dataclass(frozen=True)
class Vehiculo:
    nombre: str
    largo_carga_m: float            # largo máximo de pieza que puede llevar (incluye lo permitido sobresalir; lo declara quien llama)
    capacidad_kg: float
    rendimiento_km_gal: float
    kg_co2_gal: float
    fuente: str = "aportado por quien llama"


@dataclass(frozen=True)
class PlanTransporte:
    vehiculo: str
    estrategia: str
    varillas_compradas: int
    acero_kg: float
    acero_extra_kg: float           # por empalmes
    empalmes: int
    viajes: int
    co2_transporte_kg: float
    co2_acero_extra_kg: float
    galones: float
    advertencias: tuple[str, ...]

    @property
    def co2_total_kg(self) -> float:
        return self.co2_transporte_kg + self.co2_acero_extra_kg


def _kg_m(dia: str) -> float:
    return AREA_MM2[dia] * 1e-6 * DENSIDAD_ACERO_KG_M3


def planificar(piezas_m: Sequence[float], dia: str, v: Vehiculo, km_ida_vuelta: float, fc: float = 21.0, fy: float = 420.0,
               largo_varilla_m: float = 6.0, aceptar_empalmes: bool = False) -> PlanTransporte:
    """Plan para llevar `piezas_m` (longitudes de corte del despiece, en m) de barras #`dia`.

    Si todas caben en el vehículo, se cortan en la tienda (ILP sobre varillas de `largo_varilla_m`). Si alguna no cabe: sin `aceptar_empalmes` el
    plan es inviable y se advierte (hace falta un vehículo más largo o entrega a domicilio); con `aceptar_empalmes` se parten con traslapo de
    tracción NSR-10 clase B (C.12.15.1) hasta que cada tramo quepa. Una pieza de más de `largo_varilla_m` también exige empalme en cualquier vehículo.
    """
    adv: list[str] = []
    traslapo = traslapo_traccion_mm(dia, fc, fy) / 1000.0
    kg_m = _kg_m(dia)
    mayor = max(piezas_m)
    empalmes, extra_m = 0, 0.0
    if mayor <= v.largo_carga_m + 1e-9:
        estrategia = "corte en tienda"
        piezas = list(piezas_m)
    elif aceptar_empalmes:
        if v.largo_carga_m <= traslapo:
            raise ValueError("el traslapo exigido por la NSR-10 es mayor que el largo de carga: el empalme no reduce el tramo")
        estrategia = "empalmes para que quepa"
        piezas = []
        for p in piezas_m:
            partes = dividir_con_traslapo(p, v.largo_carga_m, traslapo)
            empalmes += len(partes) - 1
            extra_m += sum(partes) - p
            piezas.extend(partes)
        adv.append(f"{empalmes} empalmes con traslapo {traslapo * 1000:.0f} mm (clase B, C.12.15.1): requieren aprobación del diseñador, "
                   "ubicación fuera de zonas de máxima tracción y escalonamiento")
    else:
        estrategia = "inviable"
        piezas = []
        adv.append(f"hay piezas de {mayor:.2f} m y el vehículo lleva {v.largo_carga_m:.2f} m: necesita un vehículo de carga más largo, "
                   "entrega a domicilio, o autorizar empalmes (no se baja el traslapo de la NSR-10)")
    if piezas:
        barras, _ = resolver_ilp(piezas, [min(largo_varilla_m, max(piezas))] if estrategia != "corte en tienda" else [largo_varilla_m])
        n_varillas = sum(barras.values())
    else:
        n_varillas = 0
    acero_kg = sum(piezas) * kg_m if piezas else 0.0
    viajes = max(1, math.ceil(n_varillas * largo_varilla_m * kg_m / v.capacidad_kg)) if piezas else 0
    galones = viajes * km_ida_vuelta / v.rendimiento_km_gal
    return PlanTransporte(v.nombre, estrategia, n_varillas, acero_kg, extra_m * kg_m, empalmes, viajes,
                          galones * v.kg_co2_gal, extra_m * kg_m * FE["acero"], galones, tuple(adv))
