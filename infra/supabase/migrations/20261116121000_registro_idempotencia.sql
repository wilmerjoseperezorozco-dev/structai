-- Registro de idempotencia de los pasos con efectos (#221, fase 2; dag_proyecto.flujo.RegistroEfectos).
-- Una fila por (flujo, paso, idempotency_key): repetir la llave devuelve el resultado registrado sin repetir el efecto, y
-- repetirla con otras entradas (hash_entrada distinto) es un conflicto. La llave primaria es la garantía: dos instancias
-- de Cloud Run que intenten el mismo efecto a la vez no pueden registrar dos veces (gana el primer INSERT).
-- Las filas expiran (expira_en): la idempotencia protege reintentos, no es un historial. Tamaño esperado: KB.
-- RLS habilitado y sin políticas a propósito (mismo criterio que rag_cache_respuestas): solo el backend con service_role.

create table if not exists public.idempotencia_efectos (
  llave text primary key,              -- sha256(flujo | paso | idempotency_key)
  flujo text not null,
  paso text not null,
  hash_entrada text not null,          -- sha256 de los parámetros y artefactos de entrada del paso
  artefacto jsonb not null,            -- Artefacto.a_dict() del efecto ya hecho
  creado_en timestamptz not null default now(),
  expira_en timestamptz not null default now() + interval '7 days'
);

alter table public.idempotencia_efectos enable row level security;

create index if not exists idx_idempotencia_efectos_expira on public.idempotencia_efectos(expira_en);

comment on table public.idempotencia_efectos is
'Registro de idempotencia de pasos con efectos (#221 fase 2). Llave primaria = garantía de un solo efecto por idempotency_key. Sin políticas RLS a propósito: uso interno del backend vía service_role.';
