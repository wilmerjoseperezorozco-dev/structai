-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260625022113
-- Nombre: construdata_plan_analyses
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- ══════════════════════════════════════════════════════════════
-- CONSTRUDATA — Tablas análisis de planos DWG/PDF + compliance NSR-10
-- ══════════════════════════════════════════════════════════════

-- 1. Análisis de planos (DWG/PDF)
CREATE TABLE IF NOT EXISTS public.plan_analyses (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre_archivo      text NOT NULL,
    formato             text NOT NULL CHECK (formato IN ('DWG','DXF','PDF','PNG','JPG','JPEG')),
    tipo_analisis       text DEFAULT 'plano' CHECK (tipo_analisis IN ('plano','patologia')),
    cerebro_usado       text,          -- gemini-1.5-flash | gpt-4o | claude-3-5-sonnet
    elementos_detectados jsonb DEFAULT '[]',
    apu_calculados      jsonb DEFAULT '[]',
    presupuesto_total   numeric(16,2) DEFAULT 0,
    alertas_nsr10       jsonb DEFAULT '[]',
    cumplimiento_pct    numeric(5,2),
    resultado_completo  jsonb,         -- respuesta completa del análisis
    observaciones       text,
    proyecto_nombre     text,
    created_at          timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_plan_user    ON public.plan_analyses (user_id);
CREATE INDEX IF NOT EXISTS idx_plan_created ON public.plan_analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_plan_formato ON public.plan_analyses (formato);

ALTER TABLE public.plan_analyses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "plan_select_own" ON public.plan_analyses;
CREATE POLICY "plan_select_own"
  ON public.plan_analyses FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "plan_insert_own" ON public.plan_analyses;
CREATE POLICY "plan_insert_own"
  ON public.plan_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "plan_delete_own" ON public.plan_analyses;
CREATE POLICY "plan_delete_own"
  ON public.plan_analyses FOR DELETE USING (auth.uid() = user_id);

-- 2. Verificaciones NSR-10
CREATE TABLE IF NOT EXISTS public.compliance_checks (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_analysis_id    uuid REFERENCES public.plan_analyses(id) ON DELETE SET NULL,
    elemento_tipo       text NOT NULL,
    dimensiones         jsonb DEFAULT '{}',
    especificaciones    jsonb DEFAULT '{}',
    reglas_verificadas  jsonb DEFAULT '[]',
    cumplimiento_pct    numeric(5,2),
    alertas_criticas    jsonb DEFAULT '[]',
    requiere_ingeniero  boolean DEFAULT false,
    analisis_claude     text,           -- razonamiento profundo Claude si se usó
    zona_sismica        text DEFAULT 'alta',
    proyecto_nombre     text,
    created_at          timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_compliance_user    ON public.compliance_checks (user_id);
CREATE INDEX IF NOT EXISTS idx_compliance_created ON public.compliance_checks (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_compliance_tipo    ON public.compliance_checks (elemento_tipo);

ALTER TABLE public.compliance_checks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "compliance_select_own" ON public.compliance_checks;
CREATE POLICY "compliance_select_own"
  ON public.compliance_checks FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "compliance_insert_own" ON public.compliance_checks;
CREATE POLICY "compliance_insert_own"
  ON public.compliance_checks FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "compliance_delete_own" ON public.compliance_checks;
CREATE POLICY "compliance_delete_own"
  ON public.compliance_checks FOR DELETE USING (auth.uid() = user_id);

-- 3. Grants
GRANT SELECT, INSERT, UPDATE, DELETE ON public.plan_analyses    TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.compliance_checks TO authenticated;

-- 4. RPC: guardar análisis de plano
CREATE OR REPLACE FUNCTION public.save_plan_analysis(
  p_user_id            uuid,
  p_nombre_archivo     text,
  p_formato            text,
  p_tipo_analisis      text,
  p_cerebro_usado      text,
  p_elementos          jsonb,
  p_apu_calculados     jsonb,
  p_presupuesto_total  numeric,
  p_alertas_nsr10      jsonb,
  p_cumplimiento_pct   numeric,
  p_resultado_completo jsonb,
  p_proyecto_nombre    text DEFAULT NULL
) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE v_id uuid;
BEGIN
  INSERT INTO public.plan_analyses (
    user_id, nombre_archivo, formato, tipo_analisis, cerebro_usado,
    elementos_detectados, apu_calculados, presupuesto_total,
    alertas_nsr10, cumplimiento_pct, resultado_completo, proyecto_nombre
  ) VALUES (
    p_user_id, p_nombre_archivo, p_formato, p_tipo_analisis, p_cerebro_usado,
    p_elementos, p_apu_calculados, p_presupuesto_total,
    p_alertas_nsr10, p_cumplimiento_pct, p_resultado_completo, p_proyecto_nombre
  ) RETURNING id INTO v_id;
  RETURN v_id;
END;
$$;

GRANT EXECUTE ON FUNCTION public.save_plan_analysis TO authenticated;

-- 5. Vista resumen de análisis de planos
CREATE OR REPLACE VIEW public.v_plan_analyses_resumen AS
SELECT
  p.id, p.user_id,
  p.nombre_archivo, p.formato, p.tipo_analisis, p.cerebro_usado,
  jsonb_array_length(p.elementos_detectados) AS num_elementos,
  jsonb_array_length(p.apu_calculados) AS num_apus,
  p.presupuesto_total, p.cumplimiento_pct,
  jsonb_array_length(p.alertas_nsr10) AS num_alertas,
  p.proyecto_nombre, p.created_at
FROM public.plan_analyses p
ORDER BY p.created_at DESC;

GRANT SELECT ON public.v_plan_analyses_resumen TO authenticated;
