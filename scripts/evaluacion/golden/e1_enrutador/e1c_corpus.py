"""
E1c del issue #169: enrutamiento consciente del corpus. En vez de adivinar el
dominio por la forma de la pregunta, se busca primero en TODO el corpus (la
misma búsqueda híbrida search_knowledge de producción) y se decide el dominio
según de dónde vienen los mejores fragmentos. Responde a la limitación que
declaran Bansal y Agarwal (2026, arXiv:2604.03455): el enrutamiento que solo
mira la consulta tiene un techo.

Solo lectura en Supabase, sin LLM. Mismo test que E1/E1b.

Mapa fragmento -> dominio:
  nsr10_chunks  -> vulnerabilidad_vivienda si el id tiene un prefijo de
                   FUENTES_DOMINIO; si no, normativa_general
  ntc_chunks    -> normativa_general
  motor_chunks  -> su columna motor (aquai, geopot, vias, gerencia)
Los ids numéricos se repiten entre ntc_chunks y motor_chunks, así que se
desambigua por la pareja (id, norma).

Variantes:
  K1  voto del corpus: suma de score RRF de los top-10 por dominio
  K2  K1 con rechazo: si la ventaja del ganador sobre normativa_general es
      menor que rho (fracción del score total), cae a normativa_general
  K3  jerárquico: país extranjero (regex de producción) -> su corpus;
      intención de precio (keyword apu_precios) -> apu_precios; si no, K2
  K4  keyword primero; si no hay match, K3 (reemplaza al contrastivo)
  K5  acuerdo: K3 y el clasificador C3 de E1b; si discrepan, normativa_general
rho se ajusta solo con dev.

Uso: python scripts/evaluacion/golden/e1_enrutador/e1c_corpus.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import e1_enrutador as e

AQUI = Path(__file__).parent
NG = e.NG
r = e.r
K = 10


def _paginar(tabla, columnas):
    filas, off = [], 0
    while True:
        d = r.sb.table(tabla).select(columnas).range(off, off + 999).execute().data
        filas += d
        off += 1000
        if len(d) < 1000:
            return filas


def construir_mapa() -> dict[tuple[str, str], str]:
    mapa = {}
    for f in _paginar("motor_chunks", "id,norma_ref,motor"):
        mapa[(str(f["id"]), f["norma_ref"])] = f["motor"]
    for f in _paginar("ntc_chunks", "id,norma"):
        mapa.setdefault((str(f["id"]), f["norma"]), NG)
    return mapa


PREFIJOS_VIVIENDA = r._prefijos_nsr10("vulnerabilidad_vivienda")
_cache_busqueda: dict[str, list] = {}


def buscar(q):
    if q not in _cache_busqueda:
        _cache_busqueda[q] = r.search(q, top_k=K)
    return _cache_busqueda[q]


def dominio_chunk(c, mapa):
    cid = str(c.chunk_id)
    if not cid.isdigit():
        return "vulnerabilidad_vivienda" if cid.startswith(PREFIJOS_VIVIENDA) else NG
    return mapa.get((cid, c.norma), NG)


def puntajes(q, mapa):
    s = defaultdict(float)
    for c in buscar(q):
        s[dominio_chunk(c, mapa)] += float(c.score)
    return s


def k1(q, mapa):
    s = puntajes(q, mapa)
    return max(s, key=s.get) if s else NG


def k2(q, mapa, rho):
    s = puntajes(q, mapa)
    if not s:
        return NG
    gan = max(s, key=s.get)
    if gan != NG and (s[gan] - s.get(NG, 0.0)) / sum(s.values()) < rho:
        return NG
    return gan


def _extranjero(q):
    t = e.plugins_chat._norm(q)
    if e.plugins_chat._RE_PERU.search(t):
        return "peru_e030"
    if e.plugins_chat._RE_ECUADOR.search(t):
        return "ecuador_nec_se_ds"
    return None


def k3(q, mapa, rho):
    ext = _extranjero(q)
    if ext:
        return ext
    if r._score_motores(q).get("apu_precios", 0) > 0:
        return "apu_precios"
    return k2(q, mapa, rho)


def k4(q, mapa, rho):
    return r.route_motor(q) or k3(q, mapa, rho)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", help="evaluar en otro conjunto (p. ej. dataset_heldout_k6.jsonl). El ajuste (rho, "
                                      "entrenamiento de C3, umbral) sigue saliendo SOLO del dev de dataset_e1: nada se "
                                      "reajusta con el conjunto evaluado.")
    args = ap.parse_args()
    casos = [json.loads(l) for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines()]
    dev = [c for c in casos if c["split"] == "dev"]
    test = [c for c in casos if c["split"] == "test"]
    sufijo = ""
    if args.dataset:
        test = [json.loads(l) for l in (AQUI / args.dataset).read_text(encoding="utf-8").splitlines() if l.strip()]
        sufijo = "_" + Path(args.dataset).stem
        fuga = e.chequeo_fuga(test)
        dev_norm = {e._norm(c["pregunta"]) for c in dev}
        fuga_dev = [c["id"] for c in test if e._norm(c["pregunta"]) in dev_norm]
        print(f"evaluado: {args.dataset} n={len(test)} | chequeo de fuga: {len(fuga)} casi-duplicados de ejemplos "
              f"del contrastivo; {len(fuga_dev)} iguales a dev")
    mapa = construir_mapa()

    # ajuste de rho solo en dev, con K3 (la variante que lo usa en todas las demás)
    grilla = np.round(np.arange(0.0, 0.61, 0.05), 2)
    rho = max(grilla, key=lambda x: (sum(f["aceptable"] for f in e.evaluar(dev, lambda q: k3(q, mapa, x))),
                                     sum(f["estricto"] for f in e.evaluar(dev, lambda q: k3(q, mapa, x))), -x))

    # clasificador C3 de E1b para K5 (mismo entrenamiento: ejemplos + dev)
    import e1b_clasificadores as b
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    X_tr = [q for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for q in qs] + [c["pregunta"] for c in dev]
    y_tr = [d for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for _ in qs] + [c["esperado"] for c in dev]
    c3 = make_pipeline(b._Embed(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")).fit(X_tr, y_tr)
    umbral_c3 = json.loads((AQUI / "resultados_e1b.json").read_text(encoding="utf-8"))["umbrales"]["C3_minilm_logreg"]

    def c3_route(q):
        p, mg = b._margenes(c3, [q])
        return p[0] if mg[0] >= umbral_c3 else NG

    def k5(q):
        a, c = k3(q, mapa, rho), c3_route(q)
        return a if a == c else NG

    variantes = {
        "V1_produccion": e.v1,
        "V3_margen_delta0.18": lambda q: e.v3(q, 0.18),
        "C3_minilm_logreg": c3_route,
        "K1_voto_corpus": lambda q: k1(q, mapa),
        f"K2_voto+rechazo_rho{rho}": lambda q: k2(q, mapa, rho),
        f"K3_jerarquico_rho{rho}": lambda q: k3(q, mapa, rho),
        f"K4_keyword+K3": lambda q: k4(q, mapa, rho),
        "K5_acuerdo_K3_C3": k5,
        # POST HOC: diseñada después de ver en test que keyword acierta en S2 y
        # C3 en S1/S3. Exploratoria; se confirma solo con un set held-out nuevo.
        "K6_keyword+C3_posthoc": lambda q: r.route_motor(q) or c3_route(q),
    }
    filas = {k: e.evaluar(test, fn) for k, fn in variantes.items()}
    base = [f["aceptable"] for f in filas["V1_produccion"]]
    nombres = [k for k in filas if k != "V1_produccion"]
    tests_ = {k: e.mcnemar_exacto(base, [f["aceptable"] for f in filas[k]]) for k in nombres}
    ph = dict(zip(nombres, e.holm([tests_[k]["p"] for k in nombres])))

    salida = {"n_test": len(test), "rho": float(rho), "K": K, "variantes": {}, "fallos": {}}
    print(f"test E1: {len(test)} | rho={rho} (ajustado en dev) | top-K={K}\n")
    print(f"{'variante (TEST)':30s} {'estricto':>9s} {'aceptable':>22s} {'callejón':>9s} {'p_holm vs V1':>13s}")
    for k, fs in filas.items():
        res = e.resumen(fs)
        por = defaultdict(list)
        for f in fs:
            por[f["estrato"]].append(f)
        res["por_estrato"] = {s: {"n": len(v), "estricto": sum(x["estricto"] for x in v) / len(v),
                                  "aceptable": sum(x["aceptable"] for x in v) / len(v)} for s, v in sorted(por.items())}
        res["mcnemar_vs_V1"] = tests_.get(k)
        res["p_holm_vs_V1"] = ph.get(k)
        salida["variantes"][k] = res
        salida["fallos"][k] = [{"pregunta": next(c["pregunta"] for c in test if c["id"] == f["id"]),
                                "esperado": f["esperado"], "obtenido": f["obtenido"]} for f in fs if not f["aceptable"]]
        a = res["aceptable"]
        p = f"{ph[k]:.4f}" if k in ph else "—"
        print(f"{k:30s} {res['estricto']['p']:9.1%} {a['p']:8.1%} [{a['ic95'][0]:.1%}-{a['ic95'][1]:.1%}] {res['callejon_falso']['k']:>9d} {p:>13s}")
    (AQUI / f"resultados_e1c{sufijo}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
