-- Persiste el catálogo nacional de amenaza sísmica NSR-10 por municipio del
-- SGC (Servicio Geológico Colombiano), hoy solo cacheado en memoria del
-- proceso y re-descargado en cada arranque en frío desde un endpoint NO
-- documentado, HTTP (no HTTPS), fuera del dominio soportado de datos.sgc.gov.co
-- (srvags.sgc.gov.co) -- ver packages/construdata/sgc_amenaza_sismica.py,
-- que advierte explícitamente "puede cambiar o caerse sin aviso".
--
-- A diferencia del histórico de caudal del IDEAM, este NO es un dato que
-- cambie con el tiempo (Aa/Av de un municipio son fijos según NSR-10) --
-- por eso una sola tabla de referencia (sin serie temporal) es suficiente.
-- El objetivo es sacar el endpoint frágil del camino crítico: la app debe
-- poder responder con este dato aunque srvags.sgc.gov.co esté caído.
--
-- Clave compuesta (municipio + departamento), NO solo municipio: bug real
-- encontrado al cargar esta tabla por primera vez (2026-08-22) -- 68
-- nombres de municipio se repiten en más de un departamento (Candelaria
-- existe en Valle del Cauca Y Atlántico; Armenia existe en Quindío Y
-- Antioquia; etc.), y una clave por nombre solo perdía silenciosamente 86
-- de los 1.123 municipios. El mismo bug vivía sin detectar en el caché en
-- memoria de sgc_amenaza_sismica.py (nunca se había contado cuántos
-- municipios entraban vs. cuántos reporta el servicio).

create table if not exists sgc_amenaza_sismica_municipios (
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
create index if not exists idx_sgc_amenaza_municipio
  on sgc_amenaza_sismica_municipios (municipio_normalizado);

comment on table sgc_amenaza_sismica_municipios is
  'Catálogo nacional (1.123 municipios) de amenaza sísmica NSR-10 (Aa/Av/Ae/Ad/zona) del SGC, cargado una vez desde srvags.sgc.gov.co (endpoint no oficial, ver sgc_amenaza_sismica.py) para no depender de ese servicio en el camino crítico de cada respuesta. Clave compuesta municipio+departamento porque 68 nombres de municipio se repiten entre departamentos (Candelaria, Armenia, Bolívar, etc.). Recargar con scripts/ingesta/sgc_amenaza_sismica/cargar_municipios.py si el SGC actualiza valores.';
