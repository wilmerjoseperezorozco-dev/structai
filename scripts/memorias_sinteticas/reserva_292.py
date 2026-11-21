"""#292: experimento pareado u_max = 1,0 frente a 0,90 en zona baja. Ver docs/memoria_calculo/PRERREGISTRO_292_RESERVA_ZONA_BAJA.md.

Reusa el método F3b sin cambios (confiabilidad_f3b.evaluar); solo cambia u_max_gravedad del proyecto.

Uso:  python -I scripts/memorias_sinteticas/reserva_292.py [--piloto 6] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f3b_292/{brazos.csv, resultados_292.json}
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
import confiabilidad_f3b as f3b  # noqa: E402

RAIZ = f3.RAIZ
SEMILLA = f3.SEMILLA
BRAZOS = {"control": 1.0, "u090": 0.90}
_proyecto_base = f3._proyecto


def _proyecto_u(de, c):
    return dataclasses.replace(_proyecto_base(de, c), u_max_gravedad=float(c["u_max"]))


f3._proyecto = _proyecto_u                       # f3b.evaluar lo llama por el módulo: también en los procesos hijos


def evaluar(c: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    fila = f3b.evaluar(c)
    inf = de.disenar_edificio(_proyecto_u(de, c))
    return {**fila, "brazo": c["brazo"], "u_max": c["u_max"], "costo_cop": inf.cantidades["costo_cop"],
            "cumple": inf.cumple, "fallas": " | ".join(inf.fallas)[:300]}


CAMPOS = ["brazo", "u_max", "costo_cop", "cumple", "fallas"] + list(f3b.CAMPOS)


def _p10(a):
    return float(np.percentile(a, 10))


def resumir(filas: list[dict]) -> dict:
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    ids = sorted(set(por["control"]) & set(por["u090"]), key=int)
    no_cumple = [i for i in ids if por["u090"][i]["cumple"] != "True" or por["u090"][i]["estado"] != "ok"]
    ok = [i for i in ids if i not in no_cumple and por["control"][i]["estado"] == "ok"]
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_292_RESERVA_ZONA_BAJA.md", "n_pares": len(ids),
           "n_ok": len(ok), "u090_no_cumple": [(i, por["u090"][i]["fallas"]) for i in no_cumple]}
    impr = sum(int(por[b][i][f"imprecisos_{v}"]) for b in BRAZOS for i in ok for v in f3b.VARIANTES)
    nel = sum(int(por[b][i]["n_elementos"]) * len(f3b.VARIANTES) for b in BRAZOS for i in ok)
    out["Q2"] = {"imprecisos": impr, "elementos": nel, "frac": impr / max(1, nel), "cumple": impr / max(1, nel) <= 0.01}
    rng = np.random.default_rng(SEMILLA)
    B = lambda b, v: np.array([float(por[b][i][f"beta_{v}"]) for i in ok])  # noqa: E731
    c0, c1 = B("control", "central"), B("u090", "central")
    a0, a1 = B("control", "alta"), B("u090", "alta")
    reps = [rng.integers(0, len(ok), len(ok)) for _ in range(2000)]
    est = _p10(c1) - _p10(c0)
    bs = [_p10(c1[r]) - _p10(c0[r]) for r in reps]
    out["H-292a"] = {"p10_control": _p10(c0), "p10_u090": _p10(c1), "delta": est,
                     "ic95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    out["H-292a"]["cumple"] = est >= 0.3 and out["H-292a"]["ic95"][0] > 0
    fr = lambda a: float((a < 3.8).mean())  # noqa: E731
    est = fr(a0) - fr(a1)
    bs = [fr(a0[r]) - fr(a1[r]) for r in reps]
    out["H-292b"] = {"frac_control": fr(a0), "frac_u090": fr(a1), "delta": est,
                     "ic95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    out["H-292b"]["cumple"] = est >= 0.10 and out["H-292b"]["ic95"][0] > 0
    sc = np.array([float(por["u090"][i]["costo_cop"]) / float(por["control"][i]["costo_cop"]) - 1 for i in ok])
    out["C-292"] = {"mediana": float(np.median(sc)), "p90": float(np.percentile(sc, 90)), "max": float(sc.max()),
                    "frac_sin_cambio": float((np.abs(sc) < 1e-9).mean())}
    out["C-292"]["cumple"] = out["C-292"]["mediana"] <= 0.03 and out["C-292"]["p90"] <= 0.06
    d = c1 - c0
    out["descriptivo"] = {
        "mediana_central": {"control": float(np.median(c0)), "u090": float(np.median(c1))},
        "delta_beta_central": {"p10": float(np.percentile(d, 10)), "mediana": float(np.median(d)), "p90": float(np.percentile(d, 90))},
        "frac_beta_igual": float((np.abs(d) < 1e-3).mean()),
        "por_N": {g: float(np.median([d[k] for k, i in enumerate(ok) if lo <= int(por["control"][i]["N"]) <= hi]))
                  for g, (lo, hi) in {"1-5": (1, 5), "6-8": (6, 8), "9+": (9, 99)}.items()},
        "critico_control": {t: sum(por["control"][i]["critico_central"].startswith(t) for i in ok) for t in ("viga", "columna")},
    }
    adopta = out["H-292a"]["cumple"] and out["C-292"]["cumple"] and not no_cumple and out["Q2"]["cumple"]
    out["decision"] = ("ADOPTAR u_max_recomendado por defecto en zona baja" if adopta else
                       "CONDICIONADA: hay diseños que dejan de cumplir" if out["H-292a"]["cumple"] and out["C-292"]["cumple"]
                       else "NO ADOPTAR")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None)
    ap.add_argument("--salida", default=str(RAIZ / "data" / "memorias_sinteticas" / "f3b_292"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [r for r in csv.DictReader(f) if r["estado"] == "ok" and r["zona"] == "baja"]
    if a.piloto:
        casos = casos[:a.piloto]
    trabajos = [{**c, "brazo": b, "u_max": u} for c in casos for b, u in BRAZOS.items()]
    out = Path(a.salida if not a.piloto else Path(a.salida) / "piloto")
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
        with Pool(a.hilos, initializer=f3._iniciar) as pool, ruta.open("a", encoding="utf-8", newline="") as f:
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
        filas = list(csv.DictReader(f))
    if a.piloto:
        print(json.dumps({"piloto": len(filas), "estados": [(r["brazo"], r["estado"], r["cumple"]) for r in filas]},
                         ensure_ascii=False))
        return
    res = resumir(filas)
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_292.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("decision", "Q2")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
