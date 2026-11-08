"""Regionalizacion de caudales de diseno: validacion ciega, ecuaciones propias, incertidumbre y sensibilidad.
Protocolo: PROTOCOLO_REGIONALIZACION_CAUDALES.md (fijado antes de delinear cuencas ni ajustar modelos).
Entradas: cuencas_estaciones.csv (cuencas_estaciones.py). Salida: regionalizacion_resultados.json
"""
from __future__ import annotations

import io
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cuencas_estaciones as ce  # noqa: E402

warnings.filterwarnings("ignore")
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TS = (2, 5, 10, 25, 50)
REGION = {**{d: "Caribe" for d in ("08", "13", "20", "23", "44", "47", "70")},
          **{d: "Andina" for d in ("05", "15", "17", "25", "41", "54", "63", "66", "68", "73")},
          **{d: "Pacifica" for d in ("19", "52", "76")}, "50": "Orinoquia"}
BUFFER_KM = 50.0
N_BOOT = 3000
N_MC = 2000
RNG = np.random.default_rng(20261108)
MODELOS = ["B0", "B1", "M1", "M2", "M3", "M4"]
SIGMA = {"A": 0.15, "S": 0.20, "P": 0.15}


def km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def elegir_variante(c: pd.DataFrame) -> tuple[str, dict]:
    """Enmienda 1: variante con menor mediana de |elevacion del terreno en la celda - altitud del catalogo|; si la diferencia con r1500 es < 5 m, se mantiene r1500."""
    ok = c[c["motivo_exclusion"].fillna("") == ""].copy()
    ok["dz"] = (ok["elev_snap_m"] - ok["altitud_cat"]).abs()
    med = ok.groupby("variante")["dz"].median().to_dict()
    mejor = min(med, key=med.get)
    elegida = "r1500" if med["r1500"] - med[mejor] < 5.0 else mejor
    return elegida, {k: float(v) for k, v in med.items()}


def cargar(variante: str | None = None) -> pd.DataFrame:
    c0 = pd.read_csv(ce.DESTINO, dtype={"codigo": str, "depto": str})
    if variante is None:
        variante, _ = elegir_variante(c0)
    c = c0[(c0["variante"] == variante) & (c0["motivo_exclusion"].fillna("") == "")].copy()
    e = ce.estaciones()
    d = c.merge(e, on="codigo", how="inner")
    d["region"] = d["depto"].map(REGION)
    d["lA"], d["lS"], d["lP"] = np.log(d["area_km2"]), np.log(d["pend_media_pct"]), np.log(d["lluvia_media_mm"])
    d["bloque"] = d.apply(lambda r: f"{math.floor(r['lat'])}_{math.floor(r['lon'])}", axis=1)
    return d.dropna(subset=["lA", "lS", "lP"]).reset_index(drop=True)


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, y - X @ beta


def ajustar_predecir(tr: pd.DataFrame, te: pd.Series, objetivo: str):
    """Devuelve {modelo: (ln Q estimado, residuos de entrenamiento)} para la estacion `te`."""
    y = np.log(tr[objetivo].values)
    out = {}
    q_esp = np.median(tr[objetivo].values / tr["area_km2"].values)
    out["B0"] = (math.log(q_esp * te["area_km2"]), np.log(tr[objetivo].values / (q_esp * tr["area_km2"].values)))
    for nombre, cols in (("B1", ["lA"]), ("M1", ["lA", "lP"]), ("M2", ["lA", "lP", "lS"])):
        X = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in cols])
        b, res = ols(X, y)
        out[nombre] = (float(b @ np.array([1.0] + [te[c] for c in cols])), res)
    regs = sorted(tr["region"].unique())
    if te["region"] in regs and len(regs) > 1:
        D = np.column_stack([(tr["region"] == r).astype(float) for r in regs[1:]])
        X = np.column_stack([np.ones(len(tr)), tr["lA"], tr["lP"], tr["lS"], D])
        b, res = ols(X, y)
        x = np.array([1.0, te["lA"], te["lP"], te["lS"]] + [float(te["region"] == r) for r in regs[1:]])
        out["M3"] = (float(b @ x), res)
    else:
        out["M3"] = out["M2"]
    Z = tr[["lA", "lS", "lP"]]
    mu, sd = Z.mean(), Z.std(ddof=0).replace(0, 1)
    dist = (((Z - mu) / sd - (te[["lA", "lS", "lP"]].astype(float) - mu) / sd) ** 2).sum(axis=1).values
    k = int(np.argmin(dist))
    b1 = ols(np.column_stack([np.ones(len(tr)), tr["lA"].values]), y)[0][1]
    out["M4"] = (float(y[k] + b1 * (te["lA"] - tr["lA"].values[k])), np.array([0.0]))
    return out


