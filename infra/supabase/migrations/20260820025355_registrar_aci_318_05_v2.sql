-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260820025355
-- Nombre: registrar_aci_318_05_v2
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

insert into normas_registro (codigo, nombre_completo, entidad_emisora, tipo, fecha_expedicion, estado_vigencia, notas_vigencia)
values (
  'ACI-318-05',
  'ACI 318S-05 / 318SR-05 — Requisitos de Reglamento para Concreto Estructural y Comentario (versión en español y sistema métrico)',
  'American Concrete Institute (ACI)',
  'otro',
  '2005-01-01',
  'vigente',
  'Edición 2005 -- NO es la última edición ACI (existen 318-11/14/19), pero es la base declarada de NSR-10 Título C (Concreto Estructural), por eso sigue siendo la referencia relevante para Colombia. '
  'Solo se cargó ficha técnica curada de los Capítulos 11 (Cortante y Torsión) y 21 (Disposiciones especiales para diseño sísmico) -- NO es el texto normativo completo verbatim: '
  'la extracción automática del PDF (495 páginas) corrompe subíndices/ecuaciones en fórmulas complejas (confirmado 2026-08-19, ej. "φVn ≥ Vu" salía como "φ ≥nuVV"), '
  'así que se redactaron a mano solo los conceptos y ecuaciones que se pudieron verificar con alta confianza, en vez de arriesgar una fórmula mal transcrita en un producto de ingeniería real. '
  'Capítulo 12 (Longitudes de desarrollo) quedó pendiente -- su ecuación básica tiene varios coeficientes que sí requieren verificación visual contra el PDF, no de memoria.'
)
on conflict (codigo) do update set notas_vigencia = excluded.notas_vigencia;
