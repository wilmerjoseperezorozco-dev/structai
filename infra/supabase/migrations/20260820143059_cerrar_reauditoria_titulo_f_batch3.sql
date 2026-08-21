-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820143059
-- Nombre: cerrar_reauditoria_titulo_f_batch3
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

CIERRE BATCH 3, 2026-08-20: se completó F.2.10.3 (pernos) con las 3 fórmulas de resistencia de diseño que faltaban — F.2.10.3.6 (Rn=Fn*Ab, phi=0.75, tipo aplastamiento), F.2.10.3.7 (esfuerzos combinados cortante+tensión, F'nt modificada), F.2.10.3.8 (deslizamiento crítico, Rn=mu*Du*hf*Tb*ns, phi según tipo de perforación) — extraídas de NSR-10-801-840.pdf. Se confirmó además que el patrón Rn=mu*Du*hf*Tb*ns del viejo chunk obsoleto E-SEC8-FORM1 era estructuralmente correcto (solo los valores Fnv de la tabla estaban mal, ya corregido en el batch anterior).

Se identificó y corrigió el hallazgo de "F.13" (coeficientes R0 sísmicos para acero): NO es un capítulo de Título F — vive en las Tablas A.3-1/A.3-3/A.3-4 de Título A (ver NSR10-TITULO-A, chunk NSR10-A-A_3_3_1_R0_acero). Los 2 chunks obsoletos correspondientes (ntc_chunks ids 297/298) fueron borrados.

Con esto, Título F queda con 9 chunks verbatim reales (F.1, F.2.1-F.2.3, F.2.4, F.2.5×2, F.2.6, F.2.10×2) y 0 chunks obsoletos en nsr10_chunks con numeración incorrecta para contenido ya cubierto. Quedan pendientes reales sin cubrir aún (no hay obsoleto engañoso que los reemplace, simplemente no están): F.2.7 (cortante en vigas), F.2.8 (flexo-compresión combinada), F.2.9 (construcción compuesta), F.2.11 (conexiones PTE), F.3 completo (provisiones sísmicas para acero, F-208 a F-299, ~90 páginas — capítulo grande, no iniciado), F.4 a F.13 reales (fabricación, montaje, evaluación estructuras existentes, aluminio — nunca inventariados con certeza en el catálogo maestro).$$
where codigo = 'NSR10-TITULO-F';
