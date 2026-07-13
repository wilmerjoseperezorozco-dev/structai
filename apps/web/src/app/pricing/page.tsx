"use client";

import { Check, X, HardHat, Zap } from "lucide-react";
import clsx from "clsx";
import { PLANES } from "@/lib/freemium";

const FEATURES = [
  { label: "NSR-10 completa (11 títulos)", free: true,  pro: true  },
  { label: "NTC complementarias",          free: true,  pro: true  },
  { label: "Consulta RAG normativa",       free: true,  pro: true  },
  { label: "APU por mes",                  free: "5",   pro: "∞"   },
  { label: "Proyectos simultáneos",        free: "1",   pro: "∞"   },
  { label: "Historial de consultas",       free: "7 d", pro: "∞"   },
  { label: "Exportar PDF trazable",        free: false, pro: true  },
  { label: "IC90 Monte Carlo",             free: true,  pro: true  },
  { label: "Detección fotográfica YOLO",   free: false, pro: true  },
  { label: "Seguridad industrial",         free: false, pro: true  },
  { label: "Soporte prioritario",          free: false, pro: true  },
];

function FeatureVal({ val }: { val: boolean | string }) {
  if (val === true)  return <Check size={16} className="text-green-400 mx-auto" />;
  if (val === false) return <X size={16} className="text-concrete-600 mx-auto" />;
  return <span className="text-sm font-semibold text-brand-300">{val}</span>;
}

export default function PricingPage() {
  return (
    <div className="min-h-full bg-concrete-900 px-4 py-10">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 mb-4 px-3 py-1.5 bg-brand-900/50 border border-brand-700/40 rounded-full">
            <HardHat size={14} className="text-brand-400" />
            <span className="text-xs text-brand-300 font-medium">Construdata · Planes 2026</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">
            Elige tu plan
          </h1>
          <p className="text-concrete-400 text-sm">
            Empieza gratis. Actualiza cuando necesites PDF, proyectos ilimitados y más.
          </p>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">

          {/* Free */}
          <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6">
            <p className="text-xs uppercase tracking-widest text-concrete-400 mb-2">Gratis</p>
            <div className="flex items-end gap-1 mb-1">
              <span className="text-4xl font-bold text-white">$0</span>
            </div>
            <p className="text-xs text-concrete-500 mb-6">Para siempre</p>
            <button className="w-full py-3 rounded-xl border border-concrete-600 text-sm text-concrete-300 hover:border-concrete-500 transition">
              Empezar gratis
            </button>
          </div>

          {/* Pro */}
          <div className="bg-brand-950 border border-brand-700/60 rounded-2xl p-6 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="inline-flex items-center gap-1 bg-brand-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                <Zap size={11} /> Recomendado
              </span>
            </div>
            <p className="text-xs uppercase tracking-widest text-brand-300 mb-2">Pro</p>
            <div className="flex items-end gap-1 mb-1">
              <span className="text-4xl font-bold text-white">
                ${(PLANES.pro.precio_mes / 1000).toFixed(0)}K
              </span>
              <span className="text-concrete-400 text-sm mb-1">COP/mes</span>
            </div>
            <p className="text-xs text-brand-400 mb-6">
              o $159K/año · ahorras 33%
            </p>
            <button className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition">
              Activar Pro
            </button>
          </div>
        </div>

        {/* Tabla comparativa */}
        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl overflow-hidden">
          <div className="grid grid-cols-3 text-xs font-semibold uppercase tracking-wide text-concrete-400 px-4 py-3 border-b border-concrete-700">
            <span>Función</span>
            <span className="text-center">Gratis</span>
            <span className="text-center text-brand-400">Pro</span>
          </div>
          {FEATURES.map((f, i) => (
            <div
              key={f.label}
              className={clsx(
                "grid grid-cols-3 items-center px-4 py-3 text-sm",
                i % 2 === 0 ? "bg-concrete-800" : "bg-concrete-750",
                "border-b border-concrete-700/50 last:border-0"
              )}
            >
              <span className="text-concrete-300">{f.label}</span>
              <div className="text-center"><FeatureVal val={f.free} /></div>
              <div className="text-center"><FeatureVal val={f.pro} /></div>
            </div>
          ))}
        </div>

        <p className="text-center text-xs text-concrete-600 mt-6">
          Pago seguro con Wompi · Cancela cuando quieras · Factura Colombia
        </p>
      </div>
    </div>
  );
}
