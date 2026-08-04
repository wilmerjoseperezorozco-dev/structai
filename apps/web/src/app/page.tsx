"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  MessageSquare,
  Scan,
  Calculator,
  HardHat,
  LayoutDashboard,
  Loader2,
} from "lucide-react";
import clsx from "clsx";
import dynamic from "next/dynamic";
import { supabase } from "@/lib/supabase";
import { Hero } from "@/components/Hero";

// Lazy-load panels (evita SSR de componentes client-only)
const Chat         = dynamic(() => import("@/components/Chat"),         { ssr: false });
const DetectUpload = dynamic(() => import("@/components/DetectUpload"), { ssr: false });
const APUPanel     = dynamic(() => import("@/components/APUPanel"),     { ssr: false });

// ── Tabs ─────────────────────────────────────────────────────────────────────

type Tab = "chat" | "detect" | "apu";

const TABS: { id: Tab; label: string; icon: React.ReactNode; short: string }[] = [
  { id: "chat",   label: "Consulta normativa", short: "Chat",    icon: <MessageSquare size={18} /> },
  { id: "detect", label: "Detección foto",     short: "Foto",    icon: <Scan size={18} /> },
  { id: "apu",    label: "Catálogo APU",       short: "APU",     icon: <Calculator size={18} /> },
];

// ── Página principal ──────────────────────────────────────────────────────────

const VALID_TABS: Tab[] = ["chat", "detect", "apu"];

export default function Home() {
  return (
    <Suspense fallback={<div className="h-full bg-concrete-900" />}>
      <HomeContent />
    </Suspense>
  );
}

function HomeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tabParam = searchParams.get("tab");
  const initialTab: Tab = VALID_TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "chat";

  const [tab, setTab] = useState<Tab>(initialTab);
  const [hasSession, setHasSession] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setHasSession(!!data.session);
      setCheckingSession(false);
    });
  }, []);

  // Mientras se resuelve la sesión (async) no se puede saber todavía si
  // corresponde mostrar el Hero o la app de tabs — mostrar cualquiera de
  // los dos a ciegas causaba un flash real: el Hero aparecía primero y
  // saltaba a la app en cuanto getSession() resolvía para un usuario ya
  // logueado. Mismo patrón que (app)/layout.tsx: un estado neutral
  // mientras se verifica, nunca contenido que después se descarta.
  if (checkingSession) {
    return (
      <div className="flex h-full items-center justify-center bg-concrete-900">
        <Loader2 size={22} className="animate-spin text-brand-400" />
      </div>
    );
  }

  // Landing (hero) para visitantes sin sesión que llegan a "/" sin un tab
  // explícito. Enlaces existentes como "/?tab=chat" (desde /dashboard) y
  // cualquier usuario ya autenticado siguen viendo la app de tabs de siempre
  // — el hero no reemplaza ese flujo, solo cubre la primera impresión.
  if (!hasSession && !tabParam) {
    return <Hero />;
  }

  return (
    <div className="flex flex-col h-full bg-concrete-900">
      {/* ── Header ── */}
      <header className="flex items-center gap-3 px-4 py-3 bg-concrete-900 border-b border-concrete-800">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
          <HardHat size={18} className="text-ink-950" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-white leading-none">StructAI</h1>
          <p className="text-[10px] text-concrete-500 leading-none mt-0.5">
            Ingeniero Civil IA · NTC/NSR-10 · APU 2026
          </p>
        </div>
        <button
          onClick={() => router.push(hasSession ? "/dashboard" : "/login")}
          className="flex items-center gap-1.5 text-xs text-concrete-400 hover:text-brand-300 border border-concrete-700 hover:border-brand-600 rounded-lg px-2.5 py-1.5 transition flex-shrink-0"
        >
          <LayoutDashboard size={13} />
          {hasSession ? "Mi cuenta" : "Ingresar"}
        </button>
      </header>

      {/* ── Panel activo ── */}
      <main className="flex-1 overflow-hidden">
        <div className={clsx("h-full", tab !== "chat"   && "hidden")}><Chat /></div>
        <div className={clsx("h-full", tab !== "detect" && "hidden")}><DetectUpload /></div>
        <div className={clsx("h-full", tab !== "apu"    && "hidden")}><APUPanel /></div>
      </main>

      {/* ── Bottom navigation ── */}
      <nav className="flex border-t border-concrete-800 bg-concrete-900 pb-safe">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={clsx(
              "flex-1 flex flex-col items-center justify-center gap-1 py-3 text-xs transition-colors",
              tab === t.id
                ? "text-brand-400"
                : "text-concrete-500 hover:text-concrete-300"
            )}
          >
            <span className={clsx(
              "p-1.5 rounded-xl transition-colors",
              tab === t.id ? "bg-brand-900/60" : ""
            )}>
              {t.icon}
            </span>
            <span className="font-medium">{t.short}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
