"""No estacionariedad espacial y transferibilidad. Protocolo: PROTOCOLO_NO_ESTACIONARIEDAD.md"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f as fdist
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regionalizacion_validacion as rv  # noqa: E402

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
MIN_DOM = 30
PRED = ["lA", "lP", "lS"]


def ajustar(tr: pd.DataFrame, y: np.ndarray, te: pd.Series) -> float:
    X = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in PRED])
    b, _ = rv.ols(X, y)
    return float(b @ np.array([1.0] + [te[c] for c in PRED]))


def dominio_kmeans(tr: pd.DataFrame, te: pd.Series, k: int):
    cols = ["lP", "lS", "lH"]
    mu, sd = tr[cols].mean(), tr[cols].std(ddof=0).replace(0, 1)
    km = KMeans(n_clusters=k, n_init=5, random_state=0).fit(((tr[cols] - mu) / sd).values)
    zt = ((te[cols].astype(float) - mu) / sd).values.reshape(1, -1)
    return km.labels_, int(km.predict(zt)[0])


def predecir(tr: pd.DataFrame, te: pd.Series, obj: str, completo: bool) -> dict:
    y = np.log(tr[obj].values)
    out = {"M2": ajustar(tr, y, te)}
    m = (tr["region"] == te["region"]).values
    out["M5a"] = ajustar(tr[m], y[m], te) if m.sum() >= MIN_DOM else out["M2"]
    if completo:
        for k in (3, 4):
            lab, c = dominio_kmeans(tr, te, k)
            mk = lab == c
            out[f"M5b_k{k}"] = ajustar(tr[mk], y[mk], te) if mk.sum() >= MIN_DOM else out["M2"]
        rf = RandomForestRegressor(n_estimators=300, max_depth=6, random_state=0, n_jobs=1)
        rf.fit(tr[PRED + ["lH"]].values, y)
        out["R"] = float(rf.predict(te[PRED + ["lH"]].astype(float).values.reshape(1, -1))[0])
    return out


def validar(d: pd.DataFrame, obj: str, buffer_km: float, completo: bool) -> pd.DataFrame:
    filas = []
    for i, te in d.iterrows():
        lejos = np.array([rv.km(te["lat"], te["lon"], r.lat, r.lon) >= buffer_km for r in d.itertuples()])
        otra = np.array([not (isinstance(te["corriente"], str) and isinstance(c, str) and te["corriente"].strip().upper() == c.strip().upper()) for c in d["corriente"]])
        tr = d[lejos & otra & (d.index != i)]
        if len(tr) < 20 or not (te[obj] > 0):
            continue
        for m, lq in predecir(tr, te, obj, completo).items():
            filas.append({"i": i, "region": te["region"], "bloque": te["bloque"], "modelo": m, "eps": lq - math.log(te[obj]), "dentro_ic90": np.nan})
    return pd.DataFrame(filas)


def loro(d: pd.DataFrame, obj: str) -> dict:
    out = {}
    for reg in d["region"].unique():
        tr, te = d[d["region"] != reg], d[d["region"] == reg]
        y = np.log(tr[obj].values)
        e = np.array([ajustar(tr, y, r) - math.log(r[obj]) for _, r in te.iterrows() if r[obj] > 0])
        out[reg] = {"n": int(len(e)), "factor_tipico": float(math.exp(np.median(np.abs(e)))), "sesgo_factor": float(math.exp(np.median(e)))}
    return out


def coef_por_dominio(d: pd.DataFrame, obj: str) -> dict:
    out = {}
    for reg, g in list(d.groupby("region")) + [("Nacional", d)]:
        if len(g) < 15:
            out[reg] = {"n": int(len(g)), "nota": "n < 15, sin ajuste"}
            continue
        X = np.column_stack([np.ones(len(g))] + [g[c].values for c in PRED])
        y = np.log(g[obj].values)
        b, res = rv.ols(X, y)
        bl = g["bloque"].values
        et = np.unique(bl)
        idx = {k: np.where(bl == k)[0] for k in et}
        bs = []
        for _ in range(1000):
            ii = np.concatenate([idx[k] for k in rv.RNG.choice(et, len(et), replace=True)])
            if len(ii) > 6:
                bs.append(rv.ols(X[ii], y[ii])[0])
        ic = np.percentile(np.array(bs), [2.5, 97.5], axis=0)
        out[reg] = {"n": int(len(g)), **{n: {"v": float(b[k]), "ic95": [float(ic[0, k]), float(ic[1, k])]} for k, n in enumerate(["const", "lnA", "lnP", "lnS"])}}
    return out


def prueba_f(d: pd.DataFrame, obj: str) -> dict:
    y = np.log(d[obj].values)
    X0 = np.column_stack([np.ones(len(d))] + [d[c].values for c in PRED])
    regs = [r for r in d["region"].unique() if (d["region"] == r).sum() >= 15]
    dd = d[d["region"].isin(regs)]
    y = np.log(dd[obj].values)
    X0 = np.column_stack([np.ones(len(dd))] + [dd[c].values for c in PRED])
    cols = [X0]
    for r in regs[1:]:
        m = (dd["region"] == r).values.astype(float)
        cols.append(np.column_stack([m] + [m * dd[c].values for c in PRED]))
    X1 = np.column_stack(cols)
    s0, s1 = np.sum(rv.ols(X0, y)[1] ** 2), np.sum(rv.ols(X1, y)[1] ** 2)
    df1, df2 = X1.shape[1] - X0.shape[1], len(y) - X1.shape[1]
    F = ((s0 - s1) / df1) / (s1 / df2)
    return {"regiones": regs, "F": float(F), "df": [df1, df2], "p_orientativo": float(1 - fdist.cdf(F, df1, df2)),
            "aviso": "no valida como prueba formal: estaciones autocorrelacionadas en el espacio"}


def main() -> None:
    d = rv.cargar()
    d["lH"] = np.log(d["elev_media_m"].clip(lower=1))
    R = {"n": int(len(d)), "por_region": d["region"].value_counts().to_dict()}
    val10 = validar(d, "q10", 50.0, True)
    R["val_T10"] = rv.resumen(val10)
    for m in ("M5a", "M5b_k3", "M5b_k4", "R"):
        R[f"dif_{m}-M2_T10"] = rv.dif_pareada(val10, m, "M2")
    # C2: sesgo regional de M2
    c2 = {}
    v2 = val10[val10["modelo"] == "M2"]
    for reg, g in v2.groupby("region"):
        bl = g["bloque"].values
        et = np.unique(bl)
        idx = {k: np.where(bl == k)[0] for k in et}
        e = g["eps"].values
        bs = [np.median(e[np.concatenate([idx[k] for k in rv.RNG.choice(et, len(et), replace=True)])]) for _ in range(2000)]
        ic = np.percentile(bs, [2.5, 97.5])
        fb = math.exp(np.median(e))
        c2[reg] = {"n": int(len(e)), "sesgo_factor": fb, "ic95_factor": [math.exp(ic[0]), math.exp(ic[1])],
                   "falla": bool((ic[0] > 0 or ic[1] < 0) and not (0.67 <= fb <= 1.5)),
                   "factor_tipico": float(math.exp(np.median(np.abs(e))))}
    R["C2_sesgo_regional_M2_T10"] = c2
    R["coef_por_dominio_T10"] = coef_por_dominio(d, "q10")
    R["F_T10"] = prueba_f(d, "q10")
    R["LORO_T10"] = loro(d, "q10")
    for T in (2, 5, 25, 50):
        v = validar(d, f"q{T}", 50.0, False)
        R[f"val_T{T}"] = rv.resumen(v)
        R[f"dif_M5a-M2_T{T}"] = rv.dif_pareada(v, "M5a", "M2")
    for nombre, buf, obj, filt in (("buf0", 0.0, "q10", None), ("buf100", 100.0, "q10", None), ("LP3", 50.0, "qlp10", None), ("A_le_2000", 50.0, "q10", d["area_km2"] <= 2000)):
        dd = d if filt is None else d[filt].reset_index(drop=True)
        v = validar(dd, obj, buf, False)
        R[f"sens_{nombre}"] = {"M2": rv.resumen(v[v.modelo == "M2"])["M2"]["factor_tipico"], "M5a": rv.resumen(v[v.modelo == "M5a"])["M5a"]["factor_tipico"],
                              "dif_M5a-M2": rv.dif_pareada(v, "M5a", "M2")}
    (AQUI / "no_estacionariedad_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
