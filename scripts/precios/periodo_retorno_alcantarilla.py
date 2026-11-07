"""Ítem 5 (PROTOCOLO_COSTO_PARAMETRICO.md): periodo de retorno económico de una alcantarilla de cajón.
Curva de crecimiento (índice de crecida) del subconjunto limpio de estaciones IDEAM × costo de obra INVIAS 2026-1 × pérdida esperada por falla.
Ejercicio ilustrativo de sensibilidad: NO es un diseño. Reglas, supuestos y criterios fijados en el protocolo antes de correr.
Uso: python periodo_retorno_alcantarilla.py"""
from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
import _datos_caribe as dc  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TS = [2, 5, 10, 25, 50, 100]
CARIBE = {"ATLANTICO", "BOLIVAR", "CESAR", "CORDOBA", "LA GUAJIRA", "GUAJIRA", "MAGDALENA", "SUCRE"}
NUM = {"concreto": "630,1,1", "acero": "640,1", "excavacion": "600,2,3", "relleno": "610,1"}
PROV_REF = "0801"
Q2S, MS, RS, ESC = (2.0, 10.0), (0.5, 1.0, 2.0, 5.0, 10.0), (0.04, 0.08, 0.12), {"nominal": 1.0, "pesimista": 1.35}
VIDA, LONG, H_CARGA, CD, ACERO_KG_M3, EXTRA = 30, 10.0, 1.5, 0.6, 100.0, 1.25
N_BOOT, UMBRAL_ROBUSTO = 1000, 0.80
RNG = np.random.default_rng(20261107)


def precios() -> dict:
    cache = AQUI / "_cache" / "costo_alcantarilla_precios.json"
    if not cache.exists():
        filas = (dc._sb().table("invias_actividad_costos").select("numeral,costo_directo_total")
                 .eq("provincia_codigo", PROV_REF).in_("numeral", list(NUM.values())).execute().data)
        cache.parent.mkdir(exist_ok=True); cache.write_text(json.dumps(filas), encoding="utf-8")
    filas = json.loads(cache.read_text(encoding="utf-8"))
    inv = {v: k for k, v in NUM.items()}
    return {inv[f["numeral"]]: float(f["costo_directo_total"]) for f in filas}


def estaciones_limpias() -> list[dict]:
    est = json.loads((AQUI.parent / "satelite" / "frecuencia_crecientes_ideam.json").read_text(encoding="utf-8"))
    ok = []
    for e in est:
        q = e.get("q_gev") or {}
        if (e["n"] >= 30 and e["p_ks"] is not None and e["p_ks"] >= 0.10 and e["mk_p"] is not None and e["mk_p"] >= 0.10 and e["rep"] <= 0.10
                and all(str(t) in q and np.isfinite(q[str(t)]) and q[str(t)] > 0 for t in TS)):
            ok.append({"depto": e["depto"], "x": np.array([q[str(t)] / q["2"] for t in TS])})
    return ok


def costo_inversion(q: float, P: dict) -> float:
    area = q / (CD * np.sqrt(2 * 9.81 * H_CARGA))
    b = max(0.9, float(np.sqrt(area))); t = max(0.20, b / 12)
    ext = b + 2 * t
    v_conc = (ext ** 2 - b ** 2) * LONG
    exc = (ext + 1.0) * (ext + 0.5) * LONG
    relleno = exc - ext ** 2 * LONG
    cuerpo = v_conc * P["concreto"] + v_conc * ACERO_KG_M3 * P["acero"] + exc * P["excavacion"] + relleno * P["relleno"]
    return EXTRA * cuerpo


def optimo(curva: np.ndarray, q2: float, m: float, r: float, esc: float, P: dict) -> tuple[int, np.ndarray]:
    cinv = np.array([costo_inversion(q2 * x, P) for x in curva])
    perdida = m * cinv[TS.index(25)]
    fvp = sum(1 / (1 + r) ** k for k in range(1, VIDA + 1))
    p = np.minimum(1.0, esc / np.array(TS, float))
    total = cinv + perdida * p * fvp
    return TS[int(np.argmin(total))], total


