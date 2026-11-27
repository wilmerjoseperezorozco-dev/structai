"""Exporta el índice hídrico de H3 (#273) por municipio para la ficha de /sitio.

Misma receta validada en H3 (§27), con el historial actualizado a 2019-2024 para el uso en producto:
  H = log(1 + puentes vehiculares averiados por eventos hídricos 2019-2024)
  T = Q10/Q2 de la estación IDEAM más cercana (≤ 50 km; sin estación → rango neutro)
  S = pendiente p90 del DEM municipal
  índice = media de rangos percentiles. Validación (versión 2019-2022 → 2023-2024): AUC 0,75 [0,70; 0,81].
Salida: packages/construdata/data/indice_hidrico_h3.json (sin datos personales; agregados municipales).
Uso: python -I h3_exportar_indice.py   (entorno con pandas; insumos de h3_descargar_insumos.py)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h3_socavacion_puentes as h3  # noqa: E402

SALIDA = AQUI.parents[1] / "packages" / "construdata" / "data" / "indice_hidrico_h3.json"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    h3.ANIOS_PREDICTOR = (2019, 2024)
    p, meta, ung = h3.preparar(h3.insumos())
    hid = ung[ung["ev"].isin(h3.HIDRICOS) & ung["anio"].between(2019, 2024)]
    pte = hid.groupby("codigo_municipio")["puentes_vehiculares"].sum()
    pct = (rankdata(p["indice"].values) - 0.5) / len(p)
    out = {
        "version": "h3-v1-2019-2024",
        "metodo": "media de rangos percentiles de historial de puentes averiados por eventos hídricos (UNGRD 2019-2024), "
                  "torrencialidad Q10/Q2 de la estación IDEAM más cercana (≤ 50 km) y pendiente p90 del DEM",
        "validacion": "H3 prerregistrada (#273, PROTOCOLO_ANALISIS.md §27): versión 2019-2022 predijo puentes averiados "
                      "en 2023-2024 con AUC 0,75 [0,70; 0,81]; no se demostró que T y S agreguen al historial",
        "cobertura": f"{len(p)} municipios de {p['depto2'].nunique()} departamentos",
        "municipios": {c: {"indice": round(float(i), 4), "percentil": round(float(q), 3),
                           "puentes_hidricos_2019_2024": int(pte.get(c, 0)),
                           "torrencialidad_q10_q2": (None if np.isnan(t) else round(float(t), 3)),
                           "km_estacion_ideam": round(float(k), 1), "pendiente_p90_pct": round(float(s), 1)}
                       for c, i, q, t, k, s in zip(p["codigo"], p["indice"], pct, p["T"], p["km_estacion"], p["S"])},
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(SALIDA, len(out["municipios"]), f"{SALIDA.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
