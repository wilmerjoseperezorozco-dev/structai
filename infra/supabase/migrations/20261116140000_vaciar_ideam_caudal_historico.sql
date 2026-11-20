-- ideam_caudal_historico (352.022 filas, ~49 MB) sale de Supabase para seguir en el plan gratuito (2026-11-16).
--
-- * La API ya no la lee: las comparaciones de caudal usan ideam_caudal_estadisticas_mes (11.310 filas), cargada en RAM
--   y verificada idéntica al recálculo desde el crudo (promedio, n, p90, mínimo y máximo: 0 diferencias).
-- * Respaldo: ideam_caudal_historico_2026-11-16.jsonl.gz (3,3 MB), sha256 7a412fee…52fe, en
--   C:/Users/wilme/dev/respaldos/supabase y OneDrive/Respaldos-StructAI/supabase. Conteo, md5 de los ids en orden, md5 de
--   codigo_estacion|fecha|nivel_aprobacion y suma de caudal_m3s (15 cifras, como float8::numeric) idénticos a la base.
-- * Los scripts fuera de línea (ENSO, anomalías, inundaciones Caribe) leen el respaldo con scripts/respaldo/leer_respaldo.py.
--   El cargador escribe a JSONL.gz salvo IDEAM_HISTORICO_A_SUPABASE=true.
--
-- Candado: solo vacía si la tabla es exactamente la que se respaldó. Si alguien cargó o cambió filas después del
-- respaldo, aborta y no borra nada.
do $$
declare
  n bigint;
  h text;
begin
  select count(*), md5(string_agg(id::text, ',' order by id)) into n, h from public.ideam_caudal_historico;
  if n <> 352022 or h <> '8a15be3ea2308df701b9efda45d4a3da' then
    raise exception 'ideam_caudal_historico cambió desde el respaldo (n=%, md5=%): no se vacía', n, h;
  end if;
end $$;

truncate table public.ideam_caudal_historico;

-- Restaurar: cargar el JSONL.gz del respaldo (columnas id, codigo_estacion, fecha, caudal_m3s, nivel_aprobacion).
