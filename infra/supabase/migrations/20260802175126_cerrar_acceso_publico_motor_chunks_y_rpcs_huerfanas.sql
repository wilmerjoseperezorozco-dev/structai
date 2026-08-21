-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260802175126
-- Nombre: cerrar_acceso_publico_motor_chunks_y_rpcs_huerfanas
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Hallazgo 2026-08-02: policy de escritura en motor_chunks aplicaba a
-- "public" (todos los roles, incluido anon) con USING(true)/WITH CHECK(true)
-- para ALL -- cualquiera con la anon key publica podia insertar/modificar/
-- borrar el corpus normativo sin login. El backend usa la service_role key,
-- que ya bypassea RLS por diseño de Supabase, asi que esta policy nunca
-- fue necesaria para que el backend funcionara -- puro riesgo sin beneficio.
DROP POLICY IF EXISTS service_write_motor_chunks ON public.motor_chunks;

-- 4 funciones SECURITY DEFINER invocables por anon/authenticated via RPC
-- publico. Confirmado por grep en apps/api y apps/web: ninguna se usa en
-- el codigo actual (el backend inserta directo con .table().insert() via
-- service key, no via estas RPCs) -- son residuo de una arquitectura
-- anterior. handle_new_user() SI tiene un uso legitimo via el trigger
-- on_auth_user_created en auth.users; revocar EXECUTE de anon/authenticated
-- no rompe el trigger (los triggers no dependen de grants de EXECUTE sobre
-- el rol que dispara el evento).
REVOKE EXECUTE ON FUNCTION public.save_apu_calculation(
  uuid, uuid, text, text, text, text, numeric, numeric, numeric, numeric,
  numeric, numeric, numeric, numeric, numeric, numeric, text, text, text
) FROM anon, authenticated;

REVOKE EXECUTE ON FUNCTION public.save_consulta(
  uuid, text, text, text[], text[], integer, integer, text
) FROM anon, authenticated;

REVOKE EXECUTE ON FUNCTION public.save_plan_analysis(
  uuid, text, text, text, text, jsonb, jsonb, numeric, jsonb, numeric, jsonb, text
) FROM anon, authenticated;

REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM anon, authenticated;
