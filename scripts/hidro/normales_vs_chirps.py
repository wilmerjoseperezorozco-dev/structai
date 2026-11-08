"""H1: lluvia media anual de CHIRPS v3 frente a las normales climatologicas 1991-2020 del IDEAM, correccion y efecto en la Etapa A.
Protocolo: PROTOCOLO_NORMALES_CHIRPS.md (preregistrado antes de comparar). Entradas: _cache/normales_precip_1991_2020.csv (datos.gov.co nsz2-kzcq),
_cache/lluvia_media_anual_1991_2020.npz, cuencas_estaciones.csv. Salidas: normales_chirps_resultados.json, normales_chirps_estaciones.csv
"""
from __future__ import annotations

import json
import math
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from affine import Affine

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import regionalizacion_validacion as rv  # noqa: E402

RNG = np.random.default_rng(20261108)
N_BOOT = 3000
BUFFER_KM = 50.0
BANDAS_ALT = [(0, 500), (500, 1500), (1500, 2500), (2500, 9999)]
CLASES_P = [(0, 1000), (1000, 2000), (2000, 3500), (3500, 99999)]
DEPTOS = {
    "Caribe": ["ATLANTICO", "BOLIVAR", "CESAR", "CORDOBA", "LA GUAJIRA", "MAGDALENA", "SUCRE"],
    "Andina": ["ANTIOQUIA", "BOYACA", "CALDAS", "CUNDINAMARCA", "HUILA", "NORTE DE SANTANDER", "QUINDIO", "RISARALDA", "SANTANDER", "TOLIMA"],
    "Pacifica": ["CAUCA", "NARINO", "VALLE DEL CAUCA"],
    "Orinoquia": ["META"],
}
DEPTO2REG = {d: r for r, ds in DEPTOS.items() for d in ds}


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").upper().strip()


def muestrear(mm: np.ndarray, tr: Affine, lat: np.ndarray, lon: np.ndarray, ventana: int) -> np.ndarray:
    out = np.full(len(lat), np.nan)
    for k, (la, lo) in enumerate(zip(lat, lon)):
        col, fila = ~tr * (lo, la)
        r, c = int(math.floor(fila)), int(math.floor(col))
        h = ventana // 2
        if r - h < 0 or c - h < 0 or r + h >= mm.shape[0] or c + h >= mm.shape[1]:
            continue
        z = mm[r - h:r + h + 1, c - h:c + h + 1]
        if np.isfinite(z).any():
            out[k] = np.nanmean(z)
    return out


def boot_mediana(x: np.ndarray, bloques: np.ndarray) -> list[float]:
    et = np.unique(bloques)
    idx = {k: np.where(bloques == k)[0] for k in et}
    bs = [np.median(x[np.concatenate([idx[k] for k in RNG.choice(et, len(et), replace=True)])]) for _ in range(N_BOOT)]
    return [float(v) for v in np.percentile(bs, [2.5, 97.5])]


def resumen(e: np.ndarray, bloques: np.ndarray) -> dict:
    return {"n": int(len(e)), "bloques": int(len(np.unique(bloques))),
            "sesgo_factor": float(math.exp(np.median(e))), "sesgo_ic95": [float(math.exp(v)) for v in boot_mediana(e, bloques)],
            "error_tipico_factor": float(math.exp(np.median(np.abs(e)))),
            "cuantiles_factor": {q: float(math.exp(np.percentile(e, q))) for q in (5, 25, 50, 75, 95)},
            "dentro_20pct": float(np.mean(np.abs(np.expm1(e)) <= 0.20))}


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def corregir(tr: pd.DataFrame, te: dict, modelo: str) -> float:
    """ln(P corregida) para la estacion/cuenca `te` (con ln_chirps, alt_km, region), entrenando con `tr`."""
    if modelo == "C0":
        return te["ln_chirps"]
    if modelo == "C1":
        g = tr[tr["region"] == te["region"]]
        g = g if len(g) >= 5 else tr
        return te["ln_chirps"] + float(np.median(g["ln_normal"] - g["ln_chirps"]))
    regs = sorted(tr["region"].unique())
    D = np.column_stack([(tr["region"] == r).astype(float) for r in regs[1:]]) if len(regs) > 1 else np.empty((len(tr), 0))
    b = ols(np.column_stack([np.ones(len(tr)), tr["ln_chirps"], tr["alt_km"], D]), tr["ln_normal"].values)
    x = [1.0, te["ln_chirps"], te["alt_km"]] + [float(te["region"] == r) for r in regs[1:]]
    return float(np.dot(b, x))


