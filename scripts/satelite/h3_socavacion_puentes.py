"""H3 (#273): índice de riesgo de socavación y continuidad vial. Protocolo: PROTOCOLO_ANALISIS.md §27, fijado antes de
leer el resultado (puentes averiados por eventos hídricos en 2023-2024).

Índice fijo (sin ajuste a datos): media de rangos percentiles de tres componentes conocidos antes de 2023:
  H = log(1 + puentes vehiculares averiados por eventos hídricos 2019-2022)          historial (UNGRD)
  T = Q10/Q2 (GEV, §21) de la estación IDEAM con ajuste estable más cercana ≤ 50 km   torrencialidad de crecientes
  S = pendiente p90 del DEM municipal (%)                                              relieve (crecientes súbitas)
Resultado: Y = 1 si el municipio tuvo ≥ 1 puente vehicular averiado por inundación, creciente súbita o avenida torrencial
en 2023-2024.

Uso (con python -I): primero h3_descargar_insumos.py (entorno con supabase, solo lectura), luego con pandas:
  python h3_socavacion_puentes.py --conteo    # muestra, cobertura de componentes y n de positivos SOLO de 2019-2022
  python h3_socavacion_puentes.py             # análisis confirmatorio
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
INSUMOS = AQUI / "_cache" / "h3_insumos.json"

# Copiados de contraste_sgc_vs_ungrd.py y sesgo_reporte_ungrd.py (§26) para no requerir statsmodels ni supabase aquí
REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
REG = {d: r for r, ds in REGIONES.items() for d in ds.split()}
ESTRUCTURALES = {"INCENDIO ESTRUCTURAL", "COLAPSO ESTRUCTURAL"}


def auc(x: np.ndarray, y: np.ndarray) -> float:
    r = rankdata(x)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def parcial(x, y, Z):
    rx, ry = rankdata(x), rankdata(y)
    A = np.c_[np.ones(len(x)), *[rankdata(z) for z in Z]]
    res = lambda a: a - A @ np.linalg.lstsq(A, a, rcond=None)[0]  # noqa: E731
    return np.corrcoef(res(rx), res(ry))[0, 1]

N_BOOT = 2000
RNG = np.random.default_rng(273)
HIDRICOS = {"INUNDACION", "CRECIENTE SUBITA", "AVENIDA TORRENCIAL"}
KM_MAX_ESTACION = 50.0
ANIOS_PREDICTOR, ANIOS_RESULTADO = (2019, 2022), (2023, 2024)
MIN_POSITIVOS = 30


def insumos() -> dict:
    if not INSUMOS.exists():
        raise SystemExit("Falta _cache/h3_insumos.json: corra antes h3_descargar_insumos.py")
    return json.loads(INSUMOS.read_text(encoding="utf-8"))


def cargar_ungrd(ins: dict) -> pd.DataFrame:
    d = pd.DataFrame(ins["ungrd"])
    d["anio"] = pd.to_datetime(d["fecha"], errors="coerce").dt.year
    d["ev"] = d["evento"].fillna("").str.upper().str.strip()
    for c in ("puentes_vehiculares", "puentes_peatonales"):
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    return d


def _km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def torrencialidad(ins: dict, centroides: pd.DataFrame) -> pd.DataFrame:
    """Q10/Q2 de la estación con GEV estable (|ξ| ≤ 0,5) más cercana al centroide, si está a ≤ 50 km."""
    est = {e["codigo"]: e for e in ins["estaciones"]}
    filas = []
    for r in json.loads((AQUI / "frecuencia_crecientes_ideam.json").read_text(encoding="utf-8")):
        q = r.get("q_gev")
        q = ast.literal_eval(q) if isinstance(q, str) else q
        xi = float(r.get("xi", "nan"))
        e = est.get(r["codigo"])
        if not (q and e and e.get("latitud") is not None and math.isfinite(xi) and abs(xi) <= 0.5):
            continue
        q2, q10 = float(q.get("2") or q.get(2) or 0), float(q.get("10") or q.get(10) or 0)
        if q2 > 0 and q10 > 0:
            filas.append((r["codigo"], e["latitud"], e["longitud"], q10 / q2))
    E = pd.DataFrame(filas, columns=["est", "lat", "lon", "T"])
    out = []
    for _, m in centroides.iterrows():
        d = _km(m["lat"], m["lon"], E["lat"].values, E["lon"].values)
        i = int(np.argmin(d))
        out.append((m["codigo"], E["T"].iat[i] if d[i] <= KM_MAX_ESTACION else np.nan, float(d[i])))
    return pd.DataFrame(out, columns=["codigo", "T", "km_estacion"]), len(E)


def preparar(ins: dict) -> tuple[pd.DataFrame, dict]:
    panel = pd.read_csv(AQUI / "v1_panel.csv", dtype={"codigo": str})
    panel["codigo"] = panel["codigo"].str.zfill(5)
    dem = {m["codigo"]: m for m in json.loads((AQUI / "dem_poligonos_colombia.json").read_text(encoding="utf-8"))["municipios"]
           if "error" not in m}
    cent = pd.DataFrame(ins["centroides"], columns=["codigo", "lat", "lon"])
    panel = panel[panel["codigo"].isin(dem) & panel["codigo"].isin(set(cent["codigo"]))].copy()
    panel["S"] = [dem[c]["pend_p90_pct"] for c in panel["codigo"]]
    tor, n_estaciones = torrencialidad(ins, cent[cent["codigo"].isin(set(panel["codigo"]))])
    panel = panel.merge(tor, on="codigo", how="left")

    ung = cargar_ungrd(ins)
    hid = ung[ung["ev"].isin(HIDRICOS)]
    pre = hid[hid["anio"].between(*ANIOS_PREDICTOR)].groupby("codigo_municipio")["puentes_vehiculares"].sum()
    panel["H"] = np.log1p(panel["codigo"].map(pre).fillna(0))
    n_est = ung[ung["ev"].isin(ESTRUCTURALES)].groupby("codigo_municipio").size()   # P_A como en §26
    panel["n_estructural"] = panel["codigo"].map(n_est).fillna(0)
    panel["P_A"] = np.log1p(panel["n_estructural"] / panel["poblacion"] * 1e5)
    panel["log_pob"] = np.log(panel["poblacion"])
    panel["depto2"] = panel["codigo"].str[:2]
    panel["region"] = panel["depto2"].map(REG)

    # Índice fijo: T faltante (sin estación ≤ 50 km) se imputa con la mediana del rango, 0,5 (neutro)
    pr = lambda x: (rankdata(x) - 0.5) / len(x)  # noqa: E731
    rT = np.full(len(panel), 0.5)
    ok = panel["T"].notna().values
    rT[ok] = pr(panel.loc[ok, "T"].values)
    panel["rH"], panel["rT"], panel["rS"] = pr(panel["H"].values), rT, pr(panel["S"].values)
    panel["indice"] = (panel["rH"] + panel["rT"] + panel["rS"]) / 3
    meta = {"n_estaciones_utiles": n_estaciones, "con_estacion_50km": int(ok.sum())}
    return panel.reset_index(drop=True), meta, ung


def resultado(panel: pd.DataFrame, ung: pd.DataFrame, incluir_peatonales: bool = False) -> np.ndarray:
    hid = ung[ung["ev"].isin(HIDRICOS) & ung["anio"].between(*ANIOS_RESULTADO)]
    col = hid["puentes_vehiculares"] + (hid["puentes_peatonales"] if incluir_peatonales else 0)
    tot = col.groupby(hid["codigo_municipio"]).sum()
    return panel["codigo"].map(tot).fillna(0).values


def boot(fun, bloques):
    et = np.unique(bloques)
    idx = {b: np.where(bloques == b)[0] for b in et}
    vals = []
    for _ in range(N_BOOT):
        ix = np.concatenate([idx[b] for b in RNG.choice(et, len(et), replace=True)])
        try:
            v = fun(ix)
        except Exception:
            continue
        if np.isfinite(v):
            vals.append(v)
    return [float(v) for v in np.percentile(vals, [2.5, 97.5])]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--conteo", action="store_true")
    a = ap.parse_args()
    ins = insumos()
    p, meta, ung = preparar(ins)
    if a.conteo:
        print(f"municipios: {len(p)} en {p['depto2'].nunique()} departamentos; {meta}")
        print("con puentes hídricos 2019-2022 (H > 0):", int((p["H"] > 0).sum()))
        print("por región:", p["region"].value_counts().to_dict())
        print("T: mediana", round(float(p["T"].median()), 2), "| S: mediana", round(float(p["S"].median()), 1))
        print("ρ entre componentes:", {k: round(float(spearmanr(p[x], p[y], nan_policy='omit')[0]), 2)
                                       for k, (x, y) in {"H-T": ("H", "T"), "H-S": ("H", "S"), "T-S": ("T", "S")}.items()})
        return
    y_cnt = resultado(p, ung)
    y = (y_cnt >= 1).astype(int)
    salida = "vehiculares"
    if y.sum() < MIN_POSITIVOS:                # regla prerregistrada: pocos positivos → se suman peatonales
        y_cnt = resultado(p, ung, incluir_peatonales=True)
        y = (y_cnt >= 1).astype(int)
        salida = "vehiculares + peatonales (regla de potencia)"
    b = p["depto2"].values
    I, H, T, S = p["indice"].values, p["rH"].values, p["rT"].values, p["rS"].values
    y2 = y_cnt / p["area_km2"].values * 100
    R = {"n": len(p), "positivos": int(y.sum()), "salida": salida, **meta}
    R["C1_auc_indice"] = [float(auc(I, y)), boot(lambda i: auc(I[i], y[i]), b)]
    R["C2_delta_auc_vs_historial"] = [float(auc(I, y) - auc(H, y)), boot(lambda i: auc(I[i], y[i]) - auc(H[i], y[i]), b)]
    Z = [p["log_pob"].values, p["P_A"].values]
    R["C3_parcial_poblacion_reporte"] = [float(parcial(I, y2, Z)), boot(lambda i: parcial(I[i], y2[i], [z[i] for z in Z]), b)]
    R["auc_componentes"] = {k: float(auc(v, y)) for k, v in {"H": H, "T": T, "S": S}.items()}
    ok = p["T"].notna().values
    R["sensibilidad_solo_con_estacion"] = {"n": int(ok.sum()), "positivos": int(y[ok].sum()),
                                           "auc_indice": float(auc(I[ok], y[ok])), "auc_T": float(auc(T[ok], y[ok]))}
    a4 = {f["codigo"]: f["aa"] for f in ins["a4"]}
    aa = p["codigo"].map(a4).astype(float).values
    m = np.isfinite(aa)
    R["descriptivo_auc_aa_nsr10"] = float(auc(aa[m], y[m]))
    R["auc_por_region"] = {}
    for reg, g in p.groupby("region"):
        yy = y[g.index]
        if len(g) >= 30 and 0 < yy.sum() < len(g):
            R["auc_por_region"][reg] = [len(g), int(yy.sum()), float(auc(I[g.index], yy))]
    print(json.dumps(R, ensure_ascii=False, indent=1))
    (AQUI / "h3_socavacion_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
