"""Validacion del piloto satelital (issue #95, Frente C): ¿la senal satelital se
asocia con los eventos REALES de inundacion de UNGRD, mas alla del relieve solo?

Diseno declarado ANTES de mirar resultados:
- Unidad: municipio del Atlantico (n = 23). Resultado: conteo de eventos de
  inundacion/creciente subita/avenida torrencial de UNGRD 2019-2024.
- Predictor PRINCIPAL (unico confirmatorio): fraccion de agua OCASIONAL
  Sentinel-1 (umbral -18 dB). Los demas son secundarios, con correccion de Holm.
- Linea base: relieve solo (fraccion < 10 m, elevacion y pendiente del DEM).
  El satelite solo "aporta" si su rho supera al de la linea base; se reporta
  la diferencia con IC bootstrap, no solo si p < 0.05.
- Sensibilidad: sin 2022 (ano extremo de lluvias, 3-4x los eventos normales),
  y leave-one-out.

Limites que NO se pueden resolver con estos datos (se imprimen al final):
- n = 23 es muy poco: baja potencia, IC anchos. Esto es una validacion de
  humo, NO un modelo. La validacion espacial por bloques exige mas departamentos.
- UNGRD mide REPORTES, no inundaciones: municipios grandes/organizados reportan
  mas. No se normaliza por poblacion (no hay dato aqui); el sesgo queda declarado.
- Desfase temporal: UNGRD 2019-2024 vs satelite nov-2025 a oct-2026. Se usa el
  satelite como indicador de susceptibilidad ESTRUCTURAL, supone paisaje estable.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
from dotenv import dotenv_values
from scipy.stats import spearmanr
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "packages" / "eval-stats" / "src"))
import estadistica as est  # noqa: E402

EVENTOS = ["INUNDACION", "INUNDACIÓN", "INUNDACIoN", "CRECIENTE SUBITA", "Creciente Subita", "AVENIDA TORRENCIAL"]
N_BOOT = 10_000
RNG = np.random.default_rng(est.SEMILLA)


def eventos_ungrd() -> tuple[dict[str, int], dict[str, int]]:
    env = dotenv_values(RAIZ / "apps/api/.env")
    sb = create_client(env["SUPABASE_URL"], env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_KEY"])
    total: dict[str, int] = {}
    sin22: dict[str, int] = {}
    inicio = 0
    while True:
        pag = (sb.table("ungrd_emergencias").select("codigo_municipio,fecha,evento,departamento")
               .in_("evento", EVENTOS).ilike("departamento", "atl%").range(inicio, inicio + 999).execute().data or [])
        for r in pag:
            c = r["codigo_municipio"]
            if not c:
                continue  # fila a nivel "DEPARTAMENTO", no atribuible a un municipio
            total[c] = total.get(c, 0) + 1
            if not str(r["fecha"]).startswith("2022"):
                sin22[c] = sin22.get(c, 0) + 1
        if len(pag) < 1000:
            break
        inicio += 1000
    return total, sin22


def rho_ic(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    rho, p = spearmanr(x, y)
    n = len(x)
    bs = []
    for _ in range(N_BOOT):
        i = RNG.integers(0, n, n)
        if np.ptp(x[i]) == 0 or np.ptp(y[i]) == 0:
            continue
        bs.append(spearmanr(x[i], y[i])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(rho), float(p), float(lo), float(hi)


def main() -> None:
    agua = {m["codigo"]: m for m in json.load(open(AQUI / "agua_s1_ATLANTICO.json", encoding="utf-8"))["municipios"]}
    dem = {m["codigo"]: m for m in json.load(open(AQUI / "dem_ATLANTICO.json", encoding="utf-8"))["municipios"]}
    total, sin22 = eventos_ungrd()
    codigos = sorted(set(agua) & set(dem))
    y = np.array([total.get(c, 0) for c in codigos], float)
    y22 = np.array([sin22.get(c, 0) for c in codigos], float)
    print(f"n = {len(codigos)} municipios | eventos de inundacion UNGRD: total {int(y.sum())}, sin 2022 {int(y22.sum())}")

    preds = {  # nombre: (vector, es_principal, es_satelite)
        "S1 agua ocasional (-18 dB)  [PRINCIPAL]": (np.array([agua[c]["frac_ocasional_18"] for c in codigos]), True, True),
        "S1 agua maxima por escena": (np.array([agua[c]["agua_max_18"] for c in codigos]), False, True),
        "S1 agua permanente": (np.array([agua[c]["frac_permanente_18"] for c in codigos]), False, True),
        "DEM fraccion < 10 m": (np.array([dem[c]["frac_bajo_10m"] for c in codigos]), False, False),
        "DEM elevacion media (invertida)": (-np.array([dem[c]["elev_media_m"] for c in codigos]), False, False),
        "DEM pendiente media (invertida)": (-np.array([dem[c]["pend_media_pct"] for c in codigos]), False, False),
    }
    filas = []
    for nombre, (x, _, _) in preds.items():
        filas.append((nombre, rho_ic(x, y), rho_ic(x, y22)[0]))
    pv = est.holm([f[1][1] for f in filas[1:]])
    print(f"\n{'predictor':<42}{'rho':>7}{'IC95%':>17}{'p':>8}{'p_holm':>8}{'rho sin2022':>13}")
    for k, (nombre, (rho, p, lo, hi), r22) in enumerate(filas):
        ph = "" if k == 0 else f"{pv[k-1]:.3f}"
        print(f"{nombre:<42}{rho:7.2f}  [{lo:5.2f},{hi:5.2f}]{p:8.3f}{ph:>8}{r22:13.2f}")

    # ¿Aporta el satelite sobre el relieve? diferencia pareada de rho (bootstrap sobre municipios)
    xs = preds["S1 agua ocasional (-18 dB)  [PRINCIPAL]"][0]
    xb = preds["DEM fraccion < 10 m"][0]
    dif = []
    for _ in range(N_BOOT):
        i = RNG.integers(0, len(y), len(y))
        if min(np.ptp(xs[i]), np.ptp(xb[i]), np.ptp(y[i])) == 0:
            continue
        dif.append(spearmanr(xs[i], y[i])[0] - spearmanr(xb[i], y[i])[0])
    lo, hi = np.percentile(dif, [2.5, 97.5])
    d0 = filas[0][1][0] - filas[3][1][0]
    print(f"\nrho(S1 ocasional) - rho(DEM <10 m) = {d0:+.2f}  IC95% [{lo:+.2f}, {hi:+.2f}]"
          f"  -> {'el IC incluye 0: no hay evidencia de que el satelite aporte sobre el relieve' if lo <= 0 <= hi else 'el IC excluye 0'}")

    # leave-one-out del predictor principal
    loo = []
    for j in range(len(y)):
        m = np.arange(len(y)) != j
        loo.append(spearmanr(xs[m], y[m])[0])
    print(f"Leave-one-out rho principal: min {min(loo):.2f}, max {max(loo):.2f} (rango = sensibilidad a un solo municipio)")

    print("\nLIMITES: n=23 (baja potencia); UNGRD mide reportes, no inundaciones; desfase temporal 2019-24 vs 2025-26;"
          " poligonos IGAC generalizados. Validacion de humo, no modelo.")
    (AQUI / "validacion_agua_vs_ungrd.json").write_text(json.dumps({
        "n": len(codigos), "filas": [{"predictor": n, "rho": r[0], "p": r[1], "ic": [r[2], r[3]], "rho_sin2022": r22}
                                     for n, r, r22 in filas],
        "dif_rho_s1_menos_dem": {"valor": d0, "ic": [float(lo), float(hi)]}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
