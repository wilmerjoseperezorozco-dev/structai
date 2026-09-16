-- Sistema de feedback cerrado (idea 7 del roadmap, 2026-09-16): reusa
-- consultas_history en vez de crear una tabla nueva redundante -- cada
-- /ask y /consultar YA hace un insert ahí con pregunta/respuesta/normas
-- (ver registrar_consulta() en main.py), agregar feedback a la MISMA fila
-- evita duplicar ese contenido en una segunda tabla. RLS de UPDATE ya
-- existe (consultas_update_own, auth.uid() = user_id, con WITH CHECK) --
-- no hace falta política nueva, el usuario ya puede actualizar su propia
-- fila.
alter table public.consultas_history
  add column if not exists feedback_util boolean,          -- null = sin feedback, true = util, false = no util
  add column if not exists feedback_comentario text;

create index if not exists idx_consultas_feedback_negativo
  on public.consultas_history(created_at desc)
  where feedback_util = false;

comment on column public.consultas_history.feedback_util is
'null = sin feedback todavia. true/false = boton util/no-util que el usuario presiono sobre esa respuesta especifica (idea 7, 2026-09-16).';
