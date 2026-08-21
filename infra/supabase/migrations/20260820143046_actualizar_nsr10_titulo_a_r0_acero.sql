-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820143046
-- Nombre: actualizar_nsr10_titulo_a_r0_acero
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

ADICIÓN 2026-08-20 (parte del cierre de la reauditoría de Título F): se agregó el chunk verbatim NSR10-A-A_3_3_1_R0_acero con los coeficientes sísmicos R0/Ω0 específicos de sistemas de ACERO, extraídos de las Tablas A.3-1/A.3-3/A.3-4 de este Título A. Contexto: existían 2 chunks obsoletos (ntc_chunks ids 297/298, ya borrados) que asumían erróneamente que estos coeficientes vivían en un capítulo "F.13" del Título F — en realidad las tablas R0 del Reglamento agrupan TODOS los materiales estructurales juntas en el Título A, no por título de material. Mismo patrón de error de atribución ya visto y corregido para contenido sísmico mal etiquetado bajo Título B.$$
where codigo = 'NSR10-TITULO-A';
