"""Pronóstico del índice del acero corrugado (ICOCIV) — evaluación prerregistrada en el #262 (comentario 6966129943).

Walk-forward con origen expansivo desde 2023-12 (36 meses), h = 3, 6, 12. Se modela y = log(índice). Cada modelo
recibe SOLO la historia hasta el origen (la función `ventana` corta los datos; ningún modelo ve el futuro).

Modelos (fijados en el prerregistro):
  M0 caminata aleatoria · M1 naive estacional m=12 · M2 caminata con deriva
  M3 ARIMA, orden por AICc en cada origen (p,q ≤ 2; d por KPSS)
  M4 ARIMA con el orden elegido una vez en el ICCP 2000–2021 (historia larga sin empalmar)
  M5 ARIMAX = M3 + Δlog TRM y Δlog WPU1012 rezagados h meses
  M6 Chronos-Bolt base, cero disparos

Intervalo del 80 %: ARIMA usa el suyo; Chronos, sus cuantiles 0,1 y 0,9; M0–M2, el pronóstico puntual más los
cuantiles 10/90 de sus propios errores a h pasos dentro de la ventana de entrenamiento (detalle de implementación
que el prerregistro no fijaba; se declara aquí y en el informe).

Uso (venv aparte del worktree, no el de la API):
  .venv/Scripts/python.exe scripts/precios/pronostico_acero.py [--sin-chronos]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
SERIES = RAIZ / "data" / "precios_elementos" / "series_acero_262.csv"
AQUI = Path(__file__).resolve().parent
INFORME = AQUI / "RESULTADOS_ACERO_262.md"
ERRORES = AQUI / "pronostico_acero_errores.json"
HORIZONTES = (3, 6, 12)
PRINCIPAL = 6
ENTRENAMIENTO_INICIAL = 36            # primer origen = mes 36 (2023-12)
MODELOS = ("M0", "M1", "M2", "M3", "M4", "M5", "M6")
NOMBRES = {"M0": "Caminata aleatoria", "M1": "Naive estacional (m=12)", "M2": "Caminata con deriva",
           "M3": "ARIMA (AICc por origen)", "M4": "ARIMA (orden del ICCP)", "M5": "ARIMAX (TRM, chatarra)",
           "M6": "Chronos-Bolt base"}
ALFA_INTERVALO = 0.2


# ---------------------------------------------------------------- datos

def cargar_series(ruta: Path = SERIES) -> dict[str, dict[str, float]]:
    s: dict[str, dict[str, float]] = defaultdict(dict)
    with ruta.open(encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            s[f["serie"]][f["periodo"]] = float(f["valor"])
    return {k: dict(sorted(v.items())) for k, v in s.items()}


def mes_anterior(p: str, k: int = 1) -> str:
    a, m = map(int, p.split("-"))
    t = a * 12 + (m - 1) - k
    return f"{t // 12}-{t % 12 + 1:02d}"


def dlog_rezagada(serie: dict[str, float], periodos: list[str], rezago: int) -> np.ndarray:
    """Δlog de la serie en t − rezago, para cada periodo t. Falla si falta un dato (no se rellena)."""
    out = []
    for p in periodos:
        a, b = mes_anterior(p, rezago), mes_anterior(p, rezago + 1)
        out.append(math.log(serie[a]) - math.log(serie[b]))
    return np.array(out)


# ---------------------------------------------------------------- modelos simples

def _intervalo_empirico(y: np.ndarray, h: int, regla) -> tuple[float, float]:
    """Cuantiles 10/90 de los errores a h pasos de `regla` dentro de y (solo entrenamiento)."""
    errs = [y[t + h] - regla(y[: t + 1], h) for t in range(12, len(y) - h)]
    if len(errs) < 5:
        return -np.inf, np.inf
    return float(np.quantile(errs, ALFA_INTERVALO / 2)), float(np.quantile(errs, 1 - ALFA_INTERVALO / 2))


def caminata(y: np.ndarray, h: int) -> float:
    return float(y[-1])


def estacional(y: np.ndarray, h: int) -> float:
    k = math.ceil(h / 12) * 12
    return float(y[len(y) - k + h - 1]) if len(y) >= k else float(y[-1])


def deriva(y: np.ndarray, h: int) -> float:
    return float(y[-1] + h * np.mean(np.diff(y)))


def simple(regla):
    def modelo(y: np.ndarray, h: int, **_) -> tuple[float, float, float]:
        p = regla(y, h)
        lo, hi = _intervalo_empirico(y, h, regla)
        return p, p + lo, p + hi
    return modelo


# ---------------------------------------------------------------- ARIMA

def elegir_d(y: np.ndarray) -> int:
    from statsmodels.tsa.stattools import kpss
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = kpss(y, regression="c", nlags="auto")[1]
    return 1 if p < 0.05 else 0


def _ajustar(y, orden, exog=None):
    from statsmodels.tsa.arima.model import ARIMA
    tendencia = "c" if orden[1] == 0 else "n"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ARIMA(y, exog=exog, order=orden, trend=tendencia).fit()


def elegir_orden(y: np.ndarray, exog=None) -> tuple[int, int, int]:
    d = elegir_d(y)
    mejor, orden = np.inf, (0, d, 0)
    for p in range(3):
        for q in range(3):
            try:
                r = _ajustar(y, (p, d, q), exog)
            except Exception:  # noqa: BLE001  (orden que no converge: se descarta)
                continue
            if np.isfinite(r.aicc) and r.aicc < mejor:
                mejor, orden = r.aicc, (p, d, q)
    return orden


def pronostico_arima(y, h, orden, exog=None, exog_futura=None) -> tuple[float, float, float]:
    r = _ajustar(y, orden, exog)
    f = r.get_forecast(h, exog=exog_futura)
    ci = np.asarray(f.conf_int(alpha=ALFA_INTERVALO))
    return float(np.asarray(f.predicted_mean)[-1]), float(ci[-1, 0]), float(ci[-1, 1])


# ---------------------------------------------------------------- Chronos

_CHRONOS = {}


def pronostico_chronos(y: np.ndarray, h: int) -> tuple[float, float, float]:
    import torch
    from chronos import ChronosBoltPipeline
    if "p" not in _CHRONOS:
        _CHRONOS["p"] = ChronosBoltPipeline.from_pretrained("amazon/chronos-bolt-base", device_map="cpu",
                                                            torch_dtype=torch.float32)
    q, _ = _CHRONOS["p"].predict_quantiles(torch.tensor(np.exp(y), dtype=torch.float32), prediction_length=h,
                                           quantile_levels=[0.1, 0.5, 0.9])
    lo, med, hi = (float(v) for v in q[0, -1, :])
    return math.log(med), math.log(lo), math.log(hi)


# ---------------------------------------------------------------- evaluación

def ventana(y: np.ndarray, origen: int) -> np.ndarray:
    """Historia disponible en el origen (índice incluido). Copia: ningún modelo puede tocar ni ver el futuro."""
    return y[: origen + 1].copy()


def escala_mase(y_entr: np.ndarray) -> float:
    return float(np.mean(np.abs(np.diff(y_entr))))


def winkler(real: float, lo: float, hi: float, alfa: float = ALFA_INTERVALO) -> float:
    ancho = hi - lo
    if real < lo:
        return ancho + 2 / alfa * (lo - real)
    if real > hi:
        return ancho + 2 / alfa * (real - hi)
    return ancho


def diebold_mariano(e_a: np.ndarray, e_b: np.ndarray, h: int) -> tuple[float, float]:
    """DM con pérdida absoluta, HAC Newey-West (rezago h−1) y corrección de Harvey. Una cola: a mejor que b
    (media de |e_a| − |e_b| < 0). Devuelve (estadístico, p)."""
    d = np.abs(e_a) - np.abs(e_b)
    n = len(d)
    dc = d - d.mean()
    var = np.sum(dc * dc) / n
    for k in range(1, h):
        var += 2 * (1 - k / h) * np.sum(dc[k:] * dc[:-k]) / n
    if var <= 0:
        return 0.0, 0.5 if d.mean() == 0 else (0.0 if d.mean() < 0 else 1.0)
    dm = d.mean() / math.sqrt(var / n)
    dm *= math.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return float(dm), float(stats.t.cdf(dm, df=n - 1))


def holm(pvalores: dict[str, float], alfa: float = 0.05) -> dict[str, bool]:
    orden = sorted(pvalores, key=pvalores.get)
    rechaza, m, sigue = {}, len(orden), True
    for i, k in enumerate(orden):
        sigue = sigue and pvalores[k] <= alfa / (m - i)
        rechaza[k] = sigue
    return rechaza


def evaluar(series: dict, usar_chronos: bool = True) -> dict:
    obj = series["icociv_acero_corrugado"]
    periodos = list(obj)
    y = np.log(np.array([obj[p] for p in periodos]))
    orden_iccp = elegir_orden(np.log(np.array(list(series["iccp_aceros_elementos_metalicos"].values()))))
    filas = []
    for h in HORIZONTES:
        exog_todo = np.column_stack([dlog_rezagada(series["trm_promedio_mensual"], periodos, h),
                                     dlog_rezagada(series["bls_wpu1012"], periodos, h)])
        for o in range(ENTRENAMIENTO_INICIAL - 1, len(y) - h):
            yv = ventana(y, o)
            real = float(y[o + h])
            esc = escala_mase(yv)
            pred = {"M0": simple(caminata)(yv, h), "M1": simple(estacional)(yv, h), "M2": simple(deriva)(yv, h)}
            orden = elegir_orden(yv)
            pred["M3"] = pronostico_arima(yv, h, orden)
            pred["M4"] = pronostico_arima(yv, h, orden_iccp)
            ex, exf = exog_todo[: o + 1], exog_todo[o + 1: o + 1 + h]     # exf es conocida: rezago h
            pred["M5"] = pronostico_arima(yv, h, elegir_orden(yv, ex), ex, exf)
            if usar_chronos:
                pred["M6"] = pronostico_chronos(yv, h)
            for m, (p, lo, hi) in pred.items():
                filas.append({"h": h, "origen": periodos[o], "modelo": m, "real": real, "pred": p, "lo": lo,
                              "hi": hi, "error": real - p, "escala": esc, "orden": list(orden) if m == "M3" else None})
        print(f"h={h} listo ({sum(1 for f in filas if f['h'] == h and f['modelo'] == 'M0')} orígenes)", flush=True)
    return {"orden_iccp": list(orden_iccp), "filas": filas}


def resumir(res: dict) -> tuple[dict, str]:
    filas = res["filas"]
    por = defaultdict(list)
    for f in filas:
        por[(f["h"], f["modelo"])].append(f)
    modelos = [m for m in MODELOS if (PRINCIPAL, m) in por]
    tabla, L = {}, []
    for h in HORIZONTES:
        e0 = np.array([f["error"] for f in por[(h, "M0")]])
        for m in modelos:
            fs = por[(h, m)]
            e = np.array([f["error"] for f in fs])
            dm, p = diebold_mariano(e, e0, h) if m != "M0" else (None, None)
            tabla[(h, m)] = {
                "n": len(fs), "mase": float(np.mean([abs(f["error"]) / f["escala"] for f in fs])),
                "cobertura80": float(np.mean([f["lo"] <= f["real"] <= f["hi"] for f in fs])),
                "winkler80": float(np.mean([winkler(f["real"], f["lo"], f["hi"]) for f in fs])),
                "dm": dm, "p": p}
    cand = {m: tabla[(PRINCIPAL, m)]["p"] for m in modelos if m != "M0"}
    h1 = holm(cand)

    def dm_par(a, b, idx=None):
        ea = np.array([f["error"] for f in por[(PRINCIPAL, a)]])
        eb = np.array([f["error"] for f in por[(PRINCIPAL, b)]])
        if idx is not None:
            ea, eb = ea[idx], eb[idx]
        return diebold_mariano(ea, eb, PRINCIPAL)

    h2, h3 = dm_par("M5", "M3"), dm_par("M4", "M3")
    h4 = None
    if "M6" in modelos:
        n = len(por[(PRINCIPAL, "M0")])
        mitad = n // 2
        clasicos = ("M1", "M2", "M3", "M4", "M5")
        mase_1a = {m: np.mean([abs(f["error"]) / f["escala"] for f in por[(PRINCIPAL, m)][:mitad]]) for m in clasicos}
        campeon = min(mase_1a, key=mase_1a.get)
        h4 = (campeon, *dm_par("M6", campeon, slice(mitad, n)))
    integra = [m for m in cand if h1[m] and 0.7 <= tabla[(PRINCIPAL, m)]["cobertura80"] <= 0.9]

    L += ["# Resultados: pronóstico del acero corrugado (ICOCIV) — #262", "",
          "Generado por `pronostico_acero.py` según el prerregistro del #262. Pérdida en log del índice; MASE escalado por el "
          "MAE del naive a un paso en la ventana de cada origen. DM: una cola (el modelo mejor que la referencia), HAC "
          "Newey-West rezago h−1 y corrección de Harvey.", "",
          f"Orden ARIMA elegido en el ICCP 2000–2021 (M4): {tuple(res['orden_iccp'])}.", ""]
    for h in HORIZONTES:
        etiqueta = " (principal)" if h == PRINCIPAL else " (exploratorio, sin corrección)"
        L += [f"## h = {h} meses{etiqueta}", "", "| Modelo | n | MASE | Cobertura 80 % | Winkler 80 % | DM vs M0 | p (una cola) |",
              "|---|---|---|---|---|---|---|"]
        for m in modelos:
            t = tabla[(h, m)]
            dm = "—" if t["dm"] is None else f"{t['dm']:.2f}"
            p = "—" if t["p"] is None else f"{t['p']:.3f}"
            L.append(f"| {m} {NOMBRES[m]} | {t['n']} | {t['mase']:.3f} | {t['cobertura80']:.0%} | {t['winkler80']:.4f} | {dm} | {p} |")
        L.append("")
    L += ["## Hipótesis (h = 6)", "",
          "- **H1** (Holm sobre " + ", ".join(cand) + "): " +
          (", ".join(f"{m} {'rechaza' if h1[m] else 'no rechaza'} (p={cand[m]:.3f})" for m in cand)) + ".",
          f"- **H2** M5 vs M3: DM {h2[0]:.2f}, p = {h2[1]:.3f}.",
          f"- **H3** M4 vs M3: DM {h3[0]:.2f}, p = {h3[1]:.3f}."]
    L.append(f"- **H4** M6 vs campeón clásico de la primera mitad ({h4[0]}), en la segunda mitad: DM {h4[1]:.2f}, "
             f"p = {h4[2]:.3f}." if h4 else "- **H4** no evaluada (M6 no corrió).")
    L += ["", "## Regla de integración", "",
          (f"Cumplen H1 y cobertura 80 % en [70 %, 90 %]: **{', '.join(integra)}**." if integra else
           "**Ningún modelo cumple.** Según el prerregistro, StructAI no pronostica: muestra el índice vigente con una "
           "banda de volatilidad histórica rotulada como tal."), "",
          "Intervalos de M0–M2: pronóstico + cuantiles 10/90 de sus errores a h pasos en la ventana (detalle de "
          "implementación declarado en el script).", "",
          "Fuente: DANE, www.dane.gov.co · U.S. Bureau of Labor Statistics · Banco de la República (datos.gov.co).", ""]
    return {"tabla": {f"{h}|{m}": v for (h, m), v in tabla.items()}, "h1": h1, "h2": h2, "h3": h3, "h4": h4,
            "integra": integra}, "\n".join(L)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-chronos", action="store_true")
    a = ap.parse_args()
    t = time.time()
    res = evaluar(cargar_series(), usar_chronos=not a.sin_chronos)
    resumen, texto = resumir(res)
    ERRORES.write_text(json.dumps({**res, "resumen": resumen}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"({time.time() - t:.0f} s)")


if __name__ == "__main__":
    main()
