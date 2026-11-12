"""
Cruces e hipótesis sobre los precios de referencia de EPC 2021–2026 (Cundinamarca). Supabase solo lectura.

Entrada: scripts/ingesta/epc/salida/epc_precios_largo.csv (de extraer_cartillas_epc.py).
Salida:  docs/presupuesto/EPC_HIPOTESIS.md  y  scripts/ingesta/epc/salida/*.csv (tablas intermedias)

Hipótesis (formuladas ANTES de mirar los resultados; se reportan aunque no se confirmen):
  H1 Tiempo: el precio de una misma actividad sube año a año; la variación difiere por capítulo.
     Medida: índice encadenado = mediana, por capítulo, de precio(t)/precio(t-1) de la misma actividad (descripción +
     unidad) en el mismo municipio.
  H2 Espacio: dentro de una provincia y año, las actividades intensivas en materiales y transporte varían más entre
     municipios que las de mano de obra. Medida: CV entre municipios por actividad; factor municipal = mediana de
     precio/mediana-provincial sobre todas las actividades.
  H3 Distancia: el factor municipal crece con la distancia a Bogotá. Medida: Spearman entre factor y distancia
     (coordenadas de sgc_amenaza_sismica_municipios), con IC bootstrap.
  H4 Regiones: para actividades equivalentes, Cundinamarca (EPC) y Atlántico (apu_precios_referencia) difieren.
     Emparejamiento conservador: misma unidad y similitud TF-IDF de caracteres ≥ 0,80; razón de precios por capítulo.
  H5 Clasificador (#196): fuera de dominio, ¿la etapa que predice el clasificador coincide con la que implica el
     capítulo de EPC? Tabla de contingencia sobre actividades únicas.
"""
from __future__ import annotations

