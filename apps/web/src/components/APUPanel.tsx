"use client";

import { useState, useEffect } from "react";
import { Calculator, ChevronDown, ChevronUp, Copy, Check, Loader2 } from "lucide-react";
import clsx from "clsx";
import { listAPU, calculateAPU, type APUItem, type APUDesglose, formatCOP } from "@/lib/api";

// ── Tarjeta catálogo ──────────────────────────────────────────────────────────

function CatalogCard({
  item,
  onSelect,
}: {
  item: APUItem;
  onSelect: (id: string) => void;
}) {
  const incColor =
    item.incertidumbre_pct < 5
      ? "text-green-400"
      : item.incertidumbre_pct < 10
      ? "text-yellow-400"
      : "text-orange-400";

  return (
    <button
      onClick={() => onSelect(item.id)}
      className="w-full text-left bg-concrete-800 hover:bg-concrete-700 border border-concrete-700 hover:border-brand-600 rounded-xl p-3 transition group"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-mono text-brand-300 mb-0.5">{item.id}</p>
          <p className="text-sm font-medium text-concrete-100 leading-snug">
            {item.descripcion}
          </p>
          <p className="text-xs text-concrete-500 mt-1">
            {item.capitulo} · {item.unidad}
          </p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="text-sm font-bold text-white tabular-nums">
            {formatCOP(item.precio_unitario)}
          </p>
          <p className={clsx("text-xs font-medium tabular-nums", incColor)}>
            ±{item.incertidumbre_pct}%
          </p>
        </div>
      </div>
    </button>
  );
}

// ── Desglose completo ─────────────────────────────────────────────────────────

