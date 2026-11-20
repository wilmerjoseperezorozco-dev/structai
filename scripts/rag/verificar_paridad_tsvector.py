"""Paridad del analizador local (indice_local.conteos_tsvector) con to_tsvector('spanish') de Postgres, corpus completo.

    python scripts/rag/verificar_paridad_tsvector.py nsr10            # imprime el SQL de comparación por bloques
    python scripts/rag/verificar_paridad_tsvector.py nsr10 --bloque 17 # SQL que lista los ids distintos de ese bloque

El SQL lleva las huellas locales (md5 por bloque de ids) y Postgres devuelve solo los bloques que difieren y cuántos
documentos tiene cada uno: el texto de las normas no sale de la base. Se corre con el MCP de Supabase (solo lectura).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
from indice_local import CORPUS, IndiceLocal, huella_tsvector  # noqa: E402

TABLA = {"nsr10": ("nsr10_chunks", "texto"), "ntc": ("ntc_chunks", "contenido"), "motor": ("motor_chunks", "contenido"),
         "peru": ("peru_e030_chunks", "texto"), "ecuador": ("ecuador_nec_se_ds_chunks", "texto")}
BLOQUES = 64

_HUELLA_PG = ("coalesce((select md5(string_agg(lexeme || ':' || array_length(positions, 1), ' ' order by lexeme collate \"C\")) "
              "from unnest(to_tsvector('spanish', {col}))), '')")


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def bloques_locales(idx: IndiceLocal, corpus: str) -> dict[int, list[tuple[str, str]]]:
    c = CORPUS.index(corpus)
    out = defaultdict(list)
    for i in range(idx.n):
        if idx.corpus[i] == c:
            mid = _md5(idx.ids[i])
            out[int(mid[:2], 16) % BLOQUES].append((mid, huella_tsvector(idx.contenidos[i])))
    return out


def sql_bloques(idx, corpus) -> str:
    tabla, col = TABLA[corpus]
    loc = bloques_locales(idx, corpus)
    valores = ",".join(f"({b},'{_md5(','.join(m + ':' + h for m, h in sorted(v)))}',{len(v)})" for b, v in sorted(loc.items()))
    return (f"with h as (select md5(id::text) mid, {_HUELLA_PG.format(col=col)} hv from public.{tabla}),\n"
            f"pg as (select get_byte(decode(mid,'hex'),0) % {BLOQUES} b, md5(string_agg(mid || ':' || hv, ',' order by mid)) h, count(*) n from h group by 1),\n"
            f"loc(b,h,n) as (values {valores})\n"
            "select coalesce(pg.b, loc.b) bloque, pg.n n_pg, loc.n n_local from pg full join loc using (b) "
            "where pg.h is distinct from loc.h order by 1")


def sql_bloque(idx, corpus, bloque) -> str:
    tabla, col = TABLA[corpus]
    v = sorted(bloques_locales(idx, corpus)[bloque])
    valores = ",".join(f"('{m}','{h}')" for m, h in v)
    return (f"with h as (select id::text id, md5(id::text) mid, {_HUELLA_PG.format(col=col)} hv from public.{tabla}),\n"
            f"loc(mid,hv) as (values {valores})\n"
            f"select h.id from h join loc using (mid) where get_byte(decode(h.mid,'hex'),0) % {BLOQUES} = {bloque} "
            "and h.hv <> loc.hv order by 1")


def sql_docs(idx, corpus, bloques=None) -> str:
    """Comparación por documento de todo el corpus (id md5 de 7 hex, huella de 6 hex): devuelve conteos y los ids que
    difieren. Más pesado que por bloques, pero dice cuántos documentos y cuáles."""
    tabla, col = TABLA[corpus]
    loc = bloques_locales(idx, corpus)
    sel = sorted(loc) if bloques is None else bloques
    pares = sorted((mid[:7], h[:6]) for b in sel for mid, h in loc.get(b, []))
    filtro = "" if bloques is None else (f" where get_byte(decode(md5(id::text),'hex'),0) % {BLOQUES} in "
                                         f"({','.join(map(str, bloques))})")
    valores = ",".join(f"('{m}','{h}')" for m, h in pares)
    return (f"with h as (select id::text id, left(md5(id::text),7) mid, left({_HUELLA_PG.format(col=col)},6) hv "
            f"from public.{tabla}{filtro}), loc(mid,hv) as (values {valores}) "
            "select count(*) n, count(*) filter (where h.hv <> loc.hv) distintos, "
            "(select count(*) from h) n_pg, string_agg(h.id, ' ; ') filter (where h.hv <> loc.hv) ids "
            "from h join loc using (mid)")


def sql_diff(idx, corpus, chunk_id) -> str:
    """Lexemas en los que difieren Postgres y el analizador local para un documento (solo lexemas, no el texto)."""
    tabla, col = TABLA[corpus]
    c = CORPUS.index(corpus)
    i = next(k for k in range(idx.n) if idx.corpus[k] == c and idx.ids[k] == chunk_id)
    from indice_local import conteos_tsvector
    loc = conteos_tsvector(idx.contenidos[i])
    esc = lambda x: x.replace("'", "''")
    valores = ",".join(f"('{esc(k)}',{v})" for k, v in sorted(loc.items())) or "(null::text,null::int)"
    return (f"with pg as (select lexeme lx, array_length(positions,1) n from unnest(to_tsvector('spanish', "
            f"(select {col} from public.{tabla} where id::text = '{esc(chunk_id)}')))), "
            f"loc(lx,n) as (values {valores}) "
            "select 'solo_pg' lado, * from (select * from pg except select * from loc) a union all "
            "select 'solo_local', * from (select * from loc except select * from pg) b order by 2")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", choices=CORPUS)
    ap.add_argument("--bloque", type=int)
    ap.add_argument("--diff", help="id de un documento: lexemas en que difieren")
    ap.add_argument("--docs", action="store_true", help="comparación por documento de todo el corpus")
    ap.add_argument("--bloques", help="con --docs: solo estos bloques, p. ej. 0,1,2")
    ap.add_argument("--indice", type=Path, default=RAIZ / "apps" / "api" / "datos_indice" / "indice_rag.npz")
    a = ap.parse_args()
    idx = IndiceLocal.cargar(a.indice)
    if a.diff:
        print(sql_diff(idx, a.corpus, a.diff))
    elif a.docs:
        print(sql_docs(idx, a.corpus, [int(x) for x in a.bloques.split(",")] if a.bloques else None))
    else:
        print(sql_bloque(idx, a.corpus, a.bloque) if a.bloque is not None else sql_bloques(idx, a.corpus))


if __name__ == "__main__":
    main()
