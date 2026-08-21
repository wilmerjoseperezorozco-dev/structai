-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260714071528
-- Nombre: create_normas_registro_vigencia
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.


-- Registro centralizado de vigencia normativa: una fila por norma (ley/decreto/
-- resolucion/NTC/NSR-10), no por chunk. Los chunks referencian esta tabla via
-- norma_id, asi que el estado de vigencia se actualiza en un solo lugar cuando
-- una norma se deroga, en vez de tener que re-etiquetar cada chunk individual.
create table public.normas_registro (
  id uuid primary key default gen_random_uuid(),
  codigo text unique not null,
  nombre_completo text not null,
  entidad_emisora text,
  tipo text not null default 'resolucion'
    check (tipo in ('ley','decreto','resolucion','ntc','nsr10','otro')),
  fecha_expedicion date,
  estado_vigencia text not null default 'vigente'
    check (estado_vigencia in ('vigente','derogada_total','derogada_parcial','modificada','desconocido')),
  derogada_por uuid references public.normas_registro(id),
  alcance_derogacion text,
  fuente_drive_id text,
  notas_vigencia text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.normas_registro enable row level security;
create policy "public_read_normas_registro" on public.normas_registro for select using (true);
create policy "service_write_normas_registro" on public.normas_registro for all to service_role using (true) with check (true);

create index idx_normas_registro_derogada_por on public.normas_registro(derogada_por);
create index idx_normas_registro_estado on public.normas_registro(estado_vigencia);

-- Vincula cada chunk existente a su norma en el registro (nullable: backfill
-- gradual, no rompe los chunks ya cargados que aun no se han vinculado).
alter table public.motor_chunks add column norma_id uuid references public.normas_registro(id);
alter table public.nsr10_chunks add column norma_id uuid references public.normas_registro(id);
alter table public.ntc_chunks add column norma_id uuid references public.normas_registro(id);

create index idx_motor_chunks_norma_id on public.motor_chunks(norma_id);
create index idx_nsr10_chunks_norma_id on public.nsr10_chunks(norma_id);
create index idx_ntc_chunks_norma_id on public.ntc_chunks(norma_id);
