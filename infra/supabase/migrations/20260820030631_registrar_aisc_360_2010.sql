-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820030631
-- Nombre: registrar_aisc_360_2010
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, entidad_emisora, tipo, fecha_expedicion, estado_vigencia, notas_vigencia)
values (
  'AISC-360-2010',
  'ANSI/AISC 360-10 — Especificación para Edificios de Acero Estructural (versión en español)',
  'American Institute of Steel Construction (AISC)',
  'otro',
  '2010-06-22',
  'vigente',
  'StructAI no tenia ninguna cobertura de diseño en acero antes de esto -- primera fuente normativa de acero cargada. '
  'Solo se cargó ficha técnica de Cap. A (Disposiciones Generales) y el inicio del Cap. B (Requisitos de Diseño: '
  'cargas/combinaciones, base LRFD/ASD, clasificación de secciones) -- NO es el texto completo verbatim. '
  'El PDF fuente (aisc-360-2010-v22-espa.pdf, 11.3MB) supera el límite de 10MB de la herramienta de descarga usada '
  'esta sesión (2026-08-20); la extracción vía lectura de Drive se cortó en 252.524 caracteres, alcanzando solo '
  'hasta el arranque del Cap. B (clasificación de secciones, Tabla B4.1) antes del corte -- nunca llegó a los '
  'capítulos de diseño por capacidad (D-tracción, E-compresión, F-flexión, G-corte, H-combinadas), que es donde '
  'está el valor real de cálculo. Ampliar esa cobertura requiere descargar el PDF completo por otra vía (API '
  'directa de Drive, o pedir al usuario un PDF más liviano/partido como ya existe para AASHTO) -- pendiente.'
)
on conflict (codigo) do update set notas_vigencia = excluded.notas_vigencia;
