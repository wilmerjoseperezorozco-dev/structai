"""#324: redimensionar por viento. El optimizador de secciones (optimizar_edificio_3d) usa como juez el diseño completo,
que incluye las combinaciones con W (B.2.4-3, -4, -6) cuando el proyecto declara VientoB6. Aquí se corre con y sin
viento W36D (casos 1–4) en los edificios de #242/#322 que dejan de cumplir o cambian refuerzo con W36D.
Ver docs/memoria_calculo/PRERREGISTRO_324_REDIMENSIONAR_VIENTO.md.

Uso:  python -I scripts/memorias_sinteticas/viento_324.py [--piloto 1] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f1_324/{brazos.csv, resultados_324.json}
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

RAIZ = f3.RAIZ
BRAZOS = ("sin_viento", "W36D")
CAMPOS = ["id", "grupo", "brazo", "N", "h_m", "estado", "encontrado", "c_inferior_mm", "c_superior_mm", "b_viga_mm",
          "h_viga_mm", "costo_cop", "evaluaciones_diseno", "motivo", "segundos"]


def poblacion() -> dict[str, str]:
    """id → grupo ('falla': no cumple con W36D_c14; 'cambia': cumple pero su refuerzo difiere del control)."""
    d = RAIZ / "data" / "memorias_sinteticas"
    with (d / "f1_322" / "brazos.csv").open(encoding="utf-8") as f:
        w = [r for r in csv.DictReader(f) if r["brazo"] == "W36D_c14"]
    with (d / "f1_242" / "brazos.csv").open(encoding="utf-8") as f:
        ctrl = {r["id"]: r for r in csv.DictReader(f) if r["brazo"] == "control"}
    out = {r["id"]: "falla" for r in w if r["cumple"] != "True"}
    out |= {r["id"]: "cambia" for r in w if r["cumple"] == "True" and r["firma"] != ctrl[r["id"]]["firma"]}
    return out


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de, optimizar_edificio_3d as op
    t0 = time.time()
    base = f3._proyecto(de, t)
    if t["brazo"] == "W36D":
        base = dataclasses.replace(base, viento=de.VientoB6(v_m_s=36.0, exposicion="D"))
    fila = {"id": t["id"], "grupo": t["grupo"], "brazo": t["brazo"], "N": t["N"], "h_m": int(t["N"]) * float(t["hp_m"])}
    try:
        r = op.optimizar(base)
    except Exception as ex:                                            # noqa: BLE001
        return {**fila, "estado": f"error: {type(ex).__name__}: {ex}"[:200], "segundos": round(time.time() - t0, 1)}
    fila |= {"estado": "ok", "encontrado": r.mejor is not None, "evaluaciones_diseno": r.evaluaciones_diseno,
             "motivo": r.motivo_sin_solucion[:200], "segundos": round(time.time() - t0, 1)}
    if r.mejor is not None:
        cand = min((c for c in r.candidatos if c.get("c") is not None), key=lambda c: c["costo_cop"])
        n = int(t["N"])
        delta = cand["delta"]
        fila |= {"c_inferior_mm": cand["c"], "c_superior_mm": max(300.0, cand["c"] - delta) if n > 1 else cand["c"],
                 "h_viga_mm": cand["h"], "b_viga_mm": max(300.0, 50.0 * -(-cand["h"] / 2 // 50)),
                 "costo_cop": r.mejor.cantidades["costo_cop"]}
        if t["brazo"] == "W36D" and not (r.mejor.viento or {}).get("evaluado"):
            fila["estado"] = "error: el diseño elegido no evaluó viento"
    return fila


def resumir(filas: list[dict]) -> dict:
    d = RAIZ / "data" / "memorias_sinteticas"
    with (d / "corpus.csv").open(encoding="utf-8") as f:
        corpus = {r["id"]: r for r in csv.DictReader(f)}
    with (d / "f1_322" / "brazos.csv").open(encoding="utf-8") as f:
        fijo = {r["id"]: r for r in csv.DictReader(f) if r["brazo"] == "W36D_c14"}
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    sv, w = por["sin_viento"], por["W36D"]
    ok = [i for i in sv if i in w and sv[i]["estado"] == "ok" and w[i]["estado"] == "ok"]
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_324_REDIMENSIONAR_VIENTO.md",
           "errores": [(f["id"], f["brazo"], f["estado"]) for f in filas if f["estado"] != "ok"]}

    def igual(a, b):
        return abs(float(a) - float(b)) < 1e-6
    rep = [i for i in ok if sv[i]["encontrado"] == "True" and igual(sv[i]["c_inferior_mm"], corpus[i]["c_inferior_mm"])
           and igual(sv[i]["c_superior_mm"], corpus[i]["c_superior_mm"]) and igual(sv[i]["h_viga_mm"], corpus[i]["h_viga_mm"])]
    out["R0_sin_viento_reproduce_corpus"] = {"k": len(rep), "n": len(ok), "no": [i for i in ok if i not in rep]}
    for g in ("falla", "cambia"):
        ids = [i for i in ok if sv[i]["grupo"] == g]
        enc = [i for i in ids if w[i]["encontrado"] == "True" and sv[i]["encontrado"] == "True"]
        sob = np.array([float(w[i]["costo_cop"]) / float(sv[i]["costo_cop"]) - 1 for i in enc])
        sube_c = [i for i in enc if float(w[i]["c_inferior_mm"]) > float(sv[i]["c_inferior_mm"])]
        sube_h = [i for i in enc if float(w[i]["h_viga_mm"]) > float(sv[i]["h_viga_mm"])]
        res = {"n": len(ids), "R1_encontrado_W36D": {"k": sum(w[i]["encontrado"] == "True" for i in ids),
                                                      "sin_solucion": {i: w[i]["motivo"] for i in ids if w[i]["encontrado"] != "True"}},
               "R2_sobrecosto_vs_sin_viento": {"mediana": float(np.median(sob)) if len(sob) else None,
                                               "min": float(sob.min()) if len(sob) else None,
                                               "max": float(sob.max()) if len(sob) else None,
                                               "por_id": {i: float(s) for i, s in zip(enc, sob)}},
               "R4_sube_columna_inferior": {"k": len(sube_c), "de": len(enc)}, "sube_viga": {"k": len(sube_h), "de": len(enc)},
               "secciones": {i: {"sin_viento": (sv[i]["c_inferior_mm"], sv[i]["c_superior_mm"], sv[i]["h_viga_mm"]),
                                 "W36D": (w[i]["c_inferior_mm"], w[i]["c_superior_mm"], w[i]["h_viga_mm"])} for i in enc}}
        if g == "cambia":
            mejor = [i for i in enc if i in fijo and float(w[i]["costo_cop"]) <= float(fijo[i]["costo_cop"]) + 1e-6]
            res["R3_opt_no_mas_caro_que_seccion_fija"] = {"k": len(mejor), "de": len(enc)}
        out[g] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    grupos = poblacion()
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [{**r, "grupo": grupos[r["id"]]} for r in csv.DictReader(f) if r["id"] in grupos]
    print(f"{len(casos)} edificios ({sum(c['grupo'] == 'falla' for c in casos)} fallan)", flush=True)
    if a.piloto:
        casos = casos[:a.piloto]
    # los más lentos primero, para repartir mejor la carga
    trabajos = sorted(({**c, "brazo": b} for c in casos for b in BRAZOS), key=lambda t: -float(t["segundos"]))
    out = RAIZ / "data" / "memorias_sinteticas" / "f1_324" / ("piloto" if a.piloto else "")
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
                print(f"{k}/{len(pend)} en {time.time() - t0:.0f} s ({fila['id']} {fila['brazo']} {fila['estado'][:30]})", flush=True)
                if a.hasta and time.strftime("%H:%M") >= a.hasta:
                    print("hora límite: se detiene (reanudable)", flush=True)
                    pool.terminate()
                    return
    with ruta.open(encoding="utf-8") as f:
        res = resumir(list(csv.DictReader(f)))
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_324.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "errores"}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
