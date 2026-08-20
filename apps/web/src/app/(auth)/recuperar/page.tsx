"use client";

import { useState } from "react";
import { HardHat, Loader2, MailCheck, ArrowLeft } from "lucide-react";
import { supabase } from "@/lib/supabase";
import Link from "next/link";

export default function RecuperarPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Debe apuntar a /auth/callback, NO directo a /restablecer — mismo
    // motivo que en login/page.tsx (signUp): flowType=pkce necesita
    // exchangeCodeForSession() antes de que exista sesión. Ver
    // app/auth/callback/route.ts.
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=/restablecer`,
    });

    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }
    setEnviado(true);
  };

  return (
    <div className="min-h-screen bg-concrete-900 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-4">
            <HardHat size={28} className="text-ink-950" />
          </div>
          <h1 className="text-2xl font-bold text-white">Recuperar contraseña</h1>
          <p className="text-concrete-400 text-sm mt-1">
            Te enviamos un enlace para crear una nueva
          </p>
        </div>

        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6">
          {enviado ? (
            <div className="flex items-start gap-2 text-xs text-brand-300 bg-brand-900/30 border border-brand-700/50 rounded-xl px-3 py-2.5">
              <MailCheck size={15} className="flex-shrink-0 mt-0.5" />
              <span>
                Revisa <b>{email}</b> y sigue el enlace para crear una contraseña nueva.
                Si no lo ves en unos minutos, revisa la carpeta de spam.
              </span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-xs text-concrete-400 font-medium block mb-1.5">
                  Correo electrónico
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ingeniero@email.com"
                  className="w-full bg-concrete-900 border border-concrete-700 rounded-xl px-3 py-3 text-sm text-white placeholder:text-concrete-600 outline-none focus:border-brand-500 transition"
                />
              </div>

              {error && (
                <p className="text-xs text-red-400 bg-red-900/30 border border-red-700/50 rounded-xl px-3 py-2">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-ink-950 font-semibold py-3 rounded-xl text-sm transition flex items-center justify-center gap-2"
              >
                {loading && <Loader2 size={15} className="animate-spin" />}
                Enviar enlace de recuperación
              </button>
            </form>
          )}
        </div>

        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-xs text-concrete-400 hover:text-concrete-200 transition mt-4"
        >
          <ArrowLeft size={14} />
          Volver a ingresar
        </Link>
      </div>
    </div>
  );
}
