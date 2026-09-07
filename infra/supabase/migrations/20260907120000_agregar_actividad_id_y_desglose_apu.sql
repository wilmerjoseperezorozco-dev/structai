-- Fase 4 del plan de precios (Monte Carlo calibrado + jerarquia
-- actividad-insumo + RAGAS de precios): hoy es IMPOSIBLE reconstruir el
-- desglose real de una actividad (materiales/mano de obra/equipo) a
-- partir de lo que buscar_precios_apu() devuelve, aunque el vinculo real
-- exista en el schema (apu_insumos_referencia.actividad_padre_id ->
-- apu_precios_referencia.id) -- la rama 'actividad' nunca selecciona su
-- propio id, y la rama 'insumo' nunca selecciona actividad_padre_id.
--
-- Verificado antes de escribir esto (count(*) real, no list_tables):
-- de 10.281 insumos, 6.641 (64.6%) tienen actividad_padre_id poblado,
-- 542 (5.3%) solo tienen actividad_padre_texto (fallback denormalizado,
-- sin uuid real), 3.098 (30.1%) no tienen ninguno de los dos -- son
-- insumos sueltos del catalogo general, sin actividad padre. De 4.566
-- actividades, 927 (20.3%) tienen al menos un insumo real enlazado por
-- FK. Cobertura parcial pero real: se construye sobre el 20.3% que sí
-- tiene el vinculo, sin fallback a texto (actividad_padre_texto no es
-- confiable para un join exacto -- es texto libre, no normalizado).
--
-- Cambio 1: agregar actividad_id al final del RETURNS TABLE de
-- buscar_precios_apu -- seguro porque rag_multi_norma.py accede a las
-- columnas por CLAVE (r.get(...)), no por posicion, mismo principio ya
-- usado al agregar categoria_fuente (20260809150329).
--
-- Cambio 2: nueva funcion obtener_desglose_actividad(p_actividad_id) que
-- la capa Python invoca solo para el primer resultado tipo='actividad'
-- de mejor score en ask_precios(), no para los 8 resultados -- evita
-- disparar hasta 8 llamadas RPC extra por pregunta.

-- Agregar una columna al RETURNS TABLE cambia el tipo de fila de OUT
-- parameters -- Postgres no permite CREATE OR REPLACE en ese caso
-- (42P13), hace falta DROP primero (mismo patrón ya usado en
-- 20260809150329_exponer_categoria_fuente_drop_recreate.sql).
DROP FUNCTION IF EXISTS public.buscar_precios_apu(text, integer);

CREATE FUNCTION public.buscar_precios_apu(p_query text, p_limit integer DEFAULT 8)
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
  )
  select 'actividad', actividad, unidad, precio_todo_costo, precio_solo_mano_obra,
         region, tipo_fuente, fecha_captura, item_codigo, categoria_fuente,
         greatest(ts_rank_cd(to_tsvector('spanish', actividad), (select tsq from q)),
                  similarity(actividad, (select raw from q))) as score,
         id
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
  order by score desc
  limit p_limit;
$function$;

CREATE OR REPLACE FUNCTION public.obtener_desglose_actividad(p_actividad_id uuid)
 RETURNS TABLE(tipo_insumo text, insumo text, unidad text, cantidad numeric, valor_unitario numeric, region text, fuente text)
 LANGUAGE sql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
  select tipo_insumo, insumo, unidad, cantidad,
         coalesce(precio_unitario_real, valor_unitario) as valor_unitario,
         region, fuente
  from apu_insumos_referencia
  where actividad_padre_id = p_actividad_id
  order by tipo_insumo, insumo;
$function$;
