"""Exposición de la red vial principal de Perú a terreno bajo (HAND), por distrito (issue #110, V1-Perú).

Réplica de `scripts/satelite/vias_hand_caribe.py`: vía principal = OSM highway trunk|primary|secondary; puntos cada
~90 m a lo largo de cada tramo; HAND con red de 5 km2 y corte < 10 m; los puentes (bridge distinto de no) se cuentan
aparte y no suman a la longitud. A diferencia del script del Caribe, este NO calcula ninguna estadística de asociación:
solo produce los insumos (km de vía, km bajo, puentes) para la compuerta de datos del protocolo.

Etapas:
  python -I vias_hand_peru.py extraer  <peru.osm.pbf> <vias.pkl>
  python -I vias_hand_peru.py exponer  <vias.pkl> <dir_mosaicos_dem> <per_admin3.shp> <salida.json> [adm1,...]
"""
from __future__ import annotations

import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from pysheds.grid import Grid
from rasterio.merge import merge
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calcular_hand_peru as hp  # noqa: E402  (define MARGEN, RES_GRADOS, NODATA, M_GRADO, lectura de distritos y mosaicos)

TIPOS_VIA = {"trunk", "primary", "secondary"}
PASO_M = 90.0
CORTE_HAND_M = 10.0
UMBRAL_RED_KM2 = 5.0
UMBRAL_RIO_KM2 = 25.0
PUENTE_NO = {"no", ""}


def extraer(pbf: str, salida: str) -> None:
    """Lee el .pbf y guarda los tramos de vía principal como (tipo, es_puente, [(lon, lat), ...])."""
    import osmium

    t0 = time.time()
    tramos, omitidos = [], 0
    proc = osmium.FileProcessor(pbf).with_locations().with_filter(osmium.filter.KeyFilter("highway"))
    for o in proc:
        if not o.is_way() or o.tags.get("highway") not in TIPOS_VIA:
            continue
        try:
            coords = [(n.lon, n.lat) for n in o.nodes]
        except osmium.InvalidLocationError:
            omitidos += 1
            continue
        if len(coords) >= 2:
            tramos.append((o.tags["highway"], o.tags.get("bridge", "no") not in PUENTE_NO, coords))
    with open(salida, "wb") as f:
        pickle.dump({"tramos": tramos, "omitidos_sin_ubicacion": omitidos}, f)
    por_tipo = {t: sum(1 for x in tramos if x[0] == t) for t in sorted(TIPOS_VIA)}
    print(f"{len(tramos)} tramos {por_tipo}; {omitidos} omitidos por nodo sin ubicación ({time.time() - t0:.0f}s)")


