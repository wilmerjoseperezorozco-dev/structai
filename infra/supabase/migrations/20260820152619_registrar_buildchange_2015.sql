-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820152619
-- Nombre: registrar_buildchange_2015
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'BUILDCHANGE-2015',
  'Manual de Evaluación y Reforzamiento Sísmico para Reducción de Vulnerabilidad en Viviendas',
  'otro',
  '2015-03-04',
  'vigente',
  'Build Change (ONG) + Swisscontact Colombia, con apoyo no técnico de SENA; aprobado por la Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes (CASACRS) mediante Acta 124 del 4 de marzo de 2015 como régimen de excepción al NSR-10',
  $$Ingesta 2026-08-20: 2 chunks (metodología cuantitativa PAM completa con todos los factores C, y catálogo de técnicas de reforzamiento con factores K de equivalencia) agregados como resumen técnico en palabras propias con atribución. Fuente: get.buildchange.org (sitio oficial de la ONG, publicación abierta), no se distribuye el PDF a través de la app. Es la base directa que AIS 410-23 (2023) formalizó y actualizó -- basado a su vez en ASCE-31 (evaluación) y ASCE-41 (rehabilitación), exactamente los mismos estándares que NSR-10 A.10.9.4 autoriza como metodología alterna. Confirmación explícita de aplicabilidad NACIONAL en el Anexo D del manual ("el enfoque y la metodología son aplicables a Colombia en general"), con guía específica para adaptar el uso fuera de Bogotá (identificación catastral local, cartografía de licuefacción local, Sa vía Capítulo A.2 nacional de la NSR-10 o microzonificación local donde exista). Este es el complemento cuantitativo real a NSR10-A-A_10_general y AIS410-23-*: mientras A.10 y AIS 410-23 dan el marco/procedimiento, este manual da las fórmulas y factores concretos para calcular.$$
);
