-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820150545
-- Nombre: agregar_f35_prm_acero
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

F.3.5 AGREGADO 2026-08-20: Pórticos Resistentes a Momento (PRM-DMI/DMO/DES), el sistema sísmico de acero más común en Colombia. Incluye la ecuación columna-fuerte/viga-débil de PRM-DES (F.3.5.3-1, ΣM*pc/ΣM*pb > 1) -- la disposición sísmica de acero más citada en la práctica. Sigue pendiente: F.3.6 (arriostrados PAC/PAE/PAPR), F.3.7-F.3.8 (compuestos acero-concreto), F.3.9-F.3.11 (fabricación, control de calidad, ensayos de calificación de conexiones) -- capítulo completo ya extraído en bruto localmente (packages/construdata/normativa_raw/nsr10, no versionado), falta curar/chunkear el resto.$$
where codigo = 'NSR10-TITULO-F';
