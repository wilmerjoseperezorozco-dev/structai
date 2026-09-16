"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  HardHat,
  Check,
  X,
  Copy,
  CopyCheck,
  ExternalLink,
  Building2,
  Coins,
  Layers,
  Droplet,
} from "lucide-react";
import clsx from "clsx";
import comparativas from "@/data/comparativas.json";

// Mismo lenguaje visual que /pricing y Hero.tsx (ink/bronze, blueprint de
// plano técnico, font-display Fraunces) — ver el comentario de rediseño en
// pricing/page.tsx: cualquier pantalla pública nueva se ve como la misma
// marca, no como un panel aparte.

// Deliberadamente NO se afirma nada propio sobre ChatGPT/Copilot/Perplexity
// (latencia, costo, exactitud) — docs/comparacion.md ya explica por qué: no
// hay acceso verificado a sus bases internas, y afirmar algo sobre una
// herramienta ajena sin poder probarlo no es el estándar de honestidad de
// este proyecto. En vez de inventar una cifra, el botón "Repítela en X" abre
// la MISMA pregunta ya verificada en ese asistente para que cada quien la
// compare en vivo — la comparación la hace el lector, no una tabla que
// afirma algo no verificable.
type Categoria = "estructural" | "precios" | "geotecnia" | "agua";

const CATEGORIAS: { id: Categoria; label: string; icon: React.ReactNode }[] = [
  { id: "estructural", label: "Estructural", icon: <Building2 size={13} /> },
  { id: "precios", label: "Precios", icon: <Coins size={13} /> },
  { id: "geotecnia", label: "Geotecnia", icon: <Layers size={13} /> },
  { id: "agua", label: "Agua", icon: <Droplet size={13} /> },
];

const ASISTENTES: { id: string; label: string; buildUrl: (q: string) => string }[] = [
  {
    id: "chatgpt",
    label: "ChatGPT",
    buildUrl: (q) => `https://chatgpt.com/?q=${encodeURIComponent(q)}`,
  },
  {
    id: "copilot",
    label: "Copilot",
    buildUrl: (q) => `https://copilot.microsoft.com/?q=${encodeURIComponent(q)}`,
  },
  {
    id: "perplexity",
    label: "Perplexity",
    buildUrl: (q) => `https://www.perplexity.ai/search?q=${encodeURIComponent(q)}`,
  },
];

type Criterio = { criterio: string; structai: string; generico: string };
type PreguntaEjemplo = {
  id: string;
  categoria: Categoria;
  pregunta: string;
  respuesta_structai: string;
  fuente: string;
};

const CRITERIOS = comparativas.criterios as Criterio[];
const PREGUNTAS = comparativas.preguntas_ejemplo as PreguntaEjemplo[];

