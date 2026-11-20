-- Vacía invias_actividad_insumos (619.920 filas, 154 MB = 31 % de la base; 6 lecturas por índice desde julio) para
-- seguir en el plan gratuito de Supabase. Pedido por el usuario el 2026-11-16.
-- Respaldo verificado (conteo, md5 de los ids en orden y sumas exactas de las columnas numeric):
--   invias_actividad_insumos_2026-11-16.jsonl.gz  sha256 ee88ba8867b76f113cf4ddf22d9152db6a6598964adecfc8131bf9fda8414a38
--   (scripts/respaldo/respaldar_tabla.py; lectura: scripts/respaldo/leer_respaldo.py)
-- Se conserva la tabla (esquema, FKs, RLS) vacía: los scripts que la usaban leen el respaldo.
-- Candado: solo vacía si la tabla sigue idéntica a lo respaldado; si no, aborta sin tocar nada.
do $$
declare n bigint; h text;
begin
  select count(*), md5(string_agg(id::text, ',' order by id)) into n, h from public.invias_actividad_insumos;
  if n <> 619920 or h <> 'd574b06b06bdfbda987328960e887eb4' then
    raise exception 'invias_actividad_insumos cambió desde el respaldo (n=%, md5=%): no se vacía', n, h;
  end if;
end $$;
truncate table public.invias_actividad_insumos;
