"use client";

import { useState } from "react";
import { Check, X, HardHat, Zap, Building2, ArrowRight } from "lucide-react";
import clsx from "clsx";
import Link from "next/link";
import { PLANES, PRO_ANUAL, WOMPI_CHECKOUT_URL, WOMPI_ES_MODO_PRUEBA, formatCOP } from "@/lib/freemium";

// Rediseño 2026-08-26: esta página vivía en la paleta "concrete/brand"
// (slate + naranja plano) de las pantallas internas del producto, distinta
// del lenguaje visual real de la marca — el blueprint de plano técnico
// (fondo "ink", retícula punteada, acento "bronze", titular en font-display
// Fraunces) que ya usa Hero.tsx, lo primero que ve cualquier visitante. Se
// trae ese mismo lenguaje aquí en vez de inventar uno nuevo — /pricing es
// la segunda pantalla que más ve un visitante nuevo, debería sentirse como
// la misma marca, no un panel de administración aparte.

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
  if (val === true)  return <Check size={16} className="mx-auto text-bronze-400" />;
  if (val === false) return <X size={16} className="mx-auto text-ink-700" />;
  return <span className="text-sm font-semibold text-bronze-300">{val}</span>;
}

export default function PricingPage() {
  // Solo cambia el precio MOSTRADO — hoy no hay un link de pago Wompi
  // distinto por frecuencia de facturación (la activación de Pro es manual,
  // ver freemium.ts), así que el CTA sigue siendo el mismo checkout en
  // ambos casos. Mostrar dos links falsos habría sido peor que mostrar uno
  // honesto.
  const [anual, setAnual] = useState(false);
  const precioMostrado = anual ? PRO_ANUAL.precio_mes : PLANES.pro.precio_mes;

  return (
    <div className="relative h-full overflow-y-auto bg-ink-950">
      {/* Misma atmósfera del Hero: retícula de plano técnico + resplandor
          cálido, muy sutil — nunca compite con el contenido. Van en el
          contenedor con scroll (no en el wrapper con padding de abajo)
          para cubrir todo el alto real de la página, no solo un viewport. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage:
            "linear-gradient(#E6B564 1px, transparent 1px), linear-gradient(90deg, #E6B564 1px, transparent 1px)",
          backgroundSize: "42px 42px",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 left-1/2 h-[28rem] w-[28rem] -translate-x-1/2 rounded-full bg-bronze-700/20 blur-[110px]"
      />

      {/* Barra de navegación mínima — esta página no tenía NINGUNA forma de
          volver al inicio o a login salvo el botón "atrás" del navegador
          (hueco real de navegación, encontrado al revisar buenas prácticas:
          toda pantalla debe dejar un camino de vuelta visible, no depender
          solo del historial). Sticky porque la página es lo bastante larga
          para valer la pena tenerla siempre a mano; con blur+borde para no
          tapar el contenido de golpe al hacer scroll. */}
      <header className="sticky top-0 z-20 border-b border-ink-800 bg-ink-950/85 backdrop-blur-sm">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-bronze-500">
              <HardHat size={13} className="text-ink-950" />
            </div>
            <span className="font-display text-sm font-semibold text-ink-50">StructAI</span>
          </Link>
          <Link
            href="/login"
            className="text-xs text-ink-300 transition hover:text-bronze-300"
          >
            Ingresar
          </Link>
        </div>
      </header>

      <div className="px-4 py-10">
      <div className="relative mx-auto max-w-4xl">

        {/* Header */}
        <div className="reveal reveal-1 mb-10 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-ink-700 bg-ink-900/70 px-3 py-1.5">
            <HardHat size={14} className="text-bronze-400" />
            <span className="font-mono text-[11px] uppercase tracking-[0.15em] text-bronze-300">
              StructAI · Planes 2026
            </span>
          </div>
          <h1 className="text-balance font-display text-4xl font-medium text-ink-50 sm:text-5xl">
            Elige tu plan
          </h1>
          <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-ink-400">
            Empieza gratis. Actualiza cuando necesites PDF, proyectos ilimitados y más.
          </p>

          {/* Toggle mensual/anual */}
          <div className="mt-7 inline-flex items-center gap-3">
            <div
              role="tablist"
              aria-label="Frecuencia de facturación"
              className="relative inline-grid grid-cols-2 rounded-full border border-ink-700 bg-ink-900/70 p-1 font-mono text-xs font-semibold"
            >
              <span
                aria-hidden
                className={clsx(
                  "absolute inset-y-1 left-1 w-[calc(50%-0.25rem)] rounded-full bg-bronze-500 transition-transform duration-300 ease-out",
                  anual && "translate-x-[calc(100%+0.25rem)]"
                )}
              />
              <button
                type="button"
                role="tab"
                aria-selected={!anual}
                onClick={() => setAnual(false)}
                className={clsx(
                  "relative z-10 rounded-full px-4 py-1.5 transition-colors",
                  !anual ? "text-ink-950" : "text-ink-300 hover:text-ink-100"
                )}
              >
                Mensual
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={anual}
                onClick={() => setAnual(true)}
                className={clsx(
                  "relative z-10 rounded-full px-4 py-1.5 transition-colors",
                  anual ? "text-ink-950" : "text-ink-300 hover:text-ink-100"
                )}
              >
                Anual
              </button>
            </div>
            <span className="rounded-full border border-bronze-700/40 bg-bronze-900/30 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide text-bronze-300">
              Anual: ahorras 33%
            </span>
          </div>
        </div>

        {/* Cards */}
        <div className="mb-8 grid grid-cols-1 items-stretch gap-4 sm:grid-cols-3">

          {/* Free */}
          <div className="reveal reveal-2 flex flex-col rounded-2xl border border-ink-800 bg-ink-900/60 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-ink-600">
            <p className="mb-2 font-mono text-xs uppercase tracking-widest text-ink-400">Gratis</p>
            <div className="mb-1 flex items-end gap-1">
              <span className="text-4xl font-bold text-ink-50">$0</span>
            </div>
            <p className="mb-6 text-xs text-ink-500">Para siempre</p>
            <Link
              href="/login"
              className="mt-auto block w-full rounded-xl border border-ink-700 py-3 text-center text-sm text-ink-200 transition hover:border-bronze-600/60 hover:text-bronze-300"
            >
              Empezar gratis
            </Link>
          </div>

          {/* Pro */}
          <div className="reveal reveal-3 relative flex flex-col rounded-2xl border border-bronze-700/50 bg-ink-900 p-6 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-[0_0_48px_-14px_rgba(217,154,63,0.45)]">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="inline-flex items-center gap-1 rounded-full bg-bronze-500 px-3 py-1 text-xs font-semibold text-ink-950">
                <Zap size={11} /> Precio de lanzamiento
              </span>
            </div>
            <p className="mb-2 font-mono text-xs uppercase tracking-widest text-bronze-400">Pro</p>
            <div key={anual ? "anual" : "mensual"} className="price-pop mb-1 flex items-end gap-1">
              <span className="tabular-nums text-4xl font-bold text-ink-50">
                {formatCOP(precioMostrado)}
              </span>
              <span className="mb-1 text-sm text-ink-400">/mes</span>
            </div>
            <p className="mb-6 text-xs text-bronze-400">
              {anual
                ? `Facturado ${formatCOP(PRO_ANUAL.precio_anual)}/año`
                : `o ${formatCOP(PRO_ANUAL.precio_anual)}/año · ahorras 33%`}
            </p>
            <a
              href={WOMPI_CHECKOUT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-auto flex w-full items-center justify-center gap-1.5 rounded-xl bg-bronze-500 py-3 text-sm font-semibold text-ink-950 transition hover:bg-bronze-400"
            >
              Activar Pro
              <ArrowRight size={15} />
            </a>
            {WOMPI_ES_MODO_PRUEBA && (
              <p className="mt-2 text-center text-[10px] text-yellow-500">
                ⚠ Pago en modo prueba — reemplazar por el link de producción antes de cobrar real
              </p>
            )}
          </div>

          {/* Enterprise */}
          <div className="reveal reveal-4 flex flex-col rounded-2xl border border-ink-800 bg-ink-900/60 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-ink-600">
            <p className="mb-2 flex items-center gap-1.5 font-mono text-xs uppercase tracking-widest text-ink-400">
              <Building2 size={12} /> Enterprise
            </p>
            <div className="mb-1 flex items-end gap-1">
              <span className="text-2xl font-bold text-ink-50">A medida</span>
            </div>
            <p className="mb-6 text-xs text-ink-500">
              Para semilleros, facultades y constructoras
            </p>
            <a
              href={ENTERPRISE_CONTACTO}
              className="mt-auto block w-full rounded-xl border border-ink-700 py-3 text-center text-sm text-ink-200 transition hover:border-bronze-600/60 hover:text-bronze-300"
            >
              Hablar con nosotros
            </a>
          </div>
        </div>

        {/* Tabla comparativa */}
        <div className="reveal reveal-5 overflow-x-auto rounded-2xl border border-ink-800 bg-ink-900/60">
          <div className="min-w-[560px]">
            <div className="grid grid-cols-4 border-b border-ink-800 px-4 py-3 font-mono text-xs font-semibold uppercase tracking-wide text-ink-500">
              <span>Función</span>
              <span className="text-center">Gratis</span>
              <span className="text-center text-bronze-400">Pro</span>
              <span className="text-center text-ink-300">Enterprise</span>
            </div>
            {FEATURES.map((f) => (
              <div
                key={f.label}
                className="grid grid-cols-4 items-center border-b border-ink-800/60 px-4 py-3 text-sm transition-colors last:border-0 hover:bg-ink-800/50"
              >
                <span className="text-ink-300">{f.label}</span>
                <div className="text-center"><FeatureVal val={f.free} /></div>
                <div className="text-center"><FeatureVal val={f.pro} /></div>
                <div className="text-center"><FeatureVal val={f.enterprise} /></div>
              </div>
            ))}
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-ink-600">
          Pago seguro con Wompi · Cancela cuando quieras · Factura Colombia
        </p>
      </div>
      </div>
    </div>
  );
}
