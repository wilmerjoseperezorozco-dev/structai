import { createBrowserClient } from "@supabase/ssr";

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Debe coincidir exactamente con el CHECK de public.profiles.plan en
// Supabase (verificado en vivo 2026-08-26: CHECK (plan = ANY (ARRAY['free',
// 'pro', 'enterprise']))). "pro_anual" NO es un valor real de esta columna
// — es solo una variante de precio (facturación anual) para el catálogo de
// PLANES en freemium.ts; un usuario en modo anual igual queda con plan='pro'
// en la base. Antes este tipo decía "free"|"pro"|"pro_anual" (sin
// "enterprise", con un "pro_anual" que la base rechazaría) — desajuste real
// entre el código y el constraint, corregido en la auditoría de RLS/schema.
export type UserPlan = "free" | "pro" | "enterprise";

export interface UserProfile {
  id: string;
  email: string;
  nombre: string;
  plan: UserPlan;
  apu_usados_mes: number;
  proyectos_count: number;
  created_at: string;
}
