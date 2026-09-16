-- Caché de respuestas exactas -- idea 2 del roadmap de costos, la parte
-- barata: "misma pregunta = costo cero". Sin Redis/Memorystore (dinero
-- real que no se justifica al volumen actual, 47 consultas históricas
-- totales) -- Supabase ya está pagado y ya es compartido entre instancias
-- de Cloud Run, a diferencia de un cache en memoria del proceso que se
-- pierde en cada cold start / no se comparte entre instancias si
-- max-instances > 1.
--
-- Solo coincidencia EXACTA de pregunta normalizada (lowercase + trim +
-- espacios colapsados) -- nunca similitud semántica: dos preguntas
-- "parecidas" pueden tener respuestas correctas distintas, cachear por
-- similitud arriesgaría servir la respuesta equivocada para ahorrar un
-- llamado a Groq (que ya es gratis). Con expira_en: el corpus normativo
-- cambia por ingestas verbatim nuevas -- una respuesta cacheada para
-- siempre podría quedar desactualizada sin que nadie se entere.
--
-- Sin políticas RLS abiertas a propósito -- esta tabla es un detalle de
-- implementación interno del backend (siempre usa SUPABASE_SERVICE_KEY,
-- que ignora RLS), no un dato que un usuario final deba leer/escribir
-- directo. RLS igual queda ENABLED (mismo criterio "sin excepción" que el
-- resto del esquema, ver SCHEMA.md) para que anon/authenticated queden
-- denegados por defecto si algún día se expone la tabla sin querer.

create table if not exists public.rag_cache_respuestas (
  id text primary key,               -- sha256(ruta || '|' || pregunta_normalizada)
  ruta text not null,                -- 'ask' | 'ask_delegado' | 'ask_precios' -- pipelines distintos, cache separado
  pregunta_normalizada text not null,
  respuesta jsonb not null,
  creado_en timestamptz not null default now(),
  expira_en timestamptz not null,
  hits integer not null default 0,
  ultimo_hit_en timestamptz
);

alter table public.rag_cache_respuestas enable row level security;
-- Intencionalmente sin CREATE POLICY -- deny-all para anon/authenticated,
-- service_role (el backend) bypassa RLS siempre.

create index if not exists idx_rag_cache_expira on public.rag_cache_respuestas(expira_en);

comment on table public.rag_cache_respuestas is
'Caché de respuestas exactas del RAG (idea 2 del roadmap de costos, 2026-09-16). Solo coincidencia exacta de pregunta normalizada, con expiración -- nunca similitud semántica. Sin políticas RLS a propósito: uso interno del backend vía service_role únicamente.';
