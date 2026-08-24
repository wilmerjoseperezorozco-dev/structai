-- Señal estadística de vulnerabilidad de vivienda por municipio, derivada
-- del material predominante de paredes exteriores (VIV002) de la muestra
-- anonimizada del Sisbén IV (DNP, corte marzo-2022, datos.gov.co
-- np8m-kdhq). Investigado a fondo antes de cargar (ver
-- project_structai_outreach_institucional.md): es una MUESTRA
-- probabilistica estratificada con factor de expansión, NO un censo ni
-- un dato en vivo -- por diseño no permite identificar vivienda/persona
-- específica, solo agregados por municipio.
--
-- "Material vulnerable" = códigos VIV002 documentados en la literatura de
-- ingeniería sísmica colombiana como de mal desempeño estructural: tapia
-- pisada/adobe (2), bahareque revocado/sin revocar (3,4), madera burda
-- (5), guadua/caña/vegetal (7,8), zinc/cartón/desechos (9), sin paredes
-- (10). Se excluye deliberadamente el código 6 (material prefabricado)
-- del conteo de "vulnerable": la resistencia sísmica de un prefabricado
-- varía según diseño, no hay base para asumir que es débil.
--
-- Esto es una SEÑAL ESTADÍSTICA de vulnerabilidad de vivienda 2022,
-- NUNCA una evaluación estructural ni un censo de daño -- mismo principio
-- ya aplicado a la anomalía de caudal del IDEAM (nunca alerta oficial).

create table if not exists sisben_vulnerabilidad_vivienda_municipio (
  codigo_municipio text primary key,  -- DIVIPOLA, 5 dígitos
  municipio text,
  departamento text,
  n_viviendas_muestra integer not null,
  n_viviendas_material_vulnerable integer not null,
  pct_material_vulnerable double precision not null,
  corte text not null,  -- ej. 'SIV_2022'
  actualizado_en timestamptz not null default now()
);

comment on table sisben_vulnerabilidad_vivienda_municipio is
  'Señal estadística (NO censo, NO evaluación estructural) de % de viviendas con material de pared vulnerable por municipio, derivada de la muestra anonimizada Sisbén IV (DNP, corte SIV_2022). Pensada para cruzar con sgc_amenaza_sismica_municipios y dar un primer indicio de riesgo combinado (amenaza × vulnerabilidad de vivienda) por municipio -- nunca reemplaza un estudio de vulnerabilidad estructural real (NSR-10 Título A.10).';

-- Mismo patron de RLS ya establecido esta sesion: publica de solo lectura.
alter table sisben_vulnerabilidad_vivienda_municipio enable row level security;
create policy "public_read_sisben_vulnerabilidad_vivienda_municipio"
  on sisben_vulnerabilidad_vivienda_municipio for select to public using (true);
