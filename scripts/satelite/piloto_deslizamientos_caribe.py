"""Piloto de SUSCEPTIBILIDAD a movimientos en masa en el Caribe colombiano (issue #95/#98).
Verifica factibilidad, no es un modelo de produccion.

Que responde: dado el inventario del SGC (SIMMA, puntos) y el relieve del DEM, ¿se puede
discriminar DONDE ocurren movimientos en masa mejor que al azar, y esa capacidad sobrevive
cuando se valida en un departamento que el modelo no vio?

Diseno (declarado):
- Presencia = puntos SIMMA dentro de los poligonos municipales de los departamentos con DEM ~90 m
  calculado (hand: dem90_XX.tif). Fondo = puntos aleatorios en tierra de los mismos poligonos
  (5 por cada presencia). Es un problema de SOLO PRESENCIA: el AUC mide discriminacion frente al
  fondo, NO es una probabilidad de ocurrencia.
- Variables del DEM: pendiente, elevacion, rugosidad (DE de pendiente 5x5), curvatura (laplaciano).
- Modelos: pendiente sola (linea base) vs las 4 variables. Regresion logistica.
- Validacion: AUC con CV ALEATORIA (optimista) y con CV dejando un DEPARTAMENTO fuera
  (espacial). La diferencia es la inflacion por autocorrelacion espacial.
- SIMMA NO trae fecha de evento: sirve para "donde", NO para "cuando" (no hay umbrales de lluvia).
"""
from __future__ import annotations

import io
import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.prepared import prep
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

SIMMA = "https://services1.arcgis.com/Og2nrTKe5bptW02d/arcgis/rest/services/Inventario_de_movimientos_en_masa/FeatureServer/0/query"
RAZON_FONDO = 5
SEMILLA = 20261106
RNG = np.random.default_rng(SEMILLA)
M_GRADO = 111_320.0


def simma_puntos() -> list[tuple[float, float, str]]:
    f = AQUI / "_cache" / "simma_puntos.json"
    if f.exists():
        return [tuple(x) for x in json.loads(f.read_text(encoding="utf-8"))]
    pts, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1", "outFields": "TIPO", "returnGeometry": "true", "outSR": 4326,
                                    "resultOffset": off, "resultRecordCount": 2000, "orderByFields": "OBJECTID", "f": "json"})
        with urllib.request.urlopen(urllib.request.Request(f"{SIMMA}?{q}", headers={"User-Agent": "structai-research/0.1"}), timeout=90) as r:
            fs = json.load(r)["features"]
        pts += [(x["geometry"]["x"], x["geometry"]["y"], x["attributes"]["TIPO"]) for x in fs if x.get("geometry")]
        if len(fs) < 2000:
            break
        off += 2000
    f.write_text(json.dumps(pts), encoding="utf-8")
    return pts


def variables_dem(path: Path):
    with rasterio.open(path) as ds:
        z = ds.read(1).astype("float64")
        z[z == ds.nodata] = np.nan
        tr = ds.transform
    lat = tr.f + tr.e * z.shape[0] / 2
    py = abs(tr.e) * M_GRADO
    px = tr.a * M_GRADO * math.cos(math.radians(lat))
    gy, gx = np.gradient(z, py, px)
    pend = np.degrees(np.arctan(np.hypot(gx, gy)))
    lap = (np.roll(z, 1, 0) + np.roll(z, -1, 0) + np.roll(z, 1, 1) + np.roll(z, -1, 1) - 4 * z) / (px * py)
    # rugosidad: desviacion estandar de la pendiente en 5x5 (calculada por bloques deslizantes simples)
    p2, p = np.nan_to_num(pend) ** 2, np.nan_to_num(pend)
    k = 5
    s1 = sum(np.roll(np.roll(p, i, 0), j, 1) for i in range(-2, 3) for j in range(-2, 3)) / k ** 2
    s2 = sum(np.roll(np.roll(p2, i, 0), j, 1) for i in range(-2, 3) for j in range(-2, 3)) / k ** 2
    rug = np.sqrt(np.maximum(s2 - s1 ** 2, 0))
    return z, pend, rug, lap, tr


