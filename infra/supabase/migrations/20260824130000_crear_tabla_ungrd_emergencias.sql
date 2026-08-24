-- Registro real de eventos de emergencia (post-evento, no pronóstico)
-- reportados a la UNGRD, cruzando dos datasets oficiales de datos.gov.co
-- con esquemas distintos para el detalle de ayuda logística pero 20
-- campos de impacto en común -- se normaliza a esos campos comunes.
-- Ver issue #21 y project_structai_outreach_institucional.md para la
-- investigación completa (por qué NO se cargó "Alertas Hidrológicas",
-- que no es una tabla Socrata consultable).
--
-- Fuentes: 'UNGRD 2019-2022' (wwkg-r6te, 25.857 eventos) + 'UNGRD
-- 2023-2024' (rgre-6ak4, 16.036 eventos) -- cobertura real confirmada
-- 2019-01-01 a 2024-12-31, sin dataset 2025-2026 publicado todavía.
--
-- Esto es HISTÓRICO real de impacto (muertos, heridos, viviendas
-- destruidas/averiadas), NUNCA una alerta ni un pronóstico -- sirve para
-- responder "qué ha pasado antes en este municipio", no "qué va a pasar".

create table if not exists ungrd_emergencias (
  id bigint generated always as identity primary key,
  fecha date,
  departamento text,
  municipio text,
  codigo_municipio text,  -- DIVIPOLA, resuelto vía divipola.py cuando es posible
  evento text,
  fallecidos integer,
  heridos integer,
  desaparecidos integer,
  personas integer,
  familias integer,
  viviendas_destruidas integer,
  viviendas_averiadas integer,
  vias_averiadas integer,
  puentes_vehiculares integer,
  puentes_peatonales integer,
  acueducto integer,
  alcantarillado integer,
  centros_de_salud integer,
  centros_educativos integer,
  centros_comunitarios integer,
  hectareas double precision,
  otros_afectacion text,
  fuente text not null,  -- 'UNGRD 2019-2022' | 'UNGRD 2023-2024'
  creado_en timestamptz not null default now()
);
create index if not exists idx_ungrd_emergencias_municipio
  on ungrd_emergencias (upper(municipio), upper(departamento));
create index if not exists idx_ungrd_emergencias_fecha on ungrd_emergencias (fecha);
create index if not exists idx_ungrd_emergencias_evento on ungrd_emergencias (evento);

comment on table ungrd_emergencias is
  'Histórico real de eventos de emergencia reportados a la UNGRD (2019-2024, datos.gov.co) con su afectación real: fallecidos, heridos, viviendas destruidas/averiadas, infraestructura afectada. Es HISTÓRICO de lo ya ocurrido, nunca una alerta ni un pronóstico. Ver issue #21 del repo structai.';

alter table ungrd_emergencias enable row level security;
create policy "public_read_ungrd_emergencias" on ungrd_emergencias for select to public using (true);
