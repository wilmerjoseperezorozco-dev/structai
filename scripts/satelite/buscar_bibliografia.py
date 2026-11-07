"""Busqueda bibliografica verificable en OpenAlex (API abierta, sin clave). Devuelve registros reales
(titulo, autores, anio, revista, DOI, citas), ordenados por citas dentro de cada consulta.
Uso: python buscar_bibliografia.py [salida.json]   (las consultas estan en CONSULTAS)"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
API = "https://api.openalex.org/works"

CONSULTAS = {
    "umbrales_lluvia_deslizamientos": "rainfall intensity duration thresholds landslide initiation",
    "umbrales_lluvia_revision": "rainfall thresholds for landslide early warning systems review",
    "umbrales_colombia": "rainfall threshold landslides Colombia",
    "pesos_evidencia": "weights of evidence landslide susceptibility mapping",
    "validacion_espacial": "spatial cross-validation overoptimistic performance landslide susceptibility",
    "sesgo_inventarios": "landslide inventory bias completeness susceptibility modelling",
    "area_frecuencia": "landslide area frequency distribution inventories power law",
    "cola_potencia": "power-law distributions in empirical data",
    "frecuencia_crecientes": "flood frequency analysis generalized extreme value annual maxima",
    "regionalizacion": "regional frequency analysis L-moments",
    "no_estacionariedad": "stationarity is dead: whither water management",
    "enso_colombia": "El Nino La Nina Colombia rainfall streamflow",
    "chirps": "climate hazards group infrared precipitation with stations CHIRPS",
    "chirps_colombia": "CHIRPS evaluation Colombia precipitation",
    "hand": "height above the nearest drainage terrain model hydrologically relevant",
    "hand_inundacion": "HAND flood inundation mapping validation national scale",
    "idf_desagregacion": "intensity duration frequency curves daily rainfall sub-daily scaling",
    "imerg_colombia": "IMERG satellite precipitation evaluation Colombia",
    "falacia_ecologica": "ecological fallacy aggregation spatial data modifiable areal unit problem",
    "multiples_pruebas": "multiple testing field significance climate statistics",
    "bootstrap_bloques": "block bootstrap dependent data time series",
}


def buscar(q: str, n: int = 6, desde: int | None = None) -> list[dict]:
    params = {"search": q, "per-page": n, "sort": "cited_by_count:desc"}
    if desde:
        params["filter"] = f"from_publication_date:{desde}-01-01"
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "structai-research/0.1 (mailto:investigacion@structai.local)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.load(r)["results"]
            break
        except Exception as e:
            print(f"   reintento {i + 1}: {str(e)[:60]}", flush=True)
            time.sleep(3 * (i + 1))
    else:
        return []
    out = []
    for w in res:
        autores = [a["author"]["display_name"] for a in (w.get("authorships") or [])][:4]
        loc = (w.get("primary_location") or {}).get("source") or {}
        out.append({"titulo": w.get("title"), "anio": w.get("publication_year"), "autores": autores, "revista": loc.get("display_name"),
                    "doi": w.get("doi"), "citas": w.get("cited_by_count"), "tipo": w.get("type")})
    return out


def main() -> None:
    todo = {}
    for clave, q in CONSULTAS.items():
        todo[clave] = buscar(q)
        print(f"\n== {clave} ({q})")
        for r in todo[clave]:
            print(f"  [{r['anio']}] {', '.join(r['autores'][:3])}{' et al.' if len(r['autores']) > 3 else ''} — {r['titulo'][:95] if r['titulo'] else ''} | {r['revista']} | citas {r['citas']} | {r['doi']}")
        time.sleep(0.5)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
