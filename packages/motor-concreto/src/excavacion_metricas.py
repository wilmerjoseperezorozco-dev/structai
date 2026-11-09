"""Métricas de la excavación (Fase 1a). Cada una con su definición exacta; los datos externos (consumos, factores de emisión,
esponjamiento, variabilidad del suelo, costo de la consecuencia) son argumentos obligatorios: el módulo no trae cifras por defecto.

1. IEG  = A_proyecto / A_excavada            (adimensional, 0 < IEG <= 1; por metro de longitud, volumen en banco)
2. Intensidad = consumo_gal_h / rendimiento_m3_h            [gal ACPM/m³ banco]
                kg CO2e/m³ = gal/m³ x factor_kgco2e_por_gal  (factor del usuario; citar su fuente, p. ej. factores de emisión UPME)
3. Reutilización = min(V_aprovechable, V_demanda_relleno) / V_excavado x 100        [% en banco]
4. Costo de riesgo geotécnico = Pf x costo_consecuencia           [moneda]; Pf por FOSM + log-normal sobre FS (Bishop)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

from .excavacion_estabilidad import SueloExc, factor_seguridad_talud, perfil_talud


def indice_eficiencia_geometrica(area_proyecto_m2: float, area_excavada_m2: float) -> float:
    if area_proyecto_m2 <= 0 or area_excavada_m2 < area_proyecto_m2:
        raise ValueError("el área excavada debe ser >= el área de proyecto > 0")
    return area_proyecto_m2 / area_excavada_m2


@dataclass(frozen=True)
class Intensidad:
    gal_por_m3: float
    kg_co2e_por_m3: float


def intensidad_energetica(consumo_gal_h: float, rendimiento_m3_h: float, factor_kgco2e_por_gal: float) -> Intensidad:
    if consumo_gal_h < 0 or rendimiento_m3_h <= 0 or factor_kgco2e_por_gal < 0:
        raise ValueError("consumo y factor >= 0; rendimiento > 0")
    gal = consumo_gal_h / rendimiento_m3_h
    return Intensidad(gal, gal * factor_kgco2e_por_gal)


def tasa_reutilizacion(v_excavado_banco: float, v_aprovechable_banco: float, v_demanda_relleno_banco: float) -> float:
    """% del volumen excavado (en banco) que se reutiliza en sitio: limitado por lo aprovechable y por lo que el proyecto necesita rellenar."""
    if v_excavado_banco <= 0 or v_aprovechable_banco < 0 or v_demanda_relleno_banco < 0 or v_aprovechable_banco > v_excavado_banco:
        raise ValueError("volúmenes inconsistentes")
    return 100.0 * min(v_aprovechable_banco, v_demanda_relleno_banco) / v_excavado_banco


@dataclass(frozen=True)
class RiesgoGeotecnico:
    fs_medio: float
    cov_fs: float
    beta: float
    prob_falla: float
    costo_riesgo: float


def costo_riesgo_geotecnico(altura: float, angulo_deg: float, suelo: SueloExc, cov_c: float, cov_tan_phi: float, costo_consecuencia: float,
                            **kw) -> RiesgoGeotecnico:
    """FOSM: varianza de FS por diferencias finitas en c y tan(phi) (independientes), FS ~ log-normal; Pf = Phi(-beta_LN). Los COV los aporta el usuario (ensayos del sitio)."""
    if cov_c < 0 or cov_tan_phi < 0 or costo_consecuencia < 0:
        raise ValueError("COV y costo >= 0")
    p = perfil_talud(altura, angulo_deg)
    fs0 = factor_seguridad_talud(p, suelo, **kw).fs
    tphi = math.tan(math.radians(suelo.phi_deg))
    var = 0.0
    if suelo.c_kpa > 0 and cov_c > 0:
        d = 0.05 * suelo.c_kpa
        s = SueloExc(suelo.gamma, suelo.c_kpa + d, suelo.phi_deg, suelo.gamma_sat)
        dfs = (factor_seguridad_talud(p, s, **kw).fs - fs0) / d
        var += (dfs * cov_c * suelo.c_kpa) ** 2
    if tphi > 0 and cov_tan_phi > 0:
        phi2 = math.degrees(math.atan(tphi * 1.05))
        dfs = (factor_seguridad_talud(p, SueloExc(suelo.gamma, suelo.c_kpa, phi2, suelo.gamma_sat), **kw).fs - fs0) / (0.05 * tphi)
        var += (dfs * cov_tan_phi * tphi) ** 2
    cov = math.sqrt(var) / fs0 if fs0 > 0 else float("inf")
    if cov == 0:
        pf = 0.0 if fs0 > 1 else 1.0
        return RiesgoGeotecnico(fs0, 0.0, float("inf") if fs0 > 1 else 0.0, pf, pf * costo_consecuencia)
    s_ln = math.sqrt(math.log(1 + cov * cov))
    beta = math.log(fs0 / math.sqrt(1 + cov * cov)) / s_ln
    pf = NormalDist().cdf(-beta)
    return RiesgoGeotecnico(fs0, cov, beta, pf, pf * costo_consecuencia)