def validar(d: pd.DataFrame, objetivo: str, buffer_km: float = BUFFER_KM) -> pd.DataFrame:
    filas = []
    for i, te in d.iterrows():
        lejos = np.array([km(te["lat"], te["lon"], r.lat, r.lon) >= buffer_km for r in d.itertuples()])
        otra = np.array([not (isinstance(te["corriente"], str) and isinstance(c, str) and te["corriente"].strip().upper() == c.strip().upper()) for c in d["corriente"]])
        tr = d[lejos & otra & (d.index != i)]
        if len(tr) < 20 or not (te[objetivo] > 0):
            continue
        pred = ajustar_predecir(tr, te, objetivo)
        for m, (lq, res) in pred.items():
            q05, q95 = (np.percentile(res, [5, 95]) if len(res) > 5 else (np.nan, np.nan))
            filas.append({"i": i, "codigo": te["codigo"], "region": te["region"], "bloque": te["bloque"], "modelo": m,
                          "eps": lq - math.log(te[objetivo]), "dentro_ic90": bool(lq - q95 <= math.log(te[objetivo]) <= lq - q05) if np.isfinite(q05) else np.nan})
    return pd.DataFrame(filas)


def resumen(v: pd.DataFrame) -> dict:
    out = {}
    for m, g in v.groupby("modelo"):
        e = g["eps"].values
        out[m] = {"n": int(len(e)), "factor_tipico": float(math.exp(np.median(np.abs(e)))), "sesgo_factor": float(math.exp(np.median(e))),
                  "rmse_ln": float(np.sqrt(np.mean(e ** 2))), "dentro_factor2": float(np.mean(np.abs(e) < math.log(2))),
                  "cobertura_ic90": float(np.nanmean(g["dentro_ic90"].astype(float))) if g["dentro_ic90"].notna().any() else None,
                  "cuantiles_factor": {q: float(math.exp(np.percentile(e, q))) for q in (5, 25, 50, 75, 95)}}
    return out


def dif_pareada(v: pd.DataFrame, a: str, b: str):
    pa = v[v["modelo"] == a].set_index("i")
    pb = v[v["modelo"] == b].set_index("i")
    com = pa.index.intersection(pb.index)
    da = np.abs(pa.loc[com, "eps"].values) - np.abs(pb.loc[com, "eps"].values)   # negativo: a es mejor que b
    bl = pa.loc[com, "bloque"].values
    et = np.unique(bl)
    idx = {k: np.where(bl == k)[0] for k in et}
    bs = []
    for _ in range(N_BOOT):
        ii = np.concatenate([idx[k] for k in RNG.choice(et, len(et), replace=True)])
        bs.append(np.median(da[ii]))
    return {"dif_mediana_abs_ln": float(np.median(da)), "ic95": [float(x) for x in np.percentile(bs, [2.5, 97.5])], "n": int(len(com)), "bloques": int(len(et))}


def ecuacion(d: pd.DataFrame, objetivo: str):
    y = np.log(d[objetivo].values)
    X = np.column_stack([np.ones(len(d)), d["lA"], d["lP"], d["lS"]])
    b, res = ols(X, y)
    et = d["bloque"].unique()
    grupos = {k: np.where(d["bloque"].values == k)[0] for k in et}
    bs = []
    for _ in range(N_BOOT):
        ii = np.concatenate([grupos[k] for k in RNG.choice(et, len(et), replace=True)])
        bs.append(ols(X[ii], y[ii])[0])
    ic = np.percentile(np.array(bs), [2.5, 97.5], axis=0)
    r2 = 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
    nombres = ["const", "ln_A", "ln_P", "ln_S"]
    return {"coef": {n: {"valor": float(b[k]), "ic95": [float(ic[0, k]), float(ic[1, k])]} for k, n in enumerate(nombres)},
            "r2": float(r2), "sd_residual_ln": float(res.std(ddof=4)), "n": int(len(d)),
            "dominio": {c: [float(d[c].min()), float(d[c].max())] for c in ("area_km2", "pend_media_pct", "lluvia_media_mm")}}


