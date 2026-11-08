"""Consistencia: mapa municipal de intensidad maxima observada (SGC) vs maximo de sus puntos. Protocolo: PROTOCOLO_SISMICIDAD_HISTORICA.md"""
import glob, json
from pathlib import Path
import numpy as np, requests
from scipy.stats import spearmanr
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
SAT = AQUI.parents[1] / "satelite"
H = "https://srvags.sgc.gov.co/arcgis/rest/services/sismicidad_historica_2/mapa_de_intensidades/MapServer/"
OBS = "https://srvags.sgc.gov.co/arcgis/rest/services/Mapa_Intensidad_Maxima_Observada_Colombia/Intensidad_Observada_Departamento_Municipio/MapServer/1/query"


def consultar(url, campos, paginar=False):
    filas, ini = [], 0
    while True:
        p = {"where": "1=1", "outFields": campos, "returnGeometry": "false", "f": "json"}
        if paginar:
            p.update({"resultOffset": ini, "resultRecordCount": 1000})
        d = requests.get(url, params=p, timeout=90).json()
        lote = [f["attributes"] for f in d.get("features", [])]
        filas += lote
        if not paginar or not d.get("exceededTransferLimit"):
            return filas
        ini += 1000


def main():
    pols, cods = [], []
    for f in glob.glob(str(SAT / "_cache" / "poligonos_nac_*.geojson")):
        for ft in json.loads(Path(f).read_text(encoding="utf-8"))["features"]:
            pols.append(shape(ft["geometry"])); cods.append(ft["properties"]["CODIGO"])
    arbol = STRtree(pols)
    mapa = {str(r["CODIGO_DANE"]).zfill(5): r["GRIDCODE"] for r in consultar(OBS, "CODIGO_DANE,GRIDCODE,CATEGORIA", True) if r["CATEGORIA"] == "M" and r["GRIDCODE"] is not None}
    capas = {"max": H + "2/query", "todas": H + "1/query"}
    pts = {k: consultar(u, "VALOR_INTENSIDAD,LATITUD,LONGITUD,ESCALA") for k, u in capas.items()}
    R = {"municipios_mapa_M": len(mapa)}
    escalas = {}
    for k, filas in pts.items():
        escalas[k] = {str(e): sum(1 for r in filas if r["ESCALA"] == e) for e in {r["ESCALA"] for r in filas}}
    R["escalas"] = escalas
    def maximos(filas):
        m = {}
        for r in filas:
            if r["VALOR_INTENSIDAD"] is None or r["LATITUD"] is None:
                continue
            for i in arbol.query(Point(r["LONGITUD"], r["LATITUD"]), predicate="within"):
                c = cods[i]; m[c] = max(m.get(c, -1), r["VALOR_INTENSIDAD"]); break
        return m
    conjuntos = {"max": maximos(pts["max"]), "union": maximos(pts["max"] + pts["todas"])}
    for nombre, mx in conjuntos.items():
        cs = sorted(set(mx) & set(mapa))
        a = np.array([np.floor(mx[c] + 0.5) for c in cs]); b = np.array([mapa[c] for c in cs], float)
        R[nombre] = {"municipios_con_puntos": len(mx), "en_el_mapa_M": len(cs), "exacta": float((a == b).mean()), "dif_le_1": float((np.abs(a - b) <= 1).mean()),
                     "rho": float(spearmanr(a, b)[0]), "sesgo_medio_puntos_menos_mapa": float((a - b).mean()),
                     "mapa_mayor_que_puntos": int((b > a).sum()), "puntos_mayor_que_mapa": int((a > b).sum())}
    R["mapa_M_sin_puntos_max"] = len(set(mapa) - set(conjuntos["max"]))
    R["mapa_M_sin_puntos_union"] = len(set(mapa) - set(conjuntos["union"]))
    (AQUI / "auditoria_sismicidad_historica.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1))


main()
