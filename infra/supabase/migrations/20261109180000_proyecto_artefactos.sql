-- Artefactos versionados del DAG de proyecto (issue #150).
-- Un artefacto es el resultado de un motor, direccionado por contenido: su id (SHA-256) depende de la versión del
-- motor, la versión de la norma, los parámetros declarados y los ids de los artefactos de entrada.
-- Dos usuarios con el mismo proyecto obtienen el mismo id, por eso la clave primaria es (user_id, id).
-- resultado_texto es la serialización canónica sobre la que se calcula hash_contenido (jsonb no conserva el formato
-- exacto de los números); resultado (jsonb) existe solo para consultar.
create table if not exists public.proyecto_artefactos (
  user_id uuid not null references auth.users(id) on delete cascade,
  id text not null check (length(id) = 64),
  nodo text not null,
  version_motor text not null,
  norma_version text not null,
  hash_entrada text not null,
  hash_contenido text not null,
  entradas text[] not null default '{}',
  resultado_texto text not null,
  resultado jsonb not null,
  estado text not null default 'vigente' check (estado in ('vigente', 'obsoleto')),
  created_at timestamptz not null default now(),
  primary key (user_id, id)
);
create index if not exists idx_proyecto_artefactos_nodo on public.proyecto_artefactos (user_id, nodo, created_at desc);
alter table public.proyecto_artefactos enable row level security;

drop policy if exists "proyecto_artefactos_select_own" on public.proyecto_artefactos;
create policy "proyecto_artefactos_select_own" on public.proyecto_artefactos for select using ((select auth.uid()) = user_id);
drop policy if exists "proyecto_artefactos_insert_own" on public.proyecto_artefactos;
create policy "proyecto_artefactos_insert_own" on public.proyecto_artefactos for insert with check ((select auth.uid()) = user_id);
drop policy if exists "proyecto_artefactos_update_own" on public.proyecto_artefactos;
create policy "proyecto_artefactos_update_own" on public.proyecto_artefactos for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "proyecto_artefactos_delete_own" on public.proyecto_artefactos;
create policy "proyecto_artefactos_delete_own" on public.proyecto_artefactos for delete using ((select auth.uid()) = user_id);
