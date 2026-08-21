-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820221734
-- Nombre: marcar_outliers_precio_nacional_detalle
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- 2026-08-20: al verificar el "mejor precio" via buscar_precios_apu, se
-- encontraron 1583 filas (1.4% de 114616) con precio < 10% de la mediana del
-- mismo item -- ej. un proveedor cotizando $925 COP por un accesorio de
-- tuberia de cobre cuando el resto de proveedores cotiza entre $60.000 y
-- $2.500.000 para el mismo item. Es un artefacto de captura (valor
-- centinela/placeholder), no una oferta competitiva real -- si se deja sin
-- marcar, el chat mostraria ese precio como "el mejor precio real" y
-- enganaria al usuario. Se marca (no se borra, sigue visible para
-- auditoria) y se excluye de la seleccion de "mejor precio" en la RPC.
alter table public.apu_precios_nacional_detalle
  add column if not exists precio_sospechoso boolean not null default false;

with medianas as (
  select item_no, percentile_cont(0.5) within group (order by precio_sin_iva) as mediana
  from apu_precios_nacional_detalle
  where precio_valido
  group by item_no
)
update public.apu_precios_nacional_detalle d
set precio_sospechoso = true
from medianas m
where m.item_no = d.item_no
  and d.precio_valido
  and d.precio_sin_iva < 0.1 * m.mediana;

-- La RPC ya usaba distinct on (item_no) ... order by precio_sin_iva asc para
-- elegir el "mejor precio" -- se re-crea excluyendo tambien precio_sospechoso.
create or replace function public.buscar_precios_apu(p_query text, p_limit integer default 8)
returns table(tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric, region text, tipo_fuente text, fecha_captura date, item_codigo text, categoria_fuente text, score real)
language sql
stable
set search_path to 'public', 'extensions'
as $function$
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
    select distinct on (d.item_no) d.item_no, d.precio_sin_iva, p.nombre as proveedor_nombre
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
  where to_tsvector('spanish', actividad) @@ (select tsq from q)
     or similarity(actividad, (select raw from q)) > 0.2
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
         'Nacional', 'catalogo_iad_mipymes_detalle', null, im.item_no::text,
         'Comparado entre ' || sn.n_proveedores || ' proveedores mipyme reales de todo el país (rango $' ||
           trim(to_char(sn.precio_min, 'FM999G999G999')) || '–$' || trim(to_char(sn.precio_max, 'FM999G999G999')) || ' COP sin IVA)',
         im.score
  from items_nacional_match im
  join stats_nacional sn on sn.item_no = im.item_no
  join mejor_nacional mn on mn.item_no = im.item_no
  order by score desc
  limit p_limit;
$function$;
