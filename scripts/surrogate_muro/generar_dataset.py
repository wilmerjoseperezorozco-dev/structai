"""Dataset para el sustituto del diseño de muros de contención en voladizo (tres tipologías): muestreo del espacio de diseño y etiqueta por el optimizador de referencia.

Muestreo: secuencia de Sobol con scramble (no LHS): un prefijo de potencia de 2 de Sobol sigue bien distribuido, de modo que 4096 → 8192 es una extensión válida,
mientras que un subconjunto de un LHS no es un LHS. El peso unitario del relleno se correlaciona con φ (HIPÓTESIS ρ = 0,6, cópula gaussiana). Todos los rangos son
SUPUESTOS del espacio de diseño colombiano; ver `MANIFIESTO` que se escribe junto al CSV.

Uso:  python scripts/surrogate_muro/generar_dataset.py --m 12 [--salida data/surrogate_muro/dataset.csv]     (n = 2**m casos; reanudable)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm, qmc

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))

RANGOS = {"H": (1.5, 8.0), "phi": (24.0, 40.0), "gamma": (16.0, 21.0), "q_adm": (80.0, 350.0), "q_s": (0.0, 20.0), "beta": (0.0, 20.0), "a_max": (0.05, 0.40),
          "mult_concreto": (0.8, 1.3), "p_acero": (3500.0, 7000.0)}
RHO_GAMMA_PHI = 0.6
ESCENARIOS_CO2 = {"bajo": (0.892, 1.00), "base": (1.010, 1.322), "alto": (1.15, 1.80)}      # (fe_cemento, fe_acero) kgCO2e/kg; "bajo" y "alto" son SUPUESTOS
NOMBRES = ["H", "phi", "gamma", "q_adm", "q_s", "beta", "a_max", "mult_concreto", "p_acero", "escenario_co2"]
TIPOS = ("tradicional", "estandar", "dentellon", "bandeja")
CAMPOS_SOL = ["ok", "obj", "costo", "co2", "perfil", "h_zapata", "t_corona", "t_base", "b_puntera", "b_talon", "dent_prof", "band_y", "band_vuelo", "evals", "en_limite", "en_piso"]
MANIFIESTO = {"muestreo": "Sobol scrambled", "rangos": RANGOS, "rho_gamma_phi": RHO_GAMMA_PHI, "escenarios_co2": ESCENARIOS_CO2,
              "apoyo": "φ del suelo de apoyo = φ del relleno, c = 0, μ = tan(2φ/3); dentellón: aporte de punta (tan φ sobre su ancho, confinamiento min(d/w,1)) sin empuje pasivo, η = 0 (HIPÓTESIS, H.6.7b)", "materiales": "f'c 28 MPa, fy 420 MPa", "x_ceniza": 0.0,
              "objetivo": "costo APU (lam_co2 = 0)", "sismo": "seudoestático, K_ST = 0,80·a_max", "perfiles": ["lineal", "parabolico"],
              "limites_busqueda": "ver packages/motor-concreto/src/muro_optimizador.py::LIMITES; t_corona = 0,25 m es CONSTANTE de diseño; los mínimos son pisos constructivos reportados en *_en_piso"}


def muestrear(m: int, seed: int) -> list[dict]:
    u = qmc.Sobol(d=len(NOMBRES) + 1, scramble=True, seed=seed).random_base2(m)       # +1 dimensión para el ruido independiente del peso unitario
    filas = []
    for i, ui in enumerate(u):
        f = {"id": i}
        for j, nom in enumerate(NOMBRES[:-1]):
            if nom == "gamma":
                continue
            lo, hi = RANGOS[nom]
            f[nom] = float(lo + ui[j] * (hi - lo))
        z = RHO_GAMMA_PHI * norm.ppf(np.clip(ui[1], 1e-9, 1 - 1e-9)) + np.sqrt(1 - RHO_GAMMA_PHI**2) * norm.ppf(np.clip(ui[-1], 1e-9, 1 - 1e-9))
        lo, hi = RANGOS["gamma"]
        f["gamma"] = float(lo + norm.cdf(z) * (hi - lo))
        f["escenario_co2"] = ("bajo", "base", "alto")[min(int(ui[len(NOMBRES) - 1] * 3), 2)]
        filas.append(f)
    return filas


def _fila_solucion(prefijo: str, s) -> dict:
    if s is None:
        return {f"{prefijo}_ok": 0}
    g, d = s.geometria, s.diseno
    return {f"{prefijo}_ok": 1, f"{prefijo}_obj": round(s.objetivo), f"{prefijo}_costo": round(d.costo_cop_m), f"{prefijo}_co2": round(d.co2_kg_m, 2),
            f"{prefijo}_perfil": g.perfil, f"{prefijo}_h_zapata": g.h_zapata, f"{prefijo}_t_corona": g.t_corona, f"{prefijo}_t_base": g.t_base,
            f"{prefijo}_b_puntera": g.b_puntera, f"{prefijo}_b_talon": g.b_talon, f"{prefijo}_dent_prof": g.dentellon_prof, f"{prefijo}_band_y": g.bandeja_y,
            f"{prefijo}_band_vuelo": g.bandeja_vuelo, f"{prefijo}_evals": s.evaluaciones, f"{prefijo}_en_limite": "|".join(s.variables_en_limite),
            f"{prefijo}_en_piso": "|".join(s.en_piso_constructivo)}


def calcular(f: dict) -> dict:
    from src.economia_concreto import Economia
    from src.muro_contencion import Relleno, SueloApoyo
    from src.muro_optimizador import CasoMuro, ahorro_frente_a_tradicional, optimizar_todas

    t0 = time.time()
    fe_c, fe_a = ESCENARIOS_CO2[f["escenario_co2"]]
    caso = CasoMuro(f["H"], Relleno(f["gamma"], f["phi"], f["beta"], f["q_s"]), SueloApoyo(f["phi"], f["q_adm"]),
                    economia=Economia(mult_concreto=f["mult_concreto"], p_acero=f["p_acero"], fe_cemento=fe_c, fe_acero=fe_a), a_max_g=f["a_max"])
    out = {"id": f["id"]}
    try:
        sols = optimizar_todas(caso)
    except Exception as e:  # noqa: BLE001 - se registra, no se oculta
        return out | {"error": f"{type(e).__name__}: {e}"[:200], "segundos": round(time.time() - t0, 2)}
    for t in TIPOS:
        out |= _fila_solucion(t, sols[t])
    cand = {t: sols[t] for t in ("estandar", "dentellon", "bandeja") if sols[t] is not None}
    gan = min(cand, key=lambda t: cand[t].objetivo) if cand else "ninguna"
    ah = ahorro_frente_a_tradicional(sols)
    return out | {"ganadora": gan, "ahorro": "" if gan == "ninguna" or ah[gan] is None else round(float(ah[gan]), 4), "error": "", "segundos": round(time.time() - t0, 2)}


def columnas() -> list[str]:
    return ["id"] + NOMBRES + [f"{t}_{c}" for t in TIPOS for c in CAMPOS_SOL] + ["ganadora", "ahorro", "error", "segundos"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261108)
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_muro" / "dataset_v2.csv"))
    ap.add_argument("--procesos", type=int, default=4)
    a = ap.parse_args()
    ruta = Path(a.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    (ruta.parent / "manifiesto.json").write_text(json.dumps(MANIFIESTO, indent=2, ensure_ascii=False), encoding="utf-8")
    muestras = muestrear(a.m, a.seed)
    hechos: set[int] = set()
    if ruta.exists():
        with ruta.open(encoding="utf-8", newline="") as fh:
            hechos = {int(r["id"]) for r in csv.DictReader(fh)}
    pend = [m for m in muestras if m["id"] not in hechos]
    print(f"{len(muestras)} muestras, {len(hechos)} ya calculadas, {len(pend)} pendientes", flush=True)
    por_id = {m["id"]: m for m in muestras}
    t0, k = time.time(), 0
    with ruta.open("a", encoding="utf-8", newline="") as fh, Pool(a.procesos) as pool:
        w = csv.DictWriter(fh, fieldnames=columnas(), extrasaction="ignore")
        if not hechos:
            w.writeheader()
        for r in pool.imap_unordered(calcular, pend, chunksize=4):
            w.writerow({**por_id[r["id"]], **r})
            k += 1
            if k % 100 == 0:
                fh.flush()
                print(f"{k}/{len(pend)}  {time.time() - t0:.0f}s  ({(time.time() - t0) / k:.2f}s por caso efectivo)", flush=True)
    print("listo", flush=True)
