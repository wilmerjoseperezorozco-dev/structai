"""Mapas del preregistro de #332 fase 2 y detalle de los conflictos de sensibilidad.

Lee techo_malla.npz (de cruce_pot_techo.py) y dibuja:
1. techo sobre el terreno (m) donde hay alguna superficie, con las zonas del POT de fondo;
2. margen = techo sobre el terreno − altura POT (escenario central, 3,0 m por piso), en las celdas del POT que quedan
   bajo alguna superficie. Se marcan las celdas en conflicto con 3,5 m por piso.

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided
under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus
programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

Uso (entorno geo): python -I scripts/aeronautico/mapas_techo.py <techo_malla.npz> <dir_salida_png> [detalle.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from georef_u16 import A_U16  # noqa: E402
from superficies import pista_skbq  # noqa: E402

REMATE = 1.5
AVISO = "Contiene datos Copernicus WorldDEM-30 © DLR e.V. 2010-2014 y © Airbus DS GmbH 2014-2018 (UE/ESA)."


def main(npz: str, dir_png: str, detalle: str | None = None):
    sys.stdout.reconfigure(encoding="utf-8")
    z = np.load(npz)
    t, dem, pisos, limita = z["techo_estadio"], z["dem"], z["pisos"], z["limita"]
    E0, N1, c = float(z["E0"]), float(z["N1"]), float(z["celda"])
    nfil, ncol = t.shape
    ext = [(E0) / 1e3, (E0 + ncol * c) / 1e3, (N1 - nfil * c) / 1e3, N1 / 1e3]
    libre = np.where(np.isfinite(t), t - dem, np.nan)
    pista, _ = pista_skbq(lambda lo, la: A_U16.transform(lo, la))
    px = [pista.umbral_a[0] / 1e3, pista.umbral_b[0] / 1e3]
    py = [pista.umbral_a[1] / 1e3, pista.umbral_b[1] / 1e3]
    out = Path(dir_png); out.mkdir(parents=True, exist_ok=True)

    fondo = np.where(np.isfinite(pisos), 1.0, np.nan)
    fig, ax = plt.subplots(figsize=(7, 8), dpi=110)
    ax.imshow(fondo, extent=ext, cmap="Greys", vmin=0, vmax=4, interpolation="nearest")
    im = ax.imshow(libre, extent=ext, cmap="viridis", vmin=0, vmax=150, alpha=0.75, interpolation="nearest")
    ax.plot(px, py, "r-", lw=2, label="Pista 05/23")
    fig.colorbar(im, ax=ax, shrink=0.7, label="Techo sobre el terreno (m)")
    ax.set_title("SKBQ: techo aeronáutico (RAC 14) sobre el terreno\nGris: zonas con pisos en el U-16", fontsize=10)
    ax.set_xlabel("Este U-16 (km)"); ax.set_ylabel("Norte U-16 (km)"); ax.legend(loc="lower right", fontsize=8)
    fig.text(0.01, 0.005, AVISO + " Orienta y no autoriza.", fontsize=6)
    fig.savefig(out / "techo_sobre_terreno.png", bbox_inches="tight"); plt.close(fig)

    h_pot = pisos * 3.0 + REMATE
    margen = np.where(np.isfinite(pisos) & np.isfinite(libre), libre - h_pot, np.nan)
    conf_alto = np.isfinite(pisos) & np.isfinite(libre) & (pisos * 3.5 + REMATE > libre)
    fig, ax = plt.subplots(figsize=(7, 8), dpi=110)
    ax.imshow(fondo, extent=ext, cmap="Greys", vmin=0, vmax=4, interpolation="nearest")
    im = ax.imshow(margen, extent=ext, cmap="RdYlGn", vmin=-10, vmax=60, interpolation="nearest")
    ff, cc = np.nonzero(conf_alto)
    ax.scatter((E0 + (cc + 0.5) * c) / 1e3, (N1 - (ff + 0.5) * c) / 1e3, s=6, c="k", marker="x",
               label="Conflicto con 3,5 m por piso")
    ax.plot(px, py, "r-", lw=2, label="Pista 05/23")
    fig.colorbar(im, ax=ax, shrink=0.7, label="Margen con 3,0 m por piso (m)")
    ax.set_title("Margen entre el techo aeronáutico y la altura del POT\n(solo celdas del U-16 bajo alguna superficie)",
                 fontsize=10)
    ax.set_xlabel("Este U-16 (km)"); ax.set_ylabel("Norte U-16 (km)"); ax.legend(loc="lower right", fontsize=8)
    fig.text(0.01, 0.005, AVISO + " Orienta y no autoriza.", fontsize=6)
    fig.savefig(out / "margen_pot.png", bbox_inches="tight"); plt.close(fig)

    # Detalle de las celdas en conflicto con 3,5 m por piso y de los márgenes más pequeños
    centro = (np.array(pista.umbral_a) + np.array(pista.umbral_b)) / 2
    det = []
    for f_, c_ in zip(ff, cc):
        E, N = E0 + (c_ + 0.5) * c, N1 - (f_ + 0.5) * c
        det.append({"pisos": int(pisos[f_, c_]), "superficie": str(limita[f_, c_]),
                    "techo_m": round(float(t[f_, c_]), 1), "dem_m": round(float(dem[f_, c_]), 1),
                    "libre_m": round(float(libre[f_, c_]), 1),
                    "dist_centro_pista_km": round(float(np.hypot(E - centro[0], N - centro[1]) / 1e3), 2)})
    m = margen[np.isfinite(margen)]
    info = {"celdas_conflicto_3_5": det,
            "margen_central_percentiles_m": {p: round(float(np.percentile(m, p)), 1) for p in (0, 1, 5, 50)},
            "celdas_margen_central_menor_5m": int((m < 5).sum()),
            "celdas_margen_central_menor_10m": int((m < 10).sum())}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if detalle:
        Path(detalle).write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
