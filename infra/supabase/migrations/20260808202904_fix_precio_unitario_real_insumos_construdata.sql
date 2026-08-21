-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260808202904
-- Nombre: fix_precio_unitario_real_insumos_construdata
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

-- Hallazgo (2026-08-08): en las filas tipo_fuente='catalogo_construdata', la columna
-- "valor_unitario" extraída del PDF de Construdata es en realidad el COSTO DE LA LÍNEA
-- dentro de la actividad (cantidad × precio real de mercado), no el precio por unidad.
-- Confirmado con 162 filas de "CEMENTO GRIS": valor_unitario/cantidad = 366 COP/kg
-- de forma consistente. Se agrega precio_unitario_real (derivado) para que el chat
-- responda con el precio de mercado correcto, no con el costo de línea.
alter table apu_insumos_referencia
  add column if not exists precio_unitario_real numeric;

comment on column apu_insumos_referencia.valor_unitario is
  'Para tipo_fuente=catalogo_construdata: costo de ESTA línea de insumo dentro de la actividad (cantidad × precio real). NO es precio por unidad de mercado — usar precio_unitario_real para eso. Para otras fuentes (contratos reales, INVIAS) sí es precio unitario real.';
comment on column apu_insumos_referencia.precio_unitario_real is
  'Precio real por unidad de mercado = valor_unitario / cantidad (solo calculado cuando cantidad > 0). Es el campo correcto para responder "¿cuánto cuesta X por kg/m³/unidad?".';

update apu_insumos_referencia
set precio_unitario_real = round(valor_unitario / cantidad, 2)
where cantidad is not null and cantidad > 0 and valor_unitario is not null;

-- Para fuentes que ya eran precio unitario real (no catalogo_construdata), copiar directo.
update apu_insumos_referencia
set precio_unitario_real = valor_unitario
where tipo_fuente != 'catalogo_construdata' and valor_unitario is not null and precio_unitario_real is null;
