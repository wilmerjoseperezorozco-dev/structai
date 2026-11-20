// Hosts que NO existen: el navegador nunca llega a ellos (e2e/soporte.ts
// intercepta todo). Compartidos por playwright.config.ts y las pruebas.
export const PUERTO = 3100;
export const API_FALSA = "http://api.e2e.localhost:8999";
export const SUPABASE_FALSO = "http://e2e.localhost:54321";
