-- Anexo II de la E.030 (Perú) -- listado oficial de zona sísmica por
-- región/provincia/distrito, referenciado desde el Artículo 10.1
-- ("El Anexo II contiene el listado de las provincias y distritos que
-- corresponden a cada zona"). Es una tabla de CONSULTA EXACTA (~1.874
-- distritos en todo el Perú), no texto narrativo -- por eso NO se carga
-- como peru_e030_chunks (RAG semántico), sino como tabla relacional
-- propia, mismo patrón que sisben_vulnerabilidad_vivienda_municipio o
-- sgc_amenaza_sismica_municipios en el lado colombiano: sin columna de
-- embedding, consulta por igualdad/ilike, no por similitud semántica.
--
-- PRUEBA DE CONCEPTO (2026-08-24): se carga solo Loreto y Tacna (las 2
-- regiones ya capturadas del PDF oficial del MVCS) para validar que el
-- diseño de la tabla funciona de punta a punta. Las ~23 regiones
-- restantes del Perú (~1.850 distritos) quedan pendientes para una
-- sesión futura -- decisión explícita del usuario, no un olvido: la
-- tabla completa son 40 páginas del PDF, transcribir todo en una sola
-- sesión tenía riesgo real de error de tipeo a esa escala.

create table if not exists public.peru_e030_zonificacion_distrital (
  id bigint generated always as identity primary key,
  region text not null,
  provincia text not null,
  distrito text not null,
  zona_sismica smallint not null check (zona_sismica between 1 and 4),
  ambito text,
  creado_en timestamptz not null default now(),
  unique (region, provincia, distrito)
);

create index if not exists idx_peru_e030_zonificacion_distrito
  on public.peru_e030_zonificacion_distrital (distrito);

create index if not exists idx_peru_e030_zonificacion_region
  on public.peru_e030_zonificacion_distrital (region);

alter table public.peru_e030_zonificacion_distrital enable row level security;

create policy "public_read_peru_e030_zonificacion_distrital"
  on public.peru_e030_zonificacion_distrital
  for select
  to public
  using (true);

create policy "service_write_peru_e030_zonificacion_distrital"
  on public.peru_e030_zonificacion_distrital
  for all
  to service_role
  using (true);
