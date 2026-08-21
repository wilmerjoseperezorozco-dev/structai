-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260817170034
-- Nombre: fix_search_path_buscar_precios_apu_v3
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- v2 uso 'public, extensions' como UNA sola cadena con coma adentro -- Postgres
-- lo tomo como un solo nombre de esquema literal (que no existe), no como dos
-- esquemas separados. Sintaxis correcta: comillas separadas por esquema,
-- igual que ya tiene search_knowledge.
ALTER FUNCTION public.buscar_precios_apu(text, integer) SET search_path TO 'public', 'extensions';
