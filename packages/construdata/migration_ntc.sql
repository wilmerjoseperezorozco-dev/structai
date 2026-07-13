-- ══════════════════════════════════════════════════════════════
-- MIGRACIÓN: Extender knowledge_graph para NTC + Seg. Industrial
-- Supabase / PostgreSQL + pgvector
-- ══════════════════════════════════════════════════════════════

-- 1. Extender knowledge_nodes con campo 'tipo' si no existe
ALTER TABLE knowledge_nodes
  ADD COLUMN IF NOT EXISTS tipo        text DEFAULT 'NTC',
  ADD COLUMN IF NOT EXISTS version     text,
  ADD COLUMN IF NOT EXISTS fuente      text;

-- 2. Extender knowledge_chunks con keywords array
ALTER TABLE knowledge_chunks
  ADD COLUMN IF NOT EXISTS keywords    text[] DEFAULT '{}';

-- 3. Extender knowledge_edges con id único para upsert
ALTER TABLE knowledge_edges
  ADD COLUMN IF NOT EXISTS id uuid DEFAULT gen_random_uuid(),
  ADD COLUMN IF NOT EXISTS tipo_relacion text DEFAULT 'referencia';

-- Añadir constraint único si no existe
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'knowledge_edges_id_key'
  ) THEN
    ALTER TABLE knowledge_edges ADD CONSTRAINT knowledge_edges_id_key UNIQUE (id);
  END IF;
END $$;

-- 4. Índice BM25-like sobre keywords y contenido
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_keywords
  ON knowledge_chunks USING GIN (keywords);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_contenido_fts
  ON knowledge_chunks USING GIN (to_tsvector('spanish', contenido));

-- 5. Índice pgvector para búsqueda semántica
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
  ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- 6. Función de búsqueda multi-norma (semántica + BM25)
CREATE OR REPLACE FUNCTION search_knowledge(
  query_embedding vector(1536),
  query_text      text,
  p_norma         text DEFAULT NULL,   -- filtro opcional por norma específica
  match_count     int  DEFAULT 8,
  rrf_k           int  DEFAULT 60      -- parámetro Reciprocal Rank Fusion
)
RETURNS TABLE (
  chunk_id    uuid,
  norma       text,
  seccion     text,
  contenido   text,
  score       float,
  metadata    jsonb
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  WITH
  -- Búsqueda semántica por vector
  sem AS (
    SELECT
      kc.id,
      kc.norma_id,
      kc.seccion,
      kc.contenido,
      kc.metadata,
      ROW_NUMBER() OVER (ORDER BY kc.embedding <=> query_embedding) AS rnk
    FROM knowledge_chunks kc
    WHERE (p_norma IS NULL OR kc.norma_id ILIKE '%' || p_norma || '%')
    ORDER BY kc.embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  -- Búsqueda léxica BM25 (full-text search)
  lex AS (
    SELECT
      kc.id,
      kc.norma_id,
      kc.seccion,
      kc.contenido,
      kc.metadata,
      ROW_NUMBER() OVER (
        ORDER BY ts_rank(to_tsvector('spanish', kc.contenido), plainto_tsquery('spanish', query_text)) DESC
      ) AS rnk
    FROM knowledge_chunks kc
    WHERE (p_norma IS NULL OR kc.norma_id ILIKE '%' || p_norma || '%')
      AND to_tsvector('spanish', kc.contenido) @@ plainto_tsquery('spanish', query_text)
    LIMIT match_count * 3
  ),
  -- Reciprocal Rank Fusion (RRF) para combinar ambos rankings
  rrf AS (
    SELECT
      COALESCE(sem.id, lex.id)         AS id,
      COALESCE(sem.norma_id, lex.norma_id) AS norma_id,
      COALESCE(sem.seccion, lex.seccion)   AS seccion,
      COALESCE(sem.contenido, lex.contenido) AS contenido,
      COALESCE(sem.metadata, lex.metadata)   AS metadata,
      (
        COALESCE(1.0 / (rrf_k + sem.rnk), 0) +
        COALESCE(1.0 / (rrf_k + lex.rnk), 0)
      ) AS rrf_score
    FROM sem
    FULL OUTER JOIN lex ON sem.id = lex.id
  )
  SELECT
    rrf.id           AS chunk_id,
    rrf.norma_id     AS norma,
    rrf.seccion,
    rrf.contenido,
    rrf.rrf_score    AS score,
    rrf.metadata
  FROM rrf
  ORDER BY rrf_score DESC
  LIMIT match_count;
END;
$$;

-- 7. Función para obtener grafo de dependencias de una norma
CREATE OR REPLACE FUNCTION get_norma_dependencies(p_codigo text)
RETURNS TABLE (
  source_codigo  text,
  target_codigo  text,
  tipo_relacion  text,
  descripcion    text
)
LANGUAGE sql AS $$
  SELECT
    n_src.codigo,
    n_tgt.codigo,
    ke.tipo_relacion,
    ke.descripcion
  FROM knowledge_edges ke
  JOIN knowledge_nodes n_src ON ke.source_id = n_src.id
  JOIN knowledge_nodes n_tgt ON ke.target_id = n_tgt.id
  WHERE n_src.codigo ILIKE '%' || p_codigo || '%'
     OR n_tgt.codigo ILIKE '%' || p_codigo || '%';
$$;

-- 8. Vista útil para el dashboard
CREATE OR REPLACE VIEW v_knowledge_summary AS
SELECT
  kn.codigo,
  kn.titulo,
  kn.tipo,
  COUNT(kc.id) AS total_chunks,
  kn.fuente
FROM knowledge_nodes kn
LEFT JOIN knowledge_chunks kc ON kc.norma_id = kn.codigo
GROUP BY kn.id, kn.codigo, kn.titulo, kn.tipo, kn.fuente
ORDER BY kn.tipo, kn.codigo;

COMMENT ON FUNCTION search_knowledge IS
'Búsqueda híbrida RRF (semántica + BM25) sobre NTC, NSR-10 y Seg. Industrial';
