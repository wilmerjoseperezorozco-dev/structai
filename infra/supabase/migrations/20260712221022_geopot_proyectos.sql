-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712221022
-- Nombre: geopot_proyectos
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


CREATE TABLE public.geopot_proyectos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  nombre_proyecto text NOT NULL,
  entradas jsonb NOT NULL DEFAULT '{}'::jsonb,
  resultados jsonb NOT NULL DEFAULT '{}'::jsonb,
  notas jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.geopot_proyectos ENABLE ROW LEVEL SECURITY;

CREATE POLICY geopot_select_own ON public.geopot_proyectos
  FOR SELECT USING ((select auth.uid()) = user_id);
CREATE POLICY geopot_insert_own ON public.geopot_proyectos
  FOR INSERT WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY geopot_update_own ON public.geopot_proyectos
  FOR UPDATE USING ((select auth.uid()) = user_id);
CREATE POLICY geopot_delete_own ON public.geopot_proyectos
  FOR DELETE USING ((select auth.uid()) = user_id);

CREATE INDEX idx_geopot_user_id ON public.geopot_proyectos(user_id);
CREATE INDEX idx_geopot_created ON public.geopot_proyectos(created_at DESC);
