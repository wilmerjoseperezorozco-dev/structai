-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260808203504
-- Nombre: crear_buscar_precios_apu_rpc
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Búsqueda de precios APU Barranquilla/Atlántico — texto completo (español) + trigram
-- como respaldo para términos técnicos cortos que el stemmer no cubre bien.
create extension if not exists pg_trgm;

create index if not exists idx_apu_precios_actividad_trgm on apu_precios_referencia using gin (actividad gin_trgm_ops);
create index if not exists idx_apu_insumos_insumo_trgm on apu_insumos_referencia using gin (insumo gin_trgm_ops);
create index if not exists idx_apu_proveedores_producto_trgm on apu_proveedores_catalogo using gin (producto gin_trgm_ops);

create or replace function buscar_precios_apu(p_query text, p_limit int default 8)
returns table (
  tipo text,               -- 'actividad' | 'insumo' | 'proveedor'
  nombre text,
  unidad text,
  precio numeric,
  precio_solo_mano_obra numeric,
  region text,
  tipo_fuente text,
  fecha_captura date,
  item_codigo text,
  score real
)
language sql stable
as $$
  with q as (select websearch_to_tsquery('spanish', p_query) as tsq, p_query as raw)
  select 'actividad', actividad, unidad, precio_todo_costo, precio_solo_mano_obra,
         region, tipo_fuente, fecha_captura, item_codigo,
         greatest(ts_rank_cd(to_tsvector('spanish', actividad), (select tsq from q)),
                  similarity(actividad, (select raw from q))) as score
  from apu_precios_referencia, q
  where to_tsvector('spanish', actividad) @@ (select tsq from q)
     or similarity(actividad, (select raw from q)) > 0.25
  union all
  select 'insumo', insumo, unidad, coalesce(precio_unitario_real, valor_unitario), null,
         region, tipo_fuente, fecha_captura, null,
         greatest(ts_rank_cd(to_tsvector('spanish', insumo), (select tsq from q)),
                  similarity(insumo, (select raw from q))) as score
  from apu_insumos_referencia, q
  where to_tsvector('spanish', insumo) @@ (select tsq from q)
     or similarity(insumo, (select raw from q)) > 0.25
  union all
  select 'proveedor', producto || ' — ' || proveedor, presentacion_unidad, precio_cop, null,
         ciudad, 'catalogo_' || lower(replace(proveedor, ' ', '_')), fecha_captura, null,
         greatest(ts_rank_cd(to_tsvector('spanish', producto), (select tsq from q)),
                  similarity(producto, (select raw from q))) as score
  from apu_proveedores_catalogo, q
  where to_tsvector('spanish', producto) @@ (select tsq from q)
     or similarity(producto, (select raw from q)) > 0.25
  order by score desc
  limit p_limit;
$$;
