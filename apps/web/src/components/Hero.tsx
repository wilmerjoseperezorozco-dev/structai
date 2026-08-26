"use client";

import { useState } from "react";
import Link from "next/link";
import {
  HardHat,
  ShieldCheck,
  Calculator,
  Ruler,
  Droplets,
  Mountain,
  Route,
  ClipboardList,
  ArrowRight,
  Plus,
} from "lucide-react";
import clsx from "clsx";

type Motor = {
  nombre: string;
  dominio: string;
  // Guía corta que aparece al pasar el mouse o tocar la tarjeta — capacidad
  // real del motor, no marketing genérico (ver [[project_construdata]] en
  // la memoria del proyecto: cada uno de estos ya tiene tests reales).
  guia: string;
  icon: React.ReactNode;
};

const MOTORES: Motor[] = [
  {
    nombre: "APU",
    dominio: "Precios unitarios",
    guia: "Análisis de precios unitarios con incertidumbre real: intervalo de confianza IC90 por Monte Carlo, catálogo Construdata 2026 Barranquilla, cada insumo trazado a su fuente.",
    icon: <Calculator size={17} />,
  },
  {
    nombre: "Estructural",
    dominio: "Deformación y pandeo",
    guia: "Deformación de vigas (Euler-Bernoulli) y pandeo de columnas (Euler/Johnson), con simulación Monte Carlo de incertidumbre sobre los resultados.",
    icon: <Ruler size={17} />,
  },
  {
    nombre: "AquAI",
    dominio: "Acueducto y alcantarillado",
    guia: "Acueducto y alcantarillado bajo RAS 2000: cadena de caudales, Hazen-Williams, golpe de ariete, diseño de PTAP/PTAR y tarifas CRA.",
    icon: <Droplets size={17} />,
  },
  {
    nombre: "GeoPot",
    dominio: "Geotecnia y laboratorio",
    guia: "Laboratorio de suelos (clasificación USCS, Proctor, CBR) y zonificación sísmica NSR-10 por departamento, con norma ASTM/INV citada en cada resultado.",
    icon: <Mountain size={17} />,
  },
  {
    nombre: "Vías",
    dominio: "Diseño vial INVIAS",
    guia: "Diseño geométrico y de pavimentos (INVIAS 2008, AASHTO-93), más 15 verificadores de normas NTC de materiales de vías.",
    icon: <Route size={17} />,
  },
  {
    nombre: "Gerencia",
    dominio: "EVM + predicción ML",
    guia: "Earned Value Management (CPI/SPI/EAC) y predicción de riesgo y fecha de término por machine learning, sobre el avance real de tu obra.",
    icon: <ClipboardList size={17} />,
  },
];

