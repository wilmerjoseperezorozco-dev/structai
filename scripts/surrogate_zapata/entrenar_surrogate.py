"""Entrena el sustituto LightGBM (geometría + mezcla) desde el dataset LHS y mide el costo/CO2 frente al óptimo exacto en un conjunto reservado.

El modelo NO decide la seguridad: `validar.py` verifica cada propuesta con el motor NSR-10 y repara o recurre al optimizador exacto.
Uso: python scripts/surrogate_zapata/entrenar_surrogate.py [--dataset data/surrogate_zapata/dataset.csv] [--salida data/surrogate_zapata/modelos]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]

ENTRADAS = ["Pu", "ey_x", "ex_y", "q_adm", "ks", "fc", "Df", "c_col", "mult_concreto", "p_acero", "p_encofrado", "p_ceniza", "fe_cemento", "fe_acero",
            "lam_co2", "exp_cod"]
# objetivos continuos (regresión) y de clase (clasificación)
OBJ_REG = ["L", "h_c", "h_e", "c_ped"]
OBJ_CLS = ["x_ceniza_cod", "fc_cod"]
EXP_COD = {"interior_C1_S0": 0, "costa_C2_S1_sin_ensayo": 1, "costa_C2_S1_con_ensayo": 2}
X_VALORES = [0.0, 0.1, 0.2, 0.25]
FC_VALORES = [21.0, 28.0, 35.0]


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["ok"] == 1].copy()
    df["exp_cod"] = df["exposicion_in"].map(EXP_COD)
    df["x_ceniza_cod"] = df["x_ceniza"].map(lambda v: X_VALORES.index(round(float(v), 2)))
    df["fc_cod"] = df["fc_eff"].map(lambda v: FC_VALORES.index(float(v)))
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "surrogate_zapata" / "dataset.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_zapata" / "modelos"))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)

    crudo = pd.read_csv(args.dataset)
    df = preparar(crudo)
    print(f"{len(crudo)} filas, {len(df)} con solución ({100 * len(df) / len(crudo):.1f} %)")
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(df))
    n_te = int(0.15 * len(df))
    te, tr = df.iloc[idx[:n_te]], df.iloc[idx[n_te:]]
    te.to_csv(out / "reservado.csv", index=False)

    resumen: dict = {"n_total": len(crudo), "n_resueltos": len(df), "n_entrenamiento": len(tr), "n_reservado": len(te), "metricas": {}}
    for obj in OBJ_REG:
        m = lgb.LGBMRegressor(n_estimators=600, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1, colsample_bytree=0.9,
                              random_state=args.seed, verbose=-1)
        m.fit(tr[ENTRADAS], tr[obj])
        p = m.predict(te[ENTRADAS])
        mae = float(np.mean(np.abs(p - te[obj])))
        within = float(np.mean(np.abs(p - te[obj]) <= 50))
        resumen["metricas"][obj] = {"MAE_mm": round(mae, 1), "dentro_de_50mm": round(within, 3)}
        m.booster_.save_model(str(out / f"{obj}.txt"))
        print(f"{obj}: MAE {mae:.1f} mm, ±50 mm {100 * within:.1f} %")
    for obj in OBJ_CLS:
        m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, random_state=args.seed, verbose=-1)
        m.fit(tr[ENTRADAS], tr[obj])
        acc = float(np.mean(m.predict(te[ENTRADAS]) == te[obj]))
        resumen["metricas"][obj] = {"exactitud": round(acc, 3)}
        m.booster_.save_model(str(out / f"{obj}.txt"))
        print(f"{obj}: exactitud {100 * acc:.1f} %")
    (out / "resumen_entrenamiento.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
