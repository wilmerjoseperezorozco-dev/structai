-- Replica el registro de cadenas de modificación (normas_modificaciones) a otras normas del corpus y marca en normas_registro
-- qué normas tienen su cadena revisada. Estado honesto: todo lo de abajo viene de RESÚMENES WEB (búsqueda del 2026-11-07), no del
-- texto oficial; ninguna fila se marca 'texto_verificado'. 62 de las 64 normas del registro quedan en 'no_revisada'.
--
-- Hallazgos de esta pasada:
--  * Ley 80/1993: la nota vigente del registro cita solo las leyes 1150/2007 y 1474/2011; hay además 2160/2021, 2195/2022 y 2294/2023.
--  * CCP-14: la fecha de expedición no estaba; la Resolución 108 de 2015 del Ministerio de Transporte la adopta como CCP-2014.
--  * RAS: existe la Res. 0650/2017 (transitorio hasta 31-12-2019), la 0799/2021 (79 artículos modificados) y la 0548/2022 (transitorio).
--    NO se encontraron las resoluciones «0661 de 2019» y «0550 de 2021» que se habían supuesto: no se registran.

alter table normas_registro
  add column if not exists cadena_modificaciones text not null default 'no_revisada'
  check (cadena_modificaciones in ('no_revisada', 'parcial', 'completa'));

comment on column normas_registro.cadena_modificaciones is 'Estado de la revisión de la cadena de decretos/resoluciones que modifican la norma (ver tabla normas_modificaciones).';

update normas_registro set cadena_modificaciones = 'parcial'
 where codigo like 'NSR10-TITULO-%' or codigo in ('RES-0330-2017', 'LEY-80-1993', 'CCP-14', 'DECRETO-1072-2015-CAP6-SGSST');

update normas_registro set fecha_expedicion = '2015-01-26',
  notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Fecha tomada de la Resolución 108 de 2015 (Min. Transporte), que según un resumen web actualiza el Código Colombiano de Diseño Sísmico de Puentes y lo adopta como CCP-2014; sin verificar en el texto oficial. Un proyecto de resolución de 2026 modificaría la Sección 13 (barandas); no se confirmó que se haya expedido.'
 where codigo = 'CCP-14' and fecha_expedicion is null;

update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] La nota anterior omitía modificaciones posteriores: según resúmenes web también la modifican la Ley 2160 de 2021, la Ley 2195 de 2022 y la Ley 2294 de 2023 (sin verificar en texto oficial). Los chunks del corpus pueden no reflejarlas.'
 where codigo = 'LEY-80-1993' and notas_vigencia not like '%2160%';

insert into normas_modificaciones (norma, decreto, fecha, objeto, toca_apendice_a4, estado_verificacion, fuente_verificacion) values
  ('RAS', 'Resolución 0330 de 2017', '2017-06-08', 'Adopta el RAS y deroga las resoluciones 1096/2000, 0424/2001, 0668/2003, 1459/2005 y 2320/2009 (otra fuente suma la 1447/2005; el registro ya la lista como derogada).', 'no', 'resumen_web_sin_verificar', 'Resúmenes web y cuadro de evolución normativa del Ministerio de Vivienda (2022).'),
  ('RAS', 'Resolución 0650 de 2017', null, 'Artículo transitorio: proyectos en planeación, diseño o construcción podían aplicar la Resolución 1096/2000 hasta el 31-12-2019.', 'no', 'resumen_web_sin_verificar', 'Resumen web; texto no leído.'),
  ('RAS', 'Resolución 0799 de 2021', '2021-12-09', 'Modifica la Resolución 0330 de 2017 (79 artículos modificados según un anexo del Ministerio).', 'no', 'resumen_web_sin_verificar', 'Resumen web; texto no leído. Los chunks del RAS 2000/0330 del corpus pueden no reflejar estas modificaciones.'),
  ('RAS', 'Resolución 0548 de 2022', null, 'Adiciona un artículo transitorio a la Resolución 799 de 2021.', 'no', 'resumen_web_sin_verificar', 'Resumen web (página del Ministerio de Vivienda); fecha exacta no obtenida.'),
  ('Ley 80 de 1993', 'Ley 1150 de 2007', '2007-07-16', 'Medidas de eficiencia y transparencia; modifica la Ley 80. Su normograma indica que fue modificada por la Ley 2294 de 2023.', 'no', 'resumen_web_sin_verificar', 'Resumen web y normogramas.'),
  ('Ley 80 de 1993', 'Ley 1474 de 2011', '2011-07-12', 'Estatuto Anticorrupción.', 'no', 'resumen_web_sin_verificar', 'Resumen web (D.O. 48.128).'),
  ('Ley 80 de 1993', 'Ley 2160 de 2021', null, 'Modifica la Ley 80 de 1993 y la Ley 1150 de 2007.', 'no', 'resumen_web_sin_verificar', 'Resumen web; texto no leído.'),
  ('Ley 80 de 1993', 'Ley 2195 de 2022', null, 'Transparencia, prevención y lucha contra la corrupción; su art. 53 obliga a publicar la actividad contractual de entidades de régimen excepcional en SECOP II desde el 18-07-2022.', 'no', 'resumen_web_sin_verificar', 'Resumen web; texto no leído.'),
  ('Ley 80 de 1993', 'Ley 2294 de 2023', null, 'Plan Nacional de Desarrollo 2022-2026; según un normograma modifica la Ley 1150 de 2007.', 'no', 'resumen_web_sin_verificar', 'Resumen web; texto no leído.'),
  ('CCP-14', 'Resolución 108 de 2015 (Min. Transporte)', '2015-01-26', 'Actualiza el Código Colombiano de Diseño Sísmico de Puentes y lo adopta como CCP-2014.', 'no', 'resumen_web_sin_verificar', 'Resumen web; el PDF del corpus está escaneado sin capa de texto.'),
  ('CCP-14', 'Proyecto de resolución 2026 (Min. Transporte)', null, 'Modificaría la Sección 13 (barandas); es un proyecto, no se confirmó su expedición.', 'no', 'resumen_web_sin_verificar', 'Archivo con prefijo «pr_» en un repositorio de proyectos de norma.'),
  ('SG-SST', 'Decreto 052 de 2017', null, 'Modifica el artículo 2.2.4.6.37 del Decreto 1072 de 2015 (modificación puntual).', 'no', 'resumen_web_sin_verificar', 'Presentación de actualización normativa; fecha no obtenida.'),
  ('SG-SST', 'Resolución 0312 de 2019', null, 'Estándares mínimos del SG-SST; deroga la Resolución 1111 de 2017.', 'no', 'resumen_web_sin_verificar', 'Resúmenes web; fecha no obtenida.')
on conflict (norma, decreto) do nothing;
