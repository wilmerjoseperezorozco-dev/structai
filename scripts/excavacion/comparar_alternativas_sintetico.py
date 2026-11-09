"""Comparación de alternativas de excavación con DATOS SINTÉTICOS (no medidos, no de obra). Valida la tubería de cálculo, NO produce una recomendación de obra.

Todo parámetro de ENTRADA de abajo es inventado para el ejercicio y se marca en la salida con "sintetico": true.
El motor (Bishop, Tabla H.2.4-1, métricas) es el real; los números de salida solo valen para esos supuestos.
La contención temporal no está dimensionada en esta fase: se lista sin costo y no entra al ranking.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
from src.excavacion_estabilidad import SueloExc, angulo_maximo_seguro, factor_seguridad_requerido, perfil_talud  # noqa: E402
from src.excavacion_metricas import costo_riesgo_geotecnico, indice_eficiencia_geometrica, intensidad_energetica  # noqa: E402

SINTETICO = {
    "altura_m": 6.0, "ancho_fondo_m": 10.0, "distancia_lindero_m": 8.0,
    "suelo": {"gamma": 18.0, "c_kpa": 10.0, "phi_deg": 27.0}, "cov_c": 0.30, "cov_tan_phi": 0.10,
    "costo_consecuencia_cop": 400e6, "precio_excavacion_cop_m3": 25000.0,
    "consumo_gal_h": 6.0, "rendimiento_m3_h": 40.0, "factor_kgco2e_gal": 10.0,
}


def area_excavada(perfil, altura: float, ancho_fondo: float) -> float:
    xs, ys = perfil.xs[1:-1], perfil.ys[1:-1]
    cuña = sum(0.5 * ((altura - ys[i]) + (altura - ys[i + 1])) * (xs[i + 1] - xs[i]) for i in range(len(xs) - 1))
    return cuña + ancho_fondo * altura


def evaluar(nombre: str, angulo: float, bermas: tuple, d: dict) -> dict:
    s = SueloExc(**d["suelo"])
    p = perfil_talud(d["altura_m"], angulo, bermas)
    area, area_proy = area_excavada(p, d["altura_m"], d["ancho_fondo_m"]), d["ancho_fondo_m"] * d["altura_m"]
    r = costo_riesgo_geotecnico(d["altura_m"], angulo, s, d["cov_c"], d["cov_tan_phi"], d["costo_consecuencia_cop"], grieta_traccion=False) if not bermas else None
    inten = intensidad_energetica(d["consumo_gal_h"], d["rendimiento_m3_h"], d["factor_kgco2e_gal"])
    costo_exc = area * d["precio_excavacion_cop_m3"]
    return {"alternativa": nombre, "angulo_deg": round(angulo, 1), "bermas": bermas, "retiro_horizontal_m": round(p.x_cresta, 2),
            "cabe_en_predio": p.x_cresta <= d["distancia_lindero_m"], "ieg": round(indice_eficiencia_geometrica(area_proy, area), 3),
            "area_m2_por_m": round(area, 1), "gal_acpm_por_m_long": round(area * inten.gal_por_m3, 1), "kgco2e_por_m_long": round(area * inten.kg_co2e_por_m3, 0),
            "costo_excavacion_cop_por_m": round(costo_exc), "fs_medio": round(r.fs_medio, 2) if r else None, "prob_falla": round(r.prob_falla, 4) if r else None,
            "costo_riesgo_cop_por_m": round(r.costo_riesgo) if r else None,
            "costo_total_cop_por_m": round(costo_exc + r.costo_riesgo) if r else None}


def main() -> None:
    d = SINTETICO
    s = SueloExc(**d["suelo"])
    req = factor_seguridad_requerido("construccion", False, "efectivo")
    amax = angulo_maximo_seguro(d["altura_m"], s, req, grieta_traccion=False)
    filas = [evaluar("talud al máximo seguro (FS construcción 1,25)", amax, (), d)]
    for ang in (45.0, 35.0):
        filas.append(evaluar(f"talud {ang:.0f}°", ang, (), d))
    filas.append({"alternativa": "contención temporal (entibado/pantalla)", "nota": "sin dimensionar en esta fase; no entra al ranking"})
    salida = {"sintetico": True, "aviso": "Entradas inventadas para validar la tubería; no usar para decisiones de obra.", "entradas": d, "fs_requerido": req, "resultados": filas}
    destino = RAIZ / "data" / "excavacion" / "comparacion_sintetica.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in filas:
        print(f)


if __name__ == "__main__":
    main()
