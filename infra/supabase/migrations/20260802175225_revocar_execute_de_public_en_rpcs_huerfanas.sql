-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260802175225
-- Nombre: revocar_execute_de_public_en_rpcs_huerfanas
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- El REVOKE anterior (FROM anon, authenticated) no bastó: Postgres otorga
-- EXECUTE a PUBLIC automáticamente al crear una función, y ese grant a
-- PUBLIC se hereda independientemente de lo que se revoque a un rol
-- puntual. Confirmado con has_function_privilege() tras la migración
-- anterior: seguía dando true. Revocando explícitamente de PUBLIC.
REVOKE EXECUTE ON FUNCTION public.save_apu_calculation(
  uuid, uuid, text, text, text, text, numeric, numeric, numeric, numeric,
  numeric, numeric, numeric, numeric, numeric, numeric, text, text, text
) FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.save_consulta(
  uuid, text, text, text[], text[], integer, integer, text
) FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.save_plan_analysis(
  uuid, text, text, text, text, jsonb, jsonb, numeric, jsonb, numeric, jsonb, text
) FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC;

-- Re-otorgar EXECUTE a service_role explícitamente por si el backend
-- decide usarlas en el futuro (hoy no las usa, pero no hay razón para
-- que la service key quede sin acceso a funciones propias del esquema).
GRANT EXECUTE ON FUNCTION public.save_apu_calculation(
  uuid, uuid, text, text, text, text, numeric, numeric, numeric, numeric,
  numeric, numeric, numeric, numeric, numeric, numeric, text, text, text
) TO service_role;

GRANT EXECUTE ON FUNCTION public.save_consulta(
  uuid, text, text, text[], text[], integer, integer, text
) TO service_role;

GRANT EXECUTE ON FUNCTION public.save_plan_analysis(
  uuid, text, text, text, text, jsonb, jsonb, numeric, jsonb, numeric, jsonb, text
) TO service_role;
