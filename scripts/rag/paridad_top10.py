"""Paridad top-10 de la búsqueda híbrida local (indice_local) contra los RPC de Postgres, en los 5 corpus.

    python scripts/rag/paridad_top10.py sql [--exacto]           # imprime el SQL (se corre con el MCP, solo lectura)
    python scripts/rag/paridad_top10.py comparar resultado.json  # compara con lo que devolvió Postgres

* El embedding de cada consulta es el de un chunk real (subconsulta en SQL, el mismo vector en local): no se llama a
  ninguna API de embeddings ni se gasta cuota.
* ``--exacto`` apaga los índices (HNSW) en la transacción: Postgres hace la búsqueda semántica exacta, como la local.
  Sin él, se mide contra lo que hoy responde producción (HNSW con ef_search=40, que trunca el pozo semántico a 40).
* Solo viajan ids: el texto de las normas no sale de la base.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
import hashlib  # noqa: E402

import numpy as np  # noqa: E402
from indice_local import COLOMBIA, CORPUS, IndiceLocal, consulta_or_colombia, consulta_or_pais  # noqa: E402

TABLA = {"nsr10": "nsr10_chunks", "ntc": "ntc_chunks", "motor": "motor_chunks", "peru": "peru_e030_chunks",
         "ecuador": "ecuador_nec_se_ds_chunks"}
K = 10

# (id, corpus del embedding, ordinal del chunk en ese corpus, texto, p_norma/p_capitulo, p_motor, rpc)
CONSULTAS = [
    ("c01", "nsr10", 101, "cuantía mínima de refuerzo longitudinal en vigas", None, None, "co"),
    ("c02", "nsr10", 2203, "periodo fundamental aproximado de la estructura Ta", None, None, "co"),
    ("c03", "nsr10", 4507, "deriva máxima permitida entre pisos", None, None, "co"),
    ("c04", "nsr10", 7311, "recubrimiento mínimo del concreto para el acero de refuerzo", None, None, "co"),
    ("c05", "nsr10", 9050, "capacidad portante del suelo y asentamientos admisibles", None, None, "co"),
    ("c06", "nsr10", 555, "coeficiente de disipación de energía R0 pórticos de concreto", "%A.%", None, "co"),
    ("c07", "ntc", 40, "resistencia a la compresión de cilindros de concreto", None, None, "co"),
    ("c08", "ntc", 200, "ensayo de granulometría de agregados", "%NTC%", None, "co"),
    ("c09", "motor", 300, "diseño de pavimento flexible tránsito de diseño", None, "vias", "co"),
    ("c10", "motor", 1500, "dotación neta de agua potable por habitante", None, "aquai", "co"),
    ("c11", "motor", 2500, "estabilidad de taludes factor de seguridad", None, "geopot", "co"),
    ("c12", "motor", 3500, "garantía de cumplimiento del contrato de obra pública", None, "gerencia", "co"),
    ("c13", "motor", 900, "ancho mínimo de calzada y bermas", None, None, "co"),
    ("c14", "ntc", 120, "", None, None, "co"),                                   # solo semántica
    ("c15", "nsr10", 3000, "zzqx inexistentepalabra", None, None, "co"),          # léxica vacía
    ("p01", "peru", 10, "factor de zona sísmica Z", None, None, "peru"),
    ("p02", "peru", 80, "sistemas estructurales y coeficiente básico de reducción", None, None, "peru"),
    ("p03", "peru", 150, "desplazamientos laterales relativos admisibles", "%Capítulo V%", None, "peru"),
    ("p04", "peru", 190, "cimentaciones y presión admisible", None, None, "peru"),
    ("e01", "ecuador", 20, "espectro elástico de diseño en aceleraciones", None, None, "ecuador"),
    ("e02", "ecuador", 150, "factor de importancia de la estructura", None, None, "ecuador"),
    ("e03", "ecuador", 260, "irregularidad en planta y en elevación", None, None, "ecuador"),
    ("e04", "ecuador", 380, "derivas de piso máximas inelásticas", None, None, "ecuador"),
]


def _ancla(idx: IndiceLocal, corpus: str, ordinal: int) -> int:
    c = CORPUS.index(corpus)
    filas = [i for i in range(idx.n) if idx.corpus[i] == c and idx.tiene_emb[i]]
    return filas[ordinal % len(filas)]


def _lit(x) -> str:
    return "null" if x is None else "'" + str(x).replace("'", "''") + "'"


def sql(idx: IndiceLocal, exacto: bool) -> str:
    partes = []
    for qid, corpus, ordn, texto, filtro, motor, rpc in CONSULTAS:
        i = _ancla(idx, corpus, ordn)
        emb = f"(select embedding from public.{TABLA[corpus]} where id::text = {_lit(idx.ids[i])})"
        if rpc == "co":
            fn = (f"public.search_knowledge({emb}, {_lit(texto)}, {_lit(filtro)}, {K}, 60, {_lit(motor)}) "
                  "with ordinality t(chunk_id, norma, seccion, contenido, score, metadata, o)")
        else:
            nombre = "search_knowledge_peru_e030" if rpc == "peru" else "search_knowledge_ecuador_nec_se_ds"
            fn = (f"public.{nombre}({emb}, {_lit(texto)}, {_lit(filtro)}, {K}, 60) "
                  "with ordinality t(chunk_id, capitulo, seccion, contenido, score, o)")
        partes.append(f"select '{qid}' q, (select string_agg(chunk_id || '|' || round(score::numeric, 9), ',' order by o) "
                      f"from {fn}) ids")
    cuerpo = " union all ".join(partes) + " order by 1"
    if not exacto:
        return cuerpo
    return f"set local enable_indexscan = off; set local enable_bitmapscan = off; {cuerpo}"


def sql_comparar(idx: IndiceLocal, exacto: bool) -> str:
    """Como sql(), pero con los resultados locales incrustados: Postgres devuelve solo la comparación por consulta."""
    loc = locales(idx)
    base = sql(idx, False)
    valores = ",".join(f"('{q}', {_lit(','.join(i for i, _ in v))}, {_lit(','.join(f'{x:.9f}' for _, x in v))})"
                       for q, v in loc.items())
    cuerpo = (f"with pg as ({base}), loc(q, ids, sc) as (values {valores}), "
              "p as (select q, (select string_agg(split_part(x, '|', 1), ',' order by n) from unnest(string_to_array(pg.ids, ',')) "
              "with ordinality u(x, n)) ids, (select array_agg(split_part(x, '|', 2)::numeric order by n) from "
              "unnest(string_to_array(pg.ids, ',')) with ordinality u(x, n)) sc from pg) "
              "select loc.q, p.ids = loc.ids orden_identico, "
              "(select bool_and(abs(a - b) < 1e-8) and count(*) = cardinality(p.sc) from unnest(p.sc, "
              "string_to_array(loc.sc, ',')::numeric[]) z(a, b)) puntajes_identicos, "
              "(select count(*) from (select unnest(string_to_array(p.ids, ',')) intersect "
              "select unnest(string_to_array(loc.ids, ','))) w) comunes "
              "from loc join p using (q) order by 1")
    return ("set local enable_indexscan = off; set local enable_bitmapscan = off; " if exacto else "") + cuerpo


_FUENTES = (
    "f as materialized (select src, id, norma, motor, to_tsvector('spanish', txt) tv from ("
    "select 'co' src, id::text id, capitulo norma, texto txt, null::text motor from public.nsr10_chunks union all "
    "select 'co', id::text, norma, contenido, null from public.ntc_chunks union all "
    "select 'co', id::text, norma_ref, contenido, motor from public.motor_chunks union all "
    "select 'peru', id::text, capitulo, texto, null from public.peru_e030_chunks union all "
    "select 'ecuador', id::text, capitulo, texto, null from public.ecuador_nec_se_ds_chunks) x)")
_ENT = "(r::float8 * 1e10)::bigint"


def _huellas_lexicas_locales(idx: IndiceLocal, rpc, texto, filtro, motor) -> tuple[int, str, str]:
    """(n coincidencias, md5 de 'id:ts_rank' de los que entran al pozo sin ambigüedad, md5 de los ts_rank del pozo).
    Es la comparación del pozo léxico que no depende de cómo cada lado ordena los empates de ts_rank."""
    if rpc == "co":
        grupos, mascara, pozo = consulta_or_colombia(texto), idx._filtro(COLOMBIA, filtro, motor), 300
    else:
        grupos, mascara, pozo = consulta_or_pais(texto), idx._filtro((CORPUS.index(rpc),), filtro, None), K * 3
    docs, res = idx._puntajes_lexicos(grupos, mascara)
    ent = lambda x: round(float(np.float32(x)) * 1e10)  # noqa: E731  # = (r::float8 * 1e10)::bigint en Postgres
    valores = sorted((np.float32(x) for x in res), reverse=True)[:pozo]
    corte = valores[-1] if len(res) >= pozo else None
    seguros = sorted((f"{idx.ids[d]}:{ent(r)}" for d, r in zip(docs, res) if corte is None or r > corte),
                     key=lambda x: x.encode("utf-8"))
    md5 = lambda t: hashlib.md5(t.encode("utf-8")).hexdigest()  # noqa: E731
    return len(docs), md5(",".join(seguros)), md5(",".join(str(ent(v)) for v in valores))


def sql_lexico(idx: IndiceLocal, solo: set[str] | None = None) -> str:
    """Postgres calcula las mismas huellas del pozo léxico (consulta, filtro y ts_rank idénticos a los RPC) y las
    compara con las locales, que van incrustadas en VALUES."""
    filas = []
    for qid, corpus, ordn, texto, filtro, motor, rpc in CONSULTAS:
        if solo and qid not in solo:
            continue
        n, ha, hv = _huellas_lexicas_locales(idx, rpc, texto, filtro, motor)
        pozo = 300 if rpc == "co" else K * 3
        filas.append(f"({_lit(qid)}, {_lit(rpc)}, {_lit(texto)}, {_lit(filtro)}, {_lit(motor)}, {pozo}, {n}, "
                     f"{_lit(ha)}, {_lit(hv)})")
    return (f"with {_FUENTES}, c(q, rpc, texto, filtro, motor, pozo, n, ha, hv) as (values "
            + ", ".join(filas).replace("null, null, ", "null::text, null::text, ", 1) + ") "
            "select c.q, x.n = c.n mismo_n, md5(coalesce(x.seg, '')) = c.ha mismos_seguros, "
            "md5(coalesce(x.vals, '')) = c.hv mismos_ts_rank from c cross join lateral ("
            "with qq as (select case when c.rpc = 'co' then (select to_tsquery('spanish', string_agg(lexeme, ' | ')) "
            "from unnest(to_tsvector('spanish', c.texto))) else regexp_replace(plainto_tsquery('spanish', c.texto)::text, "
            "' & ', ' | ', 'g')::tsquery end v), "
            "z as (select s.id, ts_rank(s.tv, qq.v) r from f s, qq where s.src = c.rpc and qq.v is not null "
            "and (c.filtro is null or s.norma ilike '%' || c.filtro || '%') and (c.motor is null or s.motor = c.motor) "
            "and s.tv @@ qq.v), top as (select r from z order by r desc limit c.pozo), "
            "t as (select case when (select count(*) from z) >= c.pozo then (select min(r) from top) end v) "
            f"select (select count(*) from z) n, (select string_agg(id || ':' || {_ENT}, ',' order by "
            f"(id || ':' || {_ENT}) collate \"C\") from z where (select v from t) is null or r > (select v from t)) seg, "
            f"(select string_agg({_ENT}::text, ',' order by r desc) from top) vals) x order by 1")


def locales(idx: IndiceLocal) -> dict[str, list[tuple[str, float]]]:
    out = {}
    for qid, corpus, ordn, texto, filtro, motor, rpc in CONSULTAS:
        q = idx.emb[_ancla(idx, corpus, ordn)]
        if rpc == "co":
            filas = idx.search_knowledge(q, texto, filtro, K, 60, motor)
        else:
            filas = idx.search_pais(rpc, q, texto, filtro, K, 60)
        out[qid] = [(f.chunk_id, round(f.score, 9)) for f in filas]
    return out


def comparar(loc: dict[str, list[tuple[str, float]]], pg: dict[str, list[tuple[str, float]]]) -> dict:
    """orden_identico: mismos ids en el mismo orden. puntajes_identicos: el vector de puntajes RRF posición a posición
    es el mismo (las diferencias de ids son entonces solo empates, que Postgres resuelve en orden arbitrario: sus RPC
    ordenan por score sin desempate y row_number() sobre ts_rank empatado tampoco es determinista)."""
    filas = []
    for qid, l in loc.items():
        p = pg.get(qid) or []
        ids_l, ids_p = [i for i, _ in l], [i for i, _ in p]
        sc_l, sc_p = [s for _, s in l], [s for _, s in p]
        filas.append({"q": qid, "orden_identico": ids_l == ids_p,
                      "puntajes_identicos": len(sc_l) == len(sc_p) and all(abs(a - b) < 1e-8 for a, b in zip(sc_l, sc_p)),
                      "solape_top10": round(len(set(ids_l) & set(ids_p)) / max(len(ids_l), len(ids_p), 1), 3)})
    n = max(len(filas), 1)
    return {"consultas": len(filas), "orden_identico": sum(f["orden_identico"] for f in filas),
            "puntajes_identicos": sum(f["puntajes_identicos"] for f in filas),
            "solape_medio": round(sum(f["solape_top10"] for f in filas) / n, 4), "detalle": filas}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["sql", "sql-comparar", "sql-lexico", "comparar"])
    ap.add_argument("resultado", nargs="?", type=Path, help="JSON con [{q, ids}] devuelto por Postgres")
    ap.add_argument("--exacto", action="store_true")
    ap.add_argument("--consultas", help="solo estas consultas, p. ej. c01,c02")
    ap.add_argument("--indice", type=Path, default=RAIZ / "apps" / "api" / "datos_indice" / "indice_rag.npz")
    a = ap.parse_args()
    idx = IndiceLocal.cargar(a.indice)
    if a.modo == "sql":
        print(sql(idx, a.exacto))
        return
    if a.modo == "sql-lexico":
        print(sql_lexico(idx, set(a.consultas.split(",")) if a.consultas else None))
        return
    if a.modo == "sql-comparar":
        print(sql_comparar(idx, a.exacto))
        return
    crudo = json.loads(a.resultado.read_text(encoding="utf-8"))
    pg = {r["q"]: [(x.rsplit("|", 1)[0], float(x.rsplit("|", 1)[1])) for x in r["ids"].split(",")] if r.get("ids") else []
          for r in crudo}
    print(json.dumps(comparar(locales(idx), pg), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
