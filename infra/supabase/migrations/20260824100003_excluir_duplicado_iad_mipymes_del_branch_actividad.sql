-- Encontrado probando una pregunta real end-to-end: el catalogo IAD
-- MIPYMES quedo cargado DOS VECES -- una vez como mediana generica
-- (apu_precios_referencia, tipo_fuente='catalogo_iad_mipymes', 1.754
-- filas, cargado 2026-08-08) y otra vez con detalle real por proveedor +
-- ahora ciudad (apu_items_nacional/apu_precios_nacional_detalle,
-- tipo_fuente='catalogo_iad_mipymes_detalle', cargado 2026-08-20 y
-- enriquecido con SECOP II 2026-08-24). Las 1.754 filas duplicadas del
-- branch 'actividad' rankeaban IGUAL o MEJOR que el branch
-- 'proveedor_nacional' (mas rico: proveedor real + ciudad + rango),
-- crowdeando el dato bueno fuera del top_k en preguntas reales. Se
-- excluyen del branch 'actividad' -- no se pierde informacion, el branch
-- 'proveedor_nacional' ya incluye la mediana/rango en categoria_fuente.

CREATE OR REPLACE FUNCTION public.buscar_precios_apu(p_query text, p_limit integer DEFAULT 8)
 RETURNS TABLE(tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric, region text, tipo_fuente text, fecha_captura date, item_codigo text, categoria_fuente text, score real)
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
                  similarity(actividad, (select raw from q))) as score
  from apu_precios_referencia, q
  where tipo_fuente <> 'catalogo_iad_mipymes'
    and (to_tsvector('spanish', actividad) @@ (select tsq from q)
     or similarity(actividad, (select raw from q)) > 0.2)
  union all
  select 'insumo', insumo, unidad, coalesce(precio_unitario_real, valor_unitario), null,
         region, tipo_fuente, fecha_captura, null, null,
         greatest(ts_rank_cd(to_tsvector('spanish', insumo), (select tsq from q)),
                  similarity(insumo, (select raw from q))) as score
  from apu_insumos_referencia, q
  where to_tsvector('spanish', insumo) @@ (select tsq from q)
     or similarity(insumo, (select raw from q)) > 0.2
  union all
  select 'proveedor', producto || ' — ' || proveedor, presentacion_unidad, precio_cop, null,
         ciudad, 'proveedor_' || lower(replace(proveedor, ' ', '_')), fecha_captura, null, null,
         greatest(ts_rank_cd(to_tsvector('spanish', producto), (select tsq from q)),
                  similarity(producto, (select raw from q))) as score
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
         im.score
  from items_nacional_match im
  join stats_nacional sn on sn.item_no = im.item_no
  join mejor_nacional mn on mn.item_no = im.item_no
  order by score desc
  limit p_limit;
$function$
