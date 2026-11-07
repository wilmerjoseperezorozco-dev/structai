"""Analisis CONFIRMATORIO: relieve x inundaciones reportadas (UNGRD) en 7 departamentos del
Caribe (issue #95, Frente C). Sigue PROTOCOLO_ANALISIS.md, incluida la enmienda de la
seccion 8 (fijada tras la auditoria y ANTES de ver ninguna asociacion).

Resultado principal Y: eventos de inundacion por 100 000 habitantes (poblacion DANE 2020),
todos los municipios (sin excluir por pocos reportes).
Predictor principal (unico confirmatorio): fraccion del municipio bajo 10 m.
Secundarios (Holm, bajo la especificacion principal): IGAC fraccion con inundacion,
elevacion media (invertida), pendiente media (invertida) -- cada uno por separado.
Estimador: correlacion PARCIAL de Spearman (residuos de rangos) controlando por log(poblacion)
y log(area). IC95 % por remuestreo de DEPARTAMENTOS (bloques). Efecto + IC; p solo informativo.
Curva de especificaciones: 3 variantes de Y x 5 conjuntos de controles.
Replicacion por departamento y "dejar un departamento fuera".
Veredicto con regla fija (protocolo, seccion 8.6).
"""
from __future__ import annotations

import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr, t as t_dist

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "eval-stats" / "src"))
import _datos_caribe as dc  # noqa: E402
import estadistica as est  # noqa: E402

N_BOOT = 5_000
MIN_BLOQUE = 8
RNG = np.random.default_rng(est.SEMILLA)


def residuos_rangos(v: np.ndarray, Z: np.ndarray | None) -> np.ndarray:
    r = rankdata(v)
    if Z is None or Z.shape[1] == 0:
        return r - r.mean()
    A = np.column_stack([np.ones(len(r))] + [rankdata(Z[:, j]) for j in range(Z.shape[1])])
    return r - A @ np.linalg.lstsq(A, r, rcond=None)[0]


def parcial(x, y, Z) -> float:
    ex, ey = residuos_rangos(x, Z), residuos_rangos(y, Z)
    if ex.std() == 0 or ey.std() == 0:
        return float("nan")
    return float(np.corrcoef(ex, ey)[0, 1])


def p_ingenuo(r: float, n: int, k: int) -> float:
    """p de la correlacion parcial por t con n-2-k gl. ANTICONSERVADOR: ignora la
    dependencia espacial (I de Moran alto). Solo informativo; la inferencia es el IC por bloques."""
    t = r * np.sqrt((n - 2 - k) / max(1e-12, 1 - r * r))
    return float(2 * t_dist.sf(abs(t), n - 2 - k))


def ic_bloques(x, y, Z, bloques) -> tuple[float, float]:
    etiquetas = np.unique(bloques)
    bs = []
    for _ in range(N_BOOT):
        idx = np.concatenate([np.where(bloques == b)[0] for b in RNG.choice(etiquetas, len(etiquetas), replace=True)])
        r = parcial(x[idx], y[idx], None if Z is None else Z[idx])
        if not np.isnan(r):
            bs.append(r)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def moran(v, xy, k=8, perm=999):
    n = len(v)
    d = np.hypot(xy[:, None, 0] - xy[None, :, 0], xy[:, None, 1] - xy[None, :, 1])
    np.fill_diagonal(d, np.inf)
    W = np.zeros((n, n))
    for i in range(n):
        W[i, np.argsort(d[i])[:k]] = 1 / k

    def I(a):
        z = a - a.mean()
        return float((n / W.sum()) * (z @ W @ z) / (z @ z))

    obs = I(v)
    return obs, (1 + sum(abs(I(RNG.permutation(v))) >= abs(obs) for _ in range(perm))) / (perm + 1)


