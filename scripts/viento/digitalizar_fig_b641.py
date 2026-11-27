"""#320: digitaliza las regiones de viento de la Fig. B.6.4-1 de la NSR-10 (mapa vectorial del PDF oficial).

Georreferenciación: la propia cuadrícula del mapa (líneas de -80° a -66° de longitud y de -5° a 13° de latitud),
transformación lineal en pt → (lon, lat). Las fronteras de región son el trazo de 1,96 pt; el contorno del país, el de
1,35 pt. Las caras que forman se rotulan con el número dentro del círculo blanco que cae en cada cara. Las caras sin
número son las de la nota ("zonas no estudiadas": se toma 28 m/s, como dice la nota).

Uso, en dos pasos porque pymupdf y shapely viven en entornos distintos (el PDF oficial es local y no se versiona):
  python -I scripts/viento/digitalizar_fig_b641.py extraer <ruta_pdf_nsr10> <trazos.json>       (entorno con pymupdf)
  python -I scripts/viento/digitalizar_fig_b641.py poligonizar <trazos.json> data/viento/regiones_b641.geojson  (shapely)
"""
from __future__ import annotations

import json
import sys


PAGINA = 257                                   # índice 0 de la página B-39
X0, X1, LON0, LON1 = 76.7, 521.2, -80.0, -66.0  # líneas de la cuadrícula (pt)
Y0, Y1, LAT0, LAT1 = 111.0, 682.9, 13.0, -5.0
V_REGION = {1: 17.0, 2: 22.0, 3: 28.0, 4: 33.0, 5: 36.0}
V_NOTA = 28.0
TOL_CIERRE = 0.10                              # grados (~11 km)
TOL_ROTULO = 0.15                              # grados: un rótulo fuera de toda cara se asigna a la más cercana
LAT_CORTE_VALLEDUPAR = 10.32                   # grados: corte declarado (ver poligonizar)
AREA_ASTILLA = 0.01                            # grados²: caras diminutas que crean los cierres


def lonlat(x: float, y: float) -> tuple[float, float]:
    return LON0 + (x - X0) * (LON1 - LON0) / (X1 - X0), LAT0 + (y - Y0) * (LAT1 - LAT0) / (Y1 - Y0)


def _bezier(p0, p1, p2, p3, n=12):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0.x + b * p1.x + c * p2.x + d * p3.x, a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return out


