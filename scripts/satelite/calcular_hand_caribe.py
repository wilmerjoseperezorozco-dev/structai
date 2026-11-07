"""Altura sobre el drenaje mas cercano (HAND) desde Copernicus DEM, por departamento (issue #95).

Definicion fijada en PROTOCOLO_ANALISIS.md seccion 9 ANTES de calcular asociaciones.
Solo calcula el predictor; no lo asocia con nada.

Pipeline (pysheds): DEM ~90 m por departamento con margen, oceano (elev == 0) como sin dato,
fill_pits -> fill_depressions -> resolve_flats -> flowdir D8 -> accumulation -> red por area
aguas arriba -> compute_hand. Estadistica zonal por poligono municipal IGAC.

Uso: python scripts/satelite/calcular_hand_caribe.py [codigos_depto separados por coma]
Salida: scripts/satelite/hand_caribe.json
"""
from __future__ import annotations

import io
import json
import math
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.merge import merge
from pysheds.grid import Grid

# pysheds 0.5 llama np.in1d, eliminada en NumPy recientes; np.isin es el reemplazo equivalente.
if not hasattr(np, "in1d"):
    np.in1d = np.isin

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

CACHE = AQUI / "_cache"
STAC = "https://earth-search.aws.element84.com/v1/search"
RES_GRADOS = 3 / 3600.0
MARGEN = 0.15
UMBRALES_KM2 = (1.0, 5.0, 25.0)
CORTES_M = (5.0, 10.0, 15.0)
NODATA = -9999.0
M_GRADO = 111_320.0


def hrefs(bbox):
    req = urllib.request.Request(STAC, data=json.dumps({"collections": ["cop-dem-glo-30"], "bbox": bbox, "limit": 60}).encode(),
                                 headers={"User-Agent": "structai-piloto/0.1", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        hs = [f["assets"]["data"]["href"] for f in json.load(r)["features"]]
    return [("https://" + h[5:].split("/", 1)[0] + ".s3.amazonaws.com/" + h[5:].split("/", 1)[1]) if h.startswith("s3://") else h for h in hs]


def dem_departamento(depto: str, bbox) -> Path:
    out = CACHE / f"dem90_{depto}.tif"
    if out.exists():
        return out
    with rasterio.Env(GDAL_HTTP_TIMEOUT=60, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=2):
        ds = [rasterio.open(h) for h in hrefs(bbox)]
        try:
            z, tr = merge(ds, bounds=tuple(bbox), res=(RES_GRADOS, RES_GRADOS), nodata=np.nan,
                          resampling=rasterio.enums.Resampling.average)
        finally:
            for d in ds:
                d.close()
    z = z[0].astype("float32")
    z[(z == 0) | np.isnan(z)] = NODATA          # oceano y huecos
    with rasterio.open(out, "w", driver="GTiff", height=z.shape[0], width=z.shape[1], count=1, dtype="float32",
                       crs="EPSG:4326", transform=tr, nodata=NODATA, compress="deflate") as dst:
        dst.write(z, 1)
    return out


def procesar(depto: str, pols: dict) -> list[dict]:
    mun = {c: p for c, p in pols.items() if c.startswith(depto)}
    xs = [b for p in mun.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in mun.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - MARGEN, min(ys) - MARGEN, max(xs) + MARGEN, max(ys) + MARGEN]
    t0 = time.time()
    f = dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = grid.read_raster(str(f))
    print(f"  DEM {dem.shape[1]}x{dem.shape[0]} px ({(time.time() - t0):.0f}s)", flush=True)
    pit = grid.fill_pits(dem)
    flooded = grid.fill_depressions(pit)
    inflated = grid.resolve_flats(flooded)
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)
    lat = (bbox[1] + bbox[3]) / 2
    km2_celda = (RES_GRADOS * M_GRADO) ** 2 * math.cos(math.radians(lat)) / 1e6
    print(f"  flujo y acumulacion listos ({(time.time() - t0):.0f}s); celda ~{km2_celda * 1e6:.0f} m2", flush=True)
    habiles = np.array(dem) != NODATA
    hands = {}
    for u in UMBRALES_KM2:
        red = acc > (u / km2_celda)
        h = np.array(grid.compute_hand(fdir, inflated, red), dtype="float64")
        h[~habiles] = np.nan
        h[h < 0] = 0.0
        hands[u] = h
        print(f"  HAND red {u:g} km2: {int((red & habiles).sum())} celdas de red ({(time.time() - t0):.0f}s)", flush=True)
    filas = []
    for c, p in mun.items():
        m = features.geometry_mask([p["geom"].__geo_interface__], out_shape=dem.shape, transform=grid.affine, invert=True)
        fila = {"codigo": c, "municipio": p["nombre"], "depto": depto}
        for u, h in hands.items():
            v = h[m & ~np.isnan(h)]
            fila[f"n_validos_{u:g}"] = int(len(v))
            if len(v) >= 30:
                fila[f"hand_mediana_{u:g}"] = float(np.median(v))
                fila[f"hand_p25_{u:g}"] = float(np.percentile(v, 25))
                for cm in CORTES_M:
                    fila[f"frac_hand_lt{cm:g}_{u:g}"] = float((v < cm).mean())
        fila["frac_sin_dato"] = float(1 - (m & habiles).sum() / max(1, m.sum()))
        filas.append(fila)
    return filas


def main() -> None:
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else list(dc.DEPTOS)
    pols = dc.poligonos()
    destino = AQUI / "hand_caribe.json"
    # Fusiona con lo ya calculado: reintentar un departamento no debe borrar los demas.
    previo = json.loads(destino.read_text(encoding="utf-8"))["municipios"] if destino.exists() else []
    out = [m for m in previo if m["depto"] not in deptos]
    for d in deptos:
        print(f"Departamento {d} {dc.DEPTOS[d]}", flush=True)
        try:
            out.extend(procesar(d, pols))
        except Exception as e:
            print(f"  FALLA {d}: {type(e).__name__}: {str(e)[:120]}", flush=True)
        (AQUI / "hand_caribe.json").write_text(json.dumps({"definicion": "PROTOCOLO_ANALISIS.md seccion 9", "municipios": out},
                                                          ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [o for o in out if "hand_mediana_5" in o]
    print(f"\n{len(ok)}/{len(out)} municipios con HAND valido")
    for o in sorted(ok, key=lambda x: x["hand_mediana_5"])[:5]:
        print(f"  menor HAND mediano: {o['municipio']:<22}{o['hand_mediana_5']:6.1f} m  <10 m: {o['frac_hand_lt10_5'] * 100:5.1f} %")


if __name__ == "__main__":
    main()
