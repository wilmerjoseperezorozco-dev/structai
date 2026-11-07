"""P3 (reglas fijadas antes de correr): umbral CONFORME y ajuste por PROVEEDOR en la revisión de precios del catálogo IAD.

Partición aleatoria de las cotizaciones válidas: 50 % ajuste, 25 % calibración, 25 % prueba (se supone que las cotizaciones futuras vienen de los mismos proveedores).
Modelos de puntaje (todos con la misma escala por ítem, contraída hacia la global, para que solo difiera el ajuste por proveedor):
  M0  |ln p − ln mediana_ítem| / s_ítem                (como el módulo, sin piso fijo)
  M1  |ln p − a_ítem − b_proveedor| / s_ítem'          (efectos aditivos estimados con mínimos cuadrados alternados en el 50 % de ajuste)
Umbral conforme dividido (split conformal): cuantil (1 − α)(1 + 1/n) de los puntajes de calibración, α = 5 %.
Criterios: (a) tasa de marca en prueba dentro de [4 %, 6 %] para ambos modelos; (b) sensibilidad de M1 − M0 con error ×5 > 0 con IC95 % (bootstrap por ítem) que excluye 0.
Evaluación de sensibilidad por inyección sobre cotizaciones de prueba no marcadas (×2, ×3, ×5, ×10, ×0,1). Límite: la inyección es sintética y las cotizaciones
de prueba contienen errores naturales que también entran a la calibración (el umbral resultante es conservador respecto de un catálogo limpio).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261107)
ALFA, N_BOOT = 0.05, 2000
CONT = 5


def als(df: pd.DataFrame, it: int = 25):
    l = df.l.to_numpy(); a = pd.Series(0.0, index=df.item_no.unique()); b = pd.Series(0.0, index=df.prov.unique())
    for _ in range(it):
        a = pd.Series(l - df.prov.map(b).to_numpy()).groupby(df.item_no.to_numpy()).mean()
        b = pd.Series(l - df.item_no.map(a).to_numpy()).groupby(df.prov.to_numpy()).mean()
    return a, b


def escalas(res: pd.Series, item: pd.Series) -> pd.Series:
    mad = res.abs().groupby(item).median() * 1.4826
    n = res.groupby(item).size()
    glob = float(res.abs().median() * 1.4826)
    return np.sqrt((n * mad ** 2 + CONT * glob ** 2) / (n + CONT))


def boot_items(v: np.ndarray, items: np.ndarray) -> tuple[float, float]:
    u = np.unique(items); idx = {i: np.where(items == i)[0] for i in u}
    out = [v[np.concatenate([idx[i] for i in RNG.choice(u, len(u), replace=True)])].mean() for _ in range(N_BOOT)]
    return tuple(np.percentile(out, [2.5, 97.5]))


def main() -> None:
    q = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_precios_nacional_detalle.json").read_text(encoding="utf-8")))
    q["p"] = pd.to_numeric(q.precio_sin_iva, errors="coerce")
    q = q[(q.p > 0) & (q.precio_valido.astype(bool))][["item_no", "proveedor_id", "p"]].rename(columns={"proveedor_id": "prov"}).reset_index(drop=True)
    q["l"] = np.log(q.p)
    u = RNG.random(len(q)); q["parte"] = np.where(u < 0.5, "ajuste", np.where(u < 0.75, "calib", "prueba"))
    aj = q[q.parte == "ajuste"]
    n_item = aj.groupby("item_no").size(); aj = aj[aj.item_no.map(n_item) >= 15]
    a, b = als(aj)
    med = aj.groupby("item_no").l.median()
    s0 = escalas(aj.l - aj.item_no.map(med), aj.item_no)
    res1 = aj.l - aj.item_no.map(a) - aj.prov.map(b)
    s1 = escalas(res1, aj.item_no)
    print(f"Ajuste: {len(aj)} cotizaciones; ítems {aj.item_no.nunique()}; proveedores {aj.prov.nunique()}; "
          f"escala mediana por ítem: M0 {s0.median():.3f}, M1 {s1.median():.3f} (reducción {100 * (1 - s1.median() / s0.median()):.0f} %)")

    def puntaje(df: pd.DataFrame, l: np.ndarray):
        ok = df.item_no.isin(s0.index) & df.prov.isin(b.index)
        d = df[ok]; ll = l[ok.to_numpy()]
        m0 = np.abs(ll - d.item_no.map(med).to_numpy()) / d.item_no.map(s0).to_numpy()
        m1 = np.abs(ll - d.item_no.map(a).to_numpy() - d.prov.map(b).to_numpy()) / d.item_no.map(s1).to_numpy()
        return d, m0, m1
    cal, c0, c1 = puntaje(q[q.parte == "calib"], q[q.parte == "calib"].l.to_numpy())
    prue, p0, p1 = puntaje(q[q.parte == "prueba"], q[q.parte == "prueba"].l.to_numpy())
    n = len(c0); k = int(np.ceil((n + 1) * (1 - ALFA)))
    t0, t1 = float(np.sort(c0)[k - 1]), float(np.sort(c1)[k - 1])
    f0, f1 = float((p0 > t0).mean()), float((p1 > t1).mean())
    print(f"Calibración n={n}; umbral conforme (α={ALFA:.0%}): M0 |z| > {t0:.2f}; M1 |z| > {t1:.2f}")
    print(f"(a) Tasa de marca en prueba (n={len(p0)}): M0 {100 * f0:.2f} % | M1 {100 * f1:.2f} % -> criterio [4 %, 6 %]: "
          f"{'CUMPLE' if 0.04 <= f0 <= 0.06 and 0.04 <= f1 <= 0.06 else 'NO cumple'}")
    base = prue[(p0 <= t0) & (p1 <= t1)]; lb = np.log(base.p.to_numpy())
    print(f"Sensibilidad por inyección sobre {len(base)} cotizaciones de prueba no marcadas por ninguno:")
    res = {}
    for f in (2, 3, 5, 10, 0.1):
        _, m0, m1 = puntaje(base, lb + np.log(f))
        d0, d1 = (m0 > t0).astype(float), (m1 > t1).astype(float)
        dif = d1 - d0; lo, hi = boot_items(dif, base.item_no.to_numpy())
        res[str(f)] = {"M0": float(d0.mean()), "M1": float(d1.mean()), "dif": float(dif.mean()), "ic": [float(lo), float(hi)]}
        print(f"  ×{f:<4} M0 {d0.mean():.3f} | M1 {d1.mean():.3f} | M1−M0 = {dif.mean():+.3f} IC95% [{lo:+.3f}, {hi:+.3f}]")
    print(f"(b) Criterio M1−M0 > 0 con error ×5 (IC excluye 0): {'CUMPLE' if res['5']['ic'][0] > 0 else 'NO cumple'}")
    (AQUI / "p3_resultados.json").write_text(json.dumps({"umbral_M0": t0, "umbral_M1": t1, "marca_M0": f0, "marca_M1": f1,
                                                          "escala_mediana": {"M0": float(s0.median()), "M1": float(s1.median())}, "sensibilidad": res}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
