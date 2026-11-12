"""
Clasificador de actividades de presupuesto por etapa y capítulo (#196). Sin LLM; Supabase solo lectura.

Datos:
  ORO     APU de los colegas (scripts/presupuesto/_privado/apu_colegas.jsonl): etiqueta humana (capítulo del
          ejercicio → taxonomía), sin copias exactas. Grupo = archivo (hash), para validar sin fuga.
  PLATA   Actividades de apu_precios_referencia (sin los insumos IAD) donde la línea base de palabras clave
          coincide con UN solo capítulo (sin ambigüedad). Etiqueta automática, con sesgo de las claves.
  SIN     El resto de actividades de la base: se clasifican al final y se proponen para etiquetar.

Experimentos (criterio fijado antes de correr):
  E1  oro → oro, GroupKFold(5) por archivo.
  E1b oro → oro, GroupKFold(5) por DESCRIPCIÓN normalizada: el modelo nunca vio esa actividad (todos los colegas
      presupuestaron la misma obra, así que E1 repite frases entre archivos y es optimista).
  E2  plata → oro (¿las etiquetas automáticas enseñan lo que un humano etiqueta?).
  E3  plata + oro → oro, GroupKFold(5) por archivo (la plata siempre en entrenamiento).
  Métricas: exactitud de capítulo y de ETAPA (el objetivo del usuario), macro-F1, y precisión/cobertura con
  rechazo (umbral τ elegido por validación cruzada interna para precisión ≥ 0,90 en capítulo).
Modelos: palabras clave (línea base), TF-IDF de caracteres 2–5 + regresión logística, MiniLM + regresión logística.

Uso: python scripts/presupuesto/clasificador_etapas.py
Salida: docs/presupuesto/CLASIFICADOR_ETAPAS.md, scripts/presupuesto/_privado/propuestas_clasificacion.csv
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupKFold

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import cobertura_etapas as cob  # noqa: E402

PRIVADO = AQUI / "_privado"
INFORME = RAIZ / "docs" / "presupuesto" / "CLASIFICADOR_ETAPAS.md"
PRECISION_OBJETIVO = 0.90
SEMILLA = 0


def cob_norm(x: str) -> str:
    import re
    import unicodedata
    x = unicodedata.normalize("NFKD", x.rsplit(" [", 1)[0]).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]+", " ", x).strip()[:30]


def texto(desc: str, unidad: str | None) -> str:
    return f"{desc} [{(unidad or '').strip().lower()}]"


def etapa(cap: str) -> str:
    return cap.split(".")[0]


def cargar_oro() -> tuple[list[str], list[str], list[str]]:
    X, y, g = [], [], []
    for l in (PRIVADO / "apu_colegas.jsonl").read_text(encoding="utf-8").splitlines():
        a = json.loads(l)
        if a.get("duplicado_de") or not a.get("capitulo_taxonomia"):
            continue
        X.append(texto(a["descripcion"], a["unidad"]))
        y.append(a["capitulo_taxonomia"])
        g.append(a["grupo"])
    return X, y, g


def cargar_base(caps) -> tuple[list[dict], list[dict]]:
    plata, sin = [], []
    for f in cob.leer_precios():
        if f["tipo_fuente"] in cob.INSUMOS_SUELTOS or not f["actividad"]:
            continue
        c, n = cob.clasificar(f["actividad"], caps)
        reg = {"texto": texto(f["actividad"], f["unidad"]), "actividad": f["actividad"], "unidad": f["unidad"],
               "region": f["region"], "tipo_fuente": f["tipo_fuente"], "clave": c["id"] if c else None}
        (plata if c is not None and n == 1 else sin).append(reg)
    return plata, sin


class Modelo:
    def __init__(self, tipo: str, emb=None):
        self.tipo, self.emb = tipo, emb
        self.clf = LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced")

    def _feat(self, X, ajustar=False):
        if self.tipo == "tfidf":
            if ajustar:
                self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True)
                return self.vec.fit_transform(X)
            return self.vec.transform(X)
        return self.emb(X)

    def fit(self, X, y):
        self.clf.fit(self._feat(X, True), y)
        return self

    def proba(self, X):
        return self.clf.predict_proba(self._feat(X)), self.clf.classes_


def embedder():
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    cache = {}

    def emb(X):
        faltan = [x for x in X if x not in cache]
        if faltan:
            for x, v in zip(faltan, m.encode(faltan, batch_size=64, normalize_embeddings=True, show_progress_bar=False)):
                cache[x] = v
        return np.vstack([cache[x] for x in X])
    return emb


def metricas(y_true, y_pred, conf, tau=None) -> dict:
    y_true, y_pred, conf = np.array(y_true), np.array(y_pred), np.array(conf)
    d = {"n": len(y_true), "exactitud_capitulo": float((y_true == y_pred).mean()),
         "exactitud_etapa": float(np.mean([etapa(a) == etapa(b) for a, b in zip(y_true, y_pred)])),
         "macro_f1_capitulo": float(f1_score(y_true, y_pred, average="macro", zero_division=0))}
    if tau is not None:
        acept = conf >= tau
        d.update(tau=tau, cobertura=float(acept.mean()),
                 precision_capitulo_aceptadas=float((y_true[acept] == y_pred[acept]).mean()) if acept.any() else float("nan"),
                 precision_etapa_aceptadas=float(np.mean([etapa(a) == etapa(b) for a, b in zip(y_true[acept], y_pred[acept])])) if acept.any() else float("nan"))
    return d


def elegir_tau(y, pred, conf, objetivo=PRECISION_OBJETIVO) -> float:
    """Menor τ cuya precisión en las aceptadas alcanza el objetivo (sobre predicciones fuera de pliegue)."""
    y, pred, conf = np.array(y), np.array(pred), np.array(conf)
    for tau in np.round(np.arange(0.0, 0.96, 0.025), 3):
        a = conf >= tau
        if a.sum() >= 20 and (y[a] == pred[a]).mean() >= objetivo:
            return float(tau)
    return 0.95


def cv_oof(tipo, emb, X, y, g, extra_X=(), extra_y=()):
    """Predicciones fuera de pliegue sobre el oro (GroupKFold por archivo); extra siempre en entrenamiento."""
    pred, conf = [None] * len(X), [0.0] * len(X)
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        Xtr = [X[i] for i in tr] + list(extra_X)
        ytr = [y[i] for i in tr] + list(extra_y)
        m = Modelo(tipo, emb).fit(Xtr, ytr)
        P, cl = m.proba([X[i] for i in te])
        for k, i in enumerate(te):
            j = int(P[k].argmax())
            pred[i], conf[i] = cl[j], float(P[k][j])
    return pred, conf


def main() -> None:
    caps = cob.cargar_taxonomia()
    Xo, yo, go = cargar_oro()
    plata, sin = cargar_base(caps)
    Xp, yp = [p["texto"] for p in plata], [p["clave"] for p in plata]
    print(f"oro {len(Xo)} ({len(set(go))} archivos, {len(set(yo))} capítulos) | plata {len(Xp)} | sin etiqueta {len(sin)}", flush=True)
    emb = embedder()
    filas = []

    # Línea base: palabras clave sobre el oro
    kw = [cob.clasificar(x.rsplit(" [", 1)[0], caps)[0] for x in Xo]
    cubiertos = [i for i, c in enumerate(kw) if c]
    d = metricas([yo[i] for i in cubiertos], [kw[i]["id"] for i in cubiertos], [1.0] * len(cubiertos))
    d.update(cobertura=len(cubiertos) / len(Xo))
    filas.append(("Palabras clave (línea base)", "—", d))

    for tipo, nombre in (("tfidf", "TF-IDF caracteres + LR"), ("emb", "MiniLM + LR")):
        # E1
        pred, conf = cv_oof(tipo, emb, Xo, yo, go)
        tau = elegir_tau(yo, pred, conf)
        filas.append((nombre, "E1 oro→oro (por archivo)", metricas(yo, pred, conf, tau)))
        gd = [cob_norm(x) for x in Xo]
        predb, confb = cv_oof(tipo, emb, Xo, yo, gd)
        filas.append((nombre, "E1b oro→oro (actividad no vista)", metricas(yo, predb, confb, elegir_tau(yo, predb, confb))))
        # E2
        m = Modelo(tipo, emb).fit(Xp, yp)
        P, cl = m.proba(Xo)
        pred2 = [cl[int(r.argmax())] for r in P]
        conf2 = [float(r.max()) for r in P]
        filas.append((nombre, "E2 plata→oro", metricas(yo, pred2, conf2, elegir_tau(yo, pred2, conf2))))
        # E3
        pred3, conf3 = cv_oof(tipo, emb, Xo, yo, go, Xp, yp)
        tau3 = elegir_tau(yo, pred3, conf3)
        filas.append((nombre, "E3 plata+oro→oro (por archivo)", metricas(yo, pred3, conf3, tau3)))
        print(nombre, "listo", flush=True)

    # Modelo final: MiniLM + LR con plata + oro; τ de E3. Propuestas para las actividades sin etiqueta.
    e1b = [(n, d) for n, e, d in filas if e.startswith("E1b")]
    ganador, d_gan = max(e1b, key=lambda t: (t[1]["exactitud_etapa"], t[1]["exactitud_capitulo"]))
    tipo_final = "tfidf" if ganador.startswith("TF-IDF") else "emb"
    tau_final = d_gan["tau"]
    # Solo oro: E2/E3 muestran que la plata no mejora frente a la etiqueta humana.
    final = Modelo(tipo_final, emb).fit(Xo, yo)
    print("modelo final:", ganador, "τ", tau_final, flush=True)
    P, cl = final.proba([s["texto"] for s in sin])
    nombres = {c["id"]: c["nombre"] for c in caps}
    props = []
    for s, r in zip(sin, P):
        orden = r.argsort()[::-1]
        j, j2 = int(orden[0]), int(orden[1])
        props.append({**{k: s[k] for k in ("actividad", "unidad", "region", "tipo_fuente")},
                      "capitulo_propuesto": cl[j], "nombre": nombres.get(cl[j]), "confianza": round(float(r[j]), 3),
                      "segunda_opcion": cl[j2], "margen": round(float(r[j] - r[j2]), 3),
                      "aceptada": bool(r[j] >= tau_final)})
    PRIVADO.mkdir(exist_ok=True)
    props.sort(key=lambda p: p["margen"])          # aprendizaje activo: primero las más dudosas
    with (PRIVADO / "propuestas_clasificacion.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(props[0]) + ["capitulo_correcto"])
        w.writeheader()
        for p in props:
            w.writerow({**p, "capitulo_correcto": ""})
    acept = [p for p in props if p["aceptada"]]
    por_cap = collections.Counter(p["capitulo_propuesto"] for p in acept)

    def pct(v):
        return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.1%}"
    l = ["# Clasificador de actividades por etapa y capítulo (#196)", "",
         "Generado por `scripts/presupuesto/clasificador_etapas.py`. Sin LLM; Supabase solo lectura.", "",
         f"- **Oro** (etiqueta humana): {len(Xo)} APU de los colegas, {len(set(go))} archivos, {len(set(yo))} capítulos, "
         "una sola obra (vivienda campestre).",
         f"- **Plata** (etiqueta automática): {len(Xp)} actividades de la base donde las palabras clave dan un solo capítulo.",
         f"- **Sin etiqueta**: {len(sin)} actividades de la base (sin coincidencia o ambiguas).", "",
         f"Umbral de rechazo τ: el menor que da precisión de capítulo ≥ {PRECISION_OBJETIVO:.0%} en las aceptadas "
         "(validación fuera de pliegue).", "",
         "| Modelo | Experimento | n | Exactitud capítulo | Exactitud ETAPA | Macro-F1 capítulo | τ | Cobertura | Precisión capítulo (aceptadas) | Precisión etapa (aceptadas) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for n, e, d in filas:
        l.append(f"| {n} | {e} | {d['n']} | {pct(d['exactitud_capitulo'])} | {pct(d['exactitud_etapa'])} | "
                 f"{d['macro_f1_capitulo']:.2f} | {d.get('tau', '—')} | {pct(d.get('cobertura'))} | "
                 f"{pct(d.get('precision_capitulo_aceptadas'))} | {pct(d.get('precision_etapa_aceptadas'))} |")
    l += ["", f"**Aplicado a las {len(sin)} actividades sin etiqueta** ({ganador} entrenado con el oro, elegido por E1b; τ = {tau_final}): "
          f"{len(acept)} aceptadas ({len(acept) / max(len(sin), 1):.0%}); el resto queda para etiquetar.",
          "", "Aceptadas por capítulo: " + ", ".join(f"{k} {v}" for k, v in sorted(por_cap.items())), "",
          "**Advertencia (revisión manual de una muestra, 2026-11-12):** el umbral τ se calibró con los APU de los "
          "colegas (una sola obra de vivienda) y **no se transfiere a la base**, que es otro dominio (contratos de "
          "redes, vías y catálogos). En la muestra aparecen errores claros: accesorios sanitarios y diámetros "
          "('codo reventilado', 'D=160mm') propuestos como eléctricas; adoquín como pisos en vez de urbanismo. "
          "Además el oro no tiene ejemplos de 0.x, 2.2, 2.5 ni 4.3, que el modelo no puede predecir. Las "
          "'aceptadas' de la base NO están validadas: hace falta una muestra etiquetada por una persona "
          "(`_privado/muestra_para_etiquetar.csv`) antes de usar el clasificador fuera del dominio de vivienda.", "",
          "Hallazgo de datos para #200: hay filas que son sub-ítems sin su actividad padre ('D=110mm.', "
          "'En zona dura', 'De 0,15 m x 0,20 m'): la jerarquía del contrato se aplanó al cargarlos.", "",
          "Las propuestas (ordenadas de más dudosa a más segura, para aprendizaje activo) están en "
          "`scripts/presupuesto/_privado/propuestas_clasificacion.csv`, columna `capitulo_correcto` para etiquetar.",
          "**Nada se escribe en `apu_precios_referencia`**: la columna de capítulo en producción se decide aparte."]
    INFORME.write_text("\n".join(l) + "\n", encoding="utf-8")
    print("\n".join(l))


if __name__ == "__main__":
    sys.exit(main())
