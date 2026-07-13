import type { UserPlan } from "./supabase";

export const PLANES = {
  free: {
    nombre: "Gratis",
    precio_mes: 0,
    precio_anual: 0,
    apu_por_mes: 5,
    proyectos_max: 1,
    export_pdf: false,
    nsr10_completo: true,
    historial_dias: 7,
    badge: null,
  },
  pro: {
    nombre: "Pro",
    precio_mes: 19900,
    precio_anual: 159000,
    apu_por_mes: Infinity,
    proyectos_max: Infinity,
    export_pdf: true,
    nsr10_completo: true,
    historial_dias: Infinity,
    badge: "PRO",
  },
  pro_anual: {
    nombre: "Pro Anual",
    precio_mes: 13250,
    precio_anual: 159000,
    apu_por_mes: Infinity,
    proyectos_max: Infinity,
    export_pdf: true,
    nsr10_completo: true,
    historial_dias: Infinity,
    badge: "PRO",
  },
} satisfies Record<UserPlan, object>;

export function puedeCalcularAPU(plan: UserPlan, usados: number): boolean {
  const limite = PLANES[plan].apu_por_mes;
  return limite === Infinity || usados < limite;
}

export function puedeCrearProyecto(plan: UserPlan, count: number): boolean {
  const max = PLANES[plan].proyectos_max;
  return max === Infinity || count < max;
}

export function formatCOP(n: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);
}
