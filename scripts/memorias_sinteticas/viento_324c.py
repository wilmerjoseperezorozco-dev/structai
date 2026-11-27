"""#324-C: la cimentación de los 11 edificios que se redimensionan por viento (#324). Hipótesis H1–H4 de Wilmer y
contrapredicciones de Claude en docs/memoria_calculo/PRERREGISTRO_324C_CIMENTACION_VIENTO.md.

Por edificio, dos diseños de #324 (secciones de data/memorias_sinteticas/f1_324/brazos.csv):
  sin_viento: secciones óptimas sin viento, cimentación con combinaciones sin W;
  W36D:       secciones óptimas con W36D (casos 1–4), cimentación con las combinaciones con W.
Zapatas aisladas (orquestador.cimentacion_edificio_3d) para q_adm ∈ Q_ADM (estratos declarados: el corpus no tiene
estudio de suelos).

Uso:  python -I scripts/memorias_sinteticas/viento_324c.py [--hilos 6]
Salida: data/memorias_sinteticas/f1_324c/{zapatas.csv, resultados_324c.json}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import csv
import dataclasses
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confiabilidad_f3 as f3  # noqa: E402

RAIZ = f3.RAIZ
Q_ADM = (100.0, 200.0, 400.0)                  # kPa: blando, medio, firme (estratos DECLARADOS)
VIGA = {"1290", "1729", "1762"}                # #324: la solución con viento fue peraltar la viga, no la columna


def _proy(de, op, c, fila, viento):
    n = int(c["N"])
    ci_, cs_, h = float(fila["c_inferior_mm"]), float(fila["c_superior_mm"]), float(fila["h_viga_mm"])
    cols, vigas = op._secciones(n, ci_, ci_ - cs_, h)
    p = dataclasses.replace(f3._proyecto(de, c), columnas_mm=cols, vigas_mm=vigas)
    return dataclasses.replace(p, viento=de.VientoB6(v_m_s=36.0, exposicion="D")) if viento else p


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import cimentacion_edificio_3d as ci, diseno_edificio_3d as de, optimizar_edificio_3d as op
    t0 = time.time()
    p = _proy(de, op, t["c"], t["fila"], t["brazo"] == "W36D")
    out = {"id": t["c"]["id"], "brazo": t["brazo"], "uso_deriva_sismo": op._uso_deriva(p), "por_q": {}}
    reac = ci.reacciones_por_caso(p)
    for q in Q_ADM:
        r = ci.disenar_zapatas(p, q, reac=reac)
        zs = r.zapatas
        out["por_q"][q] = {"costo_cop": r.costo_cop, "no_caben": r.no_caben, "sin_solucion": r.sin_solucion, "n": len(zs),
                           "gobierna": {g: sum(z.gobierna == g for z in zs) for g in ("portante", "excentricidad", "estructural")},
                           "traccion_neta": sum(z.traccion_neta for z in zs),
                           "L_max_mm": max((z.L_mm for z in zs if z.cumple), default=math.nan),
                           "volumen_m3": sum(z.volumen_m3 for z in zs)}
    out["segundos"] = round(time.time() - t0, 1)
    return out


def _vol_columnas(c, fila):
    """Volumen de columnas por mitad (inferior, superior), m³: optimizar_edificio_3d usa c en la mitad inferior y c − Δ arriba."""
    n, hp = int(c["N"]), float(c["hp_m"])
    ncol = (int(c["vanos_x"]) + 1) * (int(c["vanos_y"]) + 1)
    abajo = math.ceil(n / 2)
    ci_, cs_ = float(fila["c_inferior_mm"]) / 1000, float(fila["c_superior_mm"]) / 1000
    return abajo * ncol * hp * ci_ ** 2, (n - abajo) * ncol * hp * cs_ ** 2


def resumir(res: list[dict], corpus: dict, secc: dict) -> dict:
    por = {(r["id"], r["brazo"]): r for r in res}
    ids = sorted({r["id"] for r in res}, key=int)
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_324C_CIMENTACION_VIENTO.md", "Q_ADM": Q_ADM}
    for q in Q_ADM:
        d, filas = {}, []
        for i in ids:
            sv, w = por[(i, "sin_viento")]["por_q"][q], por[(i, "W36D")]["por_q"][q]
            sup_sv, sup_w = float(secc[(i, "sin_viento")]["costo_cop"]), float(secc[(i, "W36D")]["costo_cop"])
            s_sup = sup_w / sup_sv - 1
            s_tot = (sup_w + w["costo_cop"]) / (sup_sv + sv["costo_cop"]) - 1
            ecc = (w["gobierna"]["excentricidad"] + 0) / w["n"]
            filas.append({"id": i, "sobrecosto_super": s_sup, "sobrecosto_total": s_tot, "delta_pp": 100 * (s_tot - s_sup),
                          "sobrecosto_cimentacion": w["costo_cop"] / sv["costo_cop"] - 1 if sv["costo_cop"] else math.nan,
                          "cim_sobre_super_sv": sv["costo_cop"] / sup_sv,
                          "frac_excentricidad_W": ecc, "traccion_neta_W": w["traccion_neta"],
                          "frac_excentricidad_sv": sv["gobierna"]["excentricidad"] / sv["n"],
                          "no_caben_sv": sv["no_caben"], "no_caben_W": w["no_caben"],
                          "sin_solucion": sv["sin_solucion"] + w["sin_solucion"]})
        dp = np.array([f["delta_pp"] for f in filas])
        d["H1_delta_pp"] = {"mediana": float(np.median(dp)), "min": float(dp.min()), "max": float(dp.max())}
        d["H1_sobrecosto_mediano"] = {"super": float(np.median([f["sobrecosto_super"] for f in filas])),
                                     "total": float(np.median([f["sobrecosto_total"] for f in filas])),
                                     "cimentacion": float(np.nanmedian([f["sobrecosto_cimentacion"] for f in filas]))}
        gob = [f["id"] for f in filas if f["frac_excentricidad_W"] >= 0.5 or f["traccion_neta_W"] > 0]
        d["H2_gobernados_por_excentricidad_o_levantamiento"] = {"k": len(gob), "de": len(filas), "ids": gob}
        d["no_caben"] = {"edificios_con_alguna_sv": sum(f["no_caben_sv"] > 0 for f in filas),
                         "edificios_con_alguna_W": sum(f["no_caben_W"] > 0 for f in filas)}
        d["filas"] = filas
        out[f"q{int(q)}"] = d
    # H3: geometría de los 3 resueltos con viga frente a los 8 resueltos con columna
    geo = {}
    for i in ids:
        c = corpus[i]
        lx, ly = int(c["vanos_x"]) * float(c["Lx_m"]), int(c["vanos_y"]) * float(c["Ly_m"])
        geo[i] = {"luz_max_m": max(float(c["Lx_m"]), float(c["Ly_m"])), "H_sobre_Bmin": int(c["N"]) * float(c["hp_m"]) / min(lx, ly),
                  "uso_deriva_sv": por[(i, "sin_viento")]["uso_deriva_sismo"], "uso_deriva_W": por[(i, "W36D")]["uso_deriva_sismo"]}
    g_v = [geo[i] for i in ids if i in VIGA]
    g_c = [geo[i] for i in ids if i not in VIGA]
    out["H3"] = {k: {"viga_mediana": float(np.median([g[k] for g in g_v])), "columna_mediana": float(np.median([g[k] for g in g_c])),
                     "viga": [g[k] for g in g_v]} for k in ("luz_max_m", "H_sobre_Bmin")}
    out["H3"]["rango_en_11"] = {k: sorted(ids, key=lambda i: -geo[i][k]).__repr__() for k in ("luz_max_m", "H_sobre_Bmin")}
    out["H3"]["geometria"] = geo
    # H4: compensación de volumen de columnas
    comp = {}
    for i in ids:
        lo_sv, up_sv = _vol_columnas(corpus[i], secc[(i, "sin_viento")])
        lo_w, up_w = _vol_columnas(corpus[i], secc[(i, "W36D")])
        dlo, dup = lo_w - lo_sv, up_w - up_sv
        comp[i] = {"dV_inferior_m3": dlo, "dV_superior_m3": dup, "compensacion": (-dup / dlo) if dlo > 0 else None}
    vals = [v["compensacion"] for v in comp.values() if v["compensacion"] is not None]
    out["H4"] = {"n_con_dV_inferior_positivo": len(vals), "mediana": float(np.median(vals)) if vals else None,
                 "valores": comp}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hilos", type=int, default=6)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    d = RAIZ / "data" / "memorias_sinteticas"
    with (d / "corpus.csv").open(encoding="utf-8") as f:
        corpus = {r["id"]: r for r in csv.DictReader(f)}
    with (d / "f1_324" / "brazos.csv").open(encoding="utf-8") as f:
        secc = {(r["id"], r["brazo"]): r for r in csv.DictReader(f) if r["grupo"] == "falla"}
    trabajos = [{"c": corpus[i], "fila": fila, "brazo": b} for (i, b), fila in secc.items()]
    print(f"{len(trabajos)} diseños de cimentación ({len(Q_ADM)} q_adm cada uno)", flush=True)
    t0 = time.time()
    with Pool(a.hilos) as pool:
        res = []
        for k, r in enumerate(pool.imap_unordered(evaluar, trabajos), 1):
            res.append(r)
            print(f"{k}/{len(trabajos)} {r['id']} {r['brazo']} {r['segundos']} s", flush=True)
    out = d / "f1_324c"
    out.mkdir(parents=True, exist_ok=True)
    (out / "crudo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    s = resumir(res, corpus, secc)
    s["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_324c.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in s.items() if k.startswith("q")} | {"H3": {k: v for k, v in s["H3"].items() if k != "geometria"},
                      "H4": {k: v for k, v in s["H4"].items() if k != "valores"}}, ensure_ascii=False, default=str)[:4000])


if __name__ == "__main__":
    main()
