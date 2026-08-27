-- Bug de rendimiento real encontrado al verificar la carga: el índice
-- funcional (upper(municipio), upper(departamento)) NUNCA se usaba porque
-- el cliente Python consulta con ILIKE (operador ~~*), que Postgres no
-- reescribe como igualdad aunque el valor no tenga comodines -- cada
-- consulta hacía Parallel Seq Scan sobre 169.088 filas (~215ms server-side,
-- verificado con EXPLAIN ANALYZE). Se reemplaza por columnas generadas
-- (mayúsculas, sin necesidad de normalizar tildes -- el dataset ya las
-- trae consistentes, ver igac_client.py) + índice btree normal, y el
-- cliente pasa a usar igualdad exacta sobre esas columnas.

drop index if exists idx_igac_suelos_municipio_depto;

alter table igac_suelos_ufh
  add column if not exists municipio_norm text generated always as (upper(municipio)) stored,
  add column if not exists departamento_norm text generated always as (upper(departamento)) stored;

create index if not exists idx_igac_suelos_municipio_depto_norm
  on igac_suelos_ufh (municipio_norm, departamento_norm);
