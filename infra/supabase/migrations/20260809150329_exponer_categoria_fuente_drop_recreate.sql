-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260809150329
-- Nombre: exponer_categoria_fuente_drop_recreate
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

DROP FUNCTION IF EXISTS public.buscar_precios_apu(text, integer);

CREATE FUNCTION public.buscar_precios_apu(p_query text, p_limit integer DEFAULT 8)
 RETURNS TABLE(tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric, region text, tipo_fuente text, fecha_captura date, item_codigo text, categoria_fuente text, score real)
 LANGUAGE sql
 STABLE
AS $function$
  with q as (
    select
      to_tsquery('spanish', (select string_agg(lexeme, ' | ') from unnest(to_tsvector('spanish', p_query)))) as tsq,
      p_query as raw
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
  order by score desc
  limit p_limit;
$function$;