def lobo(d: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for i, te in d.iterrows():
        lejos = np.array([rv.km(te["lat"], te["lon"], r.lat, r.lon) >= BUFFER_KM for r in d.itertuples()])
        tr = d[lejos & (d.index != i)]
        if len(tr) < 20:
            continue
        t = te.to_dict()
        f = {"i": i, "bloque": te["bloque"], "region": te["region"]}
        for m in ("C0", "C1", "C2"):
            f[m] = corregir(tr, t, m) - te["ln_normal"]
        filas.append(f)
    return pd.DataFrame(filas)


def dif(v: pd.DataFrame, a: str, b: str) -> dict:
    da = np.abs(v[a].values) - np.abs(v[b].values)
    return {"dif_mediana_abs_ln": float(np.median(da)), "ic95": boot_mediana(da, v["bloque"].values), "n": int(len(v)), "bloques": int(v["bloque"].nunique())}


def tabla_por(d: pd.DataFrame, col: str, grupos) -> dict:
    out = {}
    for g in grupos:
        s = d[(d[col] >= g[0]) & (d[col] < g[1])] if isinstance(g, tuple) else d[d[col] == g]
        if len(s) >= 8:
            out[str(g)] = resumen(s["e"].values, s["bloque"].values)
    return out


def main():
    n = pd.read_csv(AQUI / "_cache" / "normales_precip_1991_2020.csv")
    n["depto_n"] = n["departamento"].map(sin_tildes)
    n["region"] = n["depto_n"].map(DEPTO2REG)
    z = np.load(AQUI / "_cache" / "lluvia_media_anual_1991_2020.npz")
    tr = Affine(*[float(v) for v in z["transform"]])
    mm = z["mm"]
    n["chirps"] = muestrear(mm, tr, n["latitud"].values, n["longitud"].values, 1)
    n["chirps3"] = muestrear(mm, tr, n["latitud"].values, n["longitud"].values, 3)
    R = {"n_normales_total": int(len(n))}
    fuera = n[n["region"].isna()]
    R["otras_regiones"] = {"n": int(len(fuera))}
    d = n[n["region"].notna() & n["anual"].between(100, 15000) & n["chirps"].notna() & (n["chirps"] > 0)].copy().reset_index(drop=True)
    R["n_analisis"] = int(len(d))
    R["descartadas_sin_chirps"] = int((n["region"].notna() & n["chirps"].isna()).sum())
    d["lat"], d["lon"] = d["latitud"], d["longitud"]
    d["bloque"] = [f"{math.floor(a)}_{math.floor(b)}" for a, b in zip(d["lat"], d["lon"])]
    d["ln_normal"], d["ln_chirps"] = np.log(d["anual"]), np.log(d["chirps"])
    d["e"] = d["ln_chirps"] - d["ln_normal"]
    d["alt_km"] = d["altitud_m"] / 1000.0
    R["por_region_n"] = d["region"].value_counts().to_dict()
    print(f"Estaciones del analisis: {len(d)} en {d['bloque'].nunique()} bloques; por region {R['por_region_n']}; sin dato CHIRPS: {R['descartadas_sin_chirps']}", flush=True)

    R["acuerdo_global"] = resumen(d["e"].values, d["bloque"].values)
    R["acuerdo_region"] = tabla_por(d, "region", sorted(d["region"].unique()))
    R["acuerdo_altitud"] = tabla_por(d, "altitud_m", BANDAS_ALT)
    R["acuerdo_clase_lluvia"] = tabla_por(d, "anual", CLASES_P)
    for k, v in (("global", R["acuerdo_global"]),):
        print(f"\n== Acuerdo CHIRPS / normal (antes de corregir) ==\n  {k}: sesgo x{v['sesgo_factor']:.2f} IC95 [{v['sesgo_ic95'][0]:.2f}, {v['sesgo_ic95'][1]:.2f}], error tipico x{v['error_tipico_factor']:.2f}, dentro de 20 %: {100 * v['dentro_20pct']:.0f} %")
    for nombre in ("acuerdo_region", "acuerdo_altitud", "acuerdo_clase_lluvia"):
        for g, v in R[nombre].items():
            print(f"  {nombre[8:]:<12} {g:<14} n={v['n']:>4}  sesgo x{v['sesgo_factor']:.2f} [{v['sesgo_ic95'][0]:.2f},{v['sesgo_ic95'][1]:.2f}]  error tipico x{v['error_tipico_factor']:.2f}")

    # sensibilidades del acuerdo
    d3 = d.dropna(subset=["chirps3"]).copy()
    R["sens_3x3"] = resumen((np.log(d3["chirps3"]) - d3["ln_normal"]).values, d3["bloque"].values)
    d5 = d[d["ao"] <= 5]
    R["sens_ao_le_5"] = resumen(d5["e"].values, d5["bloque"].values)
    print(f"\n  sensibilidad 3x3: sesgo x{R['sens_3x3']['sesgo_factor']:.2f}, error tipico x{R['sens_3x3']['error_tipico_factor']:.2f}; ao<=5 (n={len(d5)}): sesgo x{R['sens_ao_le_5']['sesgo_factor']:.2f}, error tipico x{R['sens_ao_le_5']['error_tipico_factor']:.2f}", flush=True)

    # correccion con validacion dejando fuera estaciones a menos de 50 km
    v = lobo(d)
    R["correccion"] = {m: {"error_tipico_factor": float(math.exp(np.median(np.abs(v[m])))), "sesgo_factor": float(math.exp(np.median(v[m])))} for m in ("C0", "C1", "C2")}
    R["criterio_primario_C1_vs_C0"] = dif(v, "C1", "C0")
    R["sec_C2_vs_C0"] = dif(v, "C2", "C0")
    R["sec_C2_vs_C1"] = dif(v, "C2", "C1")
    p = R["criterio_primario_C1_vs_C0"]
    R["criterio_primario_cumple"] = bool(p["ic95"][1] < 0)
    print("\n== Correccion (validacion con zona de exclusion de 50 km) ==")
    for m, r in R["correccion"].items():
        print(f"  {m}: error tipico x{r['error_tipico_factor']:.3f}, sesgo x{r['sesgo_factor']:.3f}")
    print(f"  PRIMARIO C1 frente a C0: dif {p['dif_mediana_abs_ln']:+.4f} IC95 [{p['ic95'][0]:+.4f}, {p['ic95'][1]:+.4f}] n={p['n']} -> {'SE CUMPLE' if R['criterio_primario_cumple'] else 'NO se cumple'}")
    for k in ("sec_C2_vs_C0", "sec_C2_vs_C1"):
        s = R[k]
        print(f"  {k}: {s['dif_mediana_abs_ln']:+.4f} [{s['ic95'][0]:+.4f}, {s['ic95'][1]:+.4f}]")
    R["correccion_por_region"] = {}
    for reg, g in v.groupby("region"):
        R["correccion_por_region"][reg] = {m: float(math.exp(np.median(np.abs(g[m])))) for m in ("C0", "C1", "C2")} | {"n": int(len(g))}
        print(f"  {reg:<9} n={len(g):>4}  C0 x{R['correccion_por_region'][reg]['C0']:.3f}  C1 x{R['correccion_por_region'][reg]['C1']:.3f}  C2 x{R['correccion_por_region'][reg]['C2']:.3f}")

    # efecto en la Etapa A: predictor de lluvia de cada cuenca corregido sin las normales a menos de 50 km de la estacion de caudal
    dA = rv.cargar()
    base = dA.copy()
    esc = {}
    for m in ("C1", "C2"):
        nuevo = dA.copy()
        lp = []
        for _, b in dA.iterrows():
            lejos = np.array([rv.km(b["lat"], b["lon"], r.lat, r.lon) >= BUFFER_KM for r in d.itertuples()])
            te = {"ln_chirps": math.log(b["lluvia_media_mm"]), "alt_km": float(b["elev_media_m"]) / 1000.0, "region": b["region"]}
            lp.append(corregir(d[lejos], te, m))
        nuevo["lP"] = lp
        nuevo["lluvia_media_mm"] = np.exp(lp)
        esc[m] = nuevo
    val0 = rv.validar(base, "q10")
    out = {}
    for m, dd in esc.items():
        vv = rv.validar(dd, "q10")
        s0, s1 = rv.resumen(val0)["M2"], rv.resumen(vv)["M2"]
        mix = pd.concat([val0[val0["modelo"] == "M2"].assign(modelo="M2_C0"), vv[vv["modelo"] == "M2"].assign(modelo=f"M2_{m}")])
        out[m] = {"factor_tipico_C0": s0["factor_tipico"], "factor_tipico_corregido": s1["factor_tipico"],
                  "dif_pareada": rv.dif_pareada(mix, f"M2_{m}", "M2_C0"),
                  "factor_tipico_M1_corregido": rv.resumen(vv)["M1"]["factor_tipico"], "factor_tipico_M1_C0": rv.resumen(val0)["M1"]["factor_tipico"],
                  "cambio_mediano_predictor_pct": float(100 * np.median(np.exp(dd["lP"] - base["lP"]) - 1))}
        o = out[m]
        print(f"\n== Etapa A con lluvia corregida {m} (T = 10) ==\n  M2: factor tipico {o['factor_tipico_C0']:.3f} -> {o['factor_tipico_corregido']:.3f}; dif pareada {o['dif_pareada']['dif_mediana_abs_ln']:+.4f} [{o['dif_pareada']['ic95'][0]:+.4f}, {o['dif_pareada']['ic95'][1]:+.4f}]; "
              f"M1: {o['factor_tipico_M1_C0']:.3f} -> {o['factor_tipico_M1_corregido']:.3f}; cambio mediano del predictor {o['cambio_mediano_predictor_pct']:+.1f} %", flush=True)
    R["etapa_A_escenarios"] = out

    d.drop(columns=["depto_n"]).to_csv(AQUI / "normales_chirps_estaciones.csv", index=False)
    (AQUI / "normales_chirps_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("\nlisto")


if __name__ == "__main__":
    main()
