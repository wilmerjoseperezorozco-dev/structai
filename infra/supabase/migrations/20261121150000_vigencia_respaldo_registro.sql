-- #261: el registro de vigencia afirmaba derogaciones sin respaldo. Cada corrección se apoya en la nota de vigencia ya
-- guardada en la misma fila (normas_registro.notas_vigencia); no se agrega información nueva sin fuente.
-- Ver packages/construdata/vigencia_evidencia.py (parámetros de evidencia).

-- Res. 319 de 2022: su nota dice "Modificada/complementada por Resolución 970/2024 (adición Capítulo 2 Supervisión).
-- No derogada totalmente, sigue vigente en lo no modificado". Era 'derogada_parcial' sin alcance: pasa a 'modificada'.
update normas_registro
   set estado_vigencia = 'modificada',
       alcance_derogacion = 'Modificada por la Resolución 970 de 2024 (adiciona el Capítulo 2, supervisión); sigue vigente en lo no modificado',
       updated_at = now()
 where codigo = 'RES-319-2022' and estado_vigencia = 'derogada_parcial';

-- Res. 9337 de 2016: su nota dice "Mencionada como derogada por la Resolución 319/2022" (referencia dentro de esa
-- resolución). Sigue derogada; se registra el acto que la deroga.
update normas_registro
   set derogada_por = (select id from normas_registro where codigo = 'RES-319-2022'),
       alcance_derogacion = 'Derogada por la Resolución 319 de 2022 (nuevo Manual de Interventoría de Obra Pública)',
       updated_at = now()
 where codigo = 'RES-319-2022-DEROGADA-ANTERIOR' and derogada_por is null;

-- ISO 19011:2011: su nota dice "la tercera edición ISO 19011:2018 cancela y reemplaza a esta edición". Sigue
-- derogada (superada); se registra el reemplazo como alcance (la edición 2018 no está en el registro).
update normas_registro
   set alcance_derogacion = 'Cancelada y reemplazada por la ISO 19011:2018 (tercera edición)',
       updated_at = now()
 where codigo = 'ISO-19011-2011' and alcance_derogacion is null;

-- Res. 2857 de 1999 no se toca: su nota no identifica el acto ni la edición que la reemplaza. El código la presenta como
-- "vigencia no confirmada" hasta que se registre ese respaldo.
