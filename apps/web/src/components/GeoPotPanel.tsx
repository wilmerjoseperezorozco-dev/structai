"use client";

import { useMemo, useState } from "react";
import { Mountain, Loader2, Save, Check, ChevronDown, ChevronUp } from "lucide-react";
import clsx from "clsx";
import { GEOPOT_MODULES, type ModuleSpec, type FieldSpec } from "@/components/geopot/moduleSpecs";
import ResultView from "@/components/aquai/ResultView";
import { supabase } from "@/lib/supabase";

const GRUPO_COLOR: Record<ModuleSpec["grupo"], string> = {
  Sísmica: "border-red-600 text-red-300 bg-red-950/30",
  Concreto: "border-blue-600 text-blue-300 bg-blue-950/30",
  Suelos: "border-amber-600 text-amber-300 bg-amber-950/30",
  Agregados: "border-green-600 text-green-300 bg-green-950/30",
};

function defaultsFor(fields: FieldSpec[]): Record<string, string> {
  return fields.reduce<Record<string, string>>((acc, f) => {
    acc[f.key] = f.default !== undefined ? String(f.default) : "";
    return acc;
  }, {});
}

function buildPayload(mod: ModuleSpec, raw: Record<string, string>): Record<string, unknown> {
  const base = mod.transform ? mod.transform(raw) : raw;
  const payload: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(base)) {
    const field = mod.fields.find((f) => f.key === key);
    if (typeof value !== "string") {
      payload[key] = value; // ya transformado (ej. cilindros, puntos, tamices)
      continue;
    }
    if (value === "") {
      if (field?.required === false) continue;
      payload[key] = field?.type === "number" ? undefined : value;
      continue;
    }
    payload[key] = field?.type === "number" ? Number(value) : value;
  }
  return payload;
}

function Field({
  field,
  value,
  onChange,
}: {
  field: FieldSpec;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-concrete-400">
        {field.label}
        {field.required === false && <span className="text-concrete-600"> (opcional)</span>}
      </span>
      {field.type === "select" ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="bg-concrete-800 border border-concrete-700 rounded-lg px-2 py-1.5 text-sm text-concrete-100 outline-none focus:border-brand-600"
        >
          {field.options?.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : field.type === "pairs" ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={5}
          className="bg-concrete-800 border border-concrete-700 rounded-lg px-2 py-1.5 text-xs font-mono text-concrete-100 outline-none focus:border-brand-600 resize-y"
        />
      ) : (
        <input
          type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"}
          step={field.type === "number" ? "any" : undefined}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.required === false ? "—" : undefined}
          className="bg-concrete-800 border border-concrete-700 rounded-lg px-2 py-1.5 text-sm text-concrete-100 outline-none focus:border-brand-600 tabular-nums"
        />
      )}
      {field.help && <span className="text-[10px] text-concrete-600">{field.help}</span>}
    </label>
  );
}

