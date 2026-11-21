"""
E1e del issue #169: clasificador de dominio (MiniLM + regresión logística) con
(1) ajuste del umbral de confianza y (2) aprendizaje activo.

Sin LLM, sin escritura en Supabase.

1. Umbral (selective classification, Chow 1970). El clasificador responde
   con su dominio si p_max >= tau; si no, rechaza hacia normativa_general,
   que casi siempre da una respuesta aceptable. tau minimiza, por validación
   cruzada sobre los datos etiquetados, el costo
       C(tau) = errores_de_dominio + lambda * rechazos_de_preguntas_no_NG
   con lambda = 0,35: mandar a NG una pregunta de motor cuesta menos que
   mandarla al motor equivocado (en el E1, NG fue aceptable en el 94 % de
   las sísmicas por municipio, mientras que un motor equivocado produjo los
   6 callejones). Se reporta además la curva riesgo-cobertura en test.

2. Aprendizaje activo (Settles, 2009). Se parte de lo que tiene producción
   (los 86 ejemplos de referencia del contrastivo). Por ronda, el modelo elige
   10 preguntas de un pool, un oráculo revela su etiqueta y se reentrena.
   Pool (371): las baterías existentes con etiqueta derivable
     - dataset_baseline_nsr10: Título H y NTC 174 -> geopot, Título E ->
       vulnerabilidad_vivienda, el resto -> normativa_general
     - dataset_baseline_precios -> apu_precios
     - split dev del E1 (su etiqueta estricta)
   Estrategias: aleatoria (5 semillas), menor confianza, margen, entropía,
   y margen + diversidad (k-medias sobre los embeddings de los candidatos
   más inciertos, una pregunta por grupo).
   Evaluación de cada ronda: el mismo test del E1 (58), nunca visto.

Uso: python scripts/evaluacion/golden/e1_enrutador/e1e_umbral_activo.py
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

import e1_enrutador as e

AQUI = Path(__file__).parent
EVAL = AQUI.parents[1]
NG = e.NG
LAMBDA = 0.35
LOTE = 10
RONDAS = 15
GRILLA_TAU = np.round(np.arange(0.20, 0.91, 0.05), 2)


# ── datos ──────────────────────────────────────────────────────────────────
def _literal(archivo, var):
    for nodo in ast.parse((EVAL / archivo).read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, "id", "") == var for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise KeyError(var)


def _etiqueta_nsr10(caso_id: str) -> str:
    pref = caso_id.split("-")[0]
    if pref == "H" or pref.startswith("NTC174"):
        return "geopot"
    if pref == "E":
        return "vulnerabilidad_vivienda"
    return NG


def cargar():
    casos = [json.loads(l) for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines()]
    test = [c for c in casos if c["split"] == "test"]
    semilla = [(q, d) for d, qs in e.mrc.EJEMPLOS_POR_DOMINIO.items() for q in qs]
    pool = [(c["pregunta"], _etiqueta_nsr10(c["id"]), "nsr10") for c in _literal("dataset_baseline_nsr10.py", "CASOS_BASELINE")]
    pool += [(c["pregunta"], "apu_precios", "precios") for c in _literal("dataset_baseline_precios.py", "CASOS_BASELINE_PRECIOS")]
    pool += [(c["pregunta"], c["esperado"], "e1_dev") for c in casos if c["split"] == "dev"]
    return semilla, pool, test


_emb: dict[str, np.ndarray] = {}


def emb(textos):
    for t in textos:
        if t not in _emb:
            v = np.asarray(e.r.embed_query(t), dtype=float)
            _emb[t] = v / np.linalg.norm(v)
    return np.array([_emb[t] for t in textos])


# ── clasificador con umbral ────────────────────────────────────────────────
def entrenar(X, y):
    return LogisticRegression(C=10, max_iter=4000, class_weight="balanced").fit(X, y)


def decidir(modelo, X, tau):
    P = modelo.predict_proba(X)
    pred = modelo.classes_[P.argmax(1)]
    return np.where(P.max(1) >= tau, pred, NG), P


def costo(pred, y):
    pred, y = np.asarray(pred), np.asarray(y)
    errores = ((pred != y) & (pred != NG)).sum()           # dominio equivocado
    rechazos = ((pred == NG) & (y != NG)).sum()             # se mandó a NG sin serlo
    return errores + LAMBDA * rechazos


def ajustar_tau(X, y, semilla=0):
    """tau por validación cruzada (k = min(5, clase más chica)) minimizando el costo."""
    y = np.asarray(y)
    k = int(min(5, np.bincount(np.unique(y, return_inverse=True)[1]).min()))
    if k < 2:
        return 0.5
    probs, ys = [], []
    for tr, va in StratifiedKFold(k, shuffle=True, random_state=semilla).split(X, y):
        m = entrenar(X[tr], y[tr])
        probs.append((m, X[va]))
        ys.append(y[va])
    return float(min(GRILLA_TAU, key=lambda t: (sum(costo(decidir(m, Xv, t)[0], yv) for (m, Xv), yv in zip(probs, ys)), -t)))


def evaluar_test(modelo, tau, test):
    pred, _ = decidir(modelo, emb([c["pregunta"] for c in test]), tau)
    estricto = np.mean([p == c["esperado"] for p, c in zip(pred, test)])
    aceptable = np.mean([p in c["aceptables"] for p, c in zip(pred, test)])
    callejon = sum(p in e.CALLEJONES and c["esperado"] not in e.CALLEJONES for p, c in zip(pred, test))
    return {"estricto": float(estricto), "aceptable": float(aceptable), "callejon": int(callejon), "tau": tau,
            "pred": list(pred)}


def riesgo_cobertura(modelo, test):
    X = emb([c["pregunta"] for c in test])
    P = modelo.predict_proba(X)
    pred = modelo.classes_[P.argmax(1)]
    conf = P.max(1)
    orden = np.argsort(-conf)
    curva = []
    for n in range(1, len(test) + 1):
        idx = orden[:n]
        curva.append((n / len(test), float(np.mean([pred[i] != test[i]["esperado"] for i in idx]))))
    aurc = float(np.mean([r for _, r in curva]))
    return curva, aurc


# ── aprendizaje activo ─────────────────────────────────────────────────────
def puntaje_incertidumbre(P, estrategia):
    s = np.sort(P, axis=1)
    if estrategia == "menor_confianza":
        return 1 - s[:, -1]
    if estrategia in ("margen", "margen_diversidad"):
        return -(s[:, -1] - s[:, -2])
    if estrategia == "entropia":
        return -(P * np.log(P + 1e-12)).sum(1)
    raise ValueError(estrategia)


def correr_activo(estrategia, semilla, pool, test, semilla_rng=0):
    rng = np.random.default_rng(semilla_rng)
    L_txt = [q for q, _ in semilla]
    L_y = [d for _, d in semilla]
    U = list(range(len(pool)))
    Xp = emb([q for q, _, _ in pool])
    curva = []
    for ronda in range(RONDAS + 1):
        X = emb(L_txt)
        y = np.array(L_y)
        modelo = entrenar(X, y)
        tau = ajustar_tau(X, y)
        res = evaluar_test(modelo, tau, test)
        curva.append({"etiquetas_nuevas": ronda * LOTE, "estricto": res["estricto"], "aceptable": res["aceptable"],
                      "callejon": res["callejon"], "tau": tau})
        if ronda == RONDAS or not U:
            break
        if estrategia == "aleatoria":
            elegidos = list(rng.choice(U, size=min(LOTE, len(U)), replace=False))
        else:
            P = modelo.predict_proba(Xp[U])
            punt = puntaje_incertidumbre(P, estrategia)
            if estrategia == "margen_diversidad":
                cand = [U[i] for i in np.argsort(-punt)[: LOTE * 4]]
                km = KMeans(n_clusters=LOTE, n_init=5, random_state=semilla_rng).fit(Xp[cand])
                elegidos = []
                for g in range(LOTE):
                    miembros = [c for c, l in zip(cand, km.labels_) if l == g]
                    elegidos.append(max(miembros, key=lambda c: punt[U.index(c)]))
            else:
                elegidos = [U[i] for i in np.argsort(-punt)[:LOTE]]
        for i in elegidos:
            L_txt.append(pool[i][0])
            L_y.append(pool[i][1])   # el oráculo revela la etiqueta
            U.remove(i)
    return curva


def main():
    global semilla
    semilla, pool, test = cargar()
    emb([q for q, _ in semilla] + [q for q, _, _ in pool] + [c["pregunta"] for c in test])

    # 1) umbral con los datos que ya tiene producción
    Xs, ys = emb([q for q, _ in semilla]), np.array([d for _, d in semilla])
    m0 = entrenar(Xs, ys)
    tau0 = ajustar_tau(Xs, ys)
    barrido = {float(t): {k: v for k, v in evaluar_test(m0, float(t), test).items() if k != "pred"} for t in GRILLA_TAU}
    curva_rc, aurc0 = riesgo_cobertura(m0, test)

    # 2) aprendizaje activo
    resultados = {}
    for est in ("menor_confianza", "margen", "entropia", "margen_diversidad"):
        resultados[est] = correr_activo(est, semilla, pool, test)
    aleatorias = [correr_activo("aleatoria", semilla, pool, test, semilla_rng=s) for s in range(5)]
    resultados["aleatoria_media5"] = [
        {"etiquetas_nuevas": r0["etiquetas_nuevas"],
         "estricto": float(np.mean([a[i]["estricto"] for a in aleatorias])),
         "estricto_min": float(np.min([a[i]["estricto"] for a in aleatorias])),
         "estricto_max": float(np.max([a[i]["estricto"] for a in aleatorias])),
         "aceptable": float(np.mean([a[i]["aceptable"] for a in aleatorias])),
         "callejon": float(np.mean([a[i]["callejon"] for a in aleatorias]))}
        for i, r0 in enumerate(aleatorias[0])]

    # modelo final: todo el pool etiquetado (techo de "etiquetar todo")
    Xf = emb([q for q, _ in semilla] + [q for q, _, _ in pool])
    yf = np.array([d for _, d in semilla] + [d for _, d, _ in pool])
    mf = entrenar(Xf, yf)
    tauf = ajustar_tau(Xf, yf)
    techo = {k: v for k, v in evaluar_test(mf, tauf, test).items() if k != "pred"}
    _, aurcf = riesgo_cobertura(mf, test)

    salida = {"lambda": LAMBDA, "lote": LOTE, "rondas": RONDAS, "n_semilla": len(semilla), "n_pool": len(pool),
              "n_test": len(test), "umbral_semilla": {"tau_cv": tau0, "aurc": aurc0, "barrido_test": barrido,
                                                      "curva_riesgo_cobertura": curva_rc},
              "activo": resultados, "techo_todo_el_pool": {**techo, "aurc": aurcf}}
    (AQUI / "resultados_e1e.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")

    print(f"semilla {len(semilla)} | pool {len(pool)} | test {len(test)} | lambda {LAMBDA}\n")
    print(f"1) UMBRAL con la semilla de producción: tau por CV = {tau0} | AURC test = {aurc0:.3f}")
    print("   tau   estricto  aceptable  callejón")
    for t, v in barrido.items():
        marca = " <- CV" if abs(t - tau0) < 1e-9 else ""
        print(f"   {t:.2f}  {v['estricto']:8.1%}  {v['aceptable']:8.1%}  {v['callejon']:5d}{marca}")
    print("\n2) APRENDIZAJE ACTIVO: estricto en test por número de etiquetas nuevas")
    cols = list(resultados)
    print("   +etiq " + " ".join(f"{c[:17]:>17s}" for c in cols))
    for i in range(RONDAS + 1):
        print(f"   {i * LOTE:5d} " + " ".join(f"{resultados[c][i]['estricto']:17.1%}" for c in cols))
    print(f"\n   área bajo la curva (estricto medio en las {RONDAS + 1} rondas):")
    for c in cols:
        print(f"     {c:20s} {np.mean([x['estricto'] for x in resultados[c]]):.3f}")
    print(f"\n   techo (las {len(pool)} etiquetadas): estricto {techo['estricto']:.1%} aceptable {techo['aceptable']:.1%} "
          f"callejón {techo['callejon']} tau {tauf} AURC {aurcf:.3f}")


if __name__ == "__main__":
    main()
