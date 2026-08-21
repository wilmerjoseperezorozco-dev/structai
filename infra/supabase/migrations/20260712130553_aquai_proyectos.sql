-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260712130553
-- Nombre: aquai_proyectos
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- AquAI — motor hidrosanitario RAS 2000, complementario de StructAI pero
-- diseñado para ser separable: todo el esquema usa el prefijo aquai_,
-- sin foreign keys hacia tablas propias de StructAI (solo hacia auth.users,
-- que cualquier proyecto Supabase tiene) — un futuro `pg_dump -t 'aquai_*'`
-- se lleva el módulo completo sin arrastrar nada más.

CREATE TABLE IF NOT EXISTS public.aquai_proyectos (
  id                  uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  nombre_proyecto     text NOT NULL,
  entradas            jsonb NOT NULL DEFAULT '{}'::jsonb,   -- inputs de los módulos calculados
  resultados          jsonb NOT NULL DEFAULT '{}'::jsonb,   -- outputs de los módulos calculados
  notas               jsonb NOT NULL DEFAULT '[]'::jsonb,   -- incluye intervalos IC90% Monte Carlo
  poblacion_diseno    numeric,                               -- columna resumen para listado rápido
  caudal_diseno_lps   numeric,                               -- columna resumen para listado rápido
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.aquai_proyectos ENABLE ROW LEVEL SECURITY;

CREATE POLICY aquai_select_own ON public.aquai_proyectos
  FOR SELECT USING ((select auth.uid()) = user_id);
CREATE POLICY aquai_insert_own ON public.aquai_proyectos
  FOR INSERT WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY aquai_update_own ON public.aquai_proyectos
  FOR UPDATE USING ((select auth.uid()) = user_id) WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY aquai_delete_own ON public.aquai_proyectos
  FOR DELETE USING ((select auth.uid()) = user_id);

CREATE INDEX IF NOT EXISTS idx_aquai_user_id ON public.aquai_proyectos(user_id);
CREATE INDEX IF NOT EXISTS idx_aquai_created ON public.aquai_proyectos(created_at DESC);

COMMENT ON TABLE public.aquai_proyectos IS
'AquAI — motor hidrosanitario RAS 2000. Complementario de StructAI, diseñado para ser separable (prefijo aquai_, sin FKs cruzadas a tablas de StructAI).';
