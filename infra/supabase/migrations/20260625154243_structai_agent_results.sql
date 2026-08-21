-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260625154243
-- Nombre: structai_agent_results
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Tabla de resultados del agente N8N para PWA Realtime
CREATE TABLE IF NOT EXISTS public.agent_results (
  id           uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id   text NOT NULL,          -- ID de sesión de la PWA
  user_id      uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  tipo_consulta text NOT NULL,         -- apu | nsr10 | plano | sgsst | general
  input_texto  text,
  input_archivo text,                  -- nombre del archivo si aplica
  estado       text DEFAULT 'procesando' CHECK (estado IN ('procesando','listo','error')),
  resultado    jsonb,                  -- respuesta completa del agente
  cerebro_usado text,
  latencia_ms  int,
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_agent_session   ON public.agent_results (session_id);
CREATE INDEX IF NOT EXISTS idx_agent_user      ON public.agent_results (user_id);
CREATE INDEX IF NOT EXISTS idx_agent_created   ON public.agent_results (created_at DESC);

-- RLS
ALTER TABLE public.agent_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "agent_select_own" ON public.agent_results;
CREATE POLICY "agent_select_own"
  ON public.agent_results FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "agent_insert_own" ON public.agent_results;
CREATE POLICY "agent_insert_own"
  ON public.agent_results FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "agent_update_own" ON public.agent_results;
CREATE POLICY "agent_update_own"
  ON public.agent_results FOR UPDATE USING (auth.uid() = user_id);

-- Permitir al servicio (N8N via API key) actualizar resultados
DROP POLICY IF EXISTS "agent_service_update" ON public.agent_results;
CREATE POLICY "agent_service_update"
  ON public.agent_results FOR UPDATE USING (true);

DROP POLICY IF EXISTS "agent_service_insert" ON public.agent_results;
CREATE POLICY "agent_service_insert"
  ON public.agent_results FOR INSERT WITH CHECK (true);

-- Trigger updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

DROP TRIGGER IF EXISTS trg_agent_updated ON public.agent_results;
CREATE TRIGGER trg_agent_updated
  BEFORE UPDATE ON public.agent_results
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Habilitar Realtime para esta tabla
ALTER publication supabase_realtime ADD TABLE public.agent_results;

GRANT SELECT, INSERT, UPDATE ON public.agent_results TO authenticated, anon;
