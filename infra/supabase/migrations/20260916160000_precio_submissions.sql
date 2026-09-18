-- Idea 4 del roadmap (base de precios distribuida / crowdsourcing), Fase 1:
-- solo el esquema + captura mínima de datos, SIN foto/QR/cifrado/incentivos
-- todavía. Idea 4 se PAUSÓ inmediatamente después de aplicar esta
-- migración (decisión del usuario, 2026-09-16) -- no hay app móvil ni
-- pantalla de captura construida todavía sobre esta tabla, queda lista
-- para cuando se retome.
--
-- foto_url queda nullable a propósito: subir la foto a Supabase Storage es
-- trabajo aparte (este proyecto hoy NO usa Storage en ningún lado, /detect
-- procesa imágenes en memoria sin persistirlas) -- la columna existe para
-- no tener que migrar el esquema otra vez cuando se conecte, pero no se
-- exige en el insert.
--
-- estado ('pendiente' por defecto): un envío crowdsourced NO debe
-- influenciar precios mostrados a otros usuarios sin revisión -- mismo
-- espíritu de control de calidad que ya motivó encontrar y limpiar datos
-- contaminados en apu_precios_referencia. La agregación (mediana, IQR,
-- "según N capturas") es Fase 2, cuando haya volumen real que agregar.
--
-- Sin política de UPDATE/DELETE para el usuario final -- un envío es
-- inmutable una vez creado (aproximación barata a "firma de transacción"
-- sin construir cifrado real todavía); la moderación (pendiente ->
-- aprobado/rechazado) la hace service_role, no el usuario.

create table if not exists public.precio_submissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  item_descripcion text not null check (char_length(trim(item_descripcion)) > 0),
  precio numeric not null check (precio > 0),
  unidad text not null default 'unidad',
  municipio text,
  foto_url text,
  fuente text not null default 'app_movil',
  estado text not null default 'pendiente' check (estado in ('pendiente', 'aprobado', 'rechazado')),
  created_at timestamptz not null default now()
);

alter table public.precio_submissions enable row level security;

create policy precio_submissions_select_own on public.precio_submissions
  for select using ((select auth.uid()) = user_id);
create policy precio_submissions_insert_own on public.precio_submissions
  for insert with check ((select auth.uid()) = user_id);

create index if not exists idx_precio_submissions_user_id on public.precio_submissions(user_id);
create index if not exists idx_precio_submissions_municipio on public.precio_submissions(municipio);
create index if not exists idx_precio_submissions_estado on public.precio_submissions(estado);
create index if not exists idx_precio_submissions_created on public.precio_submissions(created_at desc);

comment on table public.precio_submissions is
'Reportes de precio crowdsourced desde apps/native (idea 4 del roadmap, Fase 1 -- captura mínima sin foto/QR/cifrado/incentivos/agregación todavía). estado=pendiente hasta revisión -- no influye en precios mostrados sin moderación.';
