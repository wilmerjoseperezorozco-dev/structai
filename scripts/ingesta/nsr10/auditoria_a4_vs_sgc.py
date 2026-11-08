"""Auditoria del Apendice A-4 (PDF) contra la capa del SGC, por codigo DANE.
Protocolo: PROTOCOLO_AUDITORIA_A4_VS_SGC.md. Solo lectura. Salida: auditoria_a4_vs_sgc.json"""
import json
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

import requests

AQUI = Path(__file__).resolve().parent
URL = ("https://srvags.sgc.gov.co/arcgis/rest/services/Zonas_amenaza_Sismica_NR10/"
       "Municipios_Amenaza_NR10/MapServer/0/query")
PAGINA = 1000


def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower().strip()


def bajar_capa() -> list[dict]:
    filas, ini = [], 0
    while True:
        r = requests.get(URL, params={"where": "1=1", "outFields": "*", "returnGeometry": "false",
                                      "resultOffset": ini, "resultRecordCount": PAGINA, "f": "json"}, timeout=60)
        r.raise_for_status()
        d = r.json()
        lote = [f["attributes"] for f in d.get("features", [])]
        filas += lote
        if not d.get("exceededTransferLimit") and len(lote) < PAGINA:
            return filas
        ini += PAGINA
        time.sleep(0.5)


def main() -> None:
    a4 = json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8"))
    capa = bajar_capa()
    campo_zona = next(k for k in capa[0] if k.startswith("ZONA_AMENAZA"))
    por_cod = defaultdict(list)
    for r in capa:
        por_cod[str(r["CÓDIGO_MUNICIPIO"]).zfill(5)].append(r)
    a4_por_cod = {f["codigo"]: f for f in a4}
    dif, sin_sgc, multiples = [], [], []
    for cod, f in a4_por_cod.items():
        regs = por_cod.get(cod)
        if not regs:
            sin_sgc.append(cod)
            continue
        if len(regs) > 1:
            multiples.append((cod, len(regs)))
        r = regs[0]
        d = {}
        for a, b in (("aa", "AA"), ("av", "AV"), ("ae", "AE"), ("ad", "AD")):
            if r[b] is None or abs(f[a] - r[b]) > 1e-9:
                d[a] = (f[a], r[b])
        if sin_acentos(r[campo_zona]) != sin_acentos(f["zona"]):
            d["zona"] = (f["zona"], r[campo_zona])
        if sin_acentos(r["NOMBRE_MUNICIPIO"]) != sin_acentos(f["municipio"]):
            d["nombre"] = (f["municipio"], r["NOMBRE_MUNICIPIO"])
        if d:
            dif.append({"codigo": cod, "municipio": f["municipio"], "departamento": f["departamento"],
                        "pagina_a4": f["pagina"], "difs": d})
    sin_a4 = sorted(set(por_cod) - set(a4_por_cod))
    res = {"n_a4": len(a4_por_cod), "n_capa_registros": len(capa), "n_capa_codigos": len(por_cod),
           "con_diferencias": len(dif), "a4_sin_sgc": sin_sgc, "sgc_sin_a4": sin_a4,
           "codigos_con_varios_registros_en_sgc": multiples, "diferencias": dif}
    (AQUI / "auditoria_a4_vs_sgc.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()})
    solo_zona = sum(1 for x in dif if set(x["difs"]) == {"zona"})
    solo_nombre = sum(1 for x in dif if set(x["difs"]) == {"nombre"})
    print("solo zona:", solo_zona, "| solo nombre:", solo_nombre, "| con valores:",
          sum(1 for x in dif if set(x["difs"]) & {"aa", "av", "ae", "ad"}))
    for x in dif[:40]:
        print(x["codigo"], x["municipio"], x["departamento"], x["pagina_a4"], x["difs"])


if __name__ == "__main__":
    main()
