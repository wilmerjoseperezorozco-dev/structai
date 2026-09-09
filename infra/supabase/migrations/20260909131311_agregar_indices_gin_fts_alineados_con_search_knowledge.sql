-- Hallazgo real al medir latencia de search_knowledge() para verificar la Fase 3
-- (HNSW): la rama léxica (CTE 'lex') calcula to_tsvector('spanish', contenido) sobre
-- cada fila del UNION ALL, pero el único GIN existente (idx_chunks_fts) está sobre
-- to_tsvector('spanish', texto || ' ' || titulo) -- expresión distinta, así que
-- Postgres NO puede usarlo y hace Parallel Seq Scan completo en las 3 tablas
-- (~1.4s medido, el mayor costo real de la función, más que la parte semántica).
-- Se crean índices GIN que SÍ calzan exacto con la expresión real de la función.
create index if not exists idx_nsr10_chunks_fts_contenido
  on public.nsr10_chunks using gin (to_tsvector('spanish', texto));

create index if not exists idx_ntc_chunks_fts_contenido
  on public.ntc_chunks using gin (to_tsvector('spanish', contenido));

create index if not exists idx_motor_chunks_fts_contenido
  on public.motor_chunks using gin (to_tsvector('spanish', contenido));

-- Verificado en vivo con EXPLAIN ANALYZE contra el cuerpo real de search_knowledge():
-- la rama léxica sola bajó de Parallel Seq Scan / ~1.4s a Bitmap Index Scan / ~0.6s,
-- y la función completa (embedding real + texto real) bajó de 3.803s a 2.387s
-- (~37% más rápida) en la misma prueba, antes/después, misma consulta.
