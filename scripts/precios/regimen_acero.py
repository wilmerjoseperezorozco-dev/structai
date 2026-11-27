"""Régimen del precio del acero con cadenas de Markov (sigue al #262). Prerregistro en su issue antes de correr.

El #262 mostró que el NIVEL del índice no se pronostica mejor que con la caminata aleatoria. Aquí se pregunta por la
DIRECCIÓN: ¿la probabilidad de que el acero corrugado suba ≥ 2 % en los próximos 3 meses se puede estimar mejor que
con la frecuencia histórica?

Evento   E_t = 1 si log(I[t+3]) − log(I[t]) ≥ log(1,02). Serie: ICOCIV insumo Acero corrugado (2021–2026).
Modelos  (todos dan una probabilidad en cada origen, con datos solo hasta el origen):
  B0  climatología: frecuencia de E en la ventana (suavizado de Laplace).
  B1  cadena de Markov OBSERVADA: P(E | estado actual), estado = alza / estable / baja según el cambio de los últimos
      3 meses con el mismo umbral de ±2 %. Frecuencias de la ventana con Laplace.
  R1  cadena OCULTA (HMM gaussiano, 2 estados) sobre Δlog mensual del ICOCIV, ajustada por EM en cada origen.
  R2  HMM con la matriz de transición estimada UNA vez en el ICCP 2000–2021 (la persistencia de los regímenes) y las
      medias y varianzas reestimadas en el ICOCIV en cada origen. Prueba si la historia larga sirve sin empalmar.
  Para R1 y R2: P(E) = suma sobre las 2³ trayectorias de estados de los próximos 3 meses, cada una con suma normal.
Métrica  Brier; Brier Skill Score frente a B0; DM sobre la diferencia de pérdidas (HAC Newey-West rezago 2,
         corrección de Harvey), una cola; Holm sobre B1, R1, R2. Secundarias: log-score y tabla de calibración.

Uso: <venv del worktree de acero>/python scripts/precios/regimen_acero.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
SERIES = RAIZ / "data" / "precios_elementos" / "series_acero_262.csv"
AQUI = Path(__file__).resolve().parent
INFORME = AQUI / "RESULTADOS_REGIMEN_ACERO.md"
DETALLE = AQUI / "regimen_acero_detalle.json"
H = 3
UMBRAL = math.log(1.02)
ENTRENAMIENTO_INICIAL = 36            # primer origen 2023-12, igual que el #262
K = 2
SEMILLA = 262
ARRANQUES = 10
SIGMA_MIN = 1e-4
MODELOS = ("B0", "B1", "R1", "R2")
NOMBRES = {"B0": "Climatología", "B1": "Cadena de Markov observada", "R1": "HMM 2 estados (ICOCIV)",
           "R2": "HMM con transición del ICCP"}


# ---------------------------------------------------------------- HMM gaussiano (Baum-Welch con escalado)

def _emision(x: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return stats.norm.pdf(x[:, None], mu[None, :], sd[None, :]) + 1e-300


def adelante(x, pi, A, mu, sd):
    B = _emision(x, mu, sd)
    T = len(x)
    alfa, c = np.zeros((T, len(pi))), np.zeros(T)
    alfa[0] = pi * B[0]
    c[0] = alfa[0].sum()
    alfa[0] /= c[0]
    for t in range(1, T):
        alfa[t] = (alfa[t - 1] @ A) * B[t]
        c[t] = alfa[t].sum()
        alfa[t] /= c[t]
    return alfa, c, B


def ajustar_hmm(x: np.ndarray, A_fija: np.ndarray | None = None, iters: int = 200, semilla: int = SEMILLA) -> dict:
    """EM con varios arranques; devuelve el de mayor verosimilitud. Estados ordenados por media (0 = el más bajo)
    para que la etiqueta no cambie entre orígenes. Si A_fija se da, la transición no se reestima."""
    rng = np.random.default_rng(semilla)
    mejor = None
    for _ in range(ARRANQUES):
        mu = np.sort(rng.choice(x, K, replace=False)) + rng.normal(0, 1e-4, K)
        sd = np.full(K, max(x.std(), SIGMA_MIN))
        A = A_fija.copy() if A_fija is not None else np.full((K, K), 0.1 / (K - 1)) + np.eye(K) * (0.9 - 0.1 / (K - 1))
        pi = np.full(K, 1 / K)
        ll_prev = -np.inf
        for _ in range(iters):
            alfa, c, B = adelante(x, pi, A, mu, sd)
            beta = np.ones_like(alfa)
            for t in range(len(x) - 2, -1, -1):
                beta[t] = (A @ (B[t + 1] * beta[t + 1])) / c[t + 1]
            gamma = alfa * beta
            gamma /= gamma.sum(1, keepdims=True)
            xi = (alfa[:-1, :, None] * A[None] * (B[1:] * beta[1:])[:, None, :]) / c[1:, None, None]
            pi = gamma[0]
            if A_fija is None:
                A = xi.sum(0) / xi.sum((0, 2))[:, None]
            w = gamma.sum(0)
            mu = (gamma * x[:, None]).sum(0) / w
            sd = np.sqrt(np.maximum((gamma * (x[:, None] - mu) ** 2).sum(0) / w, SIGMA_MIN ** 2))
            ll = np.log(c).sum()
            if ll - ll_prev < 1e-8:
                break
            ll_prev = ll
        if mejor is None or ll > mejor["ll"]:
            mejor = {"ll": ll, "pi": pi, "A": A, "mu": mu, "sd": sd}
    o = np.argsort(mejor["mu"])
    mejor.update(pi=mejor["pi"][o], A=mejor["A"][np.ix_(o, o)], mu=mejor["mu"][o], sd=mejor["sd"][o])
    return mejor


def prob_evento_hmm(x: np.ndarray, m: dict, h: int = H, umbral: float = UMBRAL) -> float:
    """P(suma de los próximos h Δlog ≥ umbral), filtrando el estado en el último dato y enumerando trayectorias."""
    alfa, _, _ = adelante(x, m["pi"], m["A"], m["mu"], m["sd"])
    p_t = alfa[-1]
    total = 0.0
    for camino in product(range(K), repeat=h):
        p, previo = 1.0, None
        for k, s in enumerate(camino):
            p *= (p_t @ m["A"])[s] if k == 0 else m["A"][previo, s]
            previo = s
        media = sum(m["mu"][s] for s in camino)
        sd = math.sqrt(sum(m["sd"][s] ** 2 for s in camino))
        total += p * (1 - stats.norm.cdf(umbral, media, sd))
    return float(min(max(total, 1e-6), 1 - 1e-6))


# ---------------------------------------------------------------- referencias

def eventos(logI: np.ndarray, h: int = H, umbral: float = UMBRAL) -> np.ndarray:
    """E_t para t con t+h dentro de la serie (los demás no existen todavía)."""
    return (logI[h:] - logI[:-h] >= umbral).astype(int)


def estado_observado(logI: np.ndarray, t: int, h: int = H, umbral: float = UMBRAL) -> int:
    """0 baja, 1 estable, 2 alza, según el cambio de los últimos h meses (necesita t ≥ h)."""
    d = logI[t] - logI[t - h]
    return 2 if d >= umbral else (0 if d <= -umbral else 1)


def climatologia(logI_v: np.ndarray) -> float:
    e = eventos(logI_v)
    return (e.sum() + 1) / (len(e) + 2)


def markov_observada(logI_v: np.ndarray) -> float:
    """Pares (estado en t, E_t) con t + h ≤ origen; P(E | estado del origen) con Laplace."""
    o = len(logI_v) - 1
    e = eventos(logI_v)
    cuenta = defaultdict(lambda: [0, 0])
    for t in range(H, len(e)):
        s = estado_observado(logI_v, t)
        cuenta[s][0] += e[t]
        cuenta[s][1] += 1
    k, n = cuenta[estado_observado(logI_v, o)]
    return (k + 1) / (n + 2)


# ---------------------------------------------------------------- evaluación

def dm_perdidas(d: np.ndarray, h: int = H) -> tuple[float, float]:
    """DM sobre diferencias de pérdida d = L_modelo − L_ref; una cola (modelo mejor: media < 0)."""
    n = len(d)
    dc = d - d.mean()
    var = np.sum(dc * dc) / n
    for k in range(1, h):
        var += 2 * (1 - k / h) * np.sum(dc[k:] * dc[:-k]) / n
    if var <= 0:
        return 0.0, 0.5
    dm = d.mean() / math.sqrt(var / n) * math.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return float(dm), float(stats.t.cdf(dm, df=n - 1))


def holm(p: dict[str, float], alfa: float = 0.05) -> dict[str, bool]:
    orden, out, sigue = sorted(p, key=p.get), {}, True
    for i, k in enumerate(orden):
        sigue = sigue and p[k] <= alfa / (len(orden) - i)
        out[k] = sigue
    return out


def calibracion(p: np.ndarray, y: np.ndarray, cortes=(0, 0.2, 0.4, 0.6, 0.8, 1.0001)) -> list[dict]:
    out = []
    for a, b in zip(cortes[:-1], cortes[1:]):
        m = (p >= a) & (p < b)
        if m.any():
            out.append({"rango": f"{a:.1f}–{min(b, 1):.1f}", "n": int(m.sum()), "p_media": float(p[m].mean()),
                        "frecuencia": float(y[m].mean())})
    return out


def cargar(ruta: Path = SERIES) -> dict[str, list[float]]:
    s: dict[str, dict[str, float]] = defaultdict(dict)
    with ruta.open(encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            s[f["serie"]][f["periodo"]] = float(f["valor"])
    return {k: [v[p] for p in sorted(v)] for k, v in s.items()} | {"_periodos_obj": sorted(s["icociv_acero_corrugado"])}


def evaluar(obj: list[float], iccp: list[float], periodos: list[str] | None = None) -> dict:
    logI = np.log(np.array(obj))
    A_iccp = ajustar_hmm(np.diff(np.log(np.array(iccp))))["A"]
    y_todo = eventos(logI)
    filas = []
    for o in range(ENTRENAMIENTO_INICIAL - 1, len(logI) - H):
        v = logI[: o + 1].copy()                     # solo la historia hasta el origen
        dx = np.diff(v)
        p = {"B0": climatologia(v), "B1": markov_observada(v),
             "R1": prob_evento_hmm(dx, ajustar_hmm(dx)), "R2": prob_evento_hmm(dx, ajustar_hmm(dx, A_fija=A_iccp))}
        filas.append({"origen": periodos[o] if periodos else o, "y": int(y_todo[o]), **p})
    return {"A_iccp": A_iccp.tolist(), "filas": filas}


def resumir(res: dict) -> tuple[dict, str]:
    F = res["filas"]
    y = np.array([f["y"] for f in F])
    brier = {m: (np.array([f[m] for f in F]) - y) ** 2 for m in MODELOS}
    logs = {m: -np.mean(y * np.log([f[m] for f in F]) + (1 - y) * np.log([1 - f[m] for f in F])) for m in MODELOS}
    pruebas = {m: dm_perdidas(brier[m] - brier["B0"]) for m in MODELOS if m != "B0"}
    h = holm({m: v[1] for m, v in pruebas.items()})
    bss = {m: 1 - brier[m].mean() / brier["B0"].mean() for m in MODELOS}
    cal = {m: calibracion(np.array([f[m] for f in F]), y) for m in MODELOS}
    integra = [m for m in pruebas if h[m] and bss[m] > 0]
    A = np.array(res["A_iccp"])
    L = ["# Resultados: régimen del precio del acero (cadenas de Markov)", "",
         f"Evento: el acero corrugado (ICOCIV) sube ≥ 2 % en los próximos {H} meses. {len(F)} orígenes; frecuencia "
         f"observada del evento en ellos: {y.mean():.0%}.", "",
         f"Transición estimada en el ICCP 2000–2021 (estado 0 = media más baja): permanencia {A[0, 0]:.3f} y "
         f"{A[1, 1]:.3f}; duración media {1 / (1 - A[0, 0]):.1f} y {1 / (1 - A[1, 1]):.1f} meses.", "",
         "| Modelo | Brier | BSS vs B0 | Log-score | DM vs B0 | p (una cola) | Holm |", "|---|---|---|---|---|---|---|"]
    for m in MODELOS:
        dm, p = pruebas.get(m, (None, None))
        L.append(f"| {m} {NOMBRES[m]} | {brier[m].mean():.4f} | {bss[m]:+.3f} | {logs[m]:.3f} | "
                 f"{'—' if dm is None else f'{dm:.2f}'} | {'—' if p is None else f'{p:.3f}'} | "
                 f"{'—' if m == 'B0' else ('rechaza' if h[m] else 'no rechaza')} |")
    L += ["", "## Calibración", ""]
    for m in MODELOS:
        L.append(f"- **{m}**: " + "; ".join(f"{c['rango']} → n={c['n']}, p̄={c['p_media']:.2f}, obs={c['frecuencia']:.2f}"
                                           for c in cal[m]))
    L += ["", "## Regla de integración", "",
          (f"Cumplen (Holm y BSS > 0): **{', '.join(integra)}**." if integra else
           "**Ningún modelo cumple.** StructAI no muestra un semáforo de régimen del acero."), "",
          "Fuente: DANE, www.dane.gov.co.", ""]
    return {"brier": {m: float(v.mean()) for m, v in brier.items()}, "bss": bss, "logscore": logs,
            "dm": pruebas, "holm": h, "calibracion": cal, "integra": integra}, "\n".join(L)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    s = cargar()
    res = evaluar(s["icociv_acero_corrugado"], s["iccp_aceros_elementos_metalicos"], s["_periodos_obj"])
    resumen, texto = resumir(res)
    DETALLE.write_text(json.dumps({**res, "resumen": resumen}, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