def main() -> None:
    P = precios()
    print(f"Precios INVIAS 2026-1, provincia {PROV_REF} (COP): " + ", ".join(f"{k}={v:,.0f}" for k, v in P.items()))
    ok = estaciones_limpias()
    cnt = Counter(e["depto"] for e in ok)
    car = [e for e in ok if e["depto"] in CARIBE]
    print(f"Estaciones limpias (n≥30, KS≥0,10, MK≥0,10, repetidos≤10 %): {len(ok)} nacional; {len(car)} en el Caribe. Por departamento: {dict(cnt.most_common(8))}")
    base = car if len(car) >= 15 else ok
    nombre = "Caribe" if base is car else "nacional"
    X = np.array([e["x"] for e in base])
    curva = np.median(X, axis=0)
    boots = np.array([np.median(X[RNG.integers(0, len(X), len(X))], axis=0) for _ in range(N_BOOT)])
    print(f"\nAnálisis principal: {nombre} ({len(base)} estaciones). Curva de crecimiento x_T = Q_T/Q_2 (mediana; banda P10-P90 del bootstrap de estaciones):")
    for i, t in enumerate(TS):
        print(f"   T={t:>3}: {curva[i]:.2f}   [{np.percentile(boots[:, i], 10):.2f}, {np.percentile(boots[:, i], 90):.2f}]")
    cv100 = float(np.std(X[:, -1]) / np.mean(X[:, -1]))
    print(f"   Heterogeneidad: CV de x_100 entre estaciones = {cv100:.2f}; nacional vs analizado, mediana x_100: {np.median([e['x'][-1] for e in ok]):.2f} vs {curva[-1]:.2f}")

    resultados, estables = {}, []
    for q2, (nom_esc, esc) in product(Q2S, ESC.items()):
        print(f"\nT* (años) con Q_2 = {q2:g} m³/s, probabilidad {nom_esc}; filas = pérdida m × C_inv(T=25), columnas = tasa de descuento")
        print("          " + "".join(f"{int(100 * r):>8}%" for r in RS))
        for m in MS:
            fila = []
            for r in RS:
                t_ast, _ = optimo(curva, q2, m, r, esc, P)
                acuerdo = np.mean([optimo(b, q2, m, r, esc, P)[0] == t_ast for b in boots])
                resultados[f"{q2}|{esc}|{m}|{r}"] = {"T": t_ast, "acuerdo_bootstrap": float(acuerdo)}
                estables.append(acuerdo >= UMBRAL_ROBUSTO)
                fila.append(f"{t_ast:>4} ({100 * acuerdo:>3.0f})")
            print(f"   m={m:>4}: " + "  ".join(fila))
    ts = [v["T"] for v in resultados.values()]
    modo, n_modo = Counter(ts).most_common(1)[0]
    print(f"\nRobustez (criterio del protocolo: mismo T* en ≥ 80 % de la malla y en ≥ 80 % de los remuestreos):")
    print(f"   Distribución de T* en las {len(ts)} combinaciones: {dict(sorted(Counter(ts).items()))}; moda T={modo} en {100 * n_modo / len(ts):.0f} % de la malla")
    print(f"   Combinaciones con acuerdo bootstrap ≥ 80 %: {100 * np.mean(estables):.0f} %")
    robusto = n_modo / len(ts) >= 0.8 and np.mean(estables) >= 0.8
    print(f"   Veredicto: {'recomendación robusta' if robusto else 'SIN recomendación robusta: el óptimo depende de los supuestos de pérdida y descuento'}")
    cinv = {t: costo_inversion(Q2S[0] * x, P) for t, x in zip(TS, curva)}
    print("\nCosto de inversión (Q_2 = 2 m³/s), COP millones: " + ", ".join(f"T={t}: {v / 1e6:.1f}" for t, v in cinv.items()))
    (AQUI / "periodo_retorno_alcantarilla.json").write_text(json.dumps({"base": nombre, "n_est": len(base), "curva": curva.tolist(), "cv_x100": cv100,
                                                                     "resultados": resultados, "robusto": bool(robusto)}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
