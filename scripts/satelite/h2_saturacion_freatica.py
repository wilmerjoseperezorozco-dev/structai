"""H2 (#273): ¿se puede inferir un nivel freático somero (≤ 2 m) sin perforar, por proximidad hidrológica?

Protocolo: PROTOCOLO_ANALISIS.md §30 (fijado antes de cruzar niveles con predictores).
Resultado medido: nivel estático de pozos y aljibes de los inventarios de puntos de agua del SGC (CC BY 4.0).
Predictores (la cadena propuesta):
  S = relieve local: cota DEM del punto − cota mínima del DEM a ≤ 1 km (Copernicus GLO-90)
  E = cota DEM del punto − altitud de la estación de caudal IDEAM más cercana (≤ 30 km; sin estación → rango neutro)
  G = IGAC del municipio: media de la fracción con drenaje deficiente y la fracción inundable
  índice = media de rangos percentiles de (−S, −E, G)
Uso:
  python -I h2_saturacion_freatica.py --conteo   # muestra elegible; no cruza nivel con predictores
  python -I h2_saturacion_freatica.py            # análisis -> h2_saturacion_resultados.json
Entorno: numpy, scipy, pandas y rasterio (C:\\Users\\wilme\\dev\\venvs\\geo).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h3_socavacion_puentes as h3  # noqa: E402
import h4_subestimacion_remocion as h4  # noqa: E402

CACHE = AQUI / "_cache"
SALIDA = AQUI / "h2_saturacion_resultados.json"
UMBRAL_SOMERO_M = 2.0
RADIO_RELIEVE_KM = 1.0
RADIO_RELIEVE_SENS_KM = 3.0
KM_MAX_ESTACION = 30.0
CELDA_BLOQUE_GRADOS = 0.10
AUC_UTIL, AUC_NO_UTIL = 0.60, 0.55
TIPOS = {"POZO": "pozo", "ALJIBE": "aljibe"}
RNG_SEMILLA = 2732
h3.RNG = np.random.default_rng(RNG_SEMILLA)


def _num(v):
    try:
        x = float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return np.nan
    return x if 0 < x <= 200 else np.nan


def _mediana(*vals):
    v = [x for x in vals if np.isfinite(x)]
    return float(np.median(v)) if v else np.nan


# Regla fija de qué campo es el nivel estático (m bajo la superficie), según el nombre del campo:
NIVEL = {
    "guaviare": lambda a: _num(a.get("Nivel_E")),
    "meta": lambda a: _num(a.get("I_Nivel")) if np.isfinite(_num(a.get("I_Nivel"))) else _num(a.get("V_Nivel")),
    "inirida": lambda a: _mediana(_num(a.get("NE_Seco")), _num(a.get("NE_hum")), _num(a.get("NE_interm"))),
}
NIVEL_SENSIBILIDAD = {"casanare": lambda a: _num(a.get("PROFUNDI_4"))}   # campo de nombre ambiguo
CAMPO_TIPO = {"guaviare": "Tipo_de_pu", "meta": "Tipo", "inirida": "Tipo_de_pu", "casanare": "TIPO_DE_PU"}


def puntos(incluir_sensibilidad: bool) -> pd.DataFrame:
    reglas = {**NIVEL, **(NIVEL_SENSIBILIDAD if incluir_sensibilidad else {})}
    filas = []
    for capa, regla in reglas.items():
        for f in json.loads((CACHE / f"h2_puntos_agua_{capa}.json").read_text(encoding="utf-8"))["features"]:
            g, a = f.get("geometry") or {}, f["attributes"]
            tipo = TIPOS.get(str(a.get(CAMPO_TIPO[capa]) or "").strip().upper())
            if "x" not in g or tipo is None:
                continue
            filas.append({"capa": capa, "tipo": tipo, "lon": g["x"], "lat": g["y"], "nivel_m": regla(a)})
    return pd.DataFrame(filas)


# ── predictores ────────────────────────────────────────────────────────────────────────────────────────────────────

class DEM:
    def __init__(self):
        self.fuentes = {}
        for f in (CACHE / "dem90").glob("*.tif"):
            self.fuentes[f.stem] = rasterio.open(f)

    def _tesela(self, lat, lon):
        la, lo = math.floor(lat), math.floor(lon)
        n = f"Copernicus_DSM_COG_30_{'N' if la >= 0 else 'S'}{abs(la):02d}_00_{'E' if lo >= 0 else 'W'}{abs(lo):03d}_00_DEM"
        return self.fuentes.get(n)

    def ventana(self, lat, lon, radio_km):
        """Cota del punto y cota mínima a ≤ radio (solo dentro de la tesela del punto: borde declarado)."""
        src = self._tesela(lat, lon)
        if src is None:
            return np.nan, np.nan
        r, c = src.index(lon, lat)
        dy = radio_km / 111.32 / abs(src.res[1])
        dx = radio_km / (111.32 * math.cos(math.radians(lat))) / abs(src.res[0])
        r0, r1 = max(int(r - dy), 0), min(int(r + dy) + 1, src.height)
        c0, c1 = max(int(c - dx), 0), min(int(c + dx) + 1, src.width)
        a = src.read(1, window=((r0, r1), (c0, c1))).astype(float)
        a[a < -100] = np.nan
        yy, xx = np.mgrid[r0:r1, c0:c1]
        dentro = ((yy - r) / dy) ** 2 + ((xx - c) / dx) ** 2 <= 1
        z = a[r - r0, c - c0] if (0 <= r - r0 < a.shape[0] and 0 <= c - c0 < a.shape[1]) else np.nan
        return z, np.nanmin(np.where(dentro, a, np.nan))


def municipio(p: pd.DataFrame) -> list[str | None]:
    pols = {}
    for dep in ("50", "63", "85", "94", "95"):
        for ft in json.loads((CACHE / f"poligonos_{dep}.geojson").read_text(encoding="utf-8"))["features"]:
            pols[str(ft["properties"]["CODIGO"]).zfill(5)] = h4._anillos(ft["geometry"])
    out = []
    for lon, lat in zip(p["lon"], p["lat"]):
        cod = None
        for c, an in pols.items():
            todos = np.vstack(an)
            if not (todos[:, 0].min() <= lon <= todos[:, 0].max() and todos[:, 1].min() <= lat <= todos[:, 1].max()):
                continue
            if h4.dentro(np.array([lon]), np.array([lat]), an)[0]:
                cod = c
                break
        out.append(cod)
    return out


def predictores(p: pd.DataFrame) -> pd.DataFrame:
    dem = DEM()
    z, zmin1, zmin3 = [], [], []
    for lat, lon in zip(p["lat"], p["lon"]):
        a, b = dem.ventana(lat, lon, RADIO_RELIEVE_KM)
        _, c = dem.ventana(lat, lon, RADIO_RELIEVE_SENS_KM)
        z.append(a); zmin1.append(b); zmin3.append(c)
    p = p.assign(z_dem=z, S=np.array(z) - np.array(zmin1), S3=np.array(z) - np.array(zmin3))
    est = np.asarray(json.loads((CACHE / "h2_ideam_estaciones.json").read_text(encoding="utf-8"))["estaciones"], float)
    arbol = cKDTree(h4.xyz(est[:, 2], est[:, 1]))
    d, i = arbol.query(h4.xyz(p["lon"].values, p["lat"].values))
    km = 2 * h4.R_TIERRA * np.arcsin(np.clip(d / 2, 0, 1))
    p["km_estacion"] = km
    p["E"] = np.where(km <= KM_MAX_ESTACION, p["z_dem"].values - est[i, 3], np.nan)
    igac = json.loads((CACHE / "h2_igac_municipal.json").read_text(encoding="utf-8"))["municipios"]
    p["codigo_municipio"] = municipio(p)
    p["G"] = [np.mean(igac[c]) if c in igac else np.nan for c in p["codigo_municipio"]]
    p["bloque"] = [f"{math.floor(la / CELDA_BLOQUE_GRADOS)}_{math.floor(lo / CELDA_BLOQUE_GRADOS)}"
                   for la, lo in zip(p["lat"], p["lon"])]
    return p


def indice(p: pd.DataFrame, cols=("S", "E", "G"), signos=(-1, -1, 1)) -> np.ndarray:
    pr = []
    for c, s in zip(cols, signos):
        x = p[c].values * s
        r = np.full(len(p), 0.5)
        ok = np.isfinite(x)
        r[ok] = (rankdata(x[ok]) - 0.5) / ok.sum()
        pr.append(r)
    return np.mean(pr, axis=0)


# ── análisis ───────────────────────────────────────────────────────────────────────────────────────────────────────

def veredicto(ic):
    if ic[0] > AUC_UTIL:
        return "ÚTIL"
    if ic[1] < AUC_NO_UTIL:
        return "NO ÚTIL"
    return "NO CONCLUYENTE"


def analizar(p: pd.DataFrame, umbral=UMBRAL_SOMERO_M) -> dict:
    p = p[np.isfinite(p["nivel_m"]) & np.isfinite(p["S"])].reset_index(drop=True)
    y = (p["nivel_m"] <= umbral).astype(int).values
    I, rS = indice(p), indice(p, ("S",), (-1,))
    b = p["bloque"].values
    auc = lambda x, ix: h3.auc(x[ix], y[ix])   # noqa: E731
    todo = np.arange(len(p))
    r = {"n": len(p), "n_someros": int(y.sum()), "n_bloques": int(len(set(b))),
         "C1_auc_indice": {"valor": auc(I, todo), "ic95": h3.boot(lambda ix: auc(I, ix), b)},
         "C2_delta_auc_indice_menos_relieve": {"valor": auc(I, todo) - auc(rS, todo),
                                               "ic95": h3.boot(lambda ix: auc(I, ix) - auc(rS, ix), b)}}
    r["C1_auc_indice"]["veredicto"] = veredicto(r["C1_auc_indice"]["ic95"])
    for c, s in (("S", -1), ("S3", -1), ("E", -1), ("G", 1)):
        x = indice(p, (c,), (s,))
        r[f"auc_{c}"] = {"valor": auc(x, todo), "ic95": h3.boot(lambda ix: auc(x, ix), b)}
    r["spearman_indice_vs_profundidad"] = float(spearmanr(I, p["nivel_m"])[0])
    r["por_tipo"] = {t: {"n": int((p["tipo"] == t).sum()), "someros": int(y[p["tipo"].values == t].sum()),
                         "auc_indice": float(h3.auc(I[p["tipo"].values == t], y[p["tipo"].values == t]))
                         if 0 < y[p["tipo"].values == t].sum() < (p["tipo"] == t).sum() else None}
                     for t in ("pozo", "aljibe")}
    r["por_capa"] = {c: {"n": int((p["capa"] == c).sum()), "someros": int(y[p["capa"].values == c].sum()),
                         "auc_indice": float(h3.auc(I[p["capa"].values == c], y[p["capa"].values == c]))
                         if 0 < y[p["capa"].values == c].sum() < (p["capa"] == c).sum() else None}
                     for c in sorted(p["capa"].unique())}
    # Regla operativa para /sitio: alarma si el índice está en el tercio superior
    alto = I >= np.quantile(I, 2 / 3)
    r["alarma_tercio_superior"] = {"sensibilidad": float(y[alto].sum() / max(y.sum(), 1)),
                                   "valor_predictivo_positivo": float(y[alto].mean()),
                                   "prevalencia": float(y.mean())}
    return r


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = predictores(puntos(incluir_sensibilidad=True))
    prim = p[p["capa"].isin(NIVEL)]
    if "--conteo" in sys.argv:
        for nombre, q in (("principal", prim), ("con casanare", p)):
            ok = q[np.isfinite(q["nivel_m"])]
            print(f"{nombre}: puntos pozo/aljibe {len(q)}, con nivel {len(ok)}, con DEM {int(np.isfinite(ok['S']).sum())}, "
                  f"con estación ≤ {KM_MAX_ESTACION:.0f} km {int(np.isfinite(ok['E']).sum())}, "
                  f"con IGAC {int(np.isfinite(ok['G']).sum())}, bloques {ok['bloque'].nunique()}, "
                  f"por capa {ok['capa'].value_counts().to_dict()}, por tipo {ok['tipo'].value_counts().to_dict()}")
        return
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §30", "umbral_m": UMBRAL_SOMERO_M,
           "principal": analizar(prim),
           "sensibilidad_umbral_1m": analizar(prim, 1.0), "sensibilidad_umbral_3m": analizar(prim, 3.0),
           "sensibilidad_con_casanare": analizar(p)}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
