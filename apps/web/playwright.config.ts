import { defineConfig, devices } from "@playwright/test";
import { API_FALSA, PUERTO, SUPABASE_FALSO } from "./e2e/constantes";

/**
 * Pruebas E2E del chat (issue #190). API simulada: ninguna prueba toca
 * producción, Supabase ni un LLM. Los hosts de abajo NO existen; cualquier
 * petición que salga del navegador se intercepta en e2e/soporte.ts (la del
 * backend se responde con fixtures, el resto se aborta).
 *
 * Ejecutar: npm run test:e2e   (levanta `next dev` en el puerto 3100)
 */

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  timeout: 60_000,
  use: {
    baseURL: `http://localhost:${PUERTO}`,
    trace: "retain-on-failure",
    locale: "es-CO",
  },
  projects: [
    { name: "escritorio", use: { ...devices["Desktop Chrome"] } },
    { name: "celular", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: `npx next dev -p ${PUERTO}`,
    url: `http://localhost:${PUERTO}`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    env: {
      NEXT_PUBLIC_API_URL: API_FALSA,
      NEXT_PUBLIC_SUPABASE_URL: SUPABASE_FALSO,
      NEXT_PUBLIC_SUPABASE_ANON_KEY: "e2e-clave-anonima-falsa",
      NEXT_PUBLIC_SENTRY_DSN: "",
      NEXT_TELEMETRY_DISABLED: "1",
    },
  },
});