export default function ComparacionPage() {
  const [filtro, setFiltro] = useState<Categoria | "todas">("todas");
  const [copiadaId, setCopiadaId] = useState<string | null>(null);

  const preguntasFiltradas = useMemo(
    () => (filtro === "todas" ? PREGUNTAS : PREGUNTAS.filter((p) => p.categoria === filtro)),
    [filtro]
  );

  async function copiarPregunta(id: string, texto: string) {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiadaId(id);
      setTimeout(() => setCopiadaId((actual) => (actual === id ? null : actual)), 2000);
    } catch {
      // Clipboard puede fallar por permisos del navegador — el enlace de
      // cada asistente sigue funcionando igual, solo no queda pre-copiada.
    }
  }

  return (
    <div className="relative h-full overflow-y-auto bg-ink-950">
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

      <header className="sticky top-0 z-20 border-b border-ink-800 bg-ink-950/85 backdrop-blur-sm">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link href="/" className="-my-2.5 flex items-center gap-2 py-2.5">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-bronze-500">
              <HardHat size={13} className="text-ink-950" />
            </div>
            <span className="font-display text-sm font-semibold text-ink-50">StructAI</span>
          </Link>
          <Link
            href="/pricing"
            className="-mx-2 -my-3.5 px-2 py-3.5 text-xs text-ink-300 transition hover:text-bronze-300"
          >
            Ver planes
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
                Comparación honesta
              </span>
            </div>
            <h1 className="text-balance font-display text-4xl font-medium text-ink-50 sm:text-5xl">
              ¿Por qué StructAI?
            </h1>
            <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-ink-400">
              No afirmamos nada sobre ChatGPT, Copilot o Perplexity que no podamos probar —
              no tenemos acceso verificado a sus bases internas. En vez de eso, cada pregunta de
              abajo ya tiene la respuesta real de StructAI, con fuente citada, y un enlace para que
              la repitas ahí mismo y compares tú.
            </p>
          </div>

          {/* Tabla de criterios verificables — StructAI vs. asistente de IA genérico */}
          <div className="reveal reveal-2 mb-12 overflow-x-auto rounded-2xl border border-ink-800 bg-ink-900/60">
            <div className="min-w-[640px]">
              <div className="grid grid-cols-3 border-b border-ink-800 px-4 py-3 font-mono text-xs font-semibold uppercase tracking-wide text-ink-500">
                <span>Criterio</span>
                <span className="text-bronze-400">StructAI</span>
                <span>Asistente de IA genérico</span>
              </div>
              {CRITERIOS.map((c) => (
                <div
                  key={c.criterio}
                  className="grid grid-cols-3 gap-4 border-b border-ink-800/60 px-4 py-4 text-sm transition-colors last:border-0 hover:bg-ink-800/50"
                >
                  <span className="text-ink-300">{c.criterio}</span>
                  <span className="flex items-start gap-1.5 text-ink-200">
                    <Check size={14} className="mt-0.5 flex-shrink-0 text-bronze-400" />
                    {c.structai}
                  </span>
                  <span className="flex items-start gap-1.5 text-ink-500">
                    <X size={14} className="mt-0.5 flex-shrink-0 text-ink-700" />
                    {c.generico}
                  </span>
                </div>
              ))}
            </div>
            <p className="border-t border-ink-800 px-4 py-3 text-[11px] text-ink-600">
              Cada fila es verificable hoy mismo:{" "}
              <a
                href="https://structai-api-235651108862.us-east1.run.app/data-status"
                target="_blank"
                rel="noopener noreferrer"
                className="text-bronze-400 underline decoration-bronze-700/60 underline-offset-2 hover:text-bronze-300"
              >
                /data-status
              </a>{" "}
              en vivo, o el detalle completo en{" "}
              <a
                href="https://github.com/wilmerjoseperezorozco-dev/structai/blob/master/docs/comparacion.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-bronze-400 underline decoration-bronze-700/60 underline-offset-2 hover:text-bronze-300"
              >
                docs/comparacion.md
              </a>
              .
            </p>
          </div>

          {/* Pruébalo tú mismo */}
          <div className="reveal reveal-3 mb-6 flex items-center justify-between gap-3">
            <h2 className="font-display text-xl font-medium text-ink-50">Pruébalo tú mismo</h2>
          </div>

          {/* Filtro por tipo de pregunta */}
          <div className="reveal reveal-3 mb-6 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setFiltro("todas")}
              className={clsx(
                "rounded-full border px-3 py-1.5 font-mono text-xs transition",
                filtro === "todas"
                  ? "border-bronze-500 bg-bronze-500 text-ink-950"
                  : "border-ink-700 text-ink-300 hover:border-bronze-600/60 hover:text-bronze-300"
              )}
            >
              Todas
            </button>
            {CATEGORIAS.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setFiltro(c.id)}
                className={clsx(
                  "flex items-center gap-1.5 rounded-full border px-3 py-1.5 font-mono text-xs transition",
                  filtro === c.id
                    ? "border-bronze-500 bg-bronze-500 text-ink-950"
                    : "border-ink-700 text-ink-300 hover:border-bronze-600/60 hover:text-bronze-300"
                )}
              >
                {c.icon}
                {c.label}
              </button>
            ))}
          </div>

          {/* Preguntas de ejemplo */}
          <div className="reveal reveal-4 mb-8 space-y-4">
            {preguntasFiltradas.map((p) => {
              const yaCopiada = copiadaId === p.id;
              return (
                <div
                  key={p.id}
                  className="rounded-2xl border border-ink-800 bg-ink-900/60 p-5 transition hover:border-ink-700"
                >
                  <p className="mb-3 text-sm font-medium text-ink-100">{p.pregunta}</p>
                  <div className="mb-4 rounded-xl border border-bronze-700/30 bg-bronze-950/20 px-3.5 py-3">
                    <p className="text-sm text-ink-200">{p.respuesta_structai}</p>
                    <p className="mt-1.5 font-mono text-[10px] uppercase tracking-wide text-bronze-400">
                      {p.fuente}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[10px] uppercase tracking-wide text-ink-600">
                      Repite esta pregunta en
                    </span>
                    {ASISTENTES.map((a) => (
                      <a
                        key={a.id}
                        href={a.buildUrl(p.pregunta)}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => copiarPregunta(p.id, p.pregunta)}
                        className="inline-flex items-center gap-1 rounded-lg border border-ink-700 px-2.5 py-1.5 text-xs text-ink-300 transition hover:border-bronze-600/60 hover:text-bronze-300"
                      >
                        {a.label}
                        <ExternalLink size={11} />
                      </a>
                    ))}
                    <button
                      type="button"
                      onClick={() => copiarPregunta(p.id, p.pregunta)}
                      className="inline-flex items-center gap-1 rounded-lg border border-ink-800 px-2.5 py-1.5 text-xs text-ink-500 transition hover:border-ink-600 hover:text-ink-300"
                      title="Copiar la pregunta"
                    >
                      {yaCopiada ? <CopyCheck size={12} className="text-bronze-400" /> : <Copy size={12} />}
                      {yaCopiada ? "Copiada" : "Copiar"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <p className="reveal reveal-5 text-center text-[11px] text-ink-600">
            Cada enlace intenta pre-cargar la pregunta en ese asistente — si la plataforma no lo
            hace, ya quedó copiada al portapapeles, pégala con Ctrl+V. Latencia, costo y exactitud
            de esos asistentes no se muestran aquí porque no tenemos forma de verificarlos en
            vivo — compáralos tú mismo con la misma pregunta.
          </p>
        </div>
      </div>
    </div>
  );
}
