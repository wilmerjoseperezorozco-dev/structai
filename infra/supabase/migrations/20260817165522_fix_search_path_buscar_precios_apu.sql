-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260817165522
-- Nombre: fix_search_path_buscar_precios_apu
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Advisor de seguridad de Supabase (2026-08-15): buscar_precios_apu no tenía
-- search_path fijo, a diferencia de search_knowledge que ya lo tiene desde
-- antes ('public, extensions'). Sin SET search_path, la función resuelve
-- nombres de tabla/función según el search_path de quien la llame -- un rol
-- con privilegios para crear objetos en un esquema que se anteponga al
-- search_path podría, en teoría, hacer que la función use una tabla/función
-- suya en vez de la real (search_path hijacking). No cambia ningún
-- comportamiento para el uso normal, solo fija el esquema de resolución.
ALTER FUNCTION public.buscar_precios_apu(text, integer) SET search_path = 'public';
