"""Busqueda OpenAlex del protocolo PROTOCOLO_LITERATURA_CAUDALES.md (consultas fijadas antes de buscar)."""
import json, time, urllib.parse, urllib.request
from pathlib import Path
CONSULTAS = [
 "regional flood frequency analysis Colombia",
 "regionalization peak discharge Andes catchment area",
 "regional flood estimation tropical catchments ungauged regression drainage area",
 "ecuaciones regionales caudal máximo Colombia",
 "regionalización de caudales máximos cuencas Latinoamérica",
 "flood quantile regression ungauged basins South America"]
def resumen(inv):
    if not inv: return ""
    p = {}
    for w, pos in inv.items():
        for i in pos: p[i] = w
    return " ".join(p[i] for i in sorted(p))[:1500]
out = {}
for q in CONSULTAS:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": q, "filter": "from_publication_date:1990-01-01", "per-page": 25})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "structai-research"}), timeout=60) as r:
        d = json.load(r)
    for w in d["results"]:
        k = w["id"]
        e = out.setdefault(k, {"id": k, "doi": w.get("doi"), "titulo": w.get("title"), "anio": w.get("publication_year"),
            "oa": (w.get("open_access") or {}).get("is_oa"), "oa_url": (w.get("open_access") or {}).get("oa_url"), "resumen": resumen(w.get("abstract_inverted_index")), "consultas": []})
        e["consultas"].append(q)
    time.sleep(1)
lst = sorted(out.values(), key=lambda x: -(x["anio"] or 0))
Path(__file__).with_name("literatura_caudales_busqueda.json").write_text(json.dumps(lst, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(lst), "trabajos unicos;", sum(1 for x in lst if x["oa"]), "con acceso abierto")
