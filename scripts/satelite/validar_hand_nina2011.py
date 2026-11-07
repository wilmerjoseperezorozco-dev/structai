"""Validacion del HAND con las huellas de inundacion de La Nina 2011 del IGAC (protocolo seccion 18)."""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402
import contraste_sgc_amenaza_mm as cb  # noqa: E402


def main() -> None:
    huellas = []
    for f in sorted(glob.glob(str(AQUI / "_cache" / "igac" / "nina2011_*.geojson"))):
        huellas += [shape(ft["geometry"]).buffer(0) for ft in json.loads(Path(f).read_text(encoding="utf-8"))["features"]]
    tree = STRtree(huellas)
    pols = dc.poligonos()
    hand = {m["codigo"]: m for m in json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"] if "frac_hand_lt10_5" in m}
    dem = {m["codigo"]: m for m in json.loads((AQUI / "dem_poligonos_caribe.json").read_text(encoding="utf-8"))["municipios"] if "error" not in m}
    filas = []
    for c, h in hand.items():
        if c not in pols or c not in dem:
            continue
        g = pols[c]["geom"].buffer(0)
        ix = tree.query(g, predicate="intersects")
        frac = unary_union([huellas[i].intersection(g) for i in ix]).area / g.area if len(ix) else 0.0
        filas.append((c, c[:2], frac, h["frac_hand_lt10_5"], dem[c]["frac_bajo_10m"]))
    bl = np.array([f[1] for f in filas]); y, hd, cota = (np.array([f[i] for f in filas]) for i in (2, 3, 4))
    print(f"Municipios: {len(filas)}; con alguna huella: {int((y > 0).sum())}; fraccion inundada mediana {np.median(y):.3f}, max {y.max():.2f}")
    res = {}
    for k, f, v in [("F1 rho(inundada, HAND<10)", lambda i: spearmanr(y[i], hd[i])[0], spearmanr(y, hd)[0]),
                    ("F2 rho parcial(inundada, HAND<10 | cota<10)", lambda i: cb.parcial(y[i], hd[i], cota[i]), cb.parcial(y, hd, cota)),
                    ("ref rho(inundada, cota<10)", lambda i: spearmanr(y[i], cota[i])[0], spearmanr(y, cota)[0])]:
        lo, hi = cb.boot(f, bl, len(y))
        print(f"  {k} = {v:+.2f}  IC95% bloques [{lo:+.2f}, {hi:+.2f}]")
        res[k] = (float(v), float(lo), float(hi))
    ks = list(res)
    print(f"\nVEREDICTO: F1 {'cumple' if res[ks[0]][1] > 0 else 'NO'}, F2 {'cumple' if res[ks[1]][1] > 0 else 'NO'}")
    t = np.percentile(hd, [33.3, 66.7])
    for nm, m in [("menos llanura", hd <= t[0]), ("intermedio", (hd > t[0]) & (hd <= t[1])), ("mas llanura", hd > t[1])]:
        print(f"  HAND {nm:<14} n={int(m.sum()):3d} fraccion inundada media {y[m].mean():.3f}")
    top = np.argsort(-np.abs(np.argsort(np.argsort(y)) - np.argsort(np.argsort(hd))))[:6]
    print("Mayor desacuerdo de rangos:", [(pols[filas[i][0]]["nombre"], round(float(y[i]), 2), round(float(hd[i]), 2)) for i in top])
    (AQUI / "validar_hand_nina2011.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
