"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { HardHat } from "lucide-react";

const DiagnosticoVulnerabilidad = dynamic(() => import("@/components/DiagnosticoVulnerabilidad"), { ssr: false });

// Ruta pública, fuera del grupo (app) a propósito: no exige login. Un
// diagnóstico de vulnerabilidad sísmica debe poder compartirse como link
// directo y usarse por cualquiera, no solo usuarios registrados — ver
// project_structai_terremoto_2026_pivote.md.
export default function DiagnosticoPage() {
  return (
    <div className="flex flex-col h-full min-h-screen bg-concrete-900">
      <header className="flex items-center gap-3 px-4 py-3 bg-concrete-900 border-b border-concrete-800">
        <Link href="/" className="flex items-center gap-3 flex-1 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <HardHat size={18} className="text-ink-950" />
          </div>
          <div className="min-w-0">
            <h1 className="text-sm font-bold text-white leading-none">StructAI</h1>
            <p className="text-[10px] text-concrete-500 leading-none mt-0.5">Diagnóstico gratuito · Colombia</p>
          </div>
        </Link>
      </header>
      <main className="flex-1 overflow-hidden">
        <DiagnosticoVulnerabilidad />
      </main>
    </div>
  );
}
