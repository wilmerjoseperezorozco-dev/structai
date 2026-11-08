"""Capas de intensidad sismica del SGC vs Apendice A-4. Protocolo: PROTOCOLO_INTENSIDAD_VS_A4.md. Solo lectura."""
import json
from pathlib import Path

import numpy as np
import requests
from scipy.stats import spearmanr

AQUI = Path(__file__).resolve().parent
B = "https://srvags.sgc.gov.co/arcgis/rest/services/"
OBS = B + "Mapa_Intensidad_Maxima_Observada_Colombia/Intensidad_Observada_Departamento_Municipio/MapServer/1/query"
ESP = B + "Zonificacion_Sismica_Intensidad_Esperada/Zonificacion_Sismica_Intensidad_Esperada/MapServer/6/query"
N_BOOT = 2000
RNG = np.random.default_rng(31)


def consultar(url: str, campos: str, paginar: bool) -> list[dict]:
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


def boot(fun, bloques):
    et = np.unique(bloques)
    idx = {b: np.where(bloques == b)[0] for b in et}
    out = []
    for _ in range(N_BOOT):
        ix = np.concatenate([idx[b] for b in RNG.choice(et, len(et), replace=True)])
        v = fun(ix)
        if np.isfinite(v):
            out.append(v)
    return [float(v) for v in np.percentile(out, [2.5, 97.5])]


def main() -> None:
    a4 = {f["codigo"]: f for f in json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8"))}
    obs = {str(r["CODIGO_DANE"]).zfill(5): r for r in consultar(OBS, "CODIGO_DANE,GRIDCODE,CATEGORIA,NOMBRE_ENT", True)
           if r["CATEGORIA"] == "M" and r["GRIDCODE"] is not None}
    esp = {str(r["MPIO_CCDGO"]).zfill(5): r for r in consultar(ESP, "MPIO_CCDGO,PGA,MPIO_CNMBR,DPTO_CNMBR", False) if r["PGA"] is not None}
    cods = sorted(set(a4) & set(obs) & set(esp))
    aa = np.array([a4[c]["aa"] for c in cods]); io = np.array([obs[c]["GRIDCODE"] for c in cods], float)
    pga = np.array([esp[c]["PGA"] for c in cods]); dep = np.array([c[:2] for c in cods])
    R = {"n_a4": len(a4), "n_obs": len(obs), "n_esp": len(esp), "n_cruce": len(cods)}
    for nombre, y in (("aa_vs_intensidad_observada", io), ("aa_vs_pga_esperado", pga)):
        v = spearmanr(aa, y)[0]
        R[nombre] = [float(v)] + boot(lambda i: spearmanr(aa[i], y[i])[0], dep)
    zona = np.array([a4[c]["zona"] for c in cods])
    R["discordantes_obs_ge8_zona_baja"] = [{"codigo": c, "municipio": a4[c]["municipio"], "dep": a4[c]["departamento"], "intensidad": int(obs[c]["GRIDCODE"]),
                                            "aa": a4[c]["aa"], "pga_esperado": round(esp[c]["PGA"], 3)} for c, z, i in zip(cods, zona, io) if i >= 8 and z == "Baja"]
    R["n_obs_ge8"] = int((io >= 8).sum())
    R["obs_ge8_aa_le_010"] = int(((io >= 8) & (aa <= 0.10)).sum())
    R["intensidad_por_zona"] = {z: {"n": int((zona == z).sum()), "media": float(io[zona == z].mean()), "frac_ge8": float((io[zona == z] >= 8).mean())} for z in ("Baja", "Intermedia", "Alta")}
    razon = pga / aa
    R["razon_pga_aa"] = {"mediana": float(np.median(razon)), "p10": float(np.percentile(razon, 10)), "p90": float(np.percentile(razon, 90)),
                         "n_gt_1_5": int((razon > 1.5).sum()), "n_lt_0_67": int((razon < 0.67).sum())}
    (AQUI / "auditoria_intensidad_vs_a4.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in R.items() if k != "discordantes_obs_ge8_zona_baja"}, ensure_ascii=False, indent=1))
    print("discordantes (obs>=8 y zona Baja):", len(R["discordantes_obs_ge8_zona_baja"]))
    for x in R["discordantes_obs_ge8_zona_baja"][:25]:
        print(x)


if __name__ == "__main__":
    main()
