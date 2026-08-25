-- Corrección real encontrada al verificar la búsqueda híbrida recién
-- creada (20260825100000): plainto_tsquery() conecta todos los términos
-- con AND -- para que un chunk haga match, TODAS las palabras de la
-- pregunta deben aparecer literalmente en su texto. Para preguntas en
-- lenguaje natural que mezclan varios conceptos (ej. "¿quién es
-- responsable del mantenimiento de la estación acelerométrica y por
-- cuánto tiempo?" -- "estación acelerométrica" está en el Artículo 50,
-- "10 años" está en el Artículo 52, ningún chunk individual tiene ambos),
-- el AND estricto descarta el chunk correcto aunque sea semánticamente
-- la respuesta -- confirmado con SQL directo: 0 resultados con
-- plainto_tsquery Y con websearch_to_tsquery (misma semántica AND para
-- palabras sueltas). Con un OR de los mismos términos ya lematizados
-- (stemmed), el chunk correcto aparece con score real.
--
-- Fix: se reaprovecha el lematizado/stopwords de plainto_tsquery() pero
-- se convierte el operador de AND (&) a OR (|) antes de ejecutar la
-- búsqueda de texto completo -- verificado con SQL directo antes de
-- aplicar (Artículo 52 pasó de 0 resultados a rank #3 con score real).

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
declare
  v_tsquery tsquery;
begin
  -- AND lematizado -> OR, reaprovechando el stemming/stopwords de
  -- plainto_tsquery (ver nota de esta migración). Query vacía tras
  -- limpieza (ej. solo stopwords) da tsquery vacía -- @@ contra ella no
  -- rompe, simplemente no matchea nada y el lex CTE queda vacío.
  v_tsquery := regexp_replace(plainto_tsquery('spanish', query_text)::text, ' & ', ' | ', 'g')::tsquery;

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
             order by ts_rank(to_tsvector('spanish', ft.f_contenido), v_tsquery) desc
           ) as rnk
    from filtrado ft
    where to_tsvector('spanish', ft.f_contenido) @@ v_tsquery
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
declare
  v_tsquery tsquery;
begin
  v_tsquery := regexp_replace(plainto_tsquery('spanish', query_text)::text, ' & ', ' | ', 'g')::tsquery;

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
             order by ts_rank(to_tsvector('spanish', ft.f_contenido), v_tsquery) desc
           ) as rnk
    from filtrado ft
    where to_tsvector('spanish', ft.f_contenido) @@ v_tsquery
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
