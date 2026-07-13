"use client";

import { formatNum, humanLabel } from "@/lib/aquai-api";

type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

function BoolBadge({ value }: { value: boolean }) {
  return (
    <span
      className={
        value
          ? "text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-green-900/40 text-green-400"
          : "text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-red-900/40 text-red-400"
      }
    >
      {value ? "Cumple" : "No cumple"}
    </span>
  );
}

function ValueCell({ value }: { value: Json }) {
  if (typeof value === "boolean") return <BoolBadge value={value} />;
  if (typeof value === "number") {
    return <span className="text-concrete-100 tabular-nums font-mono text-xs">{formatNum(value)}</span>;
  }
  if (value === null || value === undefined) {
    return <span className="text-concrete-600 text-xs">—</span>;
  }
  return <span className="text-concrete-100 text-xs text-right">{String(value)}</span>;
}

function ListValue({ items }: { items: Json[] }) {
  if (items.length === 0) return <span className="text-concrete-600 text-xs">—</span>;
  if (items.every((it) => typeof it !== "object" || it === null)) {
    return (
      <ul className="text-xs text-concrete-300 space-y-0.5 text-right">
        {items.map((it, i) => (
          <li key={i}>{String(it)}</li>
        ))}
      </ul>
    );
  }
  return (
    <div className="space-y-2 w-full">
      {items.map((it, i) => (
        <div key={i} className="bg-concrete-800/60 rounded-lg p-2">
          <ResultView data={it as Record<string, Json>} nested />
        </div>
      ))}
    </div>
  );
}

/** Renderiza cualquier respuesta JSON del backend AquAI como filas etiqueta/valor. */
export default function ResultView({
  data,
  nested = false,
}: {
  data: Record<string, unknown>;
  nested?: boolean;
}) {
  const entries = Object.entries(data as Record<string, Json>);

  return (
    <div className={nested ? "space-y-1.5" : "space-y-1.5 text-sm"}>
      {entries.map(([key, value]) => {
        if (Array.isArray(value)) {
          return (
            <div key={key} className="flex flex-col gap-1 py-1 border-b border-concrete-800/60 last:border-0">
              <span className="text-concrete-400 text-xs">{humanLabel(key)}</span>
              <ListValue items={value} />
            </div>
          );
        }
        if (value !== null && typeof value === "object") {
          return (
            <div key={key} className="flex flex-col gap-1 py-1 border-b border-concrete-800/60 last:border-0">
              <span className="text-concrete-400 text-xs font-medium">{humanLabel(key)}</span>
              <div className="pl-2 border-l border-concrete-700">
                <ResultView data={value as Record<string, Json>} nested />
              </div>
            </div>
          );
        }
        return (
          <div key={key} className="flex justify-between items-center gap-3 py-1 border-b border-concrete-800/60 last:border-0">
            <span className="text-concrete-400 text-xs">{humanLabel(key)}</span>
            <ValueCell value={value} />
          </div>
        );
      })}
    </div>
  );
}
