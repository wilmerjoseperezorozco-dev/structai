"""Predictor confirmatorio-2: altura sobre el cauce (HAND) x inundaciones reportadas (UNGRD)
en el Caribe (issue #95). Definicion en PROTOCOLO_ANALISIS.md seccion 9, fijada antes de
calcular asociaciones. Mismas reglas que cruzar_relieve_ungrd_caribe.py (resultado por 100 mil
hab., correlacion parcial de Spearman controlando log(poblacion) y log(area), IC95 % por bloques
de departamentos, regla de veredicto fija).

ESTATUS: exploratorio respecto al analisis anterior (se propuso tras un resultado nulo).
Predictor principal: fraccion con HAND < 10 m, red de 5 km2. Sensibilidad: otros umbrales de
red y cortes. Comparacion directa con el predictor anterior (fraccion < 10 m de elevacion).
"""
from __future__ import annotations

import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

# La salida UTF-8 la configura cruzar_relieve_ungrd_caribe al importarse; envolverla dos veces cierra el flujo.
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402
import cruzar_relieve_ungrd_caribe as base  # noqa: E402  (funciones estadisticas compartidas)


def main() -> None:
    dem = {m["codigo"]: m for m in dc.dem() if "error" not in m}
    hand = {m["codigo"]: m for m in json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"]
            if "hand_mediana_5" in m}
    pols = dc.poligonos()
    cod = [c for c in dem if c in hand]
    pob = dc.poblacion_dane(cod)
    ung = dc.ungrd(cod)
    raw, dedup, raw22 = (defaultdict(int) for _ in range(3))
    vistos = set()
    for r in ung:
        if r["evento"] in dc.EVENTOS_INUNDACION:
            c = r["codigo_municipio"]
            raw[c] += 1
            if not str(r["fecha"]).startswith("2022"):
                raw22[c] += 1
            k = (c, r["fecha"], r["evento"], r["personas"], r["familias"], r["viviendas_destruidas"], r["viviendas_averiadas"], r["hectareas"])
            if k not in vistos:
                vistos.add(k)
                dedup[c] += 1
    cod = [c for c in cod if c in pob]
    n = len(cod)
    P = np.array([pob[c]["poblacion"] for c in cod])
    A = np.array([pols[c]["area_km2"] for c in cod])
    bloques = np.array([hand[c]["depto"] for c in cod])
    Z = np.column_stack([np.log(P), np.log(A)])
    tasa = lambda d: np.array([d[c] for c in cod], float) / P * 1e5
    Y = {"principal (conteo crudo)": tasa(raw), "duplicados colapsados": tasa(dedup), "sin 2022": tasa(raw22)}
    y0 = Y["principal (conteo crudo)"]

    H = {"HAND<10 m, red 5 km2 [PRINCIPAL-2]": np.array([hand[c]["frac_hand_lt10_5"] for c in cod]),
         "HAND<10 m, red 1 km2": np.array([hand[c]["frac_hand_lt10_1"] for c in cod]),
         "HAND<10 m, red 25 km2": np.array([hand[c]["frac_hand_lt10_25"] for c in cod]),
         "HAND<5 m, red 5 km2": np.array([hand[c]["frac_hand_lt5_5"] for c in cod]),
         "HAND<15 m, red 5 km2": np.array([hand[c]["frac_hand_lt15_5"] for c in cod]),
         "HAND mediana invertida, red 5 km2": -np.array([hand[c]["hand_mediana_5"] for c in cod])}
    ant = np.array([dem[c]["frac_bajo_10m"] for c in cod])
    x0 = H["HAND<10 m, red 5 km2 [PRINCIPAL-2]"]

    print(f"n = {n} municipios | {(x0 == 0).mean() * 100:.0f} % con valor 0 en el predictor HAND principal "
          f"(antes: {(ant == 0).mean() * 100:.0f} %)")
    print(f"Coincidencia HAND<10 m con la fraccion < 10 m de elevacion: rho = {spearmanr(x0, ant)[0]:.2f}")
    ig = dc.igac(cod)
    print(f"Coincidencia HAND<10 m con IGAC inundable: rho = {spearmanr(x0, [ig[c]['frac_inundable'] for c in cod])[0]:.2f}")

    print("\n== Predictor HAND principal-2: curva de resultados (controles log(pob)+log(area)) ==")
    cel = {}
    for yn, y in Y.items():
        r = base.parcial(x0, y, Z)
        lo, hi = base.ic_bloques(x0, y, Z, bloques)
        cel[yn] = (r, lo, hi)
        print(f"  {yn:<28} rho {r:6.2f}  IC95% bloques [{lo:6.2f}, {hi:6.2f}]")

    print("\n== Sensibilidad de la definicion de HAND (resultado principal) ==")
    for nombre, x in H.items():
        r = base.parcial(x, y0, Z)
        lo, hi = base.ic_bloques(x, y0, Z, bloques)
        print(f"  {nombre:<40} rho {r:6.2f}  [{lo:6.2f}, {hi:6.2f}]")

    print("\n== Comparacion directa con el predictor anterior (mismo resultado y controles) ==")
    r_a, lo_a, hi_a = base.parcial(ant, y0, Z), *base.ic_bloques(ant, y0, Z, bloques)
    r_h, lo_h, hi_h = cel["principal (conteo crudo)"]
    print(f"  fraccion < 10 m de elevacion: {r_a:6.2f} [{lo_a:6.2f}, {hi_a:6.2f}]")
    print(f"  HAND < 10 m (5 km2):          {r_h:6.2f} [{lo_h:6.2f}, {hi_h:6.2f}]")

    print("\n== Replicacion por departamento (HAND principal-2) ==")
    signos = []
    for b in sorted(set(bloques)):
        m = bloques == b
        if m.sum() >= base.MIN_BLOQUE and np.ptp(x0[m]) > 0:
            r = base.parcial(x0[m], y0[m], Z[m])
            signos.append(np.sign(r))
            print(f"  {b:<4} rho {r:+.2f} (n={int(m.sum())})")
    print(f"  signo positivo en {int(sum(s > 0 for s in signos))} de {len(signos)} departamentos")
    loo = [base.parcial(x0[bloques != b], y0[bloques != b], Z[bloques != b]) for b in sorted(set(bloques))]
    print(f"  dejando un departamento fuera: rho {min(loo):.2f} a {max(loo):.2f}")

    r, lo, hi = cel["principal (conteo crudo)"]
    asoc = lo > 0 or hi < 0
    robusto = asoc and all((v[1] > 0 if r > 0 else v[2] < 0) for v in cel.values())
    if not asoc:
        veredicto = "el IC por bloques incluye 0: NO hay evidencia de asociacion con HAND"
    elif robusto:
        veredicto = f"asociacion {'positiva' if r > 0 else 'negativa'} y ROBUSTA entre variantes del resultado"
    else:
        veredicto = "hay asociacion con el resultado principal pero NO es robusta entre variantes"
    print(f"\nVEREDICTO (regla fija): {veredicto}")
    print("ESTATUS: exploratorio respecto al analisis anterior; no se presenta como confirmacion. "
          "LIMITES: UNGRD mide reportes; DEM 90 m de superficie; umbral de red es una eleccion; 7 bloques = IC ancho.")
    (AQUI / "cruce_hand_ungrd_caribe.json").write_text(json.dumps({
        "n": n, "veredicto": veredicto, "principal2": {k: {"rho": v[0], "ic_bloques": [v[1], v[2]]} for k, v in cel.items()},
        "anterior": {"rho": r_a, "ic_bloques": [lo_a, hi_a]}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
