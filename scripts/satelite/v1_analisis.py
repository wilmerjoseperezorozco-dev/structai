"""V1: confirmacion y refinamiento. Protocolo: PROTOCOLO_V1_CONFIRMACION.md (fijado antes de calcular).

Entrada: v1_municipal.json (v1_municipal.py). Salidas: v1_panel.csv y v1_resultados.json.
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
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.contingency_tables import StratifiedTable

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

warnings.filterwarnings("ignore")
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DESCUBRIMIENTO = ["08", "13", "20", "23", "44", "47", "70"]
CONFIRMACION = ["63", "66", "17", "15", "25", "41", "73", "68", "54", "76", "19", "52", "50", "05"]
REGION = {**{d: "Caribe" for d in DESCUBRIMIENTO}, **{d: "Andina" for d in ["05", "15", "17", "25", "41", "54", "63", "66", "68", "73"]},
          **{d: "Pacifica" for d in ["19", "52", "76"]}, "50": "Orinoquia"}
KM_MIN = 5.0
KM_MIN_TIPO = 2.0
RHO_MIN = 0.15
N_BOOT = 4000
RNG = np.random.default_rng(20261108)
FLOOD = ["INUNDACION", "INUNDACIÓN", "INUNDACIoN", "CRECIENTE SUBITA", "Creciente Subita", "AVENIDA TORRENCIAL"]


def num(s):
    return pd.to_numeric(s, errors="coerce").fillna(0)


def construir_panel() -> pd.DataFrame:
    m = pd.DataFrame(json.loads((AQUI / "v1_municipal.json").read_text(encoding="utf-8"))["municipios"])
    m = m[m["depto"].isin(DESCUBRIMIENTO + CONFIRMACION)].copy()
    codigos = list(m["codigo"])
    pols = dc.poligonos(sorted(set(m["depto"])))
    pob = dc.poblacion_dane(codigos)
    sis = dc.sisben(codigos)
    nbi = pd.read_excel(AQUI / "_cache/nbi/nbi_municipal.xlsx")
    nbi = nbi.dropna(subset=["DIVIPOLA"])
    nbi["codigo"] = nbi["DIVIPOLA"].astype(int).astype(str).str.zfill(5)
    nbi = nbi.set_index("codigo")["NBI 2018"].to_dict()
    chirps = json.loads((AQUI / "chirps_mensual_colombia.json").read_text(encoding="utf-8"))["municipios"]
    ung = pd.DataFrame(dc.ungrd(codigos))
    for c in ("personas", "viviendas_destruidas", "viviendas_averiadas"):
        ung[c] = num(ung[c])
    ung["viv"] = ung["viviendas_destruidas"] + ung["viviendas_averiadas"]
    g_all = ung.groupby("codigo_municipio")["viv"].sum()
    g_flood = ung[ung["evento"].isin(FLOOD)].groupby("codigo_municipio")
    n_flood = g_flood.size()
    viv_flood = g_flood["viv"].sum()
    n_mm = ung[ung["evento"] == "MOVIMIENTO EN MASA"].groupby("codigo_municipio").size()
    n_inc = ung[ung["evento"] == "INCENDIO FORESTAL"].groupby("codigo_municipio").size()
    filas = []
    for r in m.to_dict("records"):
        c = r["codigo"]
        if c not in pob or c not in pols:
            continue
        p, area = pob[c]["poblacion"], pols[c]["area_km2"]
        f = {"codigo": c, "municipio": r["municipio"], "depto": r["depto"], "region": REGION[r["depto"]], "poblacion": p, "area_km2": area,
             "pct_cabecera": pob[c]["pct_cabecera"], "frac_hand": r["frac_hand_lt10"],
             "viv_danadas": float(g_all.get(c, 0.0)), "viv_inund": float(viv_flood.get(c, 0.0)),
             "n_inund": int(n_flood.get(c, 0)), "n_mm": int(n_mm.get(c, 0)), "n_incendio": int(n_inc.get(c, 0)),
             "pct_mat_vulnerable": float(sis[c]["pct_material_vulnerable"]) if c in sis and sis[c].get("pct_material_vulnerable") is not None else None,
             "nbi2018": nbi.get(c)}
        if c in chirps:
            f["lluvia_p95"] = float(np.percentile(np.array(chirps[c]["precip_mm"], float), 95))
        km = r["km_via"]
        f["km_via"] = km
        f["expo_vial"] = r["km_bajo"] / km if km >= KM_MIN else None
        for t in ("trunk", "primary", "secondary"):
            f[f"expo_{t}"] = r[f"km_{t}_bajo"] / r[f"km_{t}"] if r[f"km_{t}"] >= KM_MIN_TIPO else None
            f[f"km_{t}"] = r[f"km_{t}"]
        n = r["n_lugares"]
        f["n_lugares"] = n
        f["lug_bajo_cerca"] = r["n_lugares_bajo_cerca"] / n if n >= 3 else None
        d = r.get("cab_dist_via_m")
        f["cab_bajo_en_via"] = float(bool(r.get("cab_bajo")) and d is not None and d <= 1000) if "cab_bajo" in r and r["cab_bajo"] is not None else None
        f["_cerca"], f["_lejos"], f["_bajo_cerca"], f["_bajo_lejos"] = r["n_lugares_cerca"], n - r["n_lugares_cerca"], r["n_lugares_bajo_cerca"], r["n_lugares_bajo"] - r["n_lugares_bajo_cerca"]
        for k, v in (("viv_danadas", "viv_danadas"), ("viv_inund", "viv_inund"), ("n_inund", "n_inund"), ("n_mm", "n_mm"), ("n_incendio", "n_incendio")):
            f[k + "_x100k"] = f[v] / p * 1e5
        filas.append(f)
    return pd.DataFrame(filas)


def residuos(d, y, x, ctrl):
    rk = stats.rankdata
    Z = np.column_stack([rk(np.log(d["poblacion"])), rk(np.log(d["area_km2"]))] + [rk(d[c]) for c in ctrl] + [np.ones(len(d))])
    res = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return res(rk(d[y])), res(rk(d[x]))


def parcial(d, y, x, ctrl):
    d = d.dropna(subset=[y, x] + ctrl)
    if len(d) < 30 or d[x].nunique() < 5 or d[y].nunique() < 5:
        return None
    a, b = residuos(d, y, x, ctrl)
    return float(np.corrcoef(a, b)[0, 1]), len(d), d


def parcial_ic(d, y, x, ctrl):
    base = parcial(d, y, x, ctrl)
    if base is None:
        return None
    r, n, dd = base
    deps = dd["depto"].unique()
    grupos = {k: v for k, v in dd.groupby("depto")}
    bs = []
    for _ in range(N_BOOT):
        s = RNG.choice(deps, len(deps), replace=True)
        x_ = pd.concat([grupos[k] for k in s])
        if x_[x].nunique() > 5 and x_[y].nunique() > 5:
            a, b = residuos(x_, y, x, ctrl)
            bs.append(np.corrcoef(a, b)[0, 1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"rho": r, "n": n, "n_deptos": len(deps), "ic95": [float(lo), float(hi)]}


def glm(d, y, cols, fe=True, extra=None):
    x = d.dropna(subset=cols + [y]).copy()
    X = x[cols].astype(float)
    X = (X - X.mean()) / X.std(ddof=0).replace(0, 1) if False else X
    if fe:
        X = pd.concat([X, pd.get_dummies(x["depto"], prefix="d", drop_first=True).astype(float)], axis=1)
    X = sm.add_constant(X)
    mod = sm.GLM(x[y], X, family=sm.families.Poisson(), offset=np.log(x["poblacion"]))
    return mod.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(x["depto"])[0]}), len(x)


def rr(res, col, paso):
    b, se = res.params[col], res.bse[col]
    return {"rr": float(math.exp(b * paso)), "ic95": [float(math.exp((b - 1.96 * se) * paso)), float(math.exp((b + 1.96 * se) * paso))], "p": float(res.pvalues[col])}


def holm(ps):
    o = np.argsort(ps); m = len(ps); out = np.empty(m); prev = 0.0
    for i, idx in enumerate(o):
        prev = max(prev, min(1.0, ps[idx] * (m - i))); out[idx] = prev
    return out


def main():
    panel = construir_panel()
    panel.to_csv(AQUI / "v1_panel.csv", index=False)
    conf = panel[panel["depto"].isin(CONFIRMACION)]
    desc = panel[panel["depto"].isin(DESCUBRIMIENTO)]
    print(f"Panel: {len(panel)} municipios ({len(desc)} descubrimiento, {len(conf)} confirmacion); departamentos en confirmacion con datos: {sorted(conf['depto'].unique())}")
    faltan = [d for d in CONFIRMACION if d not in set(conf['depto'])]
    print(f"Departamentos de confirmacion sin procesar: {faltan}")
    R = {"faltan": faltan}
    ctrl = ["frac_hand"]
    print("\n== C-1 (confirmatoria) y comparacion ==")
    for nombre, d in (("confirmacion", conf), ("descubrimiento (recalculado con esta tuberia)", desc), ("conjunta", panel)):
        for y in ("viv_danadas_x100k", "viv_inund_x100k", "n_inund_x100k"):
            r = parcial_ic(d, y, "expo_vial", ctrl)
            R[f"C1|{nombre}|{y}"] = r
            if r:
                print(f"{nombre:<46}{y:<20} rho={r['rho']:+.2f} n={r['n']} deptos={r['n_deptos']} IC95 [{r['ic95'][0]:+.2f}, {r['ic95'][1]:+.2f}]")
    c1 = R["C1|confirmacion|viv_danadas_x100k"]
    ok = bool(c1 and c1["ic95"][0] > 0 and c1["rho"] >= RHO_MIN)
    R["C1_confirmada"] = ok
    print(f"\n>>> C-1 {'SE CONFIRMA' if ok else 'NO se confirma'} (criterio: IC95 inferior > 0 y rho >= {RHO_MIN})")
    print("\nPor region (descriptivo), resultado primario:")
    for reg, d in panel.groupby("region"):
        r = parcial_ic(d, "viv_danadas_x100k", "expo_vial", ctrl)
        R[f"region|{reg}"] = r
        if r:
            print(f"  {reg:<10} rho={r['rho']:+.2f} n={r['n']} deptos={r['n_deptos']} IC95 [{r['ic95'][0]:+.2f}, {r['ic95'][1]:+.2f}]")

    print("\n== R1 efectos fijos de departamento, cuasi-Poisson, razon de tasas por +0,10 de exposicion vial ==")
    cov = ["expo_vial", "frac_hand", "pct_cabecera", "pct_mat_vulnerable", "nbi2018", "lluvia_p95"]
    for nombre, d in (("conjunta", panel), ("confirmacion", conf), ("descubrimiento", desc)):
        d = d.copy(); d["log_area"] = np.log(d["area_km2"])
        res, n = glm(d, "viv_danadas", cov + ["log_area"])
        R[f"R1|{nombre}"] = {"n": n, **rr(res, "expo_vial", 0.10)}
        print(f"  {nombre:<15} n={n}  RR={R[f'R1|{nombre}']['rr']:.2f} IC95 [{R[f'R1|{nombre}']['ic95'][0]:.2f}, {R[f'R1|{nombre}']['ic95'][1]:.2f}] p={R[f'R1|{nombre}']['p']:.3f}")
    base = panel.copy(); base["log_area"] = np.log(base["area_km2"])
    base_cols = cov + ["log_area"]

    print("\n== R2 interacciones (conjunta; Holm sobre 4) ==")
    inter, ps = {}, []
    for v in ("pct_mat_vulnerable", "nbi2018", "pct_cabecera", "lluvia_p95"):
        b = base.dropna(subset=base_cols).copy()
        b["expo_c"] = b["expo_vial"] - b["expo_vial"].mean()
        b[v + "_c"] = (b[v] - b[v].mean()) / b[v].std()
        b["inter"] = b["expo_c"] * b[v + "_c"]
        res, n = glm(b, "viv_danadas", ["expo_c", v + "_c", "inter", "frac_hand", "log_area"] + [c for c in base_cols if c not in ("expo_vial", v, "frac_hand", "log_area")])
        rv = rr(res, "inter", 0.10)
        inter[v] = {"n": n, **rv}; ps.append(rv["p"])
    for (v, r), q in zip(inter.items(), holm(np.array(ps))):
        r["p_holm"] = float(q); R[f"R2|{v}"] = r
        print(f"  expo x {v:<20} RR de la interaccion por +0,10 x 1 DE = {r['rr']:.2f} IC95 [{r['ic95'][0]:.2f}, {r['ic95'][1]:.2f}] p={r['p']:.3f} p Holm={q:.3f}")

    print("\n== R3 tipo de via (conjunta; km minimo por tipo) ==")
    for t in ("trunk", "primary", "secondary"):
        b = base.dropna(subset=[f"expo_{t}"]).copy()
        b["e"] = b[f"expo_{t}"]
        res, n = glm(b, "viv_danadas", ["e", "frac_hand", "pct_cabecera", "pct_mat_vulnerable", "nbi2018", "lluvia_p95", "log_area"])
        R[f"R3|{t}"] = {"n": n, **rr(res, "e", 0.10)}
        print(f"  {t:<10} n={n}  RR por +0,10 = {R[f'R3|{t}']['rr']:.2f} IC95 [{R[f'R3|{t}']['ic95'][0]:.2f}, {R[f'R3|{t}']['ic95'][1]:.2f}] p={R[f'R3|{t}']['p']:.3f}")

    print("\n== R4 mecanismo ==")
    tablas = []
    for _, r in panel.iterrows():
        if r["_cerca"] > 0 and r["_lejos"] > 0:
            tablas.append(np.array([[r["_bajo_cerca"], r["_cerca"] - r["_bajo_cerca"]], [r["_bajo_lejos"], r["_lejos"] - r["_bajo_lejos"]]]))
    if tablas:
        st = StratifiedTable(tablas)
        lo, hi = st.oddsratio_pooled_confint()
        R["R4|P1"] = {"or_mh": float(st.oddsratio_pooled), "ic95": [float(lo), float(hi)], "n_municipios": len(tablas)}
        print(f"  P1 razon de momios de MH (lugar en terreno bajo | cerca de via vs lejos): {st.oddsratio_pooled:.2f} IC95 [{lo:.2f}, {hi:.2f}] en {len(tablas)} municipios")
    b = base.dropna(subset=base_cols + ["lug_bajo_cerca", "cab_bajo_en_via"]).copy()
    r0, n0 = glm(b, "viv_danadas", base_cols)
    r1, n1 = glm(b, "viv_danadas", base_cols + ["lug_bajo_cerca", "cab_bajo_en_via"])
    c0, c1_ = r0.params["expo_vial"], r1.params["expo_vial"]
    R["R4|P2"] = {"n": n0, "coef_sin": float(c0), "coef_con": float(c1_), "reduccion_pct": float(100 * (1 - c1_ / c0)) if c0 else None, "rr_sin": rr(r0, "expo_vial", 0.10), "rr_con": rr(r1, "expo_vial", 0.10)}
    print(f"  P2 (n={n0}) RR por +0,10: sin mecanismo {R['R4|P2']['rr_sin']['rr']:.2f}; con lugares en terreno bajo cerca de via y cabecera en via: {R['R4|P2']['rr_con']['rr']:.2f}; reduccion del coeficiente {R['R4|P2']['reduccion_pct']:.0f} %")

    print("\n== R5 controles negativos (mismo modelo R1, conjunta) ==")
    for y in ("n_mm", "n_incendio", "n_inund"):
        res, n = glm(base, y, base_cols)
        R[f"R5|{y}"] = {"n": n, **rr(res, "expo_vial", 0.10)}
        print(f"  {y:<11} n={n} RR por +0,10 = {R[f'R5|{y}']['rr']:.2f} IC95 [{R[f'R5|{y}']['ic95'][0]:.2f}, {R[f'R5|{y}']['ic95'][1]:.2f}] p={R[f'R5|{y}']['p']:.3f}")

    print("\n== R6 focalizacion (dejando un departamento fuera; captura del 20 % mejor clasificado) ==")
    f = base.dropna(subset=base_cols).copy()
    f["log_pob"] = np.log(f["poblacion"])
    conjuntos = {"A: solo poblacion": ["log_pob"], "B: + HAND municipal y area": ["log_pob", "frac_hand", "log_area"],
                 "C: + exposicion vial": ["log_pob", "frac_hand", "log_area", "expo_vial"]}
    cap = {k: [] for k in conjuntos}
    for dep in sorted(f["depto"].unique()):
        te, tr = f[f["depto"] == dep], f[f["depto"] != dep]
        if len(te) < 10 or te["viv_danadas"].sum() <= 0:
            continue
        top = max(1, int(round(0.2 * len(te))))
        for k, cols in conjuntos.items():
            X = sm.add_constant(tr[cols])
            m = sm.GLM(tr["viv_danadas"], X, family=sm.families.Poisson()).fit()
            pred = m.predict(sm.add_constant(te[cols], has_constant="add"))
            orden = np.argsort(-pred.values)[:top]
            cap[k].append((dep, float(te["viv_danadas"].values[orden].sum() / te["viv_danadas"].sum())))
    deps = sorted({d for v in cap.values() for d, _ in v})
    M = {k: {d: c for d, c in v} for k, v in cap.items()}
    for k in conjuntos:
        vals = [M[k][d] for d in deps]
        print(f"  {k:<30} captura media = {100 * np.mean(vals):.1f} % (n deptos = {len(deps)})")
    dif = np.array([M["C: + exposicion vial"][d] - M["B: + HAND municipal y area"][d] for d in deps])
    bs = [dif[RNG.integers(0, len(dif), len(dif))].mean() for _ in range(N_BOOT)]
    R["R6"] = {"captura_media": {k: float(np.mean([M[k][d] for d in deps])) for k in conjuntos}, "dif_C_menos_B": float(dif.mean()),
               "ic95": [float(x) for x in np.percentile(bs, [2.5, 97.5])], "n_deptos": len(deps), "por_depto": {k: M[k] for k in M}}
    print(f"  C - B = {100 * dif.mean():+.1f} puntos porcentuales, IC95 por departamentos [{100 * R['R6']['ic95'][0]:+.1f}, {100 * R['R6']['ic95'][1]:+.1f}]")
    (AQUI / "v1_resultados.json").write_text(json.dumps(R, indent=1, default=lambda o: None if o is None else str(o)), encoding="utf-8")


if __name__ == "__main__":
    main()
