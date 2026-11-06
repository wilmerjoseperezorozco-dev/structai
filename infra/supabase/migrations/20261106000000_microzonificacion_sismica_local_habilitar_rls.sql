-- Corrige hallazgo del linter de Supabase (2026-11-06, nivel ERROR):
-- microzonificacion_sismica_local (migracion 20260930000000) se creo con una
-- politica de lectura para usuarios autenticados pero SIN habilitar RLS, asi
-- que la politica nunca se aplicaba y la tabla quedaba expuesta (lectura y
-- escritura) a cualquier cliente con la anon key via PostgREST. El backend
-- usa la service key (ignora RLS), asi que habilitarlo no cambia su
-- comportamiento -- solo cierra el acceso publico de escritura.
alter table public.microzonificacion_sismica_local enable row level security;
