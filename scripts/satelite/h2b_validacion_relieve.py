"""H2b (#273): validación fuera de muestra de la regla de relieve hallada en H2.

Protocolo: PROTOCOLO_ANALISIS.md §31. La regla se fijó solo con la muestra de entrenamiento de H2
(Meta, Guaviare e Inírida; 453 puntos): relieve local S (cota DEM − mínima a ≤ 1 km) ≤ 6,5 m → alarma de nivel
freático somero (umbral de Youden en entrenamiento: sensibilidad 0,74, especificidad 0,70).
Validación:
  principal: Casanare (campo PROFUNDI_4, confirmado como nivel: va después del método de medición del nivel y es menor
             que la profundidad del pozo/aljibe en el 98-100 %). Parcialmente vista en H2 (ver protocolo).
  secundaria: Quindío (campo Profundi_4, mismo criterio; región andina, niveles más profundos). Nunca vista.
Uso: python -I h2b_validacion_relieve.py   -> h2b_validacion_resultados.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h2_saturacion_freatica as h2  # noqa: E402
import h3_socavacion_puentes as h3  # noqa: E402

SALIDA = AQUI / "h2b_validacion_resultados.json"
UMBRAL_S_M = 6.5
h3.RNG = np.random.default_rng(27321)


def muestra(capa: str):
    h2.NIVEL.clear()
    h2.NIVEL_SENSIBILIDAD.clear()
    campo = {"casanare": "PROFUNDI_4", "quindio": "Profundi_4"}[capa]
    h2.NIVEL[capa] = lambda a: h2._num(a.get(campo))
    h2.CAMPO_TIPO["quindio"] = "Tipo_de_pu"
    p = h2.predictores(h2.puntos(incluir_sensibilidad=False))
    return p[np.isfinite(p["nivel_m"]) & np.isfinite(p["S"])].reset_index(drop=True)


def evaluar(p, umbral_nivel: float) -> dict:
    y = (p["nivel_m"] <= umbral_nivel).astype(int).values
    S = p["S"].values
    alarma = S <= UMBRAL_S_M
    b = p["bloque"].values
    r = {"n": len(p), "n_someros": int(y.sum()), "prevalencia": float(y.mean()), "n_bloques": int(len(set(b)))}
    if 0 < y.sum() < len(y):
        r["auc_relieve"] = {"valor": float(h3.auc(-S, y)), "ic95": h3.boot(lambda ix: h3.auc(-S[ix], y[ix]), b)}
        r["regla"] = {
            "sensibilidad": float(alarma[y == 1].mean()), "especificidad": float((~alarma[y == 0]).mean()),
            "vpp": float(y[alarma].mean()) if alarma.any() else None,
            "vpp_ic95": h3.boot(lambda ix: y[ix][alarma[ix]].mean() if alarma[ix].any() else np.nan, b),
            "fraccion_alarma": float(alarma.mean())}
    r["spearman_relieve_profundidad"] = float(spearmanr(S, p["nivel_m"])[0])
    r["por_tipo"] = {t: {"n": int((p["tipo"] == t).sum()), "someros": int(y[p["tipo"].values == t].sum()),
                         "auc_relieve": float(h3.auc(-S[p["tipo"].values == t], y[p["tipo"].values == t]))
                         if 0 < y[p["tipo"].values == t].sum() < (p["tipo"] == t).sum() else None}
                     for t in ("pozo", "aljibe")}
    return r


def veredicto(r) -> str:
    if "auc_relieve" not in r:
        return "SIN CASOS"
    lo, hi = r["auc_relieve"]["ic95"]
    vlo = r["regla"]["vpp_ic95"][0]
    if lo > 0.60 and vlo > r["prevalencia"]:
        return "VALIDADA"
    if hi < 0.55:
        return "NO VALIDADA"
    return "NO CONCLUYENTE"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §31", "regla": f"relieve local (1 km) <= {UMBRAL_S_M} m"}
    cas = muestra("casanare")
    out["casanare_2m"] = evaluar(cas, 2.0)
    out["casanare_2m"]["veredicto"] = veredicto(out["casanare_2m"])
    out["casanare_3m"] = evaluar(cas, 3.0)
    qui = muestra("quindio")
    out["quindio_2m"] = evaluar(qui, 2.0)
    out["quindio_5m"] = evaluar(qui, 5.0)
    out["quindio_5m"]["veredicto"] = veredicto(out["quindio_5m"])
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
