"""#242: viento B.6 (método general, cualquier altura) sobre los pórticos de concreto de zona sísmica baja del corpus F1
que NO son 'edificios bajos' (h > 18 m o h > menor dimensión en planta). Ver docs/memoria_calculo/PRERREGISTRO_242_VIENTO_ALTURA.md.

Brazos por edificio: control (sin viento), W28C y W36D, como en #292-W. n1 = 1/T_modelo por dirección (Gf si n1 < 1 Hz,
β = 0,02 declarado). Además, en los brazos de viento: razón 1,6W/E por dirección y deriva de viento en servicio (1,0W
lateral, centro del diafragma) frente a h_piso/400 (criterio declarado, no NSR-10).

Uso:  python -I scripts/memorias_sinteticas/viento_242.py [--piloto 2] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f1_242/{brazos.csv, resultados_242.json}
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
SEMILLA = 2421
BRAZOS = {"control": None, "W28C": (28.0, "C"), "W36D": (36.0, "D")}
CAMPOS = ["id", "brazo", "N", "h_m", "estado", "cumple", "fallas", "costo_cop", "firma", "firma_vigas", "firma_columnas",
          "E_base_max_kn", "W_base_max_kn", "qh_kpa", "T_x_s", "T_y_s", "E_x_kn", "E_y_kn", "W_x_kn", "W_y_kn", "rho_x", "rho_y",
          "G_x", "G_y", "rafaga_x", "rafaga_y", "uso_deriva_sismo", "tercio_deriva_sismo", "uso_deriva_viento",
          "tercio_deriva_viento", "segundos"]
DERIVA_VIENTO = 1 / 400                                                # criterio DECLARADO (no NSR-10)


def bajo(c: dict) -> bool:
    h = int(c["N"]) * float(c["hp_m"])
    return h <= 18.0 and h <= min(int(c["vanos_x"]) * float(c["Lx_m"]), int(c["vanos_y"]) * float(c["Ly_m"]))


def _tercio(i: int, n: int) -> str:
    return ("inferior", "medio", "superior")[min(2, 3 * i // n)]


def _firma(inf, que: str = "todo") -> str:
    """Refuerzo completo de vigas y columnas: dos diseños con la misma firma tienen el mismo armado."""
    partes = []
    for v in inf.vigas:
        d = v["diseno"]
        if que == "columnas":
            continue
        partes.append("V-" if d is None else f"V{v['nivel']}:{d.n_sup}/{d.n_inf}#{d.dia},e#{d.estribo_dia}@{d.s_conf:g}/{d.s_centro:g}")
    for c in inf.columnas:
        d = c["diseno"]
        if que == "vigas":
            continue
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
             "costo_cop": inf.cantidades["costo_cop"], "firma": _firma(inf), "firma_vigas": _firma(inf, "vigas"),
             "firma_columnas": _firma(inf, "columnas"),
             "E_base_max_kn": max(sum(inf.sismo[d]["E_kn"]) for d in ("x", "y")),
             "T_x_s": inf.sismo["x"]["T_modelo_s"], "T_y_s": inf.sismo["y"]["T_modelo_s"],
             "E_x_kn": sum(inf.sismo["x"]["E_kn"]), "E_y_kn": sum(inf.sismo["y"]["E_kn"])}
    pp = inf.deriva["por_piso"]
    k = max(range(len(pp)), key=lambda i: pp[i]["uso"])
    fila |= {"uso_deriva_sismo": inf.deriva["uso_max"], "tercio_deriva_sismo": _tercio(k, len(pp))}
    if t["brazo"] != "control":
        vw = inf.viento
        if not vw.get("evaluado"):
            return {**fila, "estado": f"error: viento no evaluado: {vw.get('motivo')}"[:200]}
        fila |= {"W_base_max_kn": max(vw["cortante_basal_kn"].values()), "qh_kpa": vw["qh_kpa"],
                 "W_x_kn": vw["cortante_basal_kn"]["x"], "W_y_kn": vw["cortante_basal_kn"]["y"],
                 "G_x": vw["G"]["x"], "G_y": vw["G"]["y"], "rafaga_x": vw["rafaga"]["x"], "rafaga_y": vw["rafaga"]["y"]}
        fila["rho_x"], fila["rho_y"] = 1.6 * fila["W_x_kn"] / fila["E_x_kn"], 1.6 * fila["W_y_kn"] / fila["E_y_kn"]
        # deriva en servicio: 1,0W lateral solo (sin cubierta), desplazamiento del centro del diafragma
        m = de.construir_modelo(p)
        n, mejor = len(p.alturas_piso_m), (0.0, 0)
        for j, d in ((0, "x"), (1, "y")):
            f = vw["fuerzas_kn"][d]
            maes = {f"P{i}": ((f[i - 1], 0.0, 0.0) if d == "x" else (0.0, f[i - 1], 0.0)) for i in range(1, n + 1)}
            r = m.portico.resolver(de._p3.Caso3D(f"Wserv{d}", maestros=maes))
            u = [0.0] + [r.maestros[f"P{i}"][j] for i in range(1, n + 1)]
            for i in range(n):
                uso = abs(u[i + 1] - u[i]) / p.alturas_piso_m[i] / DERIVA_VIENTO
                if uso > mejor[0]:
                    mejor = (uso, i)
        fila |= {"uso_deriva_viento": mejor[0], "tercio_deriva_viento": _tercio(mejor[1], n)}
    fila["segundos"] = round(time.time() - t0, 1)
    return fila


def _wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [math.nan, math.nan]
    z, ph = 1.959964, k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    w = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - w, c + w]


def _boot_ic(x, y, f, n=2000):
    rng = np.random.default_rng(SEMILLA)
    x, y = np.asarray(x), np.asarray(y)
    v = []
    for _ in range(n):
        k = rng.integers(0, len(x), len(x))
        v.append(f(x[k], y[k]))
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def _spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def _pendiente_loglog(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


def resumir(filas: list[dict]) -> dict:
    por = {b: {f["id"]: f for f in filas if f["brazo"] == b} for b in BRAZOS}
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_242_VIENTO_ALTURA.md"}
    ctrl = por["control"]
    for b in ("W28C", "W36D"):
        ids = sorted(set(ctrl) & set(por[b]), key=int)
        ok = [i for i in ids if ctrl[i]["estado"] == "ok" and por[b][i]["estado"] == "ok"]
        n = len(ok)
        cambia = [i for i in ok if por[b][i]["firma"] != ctrl[i]["firma"]]
        cv = [i for i in ok if por[b][i]["firma_vigas"] != ctrl[i]["firma_vigas"]]
        cc = [i for i in ok if por[b][i]["firma_columnas"] != ctrl[i]["firma_columnas"]]
        rompe = [i for i in ok if ctrl[i]["cumple"] == "True" and por[b][i]["cumple"] != "True"]
        sc = np.array([float(por[b][i]["costo_cop"]) / float(ctrl[i]["costo_cop"]) - 1 for i in ok]) if n else np.array([0.0])
        h = np.array([float(por[b][i]["h_m"]) for i in ok])
        rho = np.array([max(float(por[b][i]["rho_x"]), float(por[b][i]["rho_y"])) for i in ok])
        tmax = np.array([max(float(por[b][i]["T_x_s"]), float(por[b][i]["T_y_s"])) for i in ok])
        uw = np.array([float(por[b][i]["uso_deriva_viento"]) for i in ok])
        us = np.array([float(por[b][i]["uso_deriva_sismo"]) for i in ok])
        fl = tmax > 1.5
        k3 = int(((uw > us) & fl).sum())
        sup = [por[b][i]["tercio_deriva_viento"] for i, f_ in zip(ok, fl) if f_]
        pend = _pendiente_loglog(h, rho)
        a0 = float(np.polyfit(np.log(h), np.log(rho), 1)[1])
        out[b] = {
            "n_pares": len(ids), "n_ok": n, "errores": [(i, por[b][i]["estado"]) for i in ids if i not in ok],
            "H-A1_frac_cambia_refuerzo": {"k": len(cambia), "frac": len(cambia) / max(1, n), "ic95": _wilson(len(cambia), n)},
            "H-A1b_vigas": {"k": len(cv), "ic95": _wilson(len(cv), n)}, "H-A1b_columnas": {"k": len(cc), "ic95": _wilson(len(cc), n)},
            "C-A_sobrecosto": {"mediana": float(np.median(sc)), "p90": float(np.percentile(sc, 90)), "max": float(sc.max())},
            "R-A_dejan_de_cumplir": {"k": len(rompe), "ids": rompe[:20]},
            "H-A2_rho": {"min": float(rho.min()), "mediana": float(np.median(rho)), "max": float(rho.max()),
                         "k_rho>1": int((rho > 1).sum()), "ic95_rho>1": _wilson(int((rho > 1).sum()), n),
                         "spearman_h_rho": _spearman(h, rho), "ic95_spearman": _boot_ic(h, rho, _spearman),
                         "pendiente_loglog": pend, "ic95_pendiente": _boot_ic(h, rho, _pendiente_loglog),
                         "H*_m_ajuste_mediano": float(math.exp(-a0 / pend)) if pend > 0 else math.inf},
            "H-A3_deriva": {"n_T>1.5": int(fl.sum()), "k_viento>sismo": k3, "frac": k3 / max(1, int(fl.sum())),
                            "ic95": _wilson(k3, int(fl.sum())), "uso_viento_max": float(uw.max()),
                            "uso_viento_mediana": float(np.median(uw)), "uso_sismo_mediana": float(np.median(us)),
                            "k_viento>sismo_todos": int((uw > us).sum()),
                            "tercio_max_viento_T>1.5": {t: sup.count(t) for t in ("inferior", "medio", "superior")}},
            "G_flexibles": int(sum(por[b][i]["rafaga_x"] == "flexible" or por[b][i]["rafaga_y"] == "flexible" for i in ok)),
            "ids_cambian": cambia[:40],
        }
    a, c = por["W28C"], por["W36D"]
    com = [i for i in a if i in c and a[i]["estado"] == "ok" and c[i]["estado"] == "ok"]
    rv = np.array([max(float(c[i]["rho_x"]), float(c[i]["rho_y"])) / max(float(a[i]["rho_x"]), float(a[i]["rho_y"])) for i in com])
    out["H-A2b_razon_rho_W36D_W28C"] = {"mediana": float(np.median(rv)), "min": float(rv.min()), "max": float(rv.max())}
    w = out["W36D"]
    no_gobierna = (w["H-A1_frac_cambia_refuerzo"]["ic95"][1] <= 0.10 and w["R-A_dejan_de_cumplir"]["k"] == 0
                   and w["C-A_sobrecosto"]["p90"] <= 0.01)
    out["decision"] = ("El viento NO gobierna el pórtico de concreto con losa en zona baja hasta la altura del corpus: queda opcional"
                       if no_gobierna else
                       "El viento SÍ cambia diseños de edificios altos en zona baja: evaluarlo por defecto (requiere V por municipio)")
    ic = w["H-A3_deriva"]["ic95"]
    out["H-A3_veredicto"] = ("CONFIRMADA (viento gobierna deriva con T > 1,5 s)" if ic[0] > 0.5 else
                             "REFUTADA" if ic[1] < 0.5 else "NO CONCLUYENTE")
    # H-A4 (cubierta liviana) se mueve con el módulo cubierta_liviana a su propio PR, mientras se valida:
    # ver scripts/memorias_sinteticas/viento_242_ha4.py en esa rama. Sus resultados ya medidos siguen en RESULTADOS_242.
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [r for r in csv.DictReader(f) if r["estado"] == "ok" and r["zona"] == "baja" and not bajo(r)]
    print(f"{len(casos)} edificios de zona baja que no son 'edificios bajos'", flush=True)
    if a.piloto:
        casos = casos[:a.piloto]
    trabajos = [{**c, "brazo": b} for c in casos for b in BRAZOS]
    out = RAIZ / "data" / "memorias_sinteticas" / "f1_242" / ("piloto" if a.piloto else "")
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
    (out / "resultados_242.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("decision", "H-A3_veredicto")} | {b: {kk: res[b][kk] for kk in ("n_ok",
                     "H-A1_frac_cambia_refuerzo", "R-A_dejan_de_cumplir", "H-A2_rho")} for b in ("W28C", "W36D")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
