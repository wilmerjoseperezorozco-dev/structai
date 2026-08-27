-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260827040028
-- Nombre: fix_search_knowledge_pool_desacoplado_match_count
--
-- BUG REAL confirmado 2026-08-27 (ver [[project_structai_ragas_baseline]] en
-- memoria, investigado tras encontrar inestabilidad de ranking durante el
-- trabajo de re-ranking con cross-encoder): las CTEs `sem` y `lex` de
-- search_knowledge() aplicaban "LIMIT match_count * 3" cada una -- el pool de
-- candidatos de CADA rama (semantica y lexica) quedaba atado al match_count
-- que pedia el LLAMADOR, no a un tamano fijo.
--
-- Efecto real verificado en vivo (consulta compuesta "factores phi para
-- traccion y cortante", chunk NSR10-C-C_9_3_2_1): su rank semantico puro es
-- 288 (dilucion real del embedding en preguntas compuestas) pero su rank
-- lexico puro es 19 (excelente, full-text lo encuentra bien) sobre 8387
-- chunks totales. Con el limite viejo (match_count*3):
--   - a match_count<=60 (limite interno <=180) la rama semantica NUNCA
--     incluye este chunk (288 > 180) -- solo la rama lexica contribuye al RRF.
--   - a match_count=100 (limite interno 300) la rama semantica SI lo incluye
--     (288 < 300) -- el chunk recibe una SEGUNDA contribucion RRF que no
--     tenia antes, saltando de posicion #44/#45 a #24 en el resultado final.
-- Esto no es solo "revelar mas resultados al pedir mas": el mismo chunk
-- recibe un fusionado RRF DISTINTO segun cuanto pida el llamador, lo cual
-- hace que el ranking relativo entre chunks ya incluidos cambie de forma no
-- monotona -- confirmado con posiciones reales None/None/#44/#45/#24 a
-- match_count 30/40/50/60/100.
--
-- Fix: usar un limite FIJO (300) para el pool interno de cada rama,
-- independiente de match_count. Con esto, el fusionado RRF de cualquier
-- chunk es identico sin importar cuanto pida el llamador -- pedir mas
-- match_count solo revela mas profundo en un orden ya fijo, no lo recalcula.
-- 300 se eligio por ser justo el limite en el que el caso real de arriba
-- empezaba a estabilizarse (no es un numero arbitrario) y sigue siendo un
-- pool barato de ordenar sobre un corpus de ~8.4K chunks.
--
-- No cambia el comportamiento del filtro por p_norma/p_motor ni el LIMIT
-- final (match_count), solo el tamano del pool interno pre-fusion.
--
-- Verificado tras aplicar: rank del chunk pasa de ausente/inestable
-- (None/None/#44/#45/#24 a match_count 30/40/50/60/100) a #1 ESTABLE en todo
-- ese mismo rango. test_rag_nsr10_regresion.py::C-factor-phi-traccion-090
-- (antes xfail) ahora PASA de verdad contra el pipeline real (Groq), y la
-- suite completa de motores (test_rag_motores_regresion.py, 13 casos) sigue
-- en 13/13 -- cero regresion.
CREATE OR REPLACE FUNCTION public.search_knowledge(query_embedding vector, query_text text, p_norma text DEFAULT NULL::text, match_count integer DEFAULT 8, rrf_k integer DEFAULT 60, p_motor text DEFAULT NULL::text)
 RETURNS TABLE(chunk_id text, norma text, seccion text, contenido text, score double precision, metadata jsonb)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
DECLARE
  q_or tsquery;
  pool_interno CONSTANT integer := 300;
BEGIN
  -- Combina los lexemas de la pregunta con OR en vez de AND (plainto_tsquery).
  SELECT to_tsquery('spanish', string_agg(lexeme, ' | '))
    INTO q_or
    FROM unnest(to_tsvector('spanish', query_text));

  RETURN QUERY
  WITH
  fuente AS (
    SELECT nc.id::text AS f_id, nc.capitulo AS f_norma, nc.seccion AS f_seccion, nc.texto AS f_contenido, nc.embedding AS f_embedding, NULL::text AS f_motor, nc.norma_id AS f_norma_id
      FROM public.nsr10_chunks nc
    UNION ALL
    SELECT tc.id::text AS f_id, tc.norma AS f_norma, tc.seccion AS f_seccion, tc.contenido AS f_contenido, tc.embedding AS f_embedding, NULL::text AS f_motor, tc.norma_id AS f_norma_id
      FROM public.ntc_chunks tc
    UNION ALL
    SELECT mc.id::text AS f_id, mc.norma_ref AS f_norma, mc.seccion AS f_seccion, mc.contenido AS f_contenido, mc.embedding AS f_embedding, mc.motor AS f_motor, mc.norma_id AS f_norma_id
      FROM public.motor_chunks mc
  ),
  filtrado AS (
    SELECT f.f_id, f.f_norma, f.f_seccion, f.f_contenido, f.f_embedding, f.f_norma_id
    FROM fuente f
    WHERE (p_norma IS NULL OR f.f_norma ILIKE '%' || p_norma || '%')
      AND (p_motor IS NULL OR f.f_motor = p_motor)
  ),
  sem AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido, ft.f_norma_id,
           ROW_NUMBER() OVER (ORDER BY ft.f_embedding <=> query_embedding) AS rnk
    FROM filtrado ft
    WHERE ft.f_embedding IS NOT NULL
    ORDER BY ft.f_embedding <=> query_embedding
    LIMIT pool_interno
  ),
  lex AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido, ft.f_norma_id,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(to_tsvector('spanish', ft.f_contenido), q_or) DESC
           ) AS rnk
    FROM filtrado ft
    WHERE q_or IS NOT NULL AND to_tsvector('spanish', ft.f_contenido) @@ q_or
    LIMIT pool_interno
  ),
  rrf AS (
    SELECT
      COALESCE(s.f_id, l.f_id)             AS r_id,
      COALESCE(s.f_norma, l.f_norma)       AS r_norma,
      COALESCE(s.f_seccion, l.f_seccion)   AS r_seccion,
      COALESCE(s.f_contenido, l.f_contenido) AS r_contenido,
      COALESCE(s.f_norma_id, l.f_norma_id) AS r_norma_id,
      (
        COALESCE(1.0 / (rrf_k + s.rnk), 0) +
        COALESCE(1.0 / (rrf_k + l.rnk), 0)
      )::float8 AS rrf_score
    FROM sem s
    FULL OUTER JOIN lex l ON s.f_id = l.f_id
  )
  SELECT
    r.r_id           AS chunk_id,
    r.r_norma        AS norma,
    r.r_seccion      AS seccion,
    r.r_contenido    AS contenido,
    r.rrf_score      AS score,
    CASE WHEN nr.id IS NULL THEN '{}'::jsonb
    ELSE jsonb_build_object(
      'estado_vigencia', nr.estado_vigencia,
      'derogada_por', nrd.nombre_completo,
      'alcance_derogacion', nr.alcance_derogacion
    ) END AS metadata
  FROM rrf r
  LEFT JOIN public.normas_registro nr ON nr.id = r.r_norma_id
  LEFT JOIN public.normas_registro nrd ON nrd.id = nr.derogada_por
  ORDER BY r.rrf_score DESC
  LIMIT match_count;
END;
$function$;
