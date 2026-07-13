"use client";

import { useEffect, useState } from "react";
import { HardHat, Loader2, CheckCircle2 } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RestablecerPage() {
  const router = useRouter();
  const [sesionLista, setSesionLista] = useState(false);
  const [enlaceInvalido, setEnlaceInvalido] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listo, setListo] = useState(false);

  useEffect(() => {
    // El enlace del correo deja al usuario en una sesión de recuperación
    // temporal — este evento confirma que el token del enlace era válido
    // antes de mostrar el formulario de nueva contraseña.
    const { data: subscription } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setSesionLista(true);
      }
    });

    supabase.auth.getSession().then(({ data }) => {
      if (data.session) setSesionLista(true);
    });

    return () => subscription.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (sesionLista) return;
    // Si a los 4s no llegó PASSWORD_RECOVERY ni había sesión, el enlace del
    // correo era inválido/expirado (o el usuario entró directo a esta URL).
    const timeout = setTimeout(() => setEnlaceInvalido(true), 4000);
    return () => clearTimeout(timeout);
  }, [sesionLista]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmar) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setLoading(true);
    const { error } = await supabase.auth.updateUser({ password });
    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }
    setListo(true);
    setTimeout(() => router.push("/dashboard"), 1500);
  };

  return (
    <div className="min-h-screen bg-concrete-900 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-4">
            <HardHat size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Nueva contraseña</h1>
          <p className="text-concrete-400 text-sm mt-1">
            Crea una contraseña nueva para tu cuenta
          </p>
        </div>

        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6">
          {listo ? (
            <div className="flex items-start gap-2 text-xs text-brand-300 bg-brand-900/30 border border-brand-700/50 rounded-xl px-3 py-2.5">
              <CheckCircle2 size={15} className="flex-shrink-0 mt-0.5" />
              <span>Contraseña actualizada. Entrando...</span>
            </div>
          ) : enlaceInvalido && !sesionLista ? (
            <div className="text-xs text-red-400 bg-red-900/30 border border-red-700/50 rounded-xl px-3 py-2.5">
              Este enlace ya no es válido o expiró. Solicita uno nuevo.
              <Link href="/recuperar" className="block mt-2 text-brand-400 hover:underline font-medium">
                Pedir enlace nuevo
              </Link>
            </div>
          ) : !sesionLista ? (
            <div className="flex items-center justify-center py-6">
              <Loader2 size={20} className="animate-spin text-brand-400" />
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-xs text-concrete-400 font-medium block mb-1.5">
                  Contraseña nueva
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
              <div>
                <label className="text-xs text-concrete-400 font-medium block mb-1.5">
                  Confirmar contraseña
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirmar}
                  onChange={(e) => setConfirmar(e.target.value)}
                  placeholder="••••••••"
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
                className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl text-sm transition flex items-center justify-center gap-2"
              >
                {loading && <Loader2 size={15} className="animate-spin" />}
                Guardar contraseña
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
