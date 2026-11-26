"""#333: H5 y H6 de Wilmer (costo real de la transición de cimentación). Prerregistro en
docs/memoria_calculo/PRERREGISTRO_333_H5_H6.md.

Por edificio (11 del grupo falla de #324) y diseño (sin_viento / W36D, secciones de f1_324/brazos.csv):
  q = 200 kPa: la transición más barata de la escalera cuadrada → rectangular → losa rígida
               (orquestador.transicion_cimentacion_3d.disenar_transicion);
  q = 100 kPa: losa rígida bajo todo el edificio (disenar_losa) y, como sensibilidad, la transición más barata.

Uso:  python -I scripts/memorias_sinteticas/viento_333h56.py [--hilos 6]
Salida: data/memorias_sinteticas/f1_333h56/{crudo.json, resultados_333h56.json}
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
import viento_324c as v324c  # noqa: E402

RAIZ = f3.RAIZ
H5_RANGO = (0.25, 0.35)        # predicción de Wilmer para C_cim/C_super con 200 kPa
H6_UMBRAL_PP = 0.5             # predicción de Wilmer: Δ < +0,5 pp con 100 kPa y losa


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import cimentacion_edificio_3d as ci, diseno_edificio_3d as de, optimizar_edificio_3d as op
    from src import transicion_cimentacion_3d as tr
    t0 = time.time()
    p = v324c._proy(de, op, t["c"], t["fila"], t["brazo"] == "W36D")
    reac = ci.reacciones_por_caso(p)
    out = {"id": t["c"]["id"], "brazo": t["brazo"], "costo_super_cop": float(t["fila"]["costo_cop"])}
    for q in (200.0, 100.0):
        tz = tr.disenar_transicion(p, q, reac=reac)
        d = {k: getattr(tz, k) for k in ("solucion", "costo_cop", "costo_aisladas_cop", "costo_rectangulares_cop",
                                         "costo_losa_cop", "no_caben", "rectangulares", "motivo")}
        losa = tz.losa if tz.losa is not None else tr.disenar_losa(p, q, reac=reac)
        d["losa"] = dataclasses.asdict(losa)
        out[f"q{int(q)}"] = d
    out["segundos"] = round(time.time() - t0, 1)
    return out


def _seguro(t):
    try:
        return evaluar(t)
    except Exception as e:  # noqa: BLE001 — se reporta por id
        return {"id": t["c"]["id"], "brazo": t["brazo"], "error": repr(e), "segundos": 0}


def _med(xs):
    xs = [x for x in xs if x is not None and math.isfinite(x)]
    return {"mediana": float(np.median(xs)), "min": float(min(xs)), "max": float(max(xs)), "n": len(xs)} if xs else None


def resumir(res: list[dict]) -> dict:
    por = {(r["id"], r["brazo"]): r for r in res if "error" not in r}
    ids = sorted({r["id"] for r in res}, key=int)
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_333_H5_H6.md",
           "errores": [f"{r['id']}/{r['brazo']}: {r['error']}" for r in res if "error" in r]}
    # H5 (q = 200): razón cimentación de transición / superestructura en los que no caben
    h5 = {}
    for b in ("W36D", "sin_viento"):
        filas = []
        for i in ids:
            r = por.get((i, b))
            if r is None:
                continue
            q = r["q200"]
            filas.append({"id": i, "no_caben": q["no_caben"], "solucion": q["solucion"],
                          "razon_transicion": q["costo_cop"] / r["costo_super_cop"] if math.isfinite(q["costo_cop"]) else math.nan,
                          "razon_aisladas_324c": q["costo_aisladas_cop"] / r["costo_super_cop"],
                          "costo_rect_sobre_aisladas": (q["costo_rectangulares_cop"] / q["costo_aisladas_cop"]
                                                        if math.isfinite(q["costo_rectangulares_cop"]) else math.nan),
                          "costo_losa_sobre_aisladas": (q["costo_losa_cop"] / q["costo_aisladas_cop"]
                                                        if math.isfinite(q["costo_losa_cop"]) else math.nan)})
        nc = [f for f in filas if f["no_caben"] > 0]
        m = _med([f["razon_transicion"] for f in nc])
        h5[b] = {"edificios_no_caben": [f["id"] for f in nc],
                 "razon_transicion": m, "razon_aisladas_324c_mismos": _med([f["razon_aisladas_324c"] for f in nc]),
                 "razon_todos_11": _med([f["razon_transicion"] for f in filas]),
                 "soluciones": {s: sum(f["solucion"] == s for f in nc) for s in ("aisladas", "rectangulares", "losa", "sin_solucion")},
                 "veredicto": (None if m is None else
                               ("se cumple" if H5_RANGO[0] <= m["mediana"] <= H5_RANGO[1] else "refutada")),
                 "filas": filas}
    out["H5_q200"] = h5
    # H6 (q = 100): losa rígida, sobrecosto atribuible al viento en pp del costo total sin viento
    filas, no_factible = [], []
    for i in ids:
        sv, w = por.get((i, "sin_viento")), por.get((i, "W36D"))
        if sv is None or w is None:
            continue
        ls, lw = sv["q100"]["losa"], w["q100"]["losa"]
        if not (ls["cumple"] and lw["cumple"]):
            no_factible.append({"id": i, "sv": ls["cumple"], "W": lw["cumple"], "motivo": ls["motivo"] or lw["motivo"]})
            continue
        tot_sv = sv["costo_super_cop"] + ls["costo_cop"]
        filas.append({"id": i, "delta_pp": 100 * (lw["costo_cop"] - ls["costo_cop"]) / tot_sv,
                      "sobrecosto_total_pp": 100 * ((w["costo_super_cop"] + lw["costo_cop"]) / tot_sv - 1),
                      "sobrecosto_super_pp": 100 * (w["costo_super_cop"] / sv["costo_super_cop"] - 1),
                      "losa_sobre_super_sv": ls["costo_cop"] / sv["costo_super_cop"],
                      "h_sv_mm": ls["h_mm"], "h_W_mm": lw["h_mm"], "q_max_W_kpa": lw["q_max_serv_kpa"]})
    m = _med([f["delta_pp"] for f in filas])
    out["H6_q100"] = {"factibles": len(filas), "no_factibles": no_factible, "delta_pp": m,
                      "veredicto": ("inconclusa (ninguna losa factible)" if m is None
                                    else ("se cumple" if m["mediana"] < H6_UMBRAL_PP else "refutada")),
                      "filas": filas}
    # sensibilidad: la transición más barata con 100 kPa
    out["q100_transicion"] = {b: {s: sum(por[(i, b)]["q100"]["solucion"] == s for i in ids if (i, b) in por)
                                  for s in ("aisladas", "rectangulares", "losa", "sin_solucion")} for b in ("sin_viento", "W36D")}
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
    print(f"{len(trabajos)} diseños", flush=True)
    t0 = time.time()
    with Pool(a.hilos) as pool:
        res = []
        for k, r in enumerate(pool.imap_unordered(_seguro, trabajos), 1):
            res.append(r)
            print(f"{k}/{len(trabajos)} {r['id']} {r['brazo']} {r['segundos']} s {r.get('error', '')}", flush=True)
    out = d / "f1_333h56"
    out.mkdir(parents=True, exist_ok=True)
    (out / "crudo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    s = resumir(res)
    s["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_333h56.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: (v if k != "H5_q200" else {b: {kk: vv for kk, vv in x.items() if kk != "filas"} for b, x in v.items()})
                      for k, v in s.items()}, ensure_ascii=False, default=str)[:6000])


if __name__ == "__main__":
    main()
