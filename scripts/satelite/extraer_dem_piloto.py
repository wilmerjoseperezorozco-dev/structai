"""Piloto satelital, paso 1 (issue #95, Frente C): relieve desde Copernicus DEM
GLO-30 para los municipios de un departamento.

Solo EXTRAE y VERIFICA, no entrena nada. Objetivo: comprobar que la cadena
(catalogo STAC abierto -> raster en la nube -> estadistica zonal) produce
numeros creibles ANTES de usarla como predictor.

Decisiones de metodo (declaradas, no escondidas):
- Zona = circulo de RADIO_KM alrededor del centroide DIVIPOLA. NO es el poligono
  municipal (no esta en el repo); es una aproximacion. Cuando haya poligonos
  oficiales (DANE MGN) se reemplaza y se re-corre.
- Pendiente por diferencias finitas con tamano de pixel en metros (corregido por
  latitud), sobre TODOS los pixeles de la zona (estadistica zonal), a diferencia
  del muestreo de 5 puntos de fase2 (SRTM).
- Verificacion cruzada: se compara contra la pendiente SRTM ya publicada en
  fase2_elevacion_resultados.json para los municipios en comun.

Uso: python scripts/satelite/extraer_dem_piloto.py [Departamento] [radio_km]
Sin claves ni cuenta. Salida: scripts/satelite/dem_<depto>.json
"""
from __future__ import annotations

import io
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds
from scipy.stats import spearmanr

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
import divipola  # noqa: E402

STAC = "https://earth-search.aws.element84.com/v1/search"
RADIO_KM_DEFECTO = 5.0
M_POR_GRADO_LAT = 111_320.0
BAJO_NIVEL_M = 10.0  # umbral descriptivo de llanura baja, no un criterio normativo


def _municipios(depto: str) -> list[dict]:
    divipola._cargar_cache()
    canon = divipola.resolver_departamento(depto)
    if not canon:
        raise SystemExit(f"Departamento no reconocido: {depto}")
    return [r for r in divipola._CACHE if r["departamento"] == canon and r["latitud"] is not None]


def _href_dem(bbox: list[float]) -> list[str]:
    cuerpo = json.dumps({"collections": ["cop-dem-glo-30"], "bbox": bbox, "limit": 10}).encode()
    req = urllib.request.Request(STAC, data=cuerpo, headers={
        "Content-Type": "application/json", "User-Agent": "structai-piloto/0.1"})
    with urllib.request.urlopen(req, timeout=40) as r:
        hrefs = [f["assets"]["data"]["href"] for f in json.load(r)["features"]]
    # El catalogo entrega s3://bucket/ruta; el bucket es publico y se lee por
    # https sin credenciales de AWS.
    return [("https://" + h[5:].split("/", 1)[0] + ".s3.amazonaws.com/" + h[5:].split("/", 1)[1])
            if h.startswith("s3://") else h for h in hrefs]


def _zona(lat: float, lon: float, radio_km: float):
    dlat = radio_km * 1000 / M_POR_GRADO_LAT
    dlon = dlat / math.cos(math.radians(lat))
    return [lon - dlon, lat - dlat, lon + dlon, lat + dlat]


def estadistica_zonal(lat: float, lon: float, radio_km: float) -> dict | None:
    bbox = _zona(lat, lon, radio_km)
    hrefs = _href_dem(bbox)
    if not hrefs:
        return None
    with rasterio.open(hrefs[0]) as ds:
        ventana = from_bounds(*bbox, transform=ds.transform)
        z = ds.read(1, window=ventana, boundless=True, fill_value=np.nan).astype(float)
        tr = ds.window_transform(ventana)
        nodata = ds.nodata
    if nodata is not None:
        z[z == nodata] = np.nan
    h, w = z.shape
    ys, xs = np.mgrid[0:h, 0:w]
    lons = tr.c + (xs + 0.5) * tr.a
    lats = tr.f + (ys + 0.5) * tr.e
    dist_km = np.hypot((lons - lon) * math.cos(math.radians(lat)), lats - lat) * M_POR_GRADO_LAT / 1000
    dentro = (dist_km <= radio_km) & ~np.isnan(z)
    if dentro.sum() < 100:
        return None
    paso_y = abs(tr.e) * M_POR_GRADO_LAT
    paso_x = tr.a * M_POR_GRADO_LAT * math.cos(math.radians(lat))
    gy, gx = np.gradient(z, paso_y, paso_x)
    pend_pct = np.hypot(gx, gy) * 100.0
    # np.gradient propaga NaN a los vecinos; la mascara 'dentro' ya los excluye.
    ok = dentro & ~np.isnan(pend_pct)
    v, p = z[ok], pend_pct[ok]
    return {
        "n_pixeles": int(ok.sum()),
        "elev_media_m": float(v.mean()), "elev_min_m": float(v.min()), "elev_max_m": float(v.max()),
        "rango_elev_m": float(v.max() - v.min()),
        "pend_media_pct": float(p.mean()), "pend_mediana_pct": float(np.median(p)),
        "pend_p90_pct": float(np.percentile(p, 90)),
        "frac_bajo_10m": float((v < BAJO_NIVEL_M).mean()),
    }


def _clave(s: str) -> str:
    return divipola._clave(s)


def main() -> None:
    depto = sys.argv[1] if len(sys.argv) > 1 else "Atlántico"
    radio = float(sys.argv[2]) if len(sys.argv) > 2 else RADIO_KM_DEFECTO
    filas = []
    for m in _municipios(depto):
        try:
            est = estadistica_zonal(m["latitud"], m["longitud"], radio)
        except Exception as e:  # red/COG: se informa, no se esconde
            print(f"  FALLA {m['municipio']}: {type(e).__name__}: {str(e)[:90]}")
            est = None
        filas.append({"municipio": m["municipio"], "codigo": m["codigo_municipio"],
                      "lat": m["latitud"], "lon": m["longitud"], "radio_km": radio, **(est or {"error": True})})
        if est:
            print(f"{m['municipio']:<22} elev {est['elev_media_m']:7.1f} m  pend media {est['pend_media_pct']:5.2f}%  "
                  f"p90 {est['pend_p90_pct']:5.2f}%  <10m {est['frac_bajo_10m']*100:5.1f}%")
    ok = [f for f in filas if "error" not in f]
    print(f"\n{len(ok)}/{len(filas)} municipios con estadistica valida")

    previo = json.load(open(RAIZ / "scripts/evaluacion/fase2_elevacion_resultados.json", encoding="utf-8"))
    srtm = {_clave(r["municipio"]): r["pendiente_pct"] for g in previo.values() for r in g}
    par = [(f["pend_mediana_pct"], srtm[_clave(f["municipio"])]) for f in ok if _clave(f["municipio"]) in srtm]
    verif = {"n_en_comun": len(par)}
    if len(par) >= 4:
        rho, p = spearmanr([a for a, _ in par], [b for _, b in par])
        verif.update(spearman_rho=float(rho), p=float(p))
    print("Verificacion cruzada vs SRTM de fase2:", verif)

    salida = Path(__file__).with_name(f"dem_{_clave(depto)}.json")
    salida.write_text(json.dumps({"fuente": "Copernicus DEM GLO-30 (AWS Earth Search)", "radio_km": radio,
                                  "verificacion_vs_srtm": verif, "municipios": filas}, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print("Guardado:", salida)


if __name__ == "__main__":
    main()
