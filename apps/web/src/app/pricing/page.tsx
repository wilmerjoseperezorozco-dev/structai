"use client";

import { Check, X, HardHat, Zap, Building2 } from "lucide-react";
import clsx from "clsx";
import Link from "next/link";
import { PLANES, PRO_ANUAL, WOMPI_CHECKOUT_URL, WOMPI_ES_MODO_PRUEBA, formatCOP } from "@/lib/freemium";

// Correo de contacto para cotización Enterprise — sin autoservicio (ver
// comentario en freemium.ts): todavía no hay cliente institucional para
// calibrar un precio de catálogo.
const ENTERPRISE_CONTACTO = "mailto:wilmerjoseperezorozco@gmail.com?subject=StructAI%20Enterprise";

const FEATURES = [
  { label: "NSR-10 completa (11 títulos)", free: true,  pro: true,  enterprise: true },
  { label: "NTC complementarias",          free: true,  pro: true,  enterprise: true },
  { label: "Consulta RAG normativa",       free: true,  pro: true,  enterprise: true },
  { label: "APU por mes",                  free: "5",   pro: "∞",   enterprise: "∞" },
  { label: "Proyectos simultáneos",        free: "1",   pro: "∞",   enterprise: "∞" },
  { label: "Historial de consultas",       free: "7 d", pro: "∞",   enterprise: "∞" },
  { label: "Exportar PDF trazable",        free: false, pro: true,  enterprise: true },
  { label: "IC90 Monte Carlo",             free: true,  pro: true,  enterprise: true },
  { label: "Detección fotográfica YOLO",   free: false, pro: true,  enterprise: true },
  { label: "Seguridad industrial",         free: false, pro: true,  enterprise: true },
  { label: "Soporte prioritario",          free: false, pro: true,  enterprise: true },
  { label: "Cupos para todo un semillero", free: false, pro: false, enterprise: true },
  { label: "Onboarding y soporte dedicado",free: false, pro: false, enterprise: true },
];

function FeatureVal({ val }: { val: boolean | string }) {
  if (val === true)  return <Check size={16} className="text-green-400 mx-auto" />;
  if (val === false) return <X size={16} className="text-concrete-600 mx-auto" />;
  return <span className="text-sm font-semibold text-brand-300">{val}</span>;
}

export default function PricingPage() {
  return (
    <div className="min-h-full bg-concrete-900 px-4 py-10">
      <div className="max-w-4xl mx-auto">

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
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 items-stretch">

          {/* Free */}
          <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6 flex flex-col">
            <p className="text-xs uppercase tracking-widest text-concrete-400 mb-2">Gratis</p>
            <div className="flex items-end gap-1 mb-1">
              <span className="text-4xl font-bold text-white">$0</span>
            </div>
            <p className="text-xs text-concrete-500 mb-6">Para siempre</p>
            <Link
              href="/login"
              className="mt-auto block w-full py-3 rounded-xl border border-concrete-600 text-sm text-concrete-300 hover:border-concrete-500 transition text-center"
            >
              Empezar gratis
            </Link>
          </div>

          {/* Pro */}
          <div className="bg-brand-950 border border-brand-700/60 rounded-2xl p-6 relative flex flex-col">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="inline-flex items-center gap-1 bg-brand-600 text-ink-950 text-xs font-semibold px-3 py-1 rounded-full">
                <Zap size={11} /> Precio de lanzamiento
              </span>
            </div>
            <p className="text-xs uppercase tracking-widest text-brand-300 mb-2">Pro</p>
            <div className="flex items-end gap-1 mb-1">
              <span className="text-4xl font-bold text-white">
                {formatCOP(PLANES.pro.precio_mes)}
              </span>
              <span className="text-concrete-400 text-sm mb-1">/mes</span>
            </div>
            <p className="text-xs text-brand-400 mb-6">
              o {formatCOP(PRO_ANUAL.precio_anual)}/año · ahorras 33%
            </p>
            <a
              href={WOMPI_CHECKOUT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-auto block w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-ink-950 text-sm font-semibold transition text-center"
            >
              Activar Pro
            </a>
            {WOMPI_ES_MODO_PRUEBA && (
              <p className="text-center text-[10px] text-yellow-500 mt-2">
                ⚠ Pago en modo prueba — reemplazar por el link de producción antes de cobrar real
              </p>
            )}
          </div>

          {/* Enterprise */}
          <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6 flex flex-col">
            <p className="text-xs uppercase tracking-widest text-concrete-400 mb-2 flex items-center gap-1.5">
              <Building2 size={12} /> Enterprise
            </p>
            <div className="flex items-end gap-1 mb-1">
              <span className="text-2xl font-bold text-white">A medida</span>
            </div>
            <p className="text-xs text-concrete-500 mb-6">
              Para semilleros, facultades y constructoras
            </p>
            <a
              href={ENTERPRISE_CONTACTO}
              className="mt-auto block w-full py-3 rounded-xl border border-concrete-600 text-sm text-concrete-300 hover:border-concrete-500 transition text-center"
            >
              Hablar con nosotros
            </a>
          </div>
        </div>

        {/* Tabla comparativa */}
        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl overflow-x-auto">
          <div className="min-w-[560px]">
            <div className="grid grid-cols-4 text-xs font-semibold uppercase tracking-wide text-concrete-400 px-4 py-3 border-b border-concrete-700">
              <span>Función</span>
              <span className="text-center">Gratis</span>
              <span className="text-center text-brand-400">Pro</span>
              <span className="text-center text-concrete-300">Enterprise</span>
            </div>
            {FEATURES.map((f, i) => (
              <div
                key={f.label}
                className={clsx(
                  "grid grid-cols-4 items-center px-4 py-3 text-sm",
                  i % 2 === 0 ? "bg-concrete-800" : "bg-concrete-750",
                  "border-b border-concrete-700/50 last:border-0"
                )}
              >
                <span className="text-concrete-300">{f.label}</span>
                <div className="text-center"><FeatureVal val={f.free} /></div>
                <div className="text-center"><FeatureVal val={f.pro} /></div>
                <div className="text-center"><FeatureVal val={f.enterprise} /></div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-concrete-600 mt-6">
          Pago seguro con Wompi · Cancela cuando quieras · Factura Colombia
        </p>
      </div>
    </div>
  );
}
