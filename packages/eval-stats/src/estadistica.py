"""
Estadística para evaluar un sistema RAG -- issue #95, Frente A0.

Reglas que este módulo hace cumplir (para que ningún análisis las olvide):
- Los valores faltantes (NaN) NUNCA se rellenan en silencio: se descartan y se
  informa cuántos fueron. Un promedio sin su n real engaña.
- Toda comparación entre dos configuraciones es PAREADA por pregunta; solo
  entran los pares donde ambos lados tienen valor.
- Toda prueba reporta el tamaño de efecto y un IC, no solo el p-valor.
- Con varias pruebas a la vez, corregir con Holm (`holm`).

Solo depende de numpy y scipy. Semilla fija: los resultados son reproducibles.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
from scipy import stats

SEMILLA = 20261106
N_REMUESTREOS = 10_000
NIVEL = 0.95
ALFA_NORMALIDAD = 0.05


def _a_float(valores) -> np.ndarray:
    return np.asarray(valores, dtype=float)


def _validos(valores) -> np.ndarray:
    arr = _a_float(valores)
    return arr[~np.isnan(arr)]


def _bootstrap_ic(v: np.ndarray, *, nivel: float, n_remuestreos: int, semilla: int) -> tuple[float, float]:
    """IC bootstrap de la media. BCa; si BCa no es calculable (muestra muy
    chica o degenerada) cae a percentil -- nunca devuelve NaN en silencio."""
    n = len(v)
    if n == 0:
        return (math.nan, math.nan)
    media = float(v.mean())
    if n < 2 or float(np.ptp(v)) == 0.0:
        return (media, media)
    for metodo in ("BCa", "percentile"):
        try:
            r = stats.bootstrap(
                (v,), np.mean, confidence_level=nivel, n_resamples=n_remuestreos,
                method=metodo, random_state=np.random.default_rng(semilla),
            )
            lo, hi = float(r.confidence_interval.low), float(r.confidence_interval.high)
            if math.isfinite(lo) and math.isfinite(hi):
                return (lo, hi)
        except Exception:
            continue
    return (math.nan, math.nan)


def ic_bootstrap_media(valores, *, nivel: float = NIVEL, n_remuestreos: int = N_REMUESTREOS,
                       semilla: int = SEMILLA) -> tuple[float, float]:
    return _bootstrap_ic(_validos(valores), nivel=nivel, n_remuestreos=n_remuestreos, semilla=semilla)


def resumen(valores, *, nivel: float = NIVEL, n_remuestreos: int = N_REMUESTREOS,
            semilla: int = SEMILLA) -> dict:
    """media ± DE, mediana, IC bootstrap y -- lo más importante -- cuántos
    valores eran válidos de verdad."""
    arr = _a_float(valores)
    v = arr[~np.isnan(arr)]
    n_total, n = len(arr), len(v)
    out = {
        "n_total": n_total,
        "n_validos": n,
        "n_faltantes": n_total - n,
        "pct_faltante": (100.0 * (n_total - n) / n_total) if n_total else math.nan,
        "media": math.nan, "de": math.nan, "mediana": math.nan,
        "ic_inf": math.nan, "ic_sup": math.nan,
    }
    if n == 0:
        return out
    lo, hi = _bootstrap_ic(v, nivel=nivel, n_remuestreos=n_remuestreos, semilla=semilla)
    out.update(
        media=float(v.mean()),
        de=float(v.std(ddof=1)) if n > 1 else math.nan,
        mediana=float(np.median(v)),
        ic_inf=lo, ic_sup=hi,
    )
    return out


def banda_sensibilidad_faltantes(valores, *, minimo: float = 0.0, maximo: float = 1.0) -> dict:
    """Cuánto podría moverse la media si los faltantes valieran lo peor o lo
    mejor posible. Si la banda es ancha, el promedio publicado depende de
    cuáles filas casualmente se pudieron calcular."""
    arr = _a_float(valores)
    if len(arr) == 0:
        return {"media_observada": math.nan, "media_peor_caso": math.nan, "media_mejor_caso": math.nan}
    falt = np.isnan(arr)
    peor = np.where(falt, minimo, arr).mean()
    mejor = np.where(falt, maximo, arr).mean()
    obs = arr[~falt].mean() if (~falt).any() else math.nan
    return {"media_observada": float(obs), "media_peor_caso": float(peor), "media_mejor_caso": float(mejor)}


def ic_wilson(k: int, n: int, *, nivel: float = NIVEL) -> tuple[float, float]:
    """IC de Wilson para una proporción k/n (mejor que el normal con n chico)."""
    if n <= 0:
        return (math.nan, math.nan)
    ci = stats.binomtest(int(k), int(n)).proportion_ci(confidence_level=nivel, method="wilson")
    return (float(ci.low), float(ci.high))


def bootstrap_por_cluster(valores, clusters, *, nivel: float = NIVEL, n_remuestreos: int = N_REMUESTREOS,
                          semilla: int = SEMILLA) -> dict:
    """IC de la media remuestreando CLÚSTERES completos (p. ej. títulos de la
    norma): las preguntas de un mismo título no son independientes, y un
    bootstrap por pregunta subestima la incertidumbre."""
    v = _a_float(valores)
    c = np.asarray(clusters)
    ok = ~np.isnan(v)
    v, c = v[ok], c[ok]
    etiquetas = np.unique(c)
    k = len(etiquetas)
    if k < 2:
        return {"media": float(v.mean()) if len(v) else math.nan, "ic_inf": math.nan, "ic_sup": math.nan,
                "n_clusters": k, "n_validos": len(v)}
    sumas = np.array([v[c == e].sum() for e in etiquetas])
    cuentas = np.array([(c == e).sum() for e in etiquetas], dtype=float)
    rng = np.random.default_rng(semilla)
    idx = rng.integers(0, k, size=(n_remuestreos, k))
    medias = sumas[idx].sum(axis=1) / cuentas[idx].sum(axis=1)
    alfa = (1 - nivel) / 2
    lo, hi = np.quantile(medias, [alfa, 1 - alfa])
    return {"media": float(v.mean()), "ic_inf": float(lo), "ic_sup": float(hi),
            "n_clusters": k, "n_validos": len(v)}


def comparar_pareado(a, b, *, nivel: float = NIVEL, alfa_normalidad: float = ALFA_NORMALIDAD,
                     n_remuestreos: int = N_REMUESTREOS, semilla: int = SEMILLA) -> dict:
    """Compara dos configuraciones sobre las MISMAS preguntas. Diferencia = b - a
    (positiva = b mejor). Solo cuentan los pares con valor en ambos lados.

    Prueba principal: t pareada si Shapiro-Wilk sobre las diferencias no
    rechaza normalidad; Wilcoxon de rangos con signo en caso contrario. Se
    devuelven SIEMPRE ambos p-valores y ambos tamaños de efecto
    (dz de Cohen y correlación biserial de rangos pareada) para que se vea
    si la conclusión depende de la prueba elegida."""
    a, b = _a_float(a), _a_float(b)
    if a.shape != b.shape:
        raise ValueError("a y b deben tener la misma longitud (un valor por pregunta)")
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    n = len(a)
    res: dict = {"n_pares": int(n), "n_descartados": int((~ok).sum())}
    if n < 3:
        res["prueba"] = "insuficiente"
        return res
    d = b - a
    res.update(
        media_a=float(a.mean()), media_b=float(b.mean()),
        diff_media=float(d.mean()), diff_de=float(d.std(ddof=1)),
        n_mejoran=int((d > 0).sum()), n_empeoran=int((d < 0).sum()), n_iguales=int((d == 0).sum()),
    )
    lo, hi = _bootstrap_ic(d, nivel=nivel, n_remuestreos=n_remuestreos, semilla=semilla)
    res["diff_ic_inf"], res["diff_ic_sup"] = lo, hi

    degenerada = float(np.ptp(d)) == 0.0
    shapiro_p = None if degenerada else float(stats.shapiro(d).pvalue)
    res["shapiro_p"] = shapiro_p

    sd = float(d.std(ddof=1))
    res["dz"] = (float(d.mean()) / sd) if sd > 0 else (0.0 if d.mean() == 0 else None)
    p_t = None
    if sd > 0:
        p_t = float(stats.ttest_rel(b, a).pvalue)
    elif d.mean() == 0:
        p_t = 1.0
    res["p_t"] = p_t

    nz = d[d != 0]
    p_w, r_rb = None, None
    if len(nz) == 0:
        p_w, r_rb = 1.0, 0.0
    else:
        ranks = stats.rankdata(np.abs(nz))
        w_pos, w_neg = float(ranks[nz > 0].sum()), float(ranks[nz < 0].sum())
        r_rb = (w_pos - w_neg) / (w_pos + w_neg)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                p_w = float(stats.wilcoxon(nz).pvalue)
        except ValueError:
            p_w = None
    res["p_wilcoxon"], res["r_biserial"] = p_w, r_rb

    normal = shapiro_p is not None and shapiro_p >= alfa_normalidad
    if normal:
        res["prueba"], res["p"], res["efecto_nombre"], res["efecto"] = "t_pareada", p_t, "dz", res["dz"]
    else:
        res["prueba"], res["p"], res["efecto_nombre"], res["efecto"] = "wilcoxon", p_w, "r_biserial", r_rb
    return res


def mcnemar_exacto(a, b, *, nivel: float = NIVEL) -> dict:
    """McNemar exacto (binomial) para dos clasificadores binarios sobre las mismas
    preguntas. a, b: 1/True = acierta. n10 = solo a acierta, n01 = solo b acierta.
    Razón de momios = n01/n10 (>1: b gana más veces de las que pierde)."""
    a, b = _a_float(a), _a_float(b)
    if a.shape != b.shape:
        raise ValueError("a y b deben tener la misma longitud (un valor por pregunta)")
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok] > 0.5, b[ok] > 0.5
    n = len(a)
    n11 = int((a & b).sum()); n10 = int((a & ~b).sum()); n01 = int((~a & b).sum()); n00 = n - n11 - n10 - n01
    disc = n01 + n10
    res = {
        "n_pares": n, "n11": n11, "n10_solo_a": n10, "n01_solo_b": n01, "n00": n00,
        "prop_a": (n11 + n10) / n if n else math.nan, "prop_b": (n11 + n01) / n if n else math.nan,
        "razon_momios": (n01 / n10) if n10 > 0 else (math.inf if n01 > 0 else math.nan),
        "razon_momios_haldane": (n01 + 0.5) / (n10 + 0.5),
    }
    res["diff_prop"] = res["prop_b"] - res["prop_a"] if n else math.nan
    if disc == 0:
        res.update(p=1.0, rm_ic_inf=math.nan, rm_ic_sup=math.nan)
        return res
    t = stats.binomtest(n01, disc, 0.5, alternative="two-sided")
    ci = t.proportion_ci(confidence_level=nivel, method="exact")
    res["p"] = float(t.pvalue)
    res["rm_ic_inf"] = ci.low / (1 - ci.low) if ci.low < 1 else math.inf
    res["rm_ic_sup"] = ci.high / (1 - ci.high) if ci.high < 1 else math.inf
    return res


def holm(pvalores) -> list:
    """Corrección de Holm-Bonferroni. Los None se ignoran y se devuelven como None."""
    p = list(pvalores)
    idx = [i for i, x in enumerate(p) if x is not None and not (isinstance(x, float) and math.isnan(x))]
    m = len(idx)
    ajustados = [None] * len(p)
    orden = sorted(idx, key=lambda i: p[i])
    maximo = 0.0
    for rango, i in enumerate(orden):
        maximo = max(maximo, (m - rango) * p[i])
        ajustados[i] = min(1.0, maximo)
    return ajustados
