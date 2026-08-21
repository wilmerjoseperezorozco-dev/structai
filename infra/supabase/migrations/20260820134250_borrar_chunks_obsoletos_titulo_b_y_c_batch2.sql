-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820134250
-- Nombre: borrar_chunks_obsoletos_titulo_b_y_c_batch2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Borra chunks sinteticos obsoletos de Titulo C cuya numeracion de seccion
-- estaba equivocada (C.8/C.9/C.10/C.11) y cuyo contenido real ya esta
-- cubierto correctamente por los chunks verbatim NSR10-C-C_10a/10b/11a/11b/11c/12a/12b,
-- mas los duplicados de C.1 (NSR10-ALCANCE-C, C-SEC1-001, ya cubiertos por NSR10-C-C_1).
delete from nsr10_chunks where id in (
  'NSR10-ALCANCE-C',
  'C-SEC1-001',
  'C-SEC8-IMG1', 'C-SEC8-IMG2', 'C-SEC8-FORM1', 'C-SEC8-FORM2',
  'C-SEC9-FORM1', 'C-SEC9-FORM2', 'C-SEC9-FORM3',
  'C-SEC10-IMG1', 'C-SEC10-FORM1',
  'C-SEC11-FORM1'
);

-- Borra los 19 chunks sinteticos obsoletos de Titulo B: todos estan
-- explicitamente marcados "SUPERADO por contenido verbatim real, ver
-- capitulo con prefijo NSR10-B-", y ese reemplazo real ya existe y cubre
-- B.1-B.6 completo (confirmado por consulta previa a NSR10-B-*), incluyendo
-- el chunk NSR10-B-QA-viento-no-sismo que corrige explicitamente el error
-- de contenido sismico atribuido a Titulo B (el sismo es Titulo A).
delete from nsr10_chunks where id in (
  'NSR10-ALCANCE-B', 'B-SEC1-001',
  'B-SEC3-TAB1', 'B-SEC3-TAB2', 'B-SEC3-FORM1',
  'B-SEC4-TAB1', 'B-SEC4-FORM1',
  'B-SEC5-TAB1', 'B-SEC5-IMG1', 'B-SEC5-FORM1', 'B-SEC5-FORM2',
  'B-SEC6-TAB1', 'B-SEC6-IMG1', 'B-SEC6-IMG2', 'B-SEC6-TAB2', 'B-SEC6-FORM1', 'B-SEC6-FORM2',
  'B-SEC7-FORM1',
  'B-SEC8-TEXT1'
);
