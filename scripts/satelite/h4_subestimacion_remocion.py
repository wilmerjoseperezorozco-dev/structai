"""H4 (#273): ¿subestima la consulta por cabecera municipal el inventario de movimientos en masa cercano a un sitio?

Protocolo: PROTOCOLO_ANALISIS.md §29 (fijado antes de contar SIMMA alrededor de la malla).
Para cada municipio del panel de H3 se pone una malla de ~2 km dentro del polígono municipal (ANH/IGAC) y se cuenta,
en cada nodo y en la cabecera (DIVIPOLA), el número de puntos SIMMA a ≤ 15 km. El nodo representa "un sitio con GPS";
la cabecera representa "la consulta tradicional por municipio".

Uso:
  python -I h4_subestimacion_remocion.py --conteo   # solo geometría (malla, distancias); no cuenta SIMMA
  python -I h4_subestimacion_remocion.py            # análisis completo -> h4_subestimacion_resultados.json
Insumos: h4_descargar_insumos.py (SIMMA + polígonos) y h3_descargar_insumos.py (UNGRD + DIVIPOLA).
Entorno: numpy, pandas y scipy (sin shapely: punto en polígono par-impar propio).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h3_socavacion_puentes as h3  # noqa: E402

CACHE = AQUI / "_cache"
SALIDA = AQUI / "h4_subestimacion_resultados.json"
R_TIERRA = 6371.0
PASO_KM = 2.0
PASO_FINO_KM = 1.0          # municipios con < MIN_NODOS nodos a 2 km
MIN_NODOS = 5
RADIO_KM = 15.0
RADIO_SENS_KM = 5.0
FACTOR_SUB = 2.0
UMBRAL_CV = 0.30
UMBRAL_SUB = 0.10
UMBRAL_SUB_DESPRECIABLE = 0.05
h3.RNG = np.random.default_rng(2736)


# ── geometría ──────────────────────────────────────────────────────────────────────────────────────────────────────

def _anillos(geom: dict) -> list[np.ndarray]:
    if geom["type"] == "Polygon":
        return [np.asarray(r, float) for r in geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return [np.asarray(r, float) for p in geom["coordinates"] for r in p]
    raise ValueError(geom["type"])


def dentro(lon: np.ndarray, lat: np.ndarray, anillos: list[np.ndarray]) -> np.ndarray:
    """Punto en polígono por regla par-impar sobre todos los anillos (los huecos quedan fuera)."""
    res = np.zeros(lon.shape, bool)
    for r in anillos:
        x0, y0 = r[:-1, 0], r[:-1, 1]
        x1, y1 = r[1:, 0], r[1:, 1]
        for a, b, c, d in zip(x0, y0, x1, y1):
            if b == d:
                continue
            cruza = (b > lat) != (d > lat)
            xi = a + (lat - b) * (c - a) / (d - b)
            res ^= cruza & (lon < xi)
    return res


def malla(anillos: list[np.ndarray], paso_km: float) -> tuple[np.ndarray, np.ndarray]:
    todos = np.vstack(anillos)
    lo0, la0 = todos.min(0)
    lo1, la1 = todos.max(0)
    dlat = paso_km / 111.32
    dlon = paso_km / (111.32 * np.cos(np.radians((la0 + la1) / 2)))
    lats = np.arange(la0 + dlat / 2, la1, dlat)
    lons = np.arange(lo0 + dlon / 2, lo1, dlon)
    LO, LA = np.meshgrid(lons, lats)
    LO, LA = LO.ravel(), LA.ravel()
    m = dentro(LO, LA, anillos)
    return LO[m], LA[m]


def xyz(lon, lat) -> np.ndarray:
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def cuerda(km: float) -> float:
    return 2 * np.sin(km / R_TIERRA / 2)


# ── datos ──────────────────────────────────────────────────────────────────────────────────────────────────────────

def cargar() -> tuple[pd.DataFrame, dict]:
    ins = h3.insumos()
    panel, _, ung = h3.preparar(ins)
    cent = pd.DataFrame(ins["centroides"]).drop_duplicates("codigo").set_index("codigo")
    panel["lat_c"] = panel["codigo"].map(cent["lat"]).astype(float)
    panel["lon_c"] = panel["codigo"].map(cent["lon"]).astype(float)
    mm = ung[ung["ev"].str.contains("MASA") & ung["anio"].between(2019, 2024)]
    panel["n_mm_ungrd"] = panel["codigo"].map(mm.groupby("codigo_municipio").size()).fillna(0)
    pols = {}
    for dep in sorted(panel["depto2"].unique()):
        f = CACHE / f"poligonos_{dep}.geojson"
        if not f.exists():
            raise SystemExit(f"Falta {f}: corra h4_descargar_insumos.py")
        for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
            pols[str(ft["properties"]["CODIGO"]).zfill(5)] = _anillos(ft["geometry"])
    return panel, pols


def mallas(panel: pd.DataFrame, pols: dict) -> dict:
    out = {}
    for c in panel["codigo"]:
        if c not in pols:
            continue
        lo, la = malla(pols[c], PASO_KM)
        paso = PASO_KM
        if len(lo) < MIN_NODOS:
            lo, la = malla(pols[c], PASO_FINO_KM)
            paso = PASO_FINO_KM
        if len(lo) >= MIN_NODOS:
            out[c] = (lo, la, paso)
    return out


def conteo() -> None:
    panel, pols = cargar()
    M = mallas(panel, pols)
    p = panel[panel["codigo"].isin(M)]
    dist = []
    for c, la_c, lo_c in zip(p["codigo"], p["lat_c"], p["lon_c"]):
        lo, la, _ = M[c]
        dist.append(np.median(h3._km(la_c, lo_c, la, lo)))
    n = np.array([len(M[c][0]) for c in p["codigo"]])
    print(f"panel H3: {len(panel)}; con polígono: {sum(c in pols for c in panel['codigo'])}; con malla ≥ {MIN_NODOS} nodos: {len(M)}")
    print(f"malla fina (1 km): {sum(M[c][2] == PASO_FINO_KM for c in M)}; nodos totales: {n.sum()}; "
          f"nodos por municipio p10/p50/p90: {np.percentile(n, [10, 50, 90]).round(0)}")
    print(f"distancia mediana nodo-cabecera (km) p10/p50/p90: {np.percentile(dist, [10, 50, 90]).round(1)}")
    print(f"municipios por departamento (bloques): {p['depto2'].nunique()}")


# ── análisis ───────────────────────────────────────────────────────────────────────────────────────────────────────

def contar(arbol: cKDTree, lon, lat, radio_km: float) -> np.ndarray:
    return np.array([len(v) for v in arbol.query_ball_point(xyz(lon, lat), cuerda(radio_km))])


def metricas(panel, M, arbol, radio_km) -> pd.DataFrame:
    filas = []
    for _, r in panel[panel["codigo"].isin(M)].iterrows():
        lo, la, _ = M[r["codigo"]]
        ng = contar(arbol, lo, la, radio_km)
        nc = int(contar(arbol, np.array([r["lon_c"]]), np.array([r["lat_c"]]), radio_km)[0])
        media = ng.mean()
        filas.append({
            "codigo": r["codigo"], "municipio": r["municipio"], "depto2": r["depto2"], "region": r["region"],
            "S": r["S"], "n_mm_ungrd": r["n_mm_ungrd"], "area_km2": r["area_km2"], "nodos": len(ng),
            "n_cab": nc, "media": media, "max": int(ng.max()),
            "cv": (ng.std() / media) if media > 0 else np.nan,
            "sub": int((ng >= FACTOR_SUB * max(nc, 1)).sum()),
            "sobre": int((ng <= nc / FACTOR_SUB).sum()) if nc > 0 else 0,
            "con_simma": bool(ng.max() >= 1 or nc >= 1)})
    return pd.DataFrame(filas)


def veredicto(ic, umbral_si, umbral_no, si, no):
    if ic[0] > umbral_si:
        return si
    if ic[1] < umbral_no:
        return no
    return "NO CONCLUYENTE"


def analizar(m: pd.DataFrame) -> dict:
    b = m["depto2"].values
    cvok = m["cv"].notna().values
    med_cv = lambda ix: float(np.nanmedian(m["cv"].values[ix]))   # noqa: E731
    act = m["con_simma"].values

    def frac_sub(ix):
        ix = ix[act[ix]]
        return m["sub"].values[ix].sum() / m["nodos"].values[ix].sum()

    todo = np.arange(len(m))
    c1, c2 = med_cv(todo), frac_sub(todo)
    ic1, ic2 = h3.boot(med_cv, b), h3.boot(frac_sub, b)
    ma = m[act]
    cab0 = ma[ma["n_cab"] == 0]
    res = {
        "n_municipios_malla": len(m), "n_con_simma": int(act.sum()), "n_con_cv": int(cvok.sum()),
        "C1_mediana_cv": {"valor": c1, "ic95": ic1,
                          "veredicto": veredicto(ic1, UMBRAL_CV, UMBRAL_CV, "HETEROGÉNEO", "HOMOGÉNEO")},
        "C2_fraccion_area_subestimada": {"valor": c2, "ic95": ic2,
                                         "veredicto": veredicto(ic2, UMBRAL_SUB, UMBRAL_SUB_DESPRECIABLE,
                                                                "SUBESTIMACIÓN MATERIAL", "DESPRECIABLE")},
        "D_fraccion_area_sobreestimada": float(ma["sobre"].sum() / ma["nodos"].sum()),
        "D_cabecera_cero": {"municipios": len(cab0),
                            "con_algun_nodo_simma": int((cab0["max"] >= 1).sum()),
                            "con_10pct_area_simma_ge2": int((cab0["sub"] / cab0["nodos"] >= 0.10).sum())},
        "D_cv_percentiles_10_50_90": [float(v) for v in np.nanpercentile(m["cv"], [10, 50, 90])],
        "D_max_sobre_cabecera_mediana": float(np.median(ma["max"] / np.maximum(ma["n_cab"], 1))),
    }
    # S1 (secundario): historial UNGRD de movimientos en masa 2019-2024 frente a la consulta por cabecera y por malla
    y = m["n_mm_ungrd"].values
    rho = lambda col, ix: float(spearmanr(m[col].values[ix], y[ix])[0])   # noqa: E731
    res["S1_spearman_ungrd_mm"] = {col: {"rho": rho(col, todo), "ic95": h3.boot(lambda ix: rho(col, ix), b)}
                                   for col in ("n_cab", "media", "max")}
    res["S1_diferencia_media_menos_cab"] = {
        "valor": rho("media", todo) - rho("n_cab", todo),
        "ic95": h3.boot(lambda ix: rho("media", ix) - rho("n_cab", ix), b)}
    res["S1_spearman_cv_ungrd_mm"] = rho("cv", np.where(cvok)[0])
    # Descriptivo por región y por tercil de pendiente
    m = m.assign(tercil_S=pd.qcut(m["S"], 3, labels=["baja", "media", "alta"]))
    res["D_por_region"] = {r: {"n": len(g), "mediana_cv": float(np.nanmedian(g["cv"])),
                               "frac_sub": float(g.loc[g["con_simma"], "sub"].sum() / max(g.loc[g["con_simma"], "nodos"].sum(), 1))}
                           for r, g in m.groupby("region")}
    res["D_por_tercil_pendiente"] = {str(t): {"n": len(g), "mediana_cv": float(np.nanmedian(g["cv"])),
                                              "frac_sub": float(g.loc[g["con_simma"], "sub"].sum() / max(g.loc[g["con_simma"], "nodos"].sum(), 1))}
                                     for t, g in m.groupby("tercil_S", observed=True)}
    top = m.assign(fs=m["sub"] / m["nodos"]).sort_values(["fs", "max"], ascending=False).head(10)
    res["D_top10_subestimados"] = top[["codigo", "municipio", "n_cab", "max", "fs", "nodos"]].round(3).to_dict("records")
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if "--conteo" in sys.argv:
        conteo()
        return
    panel, pols = cargar()
    M = mallas(panel, pols)
    pts = np.asarray([p[:2] for p in json.loads((CACHE / "simma_puntos.json").read_text(encoding="utf-8"))], float)
    arbol = cKDTree(xyz(pts[:, 0], pts[:, 1]))
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §29", "n_simma": len(pts), "radio_km": RADIO_KM, "paso_km": PASO_KM}
    m15 = metricas(panel, M, arbol, RADIO_KM)
    out["principal_15km"] = analizar(m15)
    out["sensibilidad_5km"] = analizar(metricas(panel, M, arbol, RADIO_SENS_KM))
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
