"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { LayoutDashboard, Calculator, BookOpen, FolderOpen, User, Loader2, Droplets, Mountain, Route, LineChart } from "lucide-react";
import clsx from "clsx";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

// Lanzamiento piloto (2026-08): navegación enfocada en NSR-10/NTC/SGSST +
// APU para no dispersar el feedback de los primeros 100 usuarios de
// prueba. AquAI/GeoPot/Vías/Gerencia siguen 100% funcionales (código,
// rutas y datos intactos, verificados end-to-end) — solo se ocultan de
// esta barra. Reactivar: cambiar SOLO_ENFOQUE_PILOTO a false.
const SOLO_ENFOQUE_PILOTO = true;
const RUTAS_OCULTAS_EN_PILOTO = new Set(["/aquai", "/geopot", "/vias", "/gerencia"]);

const NAV_ITEMS_COMPLETO = [
  { href: "/dashboard", label: "Inicio", icon: LayoutDashboard },
  { href: "/apu", label: "APU", icon: Calculator },
  { href: "/aquai", label: "AquAI", icon: Droplets },
  { href: "/geopot", label: "GeoPot", icon: Mountain },
  { href: "/vias", label: "Vías", icon: Route },
  { href: "/gerencia", label: "Gerencia", icon: LineChart },
  { href: "/nsr10", label: "NSR-10", icon: BookOpen },
  { href: "/proyectos", label: "Proyectos", icon: FolderOpen },
  { href: "/perfil", label: "Perfil", icon: User },
];

const NAV_ITEMS = SOLO_ENFOQUE_PILOTO
  ? NAV_ITEMS_COMPLETO.filter((item) => !RUTAS_OCULTAS_EN_PILOTO.has(item.href))
  : NAV_ITEMS_COMPLETO;

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<Session | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) {
        router.replace("/login");
        return;
      }
      setSession(data.session);
      setChecking(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      if (!newSession) {
        router.replace("/login");
        return;
      }
      setSession(newSession);
    });

    return () => subscription.subscription.unsubscribe();
  }, [router]);

  if (checking || !session) {
    return (
      <div className="flex h-full min-h-screen items-center justify-center bg-concrete-900">
        <Loader2 size={22} className="animate-spin text-brand-400" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full min-h-screen bg-concrete-900">
      <main className="flex-1 overflow-y-auto pb-20">{children}</main>

      <nav className="fixed bottom-0 inset-x-0 flex border-t border-concrete-800 bg-concrete-900 pb-safe">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname?.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex-1 flex flex-col items-center justify-center gap-1 py-3 text-xs transition-colors",
                active ? "text-brand-400" : "text-concrete-500 hover:text-concrete-300"
              )}
            >
              <span className={clsx("p-1.5 rounded-xl transition-colors", active && "bg-brand-900/60")}>
                <Icon size={18} />
              </span>
              <span className="font-medium">{label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
