"""Geografia de los precios de construccion en Colombia con INVIAS 2026-1 (issue #95/#98/#99).

POR QUE INVIAS: es la unica parte de nuestra base de precios con fecha verificable (periodo 2026-1) y
cobertura de las 140 provincias, 663 insumos y 526 actividades con su costo de transporte. El resto
del catalogo no tiene fecha de precio (#99) y no sirve para comparar regiones.

Preguntas (declaradas antes de correr):
 P1. ¿Que regiones naturales pagan prima en cementantes/bituminosos, acero y agregados frente a la
     mediana nacional del mismo insumo? (indice provincial = media geometrica de precio/mediana)
 P2. ¿Que categorias son mas inestables entre provincias? (mediana del coeficiente de variacion)
 P3. Consistencia interna: ¿la prima de materiales pesados se asocia con la participacion del
     transporte en el costo directo? (si no, el indice mide otra cosa)
 P4. EXPLORATORIO: ¿la prima crece con la distancia al puerto mas cercano / a Bogota? La ubicacion de
     cada provincia se aproxima con la capital de su departamento (DIVIPOLA, codigo ...001): es una
     aproximacion gruesa y se declara como tal.

Unidad: provincia (n=140). IC95 % por remuestreo de provincias. Solo descriptivo/exploratorio:
NO es un modelo de costos ni una recomendacion de inversion. Precios de REFERENCIA de INVIAS, no
cotizaciones de mercado.
Salida: scripts/precios/informe_geografia_precios.md
"""
from __future__ import annotations

import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from dotenv import dotenv_values
from scipy.stats import spearmanr
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
import divipola  # noqa: E402

CACHE = AQUI / "_cache"
MIN_PROV = 120
N_BOOT = 5000
RNG = np.random.default_rng(20261106)
CATS = {"CEMENTANTES Y BITUMINOSOS": "cementantes_bituminosos", "ACERO, ALAMBRES, SOLDADURA Y MALLAS METALICAS": "acero",
        "AGREGADOS": "agregados"}
LIN: list[str] = []


def out(t=""):
    print(t)
    LIN.append(t)


def tabla(cab, filas):
    out("| " + " | ".join(cab) + " |")
    out("|" + "|".join("---" for _ in cab) + "|")
    for f in filas:
        out("| " + " | ".join(str(x) for x in f) + " |")
    out()


def paginar(sb, tabla_, cols):
    f = CACHE / f"{tabla_}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    filas, ini = [], 0
    while True:
        pag = sb.table(tabla_).select(cols).range(ini, ini + 999).execute().data or []
        filas += pag
        if len(pag) < 1000:
            break
        ini += 1000
    CACHE.mkdir(exist_ok=True)
    f.write_text(json.dumps(filas), encoding="utf-8")
    return filas


