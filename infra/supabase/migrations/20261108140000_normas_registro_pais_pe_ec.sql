-- Issue #110: registro por país. Colombia sigue siendo primaria (default 'CO').
-- Aditiva: no cambia filas existentes ni el filtro de vigencia del RAG.
-- Los chunks de Perú/Ecuador no tienen norma_id, por lo que NO se enlazan aquí.

alter table normas_registro
  add column if not exists pais text not null default 'CO';

alter table normas_registro
  drop constraint if exists normas_registro_pais_iso2;
alter table normas_registro
  add constraint normas_registro_pais_iso2 check (pais ~ '^[A-Z]{2}$');

create index if not exists normas_registro_pais_idx on normas_registro (pais);

insert into normas_registro
  (codigo, nombre_completo, entidad_emisora, tipo, estado_vigencia, cadena_modificaciones, pais, notas_vigencia)
select 'PE-E030',
       'Norma Técnica E.030 Diseño Sismorresistente (Perú)',
       'Ministerio de Vivienda, Construcción y Saneamiento (Perú)',
       'otro', 'modificada', 'parcial', 'PE',
       '[2026-11-08] Corpus MIXTO: capítulos 1 y 5–9 y anexo 1 provienen de la edición RM 043-2019-VIVIENDA; capítulos 2–4 (ids E030-2026-CAP2/3/4) corresponden a la RM 183-2026-VIVIENDA (3-may-2026). Estado ''modificada'': la edición 2019 ya no es el texto único vigente. No se verificó si la RM 183-2026 sustituye también los capítulos 1 y 5–9; no usar como vigente sin esa comprobación. Chunks sin norma_id.'
where not exists (select 1 from normas_registro where codigo = 'PE-E030');

insert into normas_registro
  (codigo, nombre_completo, entidad_emisora, tipo, estado_vigencia, cadena_modificaciones, pais, notas_vigencia)
select 'EC-NEC-SE-DS',
       'NEC-SE-DS Peligro sísmico y requisitos de diseño sismo resistente (Ecuador)',
       'MIDUVI (Ecuador)',
       'otro', 'desconocido', 'no_revisada', 'EC',
       '[2026-11-08] Corpus cargado el 2026-08-25 desde el PDF oficial MIDUVI/MIT. Edición y vigencia posterior (reformas, actualizaciones) NO verificadas en fuente primaria. Chunks sin norma_id.'
where not exists (select 1 from normas_registro where codigo = 'EC-NEC-SE-DS');
