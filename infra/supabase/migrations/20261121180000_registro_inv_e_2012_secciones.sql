-- #295: registro de las secciones de Normas de Ensayo INVIAS 2012 que faltaban (100, 400, 600, 700-800).
-- Edición 2012 adoptada por la Resolución 1375 de 2014 del Ministerio de Transporte; reemplaza en su totalidad
-- la Resolución 3290 de 2007 (Introducción I.1.1 del manual). La Res. 2451 de 2022 añadió INV E-631-22, 632-22
-- y 826-22 (ya registradas); el extractor omite esos números en la edición 2012.
-- Solo metadatos: los chunks los carga scripts/ingesta/normas_ensayo/ingest_normas_ensayo_secciones.py.
insert into normas_registro (codigo, nombre_completo, entidad_emisora, tipo, fecha_expedicion, estado_vigencia,
                             fuente_drive_id, notas_vigencia, cadena_modificaciones, pais)
select v.codigo, v.nombre, 'INVIAS', 'otro', date '2012-01-01', 'vigente', v.drive, v.notas, 'parcial', 'CO'
from (values
  ('SECCION-100-ENSAYO-2012', 'Normas de Ensayo de Materiales para Carreteras — Sección 100: Suelos',
   '1QoZe1oTA8r9Y26JDtnt2jBEmaTt9P7f5', 'Edición 2012, adoptada por la Resolución 1375 de 2014; reemplaza en su totalidad las normas de la Resolución 3290 de 2007.'),
  ('SECCION-400-ENSAYO-2012', 'Normas de Ensayo de Materiales para Carreteras — Sección 400: Concreto hidráulico',
   '1OUmuy4Bxm9m2lzkrfTVGkVmHP5AMj3e2', 'Edición 2012, adoptada por la Resolución 1375 de 2014; reemplaza en su totalidad las normas de la Resolución 3290 de 2007.'),
  ('SECCION-600-ENSAYO-2012', 'Normas de Ensayo de Materiales para Carreteras — Sección 600: Estabilización de suelos',
   '1_eOw1jYWUw6N5GOm1REBoW3A_QCdnOoo', 'Edición 2012, adoptada por la Resolución 1375 de 2014. En la edición 2007 las estabilizaciones eran la Sección 800. INV E-631-22 y 632-22 (Res. 2451 de 2022) se registran aparte.'),
  ('SECCION-700-800-ENSAYO-2012', 'Normas de Ensayo de Materiales para Carreteras — Secciones 700 y 800: Materiales y mezclas asfálticas y prospección de pavimentos',
   '17LDsHfZeFA2eSz_PzchGi56zKi5hyxvd', 'Edición 2012, adoptada por la Resolución 1375 de 2014; dos PDF (primera parte y segunda parte mod. 2013-11-15, Drive 1L6oZDQbK82cUva2cP2VYMd3G_JeppNqZ). INV E-826-22 (Res. 2451 de 2022) se registra aparte.')
) as v(codigo, nombre, drive, notas)
where not exists (select 1 from normas_registro r where r.codigo = v.codigo);

update normas_registro
   set notas_vigencia = notas_vigencia || E'\n[2026-11] Adoptada por la Resolución 1375 de 2014 del Ministerio de Transporte.',
       updated_at = now()
 where codigo in ('SECCION-200-ENSAYO-2012', 'SECCION-300-ENSAYO-2012')
   and notas_vigencia not like '%1375 de 2014%';
