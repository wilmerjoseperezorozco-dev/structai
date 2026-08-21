-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260713010240
-- Nombre: vias_proyectos
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


CREATE TABLE public.vias_proyectos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  nombre_proyecto text NOT NULL,
  entradas jsonb NOT NULL DEFAULT '{}'::jsonb,
  resultados jsonb NOT NULL DEFAULT '{}'::jsonb,
  notas jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.vias_proyectos ENABLE ROW LEVEL SECURITY;

CREATE POLICY vias_select_own ON public.vias_proyectos
  FOR SELECT USING ((select auth.uid()) = user_id);
CREATE POLICY vias_insert_own ON public.vias_proyectos
  FOR INSERT WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY vias_update_own ON public.vias_proyectos
  FOR UPDATE USING ((select auth.uid()) = user_id);
CREATE POLICY vias_delete_own ON public.vias_proyectos
  FOR DELETE USING ((select auth.uid()) = user_id);

CREATE INDEX idx_vias_user_id ON public.vias_proyectos(user_id);
CREATE INDEX idx_vias_created ON public.vias_proyectos(created_at DESC);
