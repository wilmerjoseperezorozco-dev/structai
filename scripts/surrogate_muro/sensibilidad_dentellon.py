"""Sensibilidad del selector de tipología a la fracción de empuje pasivo (η) que se le concede al dentellón (H.6.7b: η = 0 es la lectura estricta).

Re-optimiza los primeros N casos del dataset con η ∈ {0, 0,25, 0,5, 1} y reporta: fracción con solución, tipología ganadora, ahorro mediano.
Uso:  python scripts/surrogate_muro/sensibilidad_dentellon.py [--n 512] [--salida data/surrogate_muro/sensibilidad_dentellon.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
ETAS = (0.0, 0.25, 0.5, 1.0)
ESC = {"bajo": (0.892, 1.00), "base": (1.010, 1.322), "alto": (1.15, 1.80)}


def _caso(args):
    f, eta = args
    from src.economia_concreto import Economia
    from src.muro_contencion import Relleno, SueloApoyo
    from src.muro_optimizador import CasoMuro, ahorro_frente_a_tradicional, optimizar_todas

    fe_c, fe_a = ESC[f["escenario_co2"]]
    caso = CasoMuro(f["H"], Relleno(f["gamma"], f["phi"], f["beta"], f["q_s"]), SueloApoyo(f["phi"], f["q_adm"], eta_pasivo_dentellon=eta),
                    economia=Economia(mult_concreto=f["mult_concreto"], p_acero=f["p_acero"], fe_cemento=fe_c, fe_acero=fe_a), a_max_g=f["a_max"])
    sols = optimizar_todas(caso)
    cand = {t: sols[t] for t in ("estandar", "dentellon", "bandeja") if sols[t] is not None}
    gan = min(cand, key=lambda t: cand[t].objetivo) if cand else "ninguna"
    ah = ahorro_frente_a_tradicional(sols)
    return gan, (None if gan == "ninguna" or ah[gan] is None else float(ah[gan]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "surrogate_muro" / "dataset_v2.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_muro" / "sensibilidad_dentellon.json"))
    a = ap.parse_args()
    filas = pd.read_csv(a.dataset).head(a.n).to_dict("records")
    out = {}
    with Pool(4) as pool:
        for eta in ETAS:
            res = pool.map(_caso, [(f, eta) for f in filas], chunksize=4)
            gan = pd.Series([r[0] for r in res])
            ah = np.array([r[1] for r in res if r[1] is not None])
            out[str(eta)] = {"con_solucion": float((gan != "ninguna").mean()), "ganadora": gan.value_counts(normalize=True).round(4).to_dict(),
                             "ahorro_mediano": float(np.median(ah)) if len(ah) else None}
            print(eta, out[str(eta)], flush=True)
    Path(a.salida).write_text(json.dumps({"n": len(filas), "resultados": out}, indent=2, ensure_ascii=False), encoding="utf-8")
