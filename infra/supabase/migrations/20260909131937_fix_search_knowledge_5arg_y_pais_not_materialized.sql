-- Mismo fix que la versión de 6 args, aplicado al overload viejo de 5 args
-- (por si algo lo sigue llamando) y a las 2 RPC de país que comparten el mismo
-- patrón CTE 'filtrado' referenciada 2 veces (sem + lex).
CREATE OR REPLACE FUNCTION public.search_knowledge(query_embedding vector, query_text text, p_norma text DEFAULT NULL::text, match_count integer DEFAULT 8, rrf_k integer DEFAULT 60)
 RETURNS TABLE(chunk_id text, norma text, seccion text, contenido text, score double precision, metadata jsonb)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
BEGIN
  RETURN QUERY
  WITH
  fuente AS (
    SELECT nc.id::text AS f_id, nc.capitulo AS f_norma, nc.seccion AS f_seccion, nc.texto AS f_contenido, nc.embedding AS f_embedding
      FROM public.nsr10_chunks nc
    UNION ALL
    SELECT tc.id::text AS f_id, tc.norma AS f_norma, tc.seccion AS f_seccion, tc.contenido AS f_contenido, tc.embedding AS f_embedding
      FROM public.ntc_chunks tc
  ),
  filtrado AS NOT MATERIALIZED (
    SELECT f.f_id, f.f_norma, f.f_seccion, f.f_contenido, f.f_embedding
    FROM fuente f
    WHERE p_norma IS NULL OR f.f_norma ILIKE '%' || p_norma || '%'
  ),
  sem AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido,
           ROW_NUMBER() OVER (ORDER BY ft.f_embedding <=> query_embedding) AS rnk
    FROM filtrado ft
    WHERE ft.f_embedding IS NOT NULL
    ORDER BY ft.f_embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  lex AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(to_tsvector('spanish', ft.f_contenido), plainto_tsquery('spanish', query_text)) DESC
           ) AS rnk
    FROM filtrado ft
    WHERE to_tsvector('spanish', ft.f_contenido) @@ plainto_tsquery('spanish', query_text)
    LIMIT match_count * 3
  ),
  rrf AS (
    SELECT
      COALESCE(s.f_id, l.f_id)             AS r_id,
      COALESCE(s.f_norma, l.f_norma)       AS r_norma,
      COALESCE(s.f_seccion, l.f_seccion)   AS r_seccion,
      COALESCE(s.f_contenido, l.f_contenido) AS r_contenido,
      (
        COALESCE(1.0 / (rrf_k + s.rnk), 0) +
        COALESCE(1.0 / (rrf_k + l.rnk), 0)
      )::float8 AS rrf_score
    FROM sem s
    FULL OUTER JOIN lex l ON s.f_id = l.f_id
  )
  SELECT
    r.r_id           AS chunk_id,
    r.r_norma        AS norma,
    r.r_seccion      AS seccion,
    r.r_contenido    AS contenido,
    r.rrf_score      AS score,
    '{}'::jsonb      AS metadata
  FROM rrf r
  ORDER BY r.rrf_score DESC
  LIMIT match_count;
END;
$function$;

CREATE OR REPLACE FUNCTION public.search_knowledge_peru_e030(query_embedding vector, query_text text, p_capitulo text DEFAULT NULL::text, match_count integer DEFAULT 8, rrf_k integer DEFAULT 60)
 RETURNS TABLE(chunk_id text, capitulo text, seccion text, contenido text, score double precision)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
declare
  v_tsquery tsquery;
begin
  v_tsquery := regexp_replace(plainto_tsquery('spanish', query_text)::text, ' & ', ' | ', 'g')::tsquery;

  return query
  with
  filtrado as NOT MATERIALIZED (
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

CREATE OR REPLACE FUNCTION public.search_knowledge_ecuador_nec_se_ds(query_embedding vector, query_text text, p_capitulo text DEFAULT NULL::text, match_count integer DEFAULT 8, rrf_k integer DEFAULT 60)
 RETURNS TABLE(chunk_id text, capitulo text, seccion text, contenido text, score double precision)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
declare
  v_tsquery tsquery;
begin
  v_tsquery := regexp_replace(plainto_tsquery('spanish', query_text)::text, ' & ', ' | ', 'g')::tsquery;

  return query
  with
  filtrado as NOT MATERIALIZED (
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
