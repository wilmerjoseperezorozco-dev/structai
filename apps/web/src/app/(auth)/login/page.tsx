"use client";

import { useState } from "react";
import { HardHat, Loader2, MailCheck } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmacionPendiente, setConfirmacionPendiente] = useState(false);
  const [mode, setMode] = useState<"login" | "registro">("login");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setConfirmacionPendiente(false);

    try {
      if (mode === "login") {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        router.push("/dashboard");
      } else {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        if (!data.session) {
          // Confirmación por correo requerida — sin sesión activa todavía,
          // redirigir a /dashboard solo rebotaría de vuelta al guard de (app).
          setConfirmacionPendiente(true);
        } else {
          router.push("/dashboard");
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error de autenticación");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-concrete-900 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-4">
            <HardHat size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">StructAI</h1>
          <p className="text-concrete-400 text-sm mt-1">
            NSR-10 · NTC · APU 2026 · Barranquilla
          </p>
        </div>

        {/* Form */}
        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6">
          <div className="flex mb-6 bg-concrete-900 rounded-xl p-1">
            {(["login", "registro"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition ${
                  mode === m
                    ? "bg-brand-600 text-white"
                    : "text-concrete-400 hover:text-concrete-200"
                }`}
              >
                {m === "login" ? "Ingresar" : "Registrarse"}
              </button>
            ))}
          </div>

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
            <div>
              <label className="text-xs text-concrete-400 font-medium block mb-1.5">
                Contraseña
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-concrete-900 border border-concrete-700 rounded-xl px-3 py-3 text-sm text-white placeholder:text-concrete-600 outline-none focus:border-brand-500 transition"
              />
            </div>

            {error && (
              <p className="text-xs text-red-400 bg-red-900/30 border border-red-700/50 rounded-xl px-3 py-2">
                {error}
              </p>
            )}

            {confirmacionPendiente && (
              <div className="flex items-start gap-2 text-xs text-brand-300 bg-brand-900/30 border border-brand-700/50 rounded-xl px-3 py-2.5">
                <MailCheck size={15} className="flex-shrink-0 mt-0.5" />
                <span>
                  Cuenta creada. Revisa <b>{email}</b> y confirma tu correo antes de ingresar.
                </span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl text-sm transition flex items-center justify-center gap-2"
            >
              {loading && <Loader2 size={15} className="animate-spin" />}
              {mode === "login" ? "Ingresar" : "Crear cuenta gratis"}
            </button>

            {mode === "login" && (
              <Link
                href="/recuperar"
                className="block text-center text-xs text-concrete-400 hover:text-brand-400 transition"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            )}
          </form>
        </div>

        <p className="text-center text-xs text-concrete-600 mt-4">
          Al registrarte aceptas los{" "}
          <Link href="/terminos" className="text-brand-400 hover:underline">
            términos de uso
          </Link>{" "}
          y la{" "}
          <Link href="/privacidad" className="text-brand-400 hover:underline">
            política de privacidad
          </Link>{" "}
          · Construdata 2026
        </p>
      </div>
    </div>
  );
}
