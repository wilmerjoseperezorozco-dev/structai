-- Agrega el rol de plataforma (distinto del plan de suscripción) a profiles.
-- 'user' = comportamiento actual sin cambios. 'admin' = acceso a endpoints
-- administrativos del backend (ver require_admin() en apps/api/main.py).
-- No toca RLS: el rol se lee solo desde el backend con el cliente de
-- service_role (mismo patrón que profiles.plan en verificar_limite_*),
-- nunca desde el cliente con la clave anónima.
alter table public.profiles
  add column role text not null default 'user'
  check (role in ('user', 'admin'));

comment on column public.profiles.role is
  'Rol de plataforma (user/admin) — separado de profiles.plan (free/pro/enterprise), que es el nivel de suscripción.';