def ic_mediana(v, bloques=None):
    v = np.asarray(v, float)
    bs = [np.median(v[RNG.integers(0, len(v), len(v))]) for _ in range(N_BOOT)]
    return np.percentile(bs, [2.5, 97.5])


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def main() -> None:
    env = dotenv_values(RAIZ / "apps/api/.env")
    sb = create_client(env["SUPABASE_URL"], env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_KEY"])
    prov = {p["codigo"]: p for p in paginar(sb, "invias_provincias", "codigo,codigo_departamento,departamento,provincia,region_natural")}
    ins = {i["codigo"]: i for i in paginar(sb, "invias_insumos", "codigo,descripcion,unidad,tipo_insumo,categoria")}
    pre = paginar(sb, "invias_insumos_precios", "insumo_codigo,provincia_codigo,periodo,precio")
    cos = paginar(sb, "invias_actividad_costos", "numeral,provincia_codigo,costo_transporte,costo_directo_total")
    out("# Geografia de los precios de construccion (INVIAS 2026-1)\n")
    out("Precios de REFERENCIA (analisis de precios unitarios regionalizados de INVIAS), periodo 2026-1; no son cotizaciones de mercado. "
        "Unidad de analisis: provincia. Ver el docstring del script para las preguntas y limites.\n")
    out(f"## Datos\n- Provincias: {len(prov)}; insumos con precio: {len({p['insumo_codigo'] for p in pre})}; filas de precio: {len(pre)} (periodo {sorted({p['periodo'] for p in pre})}).")
    nulos = sum(1 for p in pre if p["precio"] is None or p["precio"] <= 0)
    out(f"- Precios nulos o no positivos: {nulos}.\n")

    # ---- precios por insumo
    por_ins = defaultdict(dict)
    for p in pre:
        if p["precio"] and p["precio"] > 0:
            por_ins[p["insumo_codigo"]][p["provincia_codigo"]] = float(p["precio"])
    ratio = defaultdict(dict)          # insumo -> prov -> precio/mediana
    cv = {}
    for k, d in por_ins.items():
        if len(d) < MIN_PROV:
            continue
        v = np.array(list(d.values()))
        med = np.median(v)
        for pr, x in d.items():
            ratio[k][pr] = x / med
        cv[k] = v.std(ddof=1) / v.mean()

    # ---- P1: indice provincial por categoria
    idx = {nom: {} for nom in CATS.values()}
    nitems = {}
    for cat, nom in CATS.items():
        items = [k for k in ratio if ins.get(k, {}).get("categoria") == cat]
        nitems[nom] = len(items)
        for pr in prov:
            vals = [math.log(ratio[k][pr]) for k in items if pr in ratio[k]]
            if len(vals) >= max(3, 0.7 * len(items)):
                idx[nom][pr] = math.exp(np.mean(vals))
    out("## P1. Prima por region natural (indice provincial; 1,00 = mediana nacional del mismo insumo)")
    regiones = sorted({p["region_natural"] for p in prov.values()})
    cab = ["region (n provincias)"] + [f"{n} ({nitems[n]} insumos)" for n in CATS.values()]
    filas = []
    for r in regiones:
        fila = [f"{r} ({sum(1 for p in prov.values() if p['region_natural'] == r)})"]
        for nom in CATS.values():
            v = [idx[nom][c] for c, p in prov.items() if p["region_natural"] == r and c in idx[nom]]
            if len(v) >= 3:
                lo, hi = ic_mediana(v)
                fila.append(f"{np.median(v):.2f} [{lo:.2f}, {hi:.2f}]")
            else:
                fila.append("—")
        filas.append(fila)
    tabla(cab, filas)
    out("Mediana de los indices provinciales de la region con IC95 % (remuestreo de provincias). >1 = mas caro que la mediana nacional.\n")

    # ---- P2: inestabilidad
    out("## P2. Inestabilidad entre provincias (coeficiente de variacion por insumo; insumos con precio en >= 120 provincias)")
    cvc = defaultdict(list)
    for k, c in cv.items():
        cvc[ins.get(k, {}).get("categoria") or f"({ins.get(k, {}).get('tipo_insumo')})"].append((c, ins[k]["descripcion"][:48]))
    filas = []
    for cat, l in sorted(cvc.items(), key=lambda kv: -np.median([x[0] for x in kv[1]])):
        if len(l) >= 5:
            v = [x[0] for x in l]
            filas.append([cat[:44], len(l), f"{np.median(v):.2f}", f"{np.percentile(v, 90):.2f}"])
    tabla(["categoria", "insumos", "CV mediano", "CV p90"], filas[:12])

    # ---- transporte
    sh = defaultdict(list)
    for c in cos:
        if c["costo_directo_total"] and c["costo_directo_total"] > 0 and c["costo_transporte"] is not None:
            sh[c["provincia_codigo"]].append(c["costo_transporte"] / c["costo_directo_total"])
    tp = {pr: float(np.mean(v)) for pr, v in sh.items() if len(v) >= 100}
    out("## Participacion del transporte en el costo directo (media sobre ~526 actividades)")
    filas = []
    for r in regiones:
        v = [tp[c] for c, p in prov.items() if p["region_natural"] == r and c in tp]
        if len(v) >= 3:
            lo, hi = ic_mediana(v)
            filas.append([r, len(v), f"{100 * np.median(v):.1f} % [{100 * lo:.1f}, {100 * hi:.1f}]"])
    tabla(["region", "provincias", "transporte / costo directo (mediana, IC95 %)"], filas)

    # ---- P3 consistencia
    out("## P3. Consistencia interna: ¿la prima de materiales pesados se asocia con el peso del transporte?")
    heavy = {}
    for c in prov:
        v = [idx[n][c] for n in CATS.values() if c in idx[n]]
        if len(v) == len(CATS):
            heavy[c] = math.exp(np.mean(np.log(v)))
    comun = [c for c in heavy if c in tp]
    h = np.array([heavy[c] for c in comun]); t = np.array([tp[c] for c in comun])
    reg = np.array([prov[c]["region_natural"] for c in comun])

    def rho_ic(x, y, bl):
        r0 = spearmanr(x, y)[0]
        et = np.unique(bl); bs = []
        for _ in range(N_BOOT):
            ix = np.concatenate([np.where(bl == b)[0] for b in RNG.choice(et, len(et), replace=True)])
            if np.ptp(x[ix]) > 0 and np.ptp(y[ix]) > 0:
                bs.append(spearmanr(x[ix], y[ix])[0])
        return r0, *np.percentile(bs, [2.5, 97.5])

    r0, lo, hi = rho_ic(h, t, reg)
    out(f"rho de Spearman (n={len(comun)} provincias) = **{r0:.2f}**, IC95 % por regiones [{lo:.2f}, {hi:.2f}]. "
        f"{'Coherente: el indice mide algo ligado al costo de llevar material.' if lo > 0 else 'El IC incluye 0: el indice de prima y el peso del transporte no se asocian de forma robusta.'}\n")

    # ---- P4 exploratorio: distancia
    out("## P4 (exploratorio). Prima vs distancia (ubicacion = capital del departamento; aproximacion gruesa)")
    divipola._cargar_cache()

    def pos(cod):
        r = divipola.resolver_por_codigo(cod)
        return (r["latitud"], r["longitud"]) if r and r.get("latitud") else None

    puertos = {n: pos(c) for n, c in {"Cartagena": "13001", "Barranquilla": "08001", "Santa Marta": "47001", "Buenaventura": "76109"}.items()}
    bog = pos("11001")
    d_p, d_b, hh, bl2 = [], [], [], []
    for c in heavy:
        cap = pos(f"{prov[c]['codigo_departamento']:0>2}001")
        if cap and all(puertos.values()) and bog:
            d_p.append(min(km(cap, v) for v in puertos.values())); d_b.append(km(cap, bog))
            hh.append(heavy[c]); bl2.append(prov[c]["region_natural"])
    hh, d_p, d_b, bl2 = map(np.array, (hh, d_p, d_b, bl2))
    for nom, d in [("distancia al puerto mas cercano (Cartagena, Barranquilla, Santa Marta, Buenaventura)", d_p), ("distancia a Bogota", d_b)]:
        r0, lo, hi = rho_ic(d, hh, bl2)
        out(f"- {nom}: rho = {r0:.2f}, IC95 % por regiones [{lo:.2f}, {hi:.2f}] (n={len(hh)})")
    out("\nLas distancias usan la capital departamental, no la provincia; los puertos elegidos son una decision del analista; "
        "una correlacion no establece que la distancia cause la prima (hay confusion con relieve, vias y volumen).\n")

    # ---- puntos frágiles
    out("## Puntos fragiles (descriptivo)")
    orden = sorted(heavy, key=lambda c: -heavy[c])[:8]
    tabla(["provincia", "departamento", "region", "prima materiales pesados", "transporte / costo directo"],
          [[prov[c]["provincia"][:30], prov[c]["departamento"], prov[c]["region_natural"], f"{heavy[c]:.2f}",
            f"{100 * tp[c]:.1f} %" if c in tp else "—"] for c in orden])
    out("Limites: precios de referencia, no de mercado; un solo periodo (2026-1), por eso no hay volatilidad temporal; "
        "provincias ≠ mercados; el indice depende de los insumos que tienen precio en >= 120 provincias.")
    (AQUI / "informe_geografia_precios.md").write_text("\n".join(LIN), encoding="utf-8")


if __name__ == "__main__":
    main()
