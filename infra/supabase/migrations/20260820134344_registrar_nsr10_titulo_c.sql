-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820134344
-- Nombre: registrar_nsr10_titulo_c
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, tipo, fecha_expedicion, estado_vigencia, entidad_emisora, notas_vigencia)
values (
  'NSR10-TITULO-C',
  'NSR-10 — Reglamento Colombiano de Construcción Sismo Resistente, Título C: Concreto Estructural',
  'nsr10',
  '2010-01-01',
  'vigente',
  'Ministerio de Ambiente, Vivienda y Desarrollo Territorial — Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997)',
  $$Reauditoría 2026-08-20: el Título C ya tenía 7 chunks verbatim reales (C.1, C.4, C.5, C.7, C.9, C.21, +1 QA) de sesiones previas, pero coexistían con 16 chunks sintéticos obsoletos que tenían la NUMERACIÓN DE SECCIÓN EQUIVOCADA (ej. llamaban "C.8" a contenido de flexión que en realidad es C.10; "C.9" a contenido de cortante que es C.11; "C.10" a contenido de desarrollo/anclaje que es C.12; "C.11" a contenido de muros que es C.14) — confirmado contra nsr10_catalogo_maestro.json, catálogo verificado página por página en agosto/2026. Se agregaron 7 chunks verbatim reales para C.10 (Flexión y cargas axiales), C.11 (Cortante y torsión) y C.12 (Longitudes de desarrollo y empalmes), extraídos de NSR-10-377-387.pdf / NSR-10-389-407.pdf / NSR-10-409-419.pdf (carpeta Drive NSR10), y se borraron los 12 chunks obsoletos que ahora quedaban redundantes Y mal etiquetados (los 10 de C.8/C.9/C.10/C.11 más 2 duplicados de C.1). Limitación conocida: igual que en ACI-318-05, la extracción automática de PDF escaneado corrompe subíndices/símbolos griegos en fórmulas complejas; el contenido normativo en prosa es verbatim, las ecuaciones fueron renormalizadas a notación en línea legible (verificadas contra el texto extraído, no re-derivadas de memoria). Pendiente real: C.2 (Notación), C.3 (Materiales), C.6 (Cimbras/encofrados) y C.13 en adelante (losas, muros C.14, cimentaciones C.15, preesforzado C.18, sismo-resistente ya cubierto en C.21) siguen sin verbatim real — quedan 4 chunks sintéticos obsoletos para C.2/C.3/C.6, correctamente flagueados, no borrados por falta de reemplazo aún.$$
);