def main() -> None:
    dem = [m for m in dc.dem() if "error" not in m]
    pols = dc.poligonos()
    cod = [m["codigo"] for m in dem]
    ung = dc.ungrd(cod)
    ig = dc.igac(cod)
    pob = dc.poblacion_dane(cod)

    raw, dedup, raw22, total = (defaultdict(int) for _ in range(4))
    vistos = set()
    for r in ung:
        c = r["codigo_municipio"]
        total[c] += 1
        if r["evento"] in dc.EVENTOS_INUNDACION:
            raw[c] += 1
            if not str(r["fecha"]).startswith("2022"):
                raw22[c] += 1
            clave = (c, r["fecha"], r["evento"], r["personas"], r["familias"], r["viviendas_destruidas"], r["viviendas_averiadas"], r["hectareas"])
            if clave not in vistos:
                vistos.add(clave)
                dedup[c] += 1
    filas = [m for m in dem if m["codigo"] in pob and m["codigo"] in ig and m["codigo"] in pols]
    n = len(filas)
    c_ = [m["codigo"] for m in filas]
    P = np.array([pob[c]["poblacion"] for c in c_])
    A = np.array([pols[c]["area_km2"] for c in c_])
    CAB = np.array([pob[c]["pct_cabecera"] for c in c_])
    TOT = np.array([total[c] for c in c_], float)
    bloques = np.array([m["depto"] for m in filas])
    xy = np.array([pols[c]["centroide"] for c in c_])
    tasa = lambda d: np.array([d[c] for c in c_], float) / P * 1e5
    Y = {"principal (conteo crudo)": tasa(raw), "duplicados colapsados": tasa(dedup), "sin 2022": tasa(raw22)}

    X = {"fraccion < 10 m [PRINCIPAL]": np.array([m["frac_bajo_10m"] for m in filas]),
         "IGAC fraccion con inundacion": np.array([ig[c]["frac_inundable"] for c in c_]),
         "elevacion media (invertida)": -np.array([m["elev_media_m"] for m in filas]),
         "pendiente media (invertida)": -np.array([m["pend_media_pct"] for m in filas])}
    x0 = X["fraccion < 10 m [PRINCIPAL]"]
    CONTROLES = {"sin controles": None,
                 "log(pob)": np.column_stack([np.log(P)]),
                 "log(pob)+log(area) [PRINCIPAL]": np.column_stack([np.log(P), np.log(A)]),
                 "log(pob)+log(area)+%cabecera": np.column_stack([np.log(P), np.log(A), CAB]),
                 "log(pob)+total reportes [ILUSTRATIVA, sesgada]": np.column_stack([np.log(P), np.log(TOT)])}
    ZP = CONTROLES["log(pob)+log(area) [PRINCIPAL]"]

    print(f"n = {n} municipios | inundaciones: crudo {int(sum(raw[c] for c in c_))}, colapsado {int(sum(dedup[c] for c in c_))}")
    y0 = Y["principal (conteo crudo)"]
    print(f"Tasa de inundacion por 100 mil hab.: mediana {np.median(y0):.1f}, media {y0.mean():.1f}, DE {y0.std(ddof=1):.1f}, max {y0.max():.0f}")
    print(f"Predictor principal: {(x0 == 0).mean() * 100:.0f} % de municipios tienen valor 0 (empates)")

    print("\n== CURVA DE ESPECIFICACIONES del predictor principal (correlacion parcial de Spearman, IC95 % por bloques) ==")
    print(f"{'resultado':<28}{'controles':<50}{'rho':>7}{'IC95% bloques':>20}")
    cel = {}
    for yn, y in Y.items():
        for cn, Z in CONTROLES.items():
            r = parcial(x0, y, Z)
            lo, hi = ic_bloques(x0, y, Z, bloques)
            cel[(yn, cn)] = (r, lo, hi)
            print(f"{yn:<28}{cn:<50}{r:7.2f}  [{lo:6.2f}, {hi:6.2f}]")

    print("\n== PREDICTORES (resultado principal, controles principales) ==")
    sec = []
    print(f"{'predictor':<34}{'rho parcial':>12}{'IC95% bloques':>20}{'p ingenuo*':>12}{'p_holm*':>9}")
    res_x = {}
    for xn, xv in X.items():
        r = parcial(xv, y0, ZP)
        lo, hi = ic_bloques(xv, y0, ZP, bloques)
        res_x[xn] = (r, lo, hi, p_ingenuo(r, n, ZP.shape[1]))
        if "PRINCIPAL" not in xn:
            sec.append(res_x[xn][3])
    ph = est.holm(sec)
    k = 0
    for xn, (r, lo, hi, p) in res_x.items():
        h = "" if "PRINCIPAL" in xn else f"{ph[k]:.3f}"
        k += 0 if "PRINCIPAL" in xn else 1
        print(f"{xn:<34}{r:12.2f}  [{lo:6.2f}, {hi:6.2f}]{p:12.4f}{h:>9}")
    print("* p ingenuo: ignora la dependencia espacial (anticonservador); la inferencia es el IC por bloques.")

    print("\n== REPLICACION POR DEPARTAMENTO (predictor principal, controles principales) ==")
    signos = []
    for b in sorted(set(bloques)):
        m = bloques == b
        if m.sum() >= MIN_BLOQUE and np.ptp(x0[m]) > 0:
            r = parcial(x0[m], y0[m], ZP[m])
            signos.append(np.sign(r))
            print(f"  {b:<12} rho {r:+.2f} (n={int(m.sum())})")
    print(f"  signo positivo en {int(sum(s > 0 for s in signos))} de {len(signos)} departamentos")
    loo = [parcial(x0[bloques != b], y0[bloques != b], ZP[bloques != b]) for b in sorted(set(bloques))]
    print(f"  dejando un departamento fuera: rho {min(loo):.2f} a {max(loo):.2f}")

    rp = residuos_rangos(y0, ZP)
    I, pI = moran(rp, xy)
    print(f"\nI de Moran de los residuos de Y tras los controles: {I:.2f} (p={pI:.3f}) -> "
          f"{'persiste dependencia espacial' if pI < 0.05 else 'sin dependencia espacial detectable'}")

    # ---- Sensibilidad: excluir zonas mudas (< 10 reportes)
    m10 = TOT >= 10
    r10 = parcial(x0[m10], y0[m10], ZP[m10])
    lo10, hi10 = ic_bloques(x0[m10], y0[m10], ZP[m10], bloques[m10])
    print(f"Sensibilidad excluyendo zonas mudas (< 10 reportes, n={int(m10.sum())}): rho {r10:.2f} [{lo10:.2f}, {hi10:.2f}]")

    # ---- Veredicto (regla fija, protocolo 8.6)
    r, lo, hi = cel[("principal (conteo crudo)", "log(pob)+log(area) [PRINCIPAL]")]
    asoc = lo > 0 or hi < 0
    legit = [v for (yn, cn), v in cel.items() if "ILUSTRATIVA" not in cn]
    robusta = asoc and all((v[1] > 0 if r > 0 else v[2] < 0) for v in legit)
    if not asoc:
        veredicto = "el IC por bloques de la especificacion principal incluye 0: NO hay evidencia de asociacion"
    elif robusta:
        veredicto = f"asociacion {'positiva' if r > 0 else 'negativa'} y ROBUSTA en todas las especificaciones no ilustrativas"
    else:
        veredicto = "hay asociacion en la especificacion principal pero NO es robusta: cambia de signo o incluye 0 en otras especificaciones"
    print(f"\nVEREDICTO (regla fija): {veredicto}")
    print("\nLIMITES: UNGRD mide reportes, no inundaciones; DEM = superficie; poligonos IGAC simplificados; 7 bloques = IC "
          "muy ancho; el predictor principal tiene muchos ceros; analisis ecologico (municipal), no inferencia sobre predios.")
    (AQUI / "cruce_relieve_ungrd_caribe.json").write_text(json.dumps({
        "n": n, "veredicto": veredicto,
        "curva": {f"{yn} | {cn}": {"rho": v[0], "ic_bloques": [v[1], v[2]]} for (yn, cn), v in cel.items()},
        "predictores": {k: {"rho": v[0], "ic_bloques": [v[1], v[2]]} for k, v in res_x.items()},
        "sens_sin_zonas_mudas": {"rho": r10, "ic": [lo10, hi10], "n": int(m10.sum())}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
