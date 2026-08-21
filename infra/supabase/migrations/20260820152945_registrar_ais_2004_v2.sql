-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820152945
-- Nombre: registrar_ais_2004_v2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'AIS-2004',
  'Manual de Construcción, Evaluación y Rehabilitación Sismo Resistente de Viviendas de Mampostería',
  'otro',
  '2004-01-01',
  'vigente',
  'Asociación Colombiana de Ingeniería Sísmica (AIS), financiado por el Fondo para la Reconstrucción y Desarrollo Social del Eje Cafetero (FOREC) y la Dirección para la Prevención y Atención de Emergencias (DPAE) de Bogotá, con participación técnica de CEDERI-Universidad de los Andes',
  $$Ingesta 2026-08-20: 1 chunk (Capítulo II, evaluación cualitativa rápida de vulnerabilidad por checklist ponderado) agregado como resumen técnico en palabras propias con atribución. Origen: financiado tras el terremoto del Eje Cafetero de 1999 (Armenia/Quindío), es el eslabón más antiguo de la cadena AIS 2004 → Build Change 2015 → AIS 410-23 2023 (ver BUILDCHANGE-2015-* y AIS410-23-*). Complementa el método cuantitativo PAM con un checklist cualitativo más simple, útil como primer filtro de campo. Publicación abierta con múltiples espejos (academia.edu, bdd.pseau.org, civilgeeks.com), no se distribuye el PDF a través de la app. Es un documento histórico (2004, base de la línea evolutiva) -- pendiente: Capítulo I (construcción sismo resistente nueva, detalles constructivos de columnas/vigas de confinamiento/cimentación), Capítulo III (clasificación de daños post-sismo por mecanismo de falla -- directamente relevante al terremoto de Cali de agosto 2026, no extraído aún), Capítulo IV (catálogo detallado de técnicas de reparación y reforzamiento: inyección de grietas, reemplazo de barras, revestimiento estructural, refuerzo con fibras compuestas) -- sesión futura dedicada.$$
);
