"""Enmienda 1 del ítem 5 (PROTOCOLO_COSTO_PARAMETRICO.md): bootstrap por conglomerados (departamentos) de la curva de crecimiento,
efecto de diseño, estaciones efectivas, ICC y robustez de T* con comprobación de borde. Uso: python periodo_retorno_conglomerados.py"""
from __future__ import annotations

import sys
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import periodo_retorno_alcantarilla as pr  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RNG = np.random.default_rng(20261108)
N_BOOT = 1000


def icc_anova(y: np.ndarray, g: np.ndarray) -> float:
    """ICC(1) de un diseño de un factor, con tamaños desiguales."""
    u = np.unique(g); k = len(u); n = len(y); gm = y.mean()
    ni = np.array([np.sum(g == x) for x in u]); mi = np.array([y[g == x].mean() for x in u])
    msb = np.sum(ni * (mi - gm) ** 2) / (k - 1)
    msw = sum(np.sum((y[g == x] - m) ** 2) for x, m in zip(u, mi)) / (n - k)
    n0 = (n - np.sum(ni ** 2) / n) / (k - 1)
    return float((msb - msw) / (msb + (n0 - 1) * msw))


def main() -> None:
    P = pr.precios(); ok = pr.estaciones_limpias()
    X = np.array([e["x"] for e in ok]); dep = np.array([e["depto"] for e in ok])
    curva = np.median(X, axis=0); u = np.unique(dep)
    print(f"Estaciones limpias: {len(X)} en {len(u)} departamentos (mediana {int(np.median([np.sum(dep == d) for d in u]))} por departamento)")
    b_est = np.array([np.median(X[RNG.integers(0, len(X), len(X))], axis=0) for _ in range(N_BOOT)])
    idx = {d: np.where(dep == d)[0] for d in u}
    b_cl = []
    for _ in range(N_BOOT):
        ds = RNG.choice(u, len(u), replace=True)
        b_cl.append(np.median(X[np.concatenate([idx[d] for d in ds])], axis=0))
    b_cl = np.array(b_cl)
    print("\nCurva x_T = Q_T/Q_2 y banda P10-P90 por método (ancho entre paréntesis):")
    print(f"   {'T':>4} {'mediana':>8}   {'por estación':>22}   {'por departamento':>22}  efecto de diseño")
    deffs = []
    for i, t in enumerate(pr.TS[1:], 1):
        a = np.percentile(b_est[:, i], [10, 90]); c = np.percentile(b_cl[:, i], [10, 90])
        d = ((c[1] - c[0]) / (a[1] - a[0])) ** 2; deffs.append(d)
        print(f"   {t:>4} {curva[i]:>8.2f}   [{a[0]:.2f}, {a[1]:.2f}] ({a[1] - a[0]:.2f})   [{c[0]:.2f}, {c[1]:.2f}] ({c[1] - c[0]:.2f})   {d:.1f}")
    d100 = deffs[-1]
    print(f"\nEstaciones efectivas ≈ {len(X) / d100:.0f} de {len(X)} (efecto de diseño en T=100: {d100:.1f}); ICC de ln x_100 por departamento: {icc_anova(np.log(X[:, -1]), dep):.2f}")

    res, estables = {}, []
    for q2, (nom, esc) in product(pr.Q2S, pr.ESC.items()):
        for m, r in product(pr.MS, pr.RS):
            t0, _ = pr.optimo(curva, q2, m, r, esc, P)
            ac = np.mean([pr.optimo(b, q2, m, r, esc, P)[0] == t0 for b in b_cl])
            res[(q2, nom, m, r)] = (t0, ac); estables.append(ac >= pr.UMBRAL_ROBUSTO)
    ts = [v[0] for v in res.values()]; modo, n_m = Counter(ts).most_common(1)[0]
    ac_est = np.mean(estables)
    print(f"\nRobustez de T* con remuestreo por departamentos: moda T={modo} en {100 * n_m / len(ts):.0f} % de la malla; acuerdo ≥ 80 % en {100 * ac_est:.0f} % de las combinaciones (era 90 % con estaciones sueltas)")
    borde = modo == pr.TS[-1]
    print(f"Comprobación de borde (enmienda 1): T* = {modo} {'COINCIDE con el mayor T evaluado -> veredicto: NO INFORMATIVO' if borde else 'no está en el borde'}")
    pocas = [k for k, v in res.items() if v[1] < pr.UMBRAL_ROBUSTO]
    print(f"Combinaciones con acuerdo < 80 %: {len(pocas)} de {len(res)}; por (Q_2, escenario): {dict(Counter((k[0], k[1]) for k in pocas))}")


if __name__ == "__main__":
    main()
