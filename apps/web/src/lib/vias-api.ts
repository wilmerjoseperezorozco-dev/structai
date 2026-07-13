/**
 * Cliente tipado para el motor Vías (diseño geométrico, pavimentos, mantenimiento,
 * topografía y verificación de materiales NTC) — apps/api/routers/vias.py
 * Mismo helper que src/lib/aquai-api.ts y src/lib/geopot-api.ts, para no duplicar
 * el manejo de errores del backend.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
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

export const consultarSaludVias = () => api<Record<string, unknown>>("/vias/salud");

export const validarDisenoGeometrico = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/geometrico", payload);

export const disenarPavimento = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/pavimentos", payload);

export const diagnosticarMantenimiento = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/mantenimiento", payload);

export const verificarCierreNivelacion = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/topografia/cierre", payload);

export const verificarNTC2017 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/2017", payload);

export const verificarNTC4342 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/4342", payload);

export const verificarNTC121 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/121", payload);

export const verificarNTC1299 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/1299", payload);

export const verificarNTC1362 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/1362", payload);

export const verificarNTC3459 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/3459", payload);

export const verificarNTC3493 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/3493", payload);

export const verificarNTC3502 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/3502", payload);

export const verificarNTC3760 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/3760", payload);

export const verificarNTC4018 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/4018", payload);

export const verificarNTC4024 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/4024", payload);

export const verificarNTC4924Agregado = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/4924/agregado", payload);

export const verificarNTC4924Mamposteria = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/4924/mamposteria", payload);

export const verificarNTC5147 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/5147", payload);

export const buscarTerminoNTC6008 = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/vias/ntc/6008", payload);
