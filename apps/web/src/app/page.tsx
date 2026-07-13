"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  MessageSquare,
  Scan,
  Calculator,
  Wifi,
  WifiOff,
  HardHat,
  LayoutDashboard,
} from "lucide-react";
import clsx from "clsx";
import dynamic from "next/dynamic";
import { healthCheck, type HealthResponse } from "@/lib/api";
import { supabase } from "@/lib/supabase";

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

// ── Status bar superior ───────────────────────────────────────────────────────

function StatusBar({ health }: { health: HealthResponse | null }) {
  if (!health) return null;
  const allOk = health.modulos.rag_multi_norma && health.modulos.motor_apu;
  return (
    <div className={clsx(
      "flex items-center gap-2 px-4 py-1.5 text-xs border-b",
      allOk
        ? "bg-green-950/40 border-green-900/40 text-green-400"
        : "bg-yellow-950/40 border-yellow-900/40 text-yellow-400"
    )}>
      {allOk ? <Wifi size={11} /> : <WifiOff size={11} />}
      <span>
        RAG {health.modulos.rag_multi_norma ? "✓" : "✗"} ·
        APU {health.modulos.motor_apu ? "✓" : "✗"} ·
        YOLO {health.modulos.yolo_onnx ? "ONNX" : "stub"} ·
        {health.apu_count} actividades
      </span>
      <span className="ml-auto text-green-600">v{health.version}</span>
    </div>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────

const VALID_TABS: Tab[] = ["chat", "detect", "apu"];

export default function Home() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tabParam = searchParams.get("tab");
  const initialTab: Tab = VALID_TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "chat";

  const [tab, setTab] = useState<Tab>(initialTab);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [hasSession, setHasSession] = useState(false);

  useEffect(() => {
    healthCheck()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setHasSession(!!data.session));
  }, []);

  return (
    <div className="flex flex-col h-full bg-concrete-900">
      {/* ── Header ── */}
      <header className="flex items-center gap-3 px-4 py-3 bg-concrete-900 border-b border-concrete-800">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
          <HardHat size={18} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-white leading-none">Construdata</h1>
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

      {/* ── Status backend ── */}
      <StatusBar health={health} />

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
