import type { MetadataRoute } from "next";

// Genera /robots.txt en runtime (Next.js App Router, archivo especial).
// Antes de esto no existía ningún robots.txt real (verificado: 404 en vivo
// contra structai.online) -- sin esto, algunos rastreadores asumen "no
// permitido" por defecto en vez de "permitido", y Google Search Console no
// tiene de dónde leer la referencia al sitemap.
//
// /diagnostico se deja indexable A PROPÓSITO: es la herramienta gratuita de
// diagnóstico de vulnerabilidad sísmica, pública sin login por diseño (ver
// apps/web/src/app/diagnostico/page.tsx) -- justo el tipo de página que más
// interesa que aparezca en Google tras el terremoto de agosto 2026, no algo
// para esconder de los rastreadores.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/auth/"],
    },
    sitemap: "https://www.structai.online/sitemap.xml",
  };
}
