-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820140746
-- Nombre: borrar_chunks_obsoletos_titulo_f_batch1
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

delete from nsr10_chunks where id in ('E-SEC4-FORM1', 'E-SEC5-IMG1', 'E-SEC5-FORM1');
