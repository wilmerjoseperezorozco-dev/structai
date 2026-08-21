-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260821043741
-- Nombre: fix_search_knowledge_p_motor_filtro_roto
-- Aplicada via MCP el 2026-08-21, header reconstruido siguiendo el mismo
-- formato que las 65 migraciones historicas de este directorio.
--
-- BUG REAL confirmado 2026-08-21: la funcion search_knowledge(...,p_motor)
-- filtraba con "(p_motor IS NULL OR f.f_motor = p_motor OR f.f_motor IS NULL)".
-- El tercer termino ("OR f.f_motor IS NULL") dejaba pasar TODO
-- nsr10_chunks/ntc_chunks (que siempre tienen f_motor NULL por construccion
-- en el UNION ALL) sin importar que p_motor pidiera un dominio especifico.
--
-- Confirmado con conteo real antes de aplicar el fix: pedir p_motor='aquai'
-- dejaba pasar los 320 chunks reales de aquai MAS 1007 de nsr10_chunks MAS
-- 294 de ntc_chunks (1301 filas de ruido, 81% del pool de candidatos) en
-- cada busqueda semantica/lexica de cualquier motor (aquai/geopot/vias/
-- gerencia) via ask_delegado(). Efecto real observado en un test de
-- regresion: la pregunta "de que depende el calculo de la dotacion bruta"
-- nunca recuperaba el chunk real (ARTICULO 44, existe verbatim en
-- motor_chunks) porque competia contra 1301 chunks de otros dominios, y el
-- sistema respondia honestamente "no encontre eso" en vez de alucinar --
-- comportamiento correcto de cara al usuario, pero sintoma de un retrieval
-- roto detras.
--
-- Fix: quitar el bypass "OR f.f_motor IS NULL" -- cuando p_motor se
-- especifica, el filtro EXCLUYE nsr10_chunks/ntc_chunks por completo, que
-- es lo que ya decia el docstring de rag_multi_norma.py:search() ("deja
-- fuera nsr10_chunks/ntc_chunks cuando se usa" -- la intencion siempre fue
-- esa, el SQL no la cumplia). Cuando p_motor es NULL (busqueda general
-- /ask, sin motor), el comportamiento NO cambia: "p_motor IS NULL" ya deja
-- pasar todo por si solo, ese camino nunca estuvo roto.
--
-- Verificado end-to-end tras aplicar: la misma pregunta ahora recupera
-- ARTICULO 44/253/255 de la Resolucion 0330 de 2017 y Resolucion CRA 956
-- (las 4 fuentes genuinamente de dominio aquai, cero ruido de otros
-- dominios) y responde con la formula real. Suite de tests de motores
-- (13 casos, aquai/geopot/vias/gerencia): 13/13 en verde tras el fix.
--
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas -- este archivo
-- documenta el cambio ya aplicado, no dispara nada al hacer push.

CREATE OR REPLACE FUNCTION public.search_knowledge(query_embedding vector, query_text text, p_norma text DEFAULT NULL::text, match_count integer DEFAULT 8, rrf_k integer DEFAULT 60, p_motor text DEFAULT NULL::text)
 RETURNS TABLE(chunk_id text, norma text, seccion text, contenido text, score double precision, metadata jsonb)
 LANGUAGE plpgsql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
DECLARE
  q_or tsquery;
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
    LIMIT match_count * 3
  ),
  lex AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido, ft.f_norma_id,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(to_tsvector('spanish', ft.f_contenido), q_or) DESC
           ) AS rnk
    FROM filtrado ft
    WHERE q_or IS NOT NULL AND to_tsvector('spanish', ft.f_contenido) @@ q_or
    LIMIT match_count * 3
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
