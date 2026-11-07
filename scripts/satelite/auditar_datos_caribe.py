"""Auditoria minima de calidad y descripcion de los datos del Caribe (issue #95, Frente C).

ANTES de cualquier prueba de asociacion. Responde: que datos hay, que tan buenos son, donde
estan los extremos, cual es la variabilidad real y que tan colineales son los predictores.
NO prueba asociaciones predictor-resultado (eso es el analisis confirmatorio, con roles de
variables fijados antes en PROTOCOLO_ANALISIS.md).

Secciones: 1 inventario/faltantes | 2 duplicados | 3 coherencia de fechas | 4 descriptiva
con IC (global, por departamento, por suelo) | 5 atipicos | 6 colinealidad (rho, VIF) |
7 autocorrelacion espacial (Moran) | 8 potencia | 9 zonas sin cobertura | 10 mapas.
Salida: auditoria/auditoria_datos_caribe.md, .json y mapas PNG.
"""
from __future__ import annotations

import io
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
from scipy.stats import rankdata, skew, spearmanr

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "eval-stats" / "src"))
import _datos_caribe as dc  # noqa: E402
import estadistica as est  # noqa: E402

SALIDA = AQUI / "auditoria"
MIN_REPORTES = 10
K_VECINOS = 8
N_PERM = 999
N_SIM_POTENCIA = 1500
RNG = np.random.default_rng(est.SEMILLA)
FECHA_MIN, FECHA_MAX = date(2019, 1, 1), date.today()
LINEAS: list[str] = []


def out(txt: str = "") -> None:
    print(txt)
    LINEAS.append(txt)


def tabla(cab: list[str], filas: list[list]) -> None:
    out("| " + " | ".join(cab) + " |")
    out("|" + "|".join("---" for _ in cab) + "|")
    for f in filas:
        out("| " + " | ".join(str(x) for x in f) + " |")
    out()


def ic_mediana(v: np.ndarray, n: int = 2000) -> tuple[float, float]:
    if len(v) < 3:
        return (math.nan, math.nan)
    b = [np.median(v[RNG.integers(0, len(v), len(v))]) for _ in range(n)]
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def descriptiva(nombre: str, v: np.ndarray) -> list:
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return [nombre, 0] + ["-"] * 9
    lo, hi = est.ic_bootstrap_media(v)
    mlo, mhi = ic_mediana(v)
    q = np.percentile(v, [5, 25, 75, 95])
    return [nombre, len(v), f"{v.mean():.3g} [{lo:.3g}, {hi:.3g}]", f"{np.median(v):.3g} [{mlo:.3g}, {mhi:.3g}]",
            f"{v.std(ddof=1):.3g}" if len(v) > 1 else "-", f"{q[0]:.3g}", f"{q[1]:.3g}", f"{q[2]:.3g}", f"{q[3]:.3g}",
            f"{skew(v):.2f}" if len(v) > 2 else "-", f"{v.min():.3g} / {v.max():.3g}"]


CAB_DESC = ["variable", "n", "media [IC95%]", "mediana [IC95%]", "DE", "p5", "p25", "p75", "p95", "asimetria", "min / max"]


def vif_rangos(X: np.ndarray) -> list[float]:
    R = np.column_stack([rankdata(X[:, j]) for j in range(X.shape[1])])
    R = (R - R.mean(0)) / R.std(0)
    res = []
    for j in range(R.shape[1]):
        otros = np.delete(R, j, axis=1)
        A = np.column_stack([np.ones(len(R)), otros])
        coef = np.linalg.lstsq(A, R[:, j], rcond=None)[0]
        r2 = 1 - ((R[:, j] - A @ coef) ** 2).sum() / ((R[:, j] - R[:, j].mean()) ** 2).sum()
        res.append(1 / (1 - r2) if r2 < 0.999999 else math.inf)
    return res


