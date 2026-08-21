-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820213927
-- Nombre: borrar_jsec_obsoletos_mal_etiquetados_a9
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Los 10 chunks J-SEC* eran en realidad contenido de A.9 (Elementos No
-- Estructurales) mal etiquetado bajo prefijo "J" -- ya reemplazados por
-- NSR10-A-A_9_general_fuerzas y NSR10-A-A_9_5_a_9_6_tablas (verbatim real).
delete from nsr10_chunks where id in (
  'J-SEC1-001','J-SEC2-TAB1','J-SEC4-FORM1','J-SEC4-TAB1','J-SEC4-TAB2',
  'J-SEC5-TAB1','J-SEC7-TAB1','J-SEC8-TAB1','J-SEC9-TAB1',
  'J-SEC12-TAB1','J-SEC12-FORM1'
);
