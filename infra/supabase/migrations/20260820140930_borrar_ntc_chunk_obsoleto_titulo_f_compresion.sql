-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820140930
-- Nombre: borrar_ntc_chunk_obsoleto_titulo_f_compresion
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- id 296 (F.5, resistencia nominal en compresion por pandeo) queda redundante
-- y desactualizado frente a NSR10-F-F_2_5a/F_2_5b (verbatim real, agregado hoy
-- en nsr10_chunks). Se conservan 295 (F.8 soldadura/pernos) y 297/298 (F.13
-- R0 sismico) porque todavia no tienen reemplazo verbatim real.
delete from ntc_chunks where id = 296;
