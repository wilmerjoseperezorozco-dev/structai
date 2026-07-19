import type { HealthResponse } from "./health";

export interface ApiClientOptions {
  baseUrl: string;
  getAccessToken: () => Promise<string | null>;
}

export interface ApiClient {
  health: () => Promise<HealthResponse>;
  fetch: (path: string, init?: RequestInit) => Promise<Response>;
}

// Cliente HTTP puro, sin dependencias de React/Next/Expo — cada app le pasa
// su propia forma de obtener el token de sesión (createBrowserClient en
// apps/web, AsyncStorage en apps/native). La UI de cada app sigue siendo
// 100% propia; esto solo evita reescribir la lógica de fetch+auth dos veces.
export function createApiClient({ baseUrl, getAccessToken }: ApiClientOptions): ApiClient {
  async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
    const token = await getAccessToken();
    return fetch(`${baseUrl}${path}`, {
      ...init,
      headers: {
        ...init.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  }

  async function health(): Promise<HealthResponse> {
    const res = await apiFetch("/health");
    if (!res.ok) throw new Error(`API respondió ${res.status}`);
    return res.json();
  }

  return { health, fetch: apiFetch };
}
