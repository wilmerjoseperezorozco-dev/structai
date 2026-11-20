import { test as base, expect, type Page, type Request } from "@playwright/test";
import { API_FALSA, PUERTO, SUPABASE_FALSO } from "./constantes";

/**
 * Soporte de las pruebas E2E del chat (#190).
 *
 * 1. Red cerrada: toda petición del navegador que no vaya al servidor local
 *    de Next se aborta, salvo las del backend falso, que se responden con
 *    fixtures. Así ninguna prueba puede tocar producción ni gastar cuota de
 *    LLM aunque alguien cambie una URL por error.
 * 2. Sesión falsa: cookie de @supabase/ssr con una sesión inventada. El
 *    cliente de Supabase la lee de la cookie sin hacer ninguna petición
 *    (getSession() no valida contra el servidor si no está vencida).
 */

const REF = new URL(SUPABASE_FALSO).hostname.split(".")[0];
const COOKIE_SESION = `sb-${REF}-auth-token`;

function base64url(s: string): string {
  return Buffer.from(s, "utf-8").toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function sesionFalsa() {
  const exp = Math.floor(Date.now() / 1000) + 24 * 3600;
  const jwt = [
    base64url(JSON.stringify({ alg: "HS256", typ: "JWT" })),
    base64url(JSON.stringify({ sub: "00000000-0000-4000-8000-0000000000e2", role: "authenticated", exp })),
    "firma-falsa",
  ].join(".");
  return {
    access_token: jwt,
    refresh_token: "refresh-falso",
    token_type: "bearer",
    expires_in: 24 * 3600,
    expires_at: exp,
    user: {
      id: "00000000-0000-4000-8000-0000000000e2",
      aud: "authenticated",
      role: "authenticated",
      email: "ingeniero@e2e.test",
      app_metadata: {},
      user_metadata: {},
      created_at: "2026-01-01T00:00:00Z",
    },
  };
}

export async function iniciarSesionFalsa(page: Page) {
  await page.context().addCookies([
    {
      name: COOKIE_SESION,
      value: "base64-" + base64url(JSON.stringify(sesionFalsa())),
      domain: "localhost",
      path: "/",
      sameSite: "Lax",
    },
  ]);
}

export type Manejador = (req: Request) => { status?: number; json: unknown } | Promise<{ status?: number; json: unknown }>;

interface Backend {
  /** Responde POST /consultar con lo que devuelva `fn`. */
  consultar(fn: Manejador): void;
  /** Peticiones que llegaron al backend falso, en orden. */
  peticiones: { metodo: string; ruta: string; cuerpo: unknown }[];
  /** Hosts externos bloqueados (cualquier cosa que no sea el backend falso ni localhost:PUERTO). */
  bloqueadas: string[];
}

export const test = base.extend<{ backend: Backend }>({
  backend: async ({ page }, use) => {
    const rutas = new Map<string, Manejador>();
    const backend: Backend = {
      consultar: (fn) => rutas.set("POST /consultar", fn),
      peticiones: [],
      bloqueadas: [],
    };
    rutas.set("POST /consultas/*/feedback", () => ({ status: 200, json: { ok: true } }));
    // El panel APU (oculto en la pestaña de chat) se monta igual y pide el catálogo.
    rutas.set("GET /apu/list", () => ({ json: [] }));

    await page.context().route("**/*", async (route) => {
      const req = route.request();
      const url = new URL(req.url());
      if (url.host === `localhost:${PUERTO}`) return route.continue();
      if (url.origin === API_FALSA) {
        let cuerpo: unknown = null;
        try {
          cuerpo = req.postDataJSON();
        } catch {
          cuerpo = req.postData();
        }
        backend.peticiones.push({ metodo: req.method(), ruta: url.pathname, cuerpo });
        const clave = `${req.method()} ${url.pathname.replace(/^\/consultas\/[^/]+\/feedback$/, "/consultas/*/feedback")}`;
        const fn = rutas.get(clave);
        if (!fn) return route.fulfill({ status: 404, json: { detail: `Sin fixture para ${clave}` } });
        const r = await fn(req);
        return route.fulfill({ status: r.status ?? 200, json: r.json });
      }
      backend.bloqueadas.push(url.origin);
      return route.abort("blockedbyclient");
    });
    await use(backend);
  },
});

export { expect };

/** Abre el chat (pestaña explícita para no caer en el Hero) y espera el input. */
export async function abrirChat(page: Page) {
  await page.goto("/?tab=chat");
  await expect(page.getByRole("textbox")).toBeVisible();
}

export async function preguntar(page: Page, texto: string) {
  const caja = page.getByRole("textbox");
  await caja.fill(texto);
  await caja.press("Enter");
}