def trazos(dibujo) -> list[list[tuple[float, float]]]:
    """Segmentos del dibujo en (lon, lat); las curvas Bézier se muestrean."""
    out = []
    for it in dibujo["items"]:
        if it[0] == "l":
            pts = [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == "c":
            pts = _bezier(*it[1:5])
        else:
            continue
        out.append([lonlat(*p) for p in pts])
    return out


def extraer(pdf: str, salida: str) -> None:
    import fitz
    pg = fitz.open(pdf)[PAGINA]
    dib = pg.get_drawings()
    pais = [d for d in dib if d["type"] == "s" and abs((d.get("width") or 0) - 1.35) < 0.05]
    fronteras = [d for d in dib if d["type"] == "s" and abs((d.get("width") or 0) - 1.96) < 0.05]
    assert len(pais) == 1 and len(fronteras) == 1, (len(pais), len(fronteras))
    circulos = [d for d in dib if d["type"] == "fs" and d.get("fill") == (1.0, 1.0, 1.0) and abs(d["rect"].width - 14.7) < 0.5
                and abs(d["rect"].height - 14.7) < 0.5]
    numeros = [s for b in pg.get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"]
               if s["text"].strip() in {"1", "2", "3", "4", "5"}]
    rotulos = []
    for c in circulos:
        r = c["rect"]
        dentro = [s for s in numeros if r.contains(fitz.Point((s["bbox"][0] + s["bbox"][2]) / 2, (s["bbox"][1] + s["bbox"][3]) / 2))]
        if len(dentro) == 1:
            rotulos.append((lonlat((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), int(dentro[0]["text"].strip())))
    with open(salida, "w", encoding="utf-8") as f:
        json.dump({"pais": trazos(pais[0]), "fronteras": trazos(fronteras[0]), "rotulos": rotulos,
                   "n_circulos": len(circulos)}, f)
    print(f"{len(rotulos)} rótulos de {len(circulos)} círculos")


def poligonizar(entrada: str, salida: str) -> None:
    from shapely.geometry import LineString, Point, mapping
    from shapely.ops import polygonize, unary_union
    with open(entrada, encoding="utf-8") as f:
        t = json.load(f)
    rotulos = [(Point(p), reg) for p, reg in t["rotulos"]]
    from shapely.geometry import MultiLineString
    from shapely.ops import linemerge, nearest_points
    fr = linemerge(MultiLineString([LineString(s) for s in t["fronteras"]]))
    fr = list(getattr(fr, "geoms", [fr]))
    pais = [LineString(s) for s in t["pais"]]
    # el trazo de las fronteras no siempre toca la línea vecina: se cierra cada extremo libre con el punto más cercano
    # de las demás líneas si está a menos de TOL_CIERRE grados; el máximo se reporta como incertidumbre
    cierres = []
    for i, ln in enumerate(fr):
        if ln.is_ring:
            continue
        otros = unary_union([g for j, g in enumerate(fr) if j != i] + pais)
        for e in (Point(ln.coords[0]), Point(ln.coords[-1])):
            d = e.distance(otros)
            if d > TOL_CIERRE:
                raise RuntimeError(f"extremo libre a {d:.3f}° de cualquier línea: {e}")
            if d > 0:                                          # se prolonga 0,002° más allá para que cruce y se nodalice
                q = nearest_points(e, otros)[1]
                ux, uy = (q.x - e.x) / d, (q.y - e.y) / d
                cierres.append((LineString([e, (q.x + 0.002 * ux, q.y + 0.002 * uy)]), d))
    lineas = unary_union(fr + pais + [c for c, _d in cierres])
    caras = list(polygonize(lineas))
    # Corte declarado: el rótulo "VALLEDUPAR" tapa las líneas que separan la franja 1 (sur) de la franja 2 (norte); el
    # hueco va de ~10,15° a ~10,49° de latitud. Se cierra con la recta lat = LAT_CORTE_VALLEDUPAR, solo dentro de la
    # cara que contiene esa franja. Los municipios a menos de R_FRONTERA del corte quedan como frontera.
    pv = Point(-72.95, LAT_CORTE_VALLEDUPAR)
    cara_v = [c for c in caras if c.contains(pv)]
    if cara_v:
        corte = cara_v[0].intersection(LineString([(-74.5, LAT_CORTE_VALLEDUPAR), (-72.0, LAT_CORTE_VALLEDUPAR)]))
        partes = list(getattr(corte, "geoms", [corte]))
        caras = list(polygonize(unary_union([lineas] + [LineString(p.coords) for p in partes if p.length > 0])))
    # 1) rótulo dentro de la cara; 2) rótulo fuera de toda cara (el círculo cae sobre una línea o fuera del país): a la
    # cara más cercana si está a menos de TOL_ROTULO; 3) cara con rótulos distintos: AMBIGUA, se toma la V máxima
    asign = {k: set() for k in range(len(caras))}
    fuera = []
    for pto, reg in rotulos:
        dentro = [k for k, c in enumerate(caras) if c.contains(pto)]
        if dentro:
            asign[dentro[0]].add(reg)
            continue
        d, k = min((c.distance(pto), k) for k, c in enumerate(caras))
        if d <= TOL_ROTULO:
            asign[k].add(reg)
        fuera.append({"region": reg, "lonlat": [round(pto.x, 3), round(pto.y, 3)], "dist_grados": round(d, 3),
                      "cara": k if d <= TOL_ROTULO else None})
    feats = []
    for k, cara in enumerate(caras):
        regs = sorted(asign[k])
        if regs:
            estado = "rotulo" if len(regs) == 1 else "ambigua: rótulos " + "/".join(map(str, regs)) + " (se toma la máxima)"
            v = max(V_REGION[x] for x in regs)
        elif cara.area < AREA_ASTILLA:
            vec = [max(V_REGION[x] for x in asign[j]) for j, c in enumerate(caras) if j != k and asign[j] and c.touches(cara)]
            v, estado = (max(vec), "astilla del cierre: V máxima de las vecinas") if vec else (V_NOTA, "astilla sin vecinas rotuladas")
        else:
            v, estado = V_NOTA, "sin rótulo: nota de la figura (28 m/s)"
        feats.append({"type": "Feature", "geometry": mapping(cara),
                      "properties": {"cara": k, "regiones": regs, "v_m_s": v, "estado": estado,
                                     "area_grados2": round(cara.area, 4)}})
    geo = {"type": "FeatureCollection", "fuente": "NSR-10 Fig. B.6.4-1 (PDF oficial), digitalizada por scripts/viento/digitalizar_fig_b641.py",
           "rotulos_fuera_de_caras": fuera, "cierre_max_grados": max((d for _c, d in cierres), default=0.0),
           "features": feats}
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(geo, f, ensure_ascii=False)
    print(f"{len(caras)} caras, {len(rotulos)} rótulos, fuera de caras: {fuera}, {len(cierres)} cierres, "
          f"máx {geo['cierre_max_grados']:.3f}°")
    for ft in sorted(feats, key=lambda f: -f["properties"]["area_grados2"]):
        p = ft["properties"]
        print(p["cara"], p["regiones"], p["v_m_s"], p["area_grados2"], p["estado"])


if __name__ == "__main__":
    {"extraer": extraer, "poligonizar": poligonizar}[sys.argv[1]](sys.argv[2], sys.argv[3])
