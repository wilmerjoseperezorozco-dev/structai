-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820141010
-- Nombre: actualizar_nsr10_titulo_f_batch1
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

REAUDITORÍA BATCH 1, 2026-08-20: Título F era el título más débil del corpus (3 chunks verbatim reales de 19 totales). Hallazgo estructural clave: a diferencia de Título C (23 capítulos independientes C.1-C.23), Título F anida casi TODO su contenido de diseño dentro de un único capítulo gigante F.2 ("Estructuras de acero con perfiles laminados, armados y tubulares estructurales", páginas F-1 a F-159+, numerales F.2.1 a F.2.20+) — los chunks obsoletos E-SEC4/E-SEC5/E-SEC6/E-SEC7/E-SEC8/E-SEC10/E-SEC13 inventaban capítulos top-level "F.4", "F.5", "F.6", "F.7", "F.8", "F.10", "F.13" que NO EXISTEN como tales; ese contenido vive como F.2.4, F.2.5, F.2.6, F.2.8, F.2.10 dentro de F.2, y F.13/F.10 (coeficientes sísmicos, conexiones precalificadas DES) probablemente pertenecen a otro capítulo real (F.3, provisiones sísmicas) aún no verificado con certeza.

Se agregaron 2 chunks verbatim reales cubriendo F.2.4 (diseño a tensión, completo F.2.4.1-F.2.4.6) y F.2.5 (diseño a compresión, completo F.2.5.1-F.2.5.7 en dos chunks), extraídos de NSR-10-712-742.pdf (páginas F-31 a F-61). Se borraron 3 obsoletos redundantes en nsr10_chunks (E-SEC4-FORM1, E-SEC5-IMG1, E-SEC5-FORM1) y 1 en ntc_chunks (id 296, también F.5) — retrieval verificado top-1 para ambos temas.

HALLAZGO ADICIONAL: existen 4 chunks obsoletos más con el mismo problema pero viviendo en la tabla ntc_chunks (ids 295, 297, 298 — invisibles a una búsqueda que solo mira nsr10_chunks). Quedan sin reemplazo real: F.8 (soldadura/pernos — id 295), F.13 (coeficientes R0 sísmicos para sistemas de acero — ids 297/298).

PENDIENTE (próximo batch): F.2.6 (flexión de vigas), F.2.10 (conexiones: soldadura y pernos), y localizar el capítulo real de provisiones sísmicas para acero (probablemente F.3, referenciado por NSR10-F-F_2_1_a_F_2_3 pero nunca extraído).$$
where codigo = 'NSR10-TITULO-F';