export default function GeoPotPanel() {
  const [activeId, setActiveId] = useState(GEOPOT_MODULES[0].id);
  const active = useMemo(() => GEOPOT_MODULES.find((m) => m.id === activeId)!, [activeId]);

  const [formState, setFormState] = useState<Record<string, Record<string, string>>>(() =>
    GEOPOT_MODULES.reduce<Record<string, Record<string, string>>>((acc, m) => {
      acc[m.id] = defaultsFor(m.fields);
      return acc;
    }, {})
  );
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAllModules, setShowAllModules] = useState(false);

  const [nombreProyecto, setNombreProyecto] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const values = formState[activeId];

  const handleField = (key: string, v: string) => {
    setFormState((prev) => ({ ...prev, [activeId]: { ...prev[activeId], [key]: v } }));
  };

  const handleSelectModule = (id: string) => {
    setActiveId(id);
    setResult(null);
    setError(null);
    setSaved(false);
    setSaveError(null);
  };

  const handleCalcular = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSaved(false);
    try {
      const payload = buildPayload(active, values);
      const res = await active.submit(payload);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error calculando el módulo");
    } finally {
      setLoading(false);
    }
  };

  const handleGuardar = async () => {
    if (!result) return;
    setSaving(true);
    setSaveError(null);
    try {
      const { data: session } = await supabase.auth.getSession();
      const userId = session.session?.user.id;
      if (!userId) throw new Error("Debes iniciar sesión para guardar en Proyectos.");

      const { error: insertError } = await supabase.from("geopot_proyectos").insert({
        user_id: userId,
        nombre_proyecto: nombreProyecto || `GeoPot · ${active.label}`,
        entradas: buildPayload(active, values),
        resultados: result,
        notas: { modulo: active.id },
      });
      if (insertError) throw new Error(insertError.message);
      setSaved(true);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Error guardando el proyecto");
    } finally {
      setSaving(false);
    }
  };

  const visibleModules = showAllModules ? GEOPOT_MODULES : GEOPOT_MODULES.slice(0, 6);

  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto px-4 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-concrete-300 uppercase tracking-wide flex items-center gap-2">
          <Mountain size={14} /> GeoPot · NSR-10 Sísmica &amp; Laboratorio
        </h2>
        <span className="text-xs text-concrete-500">Colombia</span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {visibleModules.map((m) => (
          <button
            key={m.id}
            onClick={() => handleSelectModule(m.id)}
            className={clsx(
              "text-xs px-2.5 py-1 rounded-full border transition",
              activeId === m.id ? GRUPO_COLOR[m.grupo] : "border-concrete-700 text-concrete-400 hover:border-concrete-500"
            )}
          >
            {m.label}
          </button>
        ))}
        {GEOPOT_MODULES.length > 6 && (
          <button
            onClick={() => setShowAllModules((v) => !v)}
            className="text-xs px-2.5 py-1 rounded-full border border-concrete-700 text-concrete-500 hover:text-concrete-300 flex items-center gap-1"
          >
            {showAllModules ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            {showAllModules ? "Ver menos" : "Ver todos"}
          </button>
        )}
      </div>

      <div className={clsx("rounded-xl border px-3 py-2", GRUPO_COLOR[active.grupo])}>
        <p className="text-xs font-medium">{active.descripcion}</p>
        <p className="text-[10px] mt-1 opacity-80">📐 {active.normaRef}</p>
      </div>

      <div className="grid grid-cols-2 gap-2.5 bg-concrete-900 border border-concrete-700 rounded-xl p-3">
        {active.fields.map((f) => (
          <div key={f.key} className={f.type === "pairs" || (f.type === "select" && f.options && f.options.length > 3) ? "col-span-2" : ""}>
            <Field field={f} value={values[f.key] ?? ""} onChange={(v) => handleField(f.key, v)} />
          </div>
        ))}
      </div>

      <button
        onClick={handleCalcular}
        disabled={loading}
        className="bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl py-2.5 flex items-center justify-center gap-2 transition"
      >
        {loading ? <Loader2 size={16} className="animate-spin" /> : null}
        {loading ? "Calculando…" : "Calcular"}
      </button>

      {error && (
        <div className="text-xs text-red-300 bg-red-900/30 border border-red-700 rounded-xl px-3 py-2">{error}</div>
      )}

      {result && !loading && (
        <div className="bg-concrete-900 border border-brand-700/50 rounded-2xl p-4">
          <p className="font-bold text-white text-sm mb-3">Resultado — {active.label}</p>
          <ResultView data={result} />

          <div className="mt-4 border-t border-concrete-800 pt-3 flex flex-col gap-2">
            <div className="flex gap-2">
              <input
                type="text"
                value={nombreProyecto}
                onChange={(e) => setNombreProyecto(e.target.value)}
                placeholder={`GeoPot · ${active.label}`}
                className="flex-1 bg-concrete-800 border border-concrete-700 rounded-lg px-2 py-1.5 text-xs text-concrete-100 outline-none focus:border-brand-600"
              />
              <button
                onClick={handleGuardar}
                disabled={saving}
                className="flex items-center gap-1.5 text-xs bg-concrete-800 hover:bg-concrete-700 disabled:opacity-50 border border-concrete-700 rounded-lg px-3 py-1.5 text-concrete-200 transition"
              >
                {saving ? <Loader2 size={12} className="animate-spin" /> : saved ? <Check size={12} className="text-green-400" /> : <Save size={12} />}
                {saved ? "Guardado" : "Guardar en Proyectos"}
              </button>
            </div>
            {saveError && <p className="text-[10px] text-red-400">{saveError}</p>}
          </div>
        </div>
      )}
    </div>
  );
}
