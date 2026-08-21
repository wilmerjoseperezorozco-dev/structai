-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260808210951
-- Nombre: fix_prefijo_tipo_fuente_proveedores
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Bug: 'catalogo_' || proveedor colisionaba con el tipo_fuente real
-- 'catalogo_construdata' (ambos empiezan por "catalogo_"), haciendo que
-- _fuente_display() en Python tratara a Construdata como si fuera un
-- proveedor de ferretería. Prefijo distinto para evitar la colisión.
create or replace function buscar_precios_apu(p_query text, p_limit int default 8)
returns table (
  tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric,
  region text, tipo_fuente text, fecha_captura date, item_codigo text, score real
)
language sql stable
as $$
  with q as (
    select
      to_tsquery('spanish', (select string_agg(lexeme, ' | ') from unnest(to_tsvector('spanish', p_query)))) as tsq,
      p_query as raw
  )
  select 'actividad', actividad, unidad, precio_todo_costo, precio_solo_mano_obra,
         region, tipo_fuente, fecha_captura, item_codigo,
         greatest(ts_rank_cd(to_tsvector('spanish', actividad), (select tsq from q)),
                  similarity(actividad, (select raw from q))) as score
  from apu_precios_referencia, q
  where to_tsvector('spanish', actividad) @@ (select tsq from q)
     or similarity(actividad, (select raw from q)) > 0.2
  union all
  select 'insumo', insumo, unidad, coalesce(precio_unitario_real, valor_unitario), null,
         region, tipo_fuente, fecha_captura, null,
         greatest(ts_rank_cd(to_tsvector('spanish', insumo), (select tsq from q)),
                  similarity(insumo, (select raw from q))) as score
  from apu_insumos_referencia, q
  where to_tsvector('spanish', insumo) @@ (select tsq from q)
     or similarity(insumo, (select raw from q)) > 0.2
  union all
  select 'proveedor', producto || ' — ' || proveedor, presentacion_unidad, precio_cop, null,
         ciudad, 'proveedor_' || lower(replace(proveedor, ' ', '_')), fecha_captura, null,
         greatest(ts_rank_cd(to_tsvector('spanish', producto), (select tsq from q)),
                  similarity(producto, (select raw from q))) as score
  from apu_proveedores_catalogo, q
  where to_tsvector('spanish', producto) @@ (select tsq from q)
     or similarity(producto, (select raw from q)) > 0.2
  order by score desc
  limit p_limit;
$$;
