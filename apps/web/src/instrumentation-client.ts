// Sentry — captura de errores en el navegador (cliente).
// Solo se activa si NEXT_PUBLIC_SENTRY_DSN está seteado, igual patrón que
// SENTRY_DSN en apps/api/main.py — no rompe dev local sin cuenta configurada.
//
// Movido desde sentry.client.config.ts (raíz de apps/web) al subir a
// @sentry/nextjs v10: el SDK deprecó ese archivo a favor de
// instrumentation-client.ts (convención de Next.js) porque el archivo viejo
// deja de funcionar con Turbopack -- confirmado con el warning real de build
// del 2026-08-26 antes de este cambio. Mismo contenido, solo cambia dónde
// vive.
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
      //
      // Bug real encontrado 2026-08-15 revisando Sentry: este filtro NUNCA
      // coincidió desde que se instaló — comparaba contra "ServiceWorker"
      // (mayúscula) con .includes(), sensible a mayúsculas, pero el frame
      // real del stack en runtime es "navigator.serviceWorker.register"
      // (minúscula). El issue PYTHON-FASTAPI-2 siguió acumulando eventos
      // reales 10+ días después del "fix" (último visto 2026-08-14) sin que
      // el filtro los tocara. Se compara en minúsculas para no depender de
      // la capitalización exacta que use el minificador de turno.
      const frames = event.exception?.values?.[0]?.stacktrace?.frames ?? [];
      const esRegistroServiceWorker = frames.some((f) =>
        f.function?.toLowerCase().includes("serviceworker")
      );
      if (esRegistroServiceWorker && event.exception?.values?.[0]?.value === "Rejected") {
        return null;
      }
      return event;
    },
  });
}

// Requerido por @sentry/nextjs v10 para instrumentar navegaciones del App
// Router (spans de "pageload"/"navigation" en el trace) -- sin este export,
// el build imprime "ACTION REQUIRED" (confirmado real al subir de v8 a
// v10.71.0 el 2026-08-26). No-op si Sentry nunca se inicializó (sin DSN).
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
