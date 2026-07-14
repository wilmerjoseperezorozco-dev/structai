"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import TextareaAutosize from "react-textarea-autosize";
import ReactMarkdown from "react-markdown";
import { Send, Loader2, BookOpen, ChevronDown, ChevronUp } from "lucide-react";
import clsx from "clsx";
import { askNorma, type AskResponse, type FuenteChunk } from "@/lib/api";

// ── Types ────────────────────────────────────────────────────────────────────

type Role = "user" | "assistant" | "error";

interface Message {
  id: string;
  role: Role;
  text: string;
  meta?: AskResponse;
}

// ── Sugerencias rápidas (preguntas tipo ingeniero civil) ──────────────────────

const SUGERENCIAS = [
  "¿Qué resistencia mínima de concreto exige NSR-10 para columnas sísmicas?",
  "¿Cuál es el recubrimiento mínimo para vigas expuestas a la intemperie?",
  "¿Qué norma regula el acero corrugado grado 60 en Colombia?",
  "¿Cuándo es obligatorio el uso de arnés en trabajos en altura?",
  "¿Qué esparcimiento máximo de estribos se permite en zona de confinamiento?",
];

// ── Fuentes colapsables ──────────────────────────────────────────────────────

function Fuentes({ fuentes, normas }: { fuentes: FuenteChunk[]; normas: string[] }) {
  const [open, setOpen] = useState(false);
  if (!fuentes.length) return null;
  return (
    <div className="mt-2 border border-brand-700/30 rounded-lg overflow-hidden text-xs">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-brand-900/30 text-brand-300 hover:bg-brand-900/50 transition"
      >
        <BookOpen size={13} />
        <span className="font-mono font-medium">
          {normas.slice(0, 3).join(" · ")}
          {normas.length > 3 && ` +${normas.length - 3} más`}
        </span>
        <span className="ml-auto text-brand-500">{fuentes.length} fuentes</span>
        {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {open && (
        <div className="divide-y divide-concrete-700/30">
          {fuentes.map((f, i) => (
            <div key={i} className="px-3 py-2 bg-concrete-900/60">
              <div className="flex justify-between items-center mb-1">
                <span className="font-mono font-semibold text-brand-300">{f.norma}</span>
                <span className="font-mono text-concrete-400">§ {f.seccion}</span>
                <span className="font-mono tabular-nums text-concrete-500">
                  {(f.score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-concrete-300 leading-relaxed">
                {f.contenido_preview}
                {f.contenido_preview.length >= 200 && "…"}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Burbuja de mensaje ───────────────────────────────────────────────────────

function Bubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  const isError = msg.role === "error";

  return (
    <div className={clsx("flex gap-3", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={clsx(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mt-1",
          isUser
            ? "bg-brand-600 text-white"
            : isError
            ? "bg-red-700 text-white"
            : "bg-concrete-700 text-brand-300"
        )}
      >
        {isUser ? "TÚ" : isError ? "!" : "IA"}
      </div>

      {/* Contenido */}
      <div className={clsx("flex-1 min-w-0", isUser && "items-end flex flex-col")}>
        <div
          className={clsx(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed max-w-[85%]",
            isUser
              ? "bg-brand-600 text-white rounded-tr-sm"
              : isError
              ? "bg-red-900/50 border border-red-700 text-red-300 rounded-tl-sm"
              : "bg-concrete-800 text-concrete-100 rounded-tl-sm"
          )}
        >
          {isUser ? (
            <p>{msg.text}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => (
                  <strong className="font-semibold text-brand-300">{children}</strong>
                ),
                code: ({ children }) => (
                  <code className="bg-concrete-900 px-1 py-0.5 rounded text-brand-200 font-mono text-xs">
                    {children}
                  </code>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside space-y-1 mb-2">{children}</ul>
                ),
                li: ({ children }) => <li className="text-concrete-200">{children}</li>,
              }}
            >
              {msg.text}
            </ReactMarkdown>
          )}
        </div>

        {/* Metadatos RAG */}
        {msg.meta && (
          <div className="mt-1 max-w-[85%] w-full">
            <Fuentes
              fuentes={msg.meta.fuentes}
              normas={msg.meta.normas_citadas}
            />
            <p className="text-xs text-concrete-500 mt-1 px-1">
              {msg.meta.chunks_usados} chunks · {msg.meta.latencia_ms} ms
            </p>
          </div>
        )}
      </div>
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
    "Hola, soy tu asistente de ingeniería civil. Puedo consultarte sobre **NTC**, **NSR-10**, normas de seguridad industrial y calcular APUs con precios Construdata 2026 Barranquilla.\n\n¿Qué necesitas saber hoy?",
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
      const res = await askNorma(text);
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

  return (
    <div className="flex flex-col h-full">
      {/* Aviso de modo offline — el historial mostrado es el cacheado en localStorage */}
      {offline && (
        <div className="flex items-center gap-2 px-4 py-1.5 text-xs bg-yellow-950/40 border-b border-yellow-900/40 text-yellow-400">
          📡 Sin conexión — viendo historial guardado localmente
        </div>
      )}

      {/* Historial */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin scrollbar-thumb-concrete-700">
        {messages.map((m) => (
          <Bubble key={m.id} msg={m} />
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-concrete-700 flex items-center justify-center text-xs font-bold text-brand-300 mt-1">
              IA
            </div>
            <div className="bg-concrete-800 rounded-2xl rounded-tl-sm px-4 py-3">
              <Loader2 size={16} className="animate-spin text-brand-400" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Sugerencias rápidas (solo al inicio) */}
      {messages.length <= 1 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {SUGERENCIAS.map((s, i) => (
            <button
              key={i}
              onClick={() => send(s)}
              className="text-xs bg-concrete-800 hover:bg-brand-900/60 border border-concrete-700 hover:border-brand-600 text-concrete-300 hover:text-brand-200 px-3 py-1.5 rounded-full transition-all"
            >
              {s.length > 55 ? s.slice(0, 55) + "…" : s}
            </button>
          ))}
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
              <Loader2 size={15} className="animate-spin text-white" />
            ) : (
              <Send size={15} className="text-white" />
            )}
          </button>
        </div>
        <p className="text-xs text-concrete-500 mt-1.5 text-center">
          NTC · NSR-10 · Seg. Industrial · Construdata 2026 Barranquilla
        </p>
      </div>
    </div>
  );
}
