-- Apéndice A-4: registrar qué decreto modificó cada municipio y conservar el valor original de 2010.
-- Verificado el 2026-11-07 contra el anexo del Decreto 092 de 2011 (págs. 9-11 del anexo): 29 municipios modificados.
-- Pendientes sin verificar (anexos no obtenidos): Decretos 945/2017, 2113/2019, 1711/2021 (Supía), 1401/2023 y 1166/2025.

alter table nsr10_apendice_a4_municipios
  add column if not exists modificado_por text,
  add column if not exists valores_originales_2010 jsonb,
  add column if not exists observacion text;

alter table nsr10_apendice_a4_municipios
  alter column vigencia set default 'texto original Decreto 926 de 2010; modificaciones del Decreto 092 de 2011 verificadas; las de 945/2017, 2113/2019, 1711/2021, 1401/2023 y 1166/2025 sin verificar';

comment on column nsr10_apendice_a4_municipios.modificado_por is 'Decreto cuyo anexo modifica el valor de este municipio (solo los verificados contra el texto del anexo).';
comment on column nsr10_apendice_a4_municipios.valores_originales_2010 is 'Valores del texto original de 2010 cuando un decreto posterior los modificó.';
