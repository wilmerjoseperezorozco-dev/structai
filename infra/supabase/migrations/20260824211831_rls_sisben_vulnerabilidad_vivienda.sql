alter table sisben_vulnerabilidad_vivienda_municipio enable row level security;
create policy "public_read_sisben_vulnerabilidad_vivienda_municipio"
  on sisben_vulnerabilidad_vivienda_municipio for select to public using (true);
