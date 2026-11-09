"""Calibra las incertidumbres de precio (sigma lognormal) por familia a partir de datos, no de rangos inventados.

sigma_total² = sigma_localizacion² + sigma_fuente² + sigma_tiempo² (+ sigma_especificacion² donde se declara)
- localizacion: rango intercuartil entre las 140 provincias INVIAS / 1,349 (catálogo construir_catalogo.py).
- fuente: ln(máx/mín) / 4 entre contratos locales de Barranquilla/Puerto Colombia (consulta 2026-11-08, ver OBSERVACIONES_LOCALES).
- tiempo: desviación estándar de la variación anual (log) del índice ICOCED de Barranquilla AM para el insumo (indices_dane.py), horizonte de proyecto de 12 meses.
- especificacion: SUPUESTO declarado solo para el anclaje (la receta INVIAS 623,1 es en roca; en suelo cambia rendimiento y longitud fija).
Salida: data/precios_elementos/distribuciones_precios.json (lo consume packages/motor-concreto/src/precios_distribucion.py).
Uso:  python scripts/precios/calibrar_distribuciones.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "data" / "precios_elementos"
Z_IQR = 1.349

# familia -> (ítem del catálogo, insumo ICOCED, (mín, máx) de contratos locales o None, sigma de especificación)
FAMILIAS = {
    "acero": ("acero de refuerzo", "Acero corrugado", (4979.0, 7388.0), 0.0),
    "concreto": ("concreto estructural premezclado (630,1,1)", "Concreto común", (772_000.0, 947_000.0), 0.0),
    "perforacion_anclaje": ("anclaje activo postensado en roca (por m perforado)", "Servicios de preliminares y cimentación", None, 0.25),
}
OBSERVACIONES_LOCALES = "acero 4.979–7.388 COP/kg y concreto 28 MPa 772–947 mil COP/m³ en contratos de Barranquilla/Puerto Colombia (consulta SQL 2026-11-08)"


def _sigma_tiempo(ind: pd.DataFrame, insumo: str, dominio: str = "Barranquilla AM") -> float:
    s = ind[(ind["dominio"] == dominio) & (ind["insumo"] == insumo)].sort_values("periodo")["indice"].to_numpy()
    if len(s) < 14:
        return float("nan")
    dif = np.log(s[12:] / s[:-12])
    return float(np.std(dif, ddof=1))


def calibrar() -> dict:
    cat = pd.read_csv(DATOS / "catalogo_precios_2026-1.csv").set_index("item")
    ind = pd.read_csv(DATOS / "indices_icoced.csv")
    salida = {}
    for fam, (item, insumo, obs, sigma_esp) in FAMILIAS.items():
        s_loc = float(cat.loc[item, "rango_intercuartil_rel"]) / Z_IQR
        s_fuente = math.log(obs[1] / obs[0]) / 4.0 if obs else 0.0
        s_tiempo = _sigma_tiempo(ind, insumo)
        s_tiempo = 0.0 if math.isnan(s_tiempo) else s_tiempo
        total = math.sqrt(s_loc**2 + s_fuente**2 + s_tiempo**2 + sigma_esp**2)
        salida[fam] = {"mediana_catalogo": float(cat.loc[item, "ref_0802"]), "sigma_localizacion": round(s_loc, 4), "sigma_fuente": round(s_fuente, 4),
                       "sigma_tiempo": round(s_tiempo, 4), "sigma_especificacion": sigma_esp, "sigma_total": round(total, 4), "insumo_icoced": insumo}
    # variación anual de referencia (última disponible) para indexar a la fecha del proyecto
    ult = ind["periodo"].max()
    previo = f"{int(ult[:4]) - 1}-{ult[5:]}"
    for fam in ("acero", "concreto"):
        ins = salida[fam]["insumo_icoced"]
        s = ind[(ind["dominio"] == "Barranquilla AM") & (ind["insumo"] == ins)].set_index("periodo")["indice"]
        salida[fam]["variacion_anual_ultimo_periodo"] = round(float(s[ult] / s[previo] - 1.0), 4)
    return {"periodo_indices": ult, "observaciones_locales": OBSERVACIONES_LOCALES, "familias": salida}


if __name__ == "__main__":
    r = calibrar()
    (DATOS / "distribuciones_precios.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(r, indent=2, ensure_ascii=False))
