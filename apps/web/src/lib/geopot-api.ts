/**
 * Cliente tipado para el motor GeoPot (NSR-10 sísmica + laboratorio) — apps/api/routers/geopot.py
 * Mismo helper que src/lib/aquai-api.ts, para no duplicar el manejo de errores del backend.
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

export const consultarZonaSismica = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/sismica", payload);

export const resumenZonasSismicas = () =>
  api<Record<string, unknown>>("/geopot/sismica/resumen");

export const analizarConcreto = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/concreto", payload);

export const clasificarUSCS = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/suelos/uscs", payload);

export const clasificarAASHTO = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/suelos/aashto", payload);

export const analizarProctor = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/suelos/proctor", payload);

export const analizarCBR = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/suelos/cbr", payload);

export const analizarGranulometria = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/suelos/granulometria", payload);

export const verificarAgregadoGrueso = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/agregados/grueso", payload);

export const verificarAgregadoFino = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/agregados/fino", payload);

export const disenarMezcla = (payload: Record<string, unknown>) =>
  post<Record<string, unknown>>("/geopot/laboratorio/mezcla", payload);
