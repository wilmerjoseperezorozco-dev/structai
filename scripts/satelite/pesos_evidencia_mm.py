"""Susceptibilidad a movimientos en masa: pesos de evidencia y regresion logistica (protocolo seccion 22).

Entrada: susceptibilidad_muestras.csv (muestrear_susceptibilidad.py). Validacion dejando un DEPARTAMENTO fuera.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261107)
N_BOOT, MIN_PRES_DEPTO, C_LOGIT = 2000, 20, 1.0
CLASES_FALLA = [0, 1, 5, 10, 25, np.inf]
REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
REG = {d: r for r, ds in REGIONES.items() for d in ds.split()}


def discretizar(df: pd.DataFrame, entrenamiento: pd.DataFrame) -> pd.DataFrame:
    """Clases por cuantiles (20/40/60/80 %) de las PRESENCIAS de entrenamiento; fallas con cortes fijos."""
    out = pd.DataFrame(index=df.index)
    pres = entrenamiento[entrenamiento.presencia == 1]
    for v in ("pend", "curv"):
        cortes = np.unique(np.quantile(pres[v], [0.2, 0.4, 0.6, 0.8]))
        out[v] = np.digitize(df[v], cortes).astype(str)
    out["falla"] = pd.cut(df.dist_falla_km, CLASES_FALLA, right=False, labels=False).astype(str)
    out["edad"] = df.edad.astype(str)
    return out


def tabla_pesos(clases: pd.DataFrame, y: np.ndarray) -> dict[str, dict[str, tuple[float, float]]]:
    """W+ y W- por clase, con suavizado de 0,5 para evitar log(0)."""
    pesos = {}
    n1, n0 = y.sum(), (1 - y).sum()
    for v in clases.columns:
        pesos[v] = {}
        for c in clases[v].unique():
            m = (clases[v] == c).to_numpy()
            a, b = (m & (y == 1)).sum() + 0.5, (m & (y == 0)).sum() + 0.5
            wp = np.log((a / (n1 + 1)) / (b / (n0 + 1)))
            wm = np.log(((n1 - a + 1) / (n1 + 1)) / ((n0 - b + 1) / (n0 + 1)))
            pesos[v][c] = (float(wp), float(wm))
    return pesos


def puntaje_pesos(clases: pd.DataFrame, pesos) -> np.ndarray:
    s = np.zeros(len(clases))
    for v in clases.columns:
        s += clases[v].map(lambda c: pesos[v].get(c, (0.0, 0.0))[0]).to_numpy()
    return s


def modelo_logit(columnas_num, columnas_cat):
    pre = ColumnTransformer([("n", StandardScaler(), columnas_num), ("c", OneHotEncoder(handle_unknown="ignore"), columnas_cat)])
    return make_pipeline(pre, LogisticRegression(C=C_LOGIT, max_iter=2000))


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["logfalla"] = np.log1p(d.dist_falla_km)
    return d


def cramer(a: pd.Series, b: pd.Series) -> float:
    t = pd.crosstab(a, b).to_numpy().astype(float)
    n = t.sum(); esp = t.sum(1, keepdims=True) * t.sum(0, keepdims=True) / n
    chi = ((t - esp) ** 2 / esp).sum()
    return float(np.sqrt(chi / (n * (min(t.shape) - 1))))


def auc_dept(y, s, dept, sel) -> float:
    m = np.isin(dept, sel)
    return roc_auc_score(y[m], s[m]) if m.sum() > 0 and 0 < y[m].sum() < m.sum() else np.nan


def main() -> None:
    df = preparar(pd.read_csv(AQUI / "susceptibilidad_muestras.csv", dtype={"mun": str}))
    df["depto"] = df.mun.str[:2]
    y = df.presencia.to_numpy()
    print(f"Muestras: {len(df)} (presencias {int(y.sum())}, fondo {int((1 - y).sum())}); edades: {df.edad.value_counts().to_dict()}")
    cuenta = df[df.presencia == 1].groupby("depto").size()
    evaluables = sorted(cuenta[cuenta >= MIN_PRES_DEPTO].index)
    print(f"Departamentos evaluables (>= {MIN_PRES_DEPTO} presencias): {len(evaluables)} de {df.depto.nunique()}")
    oof = {k: np.full(len(df), np.nan) for k in ("logit_completo", "logit_pend", "woe")}
    for d in evaluables:
        te = (df.depto == d).to_numpy(); tr = ~te
        m = modelo_logit(["pend", "curv", "logfalla"], ["edad"]).fit(df[tr], y[tr])
        oof["logit_completo"][te] = m.predict_proba(df[te])[:, 1]
        m1 = make_pipeline(StandardScaler(), LogisticRegression(C=C_LOGIT)).fit(df.loc[tr, ["pend"]], y[tr])
        oof["logit_pend"][te] = m1.predict_proba(df.loc[te, ["pend"]])[:, 1]
        cl_tr = discretizar(df[tr], df[tr]); cl_te = discretizar(df[te], df[tr])
        oof["woe"][te] = puntaje_pesos(cl_te, tabla_pesos(cl_tr, y[tr]))
    ev = df.depto.isin(evaluables).to_numpy()
    dept = df.depto.to_numpy()
    res = {}
    for k, s in oof.items():
        res[k] = float(roc_auc_score(y[ev], s[ev]))
    print("\nAUC espacial (dejando un departamento fuera, predicciones agrupadas): " + ", ".join(f"{k} {v:.3f}" for k, v in res.items()))
    pooled = lambda s, sel: auc_dept(y, s, dept, sel)
    boot = {"completo": [], "dif_pend": [], "dif_woe": []}
    for _ in range(N_BOOT):
        sel = RNG.choice(evaluables, len(evaluables), replace=True)
        idx = np.concatenate([np.where(dept == d)[0] for d in sel])
        a = [roc_auc_score(y[idx], oof[k][idx]) for k in ("logit_completo", "logit_pend", "woe")]
        boot["completo"].append(a[0]); boot["dif_pend"].append(a[0] - a[1]); boot["dif_woe"].append(a[2] - a[0])
    ic = {k: np.percentile(v, [2.5, 97.5]) for k, v in boot.items()}
    print(f"S1 AUC regresion logistica completa = {res['logit_completo']:.3f} IC95% bloques [{ic['completo'][0]:.3f}, {ic['completo'][1]:.3f}] -> {'cumple' if ic['completo'][0] > 0.5 else 'NO cumple'}")
    d2 = res["logit_completo"] - res["logit_pend"]
    print(f"S2 completo - solo pendiente = {d2:+.3f} IC95% [{ic['dif_pend'][0]:+.3f}, {ic['dif_pend'][1]:+.3f}] -> {'cumple' if ic['dif_pend'][0] > 0 else 'NO cumple'}")
    d3 = res["woe"] - res["logit_completo"]
    print(f"S3 pesos de evidencia - logistica = {d3:+.3f} IC95% [{ic['dif_woe'][0]:+.3f}, {ic['dif_woe'][1]:+.3f}] -> {'cumple (no inferior en mas de 0,02)' if d3 >= -0.02 else 'NO cumple (inferior en mas de 0,02)'}")
    print("\nAUC por region natural (modelo logistico completo / solo pendiente / pesos de evidencia):")
    for r, ds in REGIONES.items():
        m = ev & np.isin(dept, ds.split())
        if m.sum() and 0 < y[m].sum() < m.sum():
            print(f"  {r:<10} presencias {int(y[m].sum()):5d}: {roc_auc_score(y[m], oof['logit_completo'][m]):.3f} / {roc_auc_score(y[m], oof['logit_pend'][m]):.3f} / {roc_auc_score(y[m], oof['woe'][m]):.3f}")
    cl = discretizar(df, df)
    pesos = tabla_pesos(cl, y)
    print("\nPesos por clase (contraste W+ - W-; > 0 aumenta la susceptibilidad), ajuste con todos los datos:")
    for v, tabla in pesos.items():
        orden = sorted(tabla.items(), key=lambda kv: -(kv[1][0] - kv[1][1]))
        print(f"  {v}: " + "; ".join(f"{c}: {a - b:+.2f}" for c, (a, b) in orden))
    print("\nIndependencia condicional (V de Cramer entre variables discretizadas):")
    pares = []
    cols = list(cl.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            v = cramer(cl[cols[i]], cl[cols[j]]); pares.append((cols[i], cols[j], v))
            print(f"  {cols[i]} - {cols[j]}: {v:.2f}{'  (dependientes, V > 0,3)' if v > 0.3 else ''}")
    out = {"auc": res, "ic": {k: [float(x) for x in v] for k, v in ic.items()}, "pesos": {v: {c: list(w) for c, w in t.items()} for v, t in pesos.items()},
           "cramer": [[a, b, c] for a, b, c in pares], "evaluables": evaluables}
    (AQUI / "pesos_evidencia_mm.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    # descriptivo: puntaje municipal medio vs indice SGC (seccion 16)
    sgc = {r["CODIGO_DAN"]: (r["SUM_ALTA"] or 0) + (r["SUM_MUY_AL"] or 0) for r in json.loads((AQUI / "sgc_amenaza_mm_municipios.json").read_text(encoding="utf-8")) if r["CATEGORIA"] == "M"}
    cm = df.assign(p=oof["logit_completo"]).dropna(subset=["p"]).groupby("mun").p.mean()
    comun = [c for c in cm.index if c in sgc]
    if len(comun) > 50:
        print(f"\nDescriptivo: rho(probabilidad media del modelo por municipio, indice SGC) = {spearmanr([cm[c] for c in comun], [sgc[c] for c in comun])[0]:+.2f} (n={len(comun)} municipios)")


if __name__ == "__main__":
    main()
