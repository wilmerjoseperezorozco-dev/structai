"""F1 (continuación): clasifica los tramos utilizables por potencia instalable estimada con los umbrales legales verificados.
P_inst = 9,81 · eta(0,7) · Q_p30 mensual escalado · H  (Q de diseño del protocolo: percentil 30; eta del protocolo: 0,7).
Clases: <1 MW (autogeneración a pequeña escala, Res. UPME 281/2015), 1-10 MW (tope de pequeños aprovechamientos antes de la Ley 2294/2023),
10-50 MW (pequeños aprovechamientos desde la Ley 2294/2023, art. 235), >=50 MW (fuera de la definición). Referencia de práctica: 20 MW (no legal)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
ETA = 0.7
CORTES_KW = [0, 1000, 10000, 50000, np.inf]
ETIQ = ["<1 MW", "1-10 MW", "10-50 MW", ">=50 MW"]

d = pd.read_csv(AQUI / "f1_tramos.csv", dtype={"codigo": str})
out = {}
for long_km in (1.0, 2.0, 5.0):
    x = d[(d.long_km == long_km) & d.utilizable & d.en_rango].copy()
    x["P_inst_kW"] = 9.81 * ETA * x.q_p30 * x.ratio_area.clip(upper=1) * x.H_m
    x["clase"] = pd.cut(x.P_inst_kW, CORTES_KW, labels=ETIQ, right=False)
    n_cuencas = d[d.long_km == long_km].codigo.nunique()
    r = {"tramos_utilizables_en_rango": int(len(x)), "tramos_por_clase": {k: int(v) for k, v in x.clase.value_counts().reindex(ETIQ).items()},
         "cuencas_con_al_menos_un_tramo_en_clase": {k: int(x[x.clase == k].codigo.nunique()) for k in ETIQ},
         "cuencas_con_tramo_1_a_50MW": int(x[(x.P_inst_kW >= 1000) & (x.P_inst_kW < 50000)].codigo.nunique()),
         "cuencas_con_tramo_1_a_20MW_practica": int(x[(x.P_inst_kW >= 1000) & (x.P_inst_kW < 20000)].codigo.nunique()),
         "cuencas_total": int(n_cuencas)}
    r["por_region_cuencas_con_tramo_1_a_50MW"] = {k: int(v) for k, v in x[(x.P_inst_kW >= 1000) & (x.P_inst_kW < 50000)].groupby("region").codigo.nunique().items()}
    out[str(long_km)] = r
(AQUI / "f1_clasificacion_legal.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(out["2.0"], indent=1, ensure_ascii=False)); print({k: v["cuencas_con_tramo_1_a_50MW"] for k, v in out.items()})
