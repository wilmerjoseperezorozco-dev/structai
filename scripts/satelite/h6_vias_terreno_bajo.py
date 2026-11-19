"""H6 (#273): ¿la fracción de la red vial principal en terreno bajo (HAND < 10 m) predice las vías averiadas por
eventos hídricos que reporta la UNGRD?

Protocolo: PROTOCOLO_ANALISIS.md §32 (fijado antes de cruzar exposición vial con daño vial).
Predictor: expo_vial del panel V1 = km de vía troncal/primaria/secundaria (OSM) con HAND < 10 m / km totales (≥ 5 km).
Resultado: vías averiadas en eventos hídricos (inundación, creciente súbita, avenida torrencial), UNGRD 2019-2024,
por 100 km de vía principal.
Uso:
  python -I h6_vias_terreno_bajo.py --conteo   # muestra y predictor; no cruza con el daño vial
  python -I h6_vias_terreno_bajo.py            # análisis -> h6_vias_resultados.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h3_socavacion_puentes as h3  # noqa: E402

SALIDA = AQUI / "h6_vias_resultados.json"
RHO_MIN = 0.10
h3.RNG = np.random.default_rng(2766)


def preparar():
    ins = h3.insumos()
    h3.ANIOS_PREDICTOR = (2019, 2022)
    panel, _, ung = h3.preparar(ins)            # índice H3 con historial 2019-2022 (versión validada)
    panel = panel[panel["expo_vial"].notna() & (panel["km_via"] >= 5)].copy()
    ung["vias_averiadas"] = pd.to_numeric(ung["vias_averiadas"], errors="coerce").fillna(0)
    hid = ung[ung["ev"].isin(h3.HIDRICOS)]

    def suma(df, a0, a1):
        d = df[df["anio"].between(a0, a1)]
        return panel["codigo"].map(d.groupby("codigo_municipio")["vias_averiadas"].sum()).fillna(0).values

    panel["R_19_24"] = suma(hid, 2019, 2024)
    panel["R_23_24"] = suma(hid, 2023, 2024)
    inc = ung[ung["ev"].str.contains("INCENDIO FORESTAL", na=False) & ung["anio"].between(2019, 2024)]
    panel["n_incendio_forestal"] = panel["codigo"].map(inc.groupby("codigo_municipio").size()).fillna(0).values
    panel["y1"] = np.log1p(panel["R_19_24"] / panel["km_via"] * 100)
    panel["y2"] = np.log1p(panel["R_23_24"] / panel["km_via"] * 100)
    panel["log_km_via"] = np.log(panel["km_via"])
    return panel.reset_index(drop=True)


def parcial(p, x, y, ctrl):
    return float(h3.parcial(p[x].values, p[y].values, p[ctrl].values))


def bloque(p, fun):
    b = p["depto2"].values
    return h3.boot(lambda ix: fun(p.iloc[ix].reset_index(drop=True)), b)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = preparar()
    if "--conteo" in sys.argv:
        print(f"municipios con ≥ 5 km de vía principal: {len(p)}, departamentos {p['depto2'].nunique()}, "
              f"por región {p['region'].value_counts().to_dict()}")
        print("expo_vial p10/p50/p90:", np.percentile(p["expo_vial"], [10, 50, 90]).round(3),
              "| por región (mediana):", p.groupby("region")["expo_vial"].median().round(3).to_dict())
        print("ρ(expo_vial, pendiente p90):", round(float(spearmanr(p["expo_vial"], p["S"])[0]), 2),
              "| ρ(expo_vial, índice H3):", round(float(spearmanr(p["expo_vial"], p["indice"])[0]), 2))
        return
    c1 = ["log_pob", "P_A", "log_km_via", "S"]
    c2 = ["indice", "log_pob", "P_A", "log_km_via"]
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §32", "n": len(p), "n_deptos": int(p["depto2"].nunique()),
           "municipios_con_dano_vial_hidrico": int((p["R_19_24"] > 0).sum())}
    v = parcial(p, "expo_vial", "y1", c1)
    ic = bloque(p, lambda q: parcial(q, "expo_vial", "y1", c1))
    out["C1"] = {"rho_parcial": v, "ic95": ic,
                 "veredicto": "CONFIRMADA" if (ic[0] > 0 and v >= RHO_MIN) else
                              ("REFUTADA" if ic[1] < RHO_MIN else "NO CONCLUYENTE")}
    v2 = parcial(p, "expo_vial", "y2", c2)
    ic2 = bloque(p, lambda q: parcial(q, "expo_vial", "y2", c2))
    out["C2_mas_alla_de_H3"] = {"rho_parcial": v2, "ic95": ic2,
                                "veredicto": "AGREGA" if ic2[0] > 0 else ("NO AGREGA" if ic2[1] < RHO_MIN else
                                                                          "NO CONCLUYENTE")}
    out["A0_rho_bruto"] = float(spearmanr(p["expo_vial"], p["y1"])[0])
    yb = (p["R_23_24"] > 0).astype(int).values
    out["auc_2023_2024"] = {k: {"valor": float(h3.auc(p[k].values, yb)),
                                "ic95": h3.boot(lambda ix, k=k: h3.auc(p[k].values[ix], yb[ix]), p["depto2"].values)}
                            for k in ("expo_vial", "indice")}
    comb = (rankdata(p["expo_vial"]) / len(p) + rankdata(p["indice"]) / len(p)) / 2
    out["auc_2023_2024"]["indice_mas_expo"] = {"valor": float(h3.auc(comb, yb))}
    out["control_negativo_incendio_forestal"] = {
        "rho_parcial": parcial(p.assign(yn=np.log1p(p["n_incendio_forestal"])), "expo_vial", "yn", c1)}
    out["por_region"] = {}
    for r, g in p.groupby("region"):
        g = g.reset_index(drop=True)
        if len(g) >= 30:
            out["por_region"][r] = {"n": len(g), "rho_parcial": parcial(g, "expo_vial", "y1", c1),
                                    "ic95": bloque(g, lambda q: parcial(q, "expo_vial", "y1", c1))
                                    if g["depto2"].nunique() >= 3 else None}
    p["tercil_S"] = pd.qcut(p["S"], 3, labels=["llano", "medio", "montañoso"])
    out["por_tercil_pendiente"] = {str(t): {"n": len(g), "rho_parcial": parcial(g.reset_index(drop=True), "expo_vial",
                                                                                "y1", ["log_pob", "P_A", "log_km_via"])}
                                   for t, g in p.groupby("tercil_S", observed=True)}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
