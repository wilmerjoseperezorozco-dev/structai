-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260625004313
-- Nombre: construdata_auth_rls
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- ══════════════════════════════════════════════════════════════
-- CONSTRUDATA — Auth + Row Level Security
-- ══════════════════════════════════════════════════════════════
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ════════════════════════════════════════════════════════════
-- 1. TABLA: profiles
-- ════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.profiles (
    id            uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email         text,
    nombre        text,
    empresa       text,
    ciudad        text DEFAULT 'Barranquilla',
    plan          text DEFAULT 'free'      CHECK (plan IN ('free','pro','enterprise')),
    consultas_mes int  DEFAULT 0,
    created_at    timestamptz DEFAULT now(),
    updated_at    timestamptz DEFAULT now()
);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  INSERT INTO public.profiles (id, email, nombre)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1))
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

DROP TRIGGER IF EXISTS profiles_updated_at ON public.profiles;
CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ════════════════════════════════════════════════════════════
-- 2. TABLA: consultas_history
-- ════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.consultas_history (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pregunta            text NOT NULL,
    respuesta           text,
    normas_citadas      text[]   DEFAULT '{}',
    normas_detectadas   text[]   DEFAULT '{}',
    chunks_usados       int      DEFAULT 0,
    latencia_ms         int,
    norma_hint          text,
    favorito            boolean  DEFAULT false,
    created_at          timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_consultas_user_id   ON public.consultas_history (user_id);
CREATE INDEX IF NOT EXISTS idx_consultas_created   ON public.consultas_history (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_consultas_favorito  ON public.consultas_history (user_id, favorito) WHERE favorito = true;

-- ════════════════════════════════════════════════════════════
-- 3. TABLA: apu_calculations
-- ════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.apu_calculations (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    uuid_trazabilidad   uuid NOT NULL,
    actividad_id        text NOT NULL,
    descripcion         text,
    unidad              text,
    capitulo            text,
    cantidad            numeric(12,4) DEFAULT 1,
    costo_materiales    numeric(14,2),
    costo_mano_obra     numeric(14,2),
    costo_equipo        numeric(14,2),
    costo_directo       numeric(14,2),
    aiu                 numeric(14,2),
    precio_unitario     numeric(14,2),
    pu_p05              numeric(14,2),
    pu_p95              numeric(14,2),
    pu_std              numeric(14,2),
    norma_ref           text,
    proyecto_nombre     text,
    notas               text,
    created_at          timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_apu_user_id     ON public.apu_calculations (user_id);
CREATE INDEX IF NOT EXISTS idx_apu_created     ON public.apu_calculations (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_apu_proyecto    ON public.apu_calculations (user_id, proyecto_nombre);
CREATE UNIQUE INDEX IF NOT EXISTS idx_apu_uuid ON public.apu_calculations (uuid_trazabilidad);

-- ════════════════════════════════════════════════════════════
-- 4. ROW LEVEL SECURITY
-- ════════════════════════════════════════════════════════════
ALTER TABLE public.profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consultas_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apu_calculations  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own"
  ON public.profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own"
  ON public.profiles FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_insert_own" ON public.profiles;
CREATE POLICY "profiles_insert_own"
  ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "consultas_select_own" ON public.consultas_history;
CREATE POLICY "consultas_select_own"
  ON public.consultas_history FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "consultas_insert_own" ON public.consultas_history;
CREATE POLICY "consultas_insert_own"
  ON public.consultas_history FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "consultas_update_own" ON public.consultas_history;
CREATE POLICY "consultas_update_own"
  ON public.consultas_history FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "consultas_delete_own" ON public.consultas_history;
CREATE POLICY "consultas_delete_own"
  ON public.consultas_history FOR DELETE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "apu_select_own" ON public.apu_calculations;
CREATE POLICY "apu_select_own"
  ON public.apu_calculations FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "apu_insert_own" ON public.apu_calculations;
CREATE POLICY "apu_insert_own"
  ON public.apu_calculations FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "apu_update_own" ON public.apu_calculations;
CREATE POLICY "apu_update_own"
  ON public.apu_calculations FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "apu_delete_own" ON public.apu_calculations;
CREATE POLICY "apu_delete_own"
  ON public.apu_calculations FOR DELETE USING (auth.uid() = user_id);

-- ════════════════════════════════════════════════════════════
-- 5. FUNCIONES RPC
-- ════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION public.save_consulta(
  p_user_id          uuid,
  p_pregunta         text,
  p_respuesta        text,
  p_normas_citadas   text[],
  p_normas_detect    text[],
  p_chunks_usados    int,
  p_latencia_ms      int,
  p_norma_hint       text DEFAULT NULL
) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE v_id uuid;
BEGIN
  INSERT INTO public.consultas_history (
    user_id, pregunta, respuesta,
    normas_citadas, normas_detectadas,
    chunks_usados, latencia_ms, norma_hint
  ) VALUES (
    p_user_id, p_pregunta, p_respuesta,
    p_normas_citadas, p_normas_detect,
    p_chunks_usados, p_latencia_ms, p_norma_hint
  ) RETURNING id INTO v_id;
  UPDATE public.profiles SET consultas_mes = consultas_mes + 1 WHERE id = p_user_id;
  RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.save_apu_calculation(
  p_user_id            uuid,
  p_uuid_trazab        uuid,
  p_actividad_id       text,
  p_descripcion        text,
  p_unidad             text,
  p_capitulo           text,
  p_cantidad           numeric,
  p_costo_mat          numeric,
  p_costo_mo           numeric,
  p_costo_equipo       numeric,
  p_costo_directo      numeric,
  p_aiu                numeric,
  p_precio_unitario    numeric,
  p_pu_p05             numeric,
  p_pu_p95             numeric,
  p_pu_std             numeric,
  p_norma_ref          text DEFAULT NULL,
  p_proyecto_nombre    text DEFAULT NULL,
  p_notas              text DEFAULT NULL
) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE v_id uuid;
BEGIN
  INSERT INTO public.apu_calculations (
    user_id, uuid_trazabilidad, actividad_id, descripcion, unidad, capitulo,
    cantidad, costo_materiales, costo_mano_obra, costo_equipo, costo_directo,
    aiu, precio_unitario, pu_p05, pu_p95, pu_std, norma_ref, proyecto_nombre, notas
  ) VALUES (
    p_user_id, p_uuid_trazab, p_actividad_id, p_descripcion, p_unidad, p_capitulo,
    p_cantidad, p_costo_mat, p_costo_mo, p_costo_equipo, p_costo_directo,
    p_aiu, p_precio_unitario, p_pu_p05, p_pu_p95, p_pu_std, p_norma_ref, p_proyecto_nombre, p_notas
  ) RETURNING id INTO v_id;
  RETURN v_id;
END;
$$;

CREATE OR REPLACE VIEW public.v_historial_reciente AS
SELECT
  c.id, c.user_id,
  left(c.pregunta, 120) AS pregunta_preview,
  c.normas_citadas, c.chunks_usados, c.latencia_ms, c.favorito, c.created_at
FROM public.consultas_history c
ORDER BY c.created_at DESC;

-- ════════════════════════════════════════════════════════════
-- 6. GRANTS
-- ════════════════════════════════════════════════════════════
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles          TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.consultas_history TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.apu_calculations  TO authenticated;
GRANT SELECT ON public.v_historial_reciente TO authenticated;
GRANT EXECUTE ON FUNCTION public.save_consulta        TO authenticated;
GRANT EXECUTE ON FUNCTION public.save_apu_calculation TO authenticated;
