/**
 * Mensajes claros para los errores de Supabase Auth en el login y el registro.
 *
 * Caso real (2026-11-15): el servidor de correo de confirmación (SMTP) rechazó los envíos y Supabase respondió
 * 500 con un cuerpo sin mensaje; supabase-js lo convierte en un error cuyo `message` es "{}", y el formulario
 * mostraba literalmente "{}". Aquí cada caso conocido se traduce a una instrucción que la persona pueda seguir.
 */

type ErrorSupabase = { message?: string; status?: number; code?: string; name?: string };

const POR_CODIGO: Record<string, string> = {
  invalid_credentials: "Correo o contraseña incorrectos.",
  email_not_confirmed: "Tu correo aún no está confirmado. Revisa tu bandeja (y la carpeta de spam).",
  user_already_exists: "Ya existe una cuenta con este correo. Ingresa o recupera tu contraseña.",
  email_exists: "Ya existe una cuenta con este correo. Ingresa o recupera tu contraseña.",
  weak_password: "La contraseña es débil: usa al menos 8 caracteres con mayúscula, minúscula y número.",
  email_provider_disabled: "El registro está cerrado temporalmente. Intenta más tarde.",
  signup_disabled: "El registro está cerrado temporalmente. Intenta más tarde.",
  over_email_send_rate_limit: "Se enviaron demasiados correos en poco tiempo. Espera unos minutos e intenta de nuevo.",
  over_request_rate_limit: "Demasiados intentos seguidos. Espera un momento e intenta de nuevo.",
  email_address_invalid: "Ese correo no es válido. Revisa que esté bien escrito.",
  validation_failed: "Revisa el correo y la contraseña.",
};

export const MENSAJE_FALLA_CORREO =
  "No pudimos enviar el correo de confirmación. Tu solicitud quedó registrada: intenta de nuevo en unos minutos " +
  "o escríbenos y activamos tu cuenta.";

export function mensajeErrorAuth(err: unknown): string {
  const e = (err ?? {}) as ErrorSupabase;
  if (e.code && POR_CODIGO[e.code]) return POR_CODIGO[e.code];
  const msg = (e.message ?? "").trim();
  if (/password should contain|password should be at least/i.test(msg)) return POR_CODIGO.weak_password;
  if (/invalid login credentials/i.test(msg)) return POR_CODIGO.invalid_credentials;
  if (/already registered/i.test(msg)) return POR_CODIGO.user_already_exists;
  if (/error sending confirmation|sending.*email|smtp/i.test(msg)) return MENSAJE_FALLA_CORREO;
  // 500 sin mensaje legible ("{}" o vacío): en registro casi siempre es la falla del correo de confirmación.
  if (!msg || msg === "{}" || (e.status ?? 0) >= 500) return MENSAJE_FALLA_CORREO;
  if (/failed to fetch|network/i.test(msg)) return "Sin conexión con el servidor. Revisa tu internet e intenta de nuevo.";
  return msg;
}

// Dominios frecuentes y sus errores de tipeo más comunes.
const DOMINIOS = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "live.com", "icloud.com"];

function distancia(a: string, b: string): number {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}

/** Si el dominio parece un error de tipeo de uno frecuente ("gmai.com"), devuelve el correo corregido. */
export function sugerirCorreo(email: string): string | null {
  const [usuario, dominio] = email.trim().toLowerCase().split("@");
  if (!usuario || !dominio || DOMINIOS.includes(dominio)) return null;
  const mejor = DOMINIOS.map((d) => ({ d, k: distancia(dominio, d) })).sort((x, y) => x.k - y.k)[0];
  return mejor && mejor.k > 0 && mejor.k <= 2 ? `${usuario}@${mejor.d}` : null;
}

/** Requisitos que exige Supabase Auth en este proyecto (verificado en los registros del 2026-11-15). */
export function requisitosPassword(p: string) {
  return [
    { ok: p.length >= 8, texto: "8 caracteres o más" },
    { ok: /[a-z]/.test(p), texto: "una minúscula" },
    { ok: /[A-Z]/.test(p), texto: "una mayúscula" },
    { ok: /\d/.test(p), texto: "un número" },
  ];
}
