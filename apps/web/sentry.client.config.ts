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
    ignoreErrors: [
      // TypeError del propio @ducanh2912/next-pwa leyendo registration.waiting
      // cuando el registro del Service Worker falló o aún no resolvió.
      // Confirmado real 2026-08-04 (PYTHON-FASTAPI-3): no rompe la app, solo
      // pierde caché offline en esa visita.
      /Cannot read properties of undefined \(reading 'waiting'\)/,
    ],
    beforeSend(event) {
      // "Error: Rejected" del propio registro del Service Worker
      // (ServiceWorkerContainer.register, vía @ducanh2912/next-pwa) — ocurre
      // en navegadores con soporte restringido de Service Workers; el caso
      // confirmado real 2026-08-04 (PYTHON-FASTAPI-2) vino del navegador
      // interno de Facebook/Instagram (?fbclid= en la URL). No rompe la app,
      // se descarta aquí para no generar ruido con cada visitante que entre
      // desde un enlace social.
      const frames = event.exception?.values?.[0]?.stacktrace?.frames ?? [];
      const esRegistroServiceWorker = frames.some((f) => f.function?.includes("ServiceWorker"));
      if (esRegistroServiceWorker && event.exception?.values?.[0]?.value === "Rejected") {
        return null;
      }
      return event;
    },
  });
}