def moran(v: np.ndarray, xy: np.ndarray, k: int = K_VECINOS) -> tuple[float, float]:
    n = len(v)
    d = np.hypot(xy[:, None, 0] - xy[None, :, 0], xy[:, None, 1] - xy[None, :, 1])
    np.fill_diagonal(d, np.inf)
    W = np.zeros((n, n))
    for i in range(n):
        W[i, np.argsort(d[i])[:k]] = 1.0 / k

    def I(x):
        z = x - x.mean()
        return float((n / W.sum()) * (z @ W @ z) / (z @ z))

    obs = I(v)
    perm = [I(RNG.permutation(v)) for _ in range(N_PERM)]
    p = (1 + sum(abs(x) >= abs(obs) for x in perm)) / (N_PERM + 1)
    return obs, float(p)


def rho_minimo_detectable(n: int, potencia: float = 0.8) -> float:
    """Menor |rho| de Spearman que se detecta con la potencia dada (alfa 0.05, 2 colas),
    por simulacion con datos normales bivariados. Es un PISO optimista: con dependencia
    espacial el tamano efectivo es menor y la potencia real, menor todavia."""
    for rho in np.arange(0.05, 0.95, 0.025):
        cov = np.array([[1, rho], [rho, 1]])
        hits = 0
        for _ in range(N_SIM_POTENCIA):
            xy = RNG.multivariate_normal([0, 0], cov, size=n)
            hits += spearmanr(xy[:, 0], xy[:, 1])[1] < 0.05
        if hits / N_SIM_POTENCIA >= potencia:
            return float(rho)
    return math.nan


