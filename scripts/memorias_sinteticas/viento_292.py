"""#292-W: efecto del viento B.6 sobre el diseño de los pórticos de concreto de zona sísmica baja del corpus F1.
Ver docs/memoria_calculo/PRERREGISTRO_292W_VIENTO_ZONA_BAJA.md.

Brazos por edificio (solo los 'edificios bajos' de B.6: h ≤ 18 m y h ≤ menor dimensión en planta):
  control: viento=None (con el margen u_max por defecto de #292-A, igual en todos los brazos);
  W28C:    V = 28 m/s, exposición C;
  W36D:    V = 36 m/s, exposición D (envolvente superior: región 5 y costa abierta).
Cubierta: la losa del corpus (D de entrepiso); la cubierta liviana NO se evalúa aquí.

Uso:  python -I scripts/memorias_sinteticas/viento_292.py [--piloto 6] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f1_292w/{brazos.csv, resultados_292w.json}
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
SEMILLA = 2921
BRAZOS = {"control": None, "W28C": (28.0, "C"), "W36D": (36.0, "D")}
CAMPOS = ["id", "brazo", "N", "h_m", "estado", "cumple", "fallas", "costo_cop", "firma", "E_base_max_kn", "W_base_max_kn",
          "qh_kpa", "segundos"]


def bajo(c: dict) -> bool:
    h = int(c["N"]) * float(c["hp_m"])
    return h <= 18.0 and h <= min(int(c["vanos_x"]) * float(c["Lx_m"]), int(c["vanos_y"]) * float(c["Ly_m"]))


def _firma(inf) -> str:
    """Refuerzo completo de vigas y columnas: dos diseños con la misma firma tienen el mismo armado."""
    partes = []
    for v in inf.vigas:
        d = v["diseno"]
        partes.append("V-" if d is None else f"V{v['nivel']}:{d.n_sup}/{d.n_inf}#{d.dia},e#{d.estribo_dia}@{d.s_conf:g}/{d.s_centro:g}")
    for c in inf.columnas:
        d = c["diseno"]
        partes.append("C-" if d is None else f"C{c['piso']}:{d.n_barras}#{d.dia},e#{d.estribo}@{d.s_conf:g}/{d.s_fuera:g}")
    return ";".join(partes)


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    t0 = time.time()
    p = f3._proyecto(de, t)
    if t["brazo"] != "control":
        v, e = BRAZOS[t["brazo"]]
        p = dataclasses.replace(p, viento=de.VientoB6(v_m_s=v, exposicion=e))
    fila = {"id": t["id"], "brazo": t["brazo"], "N": t["N"], "h_m": int(t["N"]) * float(t["hp_m"])}
    try:
        inf = de.disenar_edificio(p)
    except Exception as ex:                                            # noqa: BLE001
        return {**fila, "estado": f"error: {type(ex).__name__}: {ex}"[:200], "segundos": round(time.time() - t0, 1)}
    fila |= {"estado": "ok", "cumple": inf.cumple, "fallas": " | ".join(inf.fallas)[:300],
             "costo_cop": inf.cantidades["costo_cop"], "firma": _firma(inf),
             "E_base_max_kn": max(sum(inf.sismo[d]["E_kn"]) for d in ("x", "y"))}
    if t["brazo"] != "control":
        m = de.construir_modelo(p)
        casos, info = de._casos_viento(p, m)
        fila["W_base_max_kn"] = max(abs(sum(v[0] + v[1] for v in c.maestros.values())) for _n, c, _w in casos) if casos else 0.0
        fila["qh_kpa"] = info.get("qh_kpa", "")
    fila["segundos"] = round(time.time() - t0, 1)
    return fila


def _wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [math.nan, math.nan]
    z, ph = 1.959964, k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    w = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - w, c + w]


def resumir(filas: list[dict]) -> dict:
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_292W_VIENTO_ZONA_BAJA.md"}
    ctrl = por["control"]
    for b in ("W28C", "W36D"):
        ids = sorted(set(ctrl) & set(por[b]), key=int)
        ok = [i for i in ids if ctrl[i]["estado"] == "ok" and por[b][i]["estado"] == "ok"]
        cambia = [i for i in ok if por[b][i]["firma"] != ctrl[i]["firma"]]
        rompe = [i for i in ok if ctrl[i]["cumple"] == "True" and por[b][i]["cumple"] != "True"]
        n = len(ok)
        sc = np.array([float(por[b][i]["costo_cop"]) / float(ctrl[i]["costo_cop"]) - 1 for i in ok]) if n else np.array([0.0])
        w_sup = [i for i in ok if 1.6 * float(por[b][i]["W_base_max_kn"]) > float(ctrl[i]["E_base_max_kn"])]
        out[b] = {
            "n_pares": len(ids), "n_ok": n, "errores": [(i, por[b][i]["estado"]) for i in ids if i not in ok],
            "H-W1_frac_cambia_refuerzo": {"k": len(cambia), "frac": len(cambia) / max(1, n), "ic95": _wilson(len(cambia), n)},
            "H-W2_frac_1.6W_supera_E": {"k": len(w_sup), "frac": len(w_sup) / max(1, n), "ic95": _wilson(len(w_sup), n)},
            "C-W_sobrecosto": {"mediana": float(np.median(sc)), "p90": float(np.percentile(sc, 90)), "max": float(sc.max()),
                               "frac_sin_cambio": float((np.abs(sc) < 1e-9).mean())},
            "R-W_dejan_de_cumplir": {"k": len(rompe), "ids": rompe[:20]},
            "ids_cambian": cambia[:40],
        }
    w = out["W36D"]
    no_gobierna = (w["H-W1_frac_cambia_refuerzo"]["ic95"][1] <= 0.10 and w["R-W_dejan_de_cumplir"]["k"] == 0
                   and w["C-W_sobrecosto"]["p90"] <= 0.01)
    out["decision"] = ("El viento NO gobierna el pórtico de concreto con losa en zona baja (edificios bajos): queda opcional"
                       if no_gobierna else
                       "El viento SÍ cambia diseños en zona baja: evaluarlo por defecto (requiere V por municipio, issue aparte)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [r for r in csv.DictReader(f) if r["estado"] == "ok" and r["zona"] == "baja" and bajo(r)]
    print(f"{len(casos)} edificios bajos de zona baja", flush=True)
    if a.piloto:
        casos = casos[:a.piloto]
    trabajos = [{**c, "brazo": b} for c in casos for b in BRAZOS]
    out = RAIZ / "data" / "memorias_sinteticas" / "f1_292w" / ("piloto" if a.piloto else "")
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
                if k % 25 == 0 or a.piloto:
                    print(f"{k}/{len(pend)} en {time.time() - t0:.0f} s", flush=True)
                if a.hasta and time.strftime("%H:%M") >= a.hasta:
                    print("hora límite: se detiene (reanudable)", flush=True)
                    pool.terminate()
                    return
    with ruta.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    res = resumir(filas)
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_292w.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("decision",)} | {b: {kk: res[b][kk] for kk in ("n_ok", "H-W1_frac_cambia_refuerzo",
                     "H-W2_frac_1.6W_supera_E", "R-W_dejan_de_cumplir")} for b in ("W28C", "W36D")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
