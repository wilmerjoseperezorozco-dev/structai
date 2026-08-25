-- Primer paso de replicabilidad internacional (StructAI -> Perú): tabla de
-- chunks verbatim de la norma E.030 "Diseño Sismorresistente" (Reglamento
-- Nacional de Edificaciones, Perú), espejo exacto de nsr10_chunks.
--
-- Base legal para citar el texto verbatim sin riesgo de derechos de autor:
-- Art. 9(b) del Decreto Legislativo N° 822 (Ley sobre el Derecho de Autor
-- de Perú) excluye explícitamente "los textos oficiales de carácter
-- legislativo, administrativo o judicial" de la protección de copyright.
-- La E.030 se aprobó por Decreto Supremo N° 011-2006-VIVIENDA (modificado
-- por R.M. N° 355-2018-VIVIENDA), publicado en El Peruano -- misma
-- categoría legal que la NSR-10 en Colombia. Verificado 2026-08-24, no
-- asumido.
--
-- No se reutiliza nsr10_chunks con un campo "pais" porque mezclaría dos
-- normas con numeración de artículos incompatible (NSR-10 usa
-- Título.Capítulo, ej. "D.3.4"; E.030 usa Capítulo.Artículo.Numeral, ej.
-- "3.1") bajo la misma función de búsqueda -- tabla separada, mismo
-- patrón, evita falsos positivos de similitud semántica entre corpus de
-- países distintos hasta que haya una razón real para unificarlos.

create table if not exists public.peru_e030_chunks (
  id text primary key,
  capitulo text not null,
  seccion text,
  titulo text not null,
  texto text not null,
  embedding vector(384),
  created_at timestamptz default now()
);

alter table public.peru_e030_chunks enable row level security;

create policy "public_read_peru_e030_chunks"
  on public.peru_e030_chunks
  for select
  to public
  using (true);

create policy "service_write_peru_e030_chunks"
  on public.peru_e030_chunks
  for all
  to service_role
  using (true);

-- Espejo de match_nsr10_chunks -- mismo contrato (query_embedding,
-- match_count, filter_caps, min_similarity), search_path fijo por la
-- misma razón de seguridad ya aplicada hoy a las 11 tablas públicas
-- (fix(security): activar RLS + fijar search_path, commit del mismo día).
create or replace function public.match_peru_e030_chunks(
  query_embedding vector,
  match_count integer default 5,
  filter_caps text[] default null::text[],
  min_similarity double precision default 0.25
)
returns table(id text, capitulo text, seccion text, titulo text, texto text, similarity double precision)
language plpgsql
set search_path to 'public', 'pg_catalog', 'extensions'
as $function$
begin
  return query
  select c.id, c.capitulo, c.seccion, c.titulo, c.texto,
         (1 - (c.embedding <=> query_embedding))::float as similarity
  from peru_e030_chunks c
  where c.embedding is not null
    and (filter_caps is null or c.capitulo = any(filter_caps))
    and (1 - (c.embedding <=> query_embedding)) >= min_similarity
  order by c.embedding <=> query_embedding
  limit match_count;
end; $function$;