def mapa(ax, pols, valores, titulo, cmap="viridis", log=False):
    vals = np.array([valores.get(c, np.nan) for c in pols], float)
    parches = [MplPolygon(np.array(g.exterior.coords), closed=True) if g.geom_type == "Polygon" else None for g in
               [p["geom"] if p["geom"].geom_type == "Polygon" else max(p["geom"].geoms, key=lambda x: x.area) for p in pols.values()]]
    pc = PatchCollection([p for p in parches if p is not None], cmap=cmap, edgecolor="0.5", linewidth=0.2)
    arr = np.log10(vals + 1) if log else vals
    pc.set_array(np.ma.masked_invalid(arr))
    ax.add_collection(pc)
    ax.autoscale()
    ax.set_aspect("equal")
    ax.set_title(titulo, fontsize=9)
    ax.axis("off")
    plt.colorbar(pc, ax=ax, shrink=0.6)


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    out("# Auditoria de datos del Caribe (borrador reproducible)")
    out(f"Generado: {date.today()}. Semilla fija. Script: `scripts/satelite/auditar_datos_caribe.py`.\n")

    # ---- Ensamble
    demrows = dc.dem()
    pols = dc.poligonos()
    codigos = [m["codigo"] for m in demrows]
    ung = dc.ungrd(codigos)
    ig = dc.igac(codigos)
    sis = dc.sisben(codigos)
    pob = dc.poblacion_dane(codigos)

    out("## 1. Inventario y faltantes")
    err = [m for m in demrows if "error" in m]
    cods = Counter(m["codigo"] for m in demrows)
    filas = [["DEM (poligonos IGAC)", len(demrows), f"{len(err)} sin estadistica"],
             ["Poligonos con geometria", len(pols), f"{len(set(codigos) - set(pols))} DEM sin poligono"],
             ["Eventos UNGRD (195 municipios)", len(ung), "—"],
             ["Municipios con clasificacion de inundacion IGAC", len(ig), f"{len(codigos) - len(ig)} faltan"],
             ["Municipios con muestra Sisben", len(sis), f"{len(codigos) - len(sis)} faltan"],
             ["Municipios con poblacion DANE 2020", len(pob), f"{len(codigos) - len(pob)} faltan"]]
    tabla(["fuente", "n", "faltantes"], filas)
    sin_ig = [m["municipio"] for m in demrows if m["codigo"] not in ig][:10]
    if sin_ig:
        out(f"Sin IGAC (primeros 10): {', '.join(sin_ig)}\n")

    out("## 2. Duplicados")
    dup_mun = [c for c, n in cods.items() if n > 1]
    clave = lambda r: (r["codigo_municipio"], r["fecha"], r["evento"], r["personas"], r["familias"],
                       r["viviendas_destruidas"], r["viviendas_averiadas"], r["hectareas"])
    cuenta = Counter(clave(r) for r in ung)
    extra = sum(n - 1 for n in cuenta.values() if n > 1)
    ids = Counter(r["id"] for r in ung)
    out(f"- Codigos de municipio repetidos en el DEM: **{len(dup_mun)}**.")
    out(f"- Eventos UNGRD con id repetido: **{sum(n - 1 for n in ids.values() if n > 1)}**.")
    out(f"- Eventos UNGRD identicos en (municipio, fecha, evento, personas, familias, viviendas, hectareas): "
        f"**{extra}** filas extra de {len(ung)} ({100 * extra / len(ung):.1f} %). Pueden ser duplicados reales o "
        "eventos distintos con los mismos numeros (p. ej. varios sin dato); no se eliminan sin criterio.\n")

    out("## 3. Coherencia de fechas (UNGRD)")
    fechas = [r["fecha"] for r in ung]
    nulos = sum(f is None for f in fechas)
    ds = [date.fromisoformat(f) for f in fechas if f]
    fuera = [d for d in ds if d < FECHA_MIN or d > FECHA_MAX]
    out(f"- Fechas nulas: {nulos}. Fuera de [{FECHA_MIN}, {FECHA_MAX}]: {len(fuera)}.")
    creado_antes = sum(1 for r in ung if r.get("creado_en") and r["fecha"] and r["creado_en"][:10] < r["fecha"])
    out(f"- Eventos con fecha posterior a su propia carga en la base: {creado_antes}.")
    por_anio = Counter(d.year for d in ds)
    inund_por_anio = Counter(date.fromisoformat(r["fecha"]).year for r in ung if r["fecha"] and r["evento"] in dc.EVENTOS_INUNDACION)
    tabla(["año", "eventos", "inundaciones", "% inundacion"],
          [[a, por_anio[a], inund_por_anio[a], f"{100 * inund_por_anio[a] / por_anio[a]:.1f}"] for a in sorted(por_anio)])
    cnt = np.array([por_anio[a] for a in sorted(por_anio)], float)
    out(f"Variacion entre años: CV = {cnt.std(ddof=1) / cnt.mean():.2f}; el mayor año tiene {cnt.max() / np.median(cnt):.1f}x la mediana "
        "(2022 es un año de lluvias extremas: la serie NO es estacionaria).\n")
    por_mes = Counter(d.month for d in ds)
    out("Distribucion mensual de eventos: " + ", ".join(f"{m:02d}:{por_mes[m]}" for m in range(1, 13)) + "\n")

    # ---- Tabla por municipio
    tot, inu, nfr, in22 = (defaultdict(int) for _ in range(4))
    for r in ung:
        c = r["codigo_municipio"]
        tot[c] += 1
        if r["evento"] in dc.EVENTOS_INUNDACION:
            inu[c] += 1
            if not str(r["fecha"]).startswith("2022"):
                in22[c] += 1
    rows = []
    for m in demrows:
        if "error" in m or m["codigo"] not in pols:
            continue
        c = m["codigo"]
        p = pols[c]
        rows.append({**m, "area_km2": p["area_km2"], "xy": p["centroide"], "total": tot[c], "inund": inu[c], "inund_sin22": in22[c],
                     "no_inund": tot[c] - inu[c], "reportes_100km2": 100 * tot[c] / p["area_km2"],
                     "share": inu[c] / tot[c] if tot[c] else np.nan,
                     "igac_inund": ig.get(c, {}).get("frac_inundable", np.nan), "textura": ig.get(c, {}).get("textura_dom"),
                     "drenaje": ig.get(c, {}).get("drenaje_dom"),
                     "sisben_n": float(sis[c]["n_viviendas_muestra"]) if c in sis and sis[c]["n_viviendas_muestra"] is not None else np.nan,
                     "poblacion": pob.get(c, {}).get("poblacion", np.nan), "pct_cabecera": pob.get(c, {}).get("pct_cabecera", np.nan),
                     "reportes_100k_hab": 1e5 * tot[c] / pob[c]["poblacion"] if c in pob else np.nan,
                     "densidad_hab_km2": pob[c]["poblacion"] / p["area_km2"] if c in pob else np.nan})
    col = lambda k, f=None: np.array([(r[k] if f is None else f(r)) for r in rows], float)

    out("## 4. Estadistica descriptiva (media y mediana con IC95 % bootstrap)")
    vars_ = [("elevacion media (m)", "elev_media_m"), ("pendiente media (%)", "pend_media_pct"), ("pendiente p90 (%)", "pend_p90_pct"),
             ("rango de elevacion (m)", "rango_elev_m"), ("fraccion < 10 m", "frac_bajo_10m"), ("fraccion pendiente > 15 %", "frac_pend_gt_15"),
             ("IGAC fraccion con inundacion", "igac_inund"), ("area (km2)", "area_km2"), ("eventos totales", "total"),
             ("eventos de inundacion", "inund"), ("proporcion de inundacion", "share"), ("reportes / 100 km2", "reportes_100km2"),
             ("Sisben viviendas (muestra)", "sisben_n"), ("poblacion DANE 2020", "poblacion"),
             ("% poblacion en cabecera", "pct_cabecera"), ("reportes / 100 mil hab.", "reportes_100k_hab"),
             ("densidad (hab/km2)", "densidad_hab_km2")]
    out("### 4.1 Global")
    tabla(CAB_DESC, [descriptiva(n, col(k)) for n, k in vars_])
    out("### 4.2 Por departamento (variables clave)")
    for nombre, k in [("fraccion < 10 m", "frac_bajo_10m"), ("pendiente media (%)", "pend_media_pct"),
                      ("eventos de inundacion", "inund"), ("proporcion de inundacion", "share")]:
        out(f"**{nombre}**")
        tabla(CAB_DESC, [descriptiva(dc.DEPTOS[d], np.array([r[k] for r in rows if r["depto"] == d], float)) for d in dc.DEPTOS])
    out("### 4.3 Por clase dominante de textura del suelo (IGAC; grupos con n >= 5)")
    grupos = defaultdict(list)
    for r in rows:
        if r["textura"]:
            grupos[r["textura"]].append(r)
    tabla(CAB_DESC, [descriptiva(f"{t} (n={len(g)})", np.array([x["share"] for x in g], float)) for t, g in
                     sorted(grupos.items(), key=lambda kv: -len(kv[1])) if len(g) >= 5])
    out("(Variable: proporcion de inundacion. Descriptivo; no implica causalidad.)\n")

    out("## 5. Valores atipicos (descriptivo, no se eliminan)")
    out("Reglas: cercas de Tukey (1.5 y 3 IQR) y z robusto con MAD > 3.5 (convencion de Iglewicz y Hoaglin). Son convenciones, no verdades.\n")
    filas5 = []
    for nombre, k in [("pendiente media (%)", "pend_media_pct"), ("fraccion < 10 m", "frac_bajo_10m"), ("area (km2)", "area_km2"),
                      ("eventos totales", "total"), ("eventos de inundacion", "inund"), ("proporcion de inundacion", "share")]:
        v = col(k)
        ok = ~np.isnan(v)
        q1, q3 = np.percentile(v[ok], [25, 75])
        iqr = q3 - q1
        mad = np.median(np.abs(v[ok] - np.median(v[ok])))
        zr = np.where(ok, 0.6745 * (v - np.median(v[ok])) / mad, np.nan) if mad > 0 else np.full(len(v), np.nan)
        out_t = ok & ((v < q1 - 1.5 * iqr) | (v > q3 + 1.5 * iqr))
        out_x = ok & ((v < q1 - 3 * iqr) | (v > q3 + 3 * iqr))
        out_z = np.abs(np.nan_to_num(zr)) > 3.5
        top = sorted([(v[i], rows[i]["municipio"]) for i in np.where(ok)[0]], reverse=True)[:3]
        filas5.append([nombre, int(out_t.sum()), int(out_x.sum()), int(out_z.sum()),
                       ", ".join(f"{n} ({x:.3g})" for x, n in top)])
    tabla(["variable", "Tukey 1.5", "Tukey 3", "z robusto>3.5", "tres valores mas altos"], filas5)

    out("### 4.4 Capacidad de reportar: ¿se explica por el tamaño poblacional?")
    ok = ~np.isnan(col("poblacion")) & (col("total") > 0)
    xp, yt = col("poblacion")[ok], col("total")[ok]
    r_pt, _ = spearmanr(xp, yt)
    bs = [spearmanr(xp[i], yt[i])[0] for i in (RNG.integers(0, len(xp), len(xp)) for _ in range(2000))]
    out(f"rho de Spearman entre poblacion DANE y total de reportes UNGRD: **{r_pt:.2f}** "
        f"[IC95% {np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}] (n={int(ok.sum())}). "
        "Si es alto, los conteos brutos miden sobre todo tamaño poblacional, no amenaza.\n")

    out("## 6. Colinealidad entre predictores candidatos")
    preds = [("fraccion < 10 m", "frac_bajo_10m"), ("elevacion media", "elev_media_m"), ("pendiente media", "pend_media_pct"),
             ("pendiente p90", "pend_p90_pct"), ("rango de elevacion", "rango_elev_m"), ("fraccion pend > 15 %", "frac_pend_gt_15"),
             ("IGAC inundable", "igac_inund")]
    ok = np.all([~np.isnan(col(k)) for _, k in preds], axis=0)
    X = np.column_stack([col(k)[ok] for _, k in preds])
    rho = spearmanr(X).statistic
    cab = ["Spearman"] + [n for n, _ in preds]
    tabla(cab, [[preds[i][0]] + [f"{rho[i, j]:.2f}" for j in range(len(preds))] for i in range(len(preds))])
    vifs = vif_rangos(X)
    tabla(["predictor", "VIF (sobre rangos)"], [[preds[i][0], f"{vifs[i]:.1f}"] for i in range(len(preds))])
    out(f"n = {int(ok.sum())} municipios completos. Umbrales habituales (|rho| > 0.8; VIF > 5 o 10) son **reglas empiricas** que se usan con cautela. "
        "Los predictores de relieve miden casi lo mismo: no se pueden poner juntos en un modelo ni interpretar sus coeficientes por separado.\n")

    out("## 7. Autocorrelacion espacial (I de Moran, 8 vecinos mas cercanos, permutacion)")
    xy = np.array([r["xy"] for r in rows], float)
    filas7 = []
    for nombre, k in [("proporcion de inundacion", "share"), ("fraccion < 10 m", "frac_bajo_10m"), ("pendiente media", "pend_media_pct"),
                      ("eventos totales", "total")]:
        v = col(k)
        m = ~np.isnan(v)
        I, p = moran(v[m], xy[m])
        filas7.append([nombre, f"{I:.2f}", f"{p:.3f}"])
    tabla(["variable", "I de Moran", "p (permutacion)"], filas7)
    out("Un I de Moran alto significa que municipios vecinos se parecen: las observaciones NO son independientes y los p-valores "
        "ingenuos son demasiado optimistas. Por eso el analisis confirmatorio usa remuestreo por departamentos y replicacion por bloque.\n")

    out("## 8. Potencia estadistica (simulacion; piso optimista)")
    n_ok = int((~np.isnan(col("share")) & (col("total") >= MIN_REPORTES)).sum())
    tabla(["situacion", "n", "|rho| minimo detectable (potencia 80 %, alfa 5 %)"],
          [["Atlantico, piloto anterior", 23, f"{rho_minimo_detectable(23):.2f}"],
           ["Caribe, municipios con >= 10 reportes", n_ok, f"{rho_minimo_detectable(n_ok):.2f}"],
           ["Bloques (departamentos) como unidad", 7, f"{rho_minimo_detectable(7):.2f}"]])
    out("Interpretacion: un resultado nulo con n = 23 solo descarta asociaciones fuertes; con n ~ 190 se detectan correlaciones moderadas; "
        "con 7 bloques casi nada. Con dependencia espacial la potencia real es menor que estos pisos.\n")

    out("## 9. Zonas sin cobertura de reporte")
    mudas = [r for r in rows if r["total"] < MIN_REPORTES]
    por_d = Counter(r["depto"] for r in mudas)
    tabla(["departamento", "municipios", f"con < {MIN_REPORTES} reportes UNGRD", "%"],
          [[dc.DEPTOS[d], sum(1 for r in rows if r["depto"] == d), por_d[d],
            f"{100 * por_d[d] / sum(1 for r in rows if r['depto'] == d):.0f}"] for d in dc.DEPTOS])
    out("Estos municipios no se pueden distinguir entre 'sin inundaciones' y 'sin capacidad de reportar'. Quedan fuera del analisis principal.\n")
    res_pix = Counter(round(m.get("resolucion_m", 0)) for m in demrows if "error" not in m)
    out(f"Resolucion efectiva del DEM por municipio (m): {dict(sorted(res_pix.items()))}. Los municipios grandes se leyeron decimados.\n")

    out("## 10. Mapas")
    por = {r["codigo"]: r for r in rows}
    sub = {c: p for c, p in pols.items() if c in por}
    fig, axs = plt.subplots(2, 3, figsize=(15, 10))
    mapa(axs[0, 0], sub, {c: por[c]["share"] for c in sub}, "Proporcion de inundacion (UNGRD)", "magma")
    mapa(axs[0, 1], sub, {c: por[c]["reportes_100km2"] for c in sub}, "Reportes por 100 km2 (log10; cobertura)", "cividis", log=True)
    mapa(axs[0, 2], sub, {c: por[c]["frac_bajo_10m"] for c in sub}, "Fraccion del municipio < 10 m (DEM)", "Blues")
    mapa(axs[1, 0], sub, {c: por[c]["pend_media_pct"] for c in sub}, "Pendiente media % (DEM)", "YlOrBr")
    mapa(axs[1, 1], sub, {c: por[c]["igac_inund"] for c in sub}, "Fraccion con inundacion (IGAC suelos)", "PuBu")
    mapa(axs[1, 2], sub, {c: por[c]["inund"] for c in sub}, "Eventos de inundacion (conteo)", "Reds")
    fig.suptitle("Caribe colombiano: indicadores DESCRIPTIVOS por municipio (no es un mapa de riesgo)", fontsize=11)
    fig.tight_layout()
    fig.savefig(SALIDA / "mapas_descriptivos_caribe.png", dpi=110)
    out("![mapas](mapas_descriptivos_caribe.png)\n")
    out("**Por que no hay un mapa de 'riesgo':** riesgo = amenaza x exposicion x vulnerabilidad. Hoy no tenemos un modelo de amenaza validado "
        "ni la poblacion expuesta; un mapa compuesto daria apariencia de precision que los datos no respaldan. Se muestran los componentes "
        "por separado y la cobertura de reporte (que condiciona la lectura de todos).\n")

    (SALIDA / "auditoria_datos_caribe.md").write_text("\n".join(LINEAS), encoding="utf-8")
    (SALIDA / "auditoria_datos_caribe.json").write_text(json.dumps(
        {"n_municipios": len(rows), "n_eventos": len(ung), "vif": dict(zip([n for n, _ in preds], vifs))},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nGuardado en", SALIDA)


if __name__ == "__main__":
    main()
