"use client";

import { useEffect, useState } from "react";
import { Plug, Loader2, Copy, Check, ExternalLink, AlertCircle, CheckCircle2 } from "lucide-react";
import { supabase } from "@/lib/supabase";

// Servidor MCP de StructAI (issue #78) — expone /consultar (normativa +
// precios) como herramienta para clientes de IA (Claude Code hoy,
// claude.ai/Claude Desktop cuando el toggle de OAuth 2.1 de Supabase
// quede activo, ver apps/api/mcp_server.py para el detalle técnico
// completo). Esta página es el único lugar donde un usuario real puede
// encontrar y configurar esto — antes solo vivía en el código.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const MCP_URL = `${BASE}/mcp`;

type EstadoMCP = "verificando" | "disponible" | "no_disponible";

function CopyBlock({ texto }: { texto: string }) {
  const [copiado, setCopiado] = useState(false);

  const copiar = () => {
    navigator.clipboard.writeText(texto);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  };

  return (
    <div className="relative">
      <pre className="bg-ink-950 border border-concrete-700 rounded-xl p-3 pr-11 text-xs text-concrete-200 overflow-x-auto whitespace-pre-wrap break-all">
        {texto}
      </pre>
      <button
        onClick={copiar}
        aria-label="Copiar"
        className="absolute top-2 right-2 p-1.5 rounded-lg bg-concrete-800 hover:bg-concrete-700 text-concrete-300 hover:text-white transition"
      >
        {copiado ? <Check size={14} className="text-brand-400" /> : <Copy size={14} />}
      </button>
    </div>
  );
}

function Paso({ numero, titulo, children }: { numero: number; titulo: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <div className="w-6 h-6 rounded-full bg-brand-600 text-ink-950 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
        {numero}
      </div>
      <div className="min-w-0 flex-1 space-y-2">
        <p className="text-sm font-semibold text-white">{titulo}</p>
        {children}
      </div>
    </div>
  );
}

export default function IntegracionesPage() {
  const [estado, setEstado] = useState<EstadoMCP>("verificando");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;

    async function verificar() {
      const { data } = await supabase.auth.getSession();
      if (!cancelado) setToken(data.session?.access_token ?? null);

      try {
        // GET a /mcp confirma si ENABLE_MCP está activo en este backend —
        // sin esto, la página mostraría pasos que no funcionan todavía.
        const res = await fetch(MCP_URL, { method: "GET" });
        if (!cancelado) setEstado(res.status === 404 ? "no_disponible" : "disponible");
      } catch {
        if (!cancelado) setEstado("no_disponible");
      }
    }

    verificar();
    return () => {
      cancelado = true;
    };
  }, []);

  const comandoClaudeCode = token
    ? `claude mcp add --transport http structai ${MCP_URL} --header "Authorization: Bearer ${token}"`
    : `claude mcp add --transport http structai ${MCP_URL} --header "Authorization: Bearer <tu-token-de-sesión>"`;

  return (
    <div className="flex flex-col gap-6 px-4 py-6">
      <div className="flex items-center gap-3">
        <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center flex-shrink-0">
          <Plug size={26} className="text-ink-950" />
        </div>
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-white">Integraciones</h2>
          <p className="text-xs text-concrete-400">Usa StructAI desde tus propias herramientas de IA</p>
        </div>
      </div>

      <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-4 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-white">StructAI para IA (MCP)</h3>
            <p className="text-xs text-concrete-400 mt-1">
              Consulta NSR-10, NTC y precios de construcción directamente desde Claude, sin salir de tu
              editor o terminal — mismos datos y trazabilidad normativa que el chat web.
            </p>
          </div>
          {estado === "verificando" && <Loader2 size={16} className="text-concrete-500 animate-spin flex-shrink-0" />}
          {estado === "disponible" && (
            <span className="flex items-center gap-1 text-xs text-brand-400 flex-shrink-0">
              <CheckCircle2 size={14} /> Disponible
            </span>
          )}
          {estado === "no_disponible" && (
            <span className="flex items-center gap-1 text-xs text-concrete-500 flex-shrink-0">
              <AlertCircle size={14} /> Aún no disponible
            </span>
          )}
        </div>

        {estado === "no_disponible" && (
          <p className="text-xs text-concrete-500 bg-ink-950 border border-concrete-700 rounded-xl p-3">
            Esta función está construida y probada, pero todavía no se activó en este entorno. Si eres
            parte del equipo de StructAI, habilítala con <code className="text-concrete-300">ENABLE_MCP=true</code>.
          </p>
        )}

        <div className="space-y-4 pt-2 border-t border-concrete-700">
          <Paso numero={1} titulo="Con Claude Code (disponible hoy)">
            <p className="text-xs text-concrete-400">
              Copia y pega este comando en tu terminal. Usa el token de tu sesión actual de StructAI —
              no compartas este comando con nadie más, funciona como tu contraseña.
            </p>
            <CopyBlock texto={comandoClaudeCode} />
          </Paso>

          <Paso numero={2} titulo="Con claude.ai o Claude Desktop (próximamente)">
            <p className="text-xs text-concrete-400">
              El botón &quot;Add custom connector&quot; de claude.ai solo acepta conexión con inicio de
              sesión (OAuth), no un código para pegar. Estamos activando ese modo — cuando esté listo,
              vas a poder conectar StructAI con un clic usando tu misma cuenta, sin copiar nada.
            </p>
          </Paso>

          <Paso numero={3} titulo="Qué puede hacer hoy">
            <p className="text-xs text-concrete-400">
              Por ahora, un único permiso: <code className="text-concrete-300">consultar</code> — hacer
              preguntas de normativa o precios, de solo lectura. Nunca modifica tus proyectos ni tus
              datos.
            </p>
          </Paso>
        </div>
      </div>

      <a
        href="https://github.com/wilmerjoseperezorozco-dev/structai/issues/78"
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-2 w-full border border-concrete-700 hover:border-brand-600 text-concrete-400 hover:text-brand-400 text-xs font-medium py-2.5 rounded-xl transition"
      >
        Ver el detalle técnico completo <ExternalLink size={13} />
      </a>
    </div>
  );
}
