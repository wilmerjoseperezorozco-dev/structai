"""Precipitacion mensual CHIRPS v3.0 (0.05 grados, ~5 km) por municipio del Caribe, 2019-2024
(issue #95/#98). Sin cuenta: HTTP abierto del Climate Hazards Center (UCSB).

Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/tifs/chirps-v3.0.YYYY.MM.tif
Cita: Funk et al., CHIRPS (ver README-CHIRPSv3.0.txt en el mismo directorio; confirmar terminos de uso alli).
Lectura por ventana (el archivo esta organizado por filas): no se descargan los ~24 MB globales.

Detalles declarados:
- El archivo no declara nodata: se usa -9999 (verificado en la ventana: media -3549 sin mascara).
- Valor municipal = media de los pixeles que tocan el poligono (all_touched); si ninguno cae dentro
  (municipios muy pequenos frente a 5 km) se toma el pixel del centroide. Resolucion 5 km: municipios
  de < ~100 km2 quedan representados por 1-3 pixeles, es una limitacion real.
- Solo extrae; no asocia nada.

Salida: scripts/satelite/chirps_mensual_caribe.json
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.windows import from_bounds

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

BASE = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/tifs/chirps-v3.0.{a}.{m:02d}.tif"
BBOX = (-77.6, 7.7, -70.9, 12.7)
ANIOS = range(2019, 2025)
NODATA = -9999.0


def main() -> None:
    pols = dc.poligonos()
    cod = [c for c in pols]
    meses = [(a, m) for a in ANIOS for m in range(1, 13)]
    serie = {c: [] for c in cod}
    pix = {}
    t0 = time.time()
    with rasterio.Env(GDAL_HTTP_TIMEOUT=60, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=2,
                      GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        for k, (a, m) in enumerate(meses):
            with rasterio.open(BASE.format(a=a, m=m)) as ds:
                w = from_bounds(*BBOX, transform=ds.transform).round_offsets().round_lengths()
                z = ds.read(1, window=w).astype("float64")
                tr = ds.window_transform(w)
            z[z <= NODATA + 1] = np.nan
            if not pix:
                for c in cod:
                    mk = features.geometry_mask([pols[c]["geom"].buffer(0).__geo_interface__], out_shape=z.shape, transform=tr,
                                                invert=True, all_touched=True)
                    if not mk.any():
                        x, y = pols[c]["centroide"]
                        r, cc = ~tr * (x, y)
                        mk = np.zeros(z.shape, bool)
                        mk[int(r), int(cc)] = True
                    pix[c] = mk
            for c in cod:
                v = z[pix[c]]
                serie[c].append(float(np.nanmean(v)) if np.isfinite(v).any() else None)
            if k % 12 == 11:
                print(f"  {a}: listo ({time.time() - t0:.0f}s)", flush=True)
    faltan = sum(1 for c in cod for v in serie[c] if v is None)
    out = {"fuente": "CHIRPS v3.0 mensual (mm/mes), 0.05 grados", "meses": [f"{a}-{m:02d}" for a, m in meses],
           "municipios": {c: {"nombre": pols[c]["nombre"], "depto": c[:2], "precip_mm": serie[c], "n_pixeles": int(pix[c].sum())} for c in cod}}
    (AQUI / "chirps_mensual_caribe.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    arr = np.array([[v if v is not None else np.nan for v in serie[c]] for c in cod])
    print(f"\n{len(cod)} municipios x {len(meses)} meses; valores faltantes: {faltan}")
    print(f"Precipitacion anual media regional (mm): " + ", ".join(
        f"{a}: {np.nanmean(arr[:, i * 12:(i + 1) * 12].sum(1)):.0f}" for i, a in enumerate(ANIOS)))
    print(f"Pixeles por municipio: mediana {np.median([pix[c].sum() for c in cod]):.0f}, minimo {min(pix[c].sum() for c in cod)}")


if __name__ == "__main__":
    main()
