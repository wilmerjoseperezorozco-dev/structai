-- Segundo país del programa de replicabilidad internacional (StructAI ->
-- Ecuador, después de Perú): tabla de chunks verbatim de la norma
-- NEC-SE-DS "Peligro Sísmico, Diseño Sismo Resistente" (Norma Ecuatoriana
-- de la Construcción), espejo exacto de peru_e030_chunks/nsr10_chunks.
--
-- Base legal para citar el texto verbatim sin riesgo de derechos de
-- autor: el Código Orgánico de la Economía Social del Conocimiento, la
-- Creatividad y la Innovación (COESC+i / "Código Ingenios", 2016, norma
-- vigente que reemplazó a la Ley de Propiedad Intelectual) excluye del
-- derecho de autor "las disposiciones legales y reglamentarias, las
-- resoluciones judiciales y los actos, acuerdos, deliberaciones y
-- dictámenes de los organismos públicos ... y otros textos oficiales de
-- orden legislativo, administrativo o judicial". La NEC-SE-DS se aprobó
-- por Acuerdo Ministerial Nro. 0028 del MIDUVI (19-ago-2014), publicado
-- en el Registro Oficial Año II N° 319 (26-ago-2014) -- misma categoría
-- legal que NSR-10 (Colombia) y E.030 (Perú). Verificado 2026-08-25 con
-- dos fuentes independientes (Ley de Propiedad Intelectual Art. 10(b) +
-- confirmación de que el Código Ingenios retiene la misma exclusión), no
-- asumido por analogía con Perú -- la Decisión 351 de la Comunidad
-- Andina (marco regional compartido) NO trae esta exclusión en sí misma,
-- cada país la agrega en su legislación nacional.
--
-- Tabla separada de peru_e030_chunks/nsr10_chunks por la misma razón que
-- Perú quedó separado de Colombia: numeración de secciones incompatible
-- (NEC-SE-DS usa numeral.subnumeral arábigo, ej. "6.3.2", distinto de
-- E.030 "Capítulo.Artículo" y de NSR-10 "Título.Capítulo").

create table if not exists public.ecuador_nec_se_ds_chunks (
  id text primary key,
  capitulo text not null,
  seccion text,
  titulo text not null,
  texto text not null,
  embedding vector(384),
  created_at timestamptz default now()
);

alter table public.ecuador_nec_se_ds_chunks enable row level security;

create policy "public_read_ecuador_nec_se_ds_chunks"
  on public.ecuador_nec_se_ds_chunks
  for select
  to public
  using (true);

create policy "service_write_ecuador_nec_se_ds_chunks"
  on public.ecuador_nec_se_ds_chunks
  for all
  to service_role
  using (true);

create or replace function public.match_ecuador_nec_se_ds_chunks(
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
  from ecuador_nec_se_ds_chunks c
  where c.embedding is not null
    and (filter_caps is null or c.capitulo = any(filter_caps))
    and (1 - (c.embedding <=> query_embedding)) >= min_similarity
  order by c.embedding <=> query_embedding
  limit match_count;
end; $function$;