def main() -> None:
    pols = dc.poligonos()
    pts = simma_puntos()
    print(f"Puntos SIMMA totales: {len(pts)}")
    filas = []     # (depto, y, features[4])
    resumen = {}
    for d, nombre in dc.DEPTOS.items():
        tif = AQUI / "_cache" / f"dem90_{d}.tif"
        if not tif.exists():
            print(f"  {d} {nombre}: sin DEM90 (se omite)")
            continue
        poly = unary_union([p["geom"].buffer(0) for c, p in pols.items() if c.startswith(d)])   # buffer(0) repara geometrias invalidas
        pp = prep(poly)
        z, pend, rug, lap, tr = variables_dem(tif)
        H, W = z.shape

        def muestrear(x, y):
            c, r = ~tr * (x, y)
            r, c = int(r), int(c)
            if 1 <= r < H - 1 and 1 <= c < W - 1 and not np.isnan(z[r, c]) and not np.isnan(pend[r, c]):
                return [pend[r, c], z[r, c], rug[r, c], lap[r, c]]
            return None

        pres = [muestrear(x, y) for x, y, _ in pts if pp.contains(Point(x, y))]
        pres = [v for v in pres if v is not None]
        minx, miny, maxx, maxy = poly.bounds
        fondo = []
        while len(fondo) < RAZON_FONDO * max(len(pres), 1) and len(pres) > 0:
            x, y = RNG.uniform(minx, maxx), RNG.uniform(miny, maxy)
            if pp.contains(Point(x, y)):
                v = muestrear(x, y)
                if v is not None:
                    fondo.append(v)
        resumen[d] = (nombre, len(pres))
        print(f"  {d} {nombre}: {len(pres)} presencias, {len(fondo)} fondo")
        filas += [(d, 1, v) for v in pres] + [(d, 0, v) for v in fondo]

    dep = np.array([f[0] for f in filas])
    y = np.array([f[1] for f in filas])
    X = np.array([f[2] for f in filas])
    print(f"\nTotal: {int(y.sum())} presencias y {int((1 - y).sum())} fondo en {len(set(dep))} departamentos")
    modelo = lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    sets = {"pendiente sola (linea base)": [0], "pendiente+elevacion+rugosidad+curvatura": [0, 1, 2, 3]}

    print("\n== AUC con CV ALEATORIA (5 pliegues; optimista) ==")
    for nombre, cols in sets.items():
        aucs = []
        for tr_i, te_i in StratifiedKFold(5, shuffle=True, random_state=SEMILLA).split(X, y):
            m = modelo().fit(X[tr_i][:, cols], y[tr_i])
            aucs.append(roc_auc_score(y[te_i], m.predict_proba(X[te_i][:, cols])[:, 1]))
        print(f"  {nombre:<42} AUC {np.mean(aucs):.3f} (DE entre pliegues {np.std(aucs):.3f})")

    print("\n== AUC dejando un DEPARTAMENTO fuera (validacion espacial) ==")
    for nombre, cols in sets.items():
        res = []
        for d in sorted(set(dep)):
            te = dep == d
            if y[te].sum() < 8:
                continue
            m = modelo().fit(X[~te][:, cols], y[~te])
            p = m.predict_proba(X[te][:, cols])[:, 1]
            res.append((d, int(y[te].sum()), roc_auc_score(y[te], p), average_precision_score(y[te], p), brier_score_loss(y[te], p)))
        print(f"  {nombre}")
        for d, n, a, ap, b in res:
            print(f"    {d} {resumen[d][0]:<11} n_presencias={n:>3}  AUC {a:.3f}  AP {ap:.3f} (azar {1 / (1 + RAZON_FONDO):.2f})")
        print(f"    media AUC {np.mean([r[2] for r in res]):.3f} | minimo {min(r[2] for r in res):.3f} | maximo {max(r[2] for r in res):.3f}")
    print("\nLIMITES: presencia-solo (el AUC no es probabilidad); sesgo de acceso/reporte en el inventario; SIMMA sin fecha "
          "(no sirve para 'cuando'); DEM 90 m de superficie; geologia y cobertura no incluidas; pocos eventos por departamento en el Caribe.")


if __name__ == "__main__":
    main()
