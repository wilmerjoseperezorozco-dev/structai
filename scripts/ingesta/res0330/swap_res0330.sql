-- Intercambio atómico de la Res. 0330/2017: las filas nuevas (motor='aquai_stage') reemplazan a las actuales.
-- NO ejecutar sin: (1) respaldo hecho, (2) filas stage verificadas con retrieval, (3) aprobación del usuario.
-- Una sola transacción: si algo falla, no queda un hueco de normativa (lección del bug "delete antes de upsert", ver CLAUDE.md).
begin;

-- Debe haber filas stage; si no, abortar para no dejar la norma vacía.
do $$
begin
  if (select count(*) from motor_chunks where motor = 'aquai_stage' and norma_id = 'f4637666-6f95-4abc-85b8-1d64af5f52bb') < 250 then
    raise exception 'Faltan filas stage de la Res. 0330; abortado';
  end if;
end $$;

delete from motor_chunks where motor = 'aquai' and norma_id = 'f4637666-6f95-4abc-85b8-1d64af5f52bb';
update motor_chunks set motor = 'aquai' where motor = 'aquai_stage' and norma_id = 'f4637666-6f95-4abc-85b8-1d64af5f52bb';

update normas_registro
   set cadena_modificaciones = 'completa',
       notas_vigencia = coalesce(notas_vigencia, '') || E'\n[2026-11] Re-ingestada con el texto consolidado del Gestor Normativo de la CRA (265 articulos; Res. 799 y 908 de 2021 incorporadas). Cadena verificada en la pagina del Ministerio de Vivienda: 0650/2017, 0799/2021, 0908/2021, 0548/2022. Sin instrumentos posteriores listados; no se hizo busqueda exhaustiva en el Diario Oficial.',
       updated_at = now()
 where codigo = 'RES-0330-2017';

commit;
