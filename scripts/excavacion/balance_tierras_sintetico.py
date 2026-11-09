"""Balance de tierras con DATOS SINTÉTICOS (inventados; validan la tubería, no son un proyecto). Con fuente: factor de emisión del diésel (FECOC) y rendimiento km/gal
de la volqueta sencilla del catálogo de flota (rango del catálogo, contrastado con ANDI 2018). El factor de ACPM por m³-km supone viaje cargado de ida y vacío de vuelta al mismo rendimiento. Sin fuente: volúmenes, distancias, tarifas, esponjamiento, capacidad suelta, costo por m³-km."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
from src.excavacion_balance import Problema, combustible_gal_por_m3_km, resolver_balance  # noqa: E402
from src.excavacion_metricas import tasa_reutilizacion  # noqa: E402
from src.flota_construccion import CATALOGO  # noqa: E402
from src.transporte_acero import KG_CO2_GAL  # noqa: E402

S = {"sintetico": True, "cortes_m3": (4000.0, 2500.0, 1500.0), "aprovechable_base": (0.7, 0.4, 0.1), "demandas_m3": (3000.0, 1200.0),
     "d_corte_relleno_km": ((0.5, 1.5), (1.2, 0.8), (2.0, 1.0)), "d_corte_botadero_km": ((12.0,), (10.0,), (11.0,)), "tarifa_botadero_cop_m3": (6000.0,),
     "d_prestamo_relleno_km": ((8.0, 9.0),), "precio_prestamo_cop_m3": (28000.0,), "costo_cop_m3_km": 1500.0, "capacidad_suelta_m3": 6.0, "esponjamiento": 0.25}


def correr(aprov, precio_prestamo, objetivo, d_cr=None, d_pr=None):
    p = Problema(S["cortes_m3"], aprov, S["demandas_m3"], d_cr or S["d_corte_relleno_km"], (1e9,), S["d_corte_botadero_km"], S["tarifa_botadero_cop_m3"], (1e9,),
                 d_pr or S["d_prestamo_relleno_km"], (precio_prestamo,), S["costo_cop_m3_km"])
    pl = resolver_balance(p, objetivo)
    gal = pl.m3_km * combustible_gal_por_m3_km(S["capacidad_suelta_m3"], CATALOGO["C2_sencillo"].km_gal_medio(), S["esponjamiento"])
    return {"costo_millones_cop": round(pl.costo_cop / 1e6, 2), "reutilizacion_pct": round(pl.reutilizacion_pct, 1), "m3_km": round(pl.m3_km), "gal_acpm": round(gal),
            "kgco2e": round(gal * KG_CO2_GAL["diesel_fecoc"]), "prestamo_m3": round(float(pl.z.sum())), "botadero_m3": round(float(pl.y.sum()))}


def main() -> None:
    res = {"sintetico": True, "entradas": S, "escenarios": {}}
    for nombre, aprov, precio in (("base", S["aprovechable_base"], 28000.0), ("suelo_malo (aprovechable/2)", tuple(a / 2 for a in S["aprovechable_base"]), 28000.0),
                                  ("prestamo_barato (8.000)", S["aprovechable_base"], 8000.0), ("prestamo_caro (60.000)", S["aprovechable_base"], 60000.0)):
        res["escenarios"][nombre] = {obj: correr(aprov, precio, obj) for obj in ("costo", "reutilizacion")}
    # relleno 2 lejano (25 km desde todos los cortes) y préstamo cercano (3 km): el costo y la reutilización dejan de coincidir
    lejano = ((0.5, 25.0), (1.2, 25.0), (2.0, 25.0))
    res["escenarios"]["relleno_2_lejano_y_prestamo_cercano"] = {obj: correr(S["aprovechable_base"], 8000.0, obj, lejano, ((8.0, 3.0),)) for obj in ("costo", "reutilizacion")}
    destino = RAIZ / "data" / "excavacion" / "balance_tierras_sintetico.json"
    destino.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=list), encoding="utf-8")
    for k, v in res["escenarios"].items():
        print(k, v)
    print("cota de reutilización (oferta aprovechable/total):", round(100 * sum(a * c for a, c in zip(S["aprovechable_base"], S["cortes_m3"])) / sum(S["cortes_m3"]), 1), "% ; demanda/total corte:", round(100 * sum(S["demandas_m3"]) / sum(S["cortes_m3"]), 1), "%")
    print("chequeo función de métricas:", tasa_reutilizacion(8000.0, 4000 * .7 + 2500 * .4 + 1500 * .1, 4200.0))


if __name__ == "__main__":
    main()
