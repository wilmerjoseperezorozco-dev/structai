-- #295 (ordenamiento): Ley 388 de 1997 y Ley 1523 de 2012, texto compilado del Gestor Normativo EVA (Función Pública).
-- 'vigente' porque el texto cargado ya incorpora las modificaciones; los artículos derogados no se cargan.
insert into normas_registro (codigo, nombre_completo, entidad_emisora, tipo, fecha_expedicion, estado_vigencia,
                             notas_vigencia, cadena_modificaciones, pais)
select v.codigo, v.nombre, 'Congreso de la República', 'ley', v.fecha, 'vigente', v.notas, 'parcial', 'CO'
from (values
  ('LEY-388-1997', 'Ley 388 de 1997 — por la cual se modifica la Ley 9 de 1989 y la Ley 2 de 1991 (ordenamiento territorial)', date '1997-07-18',
   'Texto compilado del Gestor Normativo EVA (Función Pública), descargado 2026-11-21, con modificaciones incorporadas (el encabezado indica «Adicionado por la Ley 614 de 2000»). El artículo 120 figura como derogado y no se cargó.'),
  ('LEY-1523-2012', 'Ley 1523 de 2012 — política nacional de gestión del riesgo de desastres y Sistema Nacional de Gestión del Riesgo de Desastres', date '2012-04-24',
   'Texto compilado del Gestor Normativo EVA (Función Pública), descargado 2026-11-21, con modificaciones incorporadas.')
) as v(codigo, nombre, fecha, notas)
where not exists (select 1 from normas_registro r where r.codigo = v.codigo);
