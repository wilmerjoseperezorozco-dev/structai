-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820221000
-- Nombre: crear_iad_mipymes_nacional_detalle
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- 2026-08-20: recupera la granularidad de proveedor individual del catalogo
-- IAD MIPYMES (Colombia Compra Eficiente) que ya estaba parcialmente cargado
-- en apu_precios_referencia (region='Nacional', 1754 filas) pero solo como
-- mediana colapsada. Estas 3 tablas son aditivas: no modifican ni reemplazan
-- apu_precios_referencia/apu_insumos_referencia/apu_proveedores_catalogo.
-- Fuente: catalogo_ferreteria_-_iad_mipymes_v13.xlsx (archivo local del
-- usuario, derivado del Instrumento de Agregacion de Demanda MIPYMES de
-- Colombia Compra Eficiente, cobertura nacional, 78 proveedores reales).

create table if not exists public.apu_proveedores_nacional (
  id uuid primary key default gen_random_uuid(),
  nombre text not null unique,
  fuente text not null,
  tipo_fuente text not null default 'IAD MIPYMES',
  created_at timestamptz not null default now()
);

create table if not exists public.apu_items_nacional (
  item_no integer primary key,
  item_nombre text not null,
  unidad text,
  fuente text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.apu_precios_nacional_detalle (
  id uuid primary key default gen_random_uuid(),
  item_no integer not null references public.apu_items_nacional(item_no),
  proveedor_id uuid not null references public.apu_proveedores_nacional(id),
  precio_sin_iva numeric not null,
  precio_valido boolean not null default true,
  fuente text not null,
  created_at timestamptz not null default now(),
  unique (item_no, proveedor_id)
);

create index if not exists idx_apu_precios_nacional_item on public.apu_precios_nacional_detalle(item_no);
create index if not exists idx_apu_precios_nacional_proveedor on public.apu_precios_nacional_detalle(proveedor_id);
create index if not exists idx_apu_items_nacional_nombre_fts on public.apu_items_nacional using gin (to_tsvector('spanish', item_nombre));

alter table public.apu_proveedores_nacional enable row level security;
alter table public.apu_items_nacional enable row level security;
alter table public.apu_precios_nacional_detalle enable row level security;

create policy "lectura publica proveedores nacional" on public.apu_proveedores_nacional
  for select using (true);
create policy "lectura publica items nacional" on public.apu_items_nacional
  for select using (true);
create policy "lectura publica precios nacional detalle" on public.apu_precios_nacional_detalle
  for select using (true);
