"""Comparación de alternativas de excavación con DATOS SINTÉTICOS (no medidos, no de obra). Valida la tubería de cálculo, NO produce una recomendación de obra.

Todas las alternativas se analizan con las MISMAS hipótesis: sobrecarga `sobrecarga_kpa` en la corona y grieta de tracción seca (conservador); el único valor no calculado es la Pf de la contención (supuesto declarado). El costo de la consecuencia es POR METRO DE FRENTE afectado (misma base que los costos por metro). El factor de emisión del diésel es el de FECOC (con fuente); el resto de entradas es inventado.
Todo parámetro de ENTRADA de abajo es inventado para el ejercicio y se marca en la salida con "sintetico": true.
El motor (Bishop, Tabla H.2.4-1, métricas) es el real; los números de salida solo valen para esos supuestos.
La contención es un voladizo con empujes de Rankine (ver excavacion_contencion.py); su probabilidad de falla es un SUPUESTO sintético, no un cálculo.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
from src.transporte_acero import KG_CO2_GAL  # noqa: E402
from src.excavacion_contencion import dimensionar_voladizo  # noqa: E402
from src.excavacion_estabilidad import SueloExc, angulo_maximo_seguro, factor_seguridad_requerido, perfil_talud  # noqa: E402
from src.excavacion_metricas import costo_riesgo_geotecnico, indice_eficiencia_geometrica, intensidad_energetica  # noqa: E402

SINTETICO = {
    "altura_m": 6.0, "ancho_fondo_m": 10.0, "distancia_lindero_m": 8.0,
    "suelo": {"gamma": 18.0, "c_kpa": 10.0, "phi_deg": 27.0}, "cov_c": 0.30, "cov_tan_phi": 0.10,
    "costo_consecuencia_cop_por_m": 400e6, "precio_excavacion_cop_m3": 25000.0,
    "sobrecarga_kpa": 10.0, "fs_pasivo": 1.5, "h_max_voladizo_m": 6.0, "empotramiento_min_m": 1.0, "factor_longitud_pantalla": 1.3, "holgura_trabajo_m": 0.5,
    "precio_pantalla_cop_m2": 600000.0, "prob_falla_contencion": 0.005,
    "consumo_gal_h": 6.0, "rendimiento_m3_h": 40.0, "factor_kgco2e_gal": KG_CO2_GAL["diesel_fecoc"],
}


def area_excavada(perfil, altura: float, ancho_fondo: float) -> float:
    xs, ys = perfil.xs[1:-1], perfil.ys[1:-1]
    cuña = sum(0.5 * ((altura - ys[i]) + (altura - ys[i + 1])) * (xs[i + 1] - xs[i]) for i in range(len(xs) - 1))
    return cuña + ancho_fondo * altura


def evaluar(nombre: str, angulo: float, bermas: tuple, d: dict) -> dict:
    s = SueloExc(**d["suelo"])
    p = perfil_talud(d["altura_m"], angulo, bermas)
    area, area_proy = area_excavada(p, d["altura_m"], d["ancho_fondo_m"]), d["ancho_fondo_m"] * d["altura_m"]
    r = costo_riesgo_geotecnico(d["altura_m"], angulo, s, d["cov_c"], d["cov_tan_phi"], d["costo_consecuencia_cop_por_m"], bermas=bermas, sobrecarga_kpa=d["sobrecarga_kpa"], grieta_traccion=True) 
    inten = intensidad_energetica(d["consumo_gal_h"], d["rendimiento_m3_h"], d["factor_kgco2e_gal"])
    costo_exc = area * d["precio_excavacion_cop_m3"]
    return {"alternativa": nombre, "angulo_deg": round(angulo, 1), "bermas": bermas, "retiro_horizontal_m": round(p.x_cresta, 2),
            "cabe_en_predio": p.x_cresta <= d["distancia_lindero_m"], "ieg": round(indice_eficiencia_geometrica(area_proy, area), 3),
            "area_m2_por_m": round(area, 1), "gal_acpm_por_m_long": round(area * inten.gal_por_m3, 1), "kgco2e_por_m_long": round(area * inten.kg_co2e_por_m3, 0),
            "costo_excavacion_cop_por_m": round(costo_exc), "fs_medio": round(r.fs_medio, 2) if r else None, "prob_falla": round(r.prob_falla, 4) if r else None,
            "costo_riesgo_cop_por_m": round(r.costo_riesgo) if r else None,
            "costo_total_cop_por_m": round(costo_exc + r.costo_riesgo) if r else None}


def evaluar_contencion(d: dict) -> dict:
    s = SueloExc(**d["suelo"])
    pan = dimensionar_voladizo(s, d["altura_m"], d["sobrecarga_kpa"], d["fs_pasivo"], d["h_max_voladizo_m"], d["empotramiento_min_m"], factor_longitud=d["factor_longitud_pantalla"])
    if pan.requiere_apoyos:
        return {"alternativa": "contención temporal en voladizo", "nota": "excede la altura máxima de voladizo: requiere apoyos (no dimensionado)"}
    area_proy, area = d["ancho_fondo_m"] * d["altura_m"], (d["ancho_fondo_m"] + d["holgura_trabajo_m"]) * d["altura_m"]
    inten = intensidad_energetica(d["consumo_gal_h"], d["rendimiento_m3_h"], d["factor_kgco2e_gal"])
    costo_exc, costo_pan = area * d["precio_excavacion_cop_m3"], pan.longitud_total_m * d["precio_pantalla_cop_m2"]
    riesgo = d["prob_falla_contencion"] * d["costo_consecuencia_cop_por_m"]
    return {"alternativa": "contención temporal en voladizo", "angulo_deg": 90.0, "retiro_horizontal_m": d["holgura_trabajo_m"], "cabe_en_predio": d["holgura_trabajo_m"] <= d["distancia_lindero_m"],
            "ieg": round(indice_eficiencia_geometrica(area_proy, area), 3), "area_m2_por_m": round(area, 1), "gal_acpm_por_m_long": round(area * inten.gal_por_m3, 1),
            "kgco2e_por_m_long": round(area * inten.kg_co2e_por_m3, 0), "empotramiento_m": round(pan.empotramiento_m, 2), "longitud_pantalla_m": round(pan.longitud_total_m, 2),
            "momento_max_knm_por_m": round(pan.momento_max_knm_por_m, 1), "costo_excavacion_cop_por_m": round(costo_exc), "costo_pantalla_cop_por_m": round(costo_pan),
            "prob_falla": d["prob_falla_contencion"], "prob_falla_es_supuesto": True, "costo_riesgo_cop_por_m": round(riesgo), "costo_total_cop_por_m": round(costo_exc + costo_pan + riesgo)}


def main() -> None:
    d = SINTETICO
    s = SueloExc(**d["suelo"])
    req = factor_seguridad_requerido("construccion", False, "efectivo")
    amax = angulo_maximo_seguro(d["altura_m"], s, req, sobrecarga_kpa=d["sobrecarga_kpa"], grieta_traccion=True)
    filas = [evaluar("talud al máximo seguro (FS construcción 1,25)", amax, (), d)]
    for ang in (45.0, 35.0):
        filas.append(evaluar(f"talud {ang:.0f}°", ang, (), d))
    filas.append(evaluar(f"talud {amax:.0f}° con berma de 2 m a media altura", amax, ((d["altura_m"] / 2, 2.0),), d))
    filas.append(evaluar_contencion(d))
    viables = sorted((f for f in filas if f.get("cabe_en_predio") and f.get("costo_total_cop_por_m") is not None), key=lambda f: f["costo_total_cop_por_m"])
    ranking = [f["alternativa"] for f in viables]
    # sensibilidad: Pf de la contención que la empata con la mejor alternativa de talud (la Pf de la contención es supuesto, no cálculo)
    cont = next((f for f in filas if f["alternativa"].startswith("contención") and "costo_total_cop_por_m" in f), None)
    taludes = [f for f in viables if f is not cont]
    pf_empate = None
    if cont and taludes:
        sin_riesgo = cont["costo_total_cop_por_m"] - cont["costo_riesgo_cop_por_m"]
        margen = taludes[0]["costo_total_cop_por_m"] - sin_riesgo
        pf_empate = margen / d["costo_consecuencia_cop_por_m"] if margen > 0 else None        # None: aun con Pf = 0 la contención cuesta más que el mejor talud
    salida = {"sintetico": True, "aviso": "Entradas inventadas para validar la tubería; no usar para decisiones de obra.", "entradas": d, "fs_requerido": req, "ranking_por_costo_total_entre_las_que_caben": ranking, "pf_contencion_que_empata_con_el_mejor_talud": pf_empate, "resultados": filas}
    destino = RAIZ / "data" / "excavacion" / "comparacion_sintetica.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in filas:
        print(f)
    print("RANKING:", ranking, "Pf de empate de la contención:", pf_empate)


if __name__ == "__main__":
    main()
