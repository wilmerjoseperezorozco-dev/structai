"use client";

import { useState, useRef, useCallback } from "react";
import { Camera, Upload, X, Loader2, Scan, AlertCircle } from "lucide-react";
import clsx from "clsx";
import {
  detectImage,
  calculateAPU,
  type DetectResponse,
  type DeteccionElemento,
  type APUDesglose,
  CLASE_LABEL,
  formatCOP,
} from "@/lib/api";

// ── Tarjeta de elemento detectado ────────────────────────────────────────────

function ElementoCard({
  el,
  onCalcular,
}: {
  el: DeteccionElemento;
  onCalcular: (id: string) => void;
}) {
  const confianzaColor =
    el.confianza > 0.8
      ? "text-green-400"
      : el.confianza > 0.6
      ? "text-yellow-400"
      : "text-orange-400";

  return (
    <div className="bg-concrete-800 border border-concrete-700 rounded-xl p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-concrete-100 text-sm">
            {CLASE_LABEL[el.clase] ?? el.clase}
          </p>
          {el.apu_sugerido_id && (
            <p className="text-xs text-concrete-400 mt-0.5">
              APU: <span className="font-mono text-brand-300">{el.apu_sugerido_id}</span>
            </p>
          )}
        </div>
        <span className={clsx("text-sm font-bold tabular-nums", confianzaColor)}>
          {(el.confianza * 100).toFixed(0)}%
        </span>
      </div>

      {el.apu_sugerido_id && (
        <button
          onClick={() => onCalcular(el.apu_sugerido_id!)}
          className="mt-2 w-full text-xs bg-brand-700/40 hover:bg-brand-700/70 border border-brand-600/50 text-brand-200 rounded-lg px-3 py-1.5 transition"
        >
          Calcular APU →
        </button>
      )}
    </div>
  );
}

// ── Panel APU inline (resultado tras detectar) ───────────────────────────────

function APUInline({ result }: { result: APUDesglose }) {
  return (
    <div className="mt-3 bg-concrete-900/80 border border-brand-700/40 rounded-xl p-3 text-xs">
      <p className="font-semibold text-brand-300 mb-2">{result.descripcion}</p>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-concrete-300">
        <span>Materiales</span>
        <span className="text-right tabular-nums">{formatCOP(result.costo_materiales)}</span>
        <span>Mano de obra</span>
        <span className="text-right tabular-nums">{formatCOP(result.costo_mano_obra)}</span>
        <span>Equipo</span>
        <span className="text-right tabular-nums">{formatCOP(result.costo_equipo)}</span>
        <span>AIU</span>
        <span className="text-right tabular-nums">{formatCOP(result.aiu)}</span>
      </div>
      <div className="border-t border-concrete-700 mt-2 pt-2 flex justify-between items-center">
        <span className="font-bold text-white">PU ({result.unidad})</span>
        <span className="font-bold text-brand-300 text-sm tabular-nums">
          {formatCOP(result.precio_unitario)}
        </span>
      </div>
      <p className="text-concrete-500 mt-1.5 font-mono text-[10px] break-all">
        UUID: {result.uuid_trazabilidad}
      </p>
    </div>
  );
}

// ── Componente principal ──────────────────────────────────────────────────────

