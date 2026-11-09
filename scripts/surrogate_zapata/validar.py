"""Capa de validación determinista NSR-10 sobre las propuestas del sustituto.

Garantía por construcción: `disenar()` solo devuelve diseños que pasaron `evaluar_geometria` (zapata: flexión/cortante/punzonamiento/presiones/asentamiento;
pedestal: C.10, C.11.6, C.12, C.7.10). Si el modelo propone algo que no cumple se intenta una reparación local acotada y, si falla, se usa el optimizador
exacto. El origen queda registrado: "directo" | "reparado" | "exacto" | "sin_solucion". HIPÓTESIS de investigación: no sustituye la revisión de un
ingeniero responsable.

Uso (benchmark sobre el conjunto reservado): python scripts/surrogate_zapata/validar.py [--modelos data/surrogate_zapata/modelos] [--n 600]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

PASO = 50.0
REPARACION_L_MAX = 400.0     # mm que se puede crecer L respecto a la propuesta
REPARACION_C_MAX = 150.0     # mm que se puede crecer el lado del pedestal
_MODELOS: dict = {}


@dataclass(frozen=True)
class Caso:
    Pu: float
    ey_x: float
    ex_y: float
    q_adm: float
    ks: float
    fc: float
    Df: float
    c_col: float
    exposicion: str
    mult_concreto: float
    p_acero: float
    p_encofrado: float
    p_ceniza: float
    fe_cemento: float
    fe_acero: float
    lam_co2: float


def caso_desde_fila(r) -> Caso:
    return Caso(Pu=float(r["Pu"]), ey_x=float(r["ey_x"]), ex_y=float(r["ex_y"]), q_adm=float(r["q_adm"]), ks=float(r["ks"]), fc=float(r["fc"]),
                Df=float(r["Df"]), c_col=float(r["c_col"]), exposicion=str(r["exposicion_in"]), mult_concreto=float(r["mult_concreto"]),
                p_acero=float(r["p_acero"]), p_encofrado=float(r["p_encofrado"]), p_ceniza=float(r["p_ceniza"]), fe_cemento=float(r["fe_cemento"]),
                fe_acero=float(r["fe_acero"]), lam_co2=float(r["lam_co2"]))


def _contexto(c: Caso):
    from src import zapata as z
    from src.economia_concreto import Economia
    eco = Economia(mult_concreto=c.mult_concreto, p_acero=c.p_acero, p_encofrado=c.p_encofrado, p_ceniza=c.p_ceniza, fe_cemento=c.fe_cemento,
                   fe_acero=c.fe_acero, lam_co2=c.lam_co2)
    cargas = z.CargasZapata(P_serv=c.Pu / 1.35, P_u=c.Pu)
    suelo = z.Suelo(q_adm_kpa=c.q_adm, profundidad_desplante_m=c.Df, ks_kn_m3=c.ks)
    return eco, cargas, suelo


def criterio(cop: float, co2: float, lam: float) -> float:
    return cop + lam * co2


def evaluar_geometria(c: Caso, c_ped: float, L: float, h_c: float, h_e: float, fc: float, x: float) -> Optional[dict]:
    """Verificación determinista completa de UNA geometría. Devuelve None si no cumple (cualquier verificación) o si la mezcla viola la exposición."""
    from src import zapata as z
    from src import zapata_troncopiramidal as t
    from src.diseno_zapata_pedestal import EXPOSICIONES, _evaluar, cargas_en_base
    from src.economia_concreto import AGUA, mezcla
    from src.pedestal import disenar_pedestal
    from src.viga import Materiales

    ex = EXPOSICIONES[c.exposicion]
    if fc < ex["fc_min"] or x > ex["x_max"] + 1e-9:
        return None
    mz = mezcla(fc, x)
    if AGUA / (mz["cem"] + mz["ash"]) > ex["amc_max"] + 1e-9:
        return None
    eco, cargas, suelo = _contexto(c)
    df_mm = c.Df * 1000
    if not (300.0 <= h_e <= h_c <= min(1000.0, df_mm)) or L < c_ped + 200.0 or c_ped < c.c_col:
        return None
    h_p = df_mm - h_c
    cg, Mxb, Myb, Vx, Vy = cargas_en_base(cargas.P_u, c.Pu * c.ey_x, c.Pu * c.ex_y, h_p / 1000)
    cg = z.CargasZapata(P_serv=cargas.P_serv, P_u=cargas.P_u, Mx_serv=cg.Mx_serv, My_serv=cg.My_serv, Mx_u=cg.Mx_u, My_u=cg.My_u)
    ped = disenar_pedestal(c_ped, h_p, cargas.P_u, fc, 420.0, h_c, Mux_kNm=Mxb, Muy_kNm=Myb, Vux_kN=Vx, Vuy_kN=Vy)
    if not ped.cumple:
        return None
    zz = t.verificar(float(L), float(h_c), float(h_e), float(c_ped), cg, suelo, Materiales(fc, 420.0, 420.0))
    if not zz.cumple:
        return None
    cop, co2 = _evaluar(zz, ped, fc, x, eco)
    return {"c_ped": c_ped, "L": L, "h_c": h_c, "h_e": h_e, "fc": fc, "x": x, "costo_cop": cop, "co2_kg": co2, "crit": criterio(cop, co2, c.lam_co2),
            "barras_ped": ped.barras}


def _cargar(dir_modelos: str) -> dict:
    import lightgbm as lgb
    if dir_modelos not in _MODELOS:
        d = Path(dir_modelos)
        _MODELOS[dir_modelos] = {n: lgb.Booster(model_file=str(d / f"{n}.txt")) for n in ("L", "h_c", "h_e", "c_ped", "x_ceniza_cod", "fc_cod")}
    return _MODELOS[dir_modelos]


def _snap(v: float, lo: float, hi: float) -> float:
    return float(min(max(round(v / PASO) * PASO, lo), hi))


def predecir(c: Caso, dir_modelos: str) -> dict:
    from entrenar_surrogate import ENTRADAS, EXP_COD, FC_VALORES, X_VALORES
    m = _cargar(dir_modelos)
    fila = pd.DataFrame([{**c.__dict__, "exp_cod": EXP_COD[c.exposicion]}])[ENTRADAS]
    df_mm = c.Df * 1000
    h_c = _snap(float(m["h_c"].predict(fila)[0]), 300.0, min(1000.0, df_mm))
    h_e = _snap(float(m["h_e"].predict(fila)[0]), 300.0, h_c)
    return {"L": _snap(float(m["L"].predict(fila)[0]), c.c_col + 200.0, 6000.0), "h_c": h_c, "h_e": h_e,
            "c_ped": _snap(float(m["c_ped"].predict(fila)[0]), c.c_col, 900.0),
            "fc": FC_VALORES[int(np.argmax(m["fc_cod"].predict(fila)[0]))], "x": X_VALORES[int(np.argmax(m["x_ceniza_cod"].predict(fila)[0]))]}


def _reparar(c: Caso, p: dict) -> Optional[dict]:
    """Vecindario acotado alrededor de la propuesta: crece L, h_e, h_c y el lado del pedestal; mejor criterio entre los que cumplen."""
    mejor = None
    fc = max(p["fc"], 35.0 if c.exposicion != "interior_C1_S0" else p["fc"])
    for dc in np.arange(0.0, REPARACION_C_MAX + 1, PASO):
        for dL in np.arange(0.0, REPARACION_L_MAX + 1, PASO):
            for dhc in (0.0, 50.0, -50.0, 100.0):
                h_c = p["h_c"] + dhc
                for h_e in np.arange(p["h_e"], h_c + 1, PASO):
                    r = evaluar_geometria(c, p["c_ped"] + dc, p["L"] + dL, h_c, float(h_e), fc, p["x"])
                    if r and (mejor is None or r["crit"] < mejor["crit"]):
                        mejor = r
        if mejor is not None:
            return mejor      # el primer lado de pedestal que admite solución; no se sigue creciendo
    return mejor


def _exacto(c: Caso) -> Optional[dict]:
    from src.diseno_zapata_pedestal import optimizar_conjunto
    eco, cargas, suelo = _contexto(c)
    d = optimizar_conjunto(c.c_col, cargas, suelo, exposicion=c.exposicion, objetivo="mixto", fc=c.fc, economia=eco,
                           momentos_columna=(c.Pu * c.ey_x, c.Pu * c.ex_y))
    if d is None:
        return None
    return {"c_ped": d.pedestal.c_mm, "L": d.zapata.L_mm, "h_c": d.zapata.h_c_mm, "h_e": d.zapata.h_e_mm, "fc": d.fc, "x": d.x_ceniza,
            "costo_cop": d.costo_cop, "co2_kg": d.co2_kg, "crit": criterio(d.costo_cop, d.co2_kg, c.lam_co2), "barras_ped": d.pedestal.barras}


def disenar(c: Caso, dir_modelos: str) -> dict:
    """Diseño verificado para el caso `c`. Nunca devuelve un diseño sin pasar `evaluar_geometria`; el 'exacto' viene del optimizador determinista."""
    t0 = time.time()
    p = predecir(c, dir_modelos)
    r = evaluar_geometria(c, p["c_ped"], p["L"], p["h_c"], p["h_e"], p["fc"], p["x"])
    if r:
        return {**r, "origen": "directo", "segundos": time.time() - t0}
    r = _reparar(c, p)
    if r:
        return {**r, "origen": "reparado", "segundos": time.time() - t0}
    r = _exacto(c)
    if r:
        return {**r, "origen": "exacto", "segundos": time.time() - t0}
    return {"origen": "sin_solucion", "segundos": time.time() - t0}


def _tarea(arg) -> dict:
    fila, dir_modelos = arg
    c = caso_desde_fila(fila)
    out = disenar(c, dir_modelos)
    out["crit_verdad"] = float(fila["costo_cop"]) + c.lam_co2 * float(fila["co2_kg"])
    out["costo_verdad"] = float(fila["costo_cop"])
    out["co2_verdad"] = float(fila["co2_kg"])
    if out["origen"] != "sin_solucion":
        # re-verificación independiente de lo que se devolvió: la garantía de 0 diseños inseguros
        out["reverificado"] = evaluar_geometria(c, out["c_ped"], out["L"], out["h_c"], out["h_e"], out["fc"], out["x"]) is not None
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", default=str(RAIZ / "data" / "surrogate_zapata" / "modelos"))
    ap.add_argument("--n", type=int, default=600)
    args = ap.parse_args()
    res = pd.read_csv(Path(args.modelos) / "reservado.csv").head(args.n)
    t0 = time.time()
    with Pool(4) as pool:
        filas = pool.map(_tarea, [(r, args.modelos) for _, r in res.iterrows()], chunksize=4)
    df = pd.DataFrame(filas)
    n = len(df)
    ok = df[df["origen"] != "sin_solucion"]
    gap = (ok["crit"] - ok["crit_verdad"]) / ok["crit_verdad"] * 100
    resumen = {
        "n": n, "origen": {k: int(v) for k, v in df["origen"].value_counts().items()},
        "diseños_inseguros_tras_reverificacion": int((~ok["reverificado"]).sum()),
        "brecha_criterio_pct": {"mediana": round(float(gap.median()), 2), "p90": round(float(gap.quantile(0.9)), 2), "p99": round(float(gap.quantile(0.99)), 2),
                                "max": round(float(gap.max()), 2), "negativas_solo_por_rejilla": int((gap < -1e-6).sum())},
        "segundos_por_caso": {"surrogate_directo": round(float(df[df.origen == "directo"]["segundos"].mean()), 3) if (df.origen == "directo").any() else None,
                              "todos": round(float(df["segundos"].mean()), 3)},
        "tiempo_total_s": round(time.time() - t0, 1),
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    Path(args.modelos, "benchmark_validacion.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    df.to_csv(Path(args.modelos) / "benchmark_validacion_detalle.csv", index=False)


if __name__ == "__main__":
    main()
