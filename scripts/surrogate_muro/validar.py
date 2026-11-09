"""Capa de seguridad normativa («guardrail») + benchmark del sustituto del muro de contención.

Flujo por caso: el modelo propone tipología y dimensiones → se redondean a la rejilla y se pasan por el verificador determinista (estabilidad + estructural) →
si cumple, origen «directo»; si no, búsqueda local desde la propuesta («reparado»); si tampoco, optimizador de referencia («exacto»). Si el modelo dice «inviable» se
confirma con el optimizador (así se mide cuántos factibles se pierden). Garantía: 0 diseños inseguros POR CONSTRUCCIÓN del validador y solo respecto de lo que el
motor verifica. El caso inviable se devuelve como «sin_solucion», nunca como una geometría.

Uso:  python scripts/surrogate_muro/validar.py [--modelos data/surrogate_muro/modelos] [--n 400]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from entrenar import DIMS, ENTRADAS, ESCENARIOS, TIPOS  # noqa: E402

from src.economia_concreto import Economia  # noqa: E402
from src.muro_contencion import GeometriaMuro, Relleno, SueloApoyo, verificar_estabilidad, verificar_estabilidad_sismica  # noqa: E402
from src.muro_contencion_estructural import disenar_estructura  # noqa: E402
from src.muro_optimizador import LIMITES, PASO, CasoMuro, _redondear, optimizar, optimizar_todas  # noqa: E402


def caso_desde_fila(f) -> CasoMuro:
    fe_c, fe_a = ESCENARIOS[f["escenario_co2"]]
    return CasoMuro(float(f["H"]), Relleno(float(f["gamma"]), float(f["phi"]), float(f["beta"]), float(f["q_s"])), SueloApoyo(float(f["phi"]), float(f["q_adm"])),
                    economia=Economia(mult_concreto=float(f["mult_concreto"]), p_acero=float(f["p_acero"]), fe_cemento=fe_c, fe_acero=fe_a), a_max_g=float(f["a_max"]))


class Modelo:
    def __init__(self, carpeta: Path):
        self.b = {p.stem: lgb.Booster(model_file=str(p)) for p in carpeta.glob("*.txt")}

    def proponer(self, f: dict) -> tuple[float, str, GeometriaMuro]:
        x = pd.DataFrame([{k: f[k] for k in ENTRADAS}])
        p_viable = float(self.b["viable"].predict(x, num_threads=1)[0])
        pt = self.b["tipo"].predict(x, num_threads=1)[0]
        tipo = TIPOS[int(np.argmax(pt))]
        d = {dim: float(self.b[f"{tipo}__{dim}"].predict(x, num_threads=1)[0]) for dim in DIMS[tipo]}
        perfil = "parabolico" if float(self.b[f"{tipo}__perfil"].predict(x, num_threads=1)[0]) > 0.5 else "lineal"
        return p_viable, tipo, self._geometria(float(f["H"]), tipo, perfil, d)

    @staticmethod
    def _geometria(H: float, tipo: str, perfil: str, d: dict) -> GeometriaMuro:
        def ac(nom, paso=PASO):
            lo, hi = LIMITES[{"dent_prof": "dentellon_prof", "band_y": "bandeja_y", "band_vuelo": "bandeja_vuelo"}.get(nom, nom)]
            return min(max(_redondear(d[nom], paso), lo), hi)
        tc, tb = ac("t_corona"), ac("t_base")
        g = GeometriaMuro(H, ac("h_zapata"), tc, max(tb, tc), ac("b_puntera"), ac("b_talon"), perfil=perfil)
        if tipo == "dentellon":
            g = replace(g, dentellon_prof=ac("dent_prof"), dentellon_ancho=0.4)
        if tipo == "bandeja":
            g = replace(g, bandeja_y=min(ac("band_y", 0.1), max(H - 0.6, 0.5)), bandeja_vuelo=ac("band_vuelo", 0.1), bandeja_esp=0.25)
        return g


def disenar(modelo: Modelo, f: dict) -> dict:
    """Devuelve {origen, tipologia, geometria, objetivo}. origen ∈ directo | reparado | exacto | sin_solucion."""
    caso = caso_desde_fila(f)
    p_viable, tipo, g = modelo.proponer(f)
    try:
        d = disenar_estructura(g, caso.relleno, caso.apoyo, caso.materiales, caso.economia, a_max_g=caso.a_max_g)
    except ValueError:
        d = None
    if p_viable >= 0.5 and d is not None and d.cumple:
        return {"origen": "directo", "tipologia": tipo, "geometria": g, "objetivo": d.costo_cop_m}
    if p_viable >= 0.5:
        s = optimizar(caso, tipo, g.perfil, inicio=g)
        if s is not None:
            return {"origen": "reparado", "tipologia": tipo, "geometria": s.geometria, "objetivo": s.objetivo}
    sols = {k: v for k, v in optimizar_todas(caso).items() if k != "tradicional" and v is not None}
    if not sols:
        return {"origen": "sin_solucion", "tipologia": None, "geometria": None, "objetivo": np.nan}
    s = min(sols.values(), key=lambda v: v.objetivo)
    return {"origen": "exacto", "tipologia": s.tipologia, "geometria": s.geometria, "objetivo": s.objetivo}


def reverificar(f: dict, r: dict) -> bool:
    """Re-verificación de lo entregado: estabilidad estática y sísmica + diseño estructural completo."""
    if r["geometria"] is None:
        return True
    c = caso_desde_fila(f)
    g = r["geometria"]
    return (verificar_estabilidad(g, c.relleno, c.apoyo).cumple and verificar_estabilidad_sismica(g, c.relleno, c.apoyo, c.a_max_g).cumple
            and disenar_estructura(g, c.relleno, c.apoyo, c.materiales, c.economia, a_max_g=c.a_max_g).cumple)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", default=str(RAIZ / "data" / "surrogate_muro" / "modelos"))
    ap.add_argument("--n", type=int, default=400)
    a = ap.parse_args()
    carpeta = Path(a.modelos)
    res = pd.read_csv(carpeta / "reservado.csv").head(a.n)
    mod = Modelo(carpeta)
    filas = []
    for _, fila in res.iterrows():
        f = fila.to_dict()
        t0 = time.time()
        r = disenar(mod, f)
        dt = time.time() - t0
        ref = None if f["ganadora"] == "ninguna" else float(f[f"{f['ganadora']}_obj"])
        brecha = (r["objetivo"] / ref - 1.0) if (ref and not np.isnan(r["objetivo"])) else np.nan
        filas.append({"id": f["id"], "origen": r["origen"], "tipo_real": f["ganadora"], "tipo_dado": r["tipologia"], "brecha": brecha, "seguro": reverificar(f, r), "seg": dt})
    d = pd.DataFrame(filas)
    b = d[d["origen"] != "sin_solucion"]["brecha"].dropna()
    rng = np.random.default_rng(0)
    boot = [float(np.median(rng.choice(b.values, len(b)))) for _ in range(1000)] if len(b) else [np.nan]
    dir_ = d[d["origen"] == "directo"]
    out = {"n": len(d), "origenes": d["origen"].value_counts(normalize=True).round(4).to_dict(), "inseguros": int((~d["seguro"]).sum()),
           "falsos_inviables": int(((d["origen"] == "sin_solucion") & (d["tipo_real"] != "ninguna")).sum()),
           "tipo_correcto_directos": float((dir_["tipo_real"] == dir_["tipo_dado"]).mean()) if len(dir_) else None,
           "brecha_mediana": float(b.median()), "brecha_mediana_IC95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
           "brecha_p90": float(b.quantile(0.9)), "brecha_p99": float(b.quantile(0.99)), "brecha_negativa_mayor_1pct": int((b < -0.01).sum()),
           "segundos_medio": float(d["seg"].mean())}
    (carpeta / "benchmark_validacion.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    d.to_csv(carpeta / "benchmark_validacion_detalle.csv", index=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
