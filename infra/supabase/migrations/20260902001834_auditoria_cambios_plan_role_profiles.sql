-- Auditoria real de cambios a profiles.plan y profiles.role (punto 5 del
-- plan Data First, ver memoria privada del usuario --
-- project_structai_data_first_mejoras). Hallazgo real que corrigio el
-- alcance original: /admin/usuarios es SOLO LECTURA (confirmado leyendo
-- apps/api/main.py, sin ninguna mutacion en todo el codigo de apps/api) --
-- el cambio de plan/rol de un usuario ocurre 100% por SQL directo o el
-- panel de Supabase, fuera de la aplicacion. Un log a nivel de aplicacion
-- atado a un endpoint inexistente habria sido trabajo hueco. Por eso esto
-- es un trigger de Postgres: audita el cambio real venga de donde venga
-- (API futura, panel de Supabase, SQL Editor), no solo de un endpoint.

create table if not exists public.profiles_audit_log (
  id bigint generated always as identity primary key,
  profile_id uuid not null references public.profiles(id) on delete cascade,
  campo text not null,
  valor_anterior text,
  valor_nuevo text,
  changed_by uuid,
  created_at timestamptz not null default now()
);

comment on table public.profiles_audit_log is
  'Auditoria real de cambios a profiles.plan y profiles.role, capturada '
  'por trigger a nivel de Postgres -- funciona sin importar si el cambio '
  'vino de la API, el panel de Supabase, o SQL directo. changed_by queda '
  'NULL cuando el cambio se hizo sin contexto de sesion autenticada '
  '(service_role/SQL Editor) -- limitacion real, documentada, no oculta.';

comment on column public.profiles_audit_log.changed_by is
  'auth.uid() en el momento del UPDATE. NULL si el cambio no tuvo '
  'contexto de sesion autenticada (ej. SQL Editor, service_role directo).';

alter table public.profiles_audit_log enable row level security;

-- Solo admin puede leer el log. Sin politicas de INSERT/UPDATE/DELETE
-- para authenticated/anon -- solo la funcion SECURITY DEFINER del
-- trigger (o service_role) puede escribir.
create policy "admin puede leer el log de auditoria de perfiles"
  on public.profiles_audit_log
  for select
  using (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and p.role = 'admin'
    )
  );

create or replace function public.log_profile_plan_role_change()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.plan is distinct from old.plan then
    insert into public.profiles_audit_log (profile_id, campo, valor_anterior, valor_nuevo, changed_by)
    values (new.id, 'plan', old.plan, new.plan, auth.uid());
  end if;
  if new.role is distinct from old.role then
    insert into public.profiles_audit_log (profile_id, campo, valor_anterior, valor_nuevo, changed_by)
    values (new.id, 'role', old.role, new.role, auth.uid());
  end if;
  return new;
end;
$$;

comment on function public.log_profile_plan_role_change() is
  'Trigger AFTER UPDATE en profiles -- registra en profiles_audit_log '
  'cualquier cambio real a plan o role, venga de donde venga.';

drop trigger if exists trigger_log_profile_plan_role_change on public.profiles;
create trigger trigger_log_profile_plan_role_change
  after update on public.profiles
  for each row
  when (old.plan is distinct from new.plan or old.role is distinct from new.role)
  execute function public.log_profile_plan_role_change();
