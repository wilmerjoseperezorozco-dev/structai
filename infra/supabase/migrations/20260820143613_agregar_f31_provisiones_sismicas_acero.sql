-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820143613
-- Nombre: agregar_f31_provisiones_sismicas_acero
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

F.3 INICIADO 2026-08-20: se agregó NSR10-F-F_3_1 (alcance + materiales del capítulo de provisiones sísmicas para acero — clasificación DES/DMO/DMI, límites de Fy, tabla Ry/Rt). F.3 es un capítulo enorme (F-208 a F-299, ~90 páginas, equivalente en alcance a todo el estándar AISC 341 como documento aparte) que cubre: F.3.5 PRM (pórticos resistentes a momento DES/DMO/DMI/PCD), F.3.6 PA (arriostrados concéntricos/excéntricos/PAPR), F.3.7 PRMC (compuestos resistentes a momento), F.3.8 (arriostrados compuestos y muros de cortante de placa de acero), F.3.9-F.3.11 (control de calidad, conexiones precalificadas/ensayadas). Solo F.3.1 (alcance/materiales) está cubierto — F.3.2 en adelante (los requisitos de diseño específicos por sistema, lo más consultado en la práctica) sigue completamente pendiente, requiere una sesión dedicada por su tamaño.$$
where codigo = 'NSR10-TITULO-F';
