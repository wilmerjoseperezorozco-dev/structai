-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260714114500
-- Nombre: search_knowledge_include_general_normativa_in_motor_filter
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


CREATE OR REPLACE FUNCTION public.search_knowledge(
  query_embedding vector, query_text text, p_norma text DEFAULT NULL::text,
  match_count integer DEFAULT 8, rrf_k integer DEFAULT 60, p_motor text DEFAULT NULL::text
)
 RETURNS TABLE(chunk_id text, norma text, seccion text, contenido text, score double precision, metadata jsonb)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
BEGIN
  RETURN QUERY
  WITH
  fuente AS (
    SELECT nc.id::text AS f_id, nc.capitulo AS f_norma, nc.seccion AS f_seccion, nc.texto AS f_contenido, nc.embedding AS f_embedding, NULL::text AS f_motor, nc.norma_id AS f_norma_id
      FROM public.nsr10_chunks nc
    UNION ALL
    SELECT tc.id::text AS f_id, tc.norma AS f_norma, tc.seccion AS f_seccion, tc.contenido AS f_contenido, tc.embedding AS f_embedding, NULL::text AS f_motor, tc.norma_id AS f_norma_id
      FROM public.ntc_chunks tc
    UNION ALL
    SELECT mc.id::text AS f_id, mc.norma_ref AS f_norma, mc.seccion AS f_seccion, mc.contenido AS f_contenido, mc.embedding AS f_embedding, mc.motor AS f_motor, mc.norma_id AS f_norma_id
      FROM public.motor_chunks mc
  ),
  filtrado AS (
    -- Cuando se filtra por motor (ej. 'geopot'), se incluyen ademas los
    -- chunks de normativa general (nsr10_chunks/ntc_chunks, f_motor IS NULL)
    -- -- un dominio de motor no tiene su propio universo normativo aislado,
    -- comparte la base legal general (NSR-10/NTC) con el resto del sistema.
    SELECT f.f_id, f.f_norma, f.f_seccion, f.f_contenido, f.f_embedding, f.f_norma_id
    FROM fuente f
    WHERE (p_norma IS NULL OR f.f_norma ILIKE '%' || p_norma || '%')
      AND (p_motor IS NULL OR f.f_motor = p_motor OR f.f_motor IS NULL)
  ),
  sem AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido, ft.f_norma_id,
           ROW_NUMBER() OVER (ORDER BY ft.f_embedding <=> query_embedding) AS rnk
    FROM filtrado ft
    WHERE ft.f_embedding IS NOT NULL
    ORDER BY ft.f_embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  lex AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido, ft.f_norma_id,
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
      COALESCE(s.f_norma_id, l.f_norma_id) AS r_norma_id,
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
    CASE WHEN nr.id IS NULL THEN '{}'::jsonb
    ELSE jsonb_build_object(
      'estado_vigencia', nr.estado_vigencia,
      'derogada_por', nrd.nombre_completo,
      'alcance_derogacion', nr.alcance_derogacion
    ) END AS metadata
  FROM rrf r
  LEFT JOIN public.normas_registro nr ON nr.id = r.r_norma_id
  LEFT JOIN public.normas_registro nrd ON nrd.id = nr.derogada_por
  ORDER BY r.rrf_score DESC
  LIMIT match_count;
END;
$function$
