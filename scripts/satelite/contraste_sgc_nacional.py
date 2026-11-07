"""Extension nacional del contraste con el SGC (protocolo seccion 17)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contraste_sgc_amenaza_mm as cb  # noqa: E402  (parcial, boot)
import piloto_deslizamientos_caribe as pl  # noqa: E402

REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
REG = {d: r for r, ds in REGIONES.items() for d in ds.split()}
NAC_CARIBE = {"N1": 0.52, "N2": 0.49, "N3": 0.31}


def estadisticos(pen, sg, den, bl, etiqueta):
    out = {}
    for k, f, v in [("N1", lambda i: spearmanr(pen[i], sg[i])[0], spearmanr(pen, sg)[0]),
                    ("N2", lambda i: spearmanr(den[i], sg[i])[0], spearmanr(den, sg)[0]),
                    ("N3", lambda i: cb.parcial(den[i], sg[i], pen[i]), cb.parcial(den, sg, pen))]:
        lo, hi = cb.boot(f, bl, len(pen))
        out[k] = (float(v), float(lo), float(hi))
    print(f"  {etiqueta:<10} n={len(pen):4d} | " + " | ".join(f"{k} {v[0]:+.2f} [{v[1]:+.2f},{v[2]:+.2f}]" for k, v in out.items()), flush=True)
    return out


def main() -> None:
    sgc = {r["CODIGO_DAN"]: r for r in json.loads((AQUI / "sgc_amenaza_mm_municipios.json").read_text(encoding="utf-8")) if r["CATEGORIA"] == "M"}
    dem = {m["codigo"]: m for m in json.loads((AQUI / "dem_poligonos_colombia.json").read_text(encoding="utf-8"))["municipios"] if "error" not in m}
    pols = {}
    for f in sorted((AQUI / "_cache").glob("poligonos_nac_*.geojson")):
        for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
            pols[ft["properties"]["CODIGO"]] = shape(ft["geometry"]).buffer(0)
    pts = [Point(x, y) for x, y, *_ in pl.simma_puntos()]
    tree = STRtree(pts)
    filas = []
    for c, d in dem.items():
        if c not in sgc or c not in pols or c[:2] not in REG:
            continue
        g = pols[c]
        n = len(tree.query(g, predicate="contains"))
        area = g.area * (111.32 ** 2) * np.cos(np.radians(g.centroid.y))
        s = sgc[c]
        filas.append((c[:2], REG[c[:2]], d["pend_p90_pct"], (s["SUM_ALTA"] or 0) + (s["SUM_MUY_AL"] or 0), 100 * n / area))
    dp = np.array([f[0] for f in filas]); rg = np.array([f[1] for f in filas])
    pen, sg, den = (np.array([f[i] for f in filas]) for i in (2, 3, 4))
    print(f"Municipios nacionales con DEM, SGC y poligono: {len(filas)}; con SIMMA>0: {int((den > 0).sum())}; SGC alta>0: {int((sg > 0).sum())}")
    res = {"nacional": estadisticos(pen, sg, den, dp, "NACIONAL")}
    n = res["nacional"]
    print(f"\nVEREDICTO: N1 {'cumple' if n['N1'][1] > 0 else 'NO'}, N2 {'cumple' if n['N2'][1] > 0 else 'NO'}, N3 {'cumple' if n['N3'][1] > 0 else 'NO'}")
    print("Caribe dentro del IC nacional: " + ", ".join(f"{k} {'si' if n[k][1] <= v <= n[k][2] else 'NO'}" for k, v in NAC_CARIBE.items()))
    print("\nPor region (N4):")
    for r in REGIONES:
        m = rg == r
        if m.sum() >= 30:
            res[r] = estadisticos(pen[m], sg[m], den[m], dp[m], r)
        else:
            print(f"  {r:<10} n={int(m.sum())} (< 30: solo se reporta rho N1 = {spearmanr(pen[m], sg[m])[0]:+.2f})")
    het = [r for r in res if r != "nacional" and any(res[r][k][1] > n[k][0] or res[r][k][2] < n[k][0] for k in ("N1", "N3"))]
    print(f"\nRegiones con IC que excluye el valor nacional (heterogeneidad): {het or 'ninguna'}")
    t = np.percentile(sg[sg > 0], [50]) if (sg > 0).any() else [0]
    for nm, m in [("SGC = 0", sg == 0), ("SGC bajo (>0..mediana)", (sg > 0) & (sg <= t[0])), ("SGC alto (> mediana)", sg > t[0])]:
        print(f"  {nm:<24} n={int(m.sum()):4d} pend p90 {pen[m].mean():5.1f}% SIMMA {den[m].mean():.2f}/100km2")
    (AQUI / "contraste_sgc_nacional.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
