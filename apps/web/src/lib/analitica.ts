/**
 * Eventos de analítica sin contenido (Umami). Inerte si no hay NEXT_PUBLIC_UMAMI_WEBSITE_ID.
 * Regla de privacidad: NUNCA se envía el texto de una pregunta, un nombre de proyecto ni datos
 * del usuario. Solo nombres de evento de una lista cerrada y propiedades de tipo categoría.
 */
export const EVENTOS_PERMITIDOS = [
  "consulta_enviada",
  "consulta_sin_resultado",
  "norma_citada",
  "motor_usado",
  "informe_descargado",
  "aviso_responsabilidad_visto",
  "error_api",
] as const;

export type NombreEvento = (typeof EVENTOS_PERMITIDOS)[number];

// Propiedades permitidas: categorías cortas (sin espacios ni texto libre).
const PROPIEDADES_PERMITIDAS = new Set(["motor", "norma_titulo", "pais", "codigo_error"]);
const CATEGORIA = /^[A-Za-z0-9_.-]{1,32}$/;

type Propiedades = Record<string, string | number | boolean>;

declare global {
  interface Window {
    umami?: { track: (nombre: string, datos?: Propiedades) => void };
  }
}

export function propiedadesSeguras(props: Propiedades = {}): Propiedades {
  const salida: Propiedades = {};
  for (const [clave, valor] of Object.entries(props)) {
    if (!PROPIEDADES_PERMITIDAS.has(clave)) continue;
    if (typeof valor === "string" && !CATEGORIA.test(valor)) continue;
    salida[clave] = valor;
  }
  return salida;
}

export function registrarEvento(nombre: NombreEvento, props: Propiedades = {}): void {
  if (typeof window === "undefined" || !window.umami) return;
  if (!EVENTOS_PERMITIDOS.includes(nombre)) return;
  try {
    window.umami.track(nombre, propiedadesSeguras(props));
  } catch {
    // La analítica nunca debe romper la aplicación.
  }
}
