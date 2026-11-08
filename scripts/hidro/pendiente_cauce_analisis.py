"""E1: ¿la pendiente del cauce mejora la regionalizacion de caudales? Protocolo: PROTOCOLO_PENDIENTE_CAUCE.md (con Enmienda 1).
Entradas: cuencas_estaciones.csv, pendiente_cauce.csv (pendiente_cauce_extraer.py). Salida: pendiente_cauce_resultados.json"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import regionalizacion_validacion as rv  # noqa: E402

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(20261108)
N_BOOT = 3000
PISO_S = 0.0005
MODELOS = {"M2": ["lA", "lP", "lS"], "M2c": ["lA", "lP", "lSc"], "M2b": ["lA", "lP", "lS", "lSc"],
           "M2c10": ["lA", "lP", "lSc10"], "M2b10": ["lA", "lP", "lS", "lSc10"]}


def ajustar(tr: pd.DataFrame, te: pd.Series, objetivo: str):
    y = np.log(tr[objetivo].values)
    out = {}
    for nombre, cols in MODELOS.items():
        X = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in cols])
        b, res = rv.ols(X, y)
        out[nombre] = (float(b @ np.array([1.0] + [te[c] for c in cols])), res)
    return out


def dif(v: pd.DataFrame, a: str, b: str, nivel: float = 95.0, filtro=None):
    pa, pb = v[v["modelo"] == a].set_index("i"), v[v["modelo"] == b].set_index("i")
    com = pa.index.intersection(pb.index)
    if filtro is not None:
        com = com.intersection(filtro)
    if len(com) < 8:
        return {"n": int(len(com)), "nota": "muestra insuficiente"}
    da = np.abs(pa.loc[com, "eps"].values) - np.abs(pb.loc[com, "eps"].values)     # negativo: a es mejor
    bl = pa.loc[com, "bloque"].values
    et = np.unique(bl)
    idx = {k: np.where(bl == k)[0] for k in et}
    bs = [np.median(da[np.concatenate([idx[k] for k in RNG.choice(et, len(et), replace=True)])]) for _ in range(N_BOOT)]
    lo, hi = (100 - nivel) / 2, 100 - (100 - nivel) / 2
    return {"dif_mediana_abs_ln": float(np.median(da)), f"ic{nivel:g}": [float(x) for x in np.percentile(bs, [lo, hi])], "n": int(len(com)), "bloques": int(len(et))}


def preparar() -> tuple[pd.DataFrame, dict]:
    d = rv.cargar("r1500")
    pc = pd.read_csv(AQUI / "pendiente_cauce.csv", dtype={"codigo": str, "depto": str})
    n0 = len(d)
    d = d.merge(pc.drop(columns=["depto"]), on="codigo", how="left")
    q = {"n_etapa_A": n0, "sin_fila_de_cauce": int(d["S_ts"].isna().sum())}
    inc_area = (d["area_recalculada_km2"] / d["area_km2"] - 1).abs() > 0.15
    corta = d["L_km"] < 0.5 * np.sqrt(d["area_km2"])
    q.update({"ruta_invalida_o_error": int((d["motivo"].fillna("") != "").sum()), "area_difiere_mas_15pct": int(inc_area.sum()),
              "L_menor_0_5_raiz_A": int(corta.sum()), "fraccion_tramos_con_piso_mediana": float(d["frac_tramos_piso"].median())})
    ok = d["S_ts"].notna() & (d["motivo"].fillna("") == "") & ~inc_area.fillna(False)
    q["excluidas_total"] = int((~ok).sum())
    q["fraccion_excluida"] = float((~ok).mean())
    d = d[ok].reset_index(drop=True)
    d["lSc"] = np.log(np.maximum(d["S_ts"], PISO_S))
    d["lSc10"] = np.log(np.maximum(d["S_1085"], PISO_S))
    q["n_analisis"] = int(len(d))
    return d, q


def main():
    d, q = preparar()
    print("Calidad:", q)
    R = {"calidad": q, "corr_lS_lSc": float(np.corrcoef(d["lS"], d["lSc"])[0, 1]), "corr_lS_lSc10": float(np.corrcoef(d["lS"], d["lSc10"])[0, 1])}
    d_pend = d["pend_media_pct"] > 30
    rv.ajustar_predecir = ajustar                      # solo cambia la funcion que ajusta los modelos; zona de exclusion y misma corriente quedan intactas
    val = {}
    for T in rv.TS:
        val[T] = rv.validar(d, f"q{T}")
        s = rv.resumen(val[T])
        R[f"val|T{T}"] = {m: {k: s[m][k] for k in ("n", "factor_tipico", "sesgo_factor", "dentro_factor2")} for m in MODELOS}
        print(f"T={T:>2} " + "  ".join(f"{m} {s[m]['factor_tipico']:.2f}" for m in MODELOS), flush=True)
    v10 = val[10]
    print("\n== PRIMARIO (T=10, IC 97,5 %; negativo = el primero es mejor) ==")
    for a in ("M2b", "M2c"):
        c = dif(v10, a, "M2", 97.5)
        R[f"primario|{a}-M2"] = c
        c["cumple"] = bool(c["ic97.5"][1] < 0)
        print(f"  {a} - M2: {c['dif_mediana_abs_ln']:+.4f} IC97.5 [{c['ic97.5'][0]:+.4f}, {c['ic97.5'][1]:+.4f}] n={c['n']} -> {'SE CUMPLE' if c['cumple'] else 'NO se cumple'}")
    print("\n== Secundarios (IC 95 %) ==")
    estratos = {"pend>30%": d.index[d_pend], "pend<=30%": d.index[~d_pend], "Caribe": d.index[d["region"] == "Caribe"],
                "Andina": d.index[d["region"] == "Andina"]}
    for a in ("M2b", "M2c", "M2b10", "M2c10"):
        for nombre, ix in estratos.items():
            r = dif(v10, a, "M2", 95.0, ix)
            R[f"sec|{a}-M2|{nombre}"] = r
            if "ic95" in r:
                print(f"  {a:<6} - M2 [{nombre:<9}] {r['dif_mediana_abs_ln']:+.4f} [{r['ic95'][0]:+.4f}, {r['ic95'][1]:+.4f}] n={r['n']}")
    for T in (2, 5, 25, 50):
        for a in ("M2b", "M2c"):
            r = dif(val[T], a, "M2", 95.0)
            R[f"sec|T{T}|{a}-M2"] = r
            print(f"  T={T:>2} {a} - M2: {r['dif_mediana_abs_ln']:+.4f} [{r['ic95'][0]:+.4f}, {r['ic95'][1]:+.4f}]")
    print("\n== Coeficientes (ajuste con todas las cuencas, T=10; IC95 % por bloques) ==")
    y = np.log(d["q10"].values)
    for nombre, cols in MODELOS.items():
        X = np.column_stack([np.ones(len(d))] + [d[c].values for c in cols])
        b, res = rv.ols(X, y)
        et = d["bloque"].unique()
        gr = {k: np.where(d["bloque"].values == k)[0] for k in et}
        bs = np.array([rv.ols(X[ii], y[ii])[0] for ii in (np.concatenate([gr[k] for k in RNG.choice(et, len(et), replace=True)]) for _ in range(1500))])
        ic = np.percentile(bs, [2.5, 97.5], axis=0)
        r2 = 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
        R[f"coef|{nombre}"] = {"r2": float(r2), **{n: {"valor": float(b[k]), "ic95": [float(ic[0, k]), float(ic[1, k])]} for k, n in enumerate(["const"] + cols)}}
        print(f"  {nombre:<6} R2={r2:.3f} " + " ".join(f"{n}={b[k]:+.2f}[{ic[0, k]:+.2f},{ic[1, k]:+.2f}]" for k, n in enumerate(["const"] + cols)))
    (AQUI / "pendiente_cauce_resultados.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
