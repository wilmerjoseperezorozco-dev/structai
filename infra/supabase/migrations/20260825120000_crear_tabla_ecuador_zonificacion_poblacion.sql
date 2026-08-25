-- Sección 10.2 de la NEC-SE-DS (Ecuador) -- Tabla 16 "Poblaciones
-- ecuatorianas y valor del factor Z". Es el equivalente real al Anexo II
-- de la E.030 (Perú): consulta EXACTA de zona sísmica por localidad, no
-- texto narrativo -- misma decisión de diseño que
-- peru_e030_zonificacion_distrital, tabla relacional propia sin columna
-- de embedding.
--
-- Diferencia real de fondo con Perú (no una limitación de este script):
-- el método PRINCIPAL de zonificación de Ecuador es un MAPA (Figura 1,
-- 6 zonas sísmicas I-VI con su valor de factor Z, ver Tabla 1 en
-- NECSEDS-S4_1... corpus). La Tabla 16 de la sección 10.2 es un listado
-- de apoyo ("para facilitar la determinación del valor de Z") con
-- "algunas poblaciones del país", no una partición administrativa
-- completa y exhaustiva como el Anexo II peruano (que cubre TODOS los
-- distritos por mandato del Artículo 10.1 de la E.030). Se carga tal
-- cual la trae la norma -- no se completa por inferencia lo que el mapa
-- cubriría para las localidades no listadas.
--
-- Columna "poblacion": el texto verbatim combina las 3 columnas de la
-- tabla fuente (POBLACIÓN, PARROQUIA, CANTÓN) tal como aparecen -- no se
-- separaron en columnas individuales porque el texto extraído del PDF
-- no trae un delimitador confiable entre esas 3 celdas (se verificó
-- visualmente contra el PDF renderizado, ver
-- cargar_tabla16_poblaciones_factor_z.py). El campo sigue siendo
-- consultable por cualquiera de los 3 términos vía ILIKE.

create table if not exists public.ecuador_nec_se_ds_zonificacion_poblacion (
  id bigint generated always as identity primary key,
  poblacion text not null,
  provincia text not null,
  factor_z numeric(3,2) not null check (factor_z > 0 and factor_z <= 1),
  creado_en timestamptz not null default now(),
  unique (poblacion, provincia)
);

create index if not exists idx_ecuador_zonificacion_poblacion
  on public.ecuador_nec_se_ds_zonificacion_poblacion (poblacion);

create index if not exists idx_ecuador_zonificacion_provincia
  on public.ecuador_nec_se_ds_zonificacion_poblacion (provincia);

alter table public.ecuador_nec_se_ds_zonificacion_poblacion enable row level security;

create policy "public_read_ecuador_zonificacion_poblacion"
  on public.ecuador_nec_se_ds_zonificacion_poblacion
  for select
  to public
  using (true);

create policy "service_write_ecuador_zonificacion_poblacion"
  on public.ecuador_nec_se_ds_zonificacion_poblacion
  for all
  to service_role
  using (true);
