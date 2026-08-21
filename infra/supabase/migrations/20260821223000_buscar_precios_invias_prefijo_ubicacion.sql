-- Fix real encontrado al probar con 43 provincias cargadas (Orinoquía + Caribe):
-- buscar_precios_invias() rankeaba solo por texto de la DESCRIPCIÓN de la
-- actividad, que es IDÉNTICA en las 43 provincias (mismo numeral INVIAS,
-- mismo texto en todo el país). Sin filtro de ubicación, una pregunta como
-- "precio de relleno SBG-50 en Atlántico" devolvía las primeras N filas por
-- orden arbitrario de empate -- en la práctica, precios de Meta/Arauca en
-- vez de Atlántico. El LLM, correctamente, se negó a inventar que esos
-- precios eran de Atlántico ("no tengo información específica") -- el bug
-- estaba en la recuperación de datos, no en la síntesis.
--
-- Fix: p_provincia_codigo ahora funciona como PREFIJO, no solo código exacto.
-- Pasar el código completo de 4 dígitos de una provincia (ej. '5001') sigue
-- filtrando a esa provincia exacta; pasar solo el código de 2 dígitos de un
-- departamento (ej. '08') filtra a TODAS sus provincias -- útil cuando la
-- pregunta menciona el departamento pero no la provincia específica.
create or replace function public.buscar_precios_invias(
  p_query text,
  p_provincia_codigo text default null,
  p_limit int default 10
)
returns table (
  numeral text,
  descripcion text,
  unidad text,
  provincia text,
  departamento text,
  periodo text,
  costo_directo_total numeric,
  relevancia real
)
language sql
stable
as $$
  select
    a.numeral,
    a.descripcion,
    a.unidad,
    p.provincia,
    p.departamento,
    c.periodo,
    c.costo_directo_total,
    ts_rank(to_tsvector('spanish', a.descripcion), websearch_to_tsquery('spanish', p_query))
      + similarity(a.descripcion, p_query) as relevancia
  from public.invias_actividad_costos c
  join public.invias_actividades a on a.numeral = c.numeral
  join public.invias_provincias p on p.codigo = c.provincia_codigo
  where
    (p_provincia_codigo is null or c.provincia_codigo like p_provincia_codigo || '%')
    and (
      to_tsvector('spanish', a.descripcion) @@ websearch_to_tsquery('spanish', p_query)
      or a.descripcion % p_query
    )
  order by relevancia desc
  limit p_limit;
$$;

comment on function public.buscar_precios_invias is
  'Busca actividades de INVIAS APU Regionalizados por texto libre. p_provincia_codigo filtra por PREFIJO: un código de provincia completo (4 dígitos, ej. 5001) filtra a esa provincia exacta; un código de departamento (2 dígitos, ej. 08) filtra a todas sus provincias. Devuelve el costo directo real publicado por INVIAS (sin AIU).';
