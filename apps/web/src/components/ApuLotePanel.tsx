"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { FileSpreadsheet, Download, Upload, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { descargarPlantillaAPU, calcularLoteAPU, descargarBlob } from "@/lib/api";
import { supabase } from "@/lib/supabase";

type Estado =
  | { fase: "idle" }
  | { fase: "descargando" }
  | { fase: "subiendo" }
  | { fase: "listo"; filename: string }
  | { fase: "error"; mensaje: string };

export default function ApuLotePanel() {
  const router = useRouter();
  const [estado, setEstado] = useState<Estado>({ fase: "idle" });
  const [needsAuth, setNeedsAuth] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const requireAuth = async (): Promise<boolean> => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      setNeedsAuth(true);
      return false;
    }
    setNeedsAuth(false);
    return true;
  };

  const handleDescargarPlantilla = async () => {
    if (!(await requireAuth())) return;
    setEstado({ fase: "descargando" });
    try {
      const blob = await descargarPlantillaAPU();
      descargarBlob(blob, "plantilla_apu_construdata.xlsx");
      setEstado({ fase: "idle" });
    } catch (e: unknown) {
      setEstado({ fase: "error", mensaje: e instanceof Error ? e.message : "Error descargando plantilla" });
    }
  };

  const handleArchivoSeleccionado = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // permite volver a subir el mismo archivo si se corrige y reintenta
    if (!file) return;
    if (!(await requireAuth())) return;

    setEstado({ fase: "subiendo" });
    try {
      const blob = await calcularLoteAPU(file);
      const nombreSalida = `presupuesto_${file.name.replace(/\.xlsx$/i, "")}.xlsx`;
      descargarBlob(blob, nombreSalida);
      setEstado({ fase: "listo", filename: nombreSalida });
    } catch (e: unknown) {
      setEstado({ fase: "error", mensaje: e instanceof Error ? e.message : "Error calculando el lote" });
    }
  };

  const cargando = estado.fase === "descargando" || estado.fase === "subiendo";

  return (
    <div className="bg-concrete-800 border border-concrete-700 rounded-xl p-4">
      <h2 className="text-sm font-semibold text-concrete-300 uppercase tracking-wide flex items-center gap-2 mb-1">
        <FileSpreadsheet size={14} /> APU por lote (Excel)
      </h2>
      <p className="text-xs text-concrete-500 mb-3">
        Calcule hasta 200 actividades a la vez — catálogo y/o geometría propia mezclados. Recibe de vuelta el presupuesto completo con costos, AIU y trazabilidad normativa.
      </p>

      {needsAuth && (
        <div className="flex items-center justify-between gap-3 text-xs text-brand-200 bg-brand-900/30 border border-brand-700 rounded-xl px-3 py-2 mb-3">
          <span>🔒 Necesitas iniciar sesión para usar el cálculo por lote.</span>
          <button
            onClick={() => router.push("/login")}
            className="flex-shrink-0 text-brand-300 hover:text-brand-100 font-semibold underline underline-offset-2"
          >
            Ingresar
          </button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-2">
        <button
          onClick={handleDescargarPlantilla}
          disabled={cargando}
          className="flex items-center justify-center gap-2 text-sm bg-concrete-700 hover:bg-concrete-600 disabled:opacity-50 disabled:cursor-not-allowed border border-concrete-600 text-concrete-100 rounded-lg px-3 py-2 transition"
        >
          {estado.fase === "descargando" ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Download size={14} />
          )}
          1. Descargar plantilla
        </button>

        <button
          onClick={() => inputRef.current?.click()}
          disabled={cargando}
          className="flex items-center justify-center gap-2 text-sm bg-brand-700/40 hover:bg-brand-700/70 disabled:opacity-50 disabled:cursor-not-allowed border border-brand-600/50 text-brand-200 rounded-lg px-3 py-2 transition"
        >
          {estado.fase === "subiendo" ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Upload size={14} />
          )}
          2. Subir plantilla llena
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx"
          className="hidden"
          onChange={handleArchivoSeleccionado}
        />
      </div>

      {estado.fase === "subiendo" && (
        <p className="text-xs text-brand-400 mt-2">Calculando cada fila (Monte Carlo por actividad) — puede tardar unos segundos según el número de filas…</p>
      )}

      {estado.fase === "listo" && (
        <div className="flex items-center gap-2 text-xs text-green-300 bg-green-900/20 border border-green-700/40 rounded-lg px-3 py-2 mt-3">
          <CheckCircle2 size={14} className="flex-shrink-0" />
          <span>Presupuesto calculado y descargado ({estado.filename}). Filas con error quedan resaltadas en rojo dentro del archivo, con el detalle en la columna &quot;error_detalle&quot;.</span>
        </div>
      )}

      {estado.fase === "error" && (
        <div className="flex items-center gap-2 text-xs text-red-300 bg-red-900/20 border border-red-700/40 rounded-lg px-3 py-2 mt-3">
          <AlertTriangle size={14} className="flex-shrink-0" />
          <span>{estado.mensaje}</span>
        </div>
      )}
    </div>
  );
}
