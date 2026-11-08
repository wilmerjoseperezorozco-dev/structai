"""HAND por distrito de Perú desde Copernicus DEM GLO-90 (issue #110, protocolo V1-Perú).

Misma definición que Colombia (`scripts/satelite/calcular_hand_caribe.py`, PROTOCOLO_ANALISIS.md §9):
océano (elev == 0) como sin dato -> fill_pits -> fill_depressions -> resolve_flats -> D8 -> acumulación ->
red por área aguas arriba (1, 5, 25 km2) -> compute_hand. Estadística zonal por polígono distrital (COD-AB).
Solo calcula el predictor; no lo asocia con nada.

Uso: python -I calcular_hand_peru.py <dir_mosaicos_dem> <per_admin3.shp> <salida.json> [pcodes_adm1 separados por coma]
Los mosaicos se leen del disco (no hay descarga). Reanudable: un adm1 ya presente en la salida se salta.
"""
from __future__ import annotations

import glob
import io
import json
import math
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import rasterio
import shapefile
from pysheds.grid import Grid
from rasterio import features
from rasterio.merge import merge
from shapely.geometry import shape

if not hasattr(np, "in1d"):  # pysheds 0.5 usa np.in1d, eliminada en NumPy recientes
    np.in1d = np.isin

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

RES_GRADOS = 3 / 3600.0
MARGEN = 0.15
UMBRALES_KM2 = (1.0, 5.0, 25.0)
CORTES_M = (5.0, 10.0, 15.0)
NODATA = -9999.0
M_GRADO = 111_320.0
MIN_CELDAS = 30
PATRON = re.compile(r"_(S|N)(\d\d)_00_(W|E)(\d{3})_00_DEM\.tif$")


def leer_distritos(shp: str) -> dict[str, dict[str, object]]:
    """Distritos agrupados por departamento (adm1 = 4 primeros caracteres del adm3_pcode)."""
    lector = shapefile.Reader(shp, encoding="utf-8")
    campos = [c[0] for c in lector.fields[1:]]
    por_adm1: dict[str, dict[str, object]] = defaultdict(dict)
    for sr in lector.iterShapeRecords():
        reg = dict(zip(campos, sr.record))
        pcode = reg["adm3_pcode"]
        por_adm1[pcode[:4]][pcode] = {"geom": shape(sr.shape.__geo_interface__), "nombre": reg["adm3_name"]}
    return por_adm1


def mosaicos_que_cubren(directorio: str, bbox: list[float]) -> list[str]:
    """Rutas de los mosaicos 1x1 grados que intersectan el bbox, según el nombre del archivo."""
    out = []
    for ruta in glob.glob(str(Path(directorio) / "*.tif")):
        m = PATRON.search(ruta)
        if not m:
            continue
        lat = -int(m.group(2)) if m.group(1) == "S" else int(m.group(2))
        lon = -int(m.group(4)) if m.group(3) == "W" else int(m.group(4))
        if lon < bbox[2] and lon + 1 > bbox[0] and lat < bbox[3] and lat + 1 > bbox[1]:
            out.append(ruta)
    return sorted(out)


def procesar(adm1: str, distritos: dict[str, dict[str, object]], directorio: str, tmp: Path) -> list[dict]:
    t0 = time.time()
    lims = [d["geom"].bounds for d in distritos.values()]
    bbox = [min(b[0] for b in lims) - MARGEN, min(b[1] for b in lims) - MARGEN,
            max(b[2] for b in lims) + MARGEN, max(b[3] for b in lims) + MARGEN]
    rutas = mosaicos_que_cubren(directorio, bbox)
    if not rutas:
        raise RuntimeError("sin mosaicos para el bbox")
    ds = [rasterio.open(r) for r in rutas]
    try:
        z, tr = merge(ds, bounds=tuple(bbox), res=(RES_GRADOS, RES_GRADOS), nodata=np.nan,
                      resampling=rasterio.enums.Resampling.average)
    finally:
        for d in ds:
            d.close()
    z = z[0].astype("float32")
    z[(z == 0) | np.isnan(z)] = NODATA
    tif = tmp / f"dem90_{adm1}.tif"
    with rasterio.open(tif, "w", driver="GTiff", height=z.shape[0], width=z.shape[1], count=1, dtype="float32",
                       crs="EPSG:4326", transform=tr, nodata=NODATA, compress="deflate") as dst:
        dst.write(z, 1)
    grid = Grid.from_raster(str(tif))
    dem = grid.read_raster(str(tif))
    print(f"  {len(rutas)} mosaicos, DEM {dem.shape[1]}x{dem.shape[0]} px ({time.time() - t0:.0f}s)", flush=True)
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)
    lat = (bbox[1] + bbox[3]) / 2
    km2_celda = (RES_GRADOS * M_GRADO) ** 2 * math.cos(math.radians(lat)) / 1e6
    habiles = np.array(dem) != NODATA
    hands = {}
    for u in UMBRALES_KM2:
        h = np.array(grid.compute_hand(fdir, inflated, acc > (u / km2_celda)), dtype="float64")
        h[~habiles] = np.nan
        h[h < 0] = 0.0
        hands[u] = h
    print(f"  HAND listo ({time.time() - t0:.0f}s)", flush=True)
    filas = []
    for pcode, p in distritos.items():
        m = features.geometry_mask([p["geom"].__geo_interface__], out_shape=dem.shape, transform=grid.affine, invert=True)
        fila = {"adm3_pcode": pcode, "distrito": p["nombre"], "adm1": adm1}
        for u, h in hands.items():
            v = h[m & ~np.isnan(h)]
            fila[f"n_validos_{u:g}"] = int(len(v))
            if len(v) >= MIN_CELDAS:
                fila[f"hand_mediana_{u:g}"] = float(np.median(v))
                fila[f"hand_p25_{u:g}"] = float(np.percentile(v, 25))
                for cm in CORTES_M:
                    fila[f"frac_hand_lt{cm:g}_{u:g}"] = float((v < cm).mean())
        fila["frac_sin_dato"] = float(1 - (m & habiles).sum() / max(1, m.sum()))
        filas.append(fila)
    return filas


def main(directorio: str, shp: str, salida: str, solo: list[str] | None) -> None:
    por_adm1 = leer_distritos(shp)
    destino = Path(salida)
    hecho = json.loads(destino.read_text(encoding="utf-8"))["distritos"] if destino.exists() else []
    ya = {f["adm1"] for f in hecho}
    tmp = destino.parent / "_tmp_hand"
    tmp.mkdir(parents=True, exist_ok=True)
    for adm1 in sorted(solo or por_adm1):
        if adm1 in ya:
            print(f"{adm1}: ya calculado, se salta")
            continue
        print(f"Departamento {adm1} ({len(por_adm1[adm1])} distritos)", flush=True)
        try:
            hecho.extend(procesar(adm1, por_adm1[adm1], directorio, tmp))
        except Exception as e:  # el fallo de un departamento no debe perder los demás
            print(f"  FALLA {adm1}: {type(e).__name__}: {str(e)[:150]}", flush=True)
        destino.write_text(json.dumps({"definicion": "PROTOCOLO_ANALISIS.md sección 9; réplica Perú", "distritos": hecho},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [d for d in hecho if "hand_mediana_5" in d]
    print(f"\n{len(ok)}/{len(hecho)} distritos con HAND válido")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",") if len(sys.argv) > 4 else None)
