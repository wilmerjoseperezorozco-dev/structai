-- Registro de los Títulos E, H y J de la NSR-10 en normas_registro (aplicada vía MCP el 2026-11-08).
-- El contenido ya estaba en nsr10_chunks; faltaba solo la fila de registro. Los chunks NO se vinculan a norma_id
-- (igual que A, B, F, I, K): el filtro de vigencia trata norma_id nulo como vigente.
insert into normas_registro (codigo, nombre_completo, entidad_emisora, tipo, fecha_expedicion, estado_vigencia, notas_vigencia, cadena_modificaciones)
select v.codigo, v.nombre, 'Ministerio de Ambiente, Vivienda y Desarrollo Territorial — Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997)', 'nsr10', date '2010-01-01', 'vigente', v.nota, 'parcial'
from (values
 ('NSR10-TITULO-E','NSR-10 — Título E: Casas de uno y dos pisos','[2026-11-08] Registro creado: contenido ya en nsr10_chunks (ids NSR10-E-*), sin fila en normas_registro. Vigencia del conjunto NSR-10 y decretos modificatorios sin reverificar en esta fecha.'),
 ('NSR10-TITULO-H','NSR-10 — Título H: Estudios geotécnicos','[2026-11-08] Registro creado: Título H ingestado y cerrado verbatim el 2026-09-07 (ids NSR10-H-*). Vigencia del conjunto sin reverificar en esta fecha.'),
 ('NSR10-TITULO-J','NSR-10 — Título J: Requisitos de protección contra incendios en edificaciones','[2026-11-08] Registro creado: Título J ingestado (158/159 numerales; ids NSR10-J-*). Vigencia del conjunto sin reverificar en esta fecha.')
) as v(codigo,nombre,nota)
where not exists (select 1 from normas_registro r where r.codigo=v.codigo);
