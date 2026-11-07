"""Comparación 3 de PROTOCOLO_COMPARATIVO.md: intervalos de costo a 6 meses (nominal 80 %) con orígenes móviles sobre ICOCIV-carreteras.
Métodos: bootstrap por bloques (BB), normal iid (N), AR(1) con bootstrap de residuos (AR1B) y simulación histórica (HS). Uso: python comparativo_intervalos_costo.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import p3_p4_transmision_montecarlo as P  # noqa: E402  (cargar_icociv, simular)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

H, ALFA, ORIGEN_MIN, NS = 6, 0.20, 30, 3000
RNG = np.random.default_rng(20261109)


def int_bb(x):
    m = P.simular(x, H, NS); return np.percentile(m, [10, 90])


def int_n(x):
    mu, sd = x.mean() * H, x.std() * np.sqrt(H); return np.exp([mu - 1.2816 * sd, mu + 1.2816 * sd])


def int_ar1b(x):
    mu = x.mean(); y = x - mu; phi = float(np.dot(y[:-1], y[1:]) / np.dot(y[:-1], y[:-1])); e = y[1:] - phi * y[:-1]; tot = np.zeros(NS); cur = np.full(NS, y[-1])
    for _ in range(H):
        cur = phi * cur + RNG.choice(e, NS); tot += mu + cur
    return np.percentile(np.exp(tot), [10, 90])


def int_hs(x):
    acum = np.array([x[i:i + H].sum() for i in range(len(x) - H + 1)]); return np.percentile(np.exp(acum), [10, 90])


def winkler(lo, hi, y):
    return (hi - lo) + (2 / ALFA) * max(lo - y, 0) + (2 / ALFA) * max(y - hi, 0)


def main() -> None:
    ic = P.cargar_icociv(); x = np.log(ic["carreteras"]).diff().dropna().to_numpy()
    n_or = len(x) - H - ORIGEN_MIN + 1
    print(f"Serie: {len(x)} variaciones mensuales; {n_or} orígenes; tamaño efectivo ≈ {n_or / H:.0f} por solapamiento; intervalo nominal 80 % a {H} meses")
    print(f"{'método':>6} {'cobertura':>10} {'ancho medio':>12} {'Winkler':>9}  ¿cobertura en [0,65; 0,95]?")
    for nombre, f in (("BB", int_bb), ("N", int_n), ("AR1B", int_ar1b), ("HS", int_hs)):
        cob, anc, win = [], [], []
        for t in range(ORIGEN_MIN, len(x) - H + 1):
            lo, hi = f(x[:t]); y = float(np.exp(x[t:t + H].sum())); cob.append(lo <= y <= hi); anc.append(hi - lo); win.append(winkler(lo, hi, y))
        c = float(np.mean(cob)); print(f"{nombre:>6} {c:>10.2f} {np.mean(anc):>12.3f} {np.mean(win):>9.3f}  {'sí' if 0.65 <= c <= 0.95 else 'NO'}")


if __name__ == "__main__":
    main()
