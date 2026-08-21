-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820215743
-- Nombre: drop_ivfflat_indexes_low_recall
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- 2026-08-20: los indices ivfflat (lists=10) sobre nsr10_chunks/ntc_chunks
-- daban recall muy bajo con probes=1 por defecto (solo ~10% del espacio de
-- busqueda revisado por consulta) -- confirmado empiricamente: un chunk
-- recien insertado (NSR10-F-F_3_6_4_PAPR) con similitud coseno real 0.60
-- contra su propia consulta no aparecia ni en el top-50 via la funcion RPC,
-- pese a que el calculo manual de similitud si lo ubicaba en el top.
-- Con ~1000-4000 filas por tabla, un sequential scan exacto para KNN de
-- 384 dimensiones es del orden de milisegundos -- no se necesita un indice
-- aproximado a este volumen, y la exactitud es mas valiosa que el ahorro
-- marginal de tiempo. Se elimina el indice; Postgres hara exact KNN via
-- el operador <=> sin index, garantizando recall 100%.
drop index if exists public.idx_chunks_embedding;
drop index if exists public.idx_ntc_chunks_embedding;
