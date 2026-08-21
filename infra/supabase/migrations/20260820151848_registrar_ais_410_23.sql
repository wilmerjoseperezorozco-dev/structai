-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820151848
-- Nombre: registrar_ais_410_23
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'AIS-410-23',
  'AIS 410-23 — Evaluación y Reducción de la Vulnerabilidad Sísmica en Viviendas de Mampostería',
  'otro',
  '2023-06-01',
  'vigente',
  'Asociación Colombiana de Ingeniería Sísmica (AIS), encargado por el Ministerio de Vivienda, Ciudad y Territorio',
  $$Ingesta 2026-08-20: 2 chunks iniciales (alcance/cifras de vivienda informal en Colombia, procedimiento general) agregados como resumen técnico en palabras propias con atribución, no reproducción literal — documento publicado abiertamente por Minvivienda para consulta pública en su sitio oficial (minvivienda.gov.co), la app no distribuye el PDF original. Complementa directamente a NSR10-A-A_10_general (Capítulo A.10 de la NSR-10), que explícitamente reconoce ser de difícil aplicación en vivienda sin documentación de diseño original — el caso típico de la autoconstrucción, que según cifras citadas por el propio AIS 410-23 (CENAC, GEM, AMVA+Uniandes 2018, IDIGER 2018) representa entre 60% y 79% del parque de vivienda en las principales ciudades colombianas. Pendiente: el documento tiene 89 páginas con una metodología completa de evaluación cuantitativa (Cap. 5-6, factor PAM = porcentaje de área de muros requerido, con factores de calidad de bloque/mortero/piso/peso sísmico) y catálogo de técnicas de intervención (Cap. 7-8) que no se han extraído aún — sesión futura dedicada.$$
);
