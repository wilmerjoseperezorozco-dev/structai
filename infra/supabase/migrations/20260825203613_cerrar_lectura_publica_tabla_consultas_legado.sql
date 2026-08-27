-- La tabla "consultas" es legado/en desuso (0 filas, ya documentado en
-- infra/supabase/SCHEMA.md, sin ninguna referencia en apps/api ni
-- packages/construdata -- confirmado con grep antes de tocar nada).
-- Sin embargo tenia una politica RLS real que permitia a CUALQUIER
-- usuario autenticado leer TODAS las filas (incluyendo columnas
-- "pregunta"/"respuesta"/"usuario" -- contenido potencialmente sensible
-- si la tabla llegara a usarse de nuevo sin corregir esto primero).
-- Encontrado en repaso de RLS pedido explicitamente por el usuario
-- 2026-08-25. Cero impacto funcional (tabla vacia, sin codigo que la
-- consulte), cierre puro de una politica insegura que quedo huerfana.
drop policy if exists "auth_read_consultas" on public.consultas;

-- service_all_consultas (service_role, ALL) se deja intacta: el backend
-- con la service key sigue pudiendo escribir/leer si algun dia se
-- reactiva esta tabla -- lo que se cierra es la lectura publica sin
-- filtro por usuario, no el acceso administrativo.
