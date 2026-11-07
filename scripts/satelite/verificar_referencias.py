"""Verifica en OpenAlex cada referencia candidata (por titulo) y guarda el registro real encontrado.
Una referencia solo entra a la bibliografia si el titulo devuelto coincide con el buscado.
Uso: python verificar_referencias.py salida.json"""
from __future__ import annotations

import difflib
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
API = "https://api.openalex.org/works"

# (bloque, titulo buscado, apellido del primer autor esperado)
CANDIDATAS = [
    ("umbrales", "The rainfall intensity-duration control of shallow landslides and debris flows", "Caine"),
    ("umbrales", "The rainfall intensity-duration control of shallow landslides and debris flows: an update", "Guzzetti"),
    ("umbrales", "A review of the recent literature on rainfall thresholds for landslide occurrence", "Segoni"),
    ("umbrales", "Rainfall thresholds for possible landslide occurrence in Italy", "Peruccacci"),
    ("umbrales", "Satellite-based assessment of rainfall-triggered landslide hazard for situational awareness", "Kirschbaum"),
    ("umbrales", "A global landslide catalog for hazard applications: method, results, and limitations", "Kirschbaum"),
    ("umbrales", "Satellite rainfall products outperform ground observations for landslide prediction in India", "Brunetti"),
    ("umbrales", "Global fatal landslide occurrence from 2004 to 2016", "Froude"),
    ("susceptibilidad", "A review of statistically-based landslide susceptibility models", "Reichenbach"),
    ("susceptibilidad", "Spatial prediction models for landslide hazards: review, comparison and evaluation", "Brenning"),
    ("susceptibilidad", "Statistical landslide hazard analysis", "van Westen"),
    ("susceptibilidad", "Weights of evidence modelling: a new approach to mapping mineral potential", "Bonham-Carter"),
    ("susceptibilidad", "Assessing the quality of landslide susceptibility maps - case study Lower Austria", "Petschko"),
    ("susceptibilidad", "Recommendations for the quantitative analysis of landslide risk", "Corominas"),
    ("susceptibilidad", "Selecting pseudo-absences for species distribution models: how, where and how many?", "Barbet-Massin"),
    ("susceptibilidad", "AUC: a misleading measure of the performance of predictive distribution models", "Lobo"),
    ("susceptibilidad", "Assessing the accuracy of species distribution models: prevalence, kappa and the true skill statistic (TSS)", "Allouche"),
    ("susceptibilidad", "The new global lithological map database GLiM", "Hartmann"),
    ("magnitud", "Landslide inventories and their statistical properties", "Malamud"),
    ("magnitud", "Power-law distributions in empirical data", "Clauset"),
    ("magnitud", "Probabilistic landslide hazard assessment at the basin scale", "Guzzetti"),
    ("crecientes", "Guidelines for determining flood flow frequency Bulletin 17C", "England"),
    ("crecientes", "L-moments: analysis and estimation of distributions using linear combinations of order statistics", "Hosking"),
    ("crecientes", "Statistics of extremes in hydrology", "Katz"),
    ("crecientes", "Stationarity is dead: whither water management?", "Milly"),
    ("crecientes", "Regional frequency analysis: an approach based on L-moments", "Hosking"),
    ("crecientes", "An introduction to statistical modeling of extreme values", "Coles"),
    ("crecientes", "Hydrological regionalization flood frequency Colombia", "Poveda"),
    ("idf", "Generalized rainfall-duration-frequency relationships", "Bell"),
    ("idf", "Intensity-duration-frequency curves sub-daily rainfall scaling from daily data", "Gupta"),
    ("clima", "Seasonality in ENSO-related precipitation, river discharges, soil moisture, and vegetation index in Colombia", "Poveda"),
    ("clima", "Hydro-climatic variability over the Andes of Colombia associated with ENSO: a review of climatic processes and their impact", "Poveda"),
    ("clima", "Feedbacks between hydrological processes in tropical South America and large-scale ocean-atmospheric phenomena", "Poveda"),
    ("clima", "The climate hazards infrared precipitation with stations - a new environmental record for monitoring extremes", "Funk"),
    ("clima", "Global-scale evaluation of 22 precipitation datasets using gauge observations and hydrological modeling", "Beck"),
    ("clima", "Validation of the CHIRPS satellite rainfall estimates over eastern Africa", "Dinku"),
    ("clima", "Seasonality of rainfall in Colombia", "Urrea"),
    ("hand", "Height Above the Nearest Drainage - a hydrologically relevant new terrain model", "Nobre"),
    ("hand", "HAND, a new terrain descriptor using SRTM-DEM: mapping terra-firme rainforest environments in Amazonia", "Renno"),
    ("hand", "Terrain analysis enhancements to the Height Above Nearest Drainage flood inundation mapping method", "Garousi-Nejad"),
    ("estadistica", "Ecological correlations and the behavior of individuals", "Robinson"),
    ("estadistica", "The stippling shows statistically significant grid points: how research results are routinely overstated and overinterpreted", "Wilks"),
    ("estadistica", "Controlling the false discovery rate: a practical and powerful approach to multiple testing", "Benjamini"),
    ("estadistica", "The jackknife and the bootstrap for general stationary observations", "Kunsch"),
    ("estadistica", "Modifying the t test for assessing the correlation between two spatial processes", "Dutilleul"),
    ("estadistica", "Spatial cross-validation and bootstrap for the assessment of prediction rules in remote sensing: the R package sperrorest", "Brenning"),
]


def norm(s: str) -> str:
    return "".join(c for c in (s or "").lower() if c.isalnum() or c == " ")


def consultar(titulo: str) -> list[dict]:
    url = f"{API}?{urllib.parse.urlencode({'filter': 'title.search:' + titulo[:140].replace(',', ' ').replace(':', ' '), 'per-page': 4})}"
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "structai-research/0.1 (mailto:investigacion@structai.local)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)["results"]
        except Exception as e:
            time.sleep(3 * (i + 1))
    return []


def main() -> None:
    out = []
    for bloque, titulo, autor in CANDIDATAS:
        mejor = None
        for w in consultar(titulo):
            sim = difflib.SequenceMatcher(None, norm(titulo), norm(w.get("title") or "")).ratio()
            if mejor is None or sim > mejor[0]:
                mejor = (sim, w)
        if mejor and mejor[0] >= 0.75:
            w = mejor[1]
            aut = [a["author"]["display_name"] for a in (w.get("authorships") or [])]
            ok_autor = any(autor.lower() in norm(x) for x in aut[:3])
            loc = (w.get("primary_location") or {}).get("source") or {}
            reg = {"bloque": bloque, "buscado": titulo, "similitud": round(mejor[0], 2), "titulo": w.get("title"), "anio": w.get("publication_year"),
                   "autores": aut[:6], "revista": loc.get("display_name"), "doi": w.get("doi"), "citas": w.get("cited_by_count"), "autor_coincide": ok_autor}
            out.append(reg)
            print(f"OK  [{bloque}] {w.get('publication_year')} {', '.join(aut[:2])} — {w.get('title')[:80]} | {loc.get('display_name')} | {w.get('doi')} | autor_ok={ok_autor} sim={mejor[0]:.2f}")
        else:
            out.append({"bloque": bloque, "buscado": titulo, "no_encontrada": True})
            print(f"NO  [{bloque}] {titulo[:90]} (mejor similitud {mejor[0]:.2f})" if mejor else f"NO  [{bloque}] {titulo[:90]} (sin resultados)")
        time.sleep(0.4)
    Path(sys.argv[1]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
