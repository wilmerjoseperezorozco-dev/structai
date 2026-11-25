"""#320 v1: asigna la velocidad básica de viento V (Fig. B.6.4-1) a cada municipio por DIVIPOLA.

Entrada:
  - data/viento/regiones_b641.geojson (digitalizar_fig_b641.py);
  - DIVIPOLA del DANE (datos.gov.co, recurso gdxc-w37w, el mismo que usa packages/construdata/divipola.py), con la
    coordenada de la cabecera municipal.
Regla (v1, por cabecera; el polígono municipal del MGN sería una v2):
  - v_cabecera: V de la cara que contiene la cabecera (si cae fuera del contorno, por ejemplo en la costa, la cara más
    cercana);
  - v_asignada = V máxima dentro de R_ASIGNA grados de la cabecera (conservador frente al error de digitalización y a
    que el municipio no es un punto);
  - frontera = hay otra V dentro de R_FRONTERA grados, o la cara es ambigua o astilla → "verificar en la figura";
  - San Andrés y Providencia (departamento 88): región 5, 36 m/s (recuadro de la figura).
Salida: data/viento/v_municipio.csv. Solo códigos, nombres oficiales y la coordenada pública de la cabecera del DANE.

Uso: python -I scripts/viento/asignar_municipios.py   (entorno con shapely)
"""
from __future__ import annotations

import csv
import json
import sys
import urllib.request
from pathlib import Path

from shapely.geometry import Point, shape

RAIZ = Path(__file__).resolve().parents[2]
URL = "https://www.datos.gov.co/resource/gdxc-w37w.json?$limit=1200"
R_ASIGNA = 0.10        # grados (~11 km)
R_FRONTERA = 0.15      # grados (~17 km)
V_SAN_ANDRES = 36.0


def _num(s) -> float:
    return float(str(s).replace(",", "."))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    geo = json.loads((RAIZ / "data/viento/regiones_b641.geojson").read_text(encoding="utf-8"))
    caras = [(shape(f["geometry"]), f["properties"]) for f in geo["features"]]
    req = urllib.request.Request(URL, headers={"User-Agent": "structai-viento/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        filas = json.load(r)
    print(f"{len(filas)} municipios DIVIPOLA")
    out = []
    for f in filas:
        cod, dep = f["cod_mpio"], f["cod_dpto"]
        base = {"divipola": cod, "municipio": f["nom_mpio"], "departamento": f["dpto"]}
        if dep == "88":
            out.append(base | {"lon": "", "lat": "", "v_cabecera": V_SAN_ANDRES, "v_asignada": V_SAN_ANDRES,
                               "v_en_radio_frontera": str(V_SAN_ANDRES), "frontera": False,
                               "estado": "recuadro San Andrés y Providencia (región 5)"})
            continue
        p = Point(_num(f["longitud"]), _num(f["latitud"]))
        dentro = [(c, pr) for c, pr in caras if c.contains(p)]
        c0, pr0 = dentro[0] if dentro else min(caras, key=lambda cp: cp[0].distance(p))
        cerca = sorted({pr["v_m_s"] for c, pr in caras if c.distance(p) <= R_ASIGNA})
        radio = sorted({pr["v_m_s"] for c, pr in caras if c.distance(p) <= R_FRONTERA})
        frontera = len(radio) > 1 or not pr0["estado"].startswith("rotulo") and not pr0["estado"].startswith("sin rótulo")
        estado = pr0["estado"] + ("" if dentro else f"; cabecera fuera del contorno a {c0.distance(p):.3f}°")
        out.append(base | {"lon": round(p.x, 4), "lat": round(p.y, 4), "v_cabecera": pr0["v_m_s"],
                           "v_asignada": max(cerca + [pr0["v_m_s"]]), "v_en_radio_frontera": "/".join(f"{v:g}" for v in radio),
                           "frontera": frontera, "estado": estado})
    out.sort(key=lambda r: r["divipola"])
    ruta = RAIZ / "data/viento/v_municipio.csv"
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    import collections
    print("v_asignada:", dict(sorted(collections.Counter(r["v_asignada"] for r in out).items())))
    print("frontera:", sum(r["frontera"] for r in out), "| sube por radio:", sum(r["v_asignada"] > r["v_cabecera"] for r in out),
          "| fuera del contorno:", sum("fuera" in str(r["estado"]) for r in out))


if __name__ == "__main__":
    main()
