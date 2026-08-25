-- Búsqueda híbrida RRF (Reciprocal Rank Fusion) para peru_e030_chunks y
-- ecuador_nec_se_ds_chunks -- mismo patrón EXACTO ya en producción para
-- Colombia (search_knowledge() sobre nsr10_chunks+ntc_chunks, usado por
-- search() en packages/construdata/rag_multi_norma.py, la función real
-- que llaman /ask y /consultar).
--
-- Contexto (2026-08-25): se probó la calidad de retrieval de
-- match_peru_e030_chunks/match_ecuador_nec_se_ds_chunks (búsqueda vectorial
-- pura) y se encontraron varios casos donde el chunk correcto quedaba
-- fuera del top_k=6 (glosarios de definiciones cortas y estructuralmente
-- parecidas -- perfiles de suelo S0-S4 en Perú, PISO BLANDO/SISMO DE
-- DISEÑO en Ecuador, el Paso 13A del Anexo I). Eso era una alarma real,
-- pero probaba la función equivocada: Colombia NUNCA usa
-- match_nsr10_chunks puro en producción, usa search_knowledge() híbrida.
-- Estas funciones cierran esa brecha arquitectónica para que Perú/Ecuador
-- tengan la misma garantía que Colombia antes de wirearlos al chat.
--
-- No se unifica en una sola función con Colombia (mismo criterio que ya
-- separó las tablas): cada país tiene su propio filtro de "capítulo" con
-- semántica distinta, y mezclar corpus de normas de países distintos en
-- un solo ranking arriesga falsos positivos de similitud entre normas
-- que no tienen relación real entre sí.

create or replace function public.search_knowledge_peru_e030(
  query_embedding vector,
  query_text text,
  p_capitulo text default null::text,
  match_count integer default 8,
  rrf_k integer default 60
)
returns table(chunk_id text, capitulo text, seccion text, contenido text, score double precision)
language plpgsql
stable
set search_path to 'public', 'extensions'
as $function$
begin
  return query
  with
  filtrado as (
    select c.id::text as f_id, c.capitulo as f_capitulo, c.seccion as f_seccion,
           c.texto as f_contenido, c.embedding as f_embedding
    from public.peru_e030_chunks c
    where p_capitulo is null or c.capitulo ilike '%' || p_capitulo || '%'
  ),
  sem as (
    select ft.f_id, ft.f_capitulo, ft.f_seccion, ft.f_contenido,
           row_number() over (order by ft.f_embedding <=> query_embedding) as rnk
    from filtrado ft
    where ft.f_embedding is not null
    order by ft.f_embedding <=> query_embedding
    limit match_count * 3
  ),
  lex as (
    select ft.f_id, ft.f_capitulo, ft.f_seccion, ft.f_contenido,
           row_number() over (
             order by ts_rank(to_tsvector('spanish', ft.f_contenido), plainto_tsquery('spanish', query_text)) desc
           ) as rnk
    from filtrado ft
    where to_tsvector('spanish', ft.f_contenido) @@ plainto_tsquery('spanish', query_text)
    limit match_count * 3
  ),
  rrf as (
    select
      coalesce(s.f_id, l.f_id) as r_id,
      coalesce(s.f_capitulo, l.f_capitulo) as r_capitulo,
      coalesce(s.f_seccion, l.f_seccion) as r_seccion,
      coalesce(s.f_contenido, l.f_contenido) as r_contenido,
      (coalesce(1.0 / (rrf_k + s.rnk), 0) + coalesce(1.0 / (rrf_k + l.rnk), 0))::float8 as rrf_score
    from sem s
    full outer join lex l on s.f_id = l.f_id
  )
  select r.r_id as chunk_id, r.r_capitulo as capitulo, r.r_seccion as seccion,
         r.r_contenido as contenido, r.rrf_score as score
  from rrf r
  order by r.rrf_score desc
  limit match_count;
end; $function$;

create or replace function public.search_knowledge_ecuador_nec_se_ds(
  query_embedding vector,
  query_text text,
  p_capitulo text default null::text,
  match_count integer default 8,
  rrf_k integer default 60
)
returns table(chunk_id text, capitulo text, seccion text, contenido text, score double precision)
language plpgsql
stable
set search_path to 'public', 'extensions'
as $function$
begin
  return query
  with
  filtrado as (
    select c.id::text as f_id, c.capitulo as f_capitulo, c.seccion as f_seccion,
           c.texto as f_contenido, c.embedding as f_embedding
    from public.ecuador_nec_se_ds_chunks c
    where p_capitulo is null or c.capitulo ilike '%' || p_capitulo || '%'
  ),
  sem as (
    select ft.f_id, ft.f_capitulo, ft.f_seccion, ft.f_contenido,
           row_number() over (order by ft.f_embedding <=> query_embedding) as rnk
    from filtrado ft
    where ft.f_embedding is not null
    order by ft.f_embedding <=> query_embedding
    limit match_count * 3
  ),
  lex as (
    select ft.f_id, ft.f_capitulo, ft.f_seccion, ft.f_contenido,
           row_number() over (
             order by ts_rank(to_tsvector('spanish', ft.f_contenido), plainto_tsquery('spanish', query_text)) desc
           ) as rnk
    from filtrado ft
    where to_tsvector('spanish', ft.f_contenido) @@ plainto_tsquery('spanish', query_text)
    limit match_count * 3
  ),
  rrf as (
    select
      coalesce(s.f_id, l.f_id) as r_id,
      coalesce(s.f_capitulo, l.f_capitulo) as r_capitulo,
      coalesce(s.f_seccion, l.f_seccion) as r_seccion,
      coalesce(s.f_contenido, l.f_contenido) as r_contenido,
      (coalesce(1.0 / (rrf_k + s.rnk), 0) + coalesce(1.0 / (rrf_k + l.rnk), 0))::float8 as rrf_score
    from sem s
    full outer join lex l on s.f_id = l.f_id
  )
  select r.r_id as chunk_id, r.r_capitulo as capitulo, r.r_seccion as seccion,
         r.r_contenido as contenido, r.rrf_score as score
  from rrf r
  order by r.rrf_score desc
  limit match_count;
end; $function$;
