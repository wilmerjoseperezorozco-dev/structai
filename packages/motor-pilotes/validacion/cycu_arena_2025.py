"""Validación de motor-pilotes en suelo granular (SPT del CCP-14) contra la CYCU pile load test database (#118).

Prerregistro: issue #118 (comentario de prerregistro de arena, publicado antes de correr el modo completo).
Datos: Chen, Y.-J., Topacio, A., Laveti, S., Jos, M. A., Hsiao, M.-H. (2025). CYCU pile load test database. Mendeley Data,
V1, doi:10.17632/x6c63j8bv8.1. Licencia CC BY 4.0. El Excel no se versiona: vive en _privado/.

Muestra: pruebas a compresión en las mismas tres hojas que la validación de arcilla, con USCS solo granular (todas las
componentes empiezan por S o G), SPT-N > 0, σ'v > 0, el estrato representativo en la punta (profundidad del SPT a
±10 % de L) y L > B > 0. En pilas excavadas se excluye N > 50 (geomaterial intermedio, fuera del método).

  predicho = q_ult de src.arena_spt con un estrato homogéneo: N60 = SPT-N reportado y γ' = σ'v(punta)/L, sin nivel
             freático (así σ'v crece lineal y cierra en el valor de la base). Grava si la primera componente USCS es G.
             Hincados: Meyerhof (10.7.3.8.6g). Excavados: β y 0.057·N60 (10.8.3.5.2).
  medido   = L2 en excavadas; Davisson en hincados (las mismas columnas que cycu_2025.py)
  λ        = medido / predicho

Uso (desde packages/motor-pilotes, con python -I):
  python validacion/cycu_arena_2025.py <cycu.xlsx> --conteo   # solo cuenta la muestra; no lee capacidades
  python validacion/cycu_arena_2025.py <cycu.xlsx>            # análisis completo prerregistrado
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

from cycu_2025 import (FILA_INICIO, HOJAS, SEMILLA, _boot_cluster, _columnas_por_nombre, _num, cov, gm,  # noqa: E402
                       veredicto)
from src.arena_spt import EstratoSPT, capacidad_spt  # noqa: E402
from src.axial import Pilote  # noqa: E402

SPT = {"Drilled Shaft-Compression": dict(sv=21, n=29, zspt=28),
       "Driven Piles-Round-Compression": dict(sv=15, n=24, zspt=23),
       "Driven Piles-Square-Compression": dict(sv=20, n=29, zspt=28)}


def componentes(uscs) -> list[str]:
    return [p.strip() for p in str(uscs or "").replace("/", "-").split("-") if p.strip()]


def es_granular(uscs) -> bool:
    partes = componentes(uscs)
    return bool(partes) and all(p[0] in "SG" for p in partes)


def leer(ruta: Path) -> tuple[list[dict], Counter]:
    import openpyxl
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    filas, excl = [], Counter()
    for hoja, c0 in HOJAS.items():
        ws = wb[hoja]
        c = {**c0, **SPT[hoja]}
        if c["medido"] is None:
            c["medido"] = _columnas_por_nombre(ws, "Davisson")[0]
            c["alterno"] = [j for j in _columnas_por_nombre(ws, "Terzaghi") if j > 0][0]
        uscs_previo, ref_previa = None, None
        for r in ws.iter_rows(min_row=FILA_INICIO + 1, values_only=True):
            if not r or r[0] in (None, ""):
                continue
            ref = str(r[0]).rsplit("-", 1)[0]
            uscs = r[c["uscs"]]
            if uscs in (None, "") and ref == ref_previa:
                uscs = uscs_previo
            uscs_previo, ref_previa = uscs, ref
            f = {"hoja": hoja, "id": str(r[0]), "referencia": ref, "tipo": c["tipo"], "seccion": c["seccion"],
                 "uscs": uscs, "n": _num(r[c["n"]]), "sv": _num(r[c["sv"]]), "zspt": _num(r[c["zspt"]]),
                 "L": _num(r[c["L"]]), "B": _num(r[c["B"]]), "_r": r, "_c": c}
            if not es_granular(uscs):
                excl["no es granular (USCS)"] += 1
            elif not (f["n"] and f["n"] > 0):
                excl["sin SPT-N"] += 1
            elif not (f["sv"] and f["sv"] > 0):
                excl["sin σ'v"] += 1
            elif not (f["L"] and f["B"] and f["L"] > f["B"] > 0):
                excl["geometría incompleta"] += 1
            elif not (f["zspt"] and abs(f["zspt"] - f["L"]) <= 0.10 * f["L"]):
                excl["estrato representativo lejos de la punta"] += 1
            elif f["tipo"] == "excavado" and f["n"] > 50:
                excl["excavada con N > 50 (geomaterial intermedio)"] += 1
            else:
                f["suelo"] = "grava" if componentes(uscs)[0][0] == "G" else "arena"
                filas.append(f)
    return filas, excl


def con_capacidad(filas: list[dict], excl: Counter) -> list[dict]:
    out = []
    for f in filas:
        r, c = f.pop("_r"), f.pop("_c")
        med, qmax, alt = _num(r[c["medido"]]), _num(r[c["qmax"]]), _num(r[c["alterno"]])
        if not (med and med > 0):
            excl["sin capacidad interpretada"] += 1
            continue
        if qmax and med > qmax * 1.0001:
            excl["capacidad extrapolada (Qm > Qmax)"] += 1
            continue
        pil = Pilote(seccion=f["seccion"], ancho_m=f["B"], longitud_m=f["L"], tipo=f["tipo"])
        est = [EstratoSPT(espesor_m=f["L"] + 10 * f["B"], gamma_kn_m3=f["sv"] / f["L"], n60=f["n"], suelo=f["suelo"])]
        p = capacidad_spt(est, pil, nivel_freatico_m=None, combinacion="cm_cv_normal")
        f.update(medido_kn=med, alterno_kn=alt if (alt and (not qmax or alt <= qmax * 1.0001)) else None,
                 pred_kn=p["q_ult_kn"], lam=med / p["q_ult_kn"], frac_punta=p["qp_ult_kn"] / p["q_ult_kn"])
        out.append(f)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--conteo", action="store_true")
    a = ap.parse_args()
    filas, excl = leer(a.xlsx)
    if a.conteo:
        print(f"Candidatas (antes de leer capacidades): {len(filas)}")
        print("  por tipo:", dict(Counter(f["tipo"] for f in filas)))
        print("  por hoja:", dict(Counter(f["hoja"] for f in filas)))
        print("  por suelo:", dict(Counter(f["suelo"] for f in filas)))
        print("  referencias (sitios) distintas:", len({f['referencia'] for f in filas}))
        print("  sitios por tipo:", {t: len({f['referencia'] for f in filas if f['tipo'] == t})
                                      for t in ("excavado", "hincado")})
        print("  exclusiones:", dict(excl))
        return
    filas = con_capacidad(filas, excl)
    rng = random.Random(SEMILLA)
    print(f"n = {len(filas)} pruebas en {len({f['referencia'] for f in filas})} referencias; exclusiones: {dict(excl)}\n")
    print("| Grupo | n | sitios | λ media geométrica | IC95 (bootstrap por sitio) | COV de λ | Veredicto |")
    print("|---|---|---|---|---|---|---|")
    grupos = {"Todas": filas, "Excavadas, β (L2)": [f for f in filas if f["tipo"] == "excavado"],
              "Hincadas, Meyerhof (Davisson)": [f for f in filas if f["tipo"] == "hincado"]}
    for nombre, g in grupos.items():
        if len(g) < 3:
            print(f"| {nombre} | {len(g)} | — | — | — | — | n insuficiente |")
            continue
        lo, hi = _boot_cluster(g, gm, rng)
        print(f"| {nombre} | {len(g)} | {len({f['referencia'] for f in g})} | {gm(g):.3f} | [{lo:.3f}, {hi:.3f}] | "
              f"{cov(g):.2f} | {veredicto(lo, hi)} |")
    alt = [f for f in filas if f["alterno_kn"]]
    if alt:
        print(f"\nSensibilidad al criterio de falla (Terzaghi y Peck, n = {len(alt)}): λ media geométrica "
              f"{math.exp(sum(math.log(f['alterno_kn'] / f['pred_kn']) for f in alt) / len(alt)):.3f}")
    for nombre, g in grupos.items():
        if len(g) >= 3:
            lams = sorted(f["lam"] for f in g)
            print(f"{nombre}: p10 {lams[len(lams) // 10]:.2f}, p50 {lams[len(lams) // 2]:.2f}, "
                  f"p90 {lams[9 * len(lams) // 10]:.2f}; fracción con λ < 1: {sum(x < 1 for x in lams) / len(lams):.2f}; "
                  f"fracción media de punta en el predicho: {sum(f['frac_punta'] for f in g) / len(g):.2f}")


if __name__ == "__main__":
    main()
