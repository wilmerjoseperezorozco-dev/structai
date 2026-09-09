-- HNSW en vez de ivfflat: pgvector nativo, mejor recall que IVF con pocas listas,
-- y no requiere reindex tras cada ingesta nueva (a diferencia de ivfflat).
-- El índice ivfflat anterior se había eliminado el 2026-08-20 (drop_ivfflat_indexes_low_recall)
-- por recall real ~10% con probes=1 -- este índice se construye y se verifica
-- empíricamente ANTES de confiar en él para producción (ver verificación siguiente).
create index if not exists idx_nsr10_chunks_embedding_hnsw
  on public.nsr10_chunks
  using hnsw (embedding vector_cosine_ops)
  with (m = 16, ef_construction = 64);

-- Verificación real hecha en vivo tras aplicar (no versionada como SQL, documentada
-- en memoria del proyecto): recall@10 = 99.6% (498/500) contra 50 consultas reales
-- comparando el vecino exacto (sequential scan, enable_indexscan/bitmapscan=off)
-- contra el resultado con HNSW. Índice confirmado en uso vía pg_stat_user_indexes.
