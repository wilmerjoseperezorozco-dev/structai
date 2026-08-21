-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260713022831
-- Nombre: motor_chunks_rag_dominio
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

create table if not exists public.motor_chunks (
  id bigint generated always as identity primary key,
  motor text not null,               -- 'aquai' | 'geopot' | 'vias' | 'gerencia'
  seccion text not null,             -- ej. 'RAS B.2.1 — Dotación neta'
  titulo text not null,
  contenido text not null,
  norma_ref text not null,
  embedding vector(384),
  created_at timestamptz not null default now()
);

alter table public.motor_chunks enable row level security;

create policy public_read_motor_chunks on public.motor_chunks
  for select using (true);

create policy service_write_motor_chunks on public.motor_chunks
  for all using (true) with check (true);

create index if not exists idx_motor_chunks_motor on public.motor_chunks(motor);

create or replace function public.search_knowledge(
  query_embedding vector,
  query_text text,
  p_norma text default null::text,
  match_count integer default 8,
  rrf_k integer default 60,
  p_motor text default null::text
)
returns table(chunk_id text, norma text, seccion text, contenido text, score double precision, metadata jsonb)
language plpgsql
stable
set search_path to 'public', 'extensions'
as $function$
BEGIN
  RETURN QUERY
  WITH
  fuente AS (
    SELECT nc.id::text AS f_id, nc.capitulo AS f_norma, nc.seccion AS f_seccion, nc.texto AS f_contenido, nc.embedding AS f_embedding, NULL::text AS f_motor
      FROM public.nsr10_chunks nc
    UNION ALL
    SELECT tc.id::text AS f_id, tc.norma AS f_norma, tc.seccion AS f_seccion, tc.contenido AS f_contenido, tc.embedding AS f_embedding, NULL::text AS f_motor
      FROM public.ntc_chunks tc
    UNION ALL
    SELECT mc.id::text AS f_id, mc.norma_ref AS f_norma, mc.seccion AS f_seccion, mc.contenido AS f_contenido, mc.embedding AS f_embedding, mc.motor AS f_motor
      FROM public.motor_chunks mc
  ),
  filtrado AS (
    SELECT f.f_id, f.f_norma, f.f_seccion, f.f_contenido, f.f_embedding
    FROM fuente f
    WHERE (p_norma IS NULL OR f.f_norma ILIKE '%' || p_norma || '%')
      AND (p_motor IS NULL OR f.f_motor = p_motor)
  ),
  sem AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido,
           ROW_NUMBER() OVER (ORDER BY ft.f_embedding <=> query_embedding) AS rnk
    FROM filtrado ft
    WHERE ft.f_embedding IS NOT NULL
    ORDER BY ft.f_embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  lex AS (
    SELECT ft.f_id, ft.f_norma, ft.f_seccion, ft.f_contenido,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(to_tsvector('spanish', ft.f_contenido), plainto_tsquery('spanish', query_text)) DESC
           ) AS rnk
    FROM filtrado ft
    WHERE to_tsvector('spanish', ft.f_contenido) @@ plainto_tsquery('spanish', query_text)
    LIMIT match_count * 3
  ),
  rrf AS (
    SELECT
      COALESCE(s.f_id, l.f_id)             AS r_id,
      COALESCE(s.f_norma, l.f_norma)       AS r_norma,
      COALESCE(s.f_seccion, l.f_seccion)   AS r_seccion,
      COALESCE(s.f_contenido, l.f_contenido) AS r_contenido,
      (
        COALESCE(1.0 / (rrf_k + s.rnk), 0) +
        COALESCE(1.0 / (rrf_k + l.rnk), 0)
      )::float8 AS rrf_score
    FROM sem s
    FULL OUTER JOIN lex l ON s.f_id = l.f_id
  )
  SELECT
    r.r_id           AS chunk_id,
    r.r_norma        AS norma,
    r.r_seccion      AS seccion,
    r.r_contenido    AS contenido,
    r.rrf_score      AS score,
    '{}'::jsonb      AS metadata
  FROM rrf r
  ORDER BY r.rrf_score DESC
  LIMIT match_count;
END;
$function$;
