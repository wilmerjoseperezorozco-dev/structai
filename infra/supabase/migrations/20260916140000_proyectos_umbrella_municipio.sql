-- Prepara el esquema para el "caso de uso batch de noche" (idea 2 del
-- roadmap de costos, discutido 2026-09-16): antes de diseñar CUALQUIER job
-- nocturno que cruce precios+norma+clima por proyecto, se verificó con SQL
-- directo que hoy no hay ningún dato real sobre el que correrlo --
-- aquai_proyectos/geopot_proyectos/vias_proyectos/gerencia_proyectos tienen
-- 0 filas cada una (piloto de 8 usuarios, 47 consultas de chat, 11
-- apu_calculations, cero proyectos guardados). El batch en sí queda
-- explícitamente pospuesto hasta que haya uso real -- esta migración solo
-- prepara el esquema para cuando llegue ese momento, cerrando 2 huecos
-- estructurales reales encontrados en la misma auditoría:
--
--   1. Ninguna de las 4 tablas *_proyectos tiene ubicación -- sin eso no se
--      puede cruzar un proyecto con SGC (amenaza sísmica por municipio,
--      ver sgc_amenaza_sismica.py) ni con IDEAM (clima). Se agrega
--      `municipio text` UNA sola vez, en la tabla nueva de abajo -- no
--      duplicado en cada tabla de motor, para no tener 4 copias de "la
--      misma" ubicación que puedan quedar desincronizadas.
--   2. Los 4 motores no comparten ningún identificador de proyecto -- si
--      un usuario diseña el acueducto (AquAI) y la gerencia (Gerencia) del
--      MISMO edificio, hoy quedan como 2 filas sin ningún vínculo. Se
--      agrega `proyecto_id` a cada tabla de motor, apuntando a la nueva
--      tabla paraguas `public.proyectos`.
--
-- Convención de nombres de columna (`municipio` texto libre, sin FK a un
-- catálogo de municipios) igual a la ya usada en
-- sgc_amenaza_sismica_municipios -- no se inventa un esquema nuevo de
-- ubicación, se reutiliza el que ya existe y ya sabe matchear contra texto
-- libre (_normalizar() en sgc_amenaza_sismica.py). El issue #17 (resolver
-- único DIVIPOLA) sigue siendo trabajo futuro aparte, no se adelanta acá.

-- ─── Tabla paraguas: "un proyecto" cruzando motores ───────────────────────
create table if not exists public.proyectos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  nombre text not null,
  -- Texto libre, mismo criterio que sgc_amenaza_sismica_municipios --
  -- nullable porque un usuario puede crear el proyecto antes de fijar la
  -- ubicación, o nunca necesitarla si no usa los motores que la requieren.
  municipio text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.proyectos enable row level security;

-- WITH CHECK en la política de UPDATE desde el día 1 -- el repaso de RLS
-- del 2026-08-25 (ver 20260825204806_agregar_with_check_faltante_en_
-- update_own.sql) ya encontró y cerró este mismo hueco en otras 4 tablas;
-- no se repite el error acá.
create policy proyectos_select_own on public.proyectos
  for select using ((select auth.uid()) = user_id);
create policy proyectos_insert_own on public.proyectos
  for insert with check ((select auth.uid()) = user_id);
create policy proyectos_update_own on public.proyectos
  for update using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy proyectos_delete_own on public.proyectos
  for delete using ((select auth.uid()) = user_id);

create index if not exists idx_proyectos_user_id on public.proyectos(user_id);
create index if not exists idx_proyectos_municipio on public.proyectos(municipio);

comment on table public.proyectos is
'Tabla paraguas que agrupa los proyectos de un mismo usuario en los 4 motores de dominio (aquai/geopot/vias/gerencia) bajo un mismo sitio físico + ubicación. Vínculo opcional (proyecto_id nullable en cada tabla de motor) -- un usuario puede seguir usando cada motor sin nunca crear un registro acá.';

-- ─── Vínculo opcional en cada motor (FK dura donde no hay restricción de
-- separabilidad; sin FK en aquai_proyectos, ver abajo) ─────────────────────

alter table public.geopot_proyectos
  add column if not exists proyecto_id uuid references public.proyectos(id) on delete set null;
create index if not exists idx_geopot_proyecto_id on public.geopot_proyectos(proyecto_id);

alter table public.vias_proyectos
  add column if not exists proyecto_id uuid references public.proyectos(id) on delete set null;
create index if not exists idx_vias_proyecto_id on public.vias_proyectos(proyecto_id);

alter table public.gerencia_proyectos
  add column if not exists proyecto_id uuid references public.proyectos(id) on delete set null;
create index if not exists idx_gerencia_proyecto_id on public.gerencia_proyectos(proyecto_id);

-- aquai_proyectos: se agrega la MISMA columna pero SIN foreign key --
-- 20260712130553_aquai_proyectos.sql documenta explícitamente que este
-- motor está "diseñado para ser separable... sin foreign keys hacia
-- tablas propias de StructAI (solo hacia auth.users)", para que un futuro
-- `pg_dump -t 'aquai_*'` se lleve el módulo completo sin arrastrar nada
-- más. Una FK a public.proyectos rompería esa garantía a propósito
-- documentada; un uuid suelto (sin CHECK/REFERENCES) preserva la
-- separabilidad del dump y de todas formas permite al código de
-- aplicación unir por proyecto_id cuando haga falta.
alter table public.aquai_proyectos
  add column if not exists proyecto_id uuid;
create index if not exists idx_aquai_proyecto_id on public.aquai_proyectos(proyecto_id);

comment on column public.aquai_proyectos.proyecto_id is
'Vínculo opcional a public.proyectos.id -- SIN foreign key a propósito (ver 20260712130553_aquai_proyectos.sql, este motor está diseñado para ser separable). Integridad referencial garantizada por la capa de aplicación, no por la base de datos.';
