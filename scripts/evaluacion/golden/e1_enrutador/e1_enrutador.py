"""
E1 del issue #169: variantes del enrutador de dominio sobre dataset_e1.jsonl.
Sin LLM y sin escritura en Supabase. Solo lee el catálogo de municipios
(detectar_municipio_en_texto) y codifica con el modelo local de embeddings.

Variantes (ninguna modifica el código de producción; se envuelven aquí):
  V0  keyword solo (sin match -> normativa_general)
  V1  PRODUCCIÓN: _route_con_metodo() + depurar_motores_extranjeros()
  V2  V1, pero el contrastivo exige score >= tau
  V3  V1, pero el contrastivo exige ventaja >= delta sobre normativa_general
  V4  regla previa: municipio colombiano + intención sísmica -> geopot; si no, V1
  V5  V4 + V3

tau y delta se eligen SOLO con el split dev; se reporta el split test.

Resultado por pregunta:
  estricto       -- dominio == esperado
  aceptable      -- dominio en aceptables
  callejon       -- terminó en vulnerabilidad_vivienda, dominio sin chunks
                    ni camino propio en el chat: abstención garantizada
                    (L9, abstención falsa), salvo que esa fuera la respuesta
                    esperada (y aun así el chat se abstiene: se cuenta aparte)

Uso: python scripts/evaluacion/golden/e1_enrutador/e1_enrutador.py
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[4]
load_dotenv(RAIZ / "apps" / "api" / ".env")
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
sys.path.insert(0, str(RAIZ / "packages" / "eval-stats"))

import motor_router_contrastivo as mrc  # noqa: E402
import plugins_chat  # noqa: E402
import rag_multi_norma as r  # noqa: E402
import sgc_amenaza_sismica  # noqa: E402
from src.estadistica import bootstrap_por_cluster, holm, ic_wilson, mcnemar_exacto  # noqa: E402

AQUI = Path(__file__).parent
NG = "normativa_general"
CALLEJONES = {"vulnerabilidad_vivienda"}  # 0 motor_chunks y sin rama propia (verificado 2026-11-10)

_RE_SISMICA = re.compile(
    r"\b(aa|av|pga|amenaza sismica|zona sismica|aceleracion (horizontal )?pico|"
    r"parametros sismicos|espectro de diseno|tiembla|sismica es la zona)\b")


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


# ── variantes ──────────────────────────────────────────────────────────────
_cache_contr: dict[str, list[tuple[str, float]]] = {}
_cache_muni: dict[str, bool] = {}


def contrastivo(q: str) -> list[tuple[str, float]]:
    if q not in _cache_contr:
        _cache_contr[q] = mrc.route_motores_contrastivo(q, top_k=len(mrc.EJEMPLOS_POR_DOMINIO))
    return _cache_contr[q]


def hay_municipio(q: str) -> bool:
    if q not in _cache_muni:
        _cache_muni[q] = sgc_amenaza_sismica.detectar_municipio_en_texto(q) is not None
    return _cache_muni[q]


def _primero(motores: list[str]) -> str:
    return motores[0] if motores else NG


def v0(q):
    return r.route_motor(q) or NG


def _v1_detalle(q):
    motores, metodo, score = r._route_con_metodo(q)
    motores = plugins_chat.depurar_motores_extranjeros(q, motores, sgc_amenaza_sismica.detectar_municipio_en_texto)
    return _primero(motores), metodo, score


def v1(q):
    return _v1_detalle(q)[0]


def v2(q, tau):
    d, metodo, score = _v1_detalle(q)
    if metodo == "contrastivo" and score is not None and score < tau:
        return NG
    return d


def v3(q, delta):
    d, metodo, _ = _v1_detalle(q)
    if metodo != "contrastivo":
        return d
    puntajes = dict(contrastivo(q))
    if puntajes[d] - puntajes.get(NG, 0.0) < delta:
        return NG
    return d


def _regla_sismica(q):
    return hay_municipio(q) and bool(_RE_SISMICA.search(_norm(q)))


def v4(q):
    return "geopot" if _regla_sismica(q) else v1(q)


def v5(q, delta):
    return "geopot" if _regla_sismica(q) else v3(q, delta)


# ── métricas ───────────────────────────────────────────────────────────────
def evaluar(casos, fn):
    filas = []
    for c in casos:
        d = fn(c["pregunta"])
        filas.append({
            "id": c["id"], "estrato": c["estrato"], "cluster": c["cluster"], "obtenido": d,
            "esperado": c["esperado"],
            "estricto": int(d == c["esperado"]),
            "aceptable": int(d in c["aceptables"]),
            "callejon_falso": int(d in CALLEJONES and c["esperado"] not in CALLEJONES),
        })
    return filas


def resumen(filas):
    n = len(filas)
    out = {"n": n}
    for m in ("estricto", "aceptable", "callejon_falso"):
        k = sum(f[m] for f in filas)
        lo, hi = ic_wilson(k, n)
        out[m] = {"k": k, "p": k / n, "ic95": [lo, hi]}
    b = bootstrap_por_cluster([f["aceptable"] for f in filas], [f["cluster"] for f in filas])
    out["aceptable_ic95_cluster"] = [b.get("ic_inf"), b.get("ic_sup")] if isinstance(b, dict) else b
    return out


def chequeo_fuga(casos):
    """Duplicados exactos y casi-duplicados (coseno >= 0.95) contra los
    ejemplos de referencia del contrastivo: inflarían su exactitud."""
    ejemplos = [(d, e) for d, es in mrc.EJEMPLOS_POR_DOMINIO.items() for e in es]
    E = np.array([r.embed_query(e) for _, e in ejemplos])
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    hallazgos = []
    for c in casos:
        v = np.array(r.embed_query(c["pregunta"]))
        v /= np.linalg.norm(v)
        s = E @ v
        j = int(np.argmax(s))
        if s[j] >= 0.95 or _norm(ejemplos[j][1]) == _norm(c["pregunta"]):
            hallazgos.append({"id": c["id"], "pregunta": c["pregunta"], "ejemplo": ejemplos[j][1], "coseno": round(float(s[j]), 3)})
    return hallazgos


def main():
    casos = [json.loads(l) for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines()]
    fuga = chequeo_fuga(casos)
    ids_fuga = {f["id"] for f in fuga}
    casos = [c for c in casos if c["id"] not in ids_fuga]
    dev = [c for c in casos if c["split"] == "dev"]
    test = [c for c in casos if c["split"] == "test"]

    # ajuste de tau y delta solo en dev (criterio: tasa aceptable, desempate estricto)
    def mejor(param_fn, grilla):
        punt = []
        for x in grilla:
            f = evaluar(dev, lambda q: param_fn(q, x))
            punt.append((sum(r_["aceptable"] for r_ in f), sum(r_["estricto"] for r_ in f), -x, x))
        return max(punt)[3]

    tau = mejor(v2, [round(t, 2) for t in np.arange(0.30, 0.71, 0.05)])
    delta = mejor(v3, [round(d, 2) for d in np.arange(0.00, 0.21, 0.02)])
    delta5 = mejor(v5, [round(d, 2) for d in np.arange(0.00, 0.21, 0.02)])

    variantes = {
        "V0_keyword": v0,
        "V1_produccion": v1,
        f"V2_umbral_tau{tau}": lambda q: v2(q, tau),
        f"V3_margen_delta{delta}": lambda q: v3(q, delta),
        "V4_regla_sismica": v4,
        f"V5_regla+margen_delta{delta5}": lambda q: v5(q, delta5),
    }

    reporte = {"n_total": len(casos) + len(fuga), "excluidos_por_fuga": fuga,
               "n_dev": len(dev), "n_test": len(test), "tau": tau, "delta": delta, "delta_v5": delta5,
               "split": {}}
    filas_test = {}
    for split, cs in (("dev", dev), ("test", test)):
        reporte["split"][split] = {}
        for nombre, fn in variantes.items():
            filas = evaluar(cs, fn)
            if split == "test":
                filas_test[nombre] = filas
            res = resumen(filas)
            por_estrato = defaultdict(list)
            for f in filas:
                por_estrato[f["estrato"]].append(f)
            res["por_estrato"] = {e: {"n": len(fs), "estricto": sum(x["estricto"] for x in fs) / len(fs),
                                      "aceptable": sum(x["aceptable"] for x in fs) / len(fs),
                                      "callejon_falso": sum(x["callejon_falso"] for x in fs)}
                                  for e, fs in sorted(por_estrato.items())}
            reporte["split"][split][nombre] = res

    # pruebas pareadas en test contra producción (McNemar exacto + Holm)
    base = [f["aceptable"] for f in filas_test["V1_produccion"]]
    comparaciones, pvals = [], []
    for nombre, filas in filas_test.items():
        if nombre == "V1_produccion":
            continue
        m = mcnemar_exacto(base, [f["aceptable"] for f in filas])
        comparaciones.append({"variante": nombre, **m})
        pvals.append(m.get("p_valor", m.get("p", 1.0)))
    for c, p_adj in zip(comparaciones, holm(pvals)):
        c["p_holm"] = p_adj
    reporte["mcnemar_vs_V1_test"] = comparaciones

    # matriz de confusión de producción (todo el dataset) y sus fallos
    todas = evaluar(casos, v1)
    reporte["confusion_V1"] = {f"{k[0]} -> {k[1]}": n for k, n in
                               Counter((f["esperado"], f["obtenido"]) for f in todas if not f["aceptable"]).most_common()}
    reporte["fallos_V1"] = [{"id": f["id"], "pregunta": next(c["pregunta"] for c in casos if c["id"] == f["id"]),
                             "esperado": f["esperado"], "obtenido": f["obtenido"]}
                            for f in todas if not f["aceptable"]]

    (AQUI / "resultados_e1.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=1, default=float), encoding="utf-8")

    print(f"casos: {len(casos)} (excluidos por fuga: {len(fuga)}) | dev {len(dev)} | test {len(test)} | tau={tau} delta={delta} delta_v5={delta5}\n")
    print(f"{'variante (TEST)':34s} {'estricto':>9s} {'aceptable':>22s} {'callejón falso':>15s}")
    for nombre, res in reporte["split"]["test"].items():
        a = res["aceptable"]
        print(f"{nombre:34s} {res['estricto']['p']:9.1%} {a['p']:8.1%} [{a['ic95'][0]:.1%}-{a['ic95'][1]:.1%}] {res['callejon_falso']['k']:>10d}")
    print("\nMcNemar (aceptable) vs V1 en test, Holm:")
    for c in comparaciones:
        print(f"  {c['variante']:34s} p_holm={c['p_holm']:.4f}  {json.dumps({k: v for k, v in c.items() if k not in ('variante', 'p_holm')}, default=float)}")


if __name__ == "__main__":
    main()
