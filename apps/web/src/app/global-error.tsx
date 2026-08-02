"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

// Next.js App Router: global-error.tsx captura errores no manejados en el
// árbol de renderizado raíz (reemplaza layout.tsx + page.tsx cuando se
// dispara). Sentry.captureException aquí es lo único que reporta errores
// de render de React a Sentry — sin esto, sentry.client.config.ts solo ve
// errores no capturados por React (fetch, event handlers), no crashes de
// render.
export default function GlobalError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html lang="es">
      <body>
        <div style={{ padding: "2rem", textAlign: "center", fontFamily: "sans-serif" }}>
          <h1>Algo salió mal</h1>
          <p>El error ya fue reportado. Intenta recargar la página.</p>
        </div>
      </body>
    </html>
  );
}
