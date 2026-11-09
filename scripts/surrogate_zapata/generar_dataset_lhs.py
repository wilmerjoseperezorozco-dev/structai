"""Dataset para el sustituto (surrogate) del diseño de zapata + pedestal: muestreo Latin Hypercube del espacio de diseño y etiqueta por el optimizador
determinista (NSR-10) de `packages/motor-concreto`. HIPÓTESIS de investigación: los rangos son supuestos del espacio de diseño colombiano, no estadística real.

Uso:  python scripts/surrogate_zapata/generar_dataset_lhs.py --n 20000 [--seed 20261108] [--salida data/surrogate_zapata/dataset.csv]
Reanuda: si el CSV existe, salta los `id` ya calculados (escribe cada fila al terminar).
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import qmc

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))

# nombre: (min, max, escala)  -- escala "log" o "lin"
ESPACIO = {
    "Pu": (300.0, 6000.0, "log"),        # kN, carga axial última en la base de la columna
    "ey_x": (0.0, 0.30, "lin"),          # m, Mux = Pu·ey_x (excentricidad que genera momento alrededor de x)
    "ex_y": (0.0, 0.30, "lin"),          # m, Muy = Pu·ex_y
    "q_adm": (100.0, 400.0, "lin"),      # kPa
    "ks": (8000.0, 60000.0, "lin"),      # kN/m3, módulo de balasto
    "fc": (21.0, 35.0, "lin"),           # MPa
    "u_exposicion": (0.0, 1.0, "lin"),   # <0.5 interior, <0.75 costa sin ensayo, resto costa con ensayo
    "Df": (1.0, 2.5, "lin"),             # m, profundidad de desplante
    "c_col": (300.0, 600.0, "lin"),      # mm, lado de la columna (se redondea a 50)
    "mult_concreto": (0.8, 1.3, "lin"),  # sobre el precio ancla APU Barranquilla
    "p_acero": (3500.0, 7000.0, "lin"),  # COP/kg
    "p_encofrado": (15000.0, 35000.0, "lin"),  # COP/m2
    "p_ceniza": (100.0, 350.0, "lin"),   # COP/kg
    "fe_cemento": (0.85, 1.10, "lin"),   # kgCO2e/kg
    "fe_acero": (0.85, 1.45, "lin"),     # kgCO2e/kg
    "lam_co2": (0.0, 400.0, "lin"),      # COP por kg CO2e (precio sombra del carbono)
}
NOMBRES = list(ESPACIO)
EXPOSICIONES = ("interior_C1_S0", "costa_C2_S1_sin_ensayo", "costa_C2_S1_con_ensayo")
SALIDAS = ["ok", "exposicion", "fc_eff", "x_ceniza", "tipo", "c_ped", "L", "h_c", "h_e", "h_p", "n_x", "dia_x", "n_y", "dia_y", "ped_barras", "ped_As", "ped_util",
           "ped_Avf", "costo_cop", "co2_kg", "q_max", "segundos", "motivo"]


def muestrear(n: int, seed: int) -> list[dict]:
    u = qmc.LatinHypercube(d=len(NOMBRES), seed=seed).random(n)
    filas = []
    for i in range(n):
        f = {"id": i}
        for j, nom in enumerate(NOMBRES):
            lo, hi, esc = ESPACIO[nom]
            f[nom] = float(math.exp(math.log(lo) + u[i, j] * (math.log(hi) - math.log(lo)))) if esc == "log" else float(lo + u[i, j] * (hi - lo))
        f["c_col"] = float(round(f["c_col"] / 50) * 50)
        f["exposicion"] = EXPOSICIONES[0 if f["u_exposicion"] < 0.5 else 1 if f["u_exposicion"] < 0.75 else 2]
        filas.append(f)
    return filas


def _parsear(barras: str) -> tuple[int, str]:
    m = re.match(r"(\d+)#(\d)", barras)
    return (int(m.group(1)), m.group(2)) if m else (0, "")


def calcular(f: dict) -> dict:
    from src import zapata as z
    from src.diseno_zapata_pedestal import optimizar_conjunto
    from src.economia_concreto import Economia

    t0 = time.time()
    Pu = f["Pu"]
    eco = Economia(mult_concreto=f["mult_concreto"], p_acero=f["p_acero"], p_encofrado=f["p_encofrado"], p_ceniza=f["p_ceniza"],
                   fe_cemento=f["fe_cemento"], fe_acero=f["fe_acero"], lam_co2=f["lam_co2"])
    cargas = z.CargasZapata(P_serv=Pu / 1.35, P_u=Pu)
    suelo = z.Suelo(q_adm_kpa=f["q_adm"], profundidad_desplante_m=f["Df"], ks_kn_m3=f["ks"])
    out = {"id": f["id"]}
    try:
        d = optimizar_conjunto(f["c_col"], cargas, suelo, exposicion=f["exposicion"], objetivo="mixto", fc=f["fc"], economia=eco,
                               momentos_columna=(Pu * f["ey_x"], Pu * f["ex_y"]))
    except Exception as e:  # noqa: BLE001 - se registra, no se oculta
        return out | {"ok": 0, "motivo": f"excepción: {type(e).__name__}: {e}"[:200], "segundos": round(time.time() - t0, 2)}
    if d is None:
        return out | {"ok": 0, "motivo": "sin solución", "segundos": round(time.time() - t0, 2)}
    zz, p = d.zapata, d.pedestal
    nx, dx = _parsear(zz.barras_x)
    ny, dy = _parsear(zz.barras_y)
    return out | {"ok": 1, "exposicion": d.exposicion, "fc_eff": d.fc, "x_ceniza": d.x_ceniza, "tipo": d.tipo, "c_ped": p.c_mm, "L": zz.L_mm, "h_c": zz.h_c_mm,
                  "h_e": zz.h_e_mm, "h_p": d.h_pedestal_mm, "n_x": nx, "dia_x": dx, "n_y": ny, "dia_y": dy, "ped_barras": p.barras, "ped_As": round(p.As_mm2, 1),
                  "ped_util": round(p.utilizacion_flexion, 3), "ped_Avf": round(p.Avf_mm2, 1), "costo_cop": round(d.costo_cop), "co2_kg": round(d.co2_kg, 2),
                  "q_max": round(zz.q_max_kpa, 1), "segundos": round(time.time() - t0, 2), "motivo": ""}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261108)
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_zapata" / "dataset.csv"))
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args()
    ruta = Path(args.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    muestras = muestrear(args.n, args.seed)
    cols = ["id"] + NOMBRES + ["exposicion_in"] + SALIDAS
    hechos: set[int] = set()
    if ruta.exists():
        with ruta.open(encoding="utf-8", newline="") as fh:
            hechos = {int(r["id"]) for r in csv.DictReader(fh)}
    pend = [m for m in muestras if m["id"] not in hechos]
    print(f"{len(muestras)} muestras, {len(hechos)} ya calculadas, {len(pend)} pendientes", flush=True)
    nuevo = not ruta.exists()
    t0, k = time.time(), 0
    with ruta.open("a", encoding="utf-8", newline="") as fh, Pool(args.procesos) as pool:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        if nuevo:
            w.writeheader()
        por_id = {m["id"]: m for m in muestras}
        for r in pool.imap_unordered(calcular, pend, chunksize=8):
            m = por_id[r["id"]]
            w.writerow({**m, "exposicion_in": m["exposicion"], **{k2: v for k2, v in r.items() if k2 != "exposicion"}, **({"exposicion": r.get("exposicion", "")})})
            k += 1
            if k % 200 == 0:
                fh.flush()
                print(f"{k}/{len(pend)}  {time.time() - t0:.0f}s  ({(time.time() - t0) / k:.2f}s por caso efectivo)", flush=True)
    print("listo", flush=True)
