/**
 * Cliente tipado para el backend FastAPI de StructAI
 * Base URL: NEXT_PUBLIC_API_URL (default http://localhost:8000)
 */

import { supabase } from "@/lib/supabase";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────────────

export interface FuenteChunk {
  norma: string;
  seccion: string;
  contenido_preview: string;
  score: number;
}

export interface AskResponse {
  respuesta: string;
  normas_citadas: string[];
  normas_detectadas_router: string[];
  fuentes: FuenteChunk[];
  chunks_usados: number;
  latencia_ms: number;
}

export interface APUItem {
  id: string;
  descripcion: string;
  unidad: string;
  capitulo: string;
  precio_unitario: number;
  ic90_inf: number;
  ic90_sup: number;
  incertidumbre_pct: number;
  norma_ref?: string;
}

export interface APUDesglose {
  actividad_id: string;
  descripcion: string;
  unidad: string;
  capitulo: string;
  costo_materiales: number;
  costo_mano_obra: number;
  costo_equipo: number;
  costo_directo: number;
  aiu: number;
  precio_unitario: number;
  pu_p05: number;
  pu_p95: number;
  pu_std: number;
  norma_ref?: string;
  uuid_trazabilidad: string;
  timestamp: string;
}

export interface DeteccionElemento {
  clase: string;
  confianza: number;
  bbox: [number, number, number, number];
  apu_sugerido_id?: string;
  apu_descripcion?: string;
  alerta_seguridad?: string;
  norma_ref_seguridad?: string;
}

export interface DetectResponse {
  elementos_detectados: DeteccionElemento[];
  imagen_ancho: number;
  imagen_alto: number;
  modelo_version: string;
  latencia_ms: number;
  modo: "onnx" | "stub" | "stub_fallback";
}

export interface HealthResponse {
  status: string;
  version: string;
  modulos: {
    rag_multi_norma: boolean;
    motor_apu: boolean;
    yolo_onnx: boolean;
    yolo_deps: boolean;
  };
  apu_count: number;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  // /ask, /consultar, /detect y /apu/calculate requieren JWT de Supabase en
  // el backend — se adjunta acá para no repetirlo en cada función de abajo.
  // Endpoints que no lo requieren (/health, /apu/list) simplemente lo ignoran.
  const { data: { session } } = await supabase.auth.getSession();
  const authHeader: Record<string, string> = session?.access_token
    ? { Authorization: `Bearer ${session.access_token}` }
    : {};

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Accept": "application/json", ...authHeader, ...init?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Como api(), pero para respuestas binarias (.xlsx) en vez de JSON. */
async function apiBlob(path: string, init?: RequestInit): Promise<Blob> {
  const { data: { session } } = await supabase.auth.getSession();
  const authHeader: Record<string, string> = session?.access_token
    ? { Authorization: `Bearer ${session.access_token}` }
    : {};

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...authHeader, ...init?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.blob();
}

/** Dispara la descarga de un Blob en el navegador con el nombre dado. */
export function descargarBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ── Endpoints ────────────────────────────────────────────────────────────────

/** Consulta normativa RAG multi-norma NTC/NSR-10 */
export async function askNorma(
  pregunta: string,
  norma_hint?: string,
  top_k = 6
): Promise<AskResponse> {
  return api<AskResponse>("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pregunta, norma_hint, top_k }),
  });
}

/** Detecta elementos estructurales en imagen (YOLO ONNX / stub) */
export async function detectImage(file: File): Promise<DetectResponse> {
  const form = new FormData();
  form.append("image", file);
  return api<DetectResponse>("/detect", { method: "POST", body: form });
}

/** Lista todos los APUs del catálogo Construdata 2026 */
export async function listAPU(): Promise<APUItem[]> {
  return api<APUItem[]>("/apu/list");
}

/** Calcula APU completo con Monte Carlo para una actividad */
export async function calculateAPU(
  actividad_id: string,
  cantidad = 1,
  proyecto_nombre?: string
): Promise<APUDesglose> {
  const form = new FormData();
  form.append("actividad_id", actividad_id);
  form.append("cantidad", String(cantidad));
  if (proyecto_nombre) form.append("proyecto_nombre", proyecto_nombre);
  return api<APUDesglose>("/apu/calculate", { method: "POST", body: form });
}

/** Descarga la plantilla .xlsx para calcular APU en lote */
export async function descargarPlantillaAPU(): Promise<Blob> {
  return apiBlob("/apu/plantilla");
}

/** Sube una plantilla .xlsx llena y devuelve el .xlsx con el presupuesto calculado */
export async function calcularLoteAPU(file: File): Promise<Blob> {
  const form = new FormData();
  form.append("archivo", file);
  return apiBlob("/apu/calculate-batch", { method: "POST", body: form });
}

/** Health check del backend */
export async function healthCheck(): Promise<HealthResponse> {
  return api<HealthResponse>("/health");
}

/** Debug: qué normas detecta el router */
export async function debugRoute(q: string) {
  return api<{ query: string; normas_detectadas: string[]; total: number }>(
    `/ask/route?q=${encodeURIComponent(q)}`
  );
}

// ── Formatters ───────────────────────────────────────────────────────────────

export const formatCOP = (n: number) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);

export const CLASE_LABEL: Record<string, string> = {
  // Modelo de elementos estructurales (packages/yolo/) — 7 clases, foco
  // actual. Ver packages/yolo/README.md para el estado del dataset/entrenamiento.
  acero_refuerzo: "Acero de refuerzo",
  viga:           "Viga estructural",
  columna:        "Columna estructural",
  muro:           "Muro",
  formaleta:      "Formaleta / encofrado",
  tuberia:        "Tubería",
  trabajador:     "Trabajador",
  // Clases de un catálogo APU más amplio sin modelo entrenado correspondiente
  // (no forman parte de CLASES_MODELO en apps/api/main.py todavía)
  placa_aligerada: "Placa aligerada",
  muro_bloque_15:  "Muro bloque e=15 cm",
  muro_bloque_10:  "Muro bloque e=10 cm",
  muro_concreto:   "Muro concreto 10 cm",
  zapata:          "Zapata aislada",
  excavacion:      "Excavación",
};
