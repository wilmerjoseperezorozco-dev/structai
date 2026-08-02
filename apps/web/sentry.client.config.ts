// Sentry — captura de errores en el navegador (cliente).
// Solo se activa si NEXT_PUBLIC_SENTRY_DSN está seteado, igual patrón que
// SENTRY_DSN en apps/api/main.py — no rompe dev local sin cuenta configurada.
import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || "production",
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0.1,
    integrations: [Sentry.replayIntegration()],
  });
}
