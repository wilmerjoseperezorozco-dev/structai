-- Corrige un hallazgo real del advisor de seguridad de Supabase (ERROR):
-- 11 tablas públicas expuestas via PostgREST sin RLS activado -- sin
-- politica, el rol anon podria potencialmente escribir/borrar en tablas
-- de referencia que deberian ser solo lectura. Mismo patron ya usado en
-- nsr10_chunks/apu_precios_referencia: RLS activado + politica SELECT
-- publica (qual=true), sin politica de escritura para anon/authenticated
-- (el service_role usado por los scripts de carga bypassa RLS por diseño
-- de Supabase, no necesita politica explicita).

alter table public.ideam_estaciones_caudal enable row level security;
alter table public.ideam_caudal_historico enable row level security;
alter table public.ideam_caudal_estadisticas_mes enable row level security;
alter table public.sgc_amenaza_sismica_municipios enable row level security;
alter table public.igac_suelos_ufh enable row level security;
alter table public.invias_insumos_precios enable row level security;
alter table public.invias_insumos enable row level security;
alter table public.invias_provincias enable row level security;
alter table public.invias_actividad_insumos enable row level security;
alter table public.invias_actividad_costos enable row level security;
alter table public.invias_actividades enable row level security;

create policy "public_read_ideam_estaciones_caudal" on public.ideam_estaciones_caudal for select to public using (true);
create policy "public_read_ideam_caudal_historico" on public.ideam_caudal_historico for select to public using (true);
create policy "public_read_ideam_caudal_estadisticas_mes" on public.ideam_caudal_estadisticas_mes for select to public using (true);
create policy "public_read_sgc_amenaza_sismica_municipios" on public.sgc_amenaza_sismica_municipios for select to public using (true);
create policy "public_read_igac_suelos_ufh" on public.igac_suelos_ufh for select to public using (true);
create policy "public_read_invias_insumos_precios" on public.invias_insumos_precios for select to public using (true);
create policy "public_read_invias_insumos" on public.invias_insumos for select to public using (true);
create policy "public_read_invias_provincias" on public.invias_provincias for select to public using (true);
create policy "public_read_invias_actividad_insumos" on public.invias_actividad_insumos for select to public using (true);
create policy "public_read_invias_actividad_costos" on public.invias_actividad_costos for select to public using (true);
create policy "public_read_invias_actividades" on public.invias_actividades for select to public using (true);