def puntos_linea(coords: list[tuple[float, float]]) -> tuple[list[tuple[float, float]], float]:
    """Puntos cada ~PASO_M a lo largo de la polilínea y la longitud (km) que representa cada uno."""
    ln = LineString(coords)
    k = math.cos(math.radians(float(np.mean([c[1] for c in coords]))))
    largo_m = LineString([(x * k, y) for x, y in coords]).length * hp.M_GRADO
    n = max(1, int(largo_m // PASO_M))
    pts = [ln.interpolate((i + 0.5) / n, normalized=True) for i in range(n)]
    return [(p.x, p.y) for p in pts], largo_m / n / 1000.0


def hand_y_acc(distritos: dict, directorio: str, tmp: Path, adm1: str):
    lims = [d["geom"].bounds for d in distritos.values()]
    bbox = [min(b[0] for b in lims) - hp.MARGEN, min(b[1] for b in lims) - hp.MARGEN,
            max(b[2] for b in lims) + hp.MARGEN, max(b[3] for b in lims) + hp.MARGEN]
    ds = [rasterio.open(r) for r in hp.mosaicos_que_cubren(directorio, bbox)]
    try:
        z, tr = merge(ds, bounds=tuple(bbox), res=(hp.RES_GRADOS, hp.RES_GRADOS), nodata=np.nan,
                      resampling=rasterio.enums.Resampling.average)
    finally:
        for d in ds:
            d.close()
    z = z[0].astype("float32")
    z[(z == 0) | np.isnan(z)] = hp.NODATA
    tif = tmp / f"dem90_{adm1}.tif"
    with rasterio.open(tif, "w", driver="GTiff", height=z.shape[0], width=z.shape[1], count=1, dtype="float32",
                       crs="EPSG:4326", transform=tr, nodata=hp.NODATA, compress="deflate") as dst:
        dst.write(z, 1)
    grid = Grid.from_raster(str(tif))
    dem = grid.read_raster(str(tif))
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)
    km2_celda = (hp.RES_GRADOS * hp.M_GRADO) ** 2 * math.cos(math.radians((bbox[1] + bbox[3]) / 2)) / 1e6
    hand = np.array(grid.compute_hand(fdir, inflated, acc > (UMBRAL_RED_KM2 / km2_celda)), dtype="float64")
    hand[np.array(dem) == hp.NODATA] = np.nan
    hand[hand < 0] = 0.0
    return grid, hand, np.array(acc, dtype="float64") * km2_celda, bbox


def celda(grid, x: float, y: float, forma: tuple[int, int]) -> tuple[int, int] | None:
    col, row = ~grid.affine * (x, y)
    r, c = int(math.floor(row)), int(math.floor(col))
    return (r, c) if 0 <= r < forma[0] and 0 <= c < forma[1] else None


def procesar(adm1: str, distritos: dict, tramos: list, directorio: str, tmp: Path) -> list[dict]:
    t0 = time.time()
    grid, hand, acc_km2, bbox = hand_y_acc(distritos, directorio, tmp, adm1)
    forma = hand.shape
    codigos = list(distritos)
    arbol = STRtree([distritos[c]["geom"] for c in codigos])

    def distrito_de(x: float, y: float) -> str | None:
        for i in arbol.query(Point(x, y), predicate="intersects"):
            return codigos[int(i)]
        return None

    propios = [t for t in tramos if any(bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3] for x, y in t[2][:: max(1, len(t[2]) // 3)])]
    acum = {c: {"km_via": 0.0, "km_bajo": 0.0, "puentes": 0, "puentes_rio": 0, "km_puente": 0.0,
                "km_troncal": 0.0, "km_primaria": 0.0, "km_secundaria": 0.0} for c in codigos}
    clave = {"trunk": "km_troncal", "primary": "km_primaria", "secondary": "km_secundaria"}
    for tipo, es_puente, coords in propios:
        pts, km_pt = puntos_linea(coords)
        if es_puente:
            mx, my = coords[len(coords) // 2]
            c, ij = distrito_de(mx, my), celda(grid, mx, my, forma)
            if c and ij:
                acum[c]["puentes"] += 1
                r, cc = ij
                if np.nanmax(acc_km2[max(0, r - 1):r + 2, max(0, cc - 1):cc + 2]) >= UMBRAL_RIO_KM2:
                    acum[c]["puentes_rio"] += 1
                acum[c]["km_puente"] += len(pts) * km_pt
            continue
        for x, y in pts:
            c, ij = distrito_de(x, y), celda(grid, x, y, forma)
            if not c or not ij or np.isnan(hand[ij]):
                continue
            acum[c]["km_via"] += km_pt
            acum[c][clave[tipo]] += km_pt
            if hand[ij] < CORTE_HAND_M:
                acum[c]["km_bajo"] += km_pt
    print(f"  {len(propios)} tramos en el bbox, listo ({time.time() - t0:.0f}s)", flush=True)
    return [{"adm3_pcode": c, "distrito": distritos[c]["nombre"], "adm1": adm1, **a} for c, a in acum.items()]


def exponer(vias: str, directorio: str, shp: str, salida: str, solo: list[str] | None) -> None:
    tramos = pickle.load(open(vias, "rb"))["tramos"]  # noqa: S301  (archivo generado por la etapa 'extraer', local)
    por_adm1 = hp.leer_distritos(shp)
    destino = Path(salida)
    hecho = json.loads(destino.read_text(encoding="utf-8"))["distritos"] if destino.exists() else []
    ya = {f["adm1"] for f in hecho}
    tmp = destino.parent / "_tmp_vias"
    tmp.mkdir(parents=True, exist_ok=True)
    for adm1 in sorted(solo or por_adm1):
        if adm1 in ya:
            print(f"{adm1}: ya calculado, se salta")
            continue
        print(f"Departamento {adm1} ({len(por_adm1[adm1])} distritos)", flush=True)
        try:
            hecho.extend(procesar(adm1, por_adm1[adm1], tramos, directorio, tmp))
        except Exception as e:  # el fallo de un departamento no debe perder los demás
            print(f"  FALLA {adm1}: {type(e).__name__}: {str(e)[:150]}", flush=True)
        destino.write_text(json.dumps({"distritos": hecho}, ensure_ascii=False, indent=1), encoding="utf-8")
    con_via = [d for d in hecho if d["km_via"] > 0]
    print(f"\n{len(hecho)} distritos procesados, {len(con_via)} con vía principal")


if __name__ == "__main__":
    a = sys.argv
    if len(a) == 4 and a[1] == "extraer":
        extraer(a[2], a[3])
    elif len(a) >= 6 and a[1] == "exponer":
        exponer(a[2], a[3], a[4], a[5], a[6].split(",") if len(a) > 6 else None)
    else:
        sys.exit(__doc__)
