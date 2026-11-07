"""P1 banco C y C′ de PROTOCOLO_VALOR_INFORMATIVO.md: AUC espacial del modelo de susceptibilidad (gradient boosting, validación cruzada dejando fuera departamentos)
con sub-muestreo de las filas de ENTRENAMIENTO (E1 aleatoria, E2 estratificada por departamento y clase, E3 adelgazamiento por celdas de 0,1°) y ablación de capas.
No inferior: límite inferior del IC95 % (remuestreo de departamentos) de AUC_subconjunto − AUC_completo > −0,01. Uso: python p1_susceptibilidad.py"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FR = (0.02, 0.05, 0.10, 0.25, 0.50)
REPS, K_FOLDS, N_BOOT, DELTA_C = 3, 5, 150, 0.01
GRUPOS = {"relieve": ["elev", "pend", "curv"], "geologia": ["edad", "dist_falla_km"], "cobertura": ["cobertura"], "lluvia": ["lluvia_anual_mm"]}
TODAS = [c for g in GRUPOS.values() for c in g]


def cargar() -> pd.DataFrame:
    d = pd.read_csv(RAIZ / "scripts" / "satelite" / "susceptibilidad_muestras_wc.csv")
    d["edad"] = d["edad"].astype("category").cat.codes
    d["dep"] = (d["mun"].astype(int) // 1000).astype(int)
    return d.dropna(subset=["lon", "lat", "presencia"]).reset_index(drop=True)


def modelo(cols):
    cat = [c in ("edad", "cobertura") for c in cols]
    return HistGradientBoostingClassifier(max_iter=150, learning_rate=0.1, categorical_features=cat if any(cat) else None, random_state=0)


def indices_estrategia(est, d, idx_tr, f, rng):
    n = max(50, int(round(f * len(idx_tr))))
    if est == "E1":
        return rng.choice(idx_tr, n, replace=False)
    if est == "E2":
        g = d.loc[idx_tr, ["dep", "presencia"]].astype(int).astype(str).agg("-".join, axis=1).to_numpy(); sel = []
        for u in np.unique(g):
            ii = idx_tr[g == u]; k = max(1, int(round(f * len(ii)))); sel += rng.choice(ii, min(k, len(ii)), replace=False).tolist()
        return np.array(sel)
    cel = (np.floor(d.loc[idx_tr, "lon"] / 0.1).astype(int).astype(str) + "_" + np.floor(d.loc[idx_tr, "lat"] / 0.1).astype(int).astype(str)).to_numpy()
    orden = rng.permutation(len(idx_tr)); rango = pd.Series(cel[orden]).groupby(cel[orden]).cumcount().to_numpy()
    for m in range(1, 200):
        sel = idx_tr[orden[rango < m]]
        if len(sel) >= n:
            return sel if len(sel) == n else rng.choice(sel, n, replace=False)
    return idx_tr


def oof(d, cols, rep, est=None, f=1.0):
    rng = np.random.default_rng(1000 + rep); deps = np.unique(d.dep); rng.shuffle(deps)
    fold = {x: i % K_FOLDS for i, x in enumerate(deps)}; fd = d.dep.map(fold).to_numpy(); p = np.zeros(len(d))
    for k in range(K_FOLDS):
        tr, te = np.where(fd != k)[0], np.where(fd == k)[0]
        if est is not None and f < 1:
            tr = indices_estrategia(est, d, tr, f, np.random.default_rng(5000 + 17 * rep + k))
        m = modelo(cols).fit(d.loc[tr, cols], d.loc[tr, "presencia"]); p[te] = m.predict_proba(d.loc[te, cols])[:, 1]
    return p


def dif_ic(d, p_a, p_b, rng):
    y, dep = d.presencia.to_numpy(), d.dep.to_numpy(); u = np.unique(dep); ix = {x: np.where(dep == x)[0] for x in u}
    base = roc_auc_score(y, p_a) - roc_auc_score(y, p_b); b = []
    for _ in range(N_BOOT):
        s = np.concatenate([ix[x] for x in rng.choice(u, len(u))])
        if len(np.unique(y[s])) == 2:
            b.append(roc_auc_score(y[s], p_a[s]) - roc_auc_score(y[s], p_b[s]))
    return base, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main() -> None:
    d = cargar(); rng = np.random.default_rng(20261108)
    print(f"Muestras: {len(d)} ({int(d.presencia.sum())} con evento) en {d.dep.nunique()} departamentos; capas: {TODAS}", flush=True)
    comp = [oof(d, TODAS, r) for r in range(REPS)]
    aucs = [roc_auc_score(d.presencia, p) for p in comp]
    print(f"AUC espacial con todos los datos: {np.mean(aucs):.4f} (réplicas: {', '.join(f'{a:.4f}' for a in aucs)})", flush=True)
    res = {"completo": float(np.mean(aucs)), "filas": {}, "capas": {}}
    print("\nBanco C: ΔAUC (subconjunto − completo) con IC95 % por departamento, promedio de 3 réplicas; * = no inferior (límite inferior > −0,01)", flush=True)
    for est in ("E1", "E2", "E3"):
        for f in FR:
            ds = []
            for r in range(REPS):
                ds.append(dif_ic(d, oof(d, TODAS, r, est, f), comp[r], rng))
            m = np.mean(ds, axis=0); ok = m[1] > -DELTA_C; res["filas"][f"{est}|{f}"] = {"dif": float(m[0]), "lo": float(m[1]), "hi": float(m[2]), "no_inferior": bool(ok)}
            print(f"   {est} {100 * f:>4.0f} % de filas: Δ = {m[0]:+.4f} [{m[1]:+.4f}, {m[2]:+.4f}] {'*' if ok else ''}", flush=True)
    print("\nBanco C′: ablación de capas (datos completos)", flush=True)
    for g, cols in GRUPOS.items():
        resto = [c for c in TODAS if c not in cols]; ds = [dif_ic(d, oof(d, resto, r), comp[r], rng) for r in range(REPS)]
        m = np.mean(ds, axis=0); ok = m[1] > -DELTA_C; res["capas"][g] = {"dif": float(m[0]), "lo": float(m[1]), "hi": float(m[2]), "prescindible": bool(ok)}
        print(f"   sin {g:>9}: Δ = {m[0]:+.4f} [{m[1]:+.4f}, {m[2]:+.4f}] -> {'prescindible (no inferior)' if ok else 'aporta valor'}", flush=True)
    (AQUI / "p1_susceptibilidad_resultados.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
