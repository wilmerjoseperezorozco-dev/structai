/** @type {import('next').NextConfig} */

// Estrategias de caché del Service Worker (Workbox, vía next-pwa).
// runtimeCachingDefecto trae las reglas por defecto de next-pwa (fuentes,
// imágenes, JS/CSS) — se conservan y se antepone la regla propia para el
// backend FastAPI.
const runtimeCachingDefecto = require("next-pwa/cache");

const runtimeCaching = [
  {
    // GET al backend (health check, catálogo APU, etc.): Network First
    // cayendo a caché — intenta red primero (datos frescos), y si no hay
    // señal (sótano, zona rural) sirve la última respuesta guardada.
    // Los endpoints POST (/ask, /consultar) NO se cachean aquí a propósito:
    // el Cache API del navegador solo intercepta peticiones GET: esas
    // respuestas se persisten aparte, a nivel de app, en localStorage
    // (ver apps/web/src/components/Chat.tsx).
    urlPattern: ({ url, request }) =>
      request.method === "GET" && url.pathname.match(/^\/(health|apu\/list)/),
    handler: "NetworkFirst",
    options: {
      cacheName: "construdata-api-cache",
      networkTimeoutSeconds: 5, // si no responde en 5s, sirve la caché
      expiration: {
        maxEntries: 32,
        maxAgeSeconds: 24 * 60 * 60, // 1 día
      },
      cacheableResponse: { statuses: [0, 200] },
    },
  },
  ...runtimeCachingDefecto,
];

const withPWA = require("next-pwa")({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development",
  runtimeCaching,
});

const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

module.exports = withPWA(nextConfig);
