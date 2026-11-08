"""Mapa de amenaza por movimientos en masa del SGC vs eventos UNGRD 2019-2024. Protocolo: PROTOCOLO_ANALISIS.md seccion 26.
Salida: contraste_sgc_vs_ungrd.json"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import sesgo_reporte_ungrd as sr  # noqa: E402

N_BOOT = 2000
RNG = np.random.default_rng(26)
MIN_REGION = 30
POB_GRANDE = 500_000
EVENTO = "MOVIMIENTO EN MASA"
REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
REG = {d: r for r, ds in REGIONES.items() for d in ds.split()}


def auc(x: np.ndarray, y: np.ndarray) -> float:
    r = rankdata(x)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def parcial(x, y, Z):
    rx, ry = rankdata(x), rankdata(y)
    A = np.c_[np.ones(len(x)), *[rankdata(z) for z in Z]]
    res = lambda a: a - A @ np.linalg.lstsq(A, a, rcond=None)[0]  # noqa: E731
    return np.corrcoef(res(rx), res(ry))[0, 1]


def boot(fun, bloques):
    et = np.unique(bloques)
    idx = {b: np.where(bloques == b)[0] for b in et}
    out = []
    for _ in range(N_BOOT):
        ix = np.concatenate([idx[b] for b in RNG.choice(et, len(et), replace=True)])
        try:
            v = fun(ix)
        except Exception:
            continue
        if np.isfinite(v):
            out.append(v)
    return [float(v) for v in np.percentile(out, [2.5, 97.5])]


def preparar(anios_excluidos: tuple[int, ...] = ()) -> pd.DataFrame:
    panel = pd.read_csv(AQUI / "v1_panel.csv", dtype={"codigo": str})
    panel["codigo"] = panel["codigo"].str.zfill(5)
    ung = sr.cargar_ungrd()
    ind = sr.indicadores(ung)
    mm = ung[(ung["evento"].fillna("").str.upper() == EVENTO) & (~ung["anio"].isin(anios_excluidos))]
    panel = panel.drop(columns=["n_mm"]).merge(mm.groupby("codigo_municipio").size().rename("n_mm"), left_on="codigo", right_index=True, how="left")
    panel = panel.merge(ind[["n_estructural"]], left_on="codigo", right_index=True, how="left").fillna({"n_mm": 0, "n_estructural": 0})
    sgc = {r["CODIGO_DAN"]: r for r in json.loads((AQUI / "sgc_amenaza_mm_municipios.json").read_text(encoding="utf-8")) if r["CATEGORIA"] == "M"}
    dem = {m["codigo"]: m for m in json.loads((AQUI / "dem_poligonos_colombia.json").read_text(encoding="utf-8"))["municipios"] if "error" not in m}
    panel = panel[panel["codigo"].isin(sgc) & panel["codigo"].isin(dem)].copy()
    panel["idx_sgc"] = [sgc[c]["SUM_ALTA"] + sgc[c]["SUM_MUY_AL"] for c in panel["codigo"]]
    panel["pend_p90"] = [dem[c]["pend_p90_pct"] for c in panel["codigo"]]
    panel["y1"] = (panel["n_mm"] >= 1).astype(int)
    panel["y2"] = panel["n_mm"] / panel["area_km2"] * 100
    panel["P_A"] = np.log1p(panel["n_estructural"] / panel["poblacion"] * 1e5)
    panel["log_pob"] = np.log(panel["poblacion"])
    panel["depto2"] = panel["codigo"].str[:2]
    panel["region"] = panel["depto2"].map(REG)
    return panel.reset_index(drop=True)


def confirmatorios(p: pd.DataFrame) -> dict:
    x, y1, y2 = p["idx_sgc"].values, p["y1"].values, p["y2"].values
    bl = p["depto2"].values
    z3 = [p["log_pob"].values, p["P_A"].values]
    z4 = [p["pend_p90"].values] + z3
    out = {"n": len(p), "n_con_evento": int(y1.sum())}
    for k, f in (("K1_auc", lambda i: auc(x[i], y1[i])), ("K2_rho", lambda i: spearmanr(x[i], y2[i])[0]),
                 ("K3_parcial_reporte", lambda i: parcial(x[i], y2[i], [z[i] for z in z3])),
                 ("K4_parcial_pendiente_reporte", lambda i: parcial(x[i], y2[i], [z[i] for z in z4]))):
        v = f(np.arange(len(p)))
        out[k] = [float(v)] + boot(f, bl)
    out["pendiente_sola_auc"] = float(auc(p["pend_p90"].values, y1))
    out["pendiente_sola_rho"] = float(spearmanr(p["pend_p90"], y2)[0])
    q = pd.qcut(p["idx_sgc"].rank(method="first"), 4, labels=False)
    out["cuartiles_idx_sgc"] = [{"q": int(k), "n": int((q == k).sum()), "idx_medio": float(p.loc[q == k, "idx_sgc"].mean()),
                                 "frac_con_evento": float(p.loc[q == k, "y1"].mean()), "eventos_x100km2_mediana": float(p.loc[q == k, "y2"].median())}
                                for k in range(4)]
    return out


def main() -> None:
    p = preparar()
    R = {"principal": confirmatorios(p)}
    print(json.dumps(R["principal"], indent=1, ensure_ascii=False), flush=True)
    por_region = {}
    for r, g in p.groupby("region"):
        if len(g) >= MIN_REGION and 0 < g["y1"].sum() < len(g):
            por_region[r] = {"n": len(g), "n_con_evento": int(g["y1"].sum()), "auc": float(auc(g["idx_sgc"].values, g["y1"].values)),
                             "rho": float(spearmanr(g["idx_sgc"], g["y2"])[0])}
        else:
            por_region[r] = {"n": len(g), "nota": "no se reporta (n < 30 o sin variacion en Y1)"}
    R["por_region"] = por_region
    R["sin_2022"] = confirmatorios(preparar((2022,)))
    R["sin_municipios_grandes"] = confirmatorios(p[p["poblacion"] <= POB_GRANDE].reset_index(drop=True))
    (AQUI / "contraste_sgc_vs_ungrd.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print("por region", json.dumps(por_region, ensure_ascii=False))
    for k in ("sin_2022", "sin_municipios_grandes"):
        print(k, {a: R[k][a] for a in ("n", "K1_auc", "K2_rho", "K3_parcial_reporte", "K4_parcial_pendiente_reporte")})


if __name__ == "__main__":
    main()
