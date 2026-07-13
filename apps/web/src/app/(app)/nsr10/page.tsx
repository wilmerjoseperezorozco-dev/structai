"use client";

import { useState } from "react";
import { Search, BookOpen, ChevronRight } from "lucide-react";
import { TITULOS_NSR10, type TituloNSR } from "@/lib/nsr10";
import clsx from "clsx";

const COLOR_MAP: Record<string, string> = {
  brand:  "bg-brand-900/40 border-brand-700/50 text-brand-300",
  orange: "bg-orange-900/40 border-orange-700/50 text-orange-300",
  slate:  "bg-slate-800/60 border-slate-600/50 text-slate-300",
  amber:  "bg-amber-900/40 border-amber-700/50 text-amber-300",
  green:  "bg-green-900/40 border-green-700/50 text-green-300",
  cyan:   "bg-cyan-900/40 border-cyan-700/50 text-cyan-300",
  yellow: "bg-yellow-900/40 border-yellow-700/50 text-yellow-300",
  brown:  "bg-orange-950/60 border-orange-800/50 text-orange-200",
  purple: "bg-purple-900/40 border-purple-700/50 text-purple-300",
  red:    "bg-red-900/40 border-red-700/50 text-red-300",
  teal:   "bg-teal-900/40 border-teal-700/50 text-teal-300",
};

const LETRA_BG: Record<string, string> = {
  brand:  "bg-brand-600",
  orange: "bg-orange-600",
  slate:  "bg-slate-600",
  amber:  "bg-amber-600",
  green:  "bg-green-700",
  cyan:   "bg-cyan-700",
  yellow: "bg-yellow-600",
  brown:  "bg-orange-800",
  purple: "bg-purple-700",
  red:    "bg-red-700",
  teal:   "bg-teal-700",
};

function TituloCard({ titulo, expanded, onToggle }: {
  titulo: TituloNSR;
  expanded: boolean;
  onToggle: () => void;
}) {
  const cc = COLOR_MAP[titulo.color] ?? COLOR_MAP.brand;
  const lb = LETRA_BG[titulo.color] ?? "bg-brand-600";

  return (
    <div className={clsx("border rounded-2xl overflow-hidden transition-all", cc)}>
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-4 text-left"
      >
        <div className={clsx("w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0", lb)}>
          <span className="text-white font-bold text-lg leading-none">{titulo.letra}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white leading-snug">{titulo.nombre}</p>
          <p className="text-xs text-concrete-400 mt-0.5 line-clamp-1">{titulo.descripcion}</p>
        </div>
        <ChevronRight
          size={16}
          className={clsx("text-concrete-500 flex-shrink-0 transition-transform", expanded && "rotate-90")}
        />
      </button>

      {expanded && (
        <div className="border-t border-current/20 px-4 pb-3 pt-2 space-y-1.5">
          {titulo.capitulos.map((cap) => (
            <button
              key={cap.id}
              className="w-full flex items-center justify-between text-left px-3 py-2 rounded-xl bg-concrete-900/60 hover:bg-concrete-800 transition"
            >
              <div>
                <span className="text-xs font-mono text-concrete-400 mr-2">{cap.codigo}</span>
                <span className="text-sm text-concrete-200">{cap.nombre}</span>
              </div>
              <span className="text-xs text-concrete-500 flex-shrink-0 ml-2">
                {cap.articulos_count} arts.
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function NSR10Page() {
  const [query, setQuery] = useState("");
  const [expandido, setExpandido] = useState<string | null>(null);

  const filtrados = query.trim()
    ? TITULOS_NSR10.filter((t) =>
        t.nombre.toLowerCase().includes(query.toLowerCase()) ||
        t.descripcion.toLowerCase().includes(query.toLowerCase()) ||
        t.capitulos.some((c) => c.nombre.toLowerCase().includes(query.toLowerCase()))
      )
    : TITULOS_NSR10;

  return (
    <div className="flex flex-col h-full">
      {/* Buscador sticky */}
      <div className="sticky top-0 z-10 bg-concrete-900 px-4 pt-4 pb-3 border-b border-concrete-800">
        <div className="flex items-center gap-2 bg-concrete-800 border border-concrete-700 rounded-xl px-3 py-2.5">
          <Search size={15} className="text-concrete-500 flex-shrink-0" />
          <input
            type="search"
            placeholder="Buscar título, capítulo o artículo NSR-10…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-sm text-white placeholder:text-concrete-500 outline-none"
          />
        </div>
        <div className="flex items-center gap-2 mt-2">
          <BookOpen size={11} className="text-concrete-500" />
          <span className="text-xs text-concrete-500">
            NSR-10 · {TITULOS_NSR10.length} títulos · Reglamento Sismo Resistente Colombia
          </span>
        </div>
      </div>

      {/* Lista de títulos */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {filtrados.length === 0 && (
          <div className="text-center py-10 text-concrete-500 text-sm">
            No se encontraron resultados para "{query}"
          </div>
        )}
        {filtrados.map((titulo) => (
          <TituloCard
            key={titulo.id}
            titulo={titulo}
            expanded={expandido === titulo.id}
            onToggle={() => setExpandido(expandido === titulo.id ? null : titulo.id)}
          />
        ))}
      </div>
    </div>
  );
}
