-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820143004
-- Nombre: borrar_ntc_chunks_obsoletos_r0_acero_f13
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- ids 297/298 asumian que los coeficientes R0 sismicos de acero viven en un
-- capitulo "F.13" del Titulo F -- error de atribucion: en realidad son las
-- Tablas A.3-1/A.3-3/A.3-4 del Titulo A, ahora cubiertas por el chunk
-- verbatim NSR10-A-A_3_3_1_R0_acero.
delete from ntc_chunks where id in (297, 298);
