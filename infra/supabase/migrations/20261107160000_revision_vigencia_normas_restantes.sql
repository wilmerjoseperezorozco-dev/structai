-- Revisión de vigencia de las normas restantes del registro (2026-11-07). TODO lo que sigue sale de búsquedas web (resúmenes), no del
-- texto oficial; cada nota lo dice. Cambios de estado SOLO cuando hay dos fuentes coherentes o la fuente es el propio organismo.
--  * ISO 19011:2011 pasa a derogada_total: la edición ISO 19011:2018 la cancela y reemplaza (varias fuentes coherentes).
--  * ISO 9001:2015, 14001:2015 y 27001:2022: se mantienen vigentes con nota (hay edición nueva o enmienda 2024).
--  * Res. 2743 de 2026 (INVIAS): no se encontró en la búsqueda; se anota que el número puede ser erróneo.
--  * Falta en el corpus la Resolución 4561 de 2022 (Especificaciones Generales de Construcción de Carreteras): se registra la cadena.

alter table normas_registro drop constraint if exists normas_registro_cadena_modificaciones_check;
alter table normas_registro add constraint normas_registro_cadena_modificaciones_check
  check (cadena_modificaciones in ('no_revisada', 'parcial', 'completa', 'no_aplica'));

-- Estado
update normas_registro set estado_vigencia = 'derogada_total',
  notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Superada: la tercera edición ISO 19011:2018 cancela y reemplaza a esta edición (varias fuentes coherentes); hay una cuarta edición en desarrollo prevista para 2026 (sin verificar). No citar la edición 2011 como vigente.'
 where codigo = 'ISO-19011-2011' and estado_vigencia = 'vigente';

-- Notas (se agregan al final, con fecha)
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Según fuentes web, ISO anunció la edición ISO 9001:2026 (publicación prevista el 16-09-2026; transición de tres años hasta 2029, sujeta a confirmación). Verificar en iso.org antes de citar la 2015 como la última edición.' where codigo = 'ISO-9001-2015';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Existe la Enmienda 1:2024 (acción climática) publicada según el registro de ISO; esta ficha no la incorpora.' where codigo = 'ISO-14001-2015';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Existe la Enmienda 1:2024 (acción climática, cláusulas 4.1 y 4.2) según catálogos de normas; esta ficha no la incorpora.' where codigo = 'ISO-27001-2022';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Edición superada internacionalmente: ACI publicó ACI CODE-318-25 (impresa el 09-07-2025), primera revisión importante desde ACI 318-19. En Colombia el texto vinculante es el Título C de la NSR-10, no esta edición; úsese solo como referencia.' where codigo = 'ACI-318-05';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Edición posiblemente superada por ediciones más recientes de AISC 360 (no verificado en esta revisión). En Colombia el texto vinculante es el Título F de la NSR-10.' where codigo = 'AISC-360-2010';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Un resumen web indica que la Resolución 4561 de 2022 (29-11-2022) adopta las Especificaciones Generales de Construcción de Carreteras como norma técnica y derogó la Resolución 1524 de 2022; esta ficha dice que deroga la 1536/2022: números distintos sin conciliar. Un proyecto de 2025 modificaría tres especificaciones de las resoluciones 4561 y 2451 de 2022 (no se confirmó su expedición). La Resolución 4561 de 2022 no está en el registro.' where codigo = 'RES-2451-2022';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] No se encontró esta resolución en una búsqueda web; el número o el año pueden ser erróneos o el acto puede no estar publicado. Estado sin confirmar.' where codigo = 'RES-2743-2026';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] La agenda regulatoria 2023-2024 de INVIAS incluye revisar y actualizar el Manual de Diseño Geométrico; no se encontró una resolución que lo reemplace. Vigente mientras no haya reemplazo formal (sin confirmar).' where codigo = 'RES-000744-2009';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Un listado de la ANI asocia la Resolución 2857 de 1999 con el manual de pavimentos de medios y altos volúmenes; la resolución posterior que la derogaría sigue sin identificar. El estado «derogada_total» es una inferencia, no un acto verificado.' where codigo = 'RES-2857-1999';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Según resúmenes web, la Resolución 955 de 2021 se publicó en el Diario Oficial 51.814 (01-10-2021) y las medidas eran transitorias; la regulación de la CRA se compila en la Resolución CRA 943 de 2021, sobre cuyo texto se hacen las modificaciones posteriores.' where codigo = 'RES-CRA-955-2021';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Según resúmenes web, esta resolución (27-09-2021) adiciona el Título 2 de la Parte 8 del Libro 5 de la Resolución CRA 943 de 2021 (compilación); modificaciones posteriores se hacen sobre el texto compilado.' where codigo = 'RES-CRA-956-2021';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] No se encontró esta resolución en una búsqueda web; verificar el número y la fecha en el gestor normativo de la CRA.' where codigo = 'RES-CRA-350-2022';
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] No se encontró esta resolución en una búsqueda web; sin verificar.' where codigo in ('RES-319-2022', 'RES-970-2024');
update normas_registro set notas_vigencia = coalesce(notas_vigencia, '') || ' [2026-11-07] Resúmenes web: la Resolución 9337 de 2016 adoptó el Manual de Interventoría de Obra Pública del INVIAS (en vigor desde 01-02-2017) y reemplazó la versión de 2010 (Res. 2566); coherente con el registro.' where codigo = 'RES-319-2022-DEROGADA-ANTERIOR';

