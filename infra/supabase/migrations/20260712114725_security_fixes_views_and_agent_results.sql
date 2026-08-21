-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712114725
-- Nombre: security_fixes_views_and_agent_results
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- 1. Vistas SECURITY DEFINER -> SECURITY INVOKER (respetan RLS del usuario que consulta)
ALTER VIEW public.v_consultas_stats SET (security_invoker = true);
ALTER VIEW public.v_historial_reciente SET (security_invoker = true);
ALTER VIEW public.v_plan_analyses_resumen SET (security_invoker = true);

-- 2. agent_results: eliminar policies que permiten INSERT/UPDATE sin restriccion
-- (service_role ya bypassa RLS por completo, no necesita estas policies;
-- dejarlas expuestas a 'public' permite que cualquiera con la anon key
-- escriba o sobrescriba filas de cualquier usuario)
DROP POLICY IF EXISTS agent_service_insert ON public.agent_results;
DROP POLICY IF EXISTS agent_service_update ON public.agent_results;

-- 3. Performance: evitar re-evaluar auth.uid() por fila en las RLS existentes
ALTER POLICY profiles_select_own ON public.profiles
  USING ((select auth.uid()) = id);
ALTER POLICY profiles_update_own ON public.profiles
  USING ((select auth.uid()) = id);
ALTER POLICY profiles_insert_own ON public.profiles
  WITH CHECK ((select auth.uid()) = id);

ALTER POLICY consultas_select_own ON public.consultas_history
  USING ((select auth.uid()) = user_id);
ALTER POLICY consultas_insert_own ON public.consultas_history
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY consultas_update_own ON public.consultas_history
  USING ((select auth.uid()) = user_id);
ALTER POLICY consultas_delete_own ON public.consultas_history
  USING ((select auth.uid()) = user_id);

ALTER POLICY apu_select_own ON public.apu_calculations
  USING ((select auth.uid()) = user_id);
ALTER POLICY apu_insert_own ON public.apu_calculations
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY apu_update_own ON public.apu_calculations
  USING ((select auth.uid()) = user_id);
ALTER POLICY apu_delete_own ON public.apu_calculations
  USING ((select auth.uid()) = user_id);

ALTER POLICY plan_select_own ON public.plan_analyses
  USING ((select auth.uid()) = user_id);
ALTER POLICY plan_insert_own ON public.plan_analyses
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY plan_delete_own ON public.plan_analyses
  USING ((select auth.uid()) = user_id);

ALTER POLICY compliance_select_own ON public.compliance_checks
  USING ((select auth.uid()) = user_id);
ALTER POLICY compliance_insert_own ON public.compliance_checks
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY compliance_delete_own ON public.compliance_checks
  USING ((select auth.uid()) = user_id);

ALTER POLICY agent_select_own ON public.agent_results
  USING ((select auth.uid()) = user_id);
ALTER POLICY agent_insert_own ON public.agent_results
  WITH CHECK ((select auth.uid()) = user_id);
ALTER POLICY agent_update_own ON public.agent_results
  USING ((select auth.uid()) = user_id);

-- 4. Mover extensiones fuera de public (buena practica Supabase)
CREATE SCHEMA IF NOT EXISTS extensions;
ALTER EXTENSION vector SET SCHEMA extensions;
ALTER EXTENSION pg_trgm SET SCHEMA extensions;
