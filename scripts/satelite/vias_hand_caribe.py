"""C1: exposicion de la red vial principal a terreno bajo (HAND), Caribe. Protocolo: PROTOCOLO_VIAS_HAND.md.

Uso: python scripts/satelite/vias_hand_caribe.py [codigos_depto separados por coma]
Salida: scripts/satelite/vias_hand_caribe.json (por municipio) y resumen por consola.
"""
from __future__ import annotations

import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import calcular_hand_caribe as ch  # noqa: E402  (tuberia HAND; envuelve stdout en UTF-8)
import _datos_caribe as dc  # noqa: E402
from pysheds.grid import Grid  # noqa: E402

CACHE = AQUI / "_cache"
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "structai-research/1.0 (academic research; github wilmerjoseperezorozco-dev)"
PASO_M = 90.0
CORTE_HAND_M = 10.0
KM_VIA_MIN = 5.0
CELDAS_MIN = 30
UMBRAL_RED_KM2 = 5.0
UMBRAL_RIO_KM2 = 25.0
TECHO = 0.90
N_BOOT = 5000
RNG = np.random.default_rng(20261108)
TIPOS_PUENTE_NO = {"no", ""}


def osm_vias(depto: str, bbox) -> dict:
    ruta = CACHE / f"osm_vias_{depto}.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    q = f'[out:json][timeout:300];way["highway"~"^(trunk|primary|secondary)$"]({s},{w},{n},{e});out geom tags;'
    for intento in range(4):
        try:
            req = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=400) as r:
                datos = json.load(r)
            break
        except Exception as ex:  # reintento con espera: Overpass limita la tasa
            print(f"  Overpass intento {intento + 1} fallo: {type(ex).__name__}", flush=True)
            time.sleep(30 * (intento + 1))
    else:
        raise RuntimeError("Overpass no respondio")
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return datos


def hand_y_acc(depto: str, pols: dict):
    mun = {c: p for c, p in pols.items() if c.startswith(depto)}
    xs = [b for p in mun.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in mun.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - ch.MARGEN, min(ys) - ch.MARGEN, max(xs) + ch.MARGEN, max(ys) + ch.MARGEN]
    f = ch.dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = grid.read_raster(str(f))
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
    fdir = grid.flowdir(inflated)
    acc = np.array(grid.accumulation(fdir), dtype="float64")
    lat = (bbox[1] + bbox[3]) / 2
    km2_celda = (ch.RES_GRADOS * ch.M_GRADO) ** 2 * math.cos(math.radians(lat)) / 1e6
    red = grid.accumulation(fdir) > (UMBRAL_RED_KM2 / km2_celda)
    hand = np.array(grid.compute_hand(fdir, inflated, red), dtype="float64")
    habiles = np.array(dem) != ch.NODATA
    hand[~habiles] = np.nan
    hand[hand < 0] = 0.0
    return mun, grid, hand, acc * km2_celda, habiles


def celda(grid, x, y, forma):
    col, row = ~grid.affine * (x, y)
    r, c = int(math.floor(row)), int(math.floor(col))
    return (r, c) if 0 <= r < forma[0] and 0 <= c < forma[1] else None


