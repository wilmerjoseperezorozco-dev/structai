-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820140136
-- Nombre: registrar_nsr10_titulo_a
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'NSR10-TITULO-A',
  'NSR-10 — Reglamento Colombiano de Construcción Sismo Resistente, Título A: Requisitos Generales de Diseño y Construcción Sismo Resistente',
  'nsr10',
  '2010-01-01',
  'vigente',
  'Ministerio de Ambiente, Vivienda y Desarrollo Territorial — Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997)',
  $$Gap cerrado 2026-08-20: se agregó el chunk verbatim NSR10-A-A_3_8_a_A_3_9 (Estructuras aisladas sísmicamente en su base + uso de disipadores de energía), que antes tenía CERO cobertura pese a que la norma sí trata el tema. Hallazgo relevante para el usuario: la NSR-10 dedica solo 6 artículos cortos a esto (A.3.8.1-3, A.3.9.1-3) y no desarrolla metodología de diseño propia — remite en su totalidad a FEMA 450/NEHRP 2003 y ASCE/SEI 7-05 (ediciones de mediados de los 2000, hoy superadas por ASCE 7-16/7-22 Cap. 17). Cualquier contenido futuro más profundo sobre diseño de aislamiento sísmico en StructAI tendría que basarse en esas referencias internacionales, no en la NSR-10 misma. Pendiente: siguen existiendo 11 chunks sintéticos obsoletos bajo Título A sin identificar/limpiar todavía (mismo patrón que se resolvió para B y C en esta sesión) — no abordado aún por falta de tiempo, es la siguiente limpieza obvia dentro de A.$$
);
