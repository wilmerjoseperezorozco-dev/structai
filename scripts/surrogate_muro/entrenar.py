"""Entrena el modelo dual del muro de contención: (1) factibilidad, (2) selector de tipología, (3) predictor geométrico por tipología (regresión de dimensiones y
clasificador de perfil). LightGBM. Guarda los boosters, el conjunto reservado (15 %) y las métricas en <salida>.

Uso:  python scripts/surrogate_muro/entrenar.py [--dataset data/surrogate_muro/dataset.csv] [--salida data/surrogate_muro/modelos] [--seed 7] [--hilos 4]
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
ESCENARIOS = {"bajo": (0.892, 1.00), "base": (1.010, 1.322), "alto": (1.15, 1.80)}
ENTRADAS = ["H", "phi", "gamma", "q_adm", "q_s", "beta", "a_max", "mult_concreto", "p_acero", "fe_cemento", "fe_acero", "H_tanphi", "kh"]
TIPOS = ["estandar", "dentellon", "bandeja"]
DIMS = {"estandar": ["h_zapata", "t_corona", "t_base", "b_puntera", "b_talon"], "dentellon": ["h_zapata", "t_corona", "t_base", "b_puntera", "b_talon", "dent_prof"],
        "bandeja": ["h_zapata", "t_corona", "t_base", "b_puntera", "b_talon", "band_y", "band_vuelo"]}
PARAMS = dict(n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=10, subsample=0.9, subsample_freq=1, colsample_bytree=0.9, verbose=-1)


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["fe_cemento"] = d["escenario_co2"].map(lambda s: ESCENARIOS[s][0])
    d["fe_acero"] = d["escenario_co2"].map(lambda s: ESCENARIOS[s][1])
    d["H_tanphi"] = d["H"] / np.tan(np.radians(d["phi"]))
    d["kh"] = 0.8 * d["a_max"]
    return d


def dividir(df: pd.DataFrame, seed: int, frac: float = 0.15) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))
    k = int(len(df) * frac)
    return df.iloc[idx[k:]], df.iloc[idx[:k]]


def entrenar(ent: pd.DataFrame, hilos: int) -> dict:
    X = ent[ENTRADAS]
    modelos: dict = {}
    modelos["viable"] = lgb.LGBMClassifier(**PARAMS, n_jobs=hilos).fit(X, (ent["ganadora"] != "ninguna").astype(int))
    v = ent[ent["ganadora"] != "ninguna"]
    modelos["tipo"] = lgb.LGBMClassifier(**PARAMS, n_jobs=hilos).fit(v[ENTRADAS], v["ganadora"].map({t: i for i, t in enumerate(TIPOS)}))
    for t in TIPOS:
        s = ent[ent[f"{t}_ok"] == 1]
        for dim in DIMS[t]:
            modelos[f"{t}__{dim}"] = lgb.LGBMRegressor(**PARAMS, n_jobs=hilos).fit(s[ENTRADAS], s[f"{t}_{dim}"])
        modelos[f"{t}__perfil"] = lgb.LGBMClassifier(**PARAMS, n_jobs=hilos).fit(s[ENTRADAS], (s[f"{t}_perfil"] == "parabolico").astype(int))
    return modelos


def metricas(mod: dict, res: pd.DataFrame) -> dict:
    X = res[ENTRADAS]
    out = {"n_reservado": len(res)}
    y = (res["ganadora"] != "ninguna").astype(int)
    out["viable_accuracy"] = float((mod["viable"].predict(X) == y).mean())
    out["viable_tasa_base"] = float(y.mean())
    v = res[res["ganadora"] != "ninguna"]
    pred = mod["tipo"].predict(v[ENTRADAS])
    real = v["ganadora"].map({t: i for i, t in enumerate(TIPOS)})
    out["tipo_accuracy"] = float((pred == real).mean())
    out["tipo_mayoritaria"] = float(real.value_counts(normalize=True).max())
    for t in TIPOS:
        s = res[res[f"{t}_ok"] == 1]
        if len(s) == 0:
            continue
        out[f"{t}_n"] = len(s)
        out[f"{t}_mae_m"] = {dim: float(np.abs(mod[f"{t}__{dim}"].predict(s[ENTRADAS]) - s[f"{t}_{dim}"]).mean()) for dim in DIMS[t]}
        out[f"{t}_perfil_accuracy"] = float((mod[f"{t}__perfil"].predict(s[ENTRADAS]) == (s[f"{t}_perfil"] == "parabolico").astype(int)).mean())
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "surrogate_muro" / "dataset.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_muro" / "modelos"))
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args()
    df = preparar(pd.read_csv(a.dataset))
    df = df[df["error"].isna() | (df["error"] == "")]
    ent, res = dividir(df, a.seed)
    mod = entrenar(ent, a.hilos)
    sal = Path(a.salida)
    sal.mkdir(parents=True, exist_ok=True)
    for k, m in mod.items():
        m.booster_.save_model(str(sal / f"{k}.txt"))
    res.to_csv(sal / "reservado.csv", index=False)
    met = metricas(mod, res) | {"n_entrenamiento": len(ent), "seed": a.seed}
    (sal / "resumen_entrenamiento.json").write_text(json.dumps(met, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(met, indent=2, ensure_ascii=False))
