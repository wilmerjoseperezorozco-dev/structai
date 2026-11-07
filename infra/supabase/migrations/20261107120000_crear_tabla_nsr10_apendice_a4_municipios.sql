-- Apéndice A-4 de la NSR-10 (Aa, Av, Ae, Ad y zona de amenaza sísmica de los municipios) extraído del PDF fuente
-- (NSR-10-191-218.pdf, páginas A-153 a A-174), con clave por código DANE.
--
-- IMPORTANTE (vigencia): es el TEXTO ORIGINAL del Decreto 926 de 2010. La NSR-10 fue modificada después por los decretos
-- 2525/2010, 092/2011, 340/2012, 945/2017, 2113/2019, 1711/2021 y otros; el Decreto 1711 de 2021, por ejemplo, trae un
-- anexo técnico que (según fuentes secundarias, aún sin verificar en el texto del anexo) cambia Supía (17777) a Aa 0,25.
-- Esta tabla NO incorpora esas modificaciones; la columna `vigencia` lo dice explícitamente.
--
-- Complementa a sgc_amenaza_sismica_municipios (valores servidos por el SGC, sin código DANE): permite contrastar ambas
-- fuentes y detectar diferencias. Fuente de la extracción: scripts/ingesta/nsr10/_ingest_apendice_a4_aa_av.py.

create table if not exists nsr10_apendice_a4_municipios (
  codigo text primary key,                    -- código DANE del municipio (5 dígitos)
  municipio text not null,
  departamento text,                          -- derivado del prefijo del código DANE
  aa double precision not null,
  av double precision not null,
  ae double precision not null,
  ad double precision not null,
  zona text not null check (zona in ('Baja', 'Intermedia', 'Alta')),
  pagina_reglamento integer,                  -- página A-xxx del reglamento
  vigencia text not null default 'texto original Decreto 926 de 2010; sin modificaciones posteriores incorporadas',
  extraido_en timestamptz not null default now()
);

alter table nsr10_apendice_a4_municipios enable row level security;

drop policy if exists "lectura publica" on nsr10_apendice_a4_municipios;
create policy "lectura publica" on nsr10_apendice_a4_municipios for select using (true);

comment on table nsr10_apendice_a4_municipios is
  'Apéndice A-4 de la NSR-10 por código DANE, extraído del PDF (texto original de 2010, sin las modificaciones de decretos posteriores). Contrastar siempre con el consolidado vigente antes de usar un valor para diseño.';
