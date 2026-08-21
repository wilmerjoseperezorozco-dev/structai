-- INVIAS APU Regionalizados de Referencia — esquema normalizado
--
-- Fuente: https://www.invias.gov.co/publicaciones/4149/analisis-de-precios-unitarios-apu-regionalizados-de-referencia/
-- App real detrás del iframe público: hermes2.invias.gov.co/APUs/filtroAPU/
-- Archivos Excel públicos, sin autenticación:
--   https://hermes2.invias.gov.co/APUs/Provincias/<anio>_<periodo>/APU_<codigoprovincia>_<DEPTO>__<PROVINCIA>_<anio>_<periodo>.xlsx
-- API REST en vivo (ArcGIS):
--   https://hermes2.invias.gov.co/server/rest/services/apu/APU/MapServer/3/query
--
-- Diseño: normalizado en 6 tablas en vez de columnas fijas por región (como
-- apu_precios_referencia/apu_insumos_referencia, limitadas a Bogotá/Cali/Medellín) —
-- necesario porque esto escala a las 140 provincias del país, no 3 ciudades.
--
-- Verificado con datos reales (Meta-Ariari vs Casanare, numeral 610,3): tanto el
-- precio unitario como el RENDIMIENTO/CANTIDAD de cada insumo varían por provincia
-- (no solo el precio) — por eso invias_actividad_insumos lleva provincia_codigo,
-- no es un "recipe" nacional fijo.

-- 1. Catálogo geográfico (140 provincias del país, hoy solo Orinoquía cargada)
create table if not exists public.invias_provincias (
  codigo text primary key,                    -- ej '5001', '8100'
  codigo_departamento text not null,           -- ej '50', '81'
  departamento text not null,
  provincia text not null,
  region_natural text,                         -- Andina/Caribe/Pacífico/Orinoquía/Amazonía/Insular
  created_at timestamptz not null default now()
);

comment on table public.invias_provincias is
  'Catálogo de provincias DANE usadas por INVIAS para regionalizar precios. region_natural es un dato derivado nuestro (no viene de INVIAS), útil para agrupar consultas por región geográfica.';

-- 2. Catálogo maestro de insumos (nacional — mismo código/descripción en todo el país,
--    solo el precio varía por provincia, verificado con C0010200 en Meta vs Casanare)
create table if not exists public.invias_insumos (
  codigo text primary key,                     -- ej 'B0014347', 'C0010200', 'A0030040', 'T0100035'
  descripcion text not null,
  unidad text,
  tipo_insumo text not null check (tipo_insumo in ('equipo', 'material', 'mano_obra', 'transporte')),
  categoria text,                               -- solo viene poblado para materiales (hoja INSUMO_MATERIALES)
  created_at timestamptz not null default now()
);

-- 3. Precio de cada insumo por provincia y período (hojas consolidadas
--    MATERIALES/EQUIPO/MANO DE OBRA/TRANSPORTE de cada archivo)
create table if not exists public.invias_insumos_precios (
  id uuid primary key default gen_random_uuid(),
  insumo_codigo text not null references public.invias_insumos(codigo),
  provincia_codigo text not null references public.invias_provincias(codigo),
  periodo text not null,                        -- ej '2026-1'
  precio numeric not null,
  created_at timestamptz not null default now(),
  unique (insumo_codigo, provincia_codigo, periodo)
);

-- 4. Catálogo maestro de actividades/numerales (nacional — descripción y unidad
--    consistentes en todo el país, verificado con 610,3 en Meta vs Casanare)
create table if not exists public.invias_actividades (
  numeral text primary key,                     -- ej '610,3', '840,11'
  descripcion text not null,
  unidad text,
  created_at timestamptz not null default now()
);

