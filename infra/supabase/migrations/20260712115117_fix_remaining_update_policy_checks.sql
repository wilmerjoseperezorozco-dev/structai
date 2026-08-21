-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712115117
-- Nombre: fix_remaining_update_policy_checks
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

ALTER POLICY profiles_update_own ON public.profiles
  WITH CHECK ((select auth.uid()) = id);
ALTER POLICY consultas_update_own ON public.consultas_history
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY apu_update_own ON public.apu_calculations
  WITH CHECK ((select auth.uid()) = user_id);
