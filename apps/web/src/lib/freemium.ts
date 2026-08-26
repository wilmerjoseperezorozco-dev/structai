import type { UserPlan } from "./supabase";

// Wompi payment link — activación manual del plan Pro (2026-08-01): el botón
// "Activar Pro" abre este link de pago; cuando Wompi confirma el pago, el
// plan se activa a mano en Supabase desde el panel del owner. Webhook
// automático queda para cuando haya volumen suficiente para justificarlo
// (ver notas de la sesión). El link por defecto es de MODO PRUEBA
// (test_VPOS) — antes de cobrar dinero real hay que reemplazar
// NEXT_PUBLIC_WOMPI_CHECKOUT_URL por el link de producción desde el panel
// de Wompi (Cobros > Links de pago).
export const WOMPI_CHECKOUT_URL =
  process.env.NEXT_PUBLIC_WOMPI_CHECKOUT_URL || "https://checkout.wompi.co/l/test_VPOS_dYJ3Uh";
export const WOMPI_ES_MODO_PRUEBA = WOMPI_CHECKOUT_URL.includes("/l/test_");

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
  // Precio de lanzamiento ("fundador") decidido 2026-08-26 para maximizar
  // adopción del primer semillero universitario: el costo real de LLM por
  // consulta (respaldo OpenAI gpt-4o-mini cuando se agota la cuota gratis
  // de Groq) es del orden de centavos de dólar por miles de consultas, así
  // que el margen aguanta un precio bajo — la fricción de adopción es el
  // riesgo real a este punto, no el costo. Antes: $19.900/mes. Antes de
  // subirlo, comunicarlo explícitamente como "precio de lanzamiento" a
  // quien ya esté pagando, para no generar mala voluntad.
  pro: {
    nombre: "Pro",
    precio_mes: 9900,
    precio_anual: 79000,
    apu_por_mes: Infinity,
    proyectos_max: Infinity,
    export_pdf: true,
    nsr10_completo: true,
    historial_dias: Infinity,
    badge: "PRO",
  },
  // Cotización a medida, no autoservicio: todavía no hay ni un solo cliente
  // institucional (universidad, constructora) para calibrar un precio fijo
  // de catálogo — fijar uno ahora arriesgaría subvalorar el primer contrato
  // real. El CTA en /pricing lleva a contacto directo, no a Wompi.
  enterprise: {
    nombre: "Enterprise",
    precio_mes: null,
    precio_anual: null,
    apu_por_mes: Infinity,
    proyectos_max: Infinity,
    export_pdf: true,
    nsr10_completo: true,
    historial_dias: Infinity,
    badge: "ENTERPRISE",
  },
} satisfies Record<UserPlan, object>;

// Variante de facturación anual de Pro — NO es un UserPlan real (ver el
// comentario en supabase.ts): un usuario en esta modalidad igual queda
// guardado con plan="pro" en la base, esto es solo para mostrar el precio
// con descuento anual en /pricing. Mismo ~33% de descuento que ya existía
// antes de bajar el precio mensual de Pro.
export const PRO_ANUAL = {
  nombre: "Pro Anual",
  precio_mes: 6583,
  precio_anual: 79000,
  ...PLANES.pro,
};

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
