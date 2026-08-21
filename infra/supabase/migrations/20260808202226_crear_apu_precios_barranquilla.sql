-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260808202226
-- Nombre: crear_apu_precios_barranquilla
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Base de precios APU real Barranquilla/Atlántico — aditivo, no toca tablas existentes.
-- Fuentes: Construdata (Legis), contratos reales Triple A/Pto Colombia, INVIAS regional Atlántico,
-- catálogo Homecenter/Ferretería Samir. Ver scripts/ingesta/apu_barranquilla/ para el loader.

create table if not exists apu_precios_referencia (
  id uuid primary key default gen_random_uuid(),
  actividad text not null,
  unidad text,
  disciplina text,
  precio_todo_costo numeric,
  costo_materiales numeric,
  costo_mano_obra numeric,
  costo_equipo numeric,
  precio_solo_mano_obra numeric,
  desglose_confiable boolean default false,
  precio_bogota numeric,
  precio_cali numeric,
  precio_medellin numeric,
  item_codigo text,
  region text,                 -- 'Barranquilla' | subregión INVIAS (Norte/Sur/Centro Oriente/Occidental) | null
  categoria_fuente text,
  tipo_fuente text not null,   -- 'catalogo_construdata' | 'contrato_real_pto_colombia' | 'contrato_real_triple_a_acometidas' | 'contrato_real_infraestructura_aa' | 'invias_regional' | 'referencia_nacional'
  fuente text,
  fecha_captura date,
  created_at timestamptz default now()
);

create table if not exists apu_insumos_referencia (
  id uuid primary key default gen_random_uuid(),
  actividad_padre_id uuid references apu_precios_referencia(id) on delete set null,
  actividad_padre_texto text,
  disciplina text,
  tipo_insumo text,            -- 'Material' | 'Mano de Obra' | 'Equipo' | 'Transporte'
  insumo text not null,
  unidad text,
  cantidad numeric,
  valor_unitario numeric,      -- Barranquilla / o valor regional segun 'region'
  valor_unitario_bogota numeric,
  valor_unitario_cali numeric,
  valor_unitario_medellin numeric,
  region text,
  tipo_fuente text not null,
  fuente text,
  fecha_captura date,
  created_at timestamptz default now()
);

create table if not exists apu_proveedores_catalogo (
  id uuid primary key default gen_random_uuid(),
  categoria text,
  subcategoria text,
  producto text not null,
  marca text,
  especificaciones text,
  norma_tecnica text,
  presentacion_unidad text,
  precio_cop numeric,
  precio_unitario_normalizado text,
  proveedor text not null,
  ciudad text default 'Barranquilla',
  url_fuente text,
  fecha_captura date,
  estado_verificacion text,    -- 'VERIFICADO' | 'CAPTURADO'
  notas text,
  created_at timestamptz default now()
);

alter table apu_precios_referencia enable row level security;
alter table apu_insumos_referencia enable row level security;
alter table apu_proveedores_catalogo enable row level security;

-- Lectura pública (son precios de referencia, no datos de usuario) — igual que nsr10_chunks/motor_chunks.
create policy "apu_precios_referencia_select" on apu_precios_referencia for select using (true);
create policy "apu_insumos_referencia_select" on apu_insumos_referencia for select using (true);
create policy "apu_proveedores_catalogo_select" on apu_proveedores_catalogo for select using (true);

create index if not exists idx_apu_precios_actividad on apu_precios_referencia using gin (to_tsvector('spanish', actividad));
create index if not exists idx_apu_insumos_insumo on apu_insumos_referencia using gin (to_tsvector('spanish', insumo));
create index if not exists idx_apu_insumos_padre on apu_insumos_referencia(actividad_padre_id);
create index if not exists idx_apu_proveedores_producto on apu_proveedores_catalogo using gin (to_tsvector('spanish', producto));
