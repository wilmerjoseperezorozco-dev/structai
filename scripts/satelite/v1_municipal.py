"""V1: HAND municipal, exposicion vial por tipo de via, puentes, lugares poblados y cabecera, por departamento.
Protocolo: PROTOCOLO_V1_CONFIRMACION.md. Reutiliza la tuberia de calcular_hand_caribe.py y vias_hand_caribe.py.

Uso: python scripts/satelite/v1_municipal.py 63,66,17 ...
Salida: scripts/satelite/v1_municipal.json (se fusiona departamento a departamento; reintentar uno no borra los demas).
"""
from __future__ import annotations

import gc
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from affine import Affine
from rasterio import features
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "construdata"))
import calcular_hand_caribe as ch  # noqa: E402
import _datos_caribe as dc  # noqa: E402
import divipola  # noqa: E402
from pysheds.grid import Grid  # noqa: E402

CACHE = AQUI / "_cache"
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "structai-research/1.0 (academic research; github wilmerjoseperezorozco-dev)"
PASO_M = 90.0
CORTE_M = 10.0
CERCA_M = 1000.0
UMBRAL_RED_KM2 = 5.0
UMBRAL_RIO_KM2 = 25.0
TIPOS = ("trunk", "primary", "secondary")
LUGARES = "city|town|village|hamlet"
DESTINO = AQUI / "v1_municipal.json"


def overpass(consulta: str, ruta: Path) -> dict:
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    for intento in range(5):
        try:
            req = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": consulta}).encode(), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=500) as r:
                datos = json.load(r)
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            return datos
        except Exception as ex:
            print(f"  Overpass intento {intento + 1} fallo: {type(ex).__name__}", flush=True)
            time.sleep(40 * (intento + 1))
    raise RuntimeError("Overpass no respondio")


def osm_vias(depto, bbox):
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    return overpass(f'[out:json][timeout:400];way["highway"~"^(trunk|primary|secondary)$"]({s},{w},{n},{e});out geom tags;',
                    CACHE / f"osm_vias_{depto}.json")


def osm_lugares(depto, bbox):
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    return overpass(f'[out:json][timeout:400];node["place"~"^({LUGARES})$"]({s},{w},{n},{e});out;', CACHE / f"osm_lugares_{depto}.json")


def calcular_terreno(depto, pols):
    mun = {c: p for c, p in pols.items() if c.startswith(depto)}
    xs = [b for p in mun.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in mun.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - ch.MARGEN, min(ys) - ch.MARGEN, max(xs) + ch.MARGEN, max(ys) + ch.MARGEN]
    f = ch.dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = grid.read_raster(str(f))
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)
    lat = (bbox[1] + bbox[3]) / 2
    km2_celda = (ch.RES_GRADOS * ch.M_GRADO) ** 2 * math.cos(math.radians(lat)) / 1e6
    hand = np.array(grid.compute_hand(fdir, inflated, acc > (UMBRAL_RED_KM2 / km2_celda)), dtype="float32")
    habiles = np.array(dem) != ch.NODATA
    hand[~habiles] = np.nan
    hand[hand < 0] = 0.0
    acc_km2 = np.array(acc, dtype="float32") * km2_celda
    del fdir, inflated, acc, dem
    gc.collect()
    return mun, grid, hand, acc_km2, bbox


def celda(grid, x, y, forma):
    col, row = ~grid.affine * (x, y)
    r, c = int(math.floor(row)), int(math.floor(col))
    return (r, c) if 0 <= r < forma[0] and 0 <= c < forma[1] else None


