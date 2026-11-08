"""V1: verificaciones POSTERIORES al analisis preregistrado (no preregistradas). Ver RESULTADOS_V1.md.

Lee v1_panel.csv (generado por v1_analisis.py). Imprime: razon de momios del mecanismo por region, el
analisis P2 solo dentro del Caribe y la distribucion de la exposicion vial por region.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.contingency_tables import StratifiedTable

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
p = pd.read_csv(AQUI / "v1_panel.csv")
p["log_area"] = np.log(p["area_km2"])

print("P1: razon de momios de Mantel-Haenszel (lugar en terreno bajo | cerca de via vs lejos), por region")
for reg, d in p.groupby("region"):
    t = [np.array([[r["_bajo_cerca"], r["_cerca"] - r["_bajo_cerca"]], [r["_bajo_lejos"], r["_lejos"] - r["_bajo_lejos"]]])
         for _, r in d.iterrows() if r["_cerca"] > 0 and r["_lejos"] > 0]
    st = StratifiedTable(t)
    lo, hi = st.oddsratio_pooled_confint()
    print(f"  {reg:<10} OR={st.oddsratio_pooled:.2f} [{lo:.2f}, {hi:.2f}] municipios={len(t)}")

cov = ["expo_vial", "frac_hand", "pct_cabecera", "pct_mat_vulnerable", "nbi2018", "lluvia_p95", "log_area"]


def ajustar(d, cols):
    x = d.dropna(subset=cols + ["viv_danadas"])
    X = sm.add_constant(pd.concat([x[cols], pd.get_dummies(x["depto"], prefix="d", drop_first=True).astype(float)], axis=1))
    r = sm.GLM(x["viv_danadas"], X, family=sm.families.Poisson(), offset=np.log(x["poblacion"])).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(x["depto"])[0]})
    return r, len(x)


c = p[p["region"] == "Caribe"]
r0, n = ajustar(c, cov)
r1, _ = ajustar(c, cov + ["lug_bajo_cerca", "cab_bajo_en_via"])
for nombre, r in (("sin mecanismo", r0), ("con mecanismo", r1)):
    b, se = r.params["expo_vial"], r.bse["expo_vial"]
    print(f"P2 solo Caribe, {nombre}: n={n} RR por +0,10 = {np.exp(b * .1):.2f} [{np.exp((b - 1.96 * se) * .1):.2f}, {np.exp((b + 1.96 * se) * .1):.2f}]")

print("Exposicion vial por region (mediana y cuartiles) y fraccion de HAND municipal mediana:")
print(p.groupby("region").agg(expo_med=("expo_vial", "median"), expo_q1=("expo_vial", lambda s: s.quantile(.25)),
                              expo_q3=("expo_vial", lambda s: s.quantile(.75)), hand_med=("frac_hand", "median"),
                              n=("codigo", "count")).round(2))