export function Hero() {
  // Sin "hover-only": esta es una PWA que se usa mucho desde el celular,
  // donde no existe :hover real. El mismo estado se activa con mouse
  // (desktop), con tap (móvil, vía onClick) y con teclado (foco natural de
  // <button>) — nunca queda información solo detrás de un mouseover.
  const [abierto, setAbierto] = useState<string | null>(null);

  return (
    <div className="h-full overflow-y-auto bg-ink-950">
      <div className="relative">
        {/* Atmósfera: retícula de plano técnico + resplandor cálido, muy sutil */}
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

        <div className="relative mx-auto max-w-3xl">
          {/* Barra superior */}
          <header className="flex items-center justify-between px-5 py-4">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-bronze-500">
                <HardHat size={15} className="text-ink-950" />
              </div>
              <span className="font-display text-sm font-semibold tracking-tight text-ink-50">
                StructAI
              </span>
            </div>
            <Link
              href="/login"
              className="text-xs text-ink-300 transition hover:text-bronze-300"
            >
              Ingresar
            </Link>
          </header>

          {/* Hero */}
          <div className="px-5 pb-8 pt-8 sm:pt-14">
            <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-bronze-400">
              PWA · Ingeniería civil · Colombia
            </p>
            <h1 className="text-balance font-display text-[2.35rem] font-medium leading-[1.1] text-ink-50 sm:text-6xl sm:leading-[1.05]">
              Cálculos con{" "}
              <span className="text-bronze-400">trazabilidad normativa</span>
            </h1>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-ink-300">
              NSR-10, NTC y SGSST citados con norma, título y sección exacta en cada
              respuesta. Precios unitarios, estructuras, acueducto, geotecnia, vías y
              gerencia de obra — con la norma real detrás, nunca una cifra inventada.
            </p>

            {/* Franja de prueba: muestra, no solo afirma, la trazabilidad */}
            <div className="mt-6 inline-flex items-center gap-3 rounded-xl border border-ink-700 bg-ink-900/70 px-4 py-3">
              <ShieldCheck size={16} className="flex-shrink-0 text-bronze-400" />
              <code className="font-mono text-xs text-ink-200">
                NSR-10 C.21.1.4.2 — f&apos;c ≥ 21 MPa{" "}
                <span className="text-ink-500">(estructuras DMO/DES)</span>
              </code>
            </div>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-bronze-500 px-5 py-3 text-sm font-semibold text-ink-950 transition hover:bg-bronze-400"
              >
                Ingresar
                <ArrowRight size={16} />
              </Link>
              <Link
                href="/?tab=chat"
                className="inline-flex items-center gap-2 rounded-xl border border-ink-700 px-5 py-3 text-sm text-ink-200 transition hover:border-bronze-600/60 hover:text-bronze-300"
              >
                Probar el chat normativo
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Motores */}
      <div className="mx-auto max-w-3xl border-t border-ink-800 px-5 py-8">
        <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-500">
          7 motores de dominio
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {MOTORES.map((m) => {
            const activo = abierto === m.nombre;
            return (
              <button
                key={m.nombre}
                type="button"
                aria-expanded={activo}
                onClick={() => setAbierto(activo ? null : m.nombre)}
                onMouseEnter={() => setAbierto(m.nombre)}
                onMouseLeave={() => setAbierto((cur) => (cur === m.nombre ? null : cur))}
                className={clsx(
                  "group flex w-full flex-col items-start gap-2.5 rounded-xl border px-3.5 py-3 text-left transition-all duration-300",
                  activo
                    ? "border-bronze-600/60 bg-ink-900 shadow-[0_0_28px_-10px_rgba(217,154,63,0.4)]"
                    : "border-ink-800 bg-ink-900/50 hover:border-ink-700"
                )}
              >
                <div className="flex w-full items-start gap-2.5">
                  <span
                    className={clsx(
                      "mt-0.5 rounded-md p-1 transition-colors duration-300",
                      activo ? "bg-bronze-500/15 text-bronze-300" : "text-bronze-400"
                    )}
                  >
                    {m.icon}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-ink-100">{m.nombre}</p>
                    <p className="truncate text-xs text-ink-500">{m.dominio}</p>
                  </div>
                  <Plus
                    size={13}
                    className={clsx(
                      "mt-1 flex-shrink-0 text-ink-600 transition-transform duration-300",
                      activo && "rotate-45 text-bronze-400"
                    )}
                  />
                </div>

                {/* Guía — animada con la técnica grid-template-rows 0fr→1fr:
                    anima a "altura automática" sin medir con JS, y colapsa
                    limpio a 0 sin dejar un salto brusco de layout. */}
                <div
                  className="grid w-full transition-[grid-template-rows] duration-300 ease-out"
                  style={{ gridTemplateRows: activo ? "1fr" : "0fr" }}
                >
                  <div className="overflow-hidden">
                    <p className="pt-2 text-xs leading-relaxed text-ink-400">
                      {m.guia}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Pie */}
      <div className="mx-auto max-w-3xl px-5 pb-8 pt-2">
        <p className="text-[11px] text-ink-600">
          Wilmer José Pérez Orozco · Trabajo de grado · Corporación Universidad de la Costa
        </p>
      </div>
    </div>
  );
}
