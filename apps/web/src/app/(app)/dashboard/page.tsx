"use client";

import { Calculator, BookOpen, FolderOpen, TrendingUp, ChevronRight, MessageSquare, Scan } from "lucide-react";
import Link from "next/link";

const ACCESOS_RAPIDOS = [
  {
    href: "/?tab=chat",
    icon: <MessageSquare size={22} className="text-cyan-400" />,
    titulo: "Consulta normativa",
    sub: "Chat RAG · NTC/NSR-10",
    bg: "bg-cyan-900/30 border-cyan-700/40",
  },
  {
    href: "/apu",
    icon: <Calculator size={22} className="text-brand-400" />,
    titulo: "Calcular APU",
    sub: "Construdata 2026 · Monte Carlo",
    bg: "bg-brand-900/30 border-brand-700/40",
  },
  {
    href: "/?tab=detect",
    icon: <Scan size={22} className="text-purple-400" />,
    titulo: "Detección foto",
    sub: "Elementos estructurales · YOLO",
    bg: "bg-purple-900/30 border-purple-700/40",
  },
  {
    href: "/nsr10",
    icon: <BookOpen size={22} className="text-orange-400" />,
    titulo: "NSR-10",
    sub: "11 títulos · Consulta rápida",
    bg: "bg-orange-900/30 border-orange-700/40",
  },
  {
    href: "/proyectos",
    icon: <FolderOpen size={22} className="text-green-400" />,
    titulo: "Mis proyectos",
    sub: "APUs guardados y trazabilidad",
    bg: "bg-green-900/30 border-green-700/40",
  },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6 px-4 py-6">

      {/* Saludo */}
      <div>
        <p className="text-xs text-concrete-500 uppercase tracking-widest mb-1">Buenos días</p>
        <h2 className="text-xl font-bold text-white">Ingeniero</h2>
        <p className="text-xs text-concrete-400 mt-0.5">Plan Gratis · 5 APU disponibles este mes</p>
      </div>

      {/* Accesos rápidos */}
      <div className="space-y-3">
        <p className="text-xs font-semibold text-concrete-400 uppercase tracking-widest">Accesos rápidos</p>
        {ACCESOS_RAPIDOS.map((a) => (
          <Link
            key={a.href}
            href={a.href}
            className={`flex items-center gap-4 border rounded-2xl px-4 py-4 transition hover:opacity-90 ${a.bg}`}
          >
            <div className="flex-shrink-0">{a.icon}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white">{a.titulo}</p>
              <p className="text-xs text-concrete-400 mt-0.5">{a.sub}</p>
            </div>
            <ChevronRight size={16} className="text-concrete-600 flex-shrink-0" />
          </Link>
        ))}
      </div>

      {/* Upgrade CTA */}
      <div className="bg-brand-950 border border-brand-700/50 rounded-2xl p-4">
        <div className="flex items-start gap-3">
          <TrendingUp size={20} className="text-brand-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-white">Activa Pro por $19.900/mes</p>
            <p className="text-xs text-concrete-400 mt-0.5">
              APU ilimitados · PDF trazable · Historial completo
            </p>
          </div>
        </div>
        <Link
          href="/pricing"
          className="block mt-3 w-full text-center bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold py-2.5 rounded-xl transition"
        >
          Ver planes
        </Link>
      </div>
    </div>
  );
}
