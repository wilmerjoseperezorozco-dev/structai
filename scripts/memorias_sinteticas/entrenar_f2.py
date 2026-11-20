"""F2 (#275): subrogados entrenados con el corpus de memorias sintéticas, con la evaluación prerregistrada.

Prerregistro: docs/memoria_calculo/PRERREGISTRO_F2_SUBROGADOS.md (fijado antes de ver el corpus). Una sola evaluación sobre el
reservado. Guardia: toda propuesta del subrogado pasa por el diseño completo F4; el subrogado nunca entrega un diseño que no
verifique el motor.
Uso:  python -I scripts/memorias_sinteticas/entrenar_f2.py [--corpus data/memorias_sinteticas/corpus.csv] [--salida data/memorias_sinteticas/f2]
      [--sin-guardia]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import balanced_accuracy_score

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 275
IDS_VISTOS = set(range(16))                       # piloto: van al entrenamiento, nunca al reservado
PARAMS = dict(n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=10, subsample=0.9, subsample_freq=1,
              colsample_bytree=0.9, verbose=-1)  # los del subrogado de muros, sin búsqueda
ENTRADAS = ["N", "vanos_x", "vanos_y", "Lx_m", "Ly_m", "hp_m", "aa", "av", "perfil_n", "L_kpa", "grupo_n", "D_kpa", "fc_mpa"]
COSTOS = ["y_costo_cop_m2", "y_acero_kg_m2", "y_concreto_m3_m2", "y_co2_kg_m2"]
OTRAS = ["y_T_modelo_x_s", "c_inferior_mm", "c_superior_mm", "h_viga_mm"]
ALFA = 0.10


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["estado"].isin(["ok", "sin_solucion"])].copy()
    d["perfil_n"] = d["perfil"].map({"C": 0, "D": 1, "E": 2})
    d["grupo_n"] = d["grupo_uso"].map({"I": 1, "II": 2, "III": 3, "IV": 4})
    d["ok"] = (d["estado"] == "ok").astype(int)
    return d


def dividir(d: pd.DataFrame):
    rng = np.random.default_rng(SEMILLA)
    elegibles = d[~d["id"].isin(IDS_VISTOS)].index.to_numpy()
    res = rng.choice(elegibles, size=int(round(0.15 * len(d))), replace=False)
    resto = d.index.difference(res).to_numpy()
    cal = rng.choice(resto, size=int(round(0.15 * len(resto))), replace=False)
    return d.loc[np.setdiff1d(resto, cal)], d.loc[cal], d.loc[res]


def mape(y, p):
    return float(np.mean(np.abs(p - y) / np.abs(y)))


def boot_mejora(y, p_base, p_mod, b=10000):
    rng = np.random.default_rng(SEMILLA)
    e_b, e_m = np.abs(p_base - y) / y, np.abs(p_mod - y) / y
    n = len(y)
    dif = [float(np.mean(e_b[i] - e_m[i])) for i in (rng.integers(0, n, n) for _ in range(b))]
    return [float(np.quantile(dif, 0.025)), float(np.quantile(dif, 0.975))]


def wilson(k, n, z=1.96):
    if n == 0:
        return [math.nan, math.nan]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [c - h, c + h]


def lineal(tr, objetivo, log=True):
    def X(d):
        x = d[ENTRADAS].astype(float).copy()
        x["logN"] = np.log(d["N"])
        x["AaN"] = d["aa"] * d["N"]
        for k in (1, 2):
            x[f"perfil_{k}"] = (d["perfil_n"] == k).astype(float)
        return x
    y = np.log(tr[objetivo]) if log else tr[objetivo]
    m = LinearRegression().fit(X(tr), y)
    return lambda d: np.exp(m.predict(X(d))) if log else m.predict(X(d))


def regresion(tr, cal, objetivo, log):
    y = np.log(tr[objetivo]) if log else tr[objetivo].astype(float)
    m = lgb.LGBMRegressor(random_state=SEMILLA, **PARAMS).fit(tr[ENTRADAS], y)
    yc = np.log(cal[objetivo]) if log else cal[objetivo].astype(float)
    r = np.abs(yc - m.predict(cal[ENTRADAS]))
    n = len(r)
    q = float(np.quantile(r, min(1.0, math.ceil((n + 1) * (1 - ALFA)) / n), method="higher")) if n else math.nan
    pred = (lambda d: np.exp(m.predict(d[ENTRADAS]))) if log else (lambda d: m.predict(d[ENTRADAS]))
    inter = (lambda d: (np.exp(m.predict(d[ENTRADAS]) - q), np.exp(m.predict(d[ENTRADAS]) + q))) if log else \
        (lambda d: (m.predict(d[ENTRADAS]) - q, m.predict(d[ENTRADAS]) + q))
    return m, pred, inter, q


def guardia(res_ok: pd.DataFrame, pred_sec: dict, sin_solucion_predicha_factible: pd.DataFrame):
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de, optimizar_edificio_3d as op
    filas = []
    for idx, c in res_ok.iterrows():
        n = int(c["N"])
        base = de.ProyectoEdificio3D(
            luces_x_m=(float(c["Lx_m"]),) * int(c["vanos_x"]), luces_y_m=(float(c["Ly_m"]),) * int(c["vanos_y"]),
            alturas_piso_m=(float(c["hp_m"]),) * n, columnas_mm=(1.0,) * n, vigas_mm=((1.0, 1.0),) * n,
            carga_muerta_kpa=float(c["D_kpa"]), carga_viva_kpa=float(c["L_kpa"]), aa=float(c["aa"]), av=float(c["av"]),
            perfil_suelo=c["perfil"], grupo_uso=c["grupo_uso"], capacidad=c["capacidad"], fc_mpa=float(c["fc_mpa"]))
        h = min(op.ALTURAS_VIGA, key=lambda v: abs(v - pred_sec["h_viga_mm"][idx]))
        cc = 50.0 * round(pred_sec["c_inferior_mm"][idx] / 50.0)
        delta = min(op.REDUCCIONES, key=lambda v: abs(v - (pred_sec["c_inferior_mm"][idx] - pred_sec["c_superior_mm"][idx])))
        b_v = op._secciones(n, 300.0, 0.0, h)[1][0][0]
        c0 = max(cc, b_v + delta, 300.0)
        origen, costo, k = "exacto", float(c["y_costo_cop_m2"]), 0        # exacto: se recurre al optimizador de la F1
        for k in range(op.PASOS_EXTRA + 1):
            if c0 + 50 * k > op.COLUMNAS[-1]:
                break
            col, vig = op._secciones(n, c0 + 50 * k, delta, h)
            inf = de.disenar_edificio(dataclasses.replace(base, columnas_mm=col, vigas_mm=vig))
            if inf.cumple:                                             # solo se entrega lo que verifica el motor F4
                origen = "directo" if k == 0 else "reparado"
                costo = inf.cantidades["costo_cop"] / inf.cantidades["area_construida_m2"]
                break
        filas.append({"id": int(c["id"]), "origen": origen, "pasos": k, "costo_m2": costo,
                      "brecha": costo / float(c["y_costo_cop_m2"]) - 1.0})
    # 0 inseguros por construcción: la guardia solo devuelve diseños con InformeEdificio3D.cumple (y nada si no hay)
    return filas, 0, len(sin_solucion_predicha_factible)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(RAIZ / "data" / "memorias_sinteticas" / "corpus.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "memorias_sinteticas" / "f2"))
    ap.add_argument("--sin-guardia", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(a.corpus)
    d = preparar(df)
    tr, cal, res = dividir(d)
    R = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_F2_SUBROGADOS.md", "n_corpus": len(df),
         "n_error": int((df["estado"] == "error").sum()), "n_usado": len(d), "n_entrenamiento": len(tr), "n_calibracion": len(cal),
         "n_reservado": len(res), "tasa_factible": float(d["ok"].mean())}
    # 1. factibilidad
    clf = lgb.LGBMClassifier(random_state=SEMILLA, **PARAMS).fit(pd.concat([tr, cal])[ENTRADAS], pd.concat([tr, cal])["ok"])
    p_ok = clf.predict(res[ENTRADAS])
    R["factibilidad"] = {"exactitud_balanceada": float(balanced_accuracy_score(res["ok"], p_ok)),
                         "exactitud": float((p_ok == res["ok"]).mean()),
                         "factible_falso": int(((p_ok == 1) & (res["ok"] == 0)).sum()),
                         "inviable_falso": int(((p_ok == 0) & (res["ok"] == 1)).sum()),
                         "criterio": "exactitud balanceada > 0,90"}
    R["factibilidad"]["cumple"] = R["factibilidad"]["exactitud_balanceada"] > 0.90
    clf.booster_.save_model(str(out / "factibilidad.txt"))
    # 2. regresiones sobre los factibles
    tr_ok, cal_ok, res_ok = tr[tr.ok == 1], cal[cal.ok == 1], res[res.ok == 1]
    R["regresiones"], preds = {}, {}
    zona_n = tr_ok.groupby(["zona", "N"])["y_costo_cop_m2"].median()
    for obj in COSTOS + OTRAS:
        log = obj in COSTOS or obj == "y_T_modelo_x_s"
        m, pred, inter, q = regresion(tr_ok, cal_ok, obj, log)
        m.booster_.save_model(str(out / f"{obj}.txt"))
        y = res_ok[obj].astype(float).to_numpy()
        p = pred(res_ok)
        preds[obj] = pd.Series(p, index=res_ok.index)
        fila = {"MAPE": mape(y, p), "R2": float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)), "q_conforme_log": q}
        lo, hi = inter(res_ok)
        fila["cobertura_90"] = float(np.mean((y >= lo) & (y <= hi)))
        if obj in COSTOS:
            pl = lineal(pd.concat([tr_ok, cal_ok]), obj)(res_ok)
            fila["MAPE_lineal"] = mape(y, pl)
            fila["IC95_mejora_sobre_lineal"] = boot_mejora(y, pl, p)
        if obj == "y_costo_cop_m2":
            pm = np.array([zona_n.get((z, n), tr_ok["y_costo_cop_m2"].median()) for z, n in zip(res_ok["zona"], res_ok["N"])])
            fila["MAPE_mediana_zona_N"] = mape(y, pm)
            fila["cumple"] = bool(fila["MAPE"] <= 0.10 and fila["IC95_mejora_sobre_lineal"][0] > 0 and 0.87 <= fila["cobertura_90"] <= 0.93)
        if obj.endswith("_mm"):
            fila["error_medio_pasos_50mm"] = float(np.mean(np.abs(p - y)) / 50.0)
        R["regresiones"][obj] = fila
    # 3. extrapolación (descriptivo)
    R["extrapolacion"] = {}
    for nombre, mtr, mte in (("Aa<=0.30 -> Aa>=0.35", d.aa <= 0.30, d.aa >= 0.35), ("N<=10 -> N>=11", d.N <= 10, d.N >= 11)):
        a_tr, a_te = d[mtr & (d.ok == 1)], d[mte & (d.ok == 1)]
        if len(a_te) and len(a_tr):
            m = lgb.LGBMRegressor(random_state=SEMILLA, **PARAMS).fit(a_tr[ENTRADAS], np.log(a_tr["y_costo_cop_m2"]))
            R["extrapolacion"][nombre] = {"n_test": len(a_te), "MAPE_costo": mape(a_te["y_costo_cop_m2"].to_numpy(),
                                                                                 np.exp(m.predict(a_te[ENTRADAS])))}
    # 4. guardia
    if not a.sin_guardia:
        t = time.time()
        filas, inseguros, n_ff = guardia(res_ok, {k: preds[k] for k in ("c_inferior_mm", "c_superior_mm", "h_viga_mm")},
                                         res[(p_ok == 1) & (res.ok == 0)])
        g = pd.DataFrame(filas)
        n = len(g)
        k_ok = int(g["origen"].isin(["directo", "reparado"]).sum())
        R["guardia"] = {"n": n, "origenes": g["origen"].value_counts().to_dict(), "directo_o_reparado": k_ok / n if n else None,
                        "ic95_wilson": wilson(k_ok, n), "inseguros_entregados": inseguros,
                        "brecha_costo_mediana": float(g.loc[g.origen != "exacto", "brecha"].median()) if k_ok else None,
                        "brecha_costo_p90": float(g.loc[g.origen != "exacto", "brecha"].quantile(0.9)) if k_ok else None,
                        "sin_solucion_predichos_factibles": n_ff, "segundos": time.time() - t,
                        "criterio": "directo + reparado >= 0,80"}
        R["guardia"]["cumple"] = bool(n and k_ok / n >= 0.80)
        g.to_csv(out / "guardia_detalle.csv", index=False)
    (out / "resultados_f2.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
