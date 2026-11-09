"""Catálogo paramétrico de vehículos de carga para obra (A4: transporte) y viajes discretos.

ESTADO DE LOS DATOS (verificado en esta sesión):
- Rendimiento diésel con fuente: ANDI 2018 vía UPME 2020 (Tabla 6.1): camión 2 ejes 12,70/10,01/7,81 km/gal (plano/ondulado/montañoso),
  tractocamión 2 ejes 8,76/6,76/5,07, tractocamión 3 ejes 6,64/4,92/3,34. Camión liviano < 10 t urbano: 19,3–26,4 km/gal (MinTransporte 2019).
- CO₂ de combustión del diésel: 10,2765 kg/gal (FECOC 2016, B10) o 10,180 (EPA).
- Las filas del catálogo vienen de una tabla aportada por el usuario (origen sin citar): carga útil y rangos de km/gal por configuración. Cuando existe
  un dato con fuente para esa clase se contrasta (ver `contraste_con_fuentes`); C3/mixer y volqueta no tienen fuente de rendimiento: `verificado=False`.
- NO obtenido: la tabla vigente de pesos brutos y dimensiones de la Resolución 4100 de 2004 (la copia consultada es escaneada; la Resolución 2501 de
  2002, con otra tabla, está derogada), la clasificación 'NTC 4788' (no se pudo confirmar), la tabla de consumo del SICE-TAC y el parque de carga por
  municipio del RUNT (se solicita por la concesión).
La emisión por tonelada-kilómetro supone viaje cargado ida y retorno vacío con el mismo rendimiento (hipótesis conservadora, sin medir).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .transporte_acero import KG_CO2_GAL, RENDIMIENTO_ANDI_KM_GAL, Vehiculo

DENSIDAD_CONCRETO_T_M3 = 2.4
FACTOR_TERRENO = {      # rendimiento relativo al plano, de ANDI 2018 (camión 2 ejes y tractocamión 3 ejes)
    "camion": {"plano": 1.0, "ondulado": 10.01 / 12.70, "montanoso": 7.81 / 12.70},
    "tractocamion": {"plano": 1.0, "ondulado": 4.92 / 6.64, "montanoso": 3.34 / 6.64},
}


@dataclass(frozen=True)
class ConfigCarga:
    codigo: str
    nombre: str
    carga_util_t: tuple[float, float]
    km_gal: tuple[float, float]
    uso: str
    clase_terreno: str            # clave de FACTOR_TERRENO
    verificado: bool = False

    def km_gal_medio(self) -> float:
        return sum(self.km_gal) / 2.0

    def carga_media_t(self) -> float:
        return sum(self.carga_util_t) / 2.0

    def a_vehiculo(self, largo_carga_m: float, kg_co2_gal: float = KG_CO2_GAL["diesel_fecoc"], terreno: str = "plano") -> Vehiculo:
        """Vehículo para `transporte_acero.planificar`. El largo de carga lo aporta quien llama (no hay fuente)."""
        return Vehiculo(self.nombre, largo_carga_m, self.carga_media_t() * 1000.0, self.km_gal_medio() * FACTOR_TERRENO[self.clase_terreno][terreno],
                        kg_co2_gal, "tabla aportada por el usuario" + ("" if self.verificado else " (sin verificar)"))


CATALOGO: dict[str, ConfigCarga] = {
    "C2_liviano": ConfigCarga("C2", "Camión liviano NHR/NPR", (2.5, 4.5), (14.0, 18.0), "acero figurado urbano, cemento en sacos, ferretería", "camion"),
    "C2_sencillo": ConfigCarga("C2", "Volqueta sencilla", (7.0, 8.5), (9.0, 11.0), "agregados, excavación urbana", "camion"),
    "C3": ConfigCarga("C3", "Doble troque / mixer 7–8 m³", (15.0, 17.0), (6.0, 8.0), "concreto premezclado, agregados masivos", "camion"),
    "minimula": ConfigCarga("2S2/2S3", "Minimula", (18.0, 22.0), (5.5, 7.0), "acero corrugado regional, cemento paletizado", "tractocamion"),
    "tractomula": ConfigCarga("3S2/3S3", "Tractomula", (32.0, 35.0), (4.5, 6.0), "acero desde siderúrgica, cemento a granel", "tractocamion"),
}


def emision_por_km(cfg: ConfigCarga, kg_co2_gal: float = KG_CO2_GAL["diesel_fecoc"]) -> float:
    return kg_co2_gal / cfg.km_gal_medio()


def emision_por_ton_km(cfg: ConfigCarga, kg_co2_gal: float = KG_CO2_GAL["diesel_fecoc"]) -> float:
    """kg CO₂ por tonelada-km con el vehículo cargado a su carga media (sin retorno vacío)."""
    return emision_por_km(cfg, kg_co2_gal) / cfg.carga_media_t()


def contraste_con_fuentes(cfg: ConfigCarga) -> str | None:
    """Compara el rango km/gal del catálogo con el rango de ANDI 2018 (plano a montañoso) cuando hay dato; None si no hay fuente."""
    ref = {"C2_sencillo": "camion_2_ejes", "minimula": "tractocamion_2_ejes", "tractomula": "tractocamion_3_ejes"}
    clave = next((k for k, c in CATALOGO.items() if c is cfg), None)
    if clave not in ref:
        return None
    r = RENDIMIENTO_ANDI_KM_GAL[ref[clave]]
    lo, hi = min(r.values()), max(r.values())
    dentro = lo - 1e-9 <= cfg.km_gal[0] and cfg.km_gal[1] <= hi + 1e-9
    return f"ANDI 2018: {lo:.2f}–{hi:.2f} km/gal; catálogo {cfg.km_gal[0]}–{cfg.km_gal[1]}: {'dentro' if dentro else 'fuera'} del rango"


def viajes(masa_t: float, capacidad_t: float) -> int:
    """Función escalón: viajes enteros para mover `masa_t` en vehículos de `capacidad_t` (cada viaje paga el recorrido completo)."""
    if capacidad_t <= 0 or masa_t < 0:
        raise ValueError("capacidad positiva y masa no negativa")
    return max(1, math.ceil(masa_t / capacidad_t - 1e-12)) if masa_t > 0 else 0


def viajes_mixer(volumen_m3: float, capacidad_m3: float = 8.0, densidad_t_m3: float = DENSIDAD_CONCRETO_T_M3) -> int:
    """Viajes de mixer (por volumen; la masa es solo control de carga). Capacidad útil de un mixer: la declara quien llama."""
    if volumen_m3 < 0 or capacidad_m3 <= 0:
        raise ValueError("volumen no negativo y capacidad positiva")
    return viajes(volumen_m3 * densidad_t_m3, capacidad_m3 * densidad_t_m3)


def co2_viajes(n_viajes: int, km_ida_vuelta: float, cfg: ConfigCarga, kg_co2_gal: float = KG_CO2_GAL["diesel_fecoc"], terreno: str = "plano") -> float:
    km_gal = cfg.km_gal_medio() * FACTOR_TERRENO[cfg.clase_terreno][terreno]
    return n_viajes * km_ida_vuelta / km_gal * kg_co2_gal
