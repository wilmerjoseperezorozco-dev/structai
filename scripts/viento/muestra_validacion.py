"""#320: muestra estratificada para la validación ciega de v_municipio.csv (prerregistro en docs/viento/).

Estratos: V asignada (17/22/28/33/36) × frontera (sí/no), hasta N_ESTRATO municipios por estrato, semilla fija. La hoja
sale en orden aleatorio y SIN la V asignada. La clave queda en data/viento/v_municipio.csv, que el validador no abre.
Uso: python -I scripts/viento/muestra_validacion.py
"""
import csv
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA, N_ESTRATO = 3200, 6

filas = list(csv.DictReader((RAIZ / "data/viento/v_municipio.csv").open(encoding="utf-8")))
rng = random.Random(SEMILLA)
muestra = []
for v in ("17.0", "22.0", "28.0", "33.0", "36.0"):
    for fr in ("False", "True"):
        e = [r for r in filas if r["v_asignada"] == v and r["frontera"] == fr and r["lat"]]
        muestra += rng.sample(e, min(N_ESTRATO, len(e)))
rng.shuffle(muestra)
ids = [r["divipola"] for r in muestra]
(RAIZ / "data/viento/muestra_validacion_320.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
lin = ["# Hoja de validación ciega #320: región de viento por municipio", "",
       "Para cada municipio, ubique la **cabecera** (latitud y longitud) en la Fig. B.6.4-1 de la NSR-10 (pág. B-39) y",
       "anote el número de región (1 a 5) o **N** si cae en la zona de la nota. Si queda sobre una línea o duda, anote",
       "las dos regiones (p. ej. 3/4). **No abra `data/viento/v_municipio.csv` ni el GeoJSON** antes de terminar.", "",
       "| # | DIVIPOLA | Municipio | Departamento | Latitud | Longitud | Región leída |", "|---|---|---|---|---|---|---|"]
for k, r in enumerate(muestra, 1):
    lin.append(f"| {k} | {r['divipola']} | {r['municipio'].title()} | {r['departamento'].title()} | {float(r['lat']):.2f} | "
               f"{float(r['lon']):.2f} |   |")
(RAIZ / "docs/viento/HOJA_VALIDACION_320.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
print(len(muestra), "municipios en la hoja")
