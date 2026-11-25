"""#323: sensibilidad del factor de ráfaga Gf (B.6.5.8.2) al amortiguamiento β y al periodo usado para n1, sobre la
población de #242 (272 pórticos de concreto de zona baja que no son edificios bajos), con W36D (36 m/s, exposición D).
Ver docs/memoria_calculo/PRERREGISTRO_323_SENSIBILIDAD_GF.md.

Brazos: b02 (β 0,02, T del modelo: referencia = diseño actual), b01 (β 0,01), b05 (β 0,05), cuta (β 0,02, T = Cu·Ta).

Uso:  python -I scripts/memorias_sinteticas/viento_323.py [--piloto 2] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f1_323/{brazos.csv, resultados_323.json}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import csv
import dataclasses
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confiabilidad_f3 as f3  # noqa: E402
import viento_242 as v242  # noqa: E402

RAIZ = f3.RAIZ
SEMILLA = 3230
BRAZOS = {"b02": (0.02, "modelo"), "b01": (0.01, "modelo"), "b05": (0.05, "modelo"), "cuta": (0.02, "cu_ta")}
CAMPOS = ["id", "brazo", "N", "h_m", "estado", "cumple", "costo_cop", "firma", "G_x", "G_y", "rafaga_x", "rafaga_y",
          "rho_x", "rho_y", "segundos"]


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    t0 = time.time()
    beta, per = BRAZOS[t["brazo"]]
    p = dataclasses.replace(f3._proyecto(de, t), viento=de.VientoB6(v_m_s=36.0, exposicion="D", amortiguamiento=beta,
                                                                   periodo_gf=per))
    fila = {"id": t["id"], "brazo": t["brazo"], "N": t["N"], "h_m": int(t["N"]) * float(t["hp_m"])}
    try:
        inf = de.disenar_edificio(p)
    except Exception as ex:                                            # noqa: BLE001
        return {**fila, "estado": f"error: {type(ex).__name__}: {ex}"[:200], "segundos": round(time.time() - t0, 1)}
    vw = inf.viento
    if vw.get("amortiguamiento") != beta or vw.get("periodo_gf") != per:
        return {**fila, "estado": "error: brazo mal aplicado", "segundos": round(time.time() - t0, 1)}
    ex_, ey_ = sum(inf.sismo["x"]["E_kn"]), sum(inf.sismo["y"]["E_kn"])
    return fila | {"estado": "ok", "cumple": inf.cumple, "costo_cop": inf.cantidades["costo_cop"], "firma": v242._firma(inf),
                   "G_x": vw["G"]["x"], "G_y": vw["G"]["y"], "rafaga_x": vw["rafaga"]["x"], "rafaga_y": vw["rafaga"]["y"],
                   "rho_x": 1.6 * vw["cortante_basal_kn"]["x"] / ex_, "rho_y": 1.6 * vw["cortante_basal_kn"]["y"] / ey_,
                   "segundos": round(time.time() - t0, 1)}


def _si(x) -> bool:
    return str(x) == "True"


def resumir(filas: list[dict]) -> dict:
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    with (RAIZ / "data" / "memorias_sinteticas" / "f1_322" / "brazos.csv").open(encoding="utf-8") as f:
        ref322 = {r["id"]: r for r in csv.DictReader(f) if r["brazo"] == "W36D_c14"}
    ref = por["b02"]
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_323_SENSIBILIDAD_GF.md",
           "errores": [(i, b, f["estado"]) for b in BRAZOS for i, f in por[b].items() if f["estado"] != "ok"]}
    ok0 = [i for i, f in ref.items() if f["estado"] == "ok"]
    out["S0_b02_reproduce_322"] = {"k": sum(i in ref322 and ref322[i]["firma"] == ref[i]["firma"] for i in ok0), "n": len(ok0)}
    out["n_flexibles_b02"] = sum(ref[i]["rafaga_x"] == "flexible" or ref[i]["rafaga_y"] == "flexible" for i in ok0)
    rng = np.random.default_rng(SEMILLA)
    for b in ("b01", "b05", "cuta"):
        ids = [i for i in ok0 if i in por[b] and por[b][i]["estado"] == "ok"]
        razon = np.array([max(float(por[b][i]["rho_x"]), float(por[b][i]["rho_y"])) /
                          max(float(ref[i]["rho_x"]), float(ref[i]["rho_y"])) for i in ids])
        flex = np.array([ref[i]["rafaga_x"] == "flexible" or ref[i]["rafaga_y"] == "flexible" for i in ids])
        boot = [float(np.median(razon[rng.integers(0, len(razon), len(razon))])) for _ in range(2000)]
        cambia = [i for i in ids if por[b][i]["firma"] != ref[i]["firma"]]
        out[b] = {"n": len(ids),
                  "S1_mediana_razon_rho": float(np.median(razon)),
                  "S1_ic95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                  "S1_mediana_razon_rho_flexibles": float(np.median(razon[flex])) if flex.any() else None,
                  "razon_min_max": [float(razon.min()), float(razon.max())],
                  "S2_cambia_refuerzo": {"k": len(cambia), "ic95": v242._wilson(len(cambia), len(ids)), "ids": cambia},
                  "S2b_cumplimiento": {"no_cumple_brazo": sum(not _si(por[b][i]["cumple"]) for i in ids),
                                       "no_cumple_b02": sum(not _si(ref[i]["cumple"]) for i in ids)},
                  "pasan_a_rigida": sum((ref[i]["rafaga_x"] == "flexible") and (por[b][i]["rafaga_x"] == "rígida") for i in ids)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [r for r in csv.DictReader(f) if r["estado"] == "ok" and r["zona"] == "baja" and not v242.bajo(r)]
    print(f"{len(casos)} edificios", flush=True)
    if a.piloto:
        casos = casos[:a.piloto]
    trabajos = [{**c, "brazo": b} for c in casos for b in BRAZOS]
    out = RAIZ / "data" / "memorias_sinteticas" / "f1_323" / ("piloto" if a.piloto else "")
    out.mkdir(parents=True, exist_ok=True)
    ruta = out / "brazos.csv"
    hechos = set()
    if ruta.exists():
        with ruta.open(encoding="utf-8") as f:
            hechos = {(r["id"], r["brazo"]) for r in csv.DictReader(f)}
    pend = [t for t in trabajos if (t["id"], t["brazo"]) not in hechos]
    print(f"{len(hechos)} hechos, {len(pend)} pendientes", flush=True)
    t0 = time.time()
    if pend:
        with Pool(a.hilos) as pool, ruta.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
            if not hechos:
                w.writeheader()
            for k, fila in enumerate(pool.imap_unordered(evaluar, pend, chunksize=1), 1):
                w.writerow(fila)
                f.flush()
                if k % 50 == 0 or a.piloto:
                    print(f"{k}/{len(pend)} en {time.time() - t0:.0f} s", flush=True)
                if a.hasta and time.strftime("%H:%M") >= a.hasta:
                    print("hora límite: se detiene (reanudable)", flush=True)
                    pool.terminate()
                    return
    with ruta.open(encoding="utf-8") as f:
        res = resumir(list(csv.DictReader(f)))
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_323.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "errores"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
