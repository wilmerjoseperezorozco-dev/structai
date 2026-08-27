-- Repaso de RLS 2026-08-25: estas 4 tablas tenian USING (auth.uid() = user_id)
-- en su politica de UPDATE pero SIN WITH CHECK -- a diferencia de
-- apu_calculations/aquai_proyectos/consultas_history/profiles, que si lo
-- tienen. Sin WITH CHECK, un usuario podia UPDATE su propia fila (permitido
-- por USING) y reasignar user_id a otro valor -- no exponia datos de otros
-- usuarios, pero permitia romper la integridad de su propio registro. Se
-- agrega el mismo WITH CHECK que ya usan las demas tablas de usuario, mismo
-- patron, sin cambiar el USING existente.
alter policy "agent_update_own" on public.agent_results
  with check ((select auth.uid()) = user_id);

alter policy "geopot_update_own" on public.geopot_proyectos
  with check ((select auth.uid()) = user_id);

alter policy "gerencia_update_own" on public.gerencia_proyectos
  with check ((select auth.uid()) = user_id);

alter policy "vias_update_own" on public.vias_proyectos
  with check ((select auth.uid()) = user_id);
