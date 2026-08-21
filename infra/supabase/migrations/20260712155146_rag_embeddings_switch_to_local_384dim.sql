-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712155146
-- Nombre: rag_embeddings_switch_to_local_384dim
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


-- Ambas tablas están vacías (RAG nunca tuvo contenido cargado) — cambio seguro,
-- sin pérdida de datos. Pasa de vector(1536) (OpenAI) a vector(384)
-- (sentence-transformers paraphrase-multilingual-MiniLM-L12-v2, local y gratis).

DROP INDEX IF EXISTS public.idx_chunks_embedding;

ALTER TABLE public.nsr10_chunks ALTER COLUMN embedding TYPE vector(384);
ALTER TABLE public.ntc_chunks   ALTER COLUMN embedding TYPE vector(384);

CREATE INDEX idx_chunks_embedding ON public.nsr10_chunks
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

CREATE INDEX idx_ntc_chunks_embedding ON public.ntc_chunks
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
