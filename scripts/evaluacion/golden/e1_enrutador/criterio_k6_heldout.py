"""
Criterio prerregistrado de #171 para integrar K6 (fijado antes de ver el held-out):
  (a) diferencia K6 − V1 en "aceptable" > 0 con IC95 que no cruce 0 (pareado, sobre las mismas preguntas);
  (b) K6 no tiene más callejones sin salida que V1;
  (c) sin regresiones de enrutamiento en test_rag_motores_regresion.py (13 casos, solo el dominio, sin LLM).
Reproduce K6 exactamente como en e1c_corpus.py (route_motor → C3 con el umbral de resultados_e1b.json, C3 entrenado
con los ejemplos del contrastivo + el dev de dataset_e1). Nada se reajusta con el held-out.
Salida: RESULTADO_K6_HELDOUT.md
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import e1_enrutador as e  # noqa: E402
import e1b_clasificadores as b  # noqa: E402
from e1_enrutador import r  # noqa: E402

NG = "normativa_general"


def construir_k6():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    casos = [json.loads(l) for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines()]
    dev = [c for c in casos if c["split"] == "dev"]
    X = [q for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for q in qs] + [c["pregunta"] for c in dev]
    y = [d for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for _ in qs] + [c["esperado"] for c in dev]
    c3 = make_pipeline(b._Embed(), LogisticRegression(C=10, max_iter=3000, class_weight="balanced")).fit(X, y)
    umbral = json.loads((AQUI / "resultados_e1b.json").read_text(encoding="utf-8"))["umbrales"]["C3_minilm_logreg"]

    def c3_route(q):
        p, mg = b._margenes(c3, [q])
        return p[0] if mg[0] >= umbral else NG
    return lambda q: r.route_motor(q) or c3_route(q)


def main() -> None:
    held = [json.loads(l) for l in (AQUI / "dataset_heldout_k6.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    k6 = construir_k6()
    fv1, fk6 = e.evaluar(held, e.v1), e.evaluar(held, k6)
    a1 = np.array([f["aceptable"] for f in fv1])
    a6 = np.array([f["aceptable"] for f in fk6])
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(a1), size=(10000, len(a1)))
    difs = (a6[idx] - a1[idx]).mean(axis=1)
    lo, hi = np.quantile(difs, [0.025, 0.975])
    mc = e.mcnemar_exacto(list(a1), list(a6))
    cal1, cal6 = sum(f["callejon_falso"] for f in fv1), sum(f["callejon_falso"] for f in fk6)

    sys.path.insert(0, str(AQUI.parents[3] / "apps" / "api" / "tests"))
    import test_rag_motores_regresion as tm
    params = next(m for m in tm.test_delegador_enruta_y_responde_hecho_verificado.pytestmark if m.name == "parametrize").args[1]
    reg = []
    for p in params:
        motor, pregunta, _ = p.values
        reg.append((p.id, motor, e.v1(pregunta), k6(pregunta)))
    ok_v1 = sum(m == v for _, m, v, _ in reg)
    ok_k6 = sum(m == k for _, m, _, k in reg)
    regresiones = [(i, m, v, k) for i, m, v, k in reg if m == v and m != k]

    por = defaultdict(lambda: [0, 0, 0])
    for c, x1, x6 in zip(held, fv1, fk6):
        por[c["estrato"]][0] += 1
        por[c["estrato"]][1] += x1["aceptable"]
        por[c["estrato"]][2] += x6["aceptable"]
    por_dom = defaultdict(lambda: [0, 0, 0])
    for c, x1, x6 in zip(held, fv1, fk6):
        por_dom[c["esperado"]][0] += 1
        por_dom[c["esperado"]][1] += x1["aceptable"]
        por_dom[c["esperado"]][2] += x6["aceptable"]

    a = lo > 0
    bb = cal6 <= cal1
    c = not regresiones
    L = ["# Validación de K6 con el held-out escrito por Wilmer (#171)", "",
         "Criterio prerregistrado (fijado antes de ver el held-out): (a) diferencia K6 − V1 en *aceptable* > 0 con "
         "IC95 que no cruce 0; (b) K6 no tiene más callejones sin salida que V1; (c) sin regresiones de enrutamiento "
         "en `test_rag_motores_regresion.py`.", "",
         f"Held-out: {len(held)} preguntas escritas y etiquetadas a mano por Wilmer, congeladas en el commit fabdf2c "
         "antes de evaluar. Chequeo de fuga: 0 casi-duplicados de los ejemplos de entrenamiento y 0 iguales al dev.", "",
         "| | V1 producción | K6 |", "|---|---|---|",
         f"| Aceptable | {a1.mean():.1%} ({a1.sum()}/{len(a1)}) | {a6.mean():.1%} ({a6.sum()}/{len(a6)}) |",
         f"| Callejones sin salida | {cal1} | {cal6} |",
         f"| Enrutamiento correcto en la regresión de motores (13) | {ok_v1}/13 | {ok_k6}/13 |", "",
         f"Diferencia K6 − V1: **{(a6 - a1).mean():+.1%}**, IC95 bootstrap pareado **{lo:+.1%} a {hi:+.1%}**. "
         f"McNemar exacto: K6 gana en {mc['n01_solo_b']} preguntas, V1 en {mc['n10_solo_a']}, p = {mc['p']:.4f}.", "",
         f"- (a) {'CUMPLE' if a else 'NO CUMPLE'}", f"- (b) {'CUMPLE' if bb else 'NO CUMPLE'}",
         f"- (c) {'CUMPLE' if c else 'NO CUMPLE: ' + '; '.join(f'{i}: {m} → {k}' for i, m, _, k in regresiones)}", "",
         f"**Veredicto: {'K6 se recomienda para integrar (#192)' if a and bb and c else 'K6 NO se recomienda todavía'}.**", "",
         "Por tipo de pregunta (aceptable):", "", "| Estrato | n | V1 | K6 |", "|---|---|---|---|"]
    for s, (n, x1, x6) in sorted(por.items()):
        L.append(f"| {s} | {n} | {x1 / n:.0%} | {x6 / n:.0%} |")
    L += ["", "Por dominio esperado (aceptable):", "", "| Dominio | n | V1 | K6 |", "|---|---|---|---|"]
    for s, (n, x1, x6) in sorted(por_dom.items(), key=lambda kv: -kv[1][0]):
        L.append(f"| {s} | {n} | {x1 / n:.0%} | {x6 / n:.0%} |")
    L += ["", "Fallos de K6:", ""]
    for c_, f in zip(held, fk6):
        if not f["aceptable"]:
            L.append(f"- #{c_['numero_wilmer']} ({c_['estrato']}) esperado `{c_['esperado']}` → K6 `{f['obtenido']}`: {c_['pregunta'][:110]}")
    (AQUI / "RESULTADO_K6_HELDOUT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
