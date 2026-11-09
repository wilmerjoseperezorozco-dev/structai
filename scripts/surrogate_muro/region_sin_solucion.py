"""¿Qué parte de la región sin solución del muro en voladizo (dataset v2) recuperan los contrafuertes y los tirantes preesforzados?

Re-optimiza los primeros N casos del dataset v2 (secuencia de Sobol: cualquier prefijo es representativo) solo con las dos tipologías nuevas y las compara con la mejor de las
tres ya conocidas, que se lee del CSV (no se recalcula). Reporta recuperación por altura, φ y a_max, y en los casos que ya tenían solución, cuánto ahorran.
Uso:  python scripts/surrogate_muro/region_sin_solucion.py [--n 512] [--salida data/surrogate_muro/region_sin_solucion.json]
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
ESC = {"bajo": (0.892, 1.00), "base": (1.010, 1.322), "alto": (1.15, 1.80)}
ANTIGUAS = ("estandar", "dentellon", "bandeja")


def _caso(args):
    f, mult_ancl = args
    from src.economia_concreto import Economia
    from src.muro_contencion import Relleno, SueloApoyo
    from src.muro_optimizador import CasoMuro, optimizar

    fe_c, fe_a = ESC[f["escenario_co2"]]
    caso = CasoMuro(f["H"], Relleno(f["gamma"], f["phi"], f["beta"], f["q_s"]), SueloApoyo(f["phi"], f["q_adm"]),
                    economia=Economia(mult_concreto=f["mult_concreto"], p_acero=f["p_acero"], fe_cemento=fe_c, fe_acero=fe_a,
                                      p_perforacion_m=180_000.0 * mult_ancl, p_cabeza_anclaje=450_000.0 * mult_ancl), a_max_g=f["a_max"])
    out = {}
    cf = optimizar(caso, "contrafuerte", "lineal")
    out["contrafuerte"] = None if cf is None else float(cf.objetivo)
    sols = [s for s in (optimizar(caso, "anclaje", p) for p in ("lineal", "parabolico")) if s is not None]
    best = min(sols, key=lambda s: s.objetivo) if sols else None
    out["anclaje"] = None if best is None else float(best.objetivo)
    out["anclaje_fuerza"] = None if best is None else float(best.geometria.anc_fuerza_kn_m)
    return out


def _resumen(df: pd.DataFrame, mascara: pd.Series) -> dict:
    sub = df[mascara]
    n = len(sub)
    if n == 0:
        return {"n": 0}
    return {"n": int(n), "contrafuerte": float(sub["cf_ok"].mean()), "anclaje": float(sub["anc_ok"].mean()), "alguna": float((sub["cf_ok"] | sub["anc_ok"]).mean())}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--mult-precio-anclaje", type=float, default=1.0, help="multiplica los precios SUPUESTOS de perforación y cabeza (sensibilidad)")
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "surrogate_muro" / "dataset_v2.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_muro" / "region_sin_solucion.json"))
    a = ap.parse_args()
    df = pd.read_csv(a.dataset).head(a.n).copy()
    with Pool(4) as pool:
        res = pool.map(_caso, [(f, a.mult_precio_anclaje) for f in df.to_dict("records")], chunksize=4)
    df["cf_obj"] = [r["contrafuerte"] for r in res]
    df["anc_obj"] = [r["anclaje"] for r in res]
    df["anc_fuerza"] = [r["anclaje_fuerza"] for r in res]
    df["cf_ok"], df["anc_ok"] = df["cf_obj"].notna(), df["anc_obj"].notna()
    viejo = pd.concat([df[f"{t}_obj"].where(df[f"{t}_ok"].astype(bool)) for t in ANTIGUAS], axis=1).min(axis=1)
    df["viejo_obj"] = viejo
    sin = viejo.isna()
    nuevo = pd.concat([df["cf_obj"], df["anc_obj"]], axis=1).min(axis=1)
    con = ~sin & nuevo.notna()
    ahorro = (1.0 - nuevo[con] / viejo[con])
    gan_cf = (df["cf_obj"] < df["anc_obj"].fillna(np.inf)) & df["cf_ok"]
    out = {
        "n": int(len(df)),
        "mult_precio_anclaje": a.mult_precio_anclaje,
        "sin_solucion_antes": float(sin.mean()),
        "sin_solucion_despues": float((sin & ~(df["cf_ok"] | df["anc_ok"])).mean()),
        "recuperados_de_los_sin_solucion": _resumen(df, sin),
        "recuperados_por_altura": {f"{lo}-{hi} m": _resumen(df, sin & (df["H"] >= lo) & (df["H"] < hi)) for lo, hi in ((1.5, 3.0), (3.0, 5.0), (5.0, 6.5), (6.5, 8.01))},
        "recuperados_por_phi": {f"{lo}-{hi}°": _resumen(df, sin & (df["phi"] >= lo) & (df["phi"] < hi)) for lo, hi in ((24, 28), (28, 32), (32, 36), (36, 40.1))},
        "recuperados_por_a_max": {f"{lo}-{hi} g": _resumen(df, sin & (df["a_max"] >= lo) & (df["a_max"] < hi)) for lo, hi in ((0.05, 0.15), (0.15, 0.25), (0.25, 0.35), (0.35, 0.401))},
        "con_solucion_previa": {"n": int((~sin).sum()), "gana_una_nueva": float(((nuevo < viejo) & ~sin).sum() / max((~sin).sum(), 1)),
                                "ahorro_mediano_si_gana": float(np.median(ahorro[ahorro > 0])) if (ahorro > 0).any() else None,
                                "gana_contrafuerte": float((gan_cf & (nuevo < viejo) & ~sin).sum() / max((~sin).sum(), 1)),
                                "gana_anclaje": float((~gan_cf & (nuevo < viejo) & ~sin).sum() / max((~sin).sum(), 1))},
        "fuerza_anclaje_mediana_kn_m": float(df.loc[df["anc_ok"], "anc_fuerza"].median()) if df["anc_ok"].any() else None,
    }
    Path(a.salida).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print("listo", flush=True)
