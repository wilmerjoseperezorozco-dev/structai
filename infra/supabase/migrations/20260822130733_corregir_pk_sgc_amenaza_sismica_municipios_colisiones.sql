-- Corrige un bug real encontrado al cargar esta tabla por primera vez: la
-- clave original (solo municipio_normalizado) pierde silenciosamente 86 de
-- 1.123 municipios porque 68 nombres se repiten en más de un departamento
-- (ej. Candelaria existe en Valle del Cauca Y Atlántico; Armenia existe en
-- Quindío Y Antioquia) -- el mismo bug ya vivía en el caché en memoria de
-- packages/construdata/sgc_amenaza_sismica.py, solo que ahí era invisible
-- (nunca se contó cuántos municipios entraban vs. cuántos reportaba el
-- servicio). Clave compuesta (municipio + departamento) para no perder
-- ninguno de los 1.123.

drop table if exists sgc_amenaza_sismica_municipios;

create table sgc_amenaza_sismica_municipios (
  municipio_normalizado text not null,   -- ver sgc_amenaza_sismica._normalizar()
  departamento_normalizado text not null,
  municipio text not null,
  departamento text,
  aa double precision,
  av double precision,
  ae double precision,
  ad double precision,
  zona text,
  longitud double precision,
  latitud double precision,
  actualizado_en timestamptz not null default now(),
  primary key (municipio_normalizado, departamento_normalizado)
);
create index idx_sgc_amenaza_municipio on sgc_amenaza_sismica_municipios (municipio_normalizado);

comment on table sgc_amenaza_sismica_municipios is
  'Catálogo nacional (1.123 municipios) de amenaza sísmica NSR-10 (Aa/Av/Ae/Ad/zona) del SGC, cargado una vez desde srvags.sgc.gov.co (endpoint no oficial, ver sgc_amenaza_sismica.py) para no depender de ese servicio en el camino crítico de cada respuesta. Clave compuesta municipio+departamento porque 68 nombres de municipio se repiten entre departamentos (Candelaria, Armenia, Bolívar, etc.). Recargar con scripts/ingesta/sgc_amenaza_sismica/cargar_municipios.py si el SGC actualiza valores.';
