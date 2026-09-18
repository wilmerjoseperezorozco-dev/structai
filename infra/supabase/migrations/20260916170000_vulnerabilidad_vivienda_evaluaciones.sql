-- ════════════════════════════════════════════════════════════
-- Motor Vulnerabilidad Vivienda — Fase 1 del issue #51 (2026-09-16)
-- Guarda las evaluaciones del checklist AIS (15 criterios, Título E
-- NSR-10) que un usuario haga desde /vulnerabilidad-vivienda/evaluar,
-- mismo patrón que apu_calculations (RLS por user_id, CRUD propio).
-- ════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.vulnerabilidad_vivienda_evaluaciones (
    id                    uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id               uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    municipio             text,
    respuestas            jsonb NOT NULL,
    aspectos              jsonb NOT NULL,
    calificacion_global   numeric(4,2) NOT NULL,
    clasificacion         text NOT NULL CHECK (clasificacion IN ('BAJA', 'MEDIA', 'ALTA')),
    amenaza_sismica_sgc   jsonb,
    notas                 text,
    created_at            timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vulnerabilidad_vivienda_user_id
    ON public.vulnerabilidad_vivienda_evaluaciones (user_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilidad_vivienda_created
    ON public.vulnerabilidad_vivienda_evaluaciones (created_at DESC);

ALTER TABLE public.vulnerabilidad_vivienda_evaluaciones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "vulnerabilidad_vivienda_select_own" ON public.vulnerabilidad_vivienda_evaluaciones;
CREATE POLICY "vulnerabilidad_vivienda_select_own"
  ON public.vulnerabilidad_vivienda_evaluaciones FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "vulnerabilidad_vivienda_insert_own" ON public.vulnerabilidad_vivienda_evaluaciones;
CREATE POLICY "vulnerabilidad_vivienda_insert_own"
  ON public.vulnerabilidad_vivienda_evaluaciones FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "vulnerabilidad_vivienda_update_own" ON public.vulnerabilidad_vivienda_evaluaciones;
CREATE POLICY "vulnerabilidad_vivienda_update_own"
  ON public.vulnerabilidad_vivienda_evaluaciones FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "vulnerabilidad_vivienda_delete_own" ON public.vulnerabilidad_vivienda_evaluaciones;
CREATE POLICY "vulnerabilidad_vivienda_delete_own"
  ON public.vulnerabilidad_vivienda_evaluaciones FOR DELETE USING (auth.uid() = user_id);
