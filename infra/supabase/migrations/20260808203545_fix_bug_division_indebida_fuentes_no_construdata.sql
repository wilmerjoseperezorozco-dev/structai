-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260808203545
-- Nombre: fix_bug_division_indebida_fuentes_no_construdata
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Corrige bug propio: la migración anterior dividió valor_unitario/cantidad
-- para TODAS las filas, pero esa corrección solo aplicaba a catalogo_construdata
-- (donde valor_unitario venía mal etiquetado como costo de línea). Para
-- contrato_real_pto_colombia, contrato_real_triple_a_acometidas, invias_regional
-- y contrato_real_mano_obra_atlantico, valor_unitario YA era el precio real por
-- unidad (confirmado contra el archivo fuente) — no debía dividirse.
update apu_insumos_referencia
set precio_unitario_real = valor_unitario
where tipo_fuente != 'catalogo_construdata';
