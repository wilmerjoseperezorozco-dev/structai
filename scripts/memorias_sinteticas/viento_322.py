"""#322: efecto de los casos 2–4 de la Fig. B.6.5-6 (carga parcial y torsional) sobre la misma población de #242
(pórticos de concreto de zona baja que no son edificios bajos). Ver docs/memoria_calculo/PRERREGISTRO_322_VIENTO_TORSIONAL.md.

Brazos por edificio: W28C y W36D, cada uno con solo el caso 1 (c1) y con los casos 1–4 (c14). Mismo código, solo
cambia VientoB6.casos_parciales.

Uso:  python -I scripts/memorias_sinteticas/viento_322.py [--piloto 2] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f1_322/{brazos.csv, resultados_322.json}
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confiabilidad_f3 as f3  # noqa: E402
import viento_242 as v242  # noqa: E402

RAIZ = f3.RAIZ
BRAZOS = {"W28C_c1": (28.0, "C", False), "W28C_c14": (28.0, "C", True),
          "W36D_c1": (36.0, "D", False), "W36D_c14": (36.0, "D", True)}
CAMPOS = ["id", "brazo", "N", "h_m", "estado", "cumple", "fallas", "costo_cop", "firma", "firma_vigas", "firma_columnas",
          "segundos"]


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    t0 = time.time()
    v, e, parc = BRAZOS[t["brazo"]]
    p = dataclasses.replace(f3._proyecto(de, t), viento=de.VientoB6(v_m_s=v, exposicion=e, casos_parciales=parc))
    fila = {"id": t["id"], "brazo": t["brazo"], "N": t["N"], "h_m": int(t["N"]) * float(t["hp_m"])}
    try:
        inf = de.disenar_edificio(p)
    except Exception as ex:                                            # noqa: BLE001
        return {**fila, "estado": f"error: {type(ex).__name__}: {ex}"[:200], "segundos": round(time.time() - t0, 1)}
    if tuple(inf.viento.get("casos_fig_b656", ())) != ((1, 2, 3, 4) if parc else (1,)):
        return {**fila, "estado": "error: casos de viento inesperados", "segundos": round(time.time() - t0, 1)}
    return fila | {"estado": "ok", "cumple": inf.cumple, "fallas": " | ".join(inf.fallas)[:300],
                   "costo_cop": inf.cantidades["costo_cop"], "firma": v242._firma(inf),
                   "firma_vigas": v242._firma(inf, "vigas"), "firma_columnas": v242._firma(inf, "columnas"),
                   "segundos": round(time.time() - t0, 1)}


def _si(x) -> bool:
    return str(x) == "True"


def resumir(filas: list[dict]) -> dict:
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    with (RAIZ / "data" / "memorias_sinteticas" / "f1_242" / "brazos.csv").open(encoding="utf-8") as f:
        ant = {(r["brazo"], r["id"]): r for r in csv.DictReader(f)}
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_322_VIENTO_TORSIONAL.md"}
    for vb in ("W28C", "W36D"):
        c1, c14 = por[f"{vb}_c1"], por[f"{vb}_c14"]
        ids = sorted(set(c1) & set(c14), key=int)
        ok = [i for i in ids if c1[i]["estado"] == "ok" and c14[i]["estado"] == "ok"]
        errores = [(i, b, f["estado"]) for b in (f"{vb}_c1", f"{vb}_c14") for i, f in por[b].items() if f["estado"] != "ok"]
        rep = [i for i in ok if (vb, i) in ant and ant[(vb, i)].get("firma") == c1[i]["firma"]]          # T0
        cambia = [i for i in ok if c1[i]["firma"] != c14[i]["firma"]]
        cv = [i for i in ok if c1[i]["firma_vigas"] != c14[i]["firma_vigas"]]
        cc = [i for i in ok if c1[i]["firma_columnas"] != c14[i]["firma_columnas"]]
        gob_242 = {i for i in ok if ("control", i) in ant and ant[("control", i)]["firma"] != c1[i]["firma"]}
        dejan = [i for i in ok if _si(c1[i]["cumple"]) and not _si(c14[i]["cumple"])]
        recuperan = [i for i in ok if not _si(c1[i]["cumple"]) and _si(c14[i]["cumple"])]
        dcosto = sorted(float(c14[i]["costo_cop"]) / float(c1[i]["costo_cop"]) - 1 for i in cambia)
        out[vb] = {"n_ok": len(ok), "errores": errores,
                   "T0_reproduce_242": {"k": len(rep), "n": len(ok)},
                   "T1_cambia_refuerzo": {"k": len(cambia), "frac": len(cambia) / max(1, len(ok)),
                                          "ic95": v242._wilson(len(cambia), len(ok)), "ids": cambia},
                   "T1b_dentro_de_gobernados_242": {"k": len(set(cambia) & gob_242), "de": len(cambia),
                                                    "n_gobernados_242": len(gob_242)},
                   "T2_dejan_de_cumplir": {"k": len(dejan), "ids": dejan,
                                           "c1_no_cumple": sum(not _si(c1[i]["cumple"]) for i in ok),
                                           "c14_no_cumple": sum(not _si(c14[i]["cumple"]) for i in ok),
                                           "recuperan": recuperan},
                   "T3_vigas_columnas": {"k_vigas": len(cv), "k_columnas": len(cc)},
                   "costo_rel_en_los_que_cambian": {"mediana": dcosto[len(dcosto) // 2] if dcosto else None,
                                                    "max": dcosto[-1] if dcosto else None}}
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
    out = RAIZ / "data" / "memorias_sinteticas" / "f1_322" / ("piloto" if a.piloto else "")
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
    (out / "resultados_322.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({b: {k: v for k, v in res[b].items() if k != "errores"} for b in ("W28C", "W36D")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
