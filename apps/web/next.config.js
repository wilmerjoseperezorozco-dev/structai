/** @type {import('next').NextConfig} */

// next-pwa (original) no se actualiza desde agosto de 2022 y arrastraba
// vulnerabilidades reales en su cadena workbox-build/rollup-plugin-terser/
// serialize-javascript (RCE, CVSS 8.1 — build-time, no explotable en runtime,
// pero igual deuda real). Migrado a @ducanh2912/next-pwa, el fork
// activamente mantenido de la comunidad (auditoría de seguridad 2026-08-01).
//
// Estrategias de caché del Service Worker (Workbox, vía next-pwa).
// runtimeCachingDefecto trae las reglas por defecto del paquete (fuentes,
// imágenes, JS/CSS) — se conservan y se antepone la regla propia para el
// backend FastAPI.
const withPWAInit = require("@ducanh2912/next-pwa").default;
const { runtimeCaching: runtimeCachingDefecto } = require("@ducanh2912/next-pwa");

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

const withPWA = withPWAInit({
  dest: "public",
  register: true,
  disable: process.env.NODE_ENV === "development",
  workboxOptions: {
    runtimeCaching,
  },
});

const nextConfig = {
  reactStrictMode: true,
  // shared-types (packages/shared-types) se consume como dependencia local
  // vía "file:" — no publica JS compilado, así que Next debe transpilar su
  // TypeScript fuente igual que el resto de la app.
  transpilePackages: ["shared-types"],
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

module.exports = withPWA(nextConfig);
