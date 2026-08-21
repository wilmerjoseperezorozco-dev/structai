-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260628215952
-- Nombre: security_fixes_structai
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


-- 1. Habilitar RLS en tabla sin protección
ALTER TABLE public.ntc_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_ntc_chunks" ON public.ntc_chunks FOR SELECT USING (true);
CREATE POLICY "service_write_ntc_chunks" ON public.ntc_chunks FOR ALL TO service_role USING (true);

-- 2. Políticas para consultas (tabla de log con chat_id, sin auth.uid)
CREATE POLICY "service_all_consultas" ON public.consultas FOR ALL TO service_role USING (true);
CREATE POLICY "auth_read_consultas" ON public.consultas FOR SELECT TO authenticated USING (true);

-- 3. Políticas para nsr10_chunks (tabla de embeddings/referencia)
CREATE POLICY "public_read_nsr10_chunks" ON public.nsr10_chunks FOR SELECT USING (true);
CREATE POLICY "service_write_nsr10_chunks" ON public.nsr10_chunks FOR ALL TO service_role USING (true);

-- 4. Corregir vistas SECURITY DEFINER
DROP VIEW IF EXISTS public.v_consultas_stats;
DROP VIEW IF EXISTS public.v_historial_reciente;
DROP VIEW IF EXISTS public.v_plan_analyses_resumen;

CREATE VIEW public.v_consultas_stats AS
 SELECT date_trunc('day', created_at) AS dia, count(*) AS total_consultas,
    avg(duracion_ms)::integer AS avg_ms,
    sum(tokens_entrada + tokens_salida) AS total_tokens,
    count(DISTINCT chat_id) AS usuarios_unicos,
    round(avg(score_principal)::numeric, 3) AS avg_score
   FROM consultas
  GROUP BY date_trunc('day', created_at)
  ORDER BY date_trunc('day', created_at) DESC;

CREATE VIEW public.v_historial_reciente AS
 SELECT id, user_id, left(pregunta, 120) AS pregunta_preview,
    normas_citadas, chunks_usados, latencia_ms, favorito, created_at
   FROM consultas_history c
  ORDER BY created_at DESC;

CREATE VIEW public.v_plan_analyses_resumen AS
 SELECT id, user_id, nombre_archivo, formato, tipo_analisis, cerebro_usado,
    jsonb_array_length(elementos_detectados) AS num_elementos,
    jsonb_array_length(apu_calculados) AS num_apus,
    presupuesto_total, cumplimiento_pct,
    jsonb_array_length(alertas_nsr10) AS num_alertas,
    proyecto_nombre, created_at
   FROM plan_analyses p
  ORDER BY created_at DESC;

-- 5. Fijar search_path en funciones vulnerables
ALTER FUNCTION public.match_nsr10_chunks SET search_path = public, pg_catalog, extensions;
ALTER FUNCTION public.search_nsr10_fulltext SET search_path = public, pg_catalog;
ALTER FUNCTION public.set_updated_at() SET search_path = public, pg_catalog;
ALTER FUNCTION public.save_consulta(p_user_id uuid, p_pregunta text, p_respuesta text, p_normas_citadas text[], p_normas_detect text[], p_chunks_usados integer, p_latencia_ms integer, p_norma_hint text) SET search_path = public, pg_catalog;
ALTER FUNCTION public.save_apu_calculation(p_user_id uuid, p_uuid_trazab uuid, p_actividad_id text, p_descripcion text, p_unidad text, p_capitulo text, p_cantidad numeric, p_costo_mat numeric, p_costo_mo numeric, p_costo_equipo numeric, p_costo_directo numeric, p_aiu numeric, p_precio_unitario numeric, p_pu_p05 numeric, p_pu_p95 numeric, p_pu_std numeric, p_norma_ref text, p_proyecto_nombre text, p_notas text) SET search_path = public, pg_catalog;
ALTER FUNCTION public.save_plan_analysis(p_user_id uuid, p_nombre_archivo text, p_formato text, p_tipo_analisis text, p_cerebro_usado text, p_elementos jsonb, p_apu_calculados jsonb, p_presupuesto_total numeric, p_alertas_nsr10 jsonb, p_cumplimiento_pct numeric, p_resultado_completo jsonb, p_proyecto_nombre text) SET search_path = public, pg_catalog;

-- 6. Revocar handle_new_user desde roles públicos (trigger, no debe llamarse via REST)
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM anon;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM authenticated;

-- 7. Revocar funciones de escritura desde anon
REVOKE EXECUTE ON FUNCTION public.save_consulta(p_user_id uuid, p_pregunta text, p_respuesta text, p_normas_citadas text[], p_normas_detect text[], p_chunks_usados integer, p_latencia_ms integer, p_norma_hint text) FROM anon;
REVOKE EXECUTE ON FUNCTION public.save_apu_calculation(p_user_id uuid, p_uuid_trazab uuid, p_actividad_id text, p_descripcion text, p_unidad text, p_capitulo text, p_cantidad numeric, p_costo_mat numeric, p_costo_mo numeric, p_costo_equipo numeric, p_costo_directo numeric, p_aiu numeric, p_precio_unitario numeric, p_pu_p05 numeric, p_pu_p95 numeric, p_pu_std numeric, p_norma_ref text, p_proyecto_nombre text, p_notas text) FROM anon;
REVOKE EXECUTE ON FUNCTION public.save_plan_analysis(p_user_id uuid, p_nombre_archivo text, p_formato text, p_tipo_analisis text, p_cerebro_usado text, p_elementos jsonb, p_apu_calculados jsonb, p_presupuesto_total numeric, p_alertas_nsr10 jsonb, p_cumplimiento_pct numeric, p_resultado_completo jsonb, p_proyecto_nombre text) FROM anon;
