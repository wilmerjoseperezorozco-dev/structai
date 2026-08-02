// Next.js instrumentation hook (soportado nativamente desde Next 15, sin
// flag experimental) — patrón recomendado por @sentry/nextjs v8+ en vez de
// sentry.server.config.ts / sentry.edge.config.ts sueltos. register() corre
// una vez al arrancar el proceso, tanto en runtime nodejs (SSR normal) como
// edge (middleware) — por eso el import de Sentry.init se hace condicional
// según NEXT_RUNTIME, cada runtime tiene su propio conjunto de APIs.
export async function register() {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
  if (!dsn) return;

  if (process.env.NEXT_RUNTIME === "nodejs") {
    const Sentry = await import("@sentry/nextjs");
    Sentry.init({
      dsn,
      environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || "production",
      tracesSampleRate: 0.1,
    });
  }

  if (process.env.NEXT_RUNTIME === "edge") {
    const Sentry = await import("@sentry/nextjs");
    Sentry.init({
      dsn,
      environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || "production",
      tracesSampleRate: 0.1,
    });
  }
}

// Captura errores de Server Components / Route Handlers / Server Actions
// que Next.js intercepta internamente (no llegan a global-error.tsx porque
// ese solo cubre errores de render en el cliente).
export const onRequestError = async (...args: Parameters<typeof import("@sentry/nextjs").captureRequestError>) => {
  if (!process.env.NEXT_PUBLIC_SENTRY_DSN) return;
  const Sentry = await import("@sentry/nextjs");
  Sentry.captureRequestError(...args);
};
