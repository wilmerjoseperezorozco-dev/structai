-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820212401
-- Nombre: actualizar_ais_2004_cap3_cap4
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

CAPÍTULOS III Y IV AGREGADOS 2026-08-20: se completó la extracción del manual con 3 chunks más — AIS2004-cap3-clasificacion_danos (clasificación de daños post-sismo por mecanismo de falla, 3 niveles Leves/Moderados/Severos con umbrales cuantitativos de ancho de grieta en mm, lógica de agregación "gobierna el peor caso" — distinta del promedio ponderado del Capítulo II), AIS2004-cap4-marco_decision_reparacion (definiciones Reparación/Reforzamiento/Reconstrucción + matriz de decisión Vulnerabilidad×Daño + técnicas de reparación A.1-A.9 con detalle constructivo real: puntales, picado de superficie, anclaje epóxico, tiempos de contracción 2-4 meses), AIS2004-cap4-tecnicas_reforzamiento (técnicas de reforzamiento B.1-B.6: vigas/columnas de confinamiento nuevas, revestimiento en concreto lanzado con anclajes epóxicos cada 2-3 veces el espesor del muro, refuerzo de cimentación, confinamiento de aberturas, fibras de carbono/vidrio). Con esto el manual AIS 2004 completo (4 capítulos) está representado en el corpus: alcance/materiales (Cap I, condensado), checklist de vulnerabilidad (Cap II, completo), clasificación de daños (Cap III, completo), y catálogo de rehabilitación (Cap IV, completo). Directamente aplicable al diagnóstico y reparación post-terremoto de Cali (agosto 2026).$$
where codigo = 'AIS-2004';
