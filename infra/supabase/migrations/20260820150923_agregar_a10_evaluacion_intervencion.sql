-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820150923
-- Nombre: agregar_a10_evaluacion_intervencion
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

A.10 AGREGADO 2026-08-20 (hallazgo importante): se descubrió que A.10 ("Evaluación e Intervención de Edificaciones construidas antes de la vigencia del Reglamento") tenía CERO cobertura real -- el único chunk que ocupaba ese código (A-SEC10-TAB1, ya borrado) lo etiquetaba erróneamente como "notación general", cuando en realidad es el capítulo dedicado a refuerzo/rehabilitación sísmica de edificaciones existentes: procedimiento de 12 etapas (índice de sobreesfuerzo + índice de flexibilidad, ambos <1), requisitos según edad de construcción (antes/después de Decreto 1400/1984 y Ley 400/1997), y reparación post-sismo (A.10.10, directamente relevante al terremoto de Cali del 10-ago-2026). Incluye el hallazgo clave: A.10.9.4 autoriza explícitamente 3 metodologías internacionales alternas para evaluación de vulnerabilidad — ASCE/SEI 41-06, FEMA 356, ATC-40 — mismos documentos que la ingeniería de rehabilitación sísmica usa mundialmente. Fuente: NSR-10-140-154.pdf, páginas A-97 a A-111 (capítulo completo, sin recortes).$$
where codigo = 'NSR10-TITULO-A';
