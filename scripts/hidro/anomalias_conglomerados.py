"""Recalcula C1 y C2 de PROTOCOLO_ANOMALIAS.md con bootstrap por departamento (conglomerados) en lugar de por estación.
Motivo: las estaciones de una región comparten buena parte de la señal (ver coherencia_anomalias.py). Uso: python anomalias_conglomerados.py"""
import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
R = pd.read_csv(AQUI / "anomalias_por_estacion.csv", index_col=0, dtype={"Unnamed: 0": str}); R.index = R.index.astype(str).str.zfill(10)
m = pd.DataFrame(json.loads((AQUI / "_cache" / "estaciones_meta.json").read_text(encoding="utf-8"))).set_index("codigo"); m.index = m.index.astype(str)
norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper().strip()
d = np.array([norm(m.loc[c, "departamento"]) for c in R.index]); u = np.unique(d); idx = {x: np.where(d == x)[0] for x in u}
rng = np.random.default_rng(20261109)
pv = lambda b: min(1.0, 2 * min((np.sum(b <= 0) + 1) / (len(b) + 1), (np.sum(b >= 0) + 1) / (len(b) + 1)))
res = {}
for nombre, a, b in (("C1 M1-B0", "M1_2.0", "B0_2.0"), ("C2 M2-M1", "M2_2.0", "M1_2.0")):
    dif = (R[a] - R[b]).to_numpy(float)
    est = np.array([dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(4000)])
    cl = np.array([dif[np.concatenate([idx[x] for x in rng.choice(u, len(u))])].mean() for _ in range(4000)])
    res[nombre] = {"dif": float(dif.mean()), "ic_estaciones": np.percentile(est, [2.5, 97.5]).tolist(), "p_estaciones": pv(est),
                   "ic_departamentos": np.percentile(cl, [2.5, 97.5]).tolist(), "p_departamentos": pv(cl), "mejoran": float((dif > 0).mean())}
orden = sorted(res, key=lambda k: res[k]["p_departamentos"])
for i, k in enumerate(orden):
    res[k]["p_holm_departamentos"] = min(1.0, res[k]["p_departamentos"] * (len(orden) - i))
    print(k, json.dumps(res[k]))
(AQUI / "anomalias_conglomerados.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
