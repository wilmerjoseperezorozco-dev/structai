"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User, LogOut, Loader2, Crown } from "lucide-react";
import { supabase } from "@/lib/supabase";

interface Perfil {
  email: string;
  nombre: string | null;
  empresa: string | null;
  ciudad: string | null;
  plan: string;
  consultas_mes: number;
}

const PLAN_LABEL: Record<string, string> = {
  free: "Gratis",
  pro: "Pro",
  enterprise: "Enterprise",
};

export default function PerfilPage() {
  const router = useRouter();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [loading, setLoading] = useState(true);
  const [signingOut, setSigningOut] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const { data: session } = await supabase.auth.getSession();
      const user = session.session?.user;
      if (!user) return;

      const { data } = await supabase
        .from("profiles")
        .select("email, nombre, empresa, ciudad, plan, consultas_mes")
        .eq("id", user.id)
        .maybeSingle();

      if (cancelled) return;

      setPerfil(
        data ?? {
          email: user.email ?? "",
          nombre: null,
          empresa: null,
          ciudad: null,
          plan: "free",
          consultas_mes: 0,
        }
      );
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogout = async () => {
    setSigningOut(true);
    await supabase.auth.signOut();
    router.replace("/login");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 gap-2 text-brand-400">
        <Loader2 size={18} className="animate-spin" />
        <span className="text-sm">Cargando perfil…</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 px-4 py-6">
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center flex-shrink-0">
          <User size={26} className="text-white" />
        </div>
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-white truncate">{perfil?.nombre || perfil?.email}</h2>
          <p className="text-xs text-concrete-400 truncate">{perfil?.email}</p>
        </div>
      </div>

      <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-concrete-400">Plan</span>
          <span className="flex items-center gap-1.5 text-sm font-semibold text-white">
            {perfil?.plan !== "free" && <Crown size={14} className="text-brand-400" />}
            {PLAN_LABEL[perfil?.plan ?? "free"]}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-concrete-400">Consultas este mes</span>
          <span className="text-sm text-concrete-200 tabular-nums">{perfil?.consultas_mes ?? 0}</span>
        </div>
        {perfil?.empresa && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-concrete-400">Empresa</span>
            <span className="text-sm text-concrete-200">{perfil.empresa}</span>
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-xs text-concrete-400">Ciudad</span>
          <span className="text-sm text-concrete-200">{perfil?.ciudad ?? "Barranquilla"}</span>
        </div>
      </div>

      {perfil?.plan === "free" && (
        <a
          href="/pricing"
          className="block w-full text-center bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold py-3 rounded-xl transition"
        >
          Activa Pro por $19.900/mes
        </a>
      )}

      <button
        onClick={handleLogout}
        disabled={signingOut}
        className="flex items-center justify-center gap-2 w-full border border-concrete-700 hover:border-red-700 text-concrete-400 hover:text-red-400 text-sm font-medium py-3 rounded-xl transition disabled:opacity-60"
      >
        {signingOut ? <Loader2 size={15} className="animate-spin" /> : <LogOut size={15} />}
        Cerrar sesión
      </button>
    </div>
  );
}
