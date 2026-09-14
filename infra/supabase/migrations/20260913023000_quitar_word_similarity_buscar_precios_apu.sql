-- Revierte word_similarity() de 20260913022343 (dedup_y_word_similarity_
-- buscar_precios_apu) tras verificar con SQL directo un efecto secundario
-- real no previsto en apu_precios_referencia:
--
--   word_similarity('Maestro', <pregunta con sinonimos>)                = 1.0  (bueno, el objetivo)
--   word_similarity('en concreto', <misma pregunta>)                    = 1.0  (MALO -- fila corrupta)
--   word_similarity('EN', <misma pregunta>)                             = 1.0  (MALO -- fila corrupta)
--   word_similarity("Construcción de anden de concreto f'c 21.0 Mpa..."
--                    -- actividad REAL y especifica, <misma pregunta>)  = 0.16 (peor que la basura)
--
-- "en concreto", "en en concreto concreto", "EN" son nombres de actividad
-- corruptos en apu_precios_referencia (mismo tipo de artefacto de
-- extraccion de tabla del PDF fuente ya conocido en apu_insumos_referencia
-- -- bug de datos real pero acotado, 6 filas totales, ver informe). Con
-- word_similarity en el greatest(...), esas filas basura saltaban a
-- score=1.0 por delante de actividades reales y especificas, invirtiendo
-- la prioridad que se buscaba. Confirmado que sin word_similarity la
-- deduplicacion (20260913022343) YA resuelve GAP 1 por si sola (verificado
-- con SQL directo, ver informe) -- el problema de las 4 copias identicas
-- de "Rampas para puente peatonal..." desaparece con solo el dedup.
--
-- GAP 2 ("Maestro" no aparece en el top_k para "capataz de obra") se
-- resuelve del lado de Python (rag_multi_norma.buscar_precios_apu()): un
-- boost explicito que requiere coincidencia EXACTA de un termino de
-- SINONIMOS_CONSTRUCCION ya conocido, no fuzzy matching generico en SQL
-- que no distingue un termino de catalogo corto real de un fragmento
-- corrupto igual de corto.

CREATE OR REPLACE FUNCTION public.buscar_precios_apu(p_query text, p_limit integer DEFAULT 8)
 RETURNS TABLE(tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric, region text, tipo_fuente text, fecha_captura date, item_codigo text, categoria_fuente text, score real, actividad_id uuid)
 LANGUAGE sql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
  with q as (
    select
      to_tsquery('spanish', (select string_agg(lexeme, ' | ') from unnest(to_tsvector('spanish', p_query)))) as tsq,
      p_query as raw
  ),
  items_nacional_match as (
    select i.item_no, i.item_nombre, i.unidad,
           greatest(ts_rank_cd(to_tsvector('spanish', i.item_nombre), (select tsq from q)),
                    similarity(i.item_nombre, (select raw from q))) as score
    from apu_items_nacional i, q
    where to_tsvector('spanish', i.item_nombre) @@ (select tsq from q)
       or similarity(i.item_nombre, (select raw from q)) > 0.2
  ),
  stats_nacional as (
    select d.item_no, count(*) as n_proveedores,
           min(d.precio_sin_iva) as precio_min, max(d.precio_sin_iva) as precio_max
    from apu_precios_nacional_detalle d
    where d.precio_valido and not d.precio_sospechoso
    group by d.item_no
  ),
  mejor_nacional as (
    select distinct on (d.item_no) d.item_no, d.precio_sin_iva, p.nombre as proveedor_nombre,
           p.departamento as proveedor_departamento, p.municipio as proveedor_municipio
    from apu_precios_nacional_detalle d
    join apu_proveedores_nacional p on p.id = d.proveedor_id
    where d.precio_valido and not d.precio_sospechoso
    order by d.item_no, d.precio_sin_iva asc
  ),
  candidatos as (
    select 'actividad'::text as tipo, actividad as nombre, unidad, precio_todo_costo as precio, precio_solo_mano_obra,
           region, tipo_fuente, fecha_captura, item_codigo, categoria_fuente,
           greatest(ts_rank_cd(to_tsvector('spanish', actividad), (select tsq from q)),
                    similarity(actividad, (select raw from q))) as score,
           id as actividad_id
    from apu_precios_referencia, q
    where tipo_fuente <> 'catalogo_iad_mipymes'
      and (to_tsvector('spanish', actividad) @@ (select tsq from q)
       or similarity(actividad, (select raw from q)) > 0.2)
    union all
    select 'insumo', insumo, unidad, coalesce(precio_unitario_real, valor_unitario), null,
           region, tipo_fuente, fecha_captura, null, null,
           greatest(ts_rank_cd(to_tsvector('spanish', insumo), (select tsq from q)),
                    similarity(insumo, (select raw from q))) as score,
           null::uuid
    from apu_insumos_referencia, q
    where to_tsvector('spanish', insumo) @@ (select tsq from q)
       or similarity(insumo, (select raw from q)) > 0.2
    union all
    select 'proveedor', producto || ' — ' || proveedor, presentacion_unidad, precio_cop, null,
           ciudad, 'proveedor_' || lower(replace(proveedor, ' ', '_')), fecha_captura, null, null,
           greatest(ts_rank_cd(to_tsvector('spanish', producto), (select tsq from q)),
                    similarity(producto, (select raw from q))) as score,
           null::uuid
    from apu_proveedores_catalogo, q
    where to_tsvector('spanish', producto) @@ (select tsq from q)
       or similarity(producto, (select raw from q)) > 0.2
    union all
    select 'proveedor_nacional',
           im.item_nombre || ' — mejor precio real: ' || mn.proveedor_nombre,
           im.unidad, mn.precio_sin_iva, null,
           coalesce(
             case when mn.proveedor_municipio is not null then mn.proveedor_municipio || ', ' || mn.proveedor_departamento
                  when mn.proveedor_departamento is not null then mn.proveedor_departamento
             end,
             'Nacional'
           ),
           'catalogo_iad_mipymes_detalle', null, im.item_no::text,
           'Comparado entre ' || sn.n_proveedores || ' proveedores mipyme reales de todo el país (rango $' ||
             trim(to_char(sn.precio_min, 'FM999G999G999')) || '–$' || trim(to_char(sn.precio_max, 'FM999G999G999')) || ' COP sin IVA)',
           im.score,
           null::uuid
    from items_nacional_match im
    join stats_nacional sn on sn.item_no = im.item_no
    join mejor_nacional mn on mn.item_no = im.item_no
  ),
  dedup as (
    select distinct on (tipo, lower(trim(nombre)), precio)
           tipo, nombre, unidad, precio, precio_solo_mano_obra, region, tipo_fuente,
           fecha_captura, item_codigo, categoria_fuente, score, actividad_id
    from candidatos
    order by tipo, lower(trim(nombre)), precio, score desc, region
  )
  select tipo, nombre, unidad, precio, precio_solo_mano_obra, region, tipo_fuente, fecha_captura, item_codigo, categoria_fuente, score, actividad_id
  from dedup
  order by score desc
  limit p_limit;
$function$
