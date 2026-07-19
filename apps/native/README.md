# StructAI Native (Fase 0)

Shell nativo Expo + auth contra Supabase. Sin lógica de sensores todavía (Fase 2+).

**Android e iOS en dispositivo físico, sin Mac ni build nativo propio**: esta fase solo usa
módulos que ya vienen precompilados dentro de la app **Expo Go** (Play Store / App Store).
Instala Expo Go en tu teléfono y escanea el QR — mismo bundle JS en ambas plataformas. Un
development build (EAS Build, tampoco requiere Mac) solo hace falta cuando entren módulos
nativos fuera del set de Expo Go (Fase 2+, sensores).

## Setup

1. `cp .env.example .env.local` y completa con los mismos valores de
   `apps/web/.env.local` (`EXPO_PUBLIC_SUPABASE_URL`, `EXPO_PUBLIC_SUPABASE_ANON_KEY`).
2. Arranca `apps/api` local: `cd ../api && uvicorn main:app --reload --host 0.0.0.0`
3. En `.env.local`, pon `EXPO_PUBLIC_API_URL` según cómo vas a probar:
   - Dispositivo físico (Expo Go): IP LAN de esta máquina, ej. `http://192.168.1.X:8000`
   - Emulador Android: `http://10.0.2.2:8000`
   - Simulador iOS: `http://localhost:8000`
4. Desde la raíz del monorepo: `npm install` (workspaces — instala apps/web, apps/native y
   packages/shared-types juntos).
5. `npm start` (abre Expo Dev Tools) y escanea el QR con Expo Go, o presiona `a`/`i` para emulador.

## Qué prueba esta fase

Login real contra Supabase (mismo proyecto `zuiwdtwkahkrrnnatniy` que `apps/web`) + llamada real a `/health` de `apps/api` corriendo local. No hay mock de backend — si `apps/api` no está corriendo o `EXPO_PUBLIC_API_URL` está mal, la pantalla de home lo muestra explícitamente.
