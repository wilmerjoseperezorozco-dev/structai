-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820130729
-- Nombre: crear_noticias_relevantes
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

create table public.noticias_relevantes (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  fuente text not null,
  link text not null unique,
  categoria text not null check (categoria in ('desastre', 'regulatoria')),
  fecha_publicacion timestamptz,
  resumen text,
  query_origen text,
  created_at timestamptz not null default now()
);

comment on table public.noticias_relevantes is
  'Noticias de Colombia relevantes para StructAI (desastres/sismos y normativa de construcción), vía Google News RSS. Solo titular+resumen+link, nunca el artículo completo (evita reproducir contenido con derechos de autor de los medios). Alimentado por noticias_colombia.actualizar_noticias(), corrido periódicamente por un scheduler en apps/api.';

alter table public.noticias_relevantes enable row level security;

create policy "noticias_lectura_publica" on public.noticias_relevantes
  for select using (true);

create index idx_noticias_categoria_fecha on public.noticias_relevantes (categoria, fecha_publicacion desc);
