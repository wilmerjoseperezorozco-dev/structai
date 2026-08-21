-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820134401
-- Nombre: registrar_nsr10_titulo_b
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'NSR10-TITULO-B',
  'NSR-10 — Reglamento Colombiano de Construcción Sismo Resistente, Título B: Cargas',
  'nsr10',
  '2010-01-01',
  'vigente',
  'Ministerio de Ambiente, Vivienda y Desarrollo Territorial — Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997)',
  $$Limpieza 2026-08-20: se borraron 19 chunks sintéticos obsoletos (prefijos NSR10-ALCANCE-B, B-SEC1 a B-SEC8) que llevaban semanas marcados "SUPERADO por contenido verbatim real, ver capítulo con prefijo NSR10-B-" — el reemplazo real ya existe (15 chunks NSR10-B-*, cobertura B.1 a B.6.5 confirmada) desde una reauditoría previa, incluyendo un chunk QA explícito que corrige el error de fondo que tenían los obsoletos: atribuían contenido sísmico (espectro, Aa/Av, cortante basal) al Título B, cuando el sismo real es Título A y el Título B solo trata cargas muerta/viva/viento/empuje de tierra. No se agregó contenido nuevo en este paso, solo se eliminó la duplicación mal etiquetada que podía confundir al RAG.$$
);
