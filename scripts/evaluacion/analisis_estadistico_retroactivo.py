"""
Análisis estadístico retroactivo de las corridas RAGAS ya existentes
(issue #95, Frente A0). No llama a ningún LLM ni a Supabase: solo relee los
scorecards ya guardados, así que no cuesta nada y no toca producción.

Qué hace, y por qué:
1. Reporta cada métrica con su n REAL. Los resúmenes publicados decían n=278
   para todo, pero RAGAS dejó NaN en muchas filas; el promedio publicado sale
   solo de las filas calculables. Aquí se informa cuántas son, y entre qué
   extremos se movería la media si las faltantes valieran 0 o 1.
2. Desglosa por tipo de pregunta y por título de la norma (el id del dataset
   da la categoría; los scorecards no la traen), con IC bootstrap y marca los
   grupos con n < 10 como poco confiables.
3. Pregunta si lo que falta es aleatorio: tasa de faltantes por tipo y prueba
   chi-cuadrado. Si faltan más en cierto tipo, los promedios globales están
   sesgados hacia los tipos fáciles.
4. Comparaciones PAREADAS por pregunta entre corridas (t pareada o Wilcoxon
   según Shapiro-Wilk, tamaño de efecto, IC de la diferencia, Holm dentro de
   cada familia de pruebas).

Limitaciones que el reporte declara (no se ocultan):
- Las comparaciones entre fechas (52 -> 278, 143 -> 278) no son experimentos
  controlados: cambiaron a la vez el código, el corpus ingerido y posiblemente
  el juez. Sirven para ver tendencia, no para atribuir causa.
- Con n=12 (comparación de agosto) la potencia es baja: un p alto NO prueba
  que no haya diferencia.
- El juez de RAGAS es un LLM sin calibrar contra humanos todavía.

Uso: python scripts/evaluacion/analisis_estadistico_retroactivo.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
EVAL = RAIZ / "scripts" / "evaluacion"
sys.path.insert(0, str(RAIZ / "packages" / "eval-stats" / "src"))
import estadistica as est  # noqa: E402

METRICAS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
N_MINIMO_CONFIABLE = 10
TIPOS_ESPECIALES = ("ADV", "COLOQ", "COMP", "SINT")


def _cargar(nombre: str) -> pd.DataFrame:
    return pd.read_csv(EVAL / f"baseline_{nombre}_scorecard.csv")


def _mapa_categorias() -> pd.DataFrame:
    """pregunta -> id, tipo, titulo (a partir del dataset original)."""
    spec = importlib.util.spec_from_file_location("ds", EVAL / "dataset_baseline_nsr10.py")
    ds = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ds)
    filas = []
    for c in ds.CASOS_BASELINE:
        prefijo = c["id"].split("-")[0]
        base = prefijo.rstrip("0123456789") if prefijo.rstrip("0123456789") in TIPOS_ESPECIALES else None
        filas.append({
            "user_input": c["pregunta"], "id": c["id"],
            "tipo": base or "hecho",
            "titulo": None if base else prefijo,
        })
    return pd.DataFrame(filas)


def _limpio(obj):
    """Convierte NaN/inf/numpy a tipos JSON válidos."""
    if isinstance(obj, dict):
        return {k: _limpio(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_limpio(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 6)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def _fila(r: dict) -> str:
    def f(x, d=3):
        return "  n/d" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"
    return (f"n={r['n_validos']:>3}/{r['n_total']:<3} falta={r['pct_faltante']:>4.0f}%  "
            f"media={f(r['media'])} ±{f(r['de'])}  IC95%[{f(r['ic_inf'])}, {f(r['ic_sup'])}]")


def parte1_resumen_real(df: pd.DataFrame) -> dict:
    print("\n=== 1. Resumen con n real (278 preguntas, corrida 2026-09-09) ===")
    out = {}
    for m in METRICAS:
        r = est.resumen(df[m])
        b = est.banda_sensibilidad_faltantes(df[m])
        r["banda_media_peor_caso"], r["banda_media_mejor_caso"] = b["media_peor_caso"], b["media_mejor_caso"]
        out[m] = r
        print(f"{m:<18} {_fila(r)}\n{'':<18} si las faltantes valieran 0 o 1, la media iría de "
              f"{b['media_peor_caso']:.3f} a {b['media_mejor_caso']:.3f}")
    completas = int(df[METRICAS].notna().all(axis=1).sum())
    out["_filas_con_las_4_metricas"] = completas
    print(f"Filas con las 4 métricas completas: {completas}/{len(df)}")
    return out


def parte2_por_grupo(df: pd.DataFrame) -> dict:
    out = {"por_tipo": {}, "por_titulo": {}}
    print("\n=== 2a. Por tipo de pregunta ===")
    for tipo, g in df.groupby("tipo"):
        out["por_tipo"][tipo] = {}
        print(f"[{tipo}] ({len(g)} preguntas)")
        for m in METRICAS:
            r = est.resumen(g[m]); r["poco_confiable"] = r["n_validos"] < N_MINIMO_CONFIABLE
            out["por_tipo"][tipo][m] = r
            print(f"   {m:<18} {_fila(r)}{'  <-- n bajo' if r['poco_confiable'] else ''}")
    print("\n=== 2b. Por título de la norma (solo preguntas de hecho único), faithfulness ===")
    h = df[df.tipo == "hecho"]
    for t, g in h.groupby("titulo"):
        out["por_titulo"][t] = {m: est.resumen(g[m]) for m in METRICAS}
        r = out["por_titulo"][t]["faithfulness"]
        print(f"[{t:<12}] {_fila(r)}{'  <-- n bajo' if r['n_validos'] < N_MINIMO_CONFIABLE else ''}")
    # IC por clúster de título: las preguntas de un mismo título no son independientes
    cl = np.where(df.tipo == "hecho", df.titulo.fillna(""), df.tipo)
    out["cluster_bootstrap"] = {m: est.bootstrap_por_cluster(df[m], cl) for m in METRICAS}
    print("\nIC95% de la media global remuestreando clústeres (título/tipo) -- más honesto que por pregunta:")
    for m in METRICAS:
        c = out["cluster_bootstrap"][m]
        plano = est.ic_bootstrap_media(df[m])
        print(f"   {m:<18} por clúster [{c['ic_inf']:.3f}, {c['ic_sup']:.3f}]   vs por pregunta [{plano[0]:.3f}, {plano[1]:.3f}]   ({c['n_clusters']} clústeres)")
    return out


def parte3_faltantes(df: pd.DataFrame) -> dict:
    print("\n=== 3. ¿Los faltantes son aleatorios? ===")
    out = {}
    for m in METRICAS:
        falta = df[m].isna()
        tabla = pd.crosstab(df.tipo, falta)
        if True not in tabla.columns:
            continue
        chi2, p, gl, esperadas = stats.chi2_contingency(tabla)
        n = tabla.values.sum()
        v = math.sqrt(chi2 / (n * (min(tabla.shape) - 1)))
        tasas = (tabla[True] / tabla.sum(axis=1) * 100).round(0).to_dict()
        out[m] = {"tasa_falta_pct_por_tipo": tasas, "chi2": chi2, "gl": gl, "p": p, "cramer_v": v,
                  "celdas_esperadas_menores_a_5": int((esperadas < 5).sum()), "n_faltantes": int(falta.sum())}
        print(f"{m:<18} faltan {int(falta.sum()):>3}  por tipo %: {tasas}  chi2={chi2:.1f} gl={gl} p={p:.3g} V={v:.2f}"
              f"{'  (celdas esperadas <5: p aproximado)' if (esperadas < 5).any() else ''}")
    # ¿faltar en una métrica se asocia con ser peor en otra?
    print("\nSonda de sesgo: ¿las preguntas sin faithfulness tienen otro answer_relevancy?")
    a = df.loc[df.faithfulness.isna(), "answer_relevancy"].dropna()
    b = df.loc[df.faithfulness.notna(), "answer_relevancy"].dropna()
    if len(a) > 2 and len(b) > 2:
        u = stats.mannwhitneyu(a, b)
        rb = 2 * u.statistic / (len(a) * len(b)) - 1   # convención: positivo = "sin faithfulness" tiende a valores MAYORES
        out["sonda_mnar"] = {"n_sin_faithfulness": len(a), "n_con_faithfulness": len(b),
                             "mediana_sin": float(a.median()), "mediana_con": float(b.median()),
                             "p": float(u.pvalue), "r_biserial": rb}
        print(f"   mediana answer_relevancy: sin faithfulness={a.median():.3f} (n={len(a)}) vs con={b.median():.3f} (n={len(b)});"
              f" Mann-Whitney p={u.pvalue:.3g}, r={rb:+.2f} (negativo = las filas sin faithfulness tienden a tener MENOR answer_relevancy)")
    return out


_ABSTENCION = re.compile(
    r"no (?:se )?(?:encontr|dispon|hay informaci|puedo|tengo|cuento|aparece|define|especifica|incluye|contiene|"
    r"figura|menciona|existe|contempla)", re.I)


def parte5_diagnosticos(df: pd.DataFrame) -> dict:
    """Artefactos de medición. Heurística por patrón de texto: orienta, no
    reemplaza la lectura de un experto (eso es el benchmark v2)."""
    print("\n=== 5. Diagnóstico de artefactos de medición (heurística de texto) ===")
    df = df.assign(abstiene=df.response.astype(str).map(lambda s: bool(_ABSTENCION.search(s))))
    out = {}
    comp = df[df.tipo == "COMP"]
    cero = comp.answer_relevancy == 0
    out["COMP"] = {
        "n": len(comp), "relevancia_cero": int(cero.sum()),
        "cero_con_lenguaje_de_no_tengo": int((cero & comp.abstiene).sum()),
        "relevancia_positiva": int((comp.answer_relevancy > 0).sum()),
        "positiva_con_lenguaje_de_no_tengo": int(((comp.answer_relevancy > 0) & comp.abstiene).sum()),
    }
    c = out["COMP"]
    print(f"[COMP precio+norma] relevancia=0 en {c['relevancia_cero']}/{c['n']}; de esas, {c['cero_con_lenguaje_de_no_tengo']} "
          f"declaran no tener información. Con relevancia>0: {c['positiva_con_lenguaje_de_no_tengo']}/{c['relevancia_positiva']} lo declaran.")
    print("   -> El 0.0 refleja que la parte de precio NO se responde (falla funcional real), amplificado por una métrica que "
          "castiga cualquier fragmento 'no sé'. Sí hay que corregir el sistema, no solo la métrica.")
    adv = df[df.tipo == "ADV"]
    k = int(adv.abstiene.sum())
    lo, hi = est.ic_wilson(len(adv) - k, len(adv))
    out["ADV"] = {"n": len(adv), "abstienen_o_niegan": k, "sin_senal_de_abstencion": len(adv) - k,
                  "tasa_sin_abstencion_ic_wilson": [lo, hi],
                  "nan_faithfulness": int(adv.faithfulness.isna().sum()), "nan_context_precision": int(adv.context_precision.isna().sum())}
    print(f"[ADV sin respuesta en el corpus] {k}/{len(adv)} contienen lenguaje de abstención o negación (detección por patrón de "
          f"texto: NO verifica que la negación sea correcta); sin señal de abstención: {len(adv) - k} (IC95% Wilson de esa tasa: "
          f"{lo:.1%} a {hi:.1%}). Lectura manual preliminar de los 7 casos que un primer patrón no detectó: ninguno inventa un valor normativo.")
    print("   -> RAGAS deja faithfulness/context_precision en NaN y pone answer_relevancy≈0 justo cuando el sistema HACE LO CORRECTO "
          "(abstenerse). Para ADV la métrica válida es la tasa de abstención/alucinación, medida con anotación humana (benchmark v2).")
    return out


def _pareadas(nombre: str, a: pd.DataFrame, b: pd.DataFrame, et_a: str, et_b: str) -> list[dict]:
    m = a.merge(b, on="user_input", suffixes=("_a", "_b"))
    filas = []
    for met in METRICAS:
        r = est.comparar_pareado(m[f"{met}_a"], m[f"{met}_b"])
        r.update(familia=nombre, comparacion=f"{et_a} -> {et_b}", metrica=met, n_preguntas_comunes=len(m))
        filas.append(r)
    return filas


def _imprimir_familia(filas: list[dict]) -> None:
    padj = est.holm([f.get("p") for f in filas])
    for f, pa in zip(filas, padj):
        f["p_holm"] = pa
        if f["prueba"] == "insuficiente":
            print(f"   {f['comparacion']:<46} {f['metrica']:<18} n_pares={f['n_pares']}  (insuficiente)")
            continue
        sig = "*" if (pa is not None and pa < 0.05) else " "
        print(f"   {f['comparacion']:<46} {f['metrica']:<18} n={f['n_pares']:>3}  "
              f"Δ={f['diff_media']:+.3f} IC[{f['diff_ic_inf']:+.3f},{f['diff_ic_sup']:+.3f}]  "
              f"{f['prueba']:<10} p={f['p'] if f['p'] is None else round(f['p'], 4)}  "
              f"p_holm={None if pa is None else round(pa, 4)}{sig}  {f['efecto_nombre']}={f['efecto'] if f['efecto'] is None else round(f['efecto'], 2)}  "
              f"(+{f['n_mejoran']}/-{f['n_empeoran']}/={f['n_iguales']})")


def parte4_pareadas() -> dict:
    print("\n=== 4. Comparaciones pareadas (Δ = segunda - primera; * = p_holm < 0.05) ===")
    out = {}
    base = _cargar("2026-08-27")
    rer = _cargar("2026-08-27_reranking-combinado")
    dec = _cargar("2026-08-27_query-decomposition")
    print("\n[A] Agosto: 3 variantes sobre las MISMAS 12 preguntas (n bajo: la ausencia de significancia no prueba igualdad)")
    fam = (_pareadas("agosto_12q", base, rer, "baseline", "reranking")
           + _pareadas("agosto_12q", base, dec, "baseline", "descomposicion")
           + _pareadas("agosto_12q", rer, dec, "reranking", "descomposicion"))
    _imprimir_familia(fam); out["agosto_12q"] = fam

    c278 = _cargar("2026-09-09_278preguntas")
    print("\n[B] Evolución en el tiempo, 52 preguntas comunes (cambió código + corpus + posiblemente el juez; no es causal)")
    fam = _pareadas("evolucion_52q", _cargar("2026-08-27_52preguntas"), c278, "27-ago", "09-sep")
    _imprimir_familia(fam); out["evolucion_52q"] = fam

    print("\n[C] Evolución en el tiempo, 143 preguntas comunes (07-sep -> 09-sep)")
    fam = _pareadas("evolucion_143q", _cargar("2026-09-07_143preguntas"), c278, "07-sep", "09-sep")
    _imprimir_familia(fam); out["evolucion_143q"] = fam

    print("\n[D] Precios: antes y después del arreglo de deduplicación/sinónimos (55 preguntas)")
    fam = _pareadas("precios_55q", _cargar("2026-09-07_precios"), _cargar("2026-09-13-post-fix_precios"), "pre-fix", "post-fix")
    _imprimir_familia(fam); out["precios_55q"] = fam
    return out


def main() -> None:
    cat = _mapa_categorias()
    df = _cargar("2026-09-09_278preguntas").merge(cat, on="user_input", how="left")
    assert df.tipo.notna().all(), "hay preguntas sin categoría: el dataset y el scorecard no coinciden"
    resultados = {
        "descripcion": "Análisis estadístico retroactivo (issue #95, A0). Semilla bootstrap fija: reproducible.",
        "resumen_real_278": parte1_resumen_real(df),
        "grupos": parte2_por_grupo(df),
        "faltantes": parte3_faltantes(df),
        "pareadas": parte4_pareadas(),
        "diagnosticos": parte5_diagnosticos(df),
    }
    salida = EVAL / "analisis_estadistico_retroactivo_resultados.json"
    salida.write_text(json.dumps(_limpio(resultados), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetalle completo: {salida}")


if __name__ == "__main__":
    main()
