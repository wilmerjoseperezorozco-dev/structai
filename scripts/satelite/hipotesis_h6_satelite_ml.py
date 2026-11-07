"""§24: cobertura del suelo (WorldCover) + gradiente boosting frente a la logística del §22, AUC dejando un departamento fuera.

E1: AUC(B1) − AUC(B0) > 0   (B1 = B0 + cobertura + lluvia anual media)
E2: AUC(G1) − AUC(B1) > 0   (G1 = gradiente boosting con las variables de B1)
Holm (α = 0,05) sobre E1 y E2. Descriptivo: G0 − B0, AUC por región, importancia por permutación de G1.
Requiere susceptibilidad_muestras_wc.csv (agregar_cobertura_worldcover.py).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pesos_evidencia_mm as pe  # noqa: E402  (preparar, modelo_logit, REGIONES, MIN_PRES_DEPTO, N_BOOT, RNG)

HGB = dict(max_iter=200, max_depth=4, learning_rate=0.05, random_state=20261107)


def preparar_wc(df: pd.DataFrame) -> pd.DataFrame:
    d = pe.preparar(df)
    d["loglluvia"] = np.log1p(d.lluvia_anual_mm.fillna(d.lluvia_anual_mm.median()))
    d["cob"] = d.cobertura.fillna(0).astype(int).astype(str)
    d["depto"] = d.mun.str[:2]
    return d


def tabla_gbm(d: pd.DataFrame, num: list[str], cat: list[str]) -> pd.DataFrame:
    x = d[num].copy()
    for c in cat:
        x[c] = pd.Categorical(d[c].astype(str), categories=sorted(d[c].astype(str).unique()))
    return x


def p_boot(v: np.ndarray) -> float:
    n = len(v)
    return float(min(1.0, 2 * min((np.sum(v <= 0) + 1) / (n + 1), (np.sum(v >= 0) + 1) / (n + 1))))


def main() -> None:
    d = preparar_wc(pd.read_csv(AQUI / "susceptibilidad_muestras_wc.csv", dtype={"mun": str}))
    y = d.presencia.to_numpy()
    cuenta = d[d.presencia == 1].groupby("depto").size()
    evaluables = sorted(cuenta[cuenta >= pe.MIN_PRES_DEPTO].index)
    num0, cat0 = ["pend", "curv", "logfalla"], ["edad"]
    num1, cat1 = num0 + ["loglluvia"], cat0 + ["cob"]
    X_g0, X_g1 = tabla_gbm(d, num0, cat0), tabla_gbm(d, num1, cat1)
    oof = {k: np.full(len(d), np.nan) for k in ("B0", "B1", "G0", "G1")}
    print(f"Muestras {len(d)} (presencias {int(y.sum())}); departamentos evaluables: {len(evaluables)}; cobertura faltante: {int(d.cobertura.isna().sum())}", flush=True)
    for k, dep in enumerate(evaluables):
        te = (d.depto == dep).to_numpy(); tr = ~te
        oof["B0"][te] = pe.modelo_logit(num0, cat0).fit(d[tr], y[tr]).predict_proba(d[te])[:, 1]
        oof["B1"][te] = pe.modelo_logit(num1, cat1).fit(d[tr], y[tr]).predict_proba(d[te])[:, 1]
        g0 = HistGradientBoostingClassifier(categorical_features="from_dtype", **HGB).fit(X_g0[tr], y[tr])
        g1 = HistGradientBoostingClassifier(categorical_features="from_dtype", **HGB).fit(X_g1[tr], y[tr])
        oof["G0"][te] = g0.predict_proba(X_g0[te])[:, 1]; oof["G1"][te] = g1.predict_proba(X_g1[te])[:, 1]
        print(f"  {k + 1}/{len(evaluables)} {dep}", flush=True)
    ev = d.depto.isin(evaluables).to_numpy(); dept = d.depto.to_numpy()
    auc = {k: float(roc_auc_score(y[ev], v[ev])) for k, v in oof.items()}
    print("\nAUC espacial (predicciones agrupadas): " + ", ".join(f"{k} {v:.3f}" for k, v in auc.items()))
    difs = {"E1 B1-B0": [], "E2 G1-B1": [], "G0-B0 (descriptivo)": []}
    for _ in range(pe.N_BOOT):
        sel = pe.RNG.choice(evaluables, len(evaluables), replace=True)
        idx = np.concatenate([np.where(dept == dd)[0] for dd in sel])
        a = {k: roc_auc_score(y[idx], v[idx]) for k, v in oof.items()}
        difs["E1 B1-B0"].append(a["B1"] - a["B0"]); difs["E2 G1-B1"].append(a["G1"] - a["B1"]); difs["G0-B0 (descriptivo)"].append(a["G0"] - a["B0"])
    res = {"auc": auc}
    pv = {}
    for nombre, v in difs.items():
        v = np.array(v); lo, hi = np.percentile(v, [2.5, 97.5])
        pt = {"E1 B1-B0": auc["B1"] - auc["B0"], "E2 G1-B1": auc["G1"] - auc["B1"], "G0-B0 (descriptivo)": auc["G0"] - auc["B0"]}[nombre]
        pv[nombre] = p_boot(v)
        res[nombre] = {"dif": float(pt), "ic": [float(lo), float(hi)], "p": pv[nombre]}
        print(f"{nombre:<22} Δ = {pt:+.4f} IC95% [{lo:+.4f}, {hi:+.4f}]  p = {pv[nombre]:.4f}")
    orden = sorted([("E1 B1-B0", pv["E1 B1-B0"]), ("E2 G1-B1", pv["E2 G1-B1"])], key=lambda kv: kv[1]); sigue = True
    print("\nHolm (α = 0,05) sobre E1 y E2:")
    for i, (n, p) in enumerate(orden):
        aj = min(1.0, p * (len(orden) - i)); rech = sigue and aj < 0.05; sigue = rech
        res[n]["p_holm"] = aj; res[n]["significativo_holm"] = bool(rech)
        print(f"  {n}: p = {p:.4f}, p ajustado = {aj:.4f} -> {'SIGNIFICATIVO' if rech else 'no significativo'}")
    print("\nAUC por región natural (B0 / B1 / G0 / G1):")
    for r, ds in pe.REGIONES.items():
        m = ev & np.isin(dept, ds.split())
        if m.sum() and 0 < y[m].sum() < m.sum():
            print(f"  {r:<10} " + " / ".join(f"{roc_auc_score(y[m], oof[k][m]):.3f}" for k in ("B0", "B1", "G0", "G1")))
    # importancia por permutación de G1 en un departamento reservado grande
    gran = cuenta.idxmax(); te = (d.depto == gran).to_numpy()
    g1 = HistGradientBoostingClassifier(categorical_features="from_dtype", **HGB).fit(X_g1[~te], y[~te])
    imp = permutation_importance(g1, X_g1[te], y[te], scoring="roc_auc", n_repeats=3, random_state=1)
    res["importancia_G1"] = {c: float(m) for c, m in zip(X_g1.columns, imp.importances_mean)}
    print(f"\nImportancia por permutación de G1 (caída de AUC) con el departamento {gran} reservado:")
    for c, m in sorted(res["importancia_G1"].items(), key=lambda kv: -kv[1]):
        print(f"  {c:<10} {m:+.4f}")
    (AQUI / "hipotesis_h6.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
