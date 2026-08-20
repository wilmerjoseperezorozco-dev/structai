"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, ShieldCheck, ShieldAlert, ShieldQuestion, ShieldX, Loader2, RotateCcw } from "lucide-react";
import clsx from "clsx";
import {
  PREGUNTAS,
  calcularResultado,
  NIVEL_INFO,
  type RespuestaPregunta,
  type ResultadoDiagnostico,
} from "@/components/diagnostico/preguntas";
import { getAmenazaSismica, type AmenazaSismicaMunicipio } from "@/lib/api";

const NIVEL_ICONO: Record<ResultadoDiagnostico["nivel"], React.ElementType> = {
  bajo: ShieldCheck,
  medio: ShieldQuestion,
  alto: ShieldAlert,
  critico: ShieldX,
};

function BotonRespuesta({
  valor,
  seleccionado,
  onClick,
  children,
}: {
  valor: RespuestaPregunta;
  seleccionado: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex-1 text-xs font-medium rounded-lg px-2 py-2 border transition",
        seleccionado
          ? "bg-brand-600 border-brand-600 text-ink-950"
          : "bg-concrete-800 border-concrete-700 text-concrete-300 hover:border-concrete-500"
      )}
    >
      {children}
    </button>
  );
}

export default function DiagnosticoVulnerabilidad() {
  const [municipio, setMunicipio] = useState("");
  const [zonaSismica, setZonaSismica] = useState<AmenazaSismicaMunicipio | null>(null);
  const [buscandoZona, setBuscandoZona] = useState(false);
  const [respuestas, setRespuestas] = useState<Record<string, RespuestaPregunta>>({});
  const [mostrarResultado, setMostrarResultado] = useState(false);

  const totalRespondidas = Object.keys(respuestas).length;
  const faltan = PREGUNTAS.length - totalRespondidas;

  const categorias = useMemo(() => {
    const vistas = new Set<string>();
    const orden: string[] = [];
    for (const p of PREGUNTAS) {
      if (!vistas.has(p.categoria)) {
        vistas.add(p.categoria);
        orden.push(p.categoria);
      }
    }
    return orden;
  }, []);

  const responder = (id: string, valor: RespuestaPregunta) => {
    setRespuestas((prev) => ({ ...prev, [id]: valor }));
  };

  const handleBuscarZona = async () => {
    if (!municipio.trim()) return;
    setBuscandoZona(true);
    const r = await getAmenazaSismica(municipio.trim());
    setZonaSismica(r);
    setBuscandoZona(false);
  };

  const handleVerResultado = () => {
    setMostrarResultado(true);
  };

  const handleReiniciar = () => {
    setRespuestas({});
    setMostrarResultado(false);
  };

  const resultado = useMemo(() => calcularResultado(respuestas), [respuestas]);

  if (mostrarResultado) {
    const info = NIVEL_INFO[resultado.nivel];
    const Icono = NIVEL_ICONO[resultado.nivel];
    return (
      <div className="flex flex-col gap-3 h-full overflow-y-auto px-4 py-4 max-w-xl mx-auto w-full">
        <div className={clsx("rounded-2xl border p-4", info.bg, info.border)}>
          <div className="flex items-center gap-2 mb-2">
            <Icono size={22} className={info.color} />
            <h2 className={clsx("text-lg font-bold", info.color)}>{info.label}</h2>
          </div>
          <p className="text-sm text-concrete-200 leading-relaxed">{info.mensaje}</p>
          <p className="text-[11px] text-concrete-500 mt-2 tabular-nums">
            {resultado.puntaje} de {resultado.puntajeMaximo} señales de riesgo identificadas
            {resultado.huboFactorCritico ? " · incluye un factor crítico" : ""}
          </p>
        </div>

        {zonaSismica && (
          <div className="bg-concrete-900 border border-concrete-700 rounded-xl p-3">
            <p className="text-xs text-concrete-400">
              📍 {zonaSismica.municipio}, {zonaSismica.departamento}: zona de amenaza sísmica{" "}
              <span className="font-semibold text-concrete-200">{zonaSismica.zona ?? "no especificada"}</span>{" "}
              (Aa={zonaSismica.aa}, Av={zonaSismica.av}) — dato oficial del Servicio Geológico Colombiano.
            </p>
          </div>
        )}

        <div className="bg-concrete-900 border border-concrete-700 rounded-xl p-3">
          <p className="text-xs font-semibold text-concrete-300 uppercase tracking-wide mb-2">Qué hacer ahora</p>
          <ul className="flex flex-col gap-1.5">
            {info.acciones.map((a, i) => (
              <li key={i} className="text-xs text-concrete-300 flex gap-2">
                <span className="text-brand-400 flex-shrink-0">→</span>
                {a}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-concrete-950 border border-concrete-800 rounded-xl p-3 flex gap-2">
          <AlertTriangle size={14} className="text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-concrete-500 leading-relaxed">
            Este diagnóstico es un tamizaje orientativo, no un peritaje estructural. No reemplaza la
            evaluación presencial de un ingeniero civil matriculado. StructAI no se hace responsable por
            decisiones tomadas únicamente con base en este resultado.
          </p>
        </div>

        <button
          onClick={handleReiniciar}
          className="flex items-center justify-center gap-2 text-xs text-concrete-400 hover:text-concrete-200 border border-concrete-700 rounded-xl py-2.5 transition"
        >
          <RotateCcw size={13} /> Volver a empezar
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto px-4 py-4 max-w-xl mx-auto w-full">
      <div>
        <h2 className="text-lg font-bold text-white">Diagnóstico de vulnerabilidad sísmica</h2>
        <p className="text-xs text-concrete-400 mt-1 leading-relaxed">
          10 preguntas en lenguaje sencillo, sin necesidad de conocimientos técnicos. Pensado para
          autoconstrucción y vivienda informal — la vulnerabilidad más documentada en los daños del
          terremoto de agosto de 2026 en Colombia.
        </p>
      </div>

      <div className="bg-concrete-900 border border-concrete-700 rounded-xl p-3">
        <label className="flex flex-col gap-1">
          <span className="text-xs text-concrete-400">¿En qué municipio está la vivienda? (opcional)</span>
          <div className="flex gap-2">
            <input
              type="text"
              value={municipio}
              onChange={(e) => setMunicipio(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleBuscarZona()}
              placeholder="Ej. Barranquilla, Sincelejo, Tuchín…"
              className="flex-1 bg-concrete-800 border border-concrete-700 rounded-lg px-2 py-1.5 text-sm text-concrete-100 outline-none focus:border-brand-600"
            />
            <button
              onClick={handleBuscarZona}
              disabled={buscandoZona || !municipio.trim()}
              className="text-xs bg-concrete-800 hover:bg-concrete-700 disabled:opacity-50 border border-concrete-700 rounded-lg px-3 text-concrete-200 transition"
            >
              {buscandoZona ? <Loader2 size={13} className="animate-spin" /> : "Buscar"}
            </button>
          </div>
        </label>
        {zonaSismica && (
          <p className="text-[11px] text-concrete-400 mt-2">
            Zona de amenaza sísmica: <span className="text-concrete-200 font-medium">{zonaSismica.zona}</span>{" "}
            (Aa={zonaSismica.aa}, Av={zonaSismica.av}) — SGC.
          </p>
        )}
      </div>

      {categorias.map((cat) => (
        <div key={cat} className="flex flex-col gap-2">
          <p className="text-[11px] font-semibold text-concrete-500 uppercase tracking-wide px-1">{cat}</p>
          {PREGUNTAS.filter((p) => p.categoria === cat).map((p) => (
            <div key={p.id} className="bg-concrete-900 border border-concrete-700 rounded-xl p-3">
              <p className="text-sm text-concrete-100">{p.texto}</p>
              {p.ayuda && <p className="text-[11px] text-concrete-500 mt-1">{p.ayuda}</p>}
              <div className="flex gap-2 mt-2.5">
                <BotonRespuesta valor="si" seleccionado={respuestas[p.id] === "si"} onClick={() => responder(p.id, "si")}>
                  Sí
                </BotonRespuesta>
                <BotonRespuesta valor="no" seleccionado={respuestas[p.id] === "no"} onClick={() => responder(p.id, "no")}>
                  No
                </BotonRespuesta>
                <BotonRespuesta valor="no_se" seleccionado={respuestas[p.id] === "no_se"} onClick={() => responder(p.id, "no_se")}>
                  No sé
                </BotonRespuesta>
              </div>
            </div>
          ))}
        </div>
      ))}

      <button
        onClick={handleVerResultado}
        disabled={faltan > 0}
        className="bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-ink-950 text-sm font-medium rounded-xl py-3 transition sticky bottom-2"
      >
        {faltan > 0 ? `Responde ${faltan} pregunta${faltan === 1 ? "" : "s"} más` : "Ver resultado"}
      </button>
    </div>
  );
}
