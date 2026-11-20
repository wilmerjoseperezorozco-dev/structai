-- Índices duplicados (diagnóstico de espacio del 2026-11-16: la base estaba en 489 de 500 MB del plan gratuito).
-- Cada uno repite exactamente las columnas y el orden de la restricción UNIQUE de su tabla, que ya crea su propio índice
-- btree; el planificador usa ese índice para las mismas búsquedas. Libera ~24 MB.
-- Reversible: recrear con los CREATE INDEX comentados al final.
drop index if exists public.idx_ideam_caudal_historico_estacion_fecha;   -- = ideam_caudal_historico_codigo_estacion_fecha_key (codigo_estacion, fecha)
drop index if exists public.idx_invias_actividad_costos_lookup;          -- = invias_actividad_costos_numeral_provincia_codigo_periodo_key
drop index if exists public.idx_invias_insumos_precios_lookup;           -- = invias_insumos_precios_insumo_codigo_provincia_codigo_perio_key

-- Para revertir:
-- create index idx_ideam_caudal_historico_estacion_fecha on public.ideam_caudal_historico using btree (codigo_estacion, fecha);
-- create index idx_invias_actividad_costos_lookup on public.invias_actividad_costos using btree (numeral, provincia_codigo, periodo);
-- create index idx_invias_insumos_precios_lookup on public.invias_insumos_precios using btree (insumo_codigo, provincia_codigo, periodo);
