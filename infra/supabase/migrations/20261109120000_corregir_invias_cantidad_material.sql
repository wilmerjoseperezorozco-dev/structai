-- Issue #112: en invias_actividad_insumos las filas de tipo 'material' guardaban en cantidad_o_rendimiento
-- el PRECIO UNITARIO del insumo (columna idx11 del Excel FR-APU-1) en lugar de la cantidad (idx10).
-- Se conserva el valor leído en la columna nueva precio_unitario y la cantidad se reconstruye como
-- valor_unitario_linea / precio_unitario, redondeada a 4 decimales (valor_unitario_linea viene redondeado a 2).
-- Verificación contra el Excel de Atlántico Norte (1.328 filas de material): error relativo mediano 0; 14 filas
-- (cantidades menores de 0,01) difieren más de 0,1 % por el redondeo del valor de línea.
-- Idempotente: solo toca filas con precio_unitario nulo. Equipo, transporte y mano de obra no cambian.
alter table public.invias_actividad_insumos add column if not exists precio_unitario numeric;

comment on column public.invias_actividad_insumos.precio_unitario is
  'Precio unitario del insumo en la fila (solo materiales). Antes de la migración 20261109120000 estaba guardado por error en cantidad_o_rendimiento.';
comment on column public.invias_actividad_insumos.cantidad_o_rendimiento is
  'Materiales: cantidad por unidad de actividad (reconstruida como valor_unitario_linea / precio_unitario, 4 decimales, si la fila es anterior a 2026-11-09). Equipo y mano de obra: rendimiento. Transportes: cantidad × distancia.';

update public.invias_actividad_insumos
set precio_unitario = cantidad_o_rendimiento,
    cantidad_o_rendimiento = case when cantidad_o_rendimiento > 0 then round(valor_unitario_linea / cantidad_o_rendimiento, 4) else null end
where tipo_insumo = 'material' and precio_unitario is null and cantidad_o_rendimiento is not null;