import collections
import csv
import math
import os
import re
import statistics
import sys
import unicodedata
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
ENTRADA = AQUI / "salida" / "epc_precios_largo.csv"
INFORME = RAIZ / "docs" / "presupuesto" / "EPC_HIPOTESIS.md"
BOGOTA = (4.6097, -74.0817)
rng = np.random.default_rng(0)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def leer() -> list[dict]:
    with ENTRADA.open(encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    for f in filas:
        f["anio"] = int(f["anio"])
        f["precio"] = float(f["precio"])
        f["clave"] = (norm(f["actividad"]), norm(f["unidad"]))
        f["muni"] = norm(f["municipio"])
    return [f for f in filas if f["precio"] > 0]


def haversine(a, b) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def spearman_ic(x, y, n_boot=2000):
    from scipy.stats import spearmanr
    x, y = np.asarray(x), np.asarray(y)
    r = spearmanr(x, y).statistic
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        bs.append(spearmanr(x[i], y[i]).statistic)
    lo, hi = np.nanquantile(bs, [0.025, 0.975])
    return float(r), float(lo), float(hi)


def main() -> None:
    filas = leer()
    L = ["# Precios de referencia de EPC (Cundinamarca, 2021–2026): cruces e hipótesis", "",
         "Generado por `scripts/ingesta/epc/analizar_epc.py`. Hipótesis formuladas antes de ver los resultados "
         "(docstring del script); se reportan aunque no se confirmen.", "",
         f"Datos: {len(filas):,} precios (actividad × municipio × año), {len({f['clave'] for f in filas}):,} actividades, "
         f"{len({f['muni'] for f in filas})} municipios, años {sorted({f['anio'] for f in filas})}.", ""]

    # ── H1: índice anual encadenado por capítulo ───────────────────────────────────────────────
    idx = {(f["clave"], f["muni"], f["anio"]): f["precio"] for f in filas}
    cap_de = {f["clave"]: norm(f["capitulo"] or "SIN CAPITULO")[:40] for f in filas}
    anios = sorted({f["anio"] for f in filas})
    razones = collections.defaultdict(list)       # (capitulo, año) -> razones
    global_r = collections.defaultdict(list)
    for (clave, muni, a), p in idx.items():
        if a - 1 in anios and (clave, muni, a - 1) in idx:
            r = p / idx[(clave, muni, a - 1)]
            if 0.2 < r < 5:
                razones[(cap_de[clave], a)].append(r)
                global_r[a].append(r)
    L += ["## H1. Variación anual (misma actividad, mismo municipio)", "",
          "| Año | Pares | Mediana precio(t)/precio(t−1) | P10–P90 | Actividades que bajaron |", "|---|---|---|---|---|"]
    for a in anios[1:]:
        v = global_r.get(a, [])
        if v:
            L.append(f"| {a} | {len(v):,} | {statistics.median(v):.3f} | {np.quantile(v, .1):.3f}–{np.quantile(v, .9):.3f} | "
                     f"{sum(x < 1 for x in v) / len(v):.0%} |")
    acum = 1.0
    for a in anios[1:]:
        if global_r.get(a):
            acum *= statistics.median(global_r[a])
    L += ["", f"Índice encadenado {anios[0]}→{anios[-1]}: **×{acum:.2f}** (mediana de razones de la misma actividad).", ""]
    caps_top = collections.Counter(c for (c, _), v in razones.items() for _ in v).most_common(12)
    L += ["Por capítulo (mediana de la razón anual, años disponibles):", "", "| Capítulo | " +
          " | ".join(str(a) for a in anios[1:]) + " |", "|---|" + "---|" * len(anios[1:])]
    for c, _ in caps_top:
        celdas = [f"{statistics.median(razones[(c, a)]):.3f}" if razones.get((c, a)) else "—" for a in anios[1:]]
        L.append(f"| {c} | " + " | ".join(celdas) + " |")
    # Saltos grandes (posible cambio de definición, no inflación)
    saltos = collections.Counter()
    ejemplos = {}
    for (clave, muni, a), p in idx.items():
        if (clave, muni, a - 1) in idx:
            r = p / idx[(clave, muni, a - 1)]
            if r >= 2 or r <= 0.5:
                saltos[a] += 1
                ejemplos.setdefault(a, (clave[0][:60], clave[1], round(idx[(clave, muni, a - 1)]), round(p)))
    L += ["", "Saltos ×2 o más (o caídas a la mitad) de un año al siguiente, que sugieren cambio de especificación o "
          "de alcance más que inflación: " + ", ".join(f"{a}: {n:,}" for a, n in sorted(saltos.items())) + ".",
          "Ejemplos: " + "; ".join(f"{a}: {e[0]} [{e[1]}] {e[2]:,}→{e[3]:,}" for a, e in sorted(ejemplos.items())), ""]

    # ── H2: dispersión entre municipios y factor municipal ─────────────────────────────────────
    ult = anios[-1]
    por_prov_act = collections.defaultdict(dict)
    for f in filas:
        if f["anio"] == ult:
            por_prov_act[(f["provincia"], f["clave"])][f["muni"]] = f["precio"]
    cvs = collections.defaultdict(list)
    factores = collections.defaultdict(list)
    for (prov, clave), d in por_prov_act.items():
        if len(d) >= 3:
            v = list(d.values())
            med = statistics.median(v)
            cvs[cap_de[clave]].append(statistics.pstdev(v) / statistics.mean(v))
            for m, p in d.items():
                factores[(prov, m)].append(p / med)
    L += [f"## H2. Variación entre municipios de una misma provincia ({ult})", "",
          "| Capítulo | Actividades | Mediana del CV entre municipios | Actividades con CV > 5 % |", "|---|---|---|---|"]
    for c, v in sorted(cvs.items(), key=lambda kv: -statistics.median(kv[1]))[:14]:
        L.append(f"| {c} | {len(v)} | {statistics.median(v):.1%} | {sum(x > .05 for x in v) / len(v):.0%} |")
    fac = {k: statistics.median(v) for k, v in factores.items() if len(v) >= 20}
    with (AQUI / "salida" / f"factor_municipal_{ult}.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["provincia", "municipio", "factor_mediano", "n_actividades"])
        for (prov, m), v in sorted(fac.items(), key=lambda kv: -kv[1]):
            w.writerow([prov, m, round(v, 4), len(factores[(prov, m)])])
    orden = sorted(fac.items(), key=lambda kv: -kv[1])
    L += ["", f"Factor municipal (mediana de precio / mediana de su provincia, {len(fac)} municipios): "
          f"más caros {', '.join(f'{m} ({v:.3f})' for (_, m), v in orden[:5])}; "
          f"más baratos {', '.join(f'{m} ({v:.3f})' for (_, m), v in orden[-5:])}.", ""]

    # ── H3: factor frente a distancia a Bogotá (coordenadas del SGC) ───────────────────────────
    try:
        from dotenv import load_dotenv
        from supabase import create_client
        load_dotenv(RAIZ / "apps" / "api" / ".env")
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
        coords = {}
        for r in sb.table("sgc_amenaza_sismica_municipios").select("*").ilike("departamento", "%cundinamarca%").execute().data:
            if r.get("latitud") and r.get("longitud"):
                coords[norm(r["municipio"])] = (float(r["latitud"]), float(r["longitud"]))
        pares = [(haversine(coords[m], BOGOTA), v) for (_, m), v in fac.items() if m in coords]
        sin = [m for (_, m) in fac if m not in coords]
        if len(pares) >= 10:
            r, lo, hi = spearman_ic([p[0] for p in pares], [p[1] for p in pares])
            L += ["## H3. Factor municipal frente a distancia a Bogotá", "",
                  f"Municipios con coordenadas: {len(pares)} de {len(fac)} (sin coordenadas: {', '.join(sin[:8]) or '—'}).",
                  f"Spearman ρ = **{r:.2f}** (IC95 bootstrap {lo:.2f} a {hi:.2f}). "
                  + ("Se confirma una relación positiva." if lo > 0 else
                     "Se confirma una relación negativa." if hi < 0 else "No se confirma: el IC incluye 0."), ""]
    except Exception as e:  # noqa: BLE001
        L += ["## H3. Factor municipal frente a distancia a Bogotá", "", f"No se pudo calcular: {type(e).__name__}.", ""]

    # ── H4: Cundinamarca (EPC) frente a Atlántico (base) ──────────────────────────────────────
    try:
        sys.path.insert(0, str(RAIZ / "scripts" / "presupuesto"))
        import cobertura_etapas as cob
        from sklearn.feature_extraction.text import TfidfVectorizer
        base = [b for b in cob.leer_precios() if b["tipo_fuente"] not in cob.INSUMOS_SUELTOS
                and b["actividad"] and b["precio_todo_costo"]]
        epc_ult = {}
        for f in filas:
            if f["anio"] == ult:
                epc_ult.setdefault(f["clave"], []).append(f["precio"])
        epc_k = list(epc_ult)
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        M = vec.fit_transform([k[0] for k in epc_k] + [norm(b["actividad"]) for b in base])
        A, B = M[:len(epc_k)], M[len(epc_k):]
        S = (A @ B.T).tocsr()
        pares4 = []
        for i, k in enumerate(epc_k):
            fila = S.getrow(i)
            if fila.nnz == 0:
                continue
            j = int(fila.indices[fila.data.argmax()])
            sim = float(fila.data.max())
            b = base[j]
            if sim >= 0.80 and norm(b["unidad"] or "") == k[1]:
                pares4.append((cap_de[k], statistics.median(epc_ult[k]) / float(b["precio_todo_costo"]), sim,
                               k[0][:50], (b["actividad"] or "")[:50], b["region"]))
        rz = [p[1] for p in pares4]
        L += ["## H4. Cundinamarca (EPC) frente a Atlántico (base de StructAI)", "",
              f"Pares con misma unidad y similitud ≥ 0,80: **{len(pares4)}**."]
        if rz:
            L += [f"Mediana de precio EPC {ult} / precio base: **{statistics.median(rz):.2f}** "
                  f"(P25–P75 {np.quantile(rz, .25):.2f}–{np.quantile(rz, .75):.2f}). Ojo: la base mezcla años "
                  "(contratos 2016–2019 ajustados por IPC, catálogos recientes); la razón no es solo regional.", "",
                  "Ejemplos: " + "; ".join(f"{p[3]} ↔ {p[4]} ({p[5]}): ×{p[1]:.2f}" for p in sorted(pares4, key=lambda p: -p[2])[:5]), ""]
        with (AQUI / "salida" / "pares_epc_base.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["capitulo_epc", "razon_epc_base", "similitud", "actividad_epc", "actividad_base", "region_base"])
            w.writerows(pares4)
    except Exception as e:  # noqa: BLE001
        L += ["## H4. Cundinamarca (EPC) frente a Atlántico", "", f"No se pudo calcular: {type(e).__name__}: {e}", ""]

    # ── H5: clasificador fuera de dominio contra los capítulos de EPC ────────────────────────
    try:
        import json
        sys.path.insert(0, str(RAIZ / "scripts" / "presupuesto"))
        import clasificador_etapas as ce
        Xo, yo, _ = ce.cargar_oro()
        m = ce.Modelo("tfidf").fit(Xo, yo)
        claves = sorted({f["clave"] for f in filas})
        P, cl = m.proba([f"{c[0].lower()} [{c[1].lower()}]" for c in claves])
        tab = collections.Counter()
        for c, r in zip(claves, P):
            tab[(cap_de[c][:28], cl[int(r.argmax())].split(".")[0])] += 1
        caps_epc = [c for c, _ in collections.Counter(cap_de[c][:28] for c in claves).most_common(14)]
        L += ["## H5. Clasificador por etapa (#196) sobre las actividades de EPC (fuera de dominio)", "",
              "Filas: capítulo según EPC. Columnas: etapa predicha (0 transversales, 1 obra negra, 2 obra gris, 3 obra "
              "blanca, 4 fase final). En obras de acueducto y alcantarillado lo esperado es la etapa 4 (redes externas) "
              "o la 1 (excavación, concretos); mucho 2 o 3 indica confusión del modelo entrenado con vivienda.", "",
              "| Capítulo EPC | 0 | 1 | 2 | 3 | 4 |", "|---|---|---|---|---|---|"]
        for c in caps_epc:
            L.append(f"| {c} | " + " | ".join(str(tab.get((c, e), 0)) for e in "01234") + " |")
        L.append("")
    except Exception as e:  # noqa: BLE001
        L += ["## H5. Clasificador fuera de dominio", "", f"No se pudo calcular: {type(e).__name__}: {e}", ""]

    INFORME.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
