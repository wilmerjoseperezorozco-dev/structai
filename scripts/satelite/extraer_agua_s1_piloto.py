"""Piloto satelital, paso 2 (issue #95, Frente C): frecuencia de agua superficial
con Sentinel-1 RTC (radar, atraviesa nubes) por municipio del Atlantico.

Solo EXTRAE y VERIFICA. No entrena ni predice nada.

Metodo (declarado):
- Fuente: Microsoft Planetary Computer, coleccion sentinel-1-rtc (gamma0 lineal,
  10 m, terreno corregido). URL firmada con token anonimo gratuito.
- UNA sola orbita relativa (misma geometria en todas las fechas) para que la
  variacion en el tiempo no sea un artefacto del angulo de vista.
- Agua = retrodispersion VV (dB) < umbral. Umbral principal -18 dB; se reportan
  -16 y -20 como sensibilidad. El umbral es una eleccion, no una verdad.
- Frecuencia por pixel = fraccion de escenas en que ese pixel es agua.
  permanente >= 80 % de las escenas; ocasional >= 10 % y < 80 %.
- Poligonos municipales IGAC (servicio ANH). El propio servicio advierte que no
  son apropiados para ubicacion exacta ni calculo de areas/distancias: sirven
  para estadistica zonal a escala municipal, no para predios.
- Resolucion reducida (~DECIMACION x 10 m) para costo razonable.

Limitaciones conocidas del radar para agua: superficies lisas secas (asfalto,
arena) y sombras de relieve dan falsos positivos; el viento rugoso sobre el agua
da falsos negativos. Se mitiga con frecuencia temporal, no se elimina.

Uso: python scripts/satelite/extraer_agua_s1_piloto.py [orbita_relativa] [max_escenas, defecto 200]
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.warp import transform_bounds, transform_geom
from rasterio.windows import from_bounds

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel1euwestrtc/sentinel1-grd-rtc"
PERIODO = "2025-11-01T00:00:00Z/2026-11-01T00:00:00Z"
DECIMACION = 4
UMBRALES_DB = (-16.0, -18.0, -20.0)
UMBRAL_PRINCIPAL = -18.0
FREC_PERMANENTE, FREC_OCASIONAL = 0.80, 0.10
UA = {"User-Agent": "structai-piloto/0.1", "Content-Type": "application/json"}


def _json(url: str, cuerpo: dict | None = None) -> dict:
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo else None, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def escenas(orbita: int, maximo: int, bbox: list[float]) -> list[dict]:
    d = _json(STAC, {"collections": ["sentinel-1-rtc"], "bbox": bbox, "datetime": PERIODO, "limit": 200,
                     "query": {"sat:relative_orbit": {"eq": orbita}}})
    fs = [f for f in d["features"]
          if f["bbox"][0] < bbox[0] and f["bbox"][2] > bbox[2] and f["bbox"][1] < bbox[1] and f["bbox"][3] > bbox[3]]
    fs.sort(key=lambda f: f["properties"]["datetime"])
    return fs[:maximo]


def main() -> None:
    orbita = int(sys.argv[1]) if len(sys.argv) > 1 else 142
    maximo = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    gj = json.load(open(AQUI / "poligonos_atlantico_igac.geojson", encoding="utf-8"))
    pts = [p for f in gj["features"] for ring in f["geometry"]["coordinates"] for p in ring]
    bbox = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
    fs = escenas(orbita, maximo, bbox)
    if not fs:
        raise SystemExit("Sin escenas que cubran el departamento para esa orbita")
    print(f"Orbita {orbita}: {len(fs)} escenas ({fs[0]['properties']['datetime'][:10]} a {fs[-1]['properties']['datetime'][:10]})")

    token = _json(TOKEN)["token"]
    masks: dict[str, np.ndarray] = {}
    stack: list[np.ndarray] = []
    fechas: list[str] = []
    ref = None
    for i, f in enumerate(fs, 1):
        try:
            with rasterio.open(f["assets"]["vv"]["href"] + "?" + token) as ds:
                b = transform_bounds("EPSG:4326", ds.crs, *bbox)
                w = from_bounds(*b, transform=ds.transform)
                if ref is None:
                    ref = (int(w.height) // DECIMACION, int(w.width) // DECIMACION)
                    tr = rasterio.windows.transform(w, ds.transform) * rasterio.Affine.scale(
                        w.width / ref[1], w.height / ref[0])
                    for g in gj["features"]:
                        geom = transform_geom("EPSG:4326", ds.crs, g["geometry"])
                        masks[g["properties"]["CODIGO"]] = features.geometry_mask(
                            [geom], out_shape=ref, transform=tr, invert=True)
                vv = ds.read(1, window=w, out_shape=ref, boundless=True, fill_value=np.nan,
                             resampling=rasterio.enums.Resampling.average).astype("float32")
        except Exception as e:
            print(f"  escena {i} omitida: {type(e).__name__}: {str(e)[:80]}")
            continue
        stack.append((10 * np.log10(np.where(vv > 0, vv, np.nan))).astype("float16"))
        fechas.append(f["properties"]["datetime"][:10])
        print(f"  [{i}/{len(fs)}] {fechas[-1]} ok")

    cubo = np.stack(stack)  # (t, y, x) en dB
    valido = ~np.isnan(cubo)
    nval_pix = valido.sum(0)
    out = []
    for g in gj["features"]:
        cod = g["properties"]["CODIGO"]
        m = masks[cod]
        fila = {"codigo": cod, "municipio": g["properties"]["NOMBRE_ENT"], "area_ha_igac": g["properties"]["AREA_HA"],
                "n_escenas": len(stack), "n_pixeles": int(m.sum())}
        nval_t = valido[:, m].sum(axis=1)
        for u in UMBRALES_DB:
            agua = (cubo < u) & valido
            serie = agua[:, m].sum(axis=1) / np.maximum(nval_t, 1)
            frec = (agua.sum(0) / np.maximum(nval_pix, 1))[m & (nval_pix > 0)]
            sfx = f"{int(-u)}"
            fila.update({
                f"agua_mediana_{sfx}": float(np.median(serie)), f"agua_max_{sfx}": float(serie.max()),
                f"agua_rango_{sfx}": float(serie.max() - serie.min()),
                f"frac_permanente_{sfx}": float((frec >= FREC_PERMANENTE).mean()),
                f"frac_ocasional_{sfx}": float(((frec >= FREC_OCASIONAL) & (frec < FREC_PERMANENTE)).mean()),
            })
        out.append(fila)
    sfx = f"{int(-UMBRAL_PRINCIPAL)}"
    print(f"\n{'municipio':<20}{'perm%':>7}{'ocas%':>7}{'max%':>7}   (umbral {UMBRAL_PRINCIPAL:.0f} dB)")
    for r in sorted(out, key=lambda r: -r[f"frac_ocasional_{sfx}"]):
        print(f"{r['municipio']:<20}{r[f'frac_permanente_{sfx}']*100:7.1f}{r[f'frac_ocasional_{sfx}']*100:7.1f}{r[f'agua_max_{sfx}']*100:7.1f}")
    (AQUI / "agua_s1_ATLANTICO.json").write_text(json.dumps({
        "fuente": "Sentinel-1 RTC (Planetary Computer)", "orbita_relativa": orbita, "fechas": fechas,
        "umbral_principal_db": UMBRAL_PRINCIPAL, "decimacion": DECIMACION, "municipios": out},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("Guardado agua_s1_ATLANTICO.json")


if __name__ == "__main__":
    main()
