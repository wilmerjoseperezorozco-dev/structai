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
} from "lucide-react";

type Motor = {
  nombre: string;
  dominio: string;
  icon: React.ReactNode;
};

const MOTORES: Motor[] = [
  { nombre: "APU", dominio: "Precios unitarios", icon: <Calculator size={17} /> },
  { nombre: "Estructural", dominio: "Deformación y pandeo", icon: <Ruler size={17} /> },
  { nombre: "AquAI", dominio: "Acueducto y alcantarillado", icon: <Droplets size={17} /> },
  { nombre: "GeoPot", dominio: "Geotecnia y laboratorio", icon: <Mountain size={17} /> },
  { nombre: "Vías", dominio: "Diseño vial INVIAS", icon: <Route size={17} /> },
  { nombre: "Gerencia", dominio: "EVM + predicción ML", icon: <ClipboardList size={17} /> },
];

export function Hero() {
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
                NSR-10 C.9.2 — f&apos;c ≥ 21 MPa{" "}
                <span className="text-ink-500">(zona sísmica alta)</span>
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
          {MOTORES.map((m) => (
            <div
              key={m.nombre}
              className="flex items-start gap-2.5 rounded-xl border border-ink-800 bg-ink-900/50 px-3.5 py-3"
            >
              <span className="mt-0.5 text-bronze-400">{m.icon}</span>
              <div className="min-w-0">
                <p className="text-sm font-medium text-ink-100">{m.nombre}</p>
                <p className="truncate text-xs text-ink-500">{m.dominio}</p>
              </div>
            </div>
          ))}
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
