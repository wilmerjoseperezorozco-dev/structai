import { createBrowserClient } from "@supabase/ssr";

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export type UserPlan = "free" | "pro" | "pro_anual";

export interface UserProfile {
  id: string;
  email: string;
  nombre: string;
  plan: UserPlan;
  apu_usados_mes: number;
  proyectos_count: number;
  created_at: string;
}
