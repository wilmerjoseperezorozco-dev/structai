-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820142011
-- Nombre: borrar_ntc_chunk_obsoleto_titulo_f_soldadura
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- id 295 (F.8 phi soldadura/pernos) queda redundante frente a
-- NSR10-F-F_2_10a (verbatim real, agregado hoy en nsr10_chunks).
delete from ntc_chunks where id = 295;
