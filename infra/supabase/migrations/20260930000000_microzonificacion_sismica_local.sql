create table if not exists public.microzonificacion_sismica_local (
  id bigint generated always as identity primary key,
  ciudad text not null,
  zona text not null,
  descripcion_zona text,
  -- Tabla de diseño (sismo de 475 años, 5% amortiguamiento) -- ecuacion A.2.6 sustitutiva
  fa_diseno numeric,
  fv_diseno numeric,
  tc_diseno_s numeric,
  tl_diseno_s numeric,
  a0_diseno_g numeric,
  -- Tabla de seguridad limitada (sismo de 225 años, Titulo A.10) -- NULL si no aplica/no encontrado
  fa_seg_limitada numeric,
  fv_seg_limitada numeric,
  tc_seg_limitada_s numeric,
  tl_seg_limitada_s numeric,
  a0_seg_limitada_g numeric,
  -- Tabla de umbral de daño (sismo de 31 anios, 2% amortiguamiento, Titulo A.12) -- NULL si no aplica/no encontrado
  fa_umbral_dano numeric,
  fv_umbral_dano numeric,
  t_od_s numeric,
  t_cd_s numeric,
  t_ld_s numeric,
  a_od_g numeric,
  -- Trazabilidad de fuente -- nunca se presenta como dato sin decir de donde salio
  fuente text not null,
  fecha_decreto date,
  verificado_en_vivo date not null default current_date,
  created_at timestamptz not null default now(),
  unique (ciudad, zona)
);

comment on table public.microzonificacion_sismica_local is
  'Coeficientes de microzonificacion sismica LOCAL (Bogota Decreto 523/2010, Medellin, etc.) que reemplazan legalmente A.2.4/A.2.6 de NSR-10 para esas ciudades (A.2.9.1). Investigacion/ingesta del issue #76 -- NO esta wireado a load_engine.py/sgc_amenaza_sismica.py todavia, a peticion explicita de no tocar produccion sin decision aparte.';