-- Estado de la revisión de la cadena
update normas_registro set cadena_modificaciones = 'parcial' where codigo in (
  'ISO-9001-2015', 'ISO-14001-2015', 'ISO-19011-2011', 'ISO-27001-2022', 'ACI-318-05', 'AISC-360-2010',
  'RES-2451-2022', 'INV-E-631-22', 'INV-E-632-22', 'INV-E-826-22', 'RES-000744-2009', 'RES-2857-1999', 'RES-003482-2007',
  'RES-CRA-955-2021', 'RES-CRA-956-2021', 'RES-CRA-350-2022', 'RES-319-2022', 'RES-319-2022-DEROGADA-ANTERIOR', 'RES-970-2024', 'RES-2119-2022',
  'RES-2743-2026', 'NTC-1500', 'LEY-1150-2007', 'LEY-1474-2011', 'SECCION-200-ENSAYO-2012', 'SECCION-300-ENSAYO-2012')
  and cadena_modificaciones = 'no_revisada';
update normas_registro set cadena_modificaciones = 'completa' where codigo in
  ('RES-0424-2001', 'RES-0668-2003', 'RES-1096-2000', 'RES-1447-2005', 'RES-1459-2005', 'RES-2320-2009') and estado_vigencia = 'derogada_total';
update normas_registro set cadena_modificaciones = 'no_aplica' where codigo in
  ('IAD-MIPYMES-FERRETERIA', 'POT-FUENTES-SEC-2023', 'POT-MVCT-2024', 'BUILDCHANGE-2015', 'AIS-2004');

-- Cadenas nuevas en normas_modificaciones
insert into normas_modificaciones (norma, decreto, fecha, objeto, toca_apendice_a4, estado_verificacion, fuente_verificacion) values
  ('INVIAS especificaciones generales', 'Resolución 2451 de 2022', '2022-07-15', 'Adopta 16 especificaciones generales (nuevas tecnologías) y tres normas de ensayo (INV E 631-22, 632-22, 826-22).', 'no', 'resumen_web_sin_verificar', 'Resumen web (Gaceta 52106, 25-07-2022); el registro ya la tiene.'),
  ('INVIAS especificaciones generales', 'Resolución 4561 de 2022', '2022-11-29', 'Adopta las Especificaciones Generales de Construcción de Carreteras como norma técnica; deroga la Resolución 1524 de 2022 según el resumen (el registro menciona la 1536/2022: sin conciliar).', 'no', 'resumen_web_sin_verificar', 'Resumen web; NO está en normas_registro.'),
  ('INVIAS especificaciones generales', 'Proyecto de resolución 2025 (INVIAS)', null, 'Modificaría tres especificaciones de las resoluciones 4561 y 2451 de 2022 y derogaría la Resolución 6044 de 2024; no se confirmó su expedición.', 'no', 'resumen_web_sin_verificar', 'Encabezado de un proyecto publicado en un repositorio de proyectos de norma.'),
  ('ISO 9001', 'ISO 9001:2026', null, 'Nueva edición anunciada (publicación prevista el 16-09-2026; transición de tres años); reemplazaría ISO 9001:2015.', 'no', 'resumen_web_sin_verificar', 'Noticia del sitio de ISO y resúmenes web con datos de transición no uniformes.'),
  ('ISO 19011', 'ISO 19011:2018', null, 'Tercera edición; cancela y reemplaza ISO 19011:2011. Cuarta edición en desarrollo (prevista 2026, sin verificar).', 'no', 'resumen_web_sin_verificar', 'Varias fuentes coherentes (ANSI, universidades).'),
  ('ACI 318', 'ACI CODE-318-25', '2025-07-09', 'Edición publicada (impresa) el 9 de julio de 2025; primera revisión importante desde ACI 318-19.', 'no', 'resumen_web_sin_verificar', 'Notas de prensa del ACI y medios del sector.')
on conflict (norma, decreto) do nothing;
