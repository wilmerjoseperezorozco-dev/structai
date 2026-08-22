-- Persiste el dataset nacional de Unidades Físicas Homogéneas (UFH) de
-- suelo del IGAC/UPRA (datos.gov.co, resource fy2r-gwsd, 169.088 filas
-- verificadas en vivo 2026-08-22), hoy consultado en vivo por cada
-- pregunta (ver packages/construdata/igac_client.py). A diferencia del
-- caudal del IDEAM, este dato es esencialmente estático (taxonomía de
-- suelo no cambia con el tiempo) -- no hay serie temporal que calcular,
-- el único objetivo es no depender de una llamada HTTP externa por cada
-- pregunta y quedar resiliente ante rate-limits/caídas de datos.gov.co.
--
-- Geometría (the_geom, polígonos) NO se persiste: el uso real (contexto
-- de texto para el RAG) nunca la necesita, y agregarla infla la tabla sin
-- aportar valor -- mismo criterio que ya usa igac_client.py en su $select.

create table if not exists igac_suelos_ufh (
  id bigint primary key,  -- campo "consecutiv" del dataset origen (índice único de fila)
  municipio text not null,
  departamento text not null,
  cod_dane_municipio text,
  taxonomia text,
  textura text,
  pendiente text,
  drenaje text,
  inund text,
  profundi text,
  pedrego text,
  salinidad text,
  ph text,
  alt_msnm text,
  clase_ufh text,
  area_ha double precision,
  actualizado_en timestamptz not null default now(),
  -- Columnas generadas + índice normal en vez de un índice funcional sobre
  -- upper(): bug de rendimiento real encontrado al verificar la carga -- el
  -- cliente consulta con ILIKE (operador ~~*), que Postgres NUNCA reescribe
  -- como igualdad aunque el valor no tenga comodines, así que un índice
  -- funcional sobre upper() queda sin usar (verificado con EXPLAIN ANALYZE:
  -- Parallel Seq Scan sobre 169.088 filas, ~215ms). Con estas columnas +
  -- igualdad exacta en igac_client.py, la misma consulta baja a ~0.4ms.
  municipio_norm text generated always as (upper(municipio)) stored,
  departamento_norm text generated always as (upper(departamento)) stored
);
create index if not exists idx_igac_suelos_municipio_depto_norm
  on igac_suelos_ufh (municipio_norm, departamento_norm);

comment on table igac_suelos_ufh is
  'Dataset nacional de Unidades Físicas Homogéneas de suelo (IGAC/UPRA, datos.gov.co resource fy2r-gwsd), cargado una vez para no depender de una llamada HTTP externa en cada pregunta del chat. Ver packages/construdata/igac_client.py e scripts/ingesta/igac_suelos/cargar_suelos_ufh.py. Referencia general por zona, NUNCA reemplaza el estudio geotécnico NSR-10 Título H.';
