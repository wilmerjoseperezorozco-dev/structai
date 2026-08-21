-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820142007
-- Nombre: borrar_chunks_obsoletos_titulo_f_batch2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- E-SEC6-FORM1/FORM2 (flexion): superadas por NSR10-F-F_2_6a (verbatim real).
-- E-SEC8-FORM1: ADEMAS de ser numeracion equivocada, tenia valores Fnv
-- incorrectos para pernos A325/A490 (330/415 MPa) frente a los reales de la
-- tabla F.2.10.3-2 verbatim (372/457 MPa) -- error de contenido, no solo de
-- formato. E-SEC8-FORM2/IMG1: superadas por NSR10-F-F_2_10a (verbatim real).
delete from nsr10_chunks where id in (
  'E-SEC6-FORM1', 'E-SEC6-FORM2',
  'E-SEC8-FORM1', 'E-SEC8-FORM2', 'E-SEC8-IMG1'
);
