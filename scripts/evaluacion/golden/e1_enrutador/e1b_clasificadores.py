"""
E1b del issue #169: ¿el enrutador por centroides de embeddings es la
herramienta adecuada para StructAI? Prueba de la hipótesis con clasificadores
clásicos, siguiendo a Bansal y Agarwal (2026, arXiv:2604.03455), que en
RAGRouter-Bench encontraron que TF-IDF + SVM supera a los embeddings MiniLM
por 3,1 puntos de macro-F1 al enrutar consultas.

Entrenamiento: EJEMPLOS_POR_DOMINIO del contrastivo (los mismos datos que ya
usa producción) + split dev del E1. Evaluación: split test del E1, el mismo
de e1_enrutador.py, con las mismas métricas. Sin LLM.

Variantes nuevas (todas caen a normativa_general si su margen es bajo, la
regla de rechazo de Chow (1970) aplicada al top-1 vs top-2):
  C1  TF-IDF (palabras 1-2 + caracteres 3-5) + SVM lineal
  C2  TF-IDF + regresión logística
  C3  embeddings MiniLM (los de producción) + regresión logística
  C4  keyword primero; si no hay match, C1   (híbrido léxico)
El margen de rechazo se ajusta solo en dev.

Uso: python scripts/evaluacion/golden/e1_enrutador/e1b_clasificadores.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, make_pipeline
from sklearn.svm import LinearSVC

import e1_enrutador as e

AQUI = Path(__file__).parent
NG = e.NG


def _tfidf():
    return FeatureUnion([
        ("palabras", TfidfVectorizer(preprocessor=e._norm, ngram_range=(1, 2), sublinear_tf=True)),
        ("caracteres", TfidfVectorizer(preprocessor=e._norm, analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
    ])


class _Embed:
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        M = np.array([e.r.embed_query(x) for x in X])
        return M / np.linalg.norm(M, axis=1, keepdims=True)


def _margenes(modelo, X):
    s = modelo.decision_function(X) if hasattr(modelo, "decision_function") else modelo.predict_proba(X)
    orden = np.sort(s, axis=1)
    return modelo.classes_[np.argmax(s, axis=1)], orden[:, -1] - orden[:, -2]


def main():
    casos = [json.loads(l) for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines()]
    dev = [c for c in casos if c["split"] == "dev"]
    test = [c for c in casos if c["split"] == "test"]
    X_tr = [q for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for q in qs] + [c["pregunta"] for c in dev]
    y_tr = [d for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for _ in qs] + [c["esperado"] for c in dev]

    modelos = {
        "C1_tfidf_svm": make_pipeline(_tfidf(), LinearSVC(C=1.0, class_weight="balanced")),
        "C2_tfidf_logreg": make_pipeline(_tfidf(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")),
        "C3_minilm_logreg": make_pipeline(_Embed(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")),
    }
    for m in modelos.values():
        m.fit(X_tr, y_tr)

    # Margen de rechazo: dev se usó para entrenar, así que se ajusta con
    # validación cruzada 5-fold sobre el conjunto de entrenamiento (honesto).
    from sklearn.model_selection import StratifiedKFold
    def ajustar_margen(fabrica):
        Xa, ya = np.array(X_tr, dtype=object), np.array(y_tr)
        pred_m = []
        for tr, va in StratifiedKFold(5, shuffle=True, random_state=169).split(Xa, ya):
            m = fabrica().fit(list(Xa[tr]), ya[tr])
            p, mg = _margenes(m, list(Xa[va]))
            pred_m += list(zip(p, mg, ya[va]))
        mejor = max(((sum((p if mg >= t else NG) == y for p, mg, y in pred_m), -t, t)
                     for t in np.round(np.arange(0, 1.01, 0.05), 2)))
        return mejor[2]

    fabricas = {
        "C1_tfidf_svm": lambda: make_pipeline(_tfidf(), LinearSVC(C=1.0, class_weight="balanced")),
        "C2_tfidf_logreg": lambda: make_pipeline(_tfidf(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")),
        "C3_minilm_logreg": lambda: make_pipeline(_Embed(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")),
    }
    umbrales = {k: ajustar_margen(f) for k, f in fabricas.items()}

    def router(nombre):
        m, t = modelos[nombre], umbrales[nombre]
        def f(q):
            p, mg = _margenes(m, [q])
            return p[0] if mg[0] >= t else NG
        return f

    variantes = {
        "V1_produccion": e.v1,
        "V3_margen_delta0.18": lambda q: e.v3(q, 0.18),
        **{f"{k}_rechazo{umbrales[k]}": router(k) for k in modelos},
        "C4_keyword+tfidf_svm": lambda q: e.r.route_motor(q) or router("C1_tfidf_svm")(q),
    }

    filas = {k: e.evaluar(test, fn) for k, fn in variantes.items()}
    base = [f["aceptable"] for f in filas["V1_produccion"]]
    comps, pv = [], []
    for k, fs in filas.items():
        if k == "V1_produccion":
            continue
        m = e.mcnemar_exacto(base, [f["aceptable"] for f in fs])
        comps.append((k, m)); pv.append(m["p"])
    holm = e.holm(pv)

    print(f"Entrenamiento: {len(X_tr)} preguntas | test E1: {len(test)}\n")
    print(f"{'variante (TEST)':34s} {'estricto':>9s} {'aceptable':>22s} {'callejón':>9s} {'p_holm vs V1':>13s}")
    salida = {"n_train": len(X_tr), "n_test": len(test), "umbrales": umbrales, "variantes": {}}
    ph = dict(zip([c[0] for c in comps], holm))
    for k, fs in filas.items():
        res = e.resumen(fs)
        a = res["aceptable"]
        salida["variantes"][k] = {**res, "p_holm_vs_V1": ph.get(k)}
        p = f"{ph[k]:.4f}" if k in ph else "—"
        print(f"{k:34s} {res['estricto']['p']:9.1%} {a['p']:8.1%} [{a['ic95'][0]:.1%}-{a['ic95'][1]:.1%}] {res['callejon_falso']['k']:>9d} {p:>13s}")
    (AQUI / "resultados_e1b.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
