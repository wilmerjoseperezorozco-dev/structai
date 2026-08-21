-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820142429
-- Nombre: actualizar_nsr10_titulo_f_batch2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

update normas_registro
set notas_vigencia = notas_vigencia || $$

REAUDITORÍA BATCH 2, 2026-08-20: se agregaron 3 chunks verbatim más: F.2.6.1-F.2.6.2 (diseño a flexión, caso más común: perfiles I/canales compactos de doble simetría, momento plástico + 3 regímenes de pandeo lateral-torsional), F.2.10.1-F.2.10.2 (conexiones soldadas: soldaduras acanaladas y de filete, Rn=Fnw*Awe con phi=0.75), y F.2.10.3 (conexiones apernadas: tabla de resistencia nominal Fnt/Fnv para A307/A325/A490). Fuente: NSR-10-712-742.pdf + NSR-10-743-770.pdf (flexión) y NSR-10-771-800.pdf (conexiones).

HALLAZGO DE CONTENIDO (no solo numeración): el chunk obsoleto E-SEC8-FORM1 tenía valores Fnv INCORRECTOS para pernos A325/A490 (330/415 MPa) frente a los reales verbatim de la Tabla F.2.10.3-2 (372/457 MPa para A325, 457/579 MPa para A490) — confirma que la reauditoría no es solo cosmética, había errores numéricos reales circulando. Se borró.

LECCIÓN DE INGESTA: el primer intento de F.2.10 fue un chunk único de 5106 caracteres mezclando soldaduras+pernos — verificado en vivo que el retrieval semántico lo perdía incluso en consultas centradas en soldadura. Se dividió en NSR10-F-F_2_10_soldaduras y NSR10-F-F_2_10_pernos (mismo patrón que F.2.5a/F.2.5b) — retrieval mejoró para pernos, soldaduras compite con contenido legítimo de CCP-14 Sección 06 (acero de puentes) en consultas genéricas, comportamiento esperado en corpus multi-norma.

PENDIENTE: la fórmula exacta de resistencia de diseño a pernos (Rn=Fn×Ab, factor phi) vive en F.2.10.3.4+ dentro de NSR-10-801-840.pdf — no extraída aún, deliberadamente no se citó un valor de memoria/AISC sin verificar. F.13 (coeficientes R0 sísmicos para acero, ntc_chunks ids 297/298) y el capítulo real de provisiones sísmicas (probablemente F.3) siguen pendientes.$$
where codigo = 'NSR10-TITULO-F';