export default function DetectUpload() {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectResponse | null>(null);
  const [apuResults, setApuResults] = useState<Record<string, APUDesglose>>({});
  const [loadingDetect, setLoadingDetect] = useState(false);
  const [loadingApu, setLoadingApu] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) {
      setError("Solo se aceptan imágenes JPG/PNG/WebP");
      return;
    }
    setFile(f);
    setResult(null);
    setApuResults({});
    setError(null);
    const url = URL.createObjectURL(f);
    setPreview(url);
  }, []);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const analyze = async () => {
    if (!file) return;
    setLoadingDetect(true);
    setError(null);
    try {
      const res = await detectImage(file);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error en detección");
    } finally {
      setLoadingDetect(false);
    }
  };

  const calcularAPU = async (id: string) => {
    setLoadingApu(id);
    try {
      const res = await calculateAPU(id, 1);
      setApuResults((prev) => ({ ...prev, [id]: res }));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error calculando APU");
    } finally {
      setLoadingApu(null);
    }
  };

  const reset = () => {
    setPreview(null);
    setFile(null);
    setResult(null);
    setApuResults({});
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  };

  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto px-4 py-4">
      <h2 className="text-sm font-semibold text-concrete-300 uppercase tracking-wide">
        Detección Estructural
      </h2>

      {/* Zona drop / preview */}
      {!preview ? (
        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-concrete-600 hover:border-brand-500 rounded-2xl p-8 flex flex-col items-center gap-4 cursor-pointer transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="w-14 h-14 rounded-full bg-concrete-800 flex items-center justify-center">
            <Scan size={28} className="text-brand-400" />
          </div>
          <div className="text-center">
            <p className="text-concrete-200 font-medium text-sm">
              Arrastra una foto o toca para subir
            </p>
            <p className="text-concrete-500 text-xs mt-1">
              Columnas · Vigas · Muros · Zapatas · Placas
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
              className="flex items-center gap-2 bg-concrete-800 hover:bg-concrete-700 border border-concrete-600 text-concrete-200 text-xs px-4 py-2 rounded-xl transition"
            >
              <Upload size={14} /> Galería
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); cameraInputRef.current?.click(); }}
              className="flex items-center gap-2 bg-brand-700/50 hover:bg-brand-700 border border-brand-600 text-brand-200 text-xs px-4 py-2 rounded-xl transition"
            >
              <Camera size={14} /> Cámara
            </button>
          </div>
        </div>
      ) : (
        <div className="relative rounded-2xl overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Imagen a analizar"
            className="w-full object-cover max-h-52 rounded-2xl"
          />
          <button
            onClick={reset}
            className="absolute top-2 right-2 w-7 h-7 rounded-full bg-concrete-900/80 hover:bg-red-800 flex items-center justify-center transition"
          >
            <X size={14} className="text-white" />
          </button>
        </div>
      )}

      {/* Inputs ocultos */}
      <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={onFileChange} />
      <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={onFileChange} />

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 bg-red-900/30 border border-red-700 rounded-xl px-3 py-2 text-xs text-red-300">
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      {/* Botón analizar */}
      {preview && !result && (
        <button
          onClick={analyze}
          disabled={loadingDetect}
          className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 disabled:bg-concrete-700 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-xl py-3 transition"
        >
          {loadingDetect ? (
            <><Loader2 size={16} className="animate-spin" /> Analizando con IA…</>
          ) : (
            <><Scan size={16} /> Detectar elementos</>
          )}
        </button>
      )}

      {/* Resultados detección */}
      {result && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-concrete-300 uppercase tracking-wide">
              {result.elementos_detectados.length} elemento
              {result.elementos_detectados.length !== 1 && "s"} detectado
              {result.elementos_detectados.length !== 1 && "s"}
            </p>
            <span className={clsx(
              "text-[10px] px-2 py-0.5 rounded-full font-mono",
              result.modo === "onnx"
                ? "bg-green-900/40 text-green-400 border border-green-700"
                : "bg-yellow-900/40 text-yellow-400 border border-yellow-700"
            )}>
              {result.modo === "onnx" ? "YOLO ONNX" : "STUB (dev)"}
            </span>
          </div>

          {result.elementos_detectados.length === 0 ? (
            <p className="text-concrete-400 text-sm text-center py-4">
              No se detectaron elementos estructurales reconocidos.
            </p>
          ) : (
            <div className="space-y-3">
              {result.elementos_detectados.map((el, i) => (
                <div key={i}>
                  <ElementoCard
                    el={el}
                    onCalcular={(id) => {
                      if (loadingApu === id) return;
                      calcularAPU(id);
                    }}
                  />
                  {loadingApu === el.apu_sugerido_id && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-brand-400 px-1">
                      <Loader2 size={12} className="animate-spin" /> Calculando APU…
                    </div>
                  )}
                  {el.apu_sugerido_id && apuResults[el.apu_sugerido_id] && (
                    <APUInline result={apuResults[el.apu_sugerido_id]} />
                  )}
                </div>
              ))}
            </div>
          )}

          <p className="text-xs text-concrete-500 mt-2 text-right">
            {result.latencia_ms} ms · {result.modelo_version}
          </p>

          <button
            onClick={reset}
            className="mt-3 w-full text-xs text-concrete-400 hover:text-concrete-200 border border-concrete-700 hover:border-concrete-500 rounded-xl py-2 transition"
          >
            Analizar otra foto
          </button>
        </div>
      )}
    </div>
  );
}
