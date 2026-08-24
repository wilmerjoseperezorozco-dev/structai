"use client";

import { useState, useRef, useEffect, KeyboardEvent, ReactNode } from "react";
import { useRouter } from "next/navigation";
import TextareaAutosize from "react-textarea-autosize";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Loader2,
  BookOpen,
  Coins,
  ShieldAlert,
  Mountain,
  ChevronDown,
  ChevronUp,
  Sparkles,
  LogIn,
  ArrowRight,
} from "lucide-react";
import type { Session } from "@supabase/supabase-js";
import { consultarDelegado, type ConsultarResponse, type FuenteChunk } from "@/lib/api";
import { supabase } from "@/lib/supabase";

// ── Types ────────────────────────────────────────────────────────────────────

type Role = "user" | "assistant" | "error";

interface Message {
  id: string;
  role: Role;
  text: string;
  meta?: ConsultarResponse;
}

// ── Sugerencias agrupadas por dominio ───────────────────────────────────────
// Reflejan la cobertura real de StructAI (verificada 2026-08-21): normativa
// NSR-10/NTC completa, precios Barranquilla + INVIAS nacional (140
// provincias), seguridad industrial, y sismo/clima en vivo (SGC/IDEAM).
// Agrupar por categoría (en vez de una sola lista plana) es lo que le
// enseña al usuario, de un vistazo, TODO lo que puede preguntar — antes
// solo se veían ejemplos de normativa y precios locales, dando la
// impresión de una herramienta más limitada de lo que realmente es.

interface GrupoSugerencias {
  label: string;
  icon: ReactNode;
  preguntas: string[];
}

const GRUPOS_SUGERENCIAS: GrupoSugerencias[] = [
  {
    label: "Normativa NSR-10 / NTC",
    icon: <BookOpen size={13} />,
    preguntas: [
      "¿Qué resistencia mínima de concreto exige NSR-10 para columnas sísmicas?",
      "¿Cuál es el recubrimiento mínimo para vigas expuestas a la intemperie?",
    ],
  },
  {
    label: "Precios de construcción",
    icon: <Coins size={13} />,
    preguntas: [
      "¿Cuánto cuesta el cemento en Barranquilla?",
      "Precio de excavación mecánica en Chocó (INVIAS)",
    ],
  },
  {
    label: "Seguridad industrial",
    icon: <ShieldAlert size={13} />,
    preguntas: ["¿Cuándo es obligatorio el uso de arnés en trabajos en altura?"],
  },
  {
    label: "Sismo y clima",
    icon: <Mountain size={13} />,
    preguntas: [
      "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?",
      "¿StructAI me sirve para evaluar riesgo sísmico en mi proyecto?",
    ],
  },
];

// ── Fuentes colapsables ──────────────────────────────────────────────────────

