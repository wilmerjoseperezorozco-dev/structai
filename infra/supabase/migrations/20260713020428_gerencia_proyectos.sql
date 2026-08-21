-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260713020428
-- Nombre: gerencia_proyectos
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

create table if not exists public.gerencia_proyectos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  nombre_proyecto text not null,
  entradas jsonb not null default '{}'::jsonb,
  resultados jsonb not null default '{}'::jsonb,
  notas jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.gerencia_proyectos enable row level security;

create policy gerencia_select_own on public.gerencia_proyectos
  for select using ((select auth.uid()) = user_id);

create policy gerencia_insert_own on public.gerencia_proyectos
  for insert with check ((select auth.uid()) = user_id);

create policy gerencia_update_own on public.gerencia_proyectos
  for update using ((select auth.uid()) = user_id);

create policy gerencia_delete_own on public.gerencia_proyectos
  for delete using ((select auth.uid()) = user_id);

create index if not exists idx_gerencia_proyectos_user_id on public.gerencia_proyectos(user_id);
create index if not exists idx_gerencia_proyectos_created_at on public.gerencia_proyectos(created_at desc);
