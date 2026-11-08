"""Catalogo de sismos del SGC vs Aa del A-4. Protocolo: PROTOCOLO_CATALOGO_SISMOS_VS_A4.md. Solo lectura de servicios publicos."""
import glob
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import requests
from scipy.stats import spearmanr
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
SAT = AQUI.parents[1] / "satelite"
URL = "https://srvags.sgc.gov.co/arcgis/rest/services/catalogo_sismos/catalogo_de_sismos_2/MapServer/0/query"
CACHE = AQUI / "raw" / "catalogo_sismos_sgc.json"
ANIO_INI, ANIO_FIN = 1993, 2020
N_BOOT = 2000
RNG = np.random.default_rng(32)
KM_POR_GRADO = 111.32


def bajar() -> list[dict]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    ids = requests.get(URL, params={"where": "1=1", "returnIdsOnly": "true", "f": "json"}, timeout=90).json()["objectIds"]
    ev = []
    for a in range(min(ids), max(ids) + 1, 1000):
        r = requests.get(URL, params={"where": f"OBJECTID>={a} AND OBJECTID<{a + 1000}", "returnGeometry": "false", "f": "json",
                                      "outFields": "OBJECTID,ESP_MAGNITUD,ESP_PROFUNDIDAD,ESP_LATITUD,ESP_LONGITUD,ESP_FECHA_LONG"}, timeout=90).json()
        ev += [f["attributes"] for f in r["features"]]
        time.sleep(0.4)
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(ev), encoding="utf-8")
    return ev


def boot(fun, bloques):
    et = np.unique(bloques)
    idx = {b: np.where(bloques == b)[0] for b in et}
    out = []
    for _ in range(N_BOOT):
        ix = np.concatenate([idx[b] for b in RNG.choice(et, len(et), replace=True)])
        v = fun(ix)
        if np.isfinite(v):
            out.append(v)
    return [float(v) for v in np.percentile(out, [2.5, 97.5])]


def main() -> None:
    ev = bajar()
    print("eventos bajados:", len(ev))
    pols, area = [], {}
    cods = []
    for f in sorted(glob.glob(str(SAT / "_cache" / "poligonos_nac_*.geojson"))):
        for ft in json.loads(Path(f).read_text(encoding="utf-8"))["features"]:
            g = shape(ft["geometry"])
            c = ft["properties"]["CODIGO"]
            pols.append(g)
            cods.append(c)
            area[c] = g.area * KM_POR_GRADO ** 2 * np.cos(np.radians(g.centroid.y))
    arbol = STRtree(pols)
    a4 = {f["codigo"]: f for f in json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8"))}
    filas = []
    for e in ev:
        if e["ESP_FECHA_LONG"] is None or e["ESP_MAGNITUD"] is None:
            continue
        anio = (datetime(1970, 1, 1) + timedelta(milliseconds=e["ESP_FECHA_LONG"])).year
        if not (ANIO_INI <= anio <= ANIO_FIN):
            continue
        p = Point(e["ESP_LONGITUD"], e["ESP_LATITUD"])
        for i in arbol.query(p, predicate="within"):
            filas.append((cods[i], e["ESP_MAGNITUD"], e["ESP_PROFUNDIDAD"] if e["ESP_PROFUNDIDAD"] is not None else np.nan))
            break
    mag = np.array([m for _, m, _ in filas])
    h, bordes = np.histogram(mag, bins=np.arange(3.0, 7.0, 0.1))
    mc = float(bordes[h.argmax()])
    R = {"eventos_catalogo": len(ev), "eventos_en_municipio_1993_2020": len(filas), "magnitud_completitud_max_curvatura": round(mc, 1)}
    anios = ANIO_FIN - ANIO_INI + 1

    def tasa(mmin, hmax=None):
        n = {c: 0 for c in a4}
        for c, m, h_ in filas:
            if c in n and m >= mmin and (hmax is None or not (h_ > hmax)):
                n[c] += 1
        cs = [c for c in a4 if c in area]
        return cs, np.array([n[c] / area[c] * 1000 / anios for c in cs]), np.array([n[c] for c in cs])

    for etiqueta, mmin, hmax in (("M4.0", 4.0, None), ("M3.5", 3.5, None), ("M4.5", 4.5, None), ("M4.0_prof_le_70", 4.0, 70)):
        cs, t, n = tasa(mmin, hmax)
        aa = np.array([a4[c]["aa"] for c in cs]); dep = np.array([c[:2] for c in cs]); zona = np.array([a4[c]["zona"] for c in cs])
        r = {"n_municipios": len(cs), "eventos": int(n.sum()), "municipios_con_evento": int((n > 0).sum()),
             "C1_rho": [float(spearmanr(aa, t)[0])] + boot(lambda i: spearmanr(aa[i], t[i])[0], dep)}
        med = {z: float(np.median(t[zona == z])) for z in ("Baja", "Intermedia", "Alta")}
        r["tasa_mediana_por_zona"] = med
        r["frac_con_evento_por_zona"] = {z: float((n[zona == z] > 0).mean()) for z in ("Baja", "Intermedia", "Alta")}
        r["C2_monotona"] = bool(med["Baja"] < med["Intermedia"] < med["Alta"])
        if etiqueta == "M4.0":
            b = np.where(zona == "Baja")[0]; al = np.where(zona == "Alta")[0]
            f = lambda i: (np.mean(t[i][zona[i] == "Alta"]) / max(np.mean(t[i][zona[i] == "Baja"]), 1e-12)) if (zona[i] == "Baja").any() and (zona[i] == "Alta").any() else np.nan  # noqa: E731
            r["razon_media_Alta_Baja"] = [float(f(np.arange(len(cs))))] + boot(f, dep)
            q90 = np.percentile(t, 90)
            r["baja_con_tasa_decil_alto"] = [{"codigo": c, "municipio": a4[c]["municipio"], "dep": a4[c]["departamento"], "aa": a4[c]["aa"], "eventos": int(k), "tasa": round(float(x), 3)}
                                             for c, k, x in zip(cs, n, t) if a4[c]["zona"] == "Baja" and x >= q90]
            r["alta_sin_eventos"] = int(((zona == "Alta") & (n == 0)).sum())
            r["n_alta"] = int((zona == "Alta").sum())
        R[etiqueta] = r
    (AQUI / "auditoria_catalogo_sismos_vs_a4.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in R.items():
        if isinstance(v, dict):
            print(k, {a: b for a, b in v.items() if a != "baja_con_tasa_decil_alto"})
        else:
            print(k, v)
    print("zona Baja con tasa en el decil alto:", len(R["M4.0"]["baja_con_tasa_decil_alto"]))
    for x in R["M4.0"]["baja_con_tasa_decil_alto"][:20]:
        print(x)


if __name__ == "__main__":
    main()