def puntos_linea(coords):
    """Puntos cada ~PASO_M a lo largo de la polilinea (lon, lat) y la longitud (km) que representa cada uno."""
    if len(coords) < 2:
        return [], 0.0
    ln = LineString(coords)
    k = math.cos(math.radians(np.mean([c[1] for c in coords])))
    largo_m = LineString([(x * k, y) for x, y in coords]).length * ch.M_GRADO   # grados de longitud encogidos por la latitud
    n = max(1, int(largo_m // PASO_M))
    pts = [ln.interpolate((i + 0.5) / n, normalized=True) for i in range(n)]
    return [(p.x, p.y) for p in pts], largo_m / n / 1000.0


def procesar(depto: str, pols: dict) -> list[dict]:
    t0 = time.time()
    mun, grid, hand, acc_km2, habiles = hand_y_acc(depto, pols)
    forma = hand.shape
    print(f"  HAND y acumulacion listos ({time.time() - t0:.0f}s)", flush=True)
    bb = [min(p["geom"].bounds[0] for p in mun.values()), min(p["geom"].bounds[1] for p in mun.values()),
          max(p["geom"].bounds[2] for p in mun.values()), max(p["geom"].bounds[3] for p in mun.values())]
    datos = osm_vias(depto, bb)
    vias = [e for e in datos.get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    print(f"  OSM: {len(vias)} tramos ({time.time() - t0:.0f}s); marca de tiempo OSM: {datos.get('osm3s', {}).get('timestamp_osm_base')}", flush=True)
    codigos = list(mun)
    arbol = STRtree([mun[c]["geom"] for c in codigos])

    def municipio_de(x, y):
        p = Point(x, y)
        for i in arbol.query(p, predicate="intersects"):
            return codigos[int(i)]
        return None

    acum = {c: {"km_via": 0.0, "km_bajo": 0.0, "puentes": 0, "puentes_rio": 0, "km_puente": 0.0} for c in codigos}
    for v in vias:
        tags = v.get("tags", {})
        es_puente = tags.get("bridge", "no") not in TIPOS_PUENTE_NO
        coords = [(g["lon"], g["lat"]) for g in v["geometry"]]
        pts, km_pt = puntos_linea(coords)
        if es_puente:
            mid = coords[len(coords) // 2]
            c = municipio_de(*mid)
            ij = celda(grid, mid[0], mid[1], forma)
            if c and ij:
                acum[c]["puentes"] += 1
                r, cc = ij
                vecindad = acc_km2[max(0, r - 1):r + 2, max(0, cc - 1):cc + 2]
                if np.nanmax(vecindad) >= UMBRAL_RIO_KM2:
                    acum[c]["puentes_rio"] += 1
                acum[c]["km_puente"] += len(pts) * km_pt
            continue
        for x, y in pts:
            c = municipio_de(x, y)
            ij = celda(grid, x, y, forma)
            if not c or not ij:
                continue
            h = hand[ij]
            if np.isnan(h):
                continue
            acum[c]["km_via"] += km_pt
            if h < CORTE_HAND_M:
                acum[c]["km_bajo"] += km_pt
    print(f"  muestreo listo ({time.time() - t0:.0f}s)", flush=True)
    filas = []
    for c, a in acum.items():
        filas.append({"codigo": c, "municipio": mun[c]["nombre"], "depto": depto, **a})
    return filas


def estadistica(filas, area_share):
    """Mediana de (exposicion vial - exposicion del territorio) con IC95 % por remuestreo de departamentos."""
    d = [(f["depto"], f["km_bajo"] / f["km_via"] - area_share[f["codigo"]]) for f in filas
         if f["km_via"] >= KM_VIA_MIN and f["codigo"] in area_share]
    if not d:
        return None
    deps = sorted({x[0] for x in d})
    med = float(np.median([x[1] for x in d]))
    bs = []
    for _ in range(N_BOOT):
        sel = RNG.choice(deps, len(deps), replace=True)
        v = [y for s in sel for dd, y in d if dd == s]
        if v:
            bs.append(np.median(v))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"n_municipios": len(d), "n_departamentos": len(deps), "mediana_dif": med, "ic95": [float(lo), float(hi)]}


def main() -> None:
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else list(dc.DEPTOS)
    pols = dc.poligonos()
    destino = AQUI / "vias_hand_caribe.json"
    previo = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {"municipios": []}
    filas = [m for m in previo["municipios"] if m["depto"] not in deptos]
    for d in deptos:
        print(f"Departamento {d} {dc.DEPTOS[d]}", flush=True)
        try:
            filas.extend(procesar(d, pols))
        except Exception as ex:
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:150]}", flush=True)
        destino.write_text(json.dumps({"municipios": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
    hand = json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"]
    area_share = {m["codigo"]: m["frac_hand_lt10_5"] for m in hand if "frac_hand_lt10_5" in m and m.get("n_validos_5", 0) >= CELDAS_MIN}
    for f in filas:
        f["exposicion_via"] = f["km_bajo"] / f["km_via"] if f["km_via"] > 0 else None
        f["exposicion_territorio"] = area_share.get(f["codigo"])
    res = {
        "C1a": estadistica(filas, area_share),
        "C1a_sin_techo": estadistica([f for f in filas if area_share.get(f["codigo"], 1) <= TECHO], area_share),
    }
    res["C1b"] = {}
    for d in sorted({f["depto"] for f in filas}):
        fs = [f for f in filas if f["depto"] == d]
        km_v = sum(f["km_via"] for f in fs)
        pu = sum(f["puentes"] for f in fs)
        res["C1b"][dc.DEPTOS[d]] = {"km_via_principal": round(km_v, 1), "puentes": pu,
                                    "puentes_por_100km": round(100 * pu / km_v, 2) if km_v else None,
                                    "puentes_sobre_rio_25km2": sum(f["puentes_rio"] for f in fs)}
    destino.write_text(json.dumps({"municipios": filas, "resultados": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n== Resultados ==")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
