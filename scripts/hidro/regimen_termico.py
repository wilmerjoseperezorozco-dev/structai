"""H3: regimen termico (temperatura de las normales del IDEAM) como predictor del caudal de diseno.
Protocolo: PROTOCOLO_REGIMEN_TERMICO.md (preregistrado antes de construir el campo ni ajustar modelos con el).
Salidas: regimen_termico_resultados.json, regimen_termico_cuencas.csv
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import normales_vs_chirps as nv  # noqa: E402
import regionalizacion_validacion as rv  # noqa: E402

BUFFER_KM = 50.0
CACHE = AQUI / "_cache" / "normales_temperatura_media_1991_2020.csv"
URL = "https://www.datos.gov.co/resource/nsz2-kzcq.json"
RADIO_IDW_KM, K_IDW = 100.0, 3


def cargar_temperatura() -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_csv(CACHE)
    r = requests.get(URL, timeout=120, params={"$where": "periodo='1991-2020' and par_metro like 'TEMPERATURA MEDIA%'", "$limit": 50000}).json()
    d = pd.DataFrame(r)
    for c in ("altitud_m", "longitud", "latitud", "anual"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d.to_csv(CACHE, index=False)
    return d


def ajustar_t1(tr: pd.DataFrame):
    X = np.column_stack([np.ones(len(tr)), tr["alt_km"]])
    b, *_ = np.linalg.lstsq(X, tr["T"].values, rcond=None)
    return b


def predecir_t(tr: pd.DataFrame, b, lat: float, lon: float, alt_km: float, con_residuos: bool) -> float:
    t = float(b[0] + b[1] * alt_km)
    if not con_residuos:
        return t
    res = tr["T"].values - (b[0] + b[1] * tr["alt_km"].values)
    dist = np.array([rv.km(lat, lon, la, lo) for la, lo in zip(tr["lat"], tr["lon"])])
    ok = dist <= RADIO_IDW_KM
    if not ok.any():
        return t
    idx = np.argsort(np.where(ok, dist, np.inf))[:K_IDW]
    idx = idx[ok[idx]]
    w = 1.0 / np.maximum(dist[idx], 1.0) ** 2
    return t + float(np.sum(w * res[idx]) / np.sum(w))


def validar_modelos(d: pd.DataFrame, objetivo: str, modelos: dict[str, list[str]]) -> pd.DataFrame:
    filas = []
    for i, te in d.iterrows():
        lejos = np.array([rv.km(te["lat"], te["lon"], r.lat, r.lon) >= BUFFER_KM for r in d.itertuples()])
        otra = np.array([not (isinstance(te["corriente"], str) and isinstance(c, str) and te["corriente"].strip().upper() == c.strip().upper()) for c in d["corriente"]])
        tr = d[lejos & otra & (d.index != i)]
        if len(tr) < 20 or not (te[objetivo] > 0):
            continue
        y = np.log(tr[objetivo].values)
        for m, cols in modelos.items():
            X = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in cols])
            b, _ = rv.ols(X, y)
            lq = float(b @ np.array([1.0] + [te[c] for c in cols]))
            filas.append({"i": i, "codigo": te["codigo"], "region": te["region"], "bloque": te["bloque"], "modelo": m, "eps": lq - math.log(te[objetivo])})
    return pd.DataFrame(filas)


def main():
    t = cargar_temperatura()
    t["depto_n"] = t["departamento"].map(nv.sin_tildes)
    t = t[t["depto_n"].isin(nv.DEPTO2REG) & t["anual"].between(-5, 35) & t["altitud_m"].notna() & t["latitud"].notna()].copy().reset_index(drop=True)
    t = t.rename(columns={"anual": "T", "latitud": "lat", "longitud": "lon"})
    t["alt_km"] = t["altitud_m"] / 1000.0
    t["bloque"] = [f"{math.floor(a)}_{math.floor(b)}" for a, b in zip(t["lat"], t["lon"])]
    R = {"n_estaciones_temperatura": int(len(t)), "por_region": t["departamento"].map(lambda s: nv.DEPTO2REG[nv.sin_tildes(s)]).value_counts().to_dict()}
    print(f"Estaciones de temperatura media: {len(t)}; por region {R['por_region']}", flush=True)

    # paso 1: validacion del campo de temperatura (T1 y T2)
    err = {"T1": [], "T2": []}
    for i, te in t.iterrows():
        lejos = np.array([rv.km(te["lat"], te["lon"], r.lat, r.lon) >= BUFFER_KM for r in t.itertuples()]) & (t.index != i)
        tr = t[lejos]
        if len(tr) < 20:
            err["T1"].append(np.nan); err["T2"].append(np.nan)
            continue
        b = ajustar_t1(tr)
        for k, con in (("T1", False), ("T2", True)):
            err[k].append(predecir_t(tr, b, te["lat"], te["lon"], te["alt_km"], con) - te["T"])
    t["e_T1"], t["e_T2"] = err["T1"], err["T2"]
    v = t.dropna(subset=["e_T1", "e_T2"])
    b_all = ajustar_t1(t)
    da = np.abs(v["e_T2"].values) - np.abs(v["e_T1"].values)
    d12 = {"dif_mediana_abs_C": float(np.median(da)), "ic95": nv.boot_mediana(da, v["bloque"].values), "n": int(len(v))}
    usa_t2 = bool(d12["ic95"][1] < 0)
    R["temperatura"] = {"gradiente_C_por_km": float(b_all[1]), "T0_C": float(b_all[0]),
                        "error_medio_abs_T1_C": float(np.mean(np.abs(v["e_T1"]))), "error_medio_abs_T2_C": float(np.mean(np.abs(v["e_T2"]))),
                        "error_mediano_abs_T1_C": float(np.median(np.abs(v["e_T1"]))), "error_mediano_abs_T2_C": float(np.median(np.abs(v["e_T2"]))),
                        "T2_frente_T1": d12, "se_usa": "T2" if usa_t2 else "T1"}
    print(f"\n== Campo de temperatura (validacion con exclusion de 50 km) ==\n  gradiente {b_all[1]:+.2f} C/km, T a nivel del mar {b_all[0]:.1f} C")
    print(f"  T1 error absoluto: media {R['temperatura']['error_medio_abs_T1_C']:.2f} C, mediana {R['temperatura']['error_mediano_abs_T1_C']:.2f} C")
    print(f"  T2 error absoluto: media {R['temperatura']['error_medio_abs_T2_C']:.2f} C, mediana {R['temperatura']['error_mediano_abs_T2_C']:.2f} C; T2-T1 {d12['dif_mediana_abs_C']:+.3f} [{d12['ic95'][0]:+.3f}, {d12['ic95'][1]:+.3f}] -> se usa {R['temperatura']['se_usa']}", flush=True)

    # paso 2: temperatura de cada cuenca y modelos de la Etapa A
    d = rv.cargar()
    for nombre, con in (("T1", False), ("T2", True)):
        d[f"T_{nombre}"] = [predecir_t(t, b_all, r.lat, r.lon, r.elev_media_m / 1000.0, con) for r in d.itertuples()]
    d["T_cuenca"] = d["T_T2"] if usa_t2 else d["T_T1"]
    d["lTbio"] = np.log(np.clip(d["T_cuenca"], 0.5, 30.0))
    d["lTbio_T1"] = np.log(np.clip(d["T_T1"], 0.5, 30.0))
    d["elev_km"] = d["elev_media_m"] / 1000.0
    R["cuencas"] = {"n": int(len(d)), "T_media_rango_C": [float(d["T_cuenca"].min()), float(d["T_cuenca"].max())],
                    "corr_lTbio_elev_km": float(np.corrcoef(d["lTbio"], d["elev_km"])[0, 1]), "corr_lTbio_lP": float(np.corrcoef(d["lTbio"], d["lP"])[0, 1])}
    print(f"\nCuencas: {len(d)}; T del campo {R['cuencas']['T_media_rango_C'][0]:.1f}-{R['cuencas']['T_media_rango_C'][1]:.1f} C; correlacion ln T_bio con altitud: {R['cuencas']['corr_lTbio_elev_km']:+.2f}, con ln P: {R['cuencas']['corr_lTbio_lP']:+.2f}", flush=True)
    base = ["lA", "lP", "lS"]
    modelos = {"M2": base, "M5": base + ["lTbio"], "M6": base + ["elev_km"]}
    sal = {}
    val10 = None
    for T in rv.TS:
        vv = validar_modelos(d, f"q{T}", modelos)
        if T == 10:
            val10 = vv
        sal[f"T{T}"] = {m: {"n": int(len(g)), "factor_tipico": float(math.exp(np.median(np.abs(g["eps"])))), "sesgo_factor": float(math.exp(np.median(g["eps"])))} for m, g in vv.groupby("modelo")}
    R["validacion"] = sal
    print("\n== Validacion ciega (factor de error tipico; menor es mejor) ==")
    for T in rv.TS:
        s = sal[f"T{T}"]
        print(f"  T={T:>2}: M2 {s['M2']['factor_tipico']:.3f}   M5 (+ temperatura) {s['M5']['factor_tipico']:.3f}   M6 (+ altitud) {s['M6']['factor_tipico']:.3f}")
    prueba = {}
    for a, b, clave in (("M5", "M2", "primario_M5_vs_M2"), ("M6", "M2", "sec_M6_vs_M2"), ("M5", "M6", "sec_M5_vs_M6")):
        prueba[clave] = rv.dif_pareada(val10, a, b)
    R["pruebas_T10"] = prueba
    R["criterio_primario_cumple"] = bool(prueba["primario_M5_vs_M2"]["ic95"][1] < 0)
    print("\n== Pruebas a T = 10 (mediana de |error ln|; negativo = el primero es mejor) ==")
    for k, s in prueba.items():
        print(f"  {k}: {s['dif_mediana_abs_ln']:+.4f} [{s['ic95'][0]:+.4f}, {s['ic95'][1]:+.4f}] (n={s['n']}, bloques={s['bloques']})")
    print(f"  CRITERIO PRIMARIO: {'SE CUMPLE' if R['criterio_primario_cumple'] else 'NO se cumple'}")
    R["por_region_T10"] = {reg: {m: float(math.exp(np.median(np.abs(g[g['modelo'] == m]['eps'])))) for m in ('M2', 'M5', 'M6')} | {"n": int((g['modelo'] == 'M2').sum())} for reg, g in val10.groupby("region")}
    for reg, s in R["por_region_T10"].items():
        print(f"  {reg:<9} n={s['n']:>3}  M2 {s['M2']:.3f}  M5 {s['M5']:.3f}  M6 {s['M6']:.3f}")
    # coeficientes con todas las cuencas (T = 10) para M5, con IC95 por bloques
    y = np.log(d["q10"].values)
    X = np.column_stack([np.ones(len(d)), d["lA"], d["lP"], d["lS"], d["lTbio"]])
    b, _ = rv.ols(X, y)
    et = d["bloque"].unique()
    grupos = {k: np.where(d["bloque"].values == k)[0] for k in et}
    bs = []
    for _ in range(rv.N_BOOT):
        ii = np.concatenate([grupos[k] for k in rv.RNG.choice(et, len(et), replace=True)])
        bs.append(rv.ols(X[ii], y[ii])[0])
    ic = np.percentile(np.array(bs), [2.5, 97.5], axis=0)
    R["coef_M5_T10"] = {n: {"valor": float(b[k]), "ic95": [float(ic[0, k]), float(ic[1, k])]} for k, n in enumerate(["const", "ln_A", "ln_P", "ln_S", "ln_Tbio"])}
    print("\n  coeficientes M5 (T = 10, todas las cuencas):", {n: f"{v['valor']:+.2f} [{v['ic95'][0]:+.2f},{v['ic95'][1]:+.2f}]" for n, v in R["coef_M5_T10"].items()})
    # sensibilidad: T1 en lugar de T2 (si se uso T2)
    if usa_t2:
        d2 = d.copy(); d2["lTbio"] = d2["lTbio_T1"]
        v2 = validar_modelos(d2, "q10", {"M2": base, "M5": base + ["lTbio"]})
        s2 = rv.dif_pareada(v2, "M5", "M2")
        R["sens_T1"] = s2
        print(f"  sensibilidad con T1: M5 frente a M2 {s2['dif_mediana_abs_ln']:+.4f} [{s2['ic95'][0]:+.4f}, {s2['ic95'][1]:+.4f}]")
    d[["codigo", "region", "bloque", "elev_media_m", "lluvia_media_mm", "T_T1", "T_T2", "T_cuenca"]].to_csv(AQUI / "regimen_termico_cuencas.csv", index=False)
    (AQUI / "regimen_termico_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("\nlisto")


if __name__ == "__main__":
    main()
