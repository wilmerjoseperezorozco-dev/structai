/**
 * Cliente tipado para el motor Gerencia (EVM + ML predictivo) — apps/api/routers/gerencia.py
 * Mismo helper que src/lib/geopot-api.ts, para no duplicar el manejo de errores del backend.
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

export const calcularSnapshot = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/evm/snapshot", payload);

export const analizarPortafolio = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/evm/portafolio", payload);

export const calcularRiesgo = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/ml/riesgo", payload);

export const calcularForecast = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/ml/forecast", payload);

export const calcularFechaTermino = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/ml/fecha-termino", payload);

export const detectarAnomalias = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/ml/anomalias", payload);

export const calcularCorrelacion = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/gerencia/ml/correlacion", payload);
