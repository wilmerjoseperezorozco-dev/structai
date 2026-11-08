"""Cobertura y fraccion de amenaza alta+muy alta de SIMMA 1:25.000 por municipio (sin usar eventos)."""
import glob, json
from pathlib import Path
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely.validation import make_valid

AQUI = Path(__file__).resolve().parent
KM = 111.32
import sys
ESC = sys.argv[1] if len(sys.argv) > 1 else "25K"


def poli(rings):
    # ArcGIS: anillos exteriores horarios; construimos uno por anillo y los unimos (huecos ignorados: aproximacion)
    ps = [make_valid(Polygon(r)) for r in rings if len(r) >= 4]
    return unary_union(ps) if ps else None


def main():
    simma = json.loads((AQUI / "_cache" / f"simma_amenaza_{ESC}.json").read_text(encoding="utf-8"))
    geoms, cat = [], []
    for s in simma:
        g = poli(s["rings"])
        if g is not None and not g.is_empty:
            geoms.append(g); cat.append(s["catame"])
    arbol = STRtree(geoms)
    out = {}
    for f in glob.glob(str(AQUI / "_cache" / "poligonos_nac_*.geojson")):
        for ft in json.loads(Path(f).read_text(encoding="utf-8"))["features"]:
            m = make_valid(shape(ft["geometry"]))
            tot = m.area
            cub, alta = 0.0, 0.0
            for i in arbol.query(m, predicate="intersects"):
                a = m.intersection(geoms[i]).area
                cub += a
                if cat[i] in ("Alta", "Muy Alta"):
                    alta += a
            if cub > 0:
                out[ft["properties"]["CODIGO"]] = {"cobertura": min(cub / tot, 1.0), "frac_alta_muy_alta": alta / cub if cub else None}
    (AQUI / f"simma_{ESC.lower()}_cobertura_municipal.json").write_text(json.dumps(out), encoding="utf-8")
    c = np.array([v["cobertura"] for v in out.values()])
    print("municipios con algun poligono 25K:", len(out), "| cobertura>=50%:", int((c >= .5).sum()), "| >=80%:", int((c >= .8).sum()))

main()