def main():
    c0 = pd.read_csv(ce.DESTINO, dtype={"codigo": str, "depto": str})
    variante, med_dz = elegir_variante(c0)
    d = cargar(variante)
    print(f"Variante de ajuste a la red elegida (enmienda 1): {variante}; mediana de |dz| por variante: {med_dz}")
    print(f"Estaciones utilizables: {len(d)} en {d['bloque'].nunique()} bloques; por region: {d['region'].value_counts().to_dict()}")
    print(f"Rangos: A {d['area_km2'].min():.0f}-{d['area_km2'].max():.0f} km2, S {d['pend_media_pct'].min():.1f}-{d['pend_media_pct'].max():.1f} %, P {d['lluvia_media_mm'].min():.0f}-{d['lluvia_media_mm'].max():.0f} mm")
    R = {"n": len(d), "por_region": d["region"].value_counts().to_dict(), "variante": variante, "mediana_dz": med_dz}
    val = {}
    for T in TS:
        v = validar(d, f"q{T}")
        val[T] = v
        R[f"val|T{T}"] = resumen(v)
    print("\n== Validacion ciega (zona de exclusion de 50 km y misma corriente) ==")
    print(f"{'T':>3} {'modelo':<5}{'n':>5}{'factor tipico':>15}{'sesgo':>8}{'rmse ln':>9}{'dentro x2':>11}{'cobert. IC90':>14}")
    for T in TS:
        for m in MODELOS:
            r = R[f"val|T{T}"].get(m)
            if r:
                cob = "-" if r["cobertura_ic90"] is None else f"{100 * r['cobertura_ic90']:.0f} %"
                print(f"{T:>3} {m:<5}{r['n']:>5}{r['factor_tipico']:>15.2f}{r['sesgo_factor']:>8.2f}{r['rmse_ln']:>9.2f}{100 * r['dentro_factor2']:>10.0f} %{cob:>14}")
    print("\n== Prueba confirmatoria: T = 10, M2 frente a B1 (mediana de |error ln|; negativo = M2 mejor) ==")
    c = dif_pareada(val[10], "M2", "B1")
    R["confirmatoria"] = c
    ok = c["ic95"][1] < 0
    R["confirmatoria_cumple"] = bool(ok)
    print(f"  dif = {c['dif_mediana_abs_ln']:+.3f} (IC95 [{c['ic95'][0]:+.3f}, {c['ic95'][1]:+.3f}]; n={c['n']}, bloques={c['bloques']}) -> {'SE CUMPLE' if ok else 'NO se cumple'}")
    print("\n== Secundarias (T = 10; dif de la mediana de |error ln|; negativo = el primero es mejor) ==")
    for a, b in (("M2", "M1"), ("M1", "B1"), ("M3", "M2"), ("M4", "M2"), ("M2", "B0")):
        s = dif_pareada(val[10], a, b)
        R[f"sec|{a}-{b}"] = s
        print(f"  {a} frente a {b}: {s['dif_mediana_abs_ln']:+.3f} [{s['ic95'][0]:+.3f}, {s['ic95'][1]:+.3f}]")
    print("\n== Por region natural (T = 10, factor tipico de B1 y de M2) ==")
    for reg, g in val[10].groupby("region"):
        s = resumen(g)
        R[f"region|{reg}"] = {m: s[m] for m in ("B1", "M2") if m in s}
        print(f"  {reg:<9} n={s['M2']['n']:>3}  B1 {s['B1']['factor_tipico']:.2f}  M2 {s['M2']['factor_tipico']:.2f}")
    print("\n== Ecuaciones propias (ajuste con todas las estaciones): ln Q = a + b ln A + c ln P + d ln S ==")
    for T in TS:
        e = ecuacion(d, f"q{T}")
        R[f"ecuacion|T{T}"] = e
        k = e["coef"]
        print(f"  T={T:>2}: a={k['const']['valor']:+.2f}  b={k['ln_A']['valor']:.2f} [{k['ln_A']['ic95'][0]:.2f},{k['ln_A']['ic95'][1]:.2f}]  c={k['ln_P']['valor']:+.2f} [{k['ln_P']['ic95'][0]:+.2f},{k['ln_P']['ic95'][1]:+.2f}]  d={k['ln_S']['valor']:+.2f} [{k['ln_S']['ic95'][0]:+.2f},{k['ln_S']['ic95'][1]:+.2f}]  R2={e['r2']:.2f}  sd_res={e['sd_residual_ln']:.2f}")
    print(f"  dominio de validez: {R['ecuacion|T10']['dominio']}")
    print("\n== Incertidumbre: propagacion de errores de los predictores (T = 10, Monte Carlo) ==")
    e = R["ecuacion|T10"]["coef"]
    cv = math.sqrt((e["ln_A"]["valor"] * SIGMA["A"]) ** 2 + (e["ln_P"]["valor"] * SIGMA["P"]) ** 2 + (e["ln_S"]["valor"] * SIGMA["S"]) ** 2)
    base = val[10][val[10]["modelo"] == "M2"]["eps"].values
    pert = base + RNG.normal(0, cv, (N_MC, len(base)))
    f_base, f_pert = math.exp(np.median(np.abs(base))), math.exp(np.median(np.abs(pert), axis=1).mean())
    R["incertidumbre"] = {"sd_ln_por_predictores": cv, "factor_tipico_base": f_base, "factor_tipico_con_errores_adicionales": f_pert,
                          "aporte_por_predictor": {k: float(abs(e[f"ln_{k}"]["valor"]) * SIGMA[v]) for k, v in (("A", "A"), ("P", "P"), ("S", "S"))}}
    print(f"  Los errores supuestos (A 15 %, S 20 %, P 15 %) agregan una dispersion de {cv:.2f} en ln Q (factor {math.exp(cv):.2f}); el factor tipico pasaria de {f_base:.2f} a {f_pert:.2f} si se sumaran al error ya medido.")
    print("\n== Sensibilidad metodologica (T = 10; factor tipico M2 y B1, n) ==")
    variantes = {
        "base": d, "registro >= 40 anos": d[d["n"] >= 40], "xi estable [-0,5; 0,5]": d[d["xi"].between(-0.5, 0.5)],
        "area <= 2000 km2": d[d["area_km2"] <= 2000], "solo limnigraficas": d[d["categoria"].astype(str).str.contains("graf", case=False)],
        "area >= 20 km2": d[d["area_km2"] >= 20]}
    for nombre, dd in variantes.items():
        dd = dd.reset_index(drop=True)
        if len(dd) < 40:
            continue
        s = resumen(validar(dd, "q10"))
        R[f"sens|{nombre}"] = {m: s[m] for m in ("B1", "M2")}
        print(f"  {nombre:<26} n={s['M2']['n']:>3}  B1 {s['B1']['factor_tipico']:.2f}  M2 {s['M2']['factor_tipico']:.2f}")
    for v_ in sorted(set(c0["variante"]) - {variante}):
        dd = cargar(v_)
        if len(dd) >= 40:
            s = resumen(validar(dd, "q10"))
            R[f"sens|variante {v_}"] = {m: s[m] for m in ("B1", "M2")}
            print(f"  variante de ajuste {v_:<8}  n={s['M2']['n']:>3}  B1 {s['B1']['factor_tipico']:.2f}  M2 {s['M2']['factor_tipico']:.2f}")
    for km_ in (0.0, 100.0):
        s = resumen(validar(d, "q10", buffer_km=km_))
        R[f"sens|zona exclusion {km_:.0f} km"] = {m: s[m] for m in ("B1", "M2")}
        print(f"  zona de exclusion {km_:>5.0f} km     n={s['M2']['n']:>3}  B1 {s['B1']['factor_tipico']:.2f}  M2 {s['M2']['factor_tipico']:.2f}")
    s = resumen(validar(d.assign(q10=d["qlp10"]), "q10"))
    R["sens|objetivo Log-Pearson III"] = {m: s[m] for m in ("B1", "M2")}
    print(f"  objetivo Log-Pearson III   n={s['M2']['n']:>3}  B1 {s['B1']['factor_tipico']:.2f}  M2 {s['M2']['factor_tipico']:.2f}")
    (AQUI / "regionalizacion_resultados.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
