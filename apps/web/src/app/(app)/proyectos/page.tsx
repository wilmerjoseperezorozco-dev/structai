"use client";

import { useEffect, useState } from "react";
import { FolderOpen, Calculator, FileText, Loader2, AlertCircle } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { formatCOP } from "@/lib/api";

interface ApuCalculo {
  id: string;
  actividad_id: string;
  descripcion: string;
  precio_unitario: number;
  cantidad: number;
  proyecto_nombre: string | null;
  created_at: string;
}

interface PlanAnalysis {
  id: string;
  nombre_archivo: string;
  formato: string;
  presupuesto_total: number;
  cumplimiento_pct: number | null;
  proyecto_nombre: string | null;
  created_at: string;
}

export default function ProyectosPage() {
  const [apus, setApus] = useState<ApuCalculo[]>([]);
  const [planos, setPlanos] = useState<PlanAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const { data: session } = await supabase.auth.getSession();
      const userId = session.session?.user.id;
      if (!userId) return;

      const [apuRes, planRes] = await Promise.all([
        supabase
          .from("apu_calculations")
          .select("id, actividad_id, descripcion, precio_unitario, cantidad, proyecto_nombre, created_at")
          .eq("user_id", userId)
          .order("created_at", { ascending: false }),
        supabase
          .from("plan_analyses")
          .select("id, nombre_archivo, formato, presupuesto_total, cumplimiento_pct, proyecto_nombre, created_at")
          .eq("user_id", userId)
          .order("created_at", { ascending: false }),
      ]);

      if (cancelled) return;

      if (apuRes.error || planRes.error) {
        setError(apuRes.error?.message ?? planRes.error?.message ?? "Error cargando proyectos");
      } else {
        setApus(apuRes.data ?? []);
        setPlanos(planRes.data ?? []);
      }
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const vacio = !loading && !error && apus.length === 0 && planos.length === 0;

  return (
    <div className="flex flex-col gap-6 px-4 py-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FolderOpen size={20} className="text-green-400" /> Mis proyectos
        </h2>
        <p className="text-xs text-concrete-400 mt-0.5">APU guardados y análisis de planos, con trazabilidad completa</p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-10 gap-2 text-brand-400">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Cargando proyectos…</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 text-xs text-red-300 bg-red-900/30 border border-red-700 rounded-xl px-3 py-2">
          <AlertCircle size={14} /> {error}
        </div>
      )}

      {vacio && (
        <div className="text-center py-16 text-concrete-500 text-sm">
          Todavía no tienes APU calculados ni planos analizados.
          <br />
          Empieza desde <span className="text-brand-400">Calcular APU</span> o{" "}
          <span className="text-brand-400">Detección foto</span>.
        </div>
      )}

      {apus.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-brand-400 uppercase tracking-wide">APU calculados</p>
          {apus.map((a) => (
            <div key={a.id} className="bg-concrete-800 border border-concrete-700 rounded-xl p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="text-xs font-mono text-brand-300">{a.actividad_id}</p>
                  <p className="text-sm text-concrete-100 leading-snug">{a.descripcion}</p>
                  {a.proyecto_nombre && (
                    <p className="text-xs text-concrete-500 mt-0.5">{a.proyecto_nombre}</p>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold text-white tabular-nums">{formatCOP(a.precio_unitario)}</p>
                  <p className="text-xs text-concrete-500 tabular-nums">× {a.cantidad}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {planos.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-orange-400 uppercase tracking-wide">Planos analizados</p>
          {planos.map((p) => (
            <div key={p.id} className="bg-concrete-800 border border-concrete-700 rounded-xl p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex items-center gap-2">
                  <FileText size={16} className="text-concrete-500 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-concrete-100 leading-snug">{p.nombre_archivo}</p>
                    <p className="text-xs text-concrete-500 mt-0.5">
                      {p.formato}
                      {p.cumplimiento_pct != null && ` · Cumplimiento NSR-10: ${p.cumplimiento_pct}%`}
                    </p>
                  </div>
                </div>
                <p className="text-sm font-bold text-white tabular-nums flex-shrink-0">
                  {formatCOP(p.presupuesto_total)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