function DesglosePanel({ d, onClose }: { d: APUDesglose; onClose: () => void }) {
  const [copied, setCopied] = useState(false);

  const copyUUID = () => {
    navigator.clipboard.writeText(d.uuid_trazabilidad);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const rows = [
    { label: "Materiales",    value: d.costo_materiales, pct: (d.costo_materiales / d.costo_directo) * 100 },
    { label: "Mano de obra",  value: d.costo_mano_obra,  pct: (d.costo_mano_obra  / d.costo_directo) * 100 },
    { label: "Equipo",        value: d.costo_equipo,     pct: (d.costo_equipo     / d.costo_directo) * 100 },
  ];

  return (
    <div className="bg-concrete-900 border border-brand-700/50 rounded-2xl p-4 mt-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-4">
        <div>
          <p className="font-bold text-white text-sm leading-snug">{d.descripcion}</p>
          <p className="text-xs text-concrete-400 mt-0.5">
            {d.actividad_id} · {d.unidad} · {d.capitulo}
          </p>
          {d.norma_ref && (
            <p className="text-xs font-mono text-brand-400 mt-0.5">📐 {d.norma_ref}</p>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-xs text-concrete-500 hover:text-concrete-300 whitespace-nowrap"
        >
          Cerrar
        </button>
      </div>

      {/* Barra visual de composición */}
      <div className="h-2 rounded-full overflow-hidden flex gap-0.5 mb-3">
        <div className="bg-blue-500  rounded-full" style={{ width: `${rows[0].pct}%` }} />
        <div className="bg-green-500 rounded-full" style={{ width: `${rows[1].pct}%` }} />
        <div className="bg-orange-500 rounded-full" style={{ width: `${rows[2].pct}%` }} />
      </div>
      <div className="flex gap-3 text-[10px] text-concrete-400 mb-4">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500 inline-block" /> Mat.</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 inline-block" /> MO</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500 inline-block" /> Equipo</span>
      </div>

      {/* Tabla desglose */}
      <div className="space-y-1.5 text-sm">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between items-center">
            <span className="text-concrete-400">{r.label}</span>
            <div className="flex items-center gap-3">
              <span className="text-concrete-500 text-xs">{r.pct.toFixed(1)}%</span>
              <span className="text-concrete-200 tabular-nums font-mono text-xs">
                {formatCOP(r.value)}
              </span>
            </div>
          </div>
        ))}

        <div className="border-t border-concrete-700 pt-1.5 flex justify-between items-center">
          <span className="text-concrete-400">Costo Directo</span>
          <span className="text-concrete-200 tabular-nums font-mono text-xs">
            {formatCOP(d.costo_directo)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-concrete-400">AIU (Admin+Impr+Util)</span>
          <span className="text-concrete-200 tabular-nums font-mono text-xs">
            {formatCOP(d.aiu)}
          </span>
        </div>

        <div className="border-t border-brand-700/50 pt-2 flex justify-between items-center">
          <span className="font-bold text-white">Precio Unitario</span>
          <span className="font-bold text-brand-300 text-base tabular-nums">
            {formatCOP(d.precio_unitario)}
          </span>
        </div>
      </div>

      {/* IC90 Monte Carlo */}
      <div className="mt-3 bg-concrete-800/60 rounded-xl px-3 py-2 text-xs">
        <p className="text-concrete-400 font-medium mb-1">
          Intervalo de confianza 90% (Monte Carlo N=5000)
        </p>
        <div className="flex justify-between text-concrete-300 tabular-nums font-mono">
          <span>P5: {formatCOP(d.pu_p05)}</span>
          <span>P95: {formatCOP(d.pu_p95)}</span>
          <span>σ: {formatCOP(d.pu_std)}</span>
        </div>
      </div>

      {/* Trazabilidad UUID */}
      <div className="mt-3 bg-concrete-800/40 rounded-xl px-3 py-2">
        <div className="flex items-center justify-between">
          <p className="text-[10px] text-concrete-500 font-medium uppercase tracking-wide">
            Trazabilidad
          </p>
          <button
            onClick={copyUUID}
            className="flex items-center gap-1 text-[10px] text-concrete-400 hover:text-brand-300 transition"
          >
            {copied ? <Check size={10} className="text-green-400" /> : <Copy size={10} />}
            {copied ? "Copiado" : "Copiar"}
          </button>
        </div>
        <p className="text-[10px] font-mono text-concrete-400 break-all mt-0.5">
          {d.uuid_trazabilidad}
        </p>
        <p className="text-[10px] font-mono tabular-nums text-concrete-600 mt-0.5">
          {new Date(d.timestamp).toLocaleString("es-CO")}
        </p>
      </div>
    </div>
  );
}

// ── Panel principal ───────────────────────────────────────────────────────────

export default function APUPanel() {
  const [items, setItems] = useState<APUItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [desglose, setDesglose] = useState<APUDesglose | null>(null);
  const [loadingCalc, setLoadingCalc] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [cantidad, setCantidad] = useState(1);

  useEffect(() => {
    listAPU()
      .then(setItems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = async (id: string) => {
    if (selected === id) {
      setSelected(null);
      setDesglose(null);
      return;
    }
    setSelected(id);
    setDesglose(null);
    setLoadingCalc(true);
    try {
      const res = await calculateAPU(id, cantidad);
      setDesglose(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoadingCalc(false);
    }
  };

  // Agrupar por capítulo
  const byChapter = items.reduce<Record<string, APUItem[]>>((acc, item) => {
    const cap = item.capitulo || "Otros";
    if (!acc[cap]) acc[cap] = [];
    acc[cap].push(item);
    return acc;
  }, {});

  const chapters = Object.keys(byChapter);
  const visibleChapters = showAll ? chapters : chapters.slice(0, 3);

  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto px-4 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-concrete-300 uppercase tracking-wide flex items-center gap-2">
          <Calculator size={14} /> Catálogo APU
        </h2>
        <span className="text-xs text-concrete-500">Construdata 2026 · Barranquilla</span>
      </div>

      {/* Cantidad multiplicador */}
      <div className="flex items-center gap-3 bg-concrete-800 border border-concrete-700 rounded-xl px-3 py-2">
        <span className="text-xs text-concrete-400">Cantidad:</span>
        <input
          type="number"
          min={0.01}
          step={0.5}
          value={cantidad}
          onChange={(e) => setCantidad(Math.max(0.01, Number(e.target.value)))}
          className="w-20 bg-transparent text-sm text-white tabular-nums outline-none"
        />
        <span className="text-xs text-concrete-500 ml-auto">
          (multiplica Mat + MO + Equipo)
        </span>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-10 gap-2 text-brand-400">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Cargando catálogo…</span>
        </div>
      )}

      {error && (
        <div className="text-xs text-red-300 bg-red-900/30 border border-red-700 rounded-xl px-3 py-2">
          {error}
        </div>
      )}

      {/* Catálogo por capítulos */}
      {!loading && !error && (
        <>
          {visibleChapters.map((cap) => (
            <div key={cap}>
              <p className="text-xs font-semibold text-brand-400 uppercase tracking-wide mb-2">
                {cap}
              </p>
              <div className="space-y-2">
                {byChapter[cap].map((item) => (
                  <div key={item.id}>
                    <CatalogCard item={item} onSelect={handleSelect} />
                    {selected === item.id && (
                      <>
                        {loadingCalc && (
                          <div className="flex items-center gap-2 text-xs text-brand-400 px-2 mt-2">
                            <Loader2 size={12} className="animate-spin" />
                            Calculando con Monte Carlo…
                          </div>
                        )}
                        {desglose && !loadingCalc && (
                          <DesglosePanel
                            d={desglose}
                            onClose={() => { setSelected(null); setDesglose(null); }}
                          />
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {chapters.length > 3 && (
            <button
              onClick={() => setShowAll((v) => !v)}
              className="flex items-center justify-center gap-2 text-xs text-concrete-400 hover:text-brand-300 border border-concrete-700 hover:border-brand-600 rounded-xl py-2 transition"
            >
              {showAll ? (
                <><ChevronUp size={13} /> Ver menos</>
              ) : (
                <><ChevronDown size={13} /> Ver {chapters.length - 3} capítulos más</>
              )}
            </button>
          )}
        </>
      )}
    </div>
  );
}
