/**
 * Cliente tipado para el motor AquAI (RAS 2000) — apps/api/routers/aquai.py
 * Mismo helper `api<T>()` y BASE que src/lib/api.ts, para no duplicar el
 * manejo de errores del backend de StructAI.
 */

import { supabase } from "@/lib/supabase";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  // Los endpoints de cálculo de este router exigen JWT de Supabase (auth.py).
  const { data: { session } } = await supabase.auth.getSession();
  const authHeader: Record<string, string> = session?.access_token
    ? { Authorization: `Bearer ${session.access_token}` }
    : {};

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...authHeader, ...init?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return api<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// ── Endpoints — cada uno mapea 1:1 con apps/api/routers/aquai.py ─────────────

export const proyectarPoblacion = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/poblacion", payload);

export const calcularCaudales = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/caudales", payload);

export const calcularHazenWilliams = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/hidraulica", payload);

export const calcularHidrologia = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/hidrologia", payload);

export const calcularManning = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/hidraulica/manning", payload);

export const calcularAriete = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/hidraulica/ariete", payload);

export const calcularBombeo = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/hidraulica/bombeo", payload);

export const calcularPTAP = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/saneamiento/ptap", payload);

export const calcularPTAR = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/saneamiento/ptar", payload);

export const calcularTarifa = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/tarifas/calcular", payload);

export const generarReporteSUI = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/aquai/sui/reporte", payload);

export async function aquaiSalud(): Promise<{ estado: string; motor: string; norma_base: string }> {
  return api("/aquai/salud");
}

// ── Formatters compartidos por los módulos ────────────────────────────────────

export const formatNum = (n: unknown, decimals = 2): string => {
  if (typeof n !== "number" || Number.isNaN(n)) return String(n);
  return n.toLocaleString("es-CO", { maximumFractionDigits: decimals, minimumFractionDigits: 0 });
};

export const humanLabel = (key: string): string =>
  key
    .replace(/_ls$/, " (L/s)")
    .replace(/_m3s$/, " (m³/s)")
    .replace(/_m3_dia$/, " (m³/día)")
    .replace(/_mca$/, " (m.c.a.)")
    .replace(/_ms$/, " (m/s)")
    .replace(/_mm$/, " (mm)")
    .replace(/_mm_h$/, " (mm/h)")
    .replace(/_min$/, " (min)")
    .replace(/_pct$/, " (%)")
    .replace(/_kw$/, " (kW)")
    .replace(/_kwh_mes$/, " (kWh/mes)")
    .replace(/_kg_dia$/, " (kg/día)")
    .replace(/_mg_l$/, " (mg/L)")
    .replace(/_cop$/, " (COP)")
    .replace(/_m$/, " (m)")
    .replace(/_/g, " ")
    .replace(/^./, (c) => c.toUpperCase());