function Fuentes({
  fuentes,
  normas,
  dominio,
  dominioLabel,
}: {
  fuentes: FuenteChunk[];
  normas: string[];
  dominio?: string;
  dominioLabel?: string;
}) {
  const [open, setOpen] = useState(false);
  if (!fuentes.length) return null;

  // Precios APU (dominio="apu_precios") usa un rótulo y estilo distinto al
  // de citas normativas: acá "norma" es en realidad la fuente del precio
  // (Construdata, contrato real, INVIAS...) y "seccion" ya trae el ítem con
  // su precio formateado — no tiene sentido mostrar "§" como si fuera un
  // artículo de norma.
  const esPrecios = dominio === "apu_precios";

  return (
    <div className="mt-2 rounded-xl border border-concrete-800 overflow-hidden text-xs">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-concrete-800/50 text-concrete-300 hover:bg-concrete-800 transition"
      >
        {esPrecios ? <Coins size={13} className="text-brand-400 flex-shrink-0" /> : <BookOpen size={13} className="text-brand-400 flex-shrink-0" />}
        <span className="font-medium truncate text-left">
          {esPrecios
            ? dominioLabel ?? "Precios de construcción"
            : normas.slice(0, 3).join(" · ") + (normas.length > 3 ? ` +${normas.length - 3} más` : "")}
        </span>
        <span className="ml-auto flex-shrink-0 text-concrete-500 tabular-nums">{fuentes.length}</span>
        {open ? <ChevronUp size={13} className="flex-shrink-0" /> : <ChevronDown size={13} className="flex-shrink-0" />}
      </button>

      {open && (
        <div className="divide-y divide-concrete-800">
          {fuentes.map((f, i) => (
            <div key={i} className="px-3 py-2.5 bg-concrete-900/40">
              {esPrecios ? (
                <>
                  <p className="font-mono font-medium text-concrete-100 mb-0.5">{f.seccion}</p>
                  <p className="text-concrete-500">{f.norma}</p>
                  {f.contenido_preview && (
                    <p className="text-concrete-500 mt-0.5">{f.contenido_preview}</p>
                  )}
                </>
              ) : (
                <>
                  <div className="flex justify-between items-center gap-2 mb-1">
                    <span className="font-mono font-medium text-brand-300 truncate">{f.norma}</span>
                    <span className="font-mono text-concrete-500 flex-shrink-0">§ {f.seccion}</span>
                    <span className="font-mono tabular-nums text-concrete-600 flex-shrink-0">
                      {(f.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-concrete-400 leading-relaxed">
                    {f.contenido_preview}
                    {f.contenido_preview.length >= 200 && "…"}
                  </p>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Burbuja de mensaje ───────────────────────────────────────────────────────
// Sin avatares circulares ni bubbles con cola: el rol se distingue por
// alineación + un rótulo de texto liviano, no por un ícono decorativo —
// más cerca de una interfaz de lectura que de un chat de mensajería.

const MARKDOWN_COMPONENTS = {
  p: ({ children }: { children?: ReactNode }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }: { children?: ReactNode }) => (
    <strong className="font-semibold text-brand-300">{children}</strong>
  ),
  em: ({ children }: { children?: ReactNode }) => <em className="text-concrete-200">{children}</em>,
  code: ({ children }: { children?: ReactNode }) => (
    <code className="bg-concrete-900 px-1 py-0.5 rounded text-brand-200 font-mono text-xs">{children}</code>
  ),
  ul: ({ children }: { children?: ReactNode }) => (
    <ul className="list-disc list-inside space-y-1 mb-2">{children}</ul>
  ),
  ol: ({ children }: { children?: ReactNode }) => (
    <ol className="list-decimal list-inside space-y-1 mb-2">{children}</ol>
  ),
  li: ({ children }: { children?: ReactNode }) => <li className="text-concrete-200">{children}</li>,
  h1: ({ children }: { children?: ReactNode }) => (
    <h1 className="text-base font-bold text-white mt-3 mb-1.5 first:mt-0">{children}</h1>
  ),
  h2: ({ children }: { children?: ReactNode }) => (
    <h2 className="text-sm font-bold text-white mt-3 mb-1.5 first:mt-0">{children}</h2>
  ),
  h3: ({ children }: { children?: ReactNode }) => (
    <h3 className="text-sm font-semibold text-brand-200 mt-2.5 mb-1 first:mt-0">{children}</h3>
  ),
  a: ({ href, children }: { href?: string; children?: ReactNode }) => (
    <a
      href={href}
      target={href?.startsWith("http") ? "_blank" : undefined}
      rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
      className="text-brand-400 underline underline-offset-2 hover:text-brand-300"
    >
      {children}
    </a>
  ),
};

// ── Aviso de responsabilidad profesional (issue #18) ────────────────────────
// Texto FIJO que viene del backend (rag_multi_norma.AVISO_RESPONSABILIDAD_PROFESIONAL),
// nunca generado por el LLM — por eso se renderiza en un bloque aparte del
// markdown de `respuesta`, con estilo propio, y no se le pasa por
// ReactMarkdown. Solo aparece cuando el dominio de la respuesta es de
// diseño/cálculo (normativa_general, geopot, aquai, vías); en apu_precios y
// gerencia el backend manda `aviso_responsabilidad: null` y este bloque no
// se pinta.
function AvisoResponsabilidad({ texto }: { texto: string }) {
  return (
    <div className="mt-2 flex gap-2 rounded-xl border border-amber-800/40 bg-amber-950/20 px-3 py-2.5 text-xs leading-relaxed text-amber-200/90">
      <ShieldAlert size={14} className="mt-0.5 flex-shrink-0 text-amber-400" />
      <p>{texto}</p>
    </div>
  );
}

function Bubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  const isError = msg.role === "error";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-brand-600 text-ink-950 px-4 py-2.5 text-sm leading-relaxed">
          <p>{msg.text}</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-red-800/50 bg-red-950/30 text-red-300 px-4 py-3 text-sm leading-relaxed">
        {msg.text}
      </div>
    );
  }

  return (
    <div className="w-full">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-brand-400 mb-1.5">
        StructAI
      </p>
      <div className="rounded-xl bg-concrete-800/40 px-4 py-3 text-sm leading-relaxed text-concrete-100">
        <ReactMarkdown components={MARKDOWN_COMPONENTS}>{msg.text}</ReactMarkdown>
      </div>

      {/* Metadatos RAG */}
      {msg.meta && (
        <div className="mt-1.5">
          {msg.meta.aviso_responsabilidad && (
            <AvisoResponsabilidad texto={msg.meta.aviso_responsabilidad} />
          )}
          <Fuentes
            fuentes={msg.meta.fuentes}
            normas={msg.meta.normas_citadas}
            dominio={msg.meta.dominio}
            dominioLabel={msg.meta.dominio_label}
          />
          <p className="text-[11px] text-concrete-600 mt-1 px-1 tabular-nums">
            {msg.meta.chunks_usados} fuentes consultadas · {(msg.meta.latencia_ms / 1000).toFixed(1)}s
          </p>
        </div>
      )}
    </div>
  );
}

// ── Historial offline (localStorage) ──────────────────────────────────────────
// Las respuestas del RAG vienen de un POST /ask, que el Service Worker no
// puede cachear automáticamente (el Cache API del navegador solo intercepta
// peticiones GET). Por eso el historial se persiste aquí, a nivel de app, para
// que un ingeniero sin señal (sótano, zona rural) siga viendo sus consultas
// previas al reabrir la PWA.
const HISTORY_KEY = "construdata_chat_history_v1";
const MENSAJE_BIENVENIDA: Message = {
  id: "welcome",
  role: "assistant",
  text:
    "Hola, soy el asistente de ingeniería civil de StructAI. Consúltame la **NSR-10** y **NTC** completas (artículo por artículo, con cita exacta), **seguridad industrial**, **precios reales** de Barranquilla/Atlántico y de las **140 provincias de Colombia** (INVIAS), y **amenaza sísmica en vivo** por municipio.\n\n¿Qué necesitas resolver hoy?",
};

function cargarHistorial(): Message[] {
  if (typeof window === "undefined") return [MENSAJE_BIENVENIDA];
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [MENSAJE_BIENVENIDA];
    const parsed = JSON.parse(raw) as Message[];
    return Array.isArray(parsed) && parsed.length > 0 ? parsed : [MENSAJE_BIENVENIDA];
  } catch {
    // localStorage corrupto o inaccesible (modo privado, cuota excedida) —
    // no debe romper el chat, solo se pierde el historial persistido.
    return [MENSAJE_BIENVENIDA];
  }
}

function guardarHistorial(messages: Message[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  } catch {
    // Cuota de localStorage excedida u otro error de escritura — se ignora,
    // el chat sigue funcionando en memoria para la sesión actual.
  }
}

// ── Chat principal ───────────────────────────────────────────────────────────

export default function Chat() {
  const router = useRouter();

  // Inicializador perezoso: lee localStorage UNA vez, en el primer render,
  // en vez de un useEffect de "carga" separado del de "guardado" — así se
  // evita la condición de carrera donde el efecto de guardado (con el
  // estado por defecto) sobreescribe el historial real antes de que el
  // efecto de carga termine de aplicarlo. Seguro aquí porque este
  // componente se importa con ssr:false (ver app/page.tsx) — nunca corre
  // en servidor, `window` siempre existe cuando se monta.
  const [messages, setMessages] = useState<Message[]>(() => cargarHistorial());
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [offline, setOffline] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Sesión rastreada de forma reactiva (undefined = verificando, null = sin
  // sesión) en vez de consultarla solo al enviar — así el aviso de "inicia
  // sesión" aparece ANTES de que el ingeniero escriba y pierda su pregunta,
  // no como un error sorpresa después de intentar enviarla. Mismo patrón
  // que (app)/layout.tsx.
  const [session, setSession] = useState<Session | null | undefined>(undefined);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
    });
    return () => subscription.subscription.unsubscribe();
  }, []);

  // Persiste cada cambio de historial.
  useEffect(() => {
    guardarHistorial(messages);
  }, [messages]);

  // Detecta estado de conexión para avisar al ingeniero que está viendo
  // historial cacheado, no pudiendo hacer consultas nuevas.
  useEffect(() => {
    setOffline(!navigator.onLine);
    const onOnline = () => setOffline(false);
    const onOffline = () => setOffline(true);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;

    // session === undefined: todavía verificando (llamada async recién
    // disparada) — no se sabe aún si hay sesión, así que no se hace nada
    // en vez de redirigir de más a un usuario que sí está logueado pero
    // cuya verificación no ha resuelto todavía.
    if (session === undefined) return;

    // session === null: sin sesión confirmada. Se avisa con el banner
    // persistente de arriba, así que acá solo se redirige a /login en vez
    // de simular un envío que el backend rechazaría — no tiene sentido
    // meter la pregunta al historial para luego mostrar un error, cuando
    // ya se le avisó antes de escribir.
    if (session === null) {
      router.push("/login");
      return;
    }

    if (offline) {
      // Sin señal: no se intenta la consulta (fallaría igual), se avisa
      // directamente que está viendo historial cacheado.
      setMessages((m) => [
        ...m,
        { id: Date.now().toString(), role: "user", text },
        {
          id: Date.now().toString() + "_e",
          role: "error",
          text: "📡 Sin conexión — estás viendo tu historial guardado. Esta pregunta no se envió; vuelve a intentarla cuando recuperes señal.",
        },
      ]);
      setInput("");
      return;
    }

    const userMsg: Message = { id: Date.now().toString(), role: "user", text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await consultarDelegado(text);
      setMessages((m) => [
        ...m,
        { id: Date.now().toString() + "_r", role: "assistant", text: res.respuesta, meta: res },
      ]);
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "Error desconocido";
      setMessages((m) => [
        ...m,
        { id: Date.now().toString() + "_e", role: "error", text: `❌ ${errMsg}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const sinSesion = session === null;

  return (
    <div className="flex flex-col h-full">
      {/* Aviso de modo offline — el historial mostrado es el cacheado en localStorage */}
      {offline && (
        <div className="flex items-center gap-2 px-4 py-1.5 text-xs bg-yellow-950/40 border-b border-yellow-900/40 text-yellow-400">
          📡 Sin conexión — viendo historial guardado localmente
        </div>
      )}

      {/* Aviso de sesión requerida — visible desde el inicio, no solo tras
          intentar enviar una pregunta (ver comentario en send()). */}
      {sinSesion && !offline && (
        <div className="flex items-center gap-2 px-4 py-2 text-xs bg-brand-950/50 border-b border-brand-800/40 text-brand-200">
          <LogIn size={13} className="flex-shrink-0 text-brand-400" />
          <span className="flex-1 min-w-0">Inicia sesión para hacer consultas — es gratis.</span>
          <button
            onClick={() => router.push("/login")}
            className="flex-shrink-0 flex items-center gap-1 font-semibold text-ink-950 bg-brand-500 hover:bg-brand-400 rounded-lg px-2.5 py-1 transition"
          >
            Ingresar <ArrowRight size={12} />
          </button>
        </div>
      )}

      {/* Historial */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin scrollbar-thumb-concrete-700">
        {messages.map((m) => (
          <Bubble key={m.id} msg={m} />
        ))}

        {loading && (
          <div className="w-full">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-brand-400 mb-1.5">
              StructAI
            </p>
            <div className="rounded-xl bg-concrete-800/40 px-4 py-3">
              <Loader2 size={16} className="animate-spin text-brand-400" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Sugerencias agrupadas por dominio + guía de cómo preguntar (solo al inicio) */}
      {messages.length <= 1 && (
        <div className="px-4 pb-3 space-y-2.5">
          {GRUPOS_SUGERENCIAS.map((g) => (
            <div key={g.label}>
              <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-concrete-500 mb-1.5">
                {g.icon}
                {g.label}
              </p>
              <div className="flex flex-wrap gap-2">
                {g.preguntas.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-xs bg-concrete-800/60 hover:bg-brand-900/50 border border-concrete-700 hover:border-brand-600 text-concrete-300 hover:text-brand-200 px-3 py-1.5 rounded-full transition-all text-left"
                  >
                    {s.length > 60 ? s.slice(0, 60) + "…" : s}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <p className="flex items-start gap-1.5 text-[11px] text-concrete-500 pt-1">
            <Sparkles size={12} className="flex-shrink-0 mt-0.5 text-brand-500" />
            <span>
              <b className="text-concrete-400">Así preguntas mejor:</b> menciona la ciudad o región
              para precios, el título de la norma (ej. &quot;Título E&quot;) para respuestas puntuales,
              y el municipio si necesitas amenaza sísmica exacta.
            </span>
          </p>
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4">
        <div className="flex items-end gap-2 bg-concrete-800 border border-concrete-700 focus-within:border-brand-500 rounded-2xl px-4 py-3 transition">
          <TextareaAutosize
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            minRows={1}
            maxRows={5}
            placeholder={
              offline
                ? "Sin conexión — viendo historial guardado"
                : sinSesion
                ? "Inicia sesión para preguntar — es gratis"
                : "Pregunta como ingeniero civil... (Enter para enviar)"
            }
            className="flex-1 bg-transparent text-sm text-concrete-100 placeholder-concrete-500 resize-none outline-none leading-relaxed"
            disabled={loading}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            title={offline ? "Sin conexión — la consulta no se puede enviar ahora" : undefined}
            className="flex-shrink-0 w-8 h-8 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:bg-concrete-700 disabled:cursor-not-allowed flex items-center justify-center transition"
          >
            {loading ? (
              <Loader2 size={15} className="animate-spin text-concrete-400" />
            ) : (
              <Send size={15} className={input.trim() ? "text-ink-950" : "text-concrete-400"} />
            )}
          </button>
        </div>
        <p className="text-xs text-concrete-500 mt-1.5 text-center">
          NSR-10 · NTC · Seg. Industrial · Precios nacional (INVIAS) · Sismo en vivo (SGC)
        </p>
      </div>
    </div>
  );
}
