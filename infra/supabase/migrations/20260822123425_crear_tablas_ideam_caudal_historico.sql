-- Tablas para el análisis estadístico de caudal de ríos del IDEAM (contexto
-- de riesgo de inundación por anomalía histórica, NUNCA una alerta oficial
-- -- eso es responsabilidad exclusiva del IDEAM/UNGRD). Ver
-- packages/construdata/ideam_client.py y scripts/ingesta/ideam_caudal/.
--
-- Diseño: el dato "de ahora" se sigue trayendo EN VIVO del bucket S3
-- público del IDEAM (más fresco que cualquier snapshot cargado aquí). Lo
-- que sí vale la pena cargar una vez es el HISTÓRICO completo (para
-- recalcular estadísticas si cambia el método más adelante) y las
-- ESTADÍSTICAS por mes calendario derivadas de él (lo que realmente
-- responde "¿es normal este caudal para esta época del año?").

create table if not exists ideam_estaciones_caudal (
  codigo text primary key,  -- 10 dígitos, zfilled (ver bug real documentado en ideam_client.py)
  nombre text,
  corriente text,           -- nombre del río
  municipio text,
  departamento text,
  categoria text,           -- Limnimétrica / Limnigráfica
  estado text,              -- Activa / Suspendida / etc. (tal como lo reporta IDEAM)
  latitud double precision,
  longitud double precision,
  altitud numeric,
  actualizado_en timestamptz not null default now()
);

create table if not exists ideam_caudal_historico (
  id bigint generated always as identity primary key,
  codigo_estacion text not null references ideam_estaciones_caudal(codigo) on delete cascade,
  fecha date not null,
  caudal_m3s double precision,
  nivel_aprobacion text,   -- Preliminar / En revisión / Definitivo -- un dato Preliminar puede cambiar
  unique (codigo_estacion, fecha)
);
create index if not exists idx_ideam_caudal_historico_estacion_fecha
  on ideam_caudal_historico (codigo_estacion, fecha);

create table if not exists ideam_caudal_estadisticas_mes (
  codigo_estacion text not null references ideam_estaciones_caudal(codigo) on delete cascade,
  mes smallint not null check (mes between 1 and 12),
  promedio_m3s double precision,
  desviacion_m3s double precision,
  p10_m3s double precision,
  p90_m3s double precision,
  minimo_m3s double precision,
  maximo_m3s double precision,
  n_observaciones integer not null,
  primary key (codigo_estacion, mes)
);

comment on table ideam_caudal_historico is
  'Serie histórica real de caudal medio mensual (m³/s) por estación hidrológica del IDEAM, descargada del bucket S3 público (datos.ideam.gov.co/s3-estacionesideam). Fuente de verdad para recalcular ideam_caudal_estadisticas_mes -- nunca editar a mano.';
comment on table ideam_caudal_estadisticas_mes is
  'Estadísticas (promedio/desviación/percentiles) de caudal por estación y mes calendario (1-12), calculadas a partir de ideam_caudal_historico. Se usa para comparar el caudal ACTUAL (siempre consultado en vivo, nunca desde esta tabla) contra lo típico de ese río en esa época del año -- señal estadística de anomalía, NUNCA una alerta oficial de inundación.';
