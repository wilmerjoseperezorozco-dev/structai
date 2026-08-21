-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260817165745
-- Nombre: fix_search_path_buscar_precios_apu_v2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- v1 solo puso 'public' y rompió similarity() (vive en el esquema
-- 'extensions', donde está instalado pg_trgm) -- corregido al primer smoke
-- test, antes de que llegara a producción. Mismo patrón exacto que ya usa
-- search_knowledge: 'public, extensions'.
ALTER FUNCTION public.buscar_precios_apu(text, integer) SET search_path = 'public, extensions';