-- 5. Receta real de cada actividad por provincia y período (el desglose completo:
--    qué insumos entran, con qué cantidad/rendimiento — SÍ varía por provincia)
create table if not exists public.invias_actividad_insumos (
  id uuid primary key default gen_random_uuid(),
  numeral text not null references public.invias_actividades(numeral),
  provincia_codigo text not null references public.invias_provincias(codigo),
  periodo text not null,
  insumo_codigo text references public.invias_insumos(codigo),  -- nullable: insumos especiales tipo HERMENINV no siempre están en el catálogo consolidado
  insumo_descripcion text not null,              -- guardado literal también, por si insumo_codigo es null
  tipo_insumo text not null check (tipo_insumo in ('equipo', 'material', 'mano_obra', 'transporte')),
  cantidad_o_rendimiento numeric,
  valor_unitario_linea numeric not null,         -- el "Vr. UNITARIO" ya calculado de esa línea en el APU
  created_at timestamptz not null default now()
);

-- 6. Totales por actividad × provincia × período — la tabla más útil para consulta
--    directa del chat. Guarda el COSTO DIRECTO real que publica INVIAS; NO inventa
--    un "precio total con AIU" porque INVIAS deja esa fila vacía a propósito (el
--    Administración/Imprevistos/Utilidad lo define cada contrato, no es un dato
--    nacional único) — mismo principio de honestidad de fuente del resto del proyecto.
create table if not exists public.invias_actividad_costos (
  id uuid primary key default gen_random_uuid(),
  numeral text not null references public.invias_actividades(numeral),
  provincia_codigo text not null references public.invias_provincias(codigo),
  periodo text not null,
  costo_equipo numeric not null default 0,
  costo_materiales numeric not null default 0,
  costo_transporte numeric not null default 0,
  costo_mano_obra numeric not null default 0,
  costo_directo_total numeric not null,          -- suma de los 4 anteriores, tal como INVIAS lo reporta
  created_at timestamptz not null default now(),
  unique (numeral, provincia_codigo, periodo)
);

comment on table public.invias_actividad_costos is
  'costo_directo_total es el "TOTAL COSTO DIRECTO" que INVIAS sí publica. INVIAS deja la fila de AIU (Administración/Imprevistos/Utilidad) vacía en sus APU de referencia porque varía por contrato real — nunca inventar/estimar un precio "todo costo" aquí.';

-- Índices para búsqueda de texto (español) sobre descripciones — mismo patrón que
-- buscar_precios_apu() en apu_precios_referencia
create index if not exists idx_invias_actividades_descripcion_fts
  on public.invias_actividades using gin (to_tsvector('spanish', descripcion));

create index if not exists idx_invias_insumos_descripcion_fts
  on public.invias_insumos using gin (to_tsvector('spanish', descripcion));

create index if not exists idx_invias_actividad_costos_lookup
  on public.invias_actividad_costos (numeral, provincia_codigo, periodo);

create index if not exists idx_invias_insumos_precios_lookup
  on public.invias_insumos_precios (insumo_codigo, provincia_codigo, periodo);

-- RPC de búsqueda — mismo espíritu que buscar_precios_apu(), texto completo español
-- + trigram, OR entre términos (no AND, mismo bug ya corregido antes en esta base).
create extension if not exists pg_trgm;

create or replace function public.buscar_precios_invias(
  p_query text,
  p_provincia_codigo text default null,
  p_limit int default 10
)
returns table (
  numeral text,
  descripcion text,
  unidad text,
  provincia text,
  departamento text,
  periodo text,
  costo_directo_total numeric,
  relevancia real
)
language sql
stable
as $$
  select
    a.numeral,
    a.descripcion,
    a.unidad,
    p.provincia,
    p.departamento,
    c.periodo,
    c.costo_directo_total,
    ts_rank(to_tsvector('spanish', a.descripcion), websearch_to_tsquery('spanish', p_query))
      + similarity(a.descripcion, p_query) as relevancia
  from public.invias_actividad_costos c
  join public.invias_actividades a on a.numeral = c.numeral
  join public.invias_provincias p on p.codigo = c.provincia_codigo
  where
    (p_provincia_codigo is null or c.provincia_codigo = p_provincia_codigo)
    and (
      to_tsvector('spanish', a.descripcion) @@ websearch_to_tsquery('spanish', p_query)
      or a.descripcion % p_query
    )
  order by relevancia desc
  limit p_limit;
$$;

comment on function public.buscar_precios_invias is
  'Busca actividades de INVIAS APU Regionalizados por texto libre, opcionalmente filtrado por provincia. Devuelve el costo directo real publicado por INVIAS (sin AIU).';
