-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712115154
-- Nombre: search_knowledge_over_real_schema
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- search_knowledge() original (migration_ntc.sql) operaba sobre knowledge_nodes/
-- knowledge_chunks/knowledge_edges, que NUNCA existieron en este proyecto.
-- El esquema real es nsr10_chunks + ntc_chunks (columnas distintas cada una).
-- Se reescribe para hacer RRF (semantico + texto) sobre AMBAS con UNION.
CREATE OR REPLACE FUNCTION public.search_knowledge(
  query_embedding vector(1536),
  query_text      text,
  p_norma         text DEFAULT NULL,
  match_count     int  DEFAULT 8,
  rrf_k           int  DEFAULT 60
)
RETURNS TABLE (
  chunk_id    text,
  norma       text,
  seccion     text,
  contenido   text,
  score       float,
  metadata    jsonb
)
LANGUAGE plpgsql STABLE SECURITY INVOKER AS $$
BEGIN
  RETURN QUERY
  WITH
  fuente AS (
    -- Unifica nsr10_chunks (id text, capitulo, texto) y ntc_chunks (id bigint, norma, contenido)
    SELECT id::text AS id, capitulo AS norma, seccion, texto AS contenido, embedding
      FROM public.nsr10_chunks
    UNION ALL
    SELECT id::text AS id, norma, seccion, contenido, embedding
      FROM public.ntc_chunks
  ),
  filtrado AS (
    SELECT * FROM fuente
    WHERE p_norma IS NULL OR norma ILIKE '%' || p_norma || '%'
  ),
  sem AS (
    SELECT id, norma, seccion, contenido,
           ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rnk
    FROM filtrado
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  lex AS (
    SELECT id, norma, seccion, contenido,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(to_tsvector('spanish', contenido), plainto_tsquery('spanish', query_text)) DESC
           ) AS rnk
    FROM filtrado
    WHERE to_tsvector('spanish', contenido) @@ plainto_tsquery('spanish', query_text)
    LIMIT match_count * 3
  ),
  rrf AS (
    SELECT
      COALESCE(sem.id, lex.id)             AS id,
      COALESCE(sem.norma, lex.norma)       AS norma,
      COALESCE(sem.seccion, lex.seccion)   AS seccion,
      COALESCE(sem.contenido, lex.contenido) AS contenido,
      (
        COALESCE(1.0 / (rrf_k + sem.rnk), 0) +
        COALESCE(1.0 / (rrf_k + lex.rnk), 0)
      ) AS rrf_score
    FROM sem
    FULL OUTER JOIN lex ON sem.id = lex.id
  )
  SELECT
    rrf.id           AS chunk_id,
    rrf.norma,
    rrf.seccion,
    rrf.contenido,
    rrf.rrf_score    AS score,
    '{}'::jsonb      AS metadata
  FROM rrf
  ORDER BY rrf_score DESC
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION public.search_knowledge IS
'Busqueda hibrida RRF (semantica + texto) sobre nsr10_chunks + ntc_chunks (esquema real, reemplaza la version de migration_ntc.sql que apuntaba a tablas knowledge_* inexistentes)';
