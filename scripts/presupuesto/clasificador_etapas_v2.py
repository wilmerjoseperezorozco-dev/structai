"""
Clasificador por etapa y capítulo, v2: suma las actividades de EPC (redes de acueducto y alcantarillado, Cundinamarca)
como segundo dominio etiquetado (#196, #201). Sin LLM; Supabase solo lectura.

Etiquetas de EPC: cada actividad hereda el capítulo de la taxonomía según su CAPÍTULO/SUBCAPÍTULO en la cartilla
(estructura hecha por EPC; el mapeo a la taxonomía es una decisión documentada en MAPEO_EPC, revisable). Lo ambiguo
se EXCLUYE (no se fuerza): morteros sueltos, materiales para filtros, obras de protección, elementos de polietileno.

Experimentos (fijados antes de correr):
  A  colegas → EPC (todo): línea base, lo que mostró H5.
  B  colegas + EPC → EPC, GroupKFold(5) por actividad de EPC (la colega siempre en entrenamiento).
  B2 igual que B pero agrupando por SUBCAPÍTULO de EPC: el modelo nunca vio ningún ítem de ese tipo (B es optimista
     porque muchas actividades solo cambian el diámetro).
  C  colegas + EPC → colegas, GroupKFold(5) por descripción (E1b): sumar EPC no debe empeorar la vivienda.
Criterio para adoptar v2: B mejora la etapa en EPC frente a A, y C no baja más de 2 puntos la etapa frente a E1b v1.

Salida: docs/presupuesto/CLASIFICADOR_ETAPAS_V2.md, scripts/presupuesto/_privado/propuestas_clasificacion_v2.csv
"""
from __future__ import annotations

import collections
import csv
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupKFold

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import clasificador_etapas as v1  # noqa: E402
import cobertura_etapas as cob  # noqa: E402

EPC = RAIZ / "scripts" / "ingesta" / "epc" / "salida" / "epc_precios_largo.csv"
INFORME = RAIZ / "docs" / "presupuesto" / "CLASIFICADOR_ETAPAS_V2.md"
EXCLUIR = "excluir"
# (capítulo EPC, subcapítulo EPC o "*") → capítulo de la taxonomía. Se aplica la primera regla que coincide.
MAPEO_EPC = [
    ("CARGUE Y RETIRO DE SOBRANTES", "*", "1.2"),
    ("CONCRETOS", "MORTEROS", EXCLUIR),
    ("CONCRETOS", "*", "1.4"),
    ("CONDUCCIONES Y REDES DE ACUEDUCTO", "*", "4.3"),
    ("DEMOLICIONES", "*", "1.1"),
    ("EXCAVACIONES", "*", "1.2"),
    ("IMPACTO URBANO", "*", "0.2"),
    ("OBRAS PRELIMINARES", "*", "1.1"),
    ("PLANTAS DE TRATAMIENTO", "ACABADOS PARA PISOS", "3.2"),
    ("PLANTAS DE TRATAMIENTO", "APARATOS SANITARIOS", "3.5"),
    ("PLANTAS DE TRATAMIENTO", "CARPINTERIA METALICA", "3.3"),
    ("PLANTAS DE TRATAMIENTO", "CERRAMIENTO", "4.4"),
    ("PLANTAS DE TRATAMIENTO", "CUBIERTAS", "1.7"),
    ("PLANTAS DE TRATAMIENTO", "MAMPOSTERIA", "1.6"),
    ("PLANTAS DE TRATAMIENTO", "PINTURAS", "3.1"),
    ("PLANTAS DE TRATAMIENTO", "PUNTOS HIDRAULICOS", "2.1"),
    ("PLANTAS DE TRATAMIENTO", "*", EXCLUIR),          # filtros, polietileno: propios de la planta
    ("RECONSTRUCCION DE PAVIMENTOS", "RECONSTRUCCION DE PAVIMENTOS", "4.2"),
    ("RECONSTRUCCION DE PAVIMENTOS", "*", "4.1"),       # andenes y sardineles
    ("REDES DE ALCANTARILLADO", "*", "4.3"),
    ("RELLENOS", "OBRAS DE PROTECCION", EXCLUIR),
    ("RELLENOS", "*", "1.2"),
]


