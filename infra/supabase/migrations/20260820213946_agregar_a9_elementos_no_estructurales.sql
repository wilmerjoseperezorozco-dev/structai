-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820213946
-- Nombre: agregar_a9_elementos_no_estructurales
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

A.9 AGREGADO 2026-08-20 (hallazgo de mala etiqueta, corregido): se descubrió que 11 chunks obsoletos (prefijo "J-SEC", sección "ENE.x") no eran de Título J como sugería su ID -- eran resúmenes sintéticos de A.9 (Elementos No Estructurales), y el propio campo capitulo ya reconocía "probablemente Título A.9, sin confirmar contra índice oficial". Confirmado contra el catálogo maestro y reemplazado por 2 chunks verbatim reales (NSR10-A-A_9_general_fuerzas: grados de desempeño, fórmula de fuerza sísmica Fp, 4 tipos de anclaje según Rp; NSR10-A-A_9_5_a_9_6_tablas: elementos críticos como columnas cortas/cautivas, tablas A.9.5-1/A.9.6-1 con valores ap/Rp reales). Fuente: NSR-10-130-138.pdf, capítulo completo A-87 a A-95 sin recortes. Los 11 obsoletos fueron borrados.$$
where codigo = 'NSR10-TITULO-A';
