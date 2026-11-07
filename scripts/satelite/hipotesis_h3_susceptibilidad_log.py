"""H3 (protocolo §23): susceptibilidad con variables continuas en logaritmo frente a la regresión logística del §22.

Candidata: logit p = b0 + b1·log(1 + pendiente) + b2·log(1 + distancia a falla) + clases de edad geológica.
Línea base: la logística del §22 (pendiente, curvatura y log(1 + distancia) continuas + edad). Métrica: AUC dejando un departamento fuera;
mejora si el IC95 % (bootstrap de bloques por departamento, 2.000 réplicas) de ΔAUC excluye 0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pesos_evidencia_mm as pe  # noqa: E402  (modelo_logit, MIN_PRES_DEPTO, N_BOOT, RNG)


def main() -> None:
    df = pe.preparar(pd.read_csv(AQUI / "susceptibilidad_muestras.csv", dtype={"mun": str}))
    df["depto"] = df.mun.str[:2]
    df["logpend"] = np.log1p(df.pend)
    y = df.presencia.to_numpy()
    cuenta = df[df.presencia == 1].groupby("depto").size()
    evaluables = sorted(cuenta[cuenta >= pe.MIN_PRES_DEPTO].index)
    base, cand, ctrl = np.full(len(df), np.nan), np.full(len(df), np.nan), np.full(len(df), np.nan)
    for d in evaluables:
        te = (df.depto == d).to_numpy(); tr = ~te
        base[te] = pe.modelo_logit(["pend", "curv", "logfalla"], ["edad"]).fit(df[tr], y[tr]).predict_proba(df[te])[:, 1]
        cand[te] = pe.modelo_logit(["logpend", "logfalla"], ["edad"]).fit(df[tr], y[tr]).predict_proba(df[te])[:, 1]
        ctrl[te] = pe.modelo_logit(["pend", "logfalla"], ["edad"]).fit(df[tr], y[tr]).predict_proba(df[te])[:, 1]   # control EXPLORATORIO: sin curvatura y sin log(pendiente)
    ev = df.depto.isin(evaluables).to_numpy()
    a_b, a_c = roc_auc_score(y[ev], base[ev]), roc_auc_score(y[ev], cand[ev])
    dept = df.depto.to_numpy()
    dif = []
    for _ in range(pe.N_BOOT):
        sel = pe.RNG.choice(evaluables, len(evaluables), replace=True)
        idx = np.concatenate([np.where(dept == d)[0] for d in sel])
        dif.append(roc_auc_score(y[idx], cand[idx]) - roc_auc_score(y[idx], base[idx]))
    lo, hi = np.percentile(dif, [2.5, 97.5])
    dif_a = np.array(dif)
    pval = float(min(1.0, 2 * min((np.sum(dif_a <= 0) + 1) / (pe.N_BOOT + 1), (np.sum(dif_a >= 0) + 1) / (pe.N_BOOT + 1))))
    veredicto = "MEJORA" if lo > 0 else ("PEOR" if hi < 0 else "sin diferencia demostrada")
    print(f"H3: AUC espacial línea base (§22) {a_b:.3f}; candidata log {a_c:.3f}; ΔAUC = {a_c - a_b:+.4f} IC95% [{lo:+.4f}, {hi:+.4f}] -> {veredicto}")
    a_k = roc_auc_score(y[ev], ctrl[ev])
    print(f"   [exploratorio, no entra a la familia] control lineal sin curvatura: AUC {a_k:.3f}; candidata − control = {a_c - a_k:+.4f}  "
          f"(la candidata cambia DOS cosas respecto de la línea base: usa log y omite la curvatura; el control separa cuánto viene de cada una)")
    por_region = {}
    for r, ds in pe.REGIONES.items():
        m = ev & np.isin(dept, ds.split())
        if m.sum() and 0 < y[m].sum() < m.sum():
            por_region[r] = (float(roc_auc_score(y[m], base[m])), float(roc_auc_score(y[m], cand[m])))
            print(f"   {r:<10} base {por_region[r][0]:.3f} | candidata {por_region[r][1]:.3f}")
    (AQUI / "hipotesis_h3.json").write_text(json.dumps({"auc_base": a_b, "auc_cand": a_c, "dif": a_c - a_b, "ic": [float(lo), float(hi)],
                                                         "veredicto": veredicto, "p": pval, "auc_control_sin_curvatura": a_k, "por_region": por_region}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
