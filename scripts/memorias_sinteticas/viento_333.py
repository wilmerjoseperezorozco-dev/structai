"""#333: H8 y H7 de Wilmer (transición de cimentación). Prerregistro en docs/memoria_calculo/PRERREGISTRO_333_H7_H8.md.

H8: con q_adm = 200 kPa, ¿todo edificio con alguna zapata que no cabe tiene N ≥ 11 o P_serv,máx > 3.500 kN?
    Población: los 11 del grupo falla de #324, diseño W36D (primario) y sin_viento (sensibilidad).
H7: en 1290, 1729 y 1762 (resueltos con viga peraltada), diseño del optimizador con W36D (viga) frente a la alternativa
    "solo columna": optimizador con W36D y h de viga fija en la del diseño sin viento. Momento de servicio en la base de
    las columnas exteriores y zapatas que no caben con 200 kPa.

Uso:  python -I scripts/memorias_sinteticas/viento_333.py [--hilos 6]
Salida: data/memorias_sinteticas/f1_333/{crudo.json, resultados_333.json}
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
Q = 200.0                                  # kPa, estrato medio (primario de #324-C)
N_UMBRAL, P_UMBRAL_KN = 11, 3500.0         # regla de Wilmer (H8)
VIGA = ("1290", "1729", "1762")            # #324: resueltos con viga peraltada


def _metricas(ci, p) -> dict:
    """P de servicio máxima, momentos de servicio en la base de columnas exteriores y zapatas con 200 kPa."""
    nodos, r = reac = ci.reacciones_por_caso(p)
    combs = ci.combinaciones(list(r))
    xs = [n["x"] for n in nodos]
    ys = [n["y"] for n in nodos]
    ext = [n["k"] for n in nodos if n["x"] in (min(xs), max(xs)) or n["y"] in (min(ys), max(ys))]
    p_max, m_w, m_todas = 0.0, {}, {}
    for nd in nodos:
        k = nd["k"]
        for nom, cs, _cu in combs:
            s = ci._comb(r, cs, k)
            p_max = max(p_max, float(s[0]))
            if k in ext:
                m = float(math.hypot(s[1], s[2]))
                m_todas[k] = max(m_todas.get(k, 0.0), m)
                if "W[" in nom:
                    m_w[k] = max(m_w.get(k, 0.0), m)
    z = ci.disenar_zapatas(p, Q, reac=reac)
    return {"P_serv_max_kn": p_max, "no_caben": z.no_caben, "n_zapatas": len(z.zapatas), "sin_solucion": z.sin_solucion,
            "costo_cim_cop": z.costo_cop, "L_max_mm": max((x.L_mm for x in z.zapatas if x.cumple), default=math.nan),
            "M_ext_W_max_knm": max(m_w.values(), default=math.nan),
            "M_ext_W_mediana_knm": float(np.median(list(m_w.values()))) if m_w else math.nan,
            "M_ext_todas_max_knm": max(m_todas.values(), default=math.nan),
            "M_ext_todas_mediana_knm": float(np.median(list(m_todas.values()))) if m_todas else math.nan,
            "n_exteriores": len(ext)}


def evaluar(t: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import cimentacion_edificio_3d as ci, diseno_edificio_3d as de, optimizar_edificio_3d as op
    t0 = time.time()
    c = t["c"]
    base = f3._proyecto(de, c)
    w = de.VientoB6(v_m_s=36.0, exposicion="D")
    out = {"id": c["id"], "N": int(c["N"]), "tarea": t["tarea"]}
    if t["tarea"] == "solo_columna":
        r = op.optimizar(dataclasses.replace(base, viento=w), alturas_viga=(float(t["h_fija"]),))
        out["h_fija_mm"] = t["h_fija"]
        if r.mejor is None:
            out["encontrado"] = False
            out["motivo"] = r.motivo_sin_solucion
        else:
            p = r.mejor.proyecto
            out |= {"encontrado": True, "c_inferior_mm": p.columnas_mm[0], "c_superior_mm": p.columnas_mm[-1],
                    "h_viga_mm": p.vigas_mm[0][1], "costo_super_cop": r.mejor.cantidades["costo_cop"]}
            out |= _metricas(ci, p)
    else:                                   # "W36D" o "sin_viento": secciones de #324
        f = t["fila"]
        n = int(c["N"])
        ci_, cs_, h = float(f["c_inferior_mm"]), float(f["c_superior_mm"]), float(f["h_viga_mm"])
        cols, vigas = op._secciones(n, ci_, ci_ - cs_, h)
        p = dataclasses.replace(base, columnas_mm=cols, vigas_mm=vigas)
        if t["tarea"] == "W36D":
            p = dataclasses.replace(p, viento=w)
        out |= {"encontrado": True, "c_inferior_mm": ci_, "c_superior_mm": cs_, "h_viga_mm": h,
                "costo_super_cop": float(f["costo_cop"])}
        out |= _metricas(ci, p)
    out["segundos"] = round(time.time() - t0, 1)
    return out


def _h8(filas: list[dict]) -> dict:
    regla = lambda f: f["N"] >= N_UMBRAL or f["P_serv_max_kn"] > P_UMBRAL_KN  # noqa: E731
    no_caben = [f for f in filas if f["no_caben"] > 0]
    caben = [f for f in filas if f["no_caben"] == 0]
    # umbral de P que mejor separaría (POST HOC, solo descriptivo)
    ps = sorted({f["P_serv_max_kn"] for f in filas})
    mejor = None
    for u in ps:
        aciertos = sum((f["P_serv_max_kn"] >= u) == (f["no_caben"] > 0) for f in filas)
        if mejor is None or aciertos > mejor[1]:
            mejor = (u, aciertos)
    return {"edificios_no_caben": [f["id"] for f in no_caben],
            "implicacion_cumple": sum(regla(f) for f in no_caben), "implicacion_de": len(no_caben),
            "veredicto_implicacion": ("se cumple" if no_caben and all(regla(f) for f in no_caben)
                                      else ("vacía" if not no_caben else "refutada")),
            "reciproca_regla_y_caben": [f["id"] for f in caben if regla(f)],
            "solo_N": {"no_caben_con_N_ge_11": sum(f["N"] >= N_UMBRAL for f in no_caben),
                       "caben_con_N_ge_11": sum(f["N"] >= N_UMBRAL for f in caben)},
            "umbral_P_post_hoc_kn": {"u": mejor[0], "aciertos": mejor[1], "de": len(filas)} if mejor else None,
            "tabla": [{k: f[k] for k in ("id", "N", "P_serv_max_kn", "no_caben", "n_zapatas", "L_max_mm")} for f in filas]}


def resumir(res: list[dict]) -> dict:
    por = {(r["id"], r["tarea"]): r for r in res}
    ids = sorted({r["id"] for r in res if r["tarea"] == "W36D"}, key=int)
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_333_H7_H8.md", "q_adm_kpa": Q,
           "errores": [r["id"] + "/" + r["tarea"] for r in res if "error" in r],
           "H8_W36D": _h8([por[(i, "W36D")] for i in ids]),
           "H8_sin_viento": _h8([por[(i, "sin_viento")] for i in ids])}
    h7 = []
    for i in VIGA:
        v, c = por[(i, "W36D")], por[(i, "solo_columna")]
        fila = {"id": i, "viga": {k: v[k] for k in ("c_inferior_mm", "c_superior_mm", "h_viga_mm", "costo_super_cop",
                                                     "M_ext_W_max_knm", "M_ext_W_mediana_knm", "no_caben")},
                "solo_columna_encontrado": c["encontrado"]}
        if c["encontrado"]:
            fila["solo_columna"] = {k: c[k] for k in ("c_inferior_mm", "c_superior_mm", "h_viga_mm", "costo_super_cop",
                                                      "M_ext_W_max_knm", "M_ext_W_mediana_knm", "no_caben")}
            fila["momento_menor_con_viga"] = v["M_ext_W_max_knm"] < c["M_ext_W_max_knm"]
            fila["evita_traslape"] = v["no_caben"] == 0 and c["no_caben"] > 0
            fila["traslape_en_alguno"] = v["no_caben"] > 0 or c["no_caben"] > 0
        h7.append(fila)
    ok = [f for f in h7 if f["solo_columna_encontrado"]]
    k_evita = sum(f["evita_traslape"] and f["momento_menor_con_viga"] for f in ok)
    alguno = any(f["traslape_en_alguno"] for f in ok)
    out["H7"] = {"filas": h7, "k_momento_menor": sum(f["momento_menor_con_viga"] for f in ok),
                 "k_evita_traslape_y_momento_menor": k_evita, "de": len(ok),
                 "veredicto": ("inconclusa (ninguno tiene traslape en ningún diseño)" if not alguno
                               else ("se cumple" if k_evita >= 2 else "refutada"))}
    return out


def _seguro(t):
    try:
        return evaluar(t)
    except Exception as e:  # noqa: BLE001 — se reporta por id
        return {"id": t["c"]["id"], "tarea": t["tarea"], "error": repr(e), "segundos": 0}


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
    trabajos = [{"c": corpus[i], "fila": fila, "tarea": b} for (i, b), fila in secc.items()]
    trabajos += [{"c": corpus[i], "tarea": "solo_columna", "h_fija": secc[(i, "sin_viento")]["h_viga_mm"]} for i in VIGA]
    print(f"{len(trabajos)} trabajos", flush=True)
    t0 = time.time()
    with Pool(a.hilos) as pool:
        res = []
        for k, r in enumerate(pool.imap_unordered(_seguro, trabajos), 1):
            res.append(r)
            print(f"{k}/{len(trabajos)} {r['id']} {r['tarea']} {r['segundos']} s {r.get('error', '')}", flush=True)
    out = d / "f1_333"
    out.mkdir(parents=True, exist_ok=True)
    (out / "crudo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    s = resumir(res)
    s["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_333.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, default=str)[:5000])


if __name__ == "__main__":
    main()
