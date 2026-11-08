-- Grafo de referencias cruzadas de la NSR-10 (issue #110 / evolución KAG, fase 2).
-- Una arista = un chunk que cita un numeral («sección F.4.3.3.2», «Capítulo A.13»...).
-- Nodo destino = numeral, no chunk: una sección puede estar partida en varios chunks (sufijos _p1, _r1, _q1).
-- Resolución: 'exacta' (existe un chunk con ese numeral), 'prefijo' (solo existen subnumerales, p. ej. un capítulo),
-- 'sin_destino' (el numeral citado no está en el corpus; es un hueco de ingesta o un numeral mal leído).
-- Sin políticas RLS, igual que nsr10_chunks: solo la clave de servicio lee y escribe.
create table if not exists public.normas_referencias_cruzadas (
  id bigint generated always as identity primary key,
  fuente_chunk_id text not null references public.nsr10_chunks(id) on delete cascade,
  numeral_fuente text,
  palabra_clave text not null,
  numeral_destino text not null,
  resolucion text not null check (resolucion in ('exacta', 'prefijo', 'sin_destino')),
  n_chunks_destino integer not null default 0,
  unique (fuente_chunk_id, palabra_clave, numeral_destino)
);
create index if not exists idx_ref_cruz_destino on public.normas_referencias_cruzadas (numeral_destino);
create index if not exists idx_ref_cruz_fuente on public.normas_referencias_cruzadas (fuente_chunk_id);
alter table public.normas_referencias_cruzadas enable row level security;

with num as (
  select id, upper(substring(seccion from '^\s*([A-Ka-k][.\-]\d+(?:\.\d+)*)')) as n
  from public.nsr10_chunks where seccion ~ '^\s*[A-Ka-k][.\-]\d'
), refs as (
  select distinct c.id as src, upper(substring(c.seccion from '^\s*([A-Ka-k][.\-]\d+(?:\.\d+)*)')) as own,
         case when lower(m[1]) like 'secc%' then 'seccion' when lower(m[1]) like 'numeral%' then 'numeral'
              when lower(m[1]) like 'cap%' then 'capitulo' when lower(m[1]) like 'ap%' then 'apendice' else 'titulo' end as kw,
         upper(regexp_replace(m[2], '[.\-]+$', '')) as dest
  from public.nsr10_chunks c,
  lateral regexp_matches(c.texto, '(secci[oó]n(?:es)?|numeral(?:es)?|cap[ií]tulo|t[ií]tulo|ap[eé]ndice)\s+([A-K][.\-]\d+(?:\.\d+)*)', 'gi') as m
)
insert into public.normas_referencias_cruzadas (fuente_chunk_id, numeral_fuente, palabra_clave, numeral_destino, resolucion, n_chunks_destino)
select r.src, r.own, r.kw, r.dest,
  case when ex.n > 0 then 'exacta' when pf.n > 0 then 'prefijo' else 'sin_destino' end,
  case when ex.n > 0 then ex.n else pf.n end
from refs r
cross join lateral (select count(*) n from num where num.n = r.dest) ex
cross join lateral (select count(*) n from num where num.n like r.dest || '.%' or num.n like r.dest || '-%') pf
where r.dest is distinct from r.own
on conflict do nothing;
