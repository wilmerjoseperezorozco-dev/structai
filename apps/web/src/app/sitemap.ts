import type { MetadataRoute } from "next";

// Genera /sitemap.xml en runtime. No existía ninguno antes (verificado:
// 404 en vivo). Solo las rutas públicas reales fuera del grupo (app)
// autenticado -- landing, precios, legales, y /diagnostico (herramienta
// gratuita sin login, pensada para compartirse directo -- ver robots.ts).
export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://www.structai.online";
  const ahora = new Date();
  return [
    { url: `${base}/`, lastModified: ahora, changeFrequency: "weekly", priority: 1 },
    { url: `${base}/diagnostico`, lastModified: ahora, changeFrequency: "monthly", priority: 0.9 },
    { url: `${base}/pricing`, lastModified: ahora, changeFrequency: "monthly", priority: 0.7 },
    { url: `${base}/terminos`, lastModified: ahora, changeFrequency: "yearly", priority: 0.2 },
    { url: `${base}/privacidad`, lastModified: ahora, changeFrequency: "yearly", priority: 0.2 },
  ];
}
