-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820213456
-- Nombre: agregar_f36_pac_acero
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

F.3.6 AGREGADO 2026-08-20: Pórticos Arriostrados Concéntricamente (PAC-DMI/DES), segundo sistema sísmico de acero más usado en Colombia después de PRM. Incluye la regla de distribución 30%-70% tensión/compresión, prohibición de arriostramiento en K, y la lógica de diseño por capacidad (Emh basado en resistencia esperada Ry*Fy de la riostra, no en fuerza sísmica de código). Sigue pendiente: F.3.6.3 PAE (excéntricamente arriostrados), F.3.6.4 PAPR (pandeo restringido), F.3.6.5 MCA (muros de cortante de acero), F.3.7-F.3.8 (compuestos), F.3.9-F.3.11 (fabricación/control de calidad/ensayos de conexión).$$
where codigo = 'NSR10-TITULO-F';
