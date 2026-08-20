import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";

/**
 * Callback de PKCE para Supabase Auth — sin esto, la confirmación de
 * registro y el restablecimiento de contraseña quedaban rotos.
 *
 * Causa raíz real (encontrada 2026-08-20 revisando por qué usuarios
 * confirmaban su correo pero nunca lograban iniciar sesión): @supabase/ssr
 * usa flowType="pkce" fijo por defecto (confirmado en el propio código
 * fuente instalado, node_modules/@supabase/ssr/dist/main/createBrowserClient.js).
 * Con PKCE, el enlace del correo llega como "?code=XXXX" (query param), no
 * como "#access_token=..." (hash) — y a diferencia del flujo implícito, el
 * cliente de Supabase NO intercambia ese code automáticamente solo por
 * estar en la URL. Sin este endpoint, "/dashboard?code=XXXX" y
 * "/restablecer?code=XXXX" nunca establecían sesión: el guard de (app)
 * simplemente rebotaba a /login sin explicación, y restablecer.tsx
 * mostraba "enlace inválido o expiró" incluso con un enlace recién
 * generado y válido.
 *
 * emailRedirectTo (signUp) y redirectTo (resetPasswordForEmail) deben
 * apuntar aquí con `?next=<destino real>`, no directo a /dashboard o
 * /restablecer.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/dashboard";

  if (!code) {
    return NextResponse.redirect(`${origin}/login?error=enlace_invalido`);
  }

  const response = NextResponse.redirect(`${origin}${next}`);

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  const { error } = await supabase.auth.exchangeCodeForSession(code);
  if (error) {
    return NextResponse.redirect(`${origin}/login?error=enlace_expirado`);
  }

  return response;
}
