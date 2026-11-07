"""Contraste relieve/SIMMA vs Mapa Nacional de Amenaza por Movimientos en Masa del SGC (protocolo seccion 16)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr
from shapely.geometry import Point
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402
import piloto_deslizamientos_caribe as pl  # noqa: E402

RNG = np.random.default_rng(20261107)
N_BOOT = 2000


def parcial(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    def res(a, b):
        A = np.c_[np.ones(len(b)), b]
        return a - A @ np.linalg.lstsq(A, a, rcond=None)[0]
    return np.corrcoef(res(rx, rz), res(ry, rz))[0, 1]


def boot(fun, bloques, n):
    et = np.unique(bloques); out = []
    for _ in range(N_BOOT):
        ix = np.concatenate([np.where(bloques == b)[0] for b in RNG.choice(et, len(et), replace=True)])
        try:
            v = fun(ix)
        except Exception:
            continue
        if np.isfinite(v):
            out.append(v)
    return np.percentile(out, [2.5, 97.5])


def main() -> None:
    sgc = {r["CODIGO_DAN"]: r for r in json.loads((AQUI / "sgc_amenaza_mm_municipios.json").read_text(encoding="utf-8")) if r["CATEGORIA"] == "M"}
    dem = {m["codigo"]: m for m in json.loads((AQUI / "dem_poligonos_caribe.json").read_text(encoding="utf-8"))["municipios"]}
    pols = dc.poligonos()
    pts = [Point(x, y) for x, y, *_ in pl.simma_puntos()]
    tree = STRtree(pts)
    filas = []
    for c, d in dem.items():
        if c not in sgc or c not in pols:
            continue
        g = pols[c]["geom"].buffer(0)
        n = len(tree.query(g, predicate="contains"))
        area = g.area * (111.32 ** 2) * 0.985
        s = sgc[c]
        filas.append((c, c[:2], d["pend_p90_pct"], (s["SUM_ALTA"] or 0) + (s["SUM_MUY_AL"] or 0), 100 * n / area, n))
    a = np.array([(f[2], f[3], f[4]) for f in filas]); bl = np.array([f[1] for f in filas])
    pen, sg, den = a[:, 0], a[:, 1], a[:, 2]
    print(f"Municipios del Caribe con DEM, SGC y poligono: {len(filas)}; con SIMMA>0: {int((a[:, 2] > 0).sum())}; con SGC alta+muy alta>0: {int((sg > 0).sum())}")
    res = {}
    for nombre, fun, args in [
        ("C1 rho(pendiente p90, indice SGC)", lambda ix: spearmanr(pen[ix], sg[ix])[0], spearmanr(pen, sg)[0]),
        ("C2 rho(densidad SIMMA, indice SGC)", lambda ix: spearmanr(den[ix], sg[ix])[0], spearmanr(den, sg)[0]),
        ("C3 rho parcial(densidad SIMMA, SGC | pendiente)", lambda ix: parcial(den[ix], sg[ix], pen[ix]), parcial(den, sg, pen)),
        ("ref: rho(densidad SIMMA, pendiente p90)", lambda ix: spearmanr(den[ix], pen[ix])[0], spearmanr(den, pen)[0])]:
        lo, hi = boot(fun, bl, len(filas))
        print(f"  {nombre} = {args:+.2f}  IC95% bloques [{lo:+.2f}, {hi:+.2f}]")
        res[nombre] = (args, lo, hi)
    c1, c2, c3 = (res[k] for k in list(res)[:3])
    ok = lambda r: r[1] > 0
    print(f"\nVEREDICTO: C1 {'cumple' if ok(c1) else 'NO'}, C2 {'cumple' if ok(c2) else 'NO'}, C3 {'cumple' if ok(c3) else 'NO'}")
    t = np.percentile(sg, [33.3, 66.7])
    print("Tercil del indice SGC -> pendiente p90 media / densidad SIMMA media:")
    for nm, m in [("bajo", sg <= t[0]), ("medio", (sg > t[0]) & (sg <= t[1])), ("alto", sg > t[1])]:
        print(f"  {nm}: n={int(m.sum())} pend {pen[m].mean():.1f}% dens {den[m].mean():.2f}/100km2")
    (AQUI / "contraste_sgc_amenaza_mm.json").write_text(json.dumps({k: list(v) for k, v in res.items()}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
