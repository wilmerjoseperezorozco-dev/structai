"""Generalización de la susceptibilidad a movimientos en masa entre departamentos (PROTOCOLO_GENERALIZACION_DEPARTAMENTOS.md).

A. Tabla por departamento (dejando cada uno fuera); A1: AUC agrupado − mediana de departamentos > 0.
B. Validación aleatoria (R) frente a departamento fuera (D) y departamento fuera con zona de 25 km (D+zona); B1: R − D > 0.
C. Área de aplicabilidad (Meyer y Pebesma, 2021); C1: AUC dentro − AUC fuera > 0.
Holm (α = 0,05) sobre A1, B1 y C1. Mismos modelos e hiperparámetros que H6 (B0 logística, G1 boosting).

Entrada: susceptibilidad_muestras_wc.csv (no versionado; muestrear_susceptibilidad.py + agregar_cobertura_worldcover.py).
Uso: python generalizacion_departamentos.py [muestras.csv] [salida.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import NearestNeighbors

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import hipotesis_h6_satelite_ml as h6  # noqa: E402
import pesos_evidencia_mm as pe  # noqa: E402

SEMILLA = 20261107
N_BOOT = 2000
ZONA_KM = 25.0
H6_AUC = {"B0": 0.775, "G1": 0.830}
NUM0, CAT0 = ["pend", "curv", "logfalla"], ["edad"]
NUM1, CAT1 = NUM0 + ["loglluvia"], CAT0 + ["cob"]
RNG = np.random.default_rng(SEMILLA)


def ajustar_predecir(modelo: str, d, Xg, tr, te, y):
    if modelo == "B0":
        return pe.modelo_logit(NUM0, CAT0).fit(d[tr], y[tr]).predict_proba(d[te])[:, 1]
    g = HistGradientBoostingClassifier(categorical_features="from_dtype", **h6.HGB).fit(Xg[tr], y[tr])
    return g.predict_proba(Xg[te])[:, 1]


def auc(y, s):
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def ic_dentro(y, s, rng):
    """Bootstrap estratificado de puntos dentro de un departamento."""
    i1, i0 = np.where(y == 1)[0], np.where(y == 0)[0]
    v = []
    for _ in range(N_BOOT):
        idx = np.concatenate([rng.choice(i1, len(i1)), rng.choice(i0, len(i0))])
        v.append(roc_auc_score(y[idx], s[idx]))
    return [float(x) for x in np.percentile(v, [2.5, 97.5])]


# ---------------------------------------------------------------- área de aplicabilidad
def codificar(d, tr_mask, pesos):
    """Numéricas estandarizadas con el entrenamiento; categóricas en one-hot escaladas para que no coincidir sume w² a la
    distancia al cuadrado. Todo multiplicado por el peso de la variable."""
    cols = []
    for v in NUM1:
        x = d[v].to_numpy(float); mu, sd = x[tr_mask].mean(), x[tr_mask].std() or 1.0
        cols.append(((x - mu) / sd * pesos[v])[:, None])
    for v in CAT1:
        oh = pd.get_dummies(d[v].astype(str)).to_numpy(float)
        cols.append(oh * pesos[v] / np.sqrt(2))
    return np.hstack(cols)


def pesos_importancia(d, Xg, y, tr, dept):
    """Importancia por permutación de G1 dentro del pliegue: se reserva el departamento interno con más presencias."""
    pres = pd.Series(y[tr]).groupby(dept[tr]).sum()
    interno = pres.idxmax()
    te_i = tr & (dept == interno); tr_i = tr & (dept != interno)
    g = HistGradientBoostingClassifier(categorical_features="from_dtype", **h6.HGB).fit(Xg[tr_i], y[tr_i])
    sub = np.where(te_i)[0]
    if len(sub) > 8000:
        sub = np.sort(RNG.choice(sub, 8000, replace=False))
    imp = permutation_importance(g, Xg.iloc[sub], y[sub], scoring="roc_auc", n_repeats=3, random_state=SEMILLA)
    w = {c: max(float(m), 0.0) for c, m in zip(Xg.columns, imp.importances_mean)}
    if sum(w.values()) == 0:
        w = {c: 1.0 for c in w}
    return w, str(interno)


def aoa(d, Xg, y, tr, te, dept):
    w, interno = pesos_importancia(d, Xg, y, tr, dept)
    Z = codificar(d, tr, w)
    itr = np.where(tr)[0]
    a, b = RNG.choice(itr, 2000), RNG.choice(itr, 2000)
    dbar = float(np.mean(np.linalg.norm(Z[a] - Z[b], axis=1))) or 1.0
    # umbral: DI de cada punto de entrenamiento frente al entrenamiento de OTROS departamentos
    di_tr = []
    for dep in np.unique(dept[tr]):
        q = tr & (dept == dep); ref = tr & (dept != dep)
        nn = NearestNeighbors(n_neighbors=1).fit(Z[ref])
        di_tr.append(nn.kneighbors(Z[q])[0][:, 0] / dbar)
    umbral = float(np.percentile(np.concatenate(di_tr), 95))
    nn = NearestNeighbors(n_neighbors=1).fit(Z[tr])
    di_te = nn.kneighbors(Z[te])[0][:, 0] / dbar
    return di_te > umbral, umbral, w, interno


# ---------------------------------------------------------------- utilidades de bootstrap y Holm
def boot_deptos(evaluables, dept, f):
    idx_d = {k: np.where(dept == k)[0] for k in evaluables}
    v = []
    for _ in range(N_BOOT):
        sel = RNG.choice(evaluables, len(evaluables), replace=True)
        v.append(f(sel, np.concatenate([idx_d[k] for k in sel])))
    v = np.array(v, float)
    v = v[np.isfinite(v)]
    return v


def holm(pvals: dict[str, float]):
    orden = sorted(pvals.items(), key=lambda kv: kv[1]); sigue = True; out = {}
    for i, (n, p) in enumerate(orden):
        aj = min(1.0, p * (len(orden) - i)); rech = sigue and aj < 0.05; sigue = rech
        out[n] = {"p": p, "p_holm": aj, "significativo": bool(rech)}
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "susceptibilidad_muestras_wc.csv"
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else AQUI / "generalizacion_departamentos.json"
    d = h6.preparar_wc(pd.read_csv(entrada, dtype={"mun": str}))
    cuenta = d[d.presencia == 1].groupby("depto").size()
    evaluables = sorted(cuenta[cuenta >= pe.MIN_PRES_DEPTO].index)
    d = d[d.depto.isin(evaluables)].reset_index(drop=True)
    y, dept = d.presencia.to_numpy(), d.depto.to_numpy()
    Xg = h6.tabla_gbm(d, NUM1, CAT1)
    print(f"Muestras evaluables {len(d)} (presencias {int(y.sum())}); departamentos {len(evaluables)}", flush=True)

    tx = Transformer.from_crs(4326, 9377, always_xy=True)
    xy = np.column_stack(tx.transform(d.lon.to_numpy(), d.lat.to_numpy())) / 1000.0

    oof = {k: np.full(len(d), np.nan) for k in ("B0_D", "G1_D", "B0_R", "G1_R", "G1_Dz")}
    fuera = np.zeros(len(d), bool)
    info_aoa = {}
    for k, dep in enumerate(evaluables):
        te = dept == dep; tr = ~te
        oof["B0_D"][te] = ajustar_predecir("B0", d, Xg, tr, te, y)
        oof["G1_D"][te] = ajustar_predecir("G1", d, Xg, tr, te, y)
        dist, _ = cKDTree(xy[te]).query(xy[tr], k=1)
        trz = tr.copy(); trz[np.where(tr)[0][dist < ZONA_KM]] = False
        oof["G1_Dz"][te] = ajustar_predecir("G1", d, Xg, trz, te, y)
        f, umbral, w, interno = aoa(d, Xg, y, tr, te, dept)
        fuera[te] = f
        info_aoa[dep] = {"umbral_DI": umbral, "pesos": w, "depto_interno": interno,
                         "quitados_por_zona": int(tr.sum() - trz.sum())}
        print(f"  {k + 1}/{len(evaluables)} {dep}: AUC G1 {auc(y[te], oof['G1_D'][te]):.3f}; "
              f"fuera del área {f.mean():.1%}; quitados por zona {tr.sum() - trz.sum()}", flush=True)
    skf = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    for tr_i, te_i in skf.split(d, y):
        tr = np.zeros(len(d), bool); tr[tr_i] = True; te = ~tr
        oof["B0_R"][te] = ajustar_predecir("B0", d, Xg, tr, te, y)
        oof["G1_R"][te] = ajustar_predecir("G1", d, Xg, tr, te, y)

    res = {"n": len(d), "presencias": int(y.sum()), "departamentos": evaluables}
    agrupado = {k: auc(y, v) for k, v in oof.items()}
    res["auc_agrupado"] = agrupado
    repro = {m: {"h6": H6_AUC[m], "ahora": agrupado[f"{m}_D"], "dentro_0_01": abs(agrupado[f"{m}_D"] - H6_AUC[m]) <= 0.01}
             for m in ("B0", "G1")}
    res["reproducibilidad_h6"] = repro
    print("\nReproducibilidad frente a H6:", json.dumps(repro), flush=True)

    # A. tabla por departamento
    rng_t = np.random.default_rng(SEMILLA)
    tabla = []
    for dep in evaluables:
        m = dept == dep
        fila = {"depto": dep, "region": pe.REG.get(dep, "?"), "presencias": int(y[m].sum()), "n": int(m.sum()),
                "auc_B0": auc(y[m], oof["B0_D"][m]), "auc_G1": auc(y[m], oof["G1_D"][m]),
                "auc_G1_zona": auc(y[m], oof["G1_Dz"][m]), "frac_fuera_area": float(fuera[m].mean())}
        fila["ic_B0"] = ic_dentro(y[m], oof["B0_D"][m], rng_t)
        fila["ic_G1"] = ic_dentro(y[m], oof["G1_D"][m], rng_t)
        tabla.append(fila)
    res["tabla"] = tabla
    auc_dep = {f["depto"]: f["auc_G1"] for f in tabla}
    D_A = agrupado["G1_D"] - float(np.median(list(auc_dep.values())))
    vA = boot_deptos(evaluables, dept, lambda sel, idx: auc(y[idx], oof["G1_D"][idx]) - np.median([auc_dep[s] for s in sel]))
    n_dep = len(tabla)
    a2 = {"sobre_0_5_limite_inferior": sum(f["ic_G1"][0] > 0.5 for f in tabla),
          "sobre_0_7_limite_inferior": sum(f["ic_G1"][0] > 0.7 for f in tabla),
          "sobre_0_7_punto": sum(f["auc_G1"] > 0.7 for f in tabla), "n": n_dep}
    a2["generaliza_en_la_mayoria"] = a2["sobre_0_7_punto"] >= 0.75 * n_dep
    res["A1"] = {"D_A": D_A, "mediana_deptos": float(np.median(list(auc_dep.values()))),
                 "ic": [float(x) for x in np.percentile(vA, [2.5, 97.5])], "p": h6.p_boot(vA)}
    res["A2"] = a2

    # B. aleatoria frente a espacial
    vB = boot_deptos(evaluables, dept, lambda sel, idx: auc(y[idx], oof["G1_R"][idx]) - auc(y[idx], oof["G1_D"][idx]))
    res["B1"] = {"D_B": agrupado["G1_R"] - agrupado["G1_D"], "ic": [float(x) for x in np.percentile(vB, [2.5, 97.5])],
                 "p": h6.p_boot(vB)}
    vB2 = boot_deptos(evaluables, dept, lambda sel, idx: auc(y[idx], oof["G1_D"][idx]) - auc(y[idx], oof["G1_Dz"][idx]))
    res["B2"] = {"D_menos_Dzona": agrupado["G1_D"] - agrupado["G1_Dz"],
                 "ic": [float(x) for x in np.percentile(vB2, [2.5, 97.5])]}
    res["B_B0_descriptivo"] = {"R": agrupado["B0_R"], "D": agrupado["B0_D"]}

    # C. área de aplicabilidad
    n_f, p_f = int(fuera.sum()), int(y[fuera].sum())
    res["C"] = {"puntos_fuera": n_f, "presencias_fuera": p_f, "frac_fuera": float(fuera.mean()), "aoa": info_aoa}
    if n_f >= 200 and p_f >= 30 and (n_f - p_f) > 0:
        D_C = auc(y[~fuera], oof["G1_D"][~fuera]) - auc(y[fuera], oof["G1_D"][fuera])

        def fC(sel, idx):
            dentro, fu = idx[~fuera[idx]], idx[fuera[idx]]
            return auc(y[dentro], oof["G1_D"][dentro]) - auc(y[fu], oof["G1_D"][fu])
        vC = boot_deptos(evaluables, dept, fC)
        res["C1"] = {"D_C": D_C, "auc_dentro": auc(y[~fuera], oof["G1_D"][~fuera]),
                     "auc_fuera": auc(y[fuera], oof["G1_D"][fuera]),
                     "ic": [float(x) for x in np.percentile(vC, [2.5, 97.5])], "p": h6.p_boot(vC)}
    else:
        res["C1"] = {"evaluable": False}
    rho, p_rho = spearmanr([f["frac_fuera_area"] for f in tabla], [f["auc_G1"] for f in tabla])
    res["C2"] = {"spearman": float(rho), "p": float(p_rho)}

    pv = {"A1": res["A1"]["p"], "B1": res["B1"]["p"]}
    if "p" in res["C1"]:
        pv["C1"] = res["C1"]["p"]
    res["holm"] = holm(pv)
    signo = {"A1": res["A1"]["D_A"] > 0, "B1": res["B1"]["D_B"] > 0, "C1": res["C1"].get("D_C", -1) > 0}
    for k in res["holm"]:
        res["holm"][k]["cumple"] = res["holm"][k]["significativo"] and signo[k]
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\nTabla por departamento (G1 dejando el departamento fuera):")
    for f in sorted(tabla, key=lambda f: f["auc_G1"]):
        print(f"  {f['depto']} {f['region']:<10} pres {f['presencias']:5d}  B0 {f['auc_B0']:.3f}  G1 {f['auc_G1']:.3f} "
              f"[{f['ic_G1'][0]:.3f}; {f['ic_G1'][1]:.3f}]  zona {f['auc_G1_zona']:.3f}  fuera {f['frac_fuera_area']:.1%}")
    print("\nA1", json.dumps(res["A1"]), "\nA2", json.dumps(a2), "\nB1", json.dumps(res["B1"]), "\nB2", json.dumps(res["B2"]),
          "\nC1", json.dumps(res["C1"]), "\nC2", json.dumps(res["C2"]), "\nHolm", json.dumps(res["holm"]), flush=True)


if __name__ == "__main__":
    main()
