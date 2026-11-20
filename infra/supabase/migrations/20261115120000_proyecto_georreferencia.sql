-- Georreferenciación oficial de un proyecto (issue #211). NO aplicada a producción: requiere aprobación.
-- Un proyecto se dibuja en coordenadas locales (E - E0, N - N0, H - H0) y aquí queda el punto base real en
-- EPSG:9377 (MAGNA-SIRGAS 2018 / Origen-Nacional, IGAC) para volver al sistema oficial sin pérdida.
-- Rotación y escala con la convención de IfcMapConversion:
--   E = e0 + escala·(x·cos(rot) − y·sin(rot));  N = n0 + escala·(x·sin(rot) + y·cos(rot));  H = h0 + z
-- Un registro por exportación (historial): el vigente es el más reciente por proyecto.
create table if not exists public.proyecto_georreferencia (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  proyecto_id uuid not null references public.proyectos(id) on delete cascade,
  epsg integer not null default 9377 check (epsg = 9377),
  e0 double precision not null check (e0 between 3500000 and 6500000),
  n0 double precision not null check (n0 between 500000 and 3500000),
  h0 double precision not null default 0,
  rotacion_rad double precision not null default 0 check (rotacion_rad between -6.2832 and 6.2832),
  escala double precision not null default 1 check (escala > 0.9 and escala < 1.1),
  fuente_punto_base text not null default 'centroide'
    check (fuente_punto_base in ('centroide', 'levantamiento', 'usuario', 'catastro', 'ifc')),
  version_conversor text not null,
  formato text check (formato in ('dxf', 'ifc', 'geojson', 'las', 'otro')),
  sha256_archivo text check (sha256_archivo is null or length(sha256_archivo) = 64),
  created_at timestamptz not null default now()
);
create index if not exists idx_proyecto_georreferencia_proyecto
  on public.proyecto_georreferencia (user_id, proyecto_id, created_at desc);
alter table public.proyecto_georreferencia enable row level security;

-- RLS: cada quien ve y escribe solo lo suyo, y solo sobre proyectos propios.
drop policy if exists "proyecto_georreferencia_select_own" on public.proyecto_georreferencia;
create policy "proyecto_georreferencia_select_own" on public.proyecto_georreferencia
  for select using ((select auth.uid()) = user_id);
drop policy if exists "proyecto_georreferencia_insert_own" on public.proyecto_georreferencia;
create policy "proyecto_georreferencia_insert_own" on public.proyecto_georreferencia
  for insert with check (
    (select auth.uid()) = user_id
    and exists (select 1 from public.proyectos p where p.id = proyecto_id and p.user_id = (select auth.uid()))
  );
drop policy if exists "proyecto_georreferencia_delete_own" on public.proyecto_georreferencia;
create policy "proyecto_georreferencia_delete_own" on public.proyecto_georreferencia
  for delete using ((select auth.uid()) = user_id);
-- Sin política de update: el historial no se edita; un punto base nuevo es un registro nuevo.
