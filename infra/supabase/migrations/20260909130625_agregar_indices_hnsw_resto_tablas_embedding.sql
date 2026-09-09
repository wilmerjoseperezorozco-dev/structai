-- Mismo criterio que nsr10_chunks: HNSW nativo de pgvector, verificado empíricamente
-- (recall@10 = 99.6% en nsr10_chunks, ver migración anterior) antes de confiar en él.
create index if not exists idx_motor_chunks_embedding_hnsw
  on public.motor_chunks using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);

create index if not exists idx_ntc_chunks_embedding_hnsw
  on public.ntc_chunks using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);

create index if not exists idx_peru_e030_chunks_embedding_hnsw
  on public.peru_e030_chunks using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);

create index if not exists idx_ecuador_nec_se_ds_chunks_embedding_hnsw
  on public.ecuador_nec_se_ds_chunks using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);

-- Verificación real hecha en vivo tras aplicar (no versionada como SQL, documentada
-- en memoria del proyecto): recall@10 medido comparando vecino exacto vs. HNSW en
-- una muestra de hasta 30 chunks por tabla -- motor_chunks 99.7% (299/300),
-- ntc_chunks 100% (300/300), peru_e030_chunks 100% (300/300),
-- ecuador_nec_se_ds_chunks 100% (300/300).
