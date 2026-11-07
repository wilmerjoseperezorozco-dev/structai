"""Distribucion del area de los poligonos SIMMA (protocolo seccion 20)."""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from scipy import stats
from shapely.geometry import Polygon
from shapely.ops import unary_union

AQUI = Path(__file__).resolve().parent
URL = "https://srvags.sgc.gov.co/arcgis/rest/services/SIMMA/Capas_Principales/MapServer/3/query"
RNG = np.random.default_rng(20261107)


def descargar() -> list[dict]:
    f = AQUI / "_cache" / "simma_poligonos.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    q = urllib.parse.urlencode({"where": "1=1", "outFields": "TIPO,SUBTIPO", "returnGeometry": "true", "outSR": 9377, "f": "json"})
    with urllib.request.urlopen(f"{URL}?{q}", timeout=120) as r:
        fs = json.load(r)["features"]
    out = []
    for x in fs:
        rings = x.get("geometry", {}).get("rings") or []
        if not rings:
            continue
        g = unary_union([Polygon(r).buffer(0) for r in rings])
        out.append({"tipo": x["attributes"]["TIPO"], "subtipo": x["attributes"]["SUBTIPO"], "area_m2": g.area})
    f.parent.mkdir(exist_ok=True)
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def ks_boot(x, dist, params, n=1000):
    d0 = stats.kstest(x, dist.cdf, args=params).statistic
    mayores = 0
    for _ in range(n):
        s = dist.rvs(*params, size=len(x), random_state=RNG.integers(1 << 31))
        p = dist.fit(s, floc=0) if dist is stats.lognorm else dist.fit(s)
        mayores += stats.kstest(s, dist.cdf, args=p).statistic >= d0
    return d0, (mayores + 1) / (n + 1)


def cola_potencia(x):
    x = np.sort(x)
    mejor = None
    for xmin in np.unique(x)[:-10]:
        t = x[x >= xmin]
        if len(t) < 20:
            break
        alfa = 1 + len(t) / np.log(t / xmin).sum()
        ks = np.max(np.abs(np.arange(1, len(t) + 1) / len(t) - (1 - (t / xmin) ** (1 - alfa))))
        if mejor is None or ks < mejor[0]:
            mejor = (ks, xmin, alfa, len(t))
    return mejor


def p_cola(a, ks_obs, xmin, alfa, n_boot=300):
    """Bootstrap semiparametrico de Clauset: cuerpo remuestreado, cola sintetica de ley de potencia; se reajusta xmin."""
    cuerpo, ntot, ncola = a[a < xmin], len(a), int((a >= xmin).sum())
    mayores = 0
    for _ in range(n_boot):
        k = RNG.binomial(ntot, ncola / ntot)
        sint = np.concatenate([RNG.choice(cuerpo, ntot - k, replace=True), xmin * (1 - RNG.random(k)) ** (-1 / (alfa - 1))])
        mayores += cola_potencia(sint)[0] >= ks_obs
    return (mayores + 1) / (n_boot + 1)


def main() -> None:
    d = descargar()
    a = np.array([r["area_m2"] for r in d if r["area_m2"] > 0])
    print(f"Poligonos con area: {len(a)}; area (m2): mediana {np.median(a):,.0f}, p90 {np.percentile(a, 90):,.0f}, p99 {np.percentile(a, 99):,.0f}, max {a.max():,.0f}")
    res = {}
    s, loc, sc = stats.lognorm.fit(a, floc=0)
    ks_ln, p_ln = ks_boot(a, stats.lognorm, (s, loc, sc))
    aic_ln = 2 * 2 - 2 * stats.lognorm.logpdf(a, s, loc, sc).sum()
    print(f"Log-normal: sigma {s:.2f}, mediana {sc:,.0f} m2 | KS {ks_ln:.3f} p {p_ln:.3f} | AIC {aic_ln:.1f}")
    try:
        pi = stats.invgamma.fit(a, floc=0)
        ks_ig, p_ig = ks_boot(a, stats.invgamma, pi)
        aic_ig = 2 * 2 - 2 * stats.invgamma.logpdf(a, *pi).sum()
        print(f"Inversa gamma: a {pi[0]:.2f}, escala {pi[2]:,.0f} | KS {ks_ig:.3f} p {p_ig:.3f} | AIC {aic_ig:.1f}")
    except Exception as e:
        print("Inversa gamma no ajustada:", str(e)[:60]); p_ig, aic_ig = 0.0, np.inf
    ks, xmin, alfa, n = cola_potencia(a)
    print(f"Cola en ley de potencia: xmin {xmin:,.0f} m2, alfa {alfa:.2f}, n cola {n}, KS {ks:.3f}")
    p_c = p_cola(a, ks, xmin, alfa)
    print(f"  p (bootstrap de Clauset) de la cola = {p_c:.3f}")
    m1 = max(p_ln, p_ig) > 0.05
    m2 = 1.5 <= alfa <= 3.5 and p_c > 0.05
    print(f"\nVEREDICTO: M1 (log-normal o inversa gamma con KS p>0.05) {'cumple' if m1 else 'NO cumple'}; M2 (cola potencia alfa en [1.5,3.5] y p>0.05) {'cumple' if m2 else 'NO cumple'}")
    res = {"n": len(a), "lognormal": {"sigma": float(s), "mediana": float(sc), "p": p_ln, "aic": float(aic_ln)}, "invgamma_aic": float(aic_ig),
           "cola": {"p": float(p_c), "xmin": float(xmin), "alfa": float(alfa), "n": int(n), "ks": float(ks)}}
    por = {}
    for r in d:
        por.setdefault(r["tipo"], []).append(r["area_m2"])
    print("\nPor tipo (n >= 30):")
    for t, v in por.items():
        print(f"  {t:<24} n={len(v):3d}", f"mediana {np.median(v):,.0f} m2" if len(v) >= 30 else "(< 30, solo conteo)")
    (AQUI / "distribucion_area_simma.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
