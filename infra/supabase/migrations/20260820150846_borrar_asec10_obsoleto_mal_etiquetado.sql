-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820150846
-- Nombre: borrar_asec10_obsoleto_mal_etiquetado
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- A-SEC10-TAB1 etiquetaba A.10 como "notacion general" -- error de atribucion,
-- A.10 real es el capitulo de evaluacion/refuerzo de edificaciones existentes,
-- ahora cubierto por NSR10-A-A_10_general y NSR10-A-A_10_10_reparacion_post_sismo.
delete from nsr10_chunks where id = 'A-SEC10-TAB1';