def puntos_linea(coords):
    if len(coords) < 2:
        return [], 0.0
    ln = LineString(coords)
    k = math.cos(math.radians(np.mean([c[1] for c in coords])))
    largo_m = LineString([(x * k, y) for x, y in coords]).length * ch.M_GRADO
    n = max(1, int(largo_m // PASO_M))
    return [(p.x, p.y) for p in (ln.interpolate((i + 0.5) / n, normalized=True) for i in range(n))], largo_m / n / 1000.0


def estadistica_zonal(grid, hand, geom):
    minx, miny, maxx, maxy = geom.bounds
    c0, r1 = ~grid.affine * (minx, miny)
    c1, r0 = ~grid.affine * (maxx, maxy)
    r0, r1 = max(0, int(math.floor(min(r0, r1)))), min(hand.shape[0], int(math.ceil(max(r0, r1))) + 1)
    c0, c1 = max(0, int(math.floor(min(c0, c1)))), min(hand.shape[1], int(math.ceil(max(c0, c1))) + 1)
    sub = hand[r0:r1, c0:c1]
    if sub.size == 0:
        return 0, None
    m = features.geometry_mask([geom.__geo_interface__], out_shape=sub.shape, transform=grid.affine * Affine.translation(c0, r0), invert=True)
    v = sub[m & ~np.isnan(sub)]
    return int(len(v)), (float((v < CORTE_M).mean()) if len(v) >= 30 else None)


def procesar(depto, pols):
    t0 = time.time()
    mun, grid, hand, acc, bbox = calcular_terreno(depto, pols)
    forma = hand.shape
    print(f"  HAND listo ({time.time() - t0:.0f}s)", flush=True)
    vias = [e for e in osm_vias(depto, bbox).get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    lugares = [e for e in osm_lugares(depto, bbox).get("elements", []) if e.get("type") == "node"]
    print(f"  OSM: {len(vias)} tramos y {len(lugares)} lugares ({time.time() - t0:.0f}s)", flush=True)
    codigos = list(mun)
    arbol_mun = STRtree([mun[c]["geom"] for c in codigos])

    def municipio_de(x, y):
        for i in arbol_mun.query(Point(x, y), predicate="intersects"):
            return codigos[int(i)]
        return None

    k = math.cos(math.radians((bbox[1] + bbox[3]) / 2))
    lineas = [LineString([(g["lon"] * k, g["lat"]) for g in v["geometry"]]) for v in vias if len(v["geometry"]) >= 2]
    arbol_vias = STRtree(lineas) if lineas else None

    def dist_via_m(x, y):
        if arbol_vias is None:
            return None
        i = arbol_vias.nearest(Point(x * k, y))
        return float(lineas[int(i)].distance(Point(x * k, y)) * ch.M_GRADO)

    ac = {c: {"km_via": 0.0, "km_bajo": 0.0, "puentes": 0, "puentes_rio": 0,
              **{f"km_{t}": 0.0 for t in TIPOS}, **{f"km_{t}_bajo": 0.0 for t in TIPOS},
              "n_lugares": 0, "n_lugares_cerca": 0, "n_lugares_bajo": 0, "n_lugares_bajo_cerca": 0} for c in codigos}
    for v in vias:
        tags = v.get("tags", {})
        tipo = tags.get("highway")
        es_puente = tags.get("bridge", "no") not in {"no", ""}
        coords = [(g["lon"], g["lat"]) for g in v["geometry"]]
        pts, km_pt = puntos_linea(coords)
        if es_puente:
            mid = coords[len(coords) // 2]
            c, ij = municipio_de(*mid), celda(grid, mid[0], mid[1], forma)
            if c and ij:
                ac[c]["puentes"] += 1
                r, cc = ij
                if np.nanmax(acc[max(0, r - 1):r + 2, max(0, cc - 1):cc + 2]) >= UMBRAL_RIO_KM2:
                    ac[c]["puentes_rio"] += 1
            continue
        for x, y in pts:
            c, ij = municipio_de(x, y), celda(grid, x, y, forma)
            if not c or not ij or np.isnan(hand[ij]):
                continue
            bajo = hand[ij] < CORTE_M
            ac[c]["km_via"] += km_pt
            ac[c]["km_bajo"] += km_pt if bajo else 0.0
            if tipo in TIPOS:
                ac[c][f"km_{tipo}"] += km_pt
                ac[c][f"km_{tipo}_bajo"] += km_pt if bajo else 0.0
    for l in lugares:
        c, ij = municipio_de(l["lon"], l["lat"]), celda(grid, l["lon"], l["lat"], forma)
        if not c or not ij or np.isnan(hand[ij]):
            continue
        d = dist_via_m(l["lon"], l["lat"])
        cerca, bajo = (d is not None and d <= CERCA_M), bool(hand[ij] < CORTE_M)
        ac[c]["n_lugares"] += 1
        ac[c]["n_lugares_cerca"] += int(cerca)
        ac[c]["n_lugares_bajo"] += int(bajo)
        ac[c]["n_lugares_bajo_cerca"] += int(cerca and bajo)
    filas = []
    for c in codigos:
        n_val, frac = estadistica_zonal(grid, hand, mun[c]["geom"])
        fila = {"codigo": c, "municipio": mun[c]["nombre"], "depto": depto, "n_validos": n_val, "frac_hand_lt10": frac, **ac[c]}
        sede = divipola.resolver_por_codigo(c)
        if sede and sede.get("latitud") is not None:
            ij = celda(grid, sede["longitud"], sede["latitud"], forma)
            if ij and not np.isnan(hand[ij]):
                d = dist_via_m(sede["longitud"], sede["latitud"])
                fila["cab_bajo"] = bool(hand[ij] < CORTE_M)
                fila["cab_dist_via_m"] = d
        filas.append(fila)
    print(f"  listo ({time.time() - t0:.0f}s)", flush=True)
    return filas


def main():
    deptos = sys.argv[1].split(",")
    divipola._cargar_cache()
    previo = json.loads(DESTINO.read_text(encoding="utf-8"))["municipios"] if DESTINO.exists() else []
    out = [m for m in previo if m["depto"] not in deptos]
    for d in deptos:
        print(f"Departamento {d}", flush=True)
        try:
            out.extend(procesar(d, dc.poligonos([d])))
        except Exception as ex:
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:160]}", flush=True)
        DESTINO.write_text(json.dumps({"municipios": out}, ensure_ascii=False), encoding="utf-8")
        gc.collect()
    print(f"\n{len(out)} municipios guardados")


if __name__ == "__main__":
    main()