def n(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()


def mapear(cap: str, sub: str) -> str | None:
    c, s = n(cap), n(sub)
    for rc, rs, destino in MAPEO_EPC:
        if c.startswith(rc) and (rs == "*" or s.startswith(rs)):
            return destino
    return None


def cargar_epc(agrupar_por: str = "actividad") -> tuple[list[str], list[str], list[str], collections.Counter]:
    vistos, X, y, g = set(), [], [], []
    excl = collections.Counter()
    with EPC.open(encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            clave = (n(f["actividad"]), n(f["unidad"]))
            if clave in vistos:
                continue
            vistos.add(clave)
            destino = mapear(f["capitulo"], f["subcapitulo"])
            if destino in (None, EXCLUIR):
                excl[f"{n(f['capitulo'])[:30]} / {n(f['subcapitulo'])[:30]}"] += 1
                continue
            X.append(v1.texto(f["actividad"], f["unidad"]))
            y.append(destino)
            g.append(v1.cob_norm(X[-1]) if agrupar_por == "actividad" else n(f["subcapitulo"]))
    return X, y, g, excl


def main() -> None:
    Xo, yo, go = v1.cargar_oro()
    Xe, ye, ge = (*cargar_epc()[:3],)
    _, _, _, excl = cargar_epc()
    print(f"colegas {len(Xo)} | EPC {len(Xe)} (excluidas {sum(excl.values())})", flush=True)
    filas = []

    # A: colegas → EPC
    m = v1.Modelo("tfidf").fit(Xo, yo)
    P, cl = m.proba(Xe)
    pa = [cl[int(r.argmax())] for r in P]
    ca = [float(r.max()) for r in P]
    filas.append(("A colegas → EPC (línea base)", v1.metricas(ye, pa, ca, v1.elegir_tau(ye, pa, ca))))

    # B: colegas + EPC → EPC, por actividad de EPC
    pb, cb = [None] * len(Xe), [0.0] * len(Xe)
    for tr, te in GroupKFold(n_splits=5).split(Xe, ye, ge):
        mm = v1.Modelo("tfidf").fit(Xo + [Xe[i] for i in tr], yo + [ye[i] for i in tr])
        Pp, cc = mm.proba([Xe[i] for i in te])
        for k, i in enumerate(te):
            j = int(Pp[k].argmax())
            pb[i], cb[i] = cc[j], float(Pp[k][j])
    filas.append(("B colegas + EPC → EPC (actividad no vista)", v1.metricas(ye, pb, cb, v1.elegir_tau(ye, pb, cb))))
    _, _, gs, _ = cargar_epc("subcapitulo")
    p2b, c2b = [None] * len(Xe), [0.0] * len(Xe)
    for tr, te in GroupKFold(n_splits=5).split(Xe, ye, gs):
        mm = v1.Modelo("tfidf").fit(Xo + [Xe[i] for i in tr], yo + [ye[i] for i in tr])
        Pp, cc = mm.proba([Xe[i] for i in te])
        for k, i in enumerate(te):
            j = int(Pp[k].argmax())
            p2b[i], c2b[i] = cc[j], float(Pp[k][j])
    filas.append(("B2 colegas + EPC → EPC (subcapítulo no visto)", v1.metricas(ye, p2b, c2b, v1.elegir_tau(ye, p2b, c2b))))

    # C: colegas + EPC → colegas (E1b), y referencia v1
    gd = [v1.cob_norm(x) for x in Xo]
    p1, c1 = v1.cv_oof("tfidf", None, Xo, yo, gd)
    filas.append(("v1: colegas → colegas (E1b)", v1.metricas(yo, p1, c1, v1.elegir_tau(yo, p1, c1))))
    p2, c2 = v1.cv_oof("tfidf", None, Xo, yo, gd, Xe, ye)
    filas.append(("C colegas + EPC → colegas (E1b)", v1.metricas(yo, p2, c2, v1.elegir_tau(yo, p2, c2))))

    d = dict(filas)
    mejora_b = d["B colegas + EPC → EPC (actividad no vista)"]["exactitud_etapa"] - d["A colegas → EPC (línea base)"]["exactitud_etapa"]
    caida_c = d["v1: colegas → colegas (E1b)"]["exactitud_etapa"] - d["C colegas + EPC → colegas (E1b)"]["exactitud_etapa"]
    adoptar = mejora_b > 0 and caida_c <= 0.02

    # Confusión de 4.3 (redes externas) en B
    conf = collections.Counter(p for t, p in zip(ye, pb) if t == "4.3")

    # Modelo final v2 (si se adopta): colegas + EPC; propuestas para las actividades sin etiqueta de la base
    caps = cob.cargar_taxonomia()
    plata, sin = v1.cargar_base(caps)
    tau = d["C colegas + EPC → colegas (E1b)"]["tau"]
    final = v1.Modelo("tfidf").fit(Xo + Xe, yo + ye)
    P, cl = final.proba([s["texto"] for s in sin])
    nombres = {c["id"]: c["nombre"] for c in caps}
    props = []
    for s, r in zip(sin, P):
        o = r.argsort()[::-1]
        props.append({**{k: s[k] for k in ("actividad", "unidad", "region", "tipo_fuente")},
                      "capitulo_propuesto": cl[o[0]], "nombre": nombres.get(cl[o[0]]), "confianza": round(float(r[o[0]]), 3),
                      "segunda_opcion": cl[o[1]], "margen": round(float(r[o[0]] - r[o[1]]), 3)})
    props.sort(key=lambda p: p["margen"])
    with (AQUI / "_privado" / "propuestas_clasificacion_v2.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(props[0]) + ["capitulo_correcto"])
        w.writeheader()
        for p in props:
            w.writerow({**p, "capitulo_correcto": ""})
    etapa_v2 = collections.Counter(p["capitulo_propuesto"].split(".")[0] for p in props)

    def pct(x):
        return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.1%}"
    L = ["# Clasificador por etapa v2: colegas (vivienda) + EPC (redes) (#196)", "",
         "Generado por `scripts/presupuesto/clasificador_etapas_v2.py`. TF-IDF de caracteres + regresión logística con "
         "rechazo. Sin LLM.", "",
         f"- Oro de colegas: {len(Xo)} APU (vivienda campestre).",
         f"- EPC: **{len(Xe)}** actividades únicas etiquetadas por su capítulo/subcapítulo de la cartilla, mapeado a la "
         f"taxonomía (`MAPEO_EPC` en el script, revisable). Excluidas por ambiguas: {sum(excl.values())} "
         f"({', '.join(f'{k} {v}' for k, v in excl.most_common(4))}).",
         f"- Por capítulo de la taxonomía en EPC: " + ", ".join(f"{k} {v}" for k, v in sorted(collections.Counter(ye).items())), "",
         "| Experimento | n | Exactitud capítulo | Exactitud ETAPA | Macro-F1 | τ | Cobertura | Precisión etapa (aceptadas) |",
         "|---|---|---|---|---|---|---|---|"]
    for nom, m_ in filas:
        L.append(f"| {nom} | {m_['n']} | {pct(m_['exactitud_capitulo'])} | {pct(m_['exactitud_etapa'])} | "
                 f"{m_['macro_f1_capitulo']:.2f} | {m_.get('tau', '—')} | {pct(m_.get('cobertura'))} | "
                 f"{pct(m_.get('precision_etapa_aceptadas'))} |")
    L += ["", f"En B, las actividades de redes (4.3) se predicen como: " +
          ", ".join(f"{k} {v}" for k, v in conf.most_common(5)) + ".", "",
          f"Criterio (fijado antes): B mejora la etapa en EPC frente a A (**{mejora_b:+.1%}**) y C no baja más de 2 "
          f"puntos la etapa en vivienda (**{-caida_c:+.1%}**). Veredicto: "
          f"**{'se adopta v2' if adoptar else 'NO se adopta v2'}**.", "",
          f"Propuestas v2 para las {len(sin)} actividades sin etiqueta de la base, por etapa: " +
          ", ".join(f"{k} {v}" for k, v in sorted(etapa_v2.items())) +
          ". Siguen sin validar en la base: hace falta la muestra etiquetada por una persona "
          "(`_privado/muestra_para_etiquetar.csv`)."]
    INFORME.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
