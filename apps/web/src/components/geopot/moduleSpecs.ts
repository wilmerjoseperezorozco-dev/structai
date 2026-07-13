/**
 * GeoPot — especificación de módulos: sísmica NSR-10 + laboratorio (concreto/suelos/agregados)
 * Mismo enfoque data-driven que components/aquai/moduleSpecs.ts.
 */
import {
  consultarZonaSismica,
  analizarConcreto,
  clasificarUSCS,
  clasificarAASHTO,
  analizarProctor,
  analizarCBR,
  analizarGranulometria,
  verificarAgregadoGrueso,
  verificarAgregadoFino,
  disenarMezcla,
} from "@/lib/geopot-api";

export type FieldType = "number" | "text" | "select" | "date" | "pairs";

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldSpec {
  key: string;
  label: string;
  type: FieldType;
  options?: FieldOption[];
  default?: number | string;
  step?: number;
  required?: boolean;
  help?: string;
}

export interface ModuleSpec {
  id: string;
  label: string;
  grupo: "Sísmica" | "Concreto" | "Suelos" | "Agregados";
  descripcion: string;
  normaRef: string;
  fields: FieldSpec[];
  submit: (payload: Record<string, unknown>) => Promise<Record<string, unknown>>;
  transform?: (raw: Record<string, string>) => Record<string, unknown>;
}

const ZONA_SISMICA: FieldOption[] = [
  { value: "BAJA", label: "Baja" },
  { value: "INTERMEDIA", label: "Intermedia" },
  { value: "ALTA", label: "Alta" },
];

const TIPO_PROCTOR: FieldOption[] = [
  { value: "MODIFICADO", label: "Modificado (INV E-142)" },
  { value: "ESTANDAR", label: "Estándar (INV E-141)" },
];

const CONDICION_CBR: FieldOption[] = [
  { value: "SATURADO", label: "Saturado" },
  { value: "SIN SATURAR", label: "Sin saturar" },
];

const ORIGEN_AGREGADO: FieldOption[] = [
  { value: "Triturado", label: "Triturado" },
  { value: "Rodado", label: "Rodado" },
  { value: "Mixto", label: "Mixto" },
];

const USO_AGREGADO: FieldOption[] = [
  { value: "CONCRETO", label: "Concreto" },
  { value: "ASFALTO", label: "Asfalto" },
  { value: "BASE_GRANULAR", label: "Base granular" },
];

const IMPUREZAS: FieldOption[] = [
  { value: "CLARO", label: "Claro" },
  { value: "MÁS CLARO", label: "Más claro" },
  { value: "OSCURO", label: "Oscuro" },
];

/** Convierte texto multilínea "a,b" por línea en [[a,b], ...] */
function parsePairs(text: string): [number, number][] {
  return text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => {
      const [a, b] = l.split(",").map((v) => Number(v.trim()));
      return [a, b] as [number, number];
    })
    .filter(([a, b]) => Number.isFinite(a) && Number.isFinite(b));
}

export const GEOPOT_MODULES: ModuleSpec[] = [
  {
    id: "sismica",
    label: "Zona sísmica",
    grupo: "Sísmica",
    descripcion: "Clasificación sísmica NSR-10 por departamento: Aa, Av, Fa, Fv, zona y medidas constructivas mínimas.",
    normaRef: "NSR-10 Título A.2",
    submit: consultarZonaSismica,
    fields: [
      { key: "departamento", label: "Departamento o capital", type: "text", default: "Atlántico", help: "Ej. 'Atlántico' o 'Barranquilla' — no importan las tildes" },
    ],
  },
  {
    id: "concreto",
    label: "Ensayo de concreto",
    grupo: "Concreto",
    descripcion: "Informe de conformidad de cilindros a compresión y asentamiento contra fc de diseño y mínimo NSR-10.",
    normaRef: "NTC 673 · NTC 396 · ACI 318 / NSR-10",
    submit: analizarConcreto,
    fields: [
      { key: "proyecto", label: "Proyecto", type: "text", default: "" },
      { key: "elemento", label: "Elemento", type: "text", default: "" },
      { key: "fc_diseno_MPa", label: "f'c de diseño (MPa)", type: "number", default: 21 },
      { key: "zona_sismica", label: "Zona sísmica", type: "select", options: ZONA_SISMICA, default: "ALTA" },
      { key: "fecha_colada", label: "Fecha de colada", type: "date", default: "" },
      { key: "fecha_ensayo", label: "Fecha de ensayo", type: "date", default: "" },
      { key: "cil1_edad", label: "Cilindro 1 — edad (días)", type: "number", default: 28 },
      { key: "cil1_diametro", label: "Cilindro 1 — diámetro (mm)", type: "number", default: 152 },
      { key: "cil1_carga", label: "Cilindro 1 — carga a la falla (kN)", type: "number", required: false },
      { key: "cil2_edad", label: "Cilindro 2 — edad (días)", type: "number", default: 28 },
      { key: "cil2_diametro", label: "Cilindro 2 — diámetro (mm)", type: "number", default: 152 },
      { key: "cil2_carga", label: "Cilindro 2 — carga a la falla (kN)", type: "number", required: false },
      { key: "cil3_edad", label: "Cilindro 3 — edad (días)", type: "number", default: 28 },
      { key: "cil3_diametro", label: "Cilindro 3 — diámetro (mm)", type: "number", default: 152 },
      { key: "cil3_carga", label: "Cilindro 3 — carga a la falla (kN)", type: "number", required: false },
      { key: "slump_mm", label: "Asentamiento medido (mm)", type: "number", required: false },
      { key: "slump_temp", label: "Temperatura al momento del slump (°C)", type: "number", required: false, default: 28 },
    ],
    transform: (raw) => {
      const cilindros: Record<string, unknown>[] = [];
      for (const n of [1, 2, 3]) {
        const carga = raw[`cil${n}_carga`];
        if (!carga) continue;
        cilindros.push({
          id_cilindro: `CIL-0${n}`,
          edad_dias: Number(raw[`cil${n}_edad`]),
          diametro_mm: Number(raw[`cil${n}_diametro`]),
          carga_kN: Number(carga),
          fecha_colada: raw.fecha_colada,
          fecha_ensayo: raw.fecha_ensayo,
        });
      }
      const slumps: Record<string, unknown>[] = [];
      if (raw.slump_mm) {
        slumps.push({
          id_muestra: "S-01",
          slump_mm: Number(raw.slump_mm),
          temperatura_C: Number(raw.slump_temp || 28),
          hora_toma: "N/A",
        });
      }
      return {
        proyecto: raw.proyecto,
        elemento: raw.elemento,
        fc_diseno_MPa: Number(raw.fc_diseno_MPa),
        zona_sismica: raw.zona_sismica,
        cilindros,
        slumps,
      };
    },
  },
  {
    id: "uscs",
    label: "Clasificación USCS",
    grupo: "Suelos",
    descripcion: "Sistema Unificado de Clasificación de Suelos a partir de granulometría y límites de Atterberg.",
    normaRef: "ASTM D2487",
    submit: clasificarUSCS,
    fields: [
      { key: "pasa_200_pct", label: "% que pasa tamiz #200", type: "number", default: 65 },
      { key: "pasa_4_pct", label: "% que pasa tamiz #4", type: "number", default: 95 },
      { key: "ll", label: "Límite líquido LL (%)", type: "number", required: false },
      { key: "ip", label: "Índice de plasticidad IP (%)", type: "number", required: false },
      { key: "d10", label: "D10 (mm)", type: "number", required: false },
      { key: "d30", label: "D30 (mm)", type: "number", required: false },
      { key: "d60", label: "D60 (mm)", type: "number", required: false },
    ],
  },
  {
    id: "aashto",
    label: "Clasificación AASHTO",
    grupo: "Suelos",
    descripcion: "Clasificación de subrasante AASHTO M145 (grupo + índice de grupo).",
    normaRef: "AASHTO M145",
    submit: clasificarAASHTO,
    fields: [
      { key: "ll", label: "Límite líquido LL (%)", type: "number", default: 42 },
      { key: "ip", label: "Índice de plasticidad IP (%)", type: "number", default: 18 },
      { key: "pasa_200_pct", label: "% que pasa tamiz #200", type: "number", default: 65 },
    ],
  },
  {
    id: "proctor",
    label: "Proctor (compactación)",
    grupo: "Suelos",
    descripcion: "Humedad óptima y densidad máxima seca por ajuste cuadrático, más verificación de compactación de campo.",
    normaRef: "INV E-141 / E-142",
    submit: analizarProctor,
    fields: [
      { key: "id_muestra", label: "ID de muestra", type: "text", default: "M-01" },
      { key: "tipo", label: "Tipo de ensayo", type: "select", options: TIPO_PROCTOR, default: "MODIFICADO" },
      { key: "puntos", label: "Puntos (humedad_%, densidad_seca_g_cm3) — uno por línea", type: "pairs", default: "8,1.82\n10,1.93\n12,1.97\n14,1.94\n16,1.88" },
      { key: "densidad_campo_gcm3", label: "Densidad de campo medida (g/cm³)", type: "number", required: false },
      { key: "porcentaje_minimo", label: "% de compactación mínimo requerido", type: "number", default: 95 },
    ],
    transform: (raw) => ({
      id_muestra: raw.id_muestra,
      tipo: raw.tipo,
      puntos: parsePairs(raw.puntos || ""),
      densidad_campo_gcm3: raw.densidad_campo_gcm3 ? Number(raw.densidad_campo_gcm3) : undefined,
      porcentaje_minimo: Number(raw.porcentaje_minimo || 95),
    }),
  },
  {
    id: "cbr",
    label: "CBR de laboratorio",
    grupo: "Suelos",
    descripcion: "Relación de soporte californiano y clasificación de subrasante, con estimación referencial de espesor de pavimento.",
    normaRef: "INV E-148",
    submit: analizarCBR,
    fields: [
      { key: "id_muestra", label: "ID de muestra", type: "text", default: "CBR-01" },
      { key: "carga_254_kN", label: "Carga a 2.54 mm (kN)", type: "number", default: 5.2 },
      { key: "carga_508_kN", label: "Carga a 5.08 mm (kN)", type: "number", default: 7.8 },
      { key: "densidad_seca", label: "Densidad seca (g/cm³)", type: "number", default: 1.9 },
      { key: "humedad_pct", label: "Humedad (%)", type: "number", default: 11.5 },
      { key: "condicion", label: "Condición", type: "select", options: CONDICION_CBR, default: "SATURADO" },
      { key: "esal_millones", label: "ESAL de diseño (millones)", type: "number", required: false, help: "Si se provee, estima espesor de pavimento AASHTO 93" },
    ],
  },
  {
    id: "granulometria",
    label: "Granulometría",
    grupo: "Suelos",
    descripcion: "Análisis granulométrico por tamizado: D10/D30/D60, Cu, Cc, % pasa #200 y módulo de finura.",
    normaRef: "INV E-123 / NTC 77",
    submit: analizarGranulometria,
    fields: [
      { key: "id_muestra", label: "ID de muestra", type: "text", default: "GR-01" },
      { key: "tamices", label: "Tamices (abertura_mm, %_que_pasa) — uno por línea", type: "pairs", default: "9.5,100\n4.75,85\n2.36,60\n1.18,40\n0.6,25\n0.3,12\n0.15,5\n0.075,2" },
    ],
    transform: (raw) => ({
      id_muestra: raw.id_muestra,
      tamices: parsePairs(raw.tamices || ""),
    }),
  },
  {
    id: "agregado_grueso",
    label: "Agregado grueso",
    grupo: "Agregados",
    descripcion: "Densidad, absorción y verificación NTC 174 de grava/triturado según el uso previsto.",
    normaRef: "NTC 174 · NTC 237 · NTC 218",
    submit: verificarAgregadoGrueso,
    fields: [
      { key: "id_muestra", label: "ID de muestra", type: "text", default: "AG-01" },
      { key: "origen", label: "Origen", type: "select", options: ORIGEN_AGREGADO, default: "Triturado" },
      { key: "uso", label: "Uso previsto", type: "select", options: USO_AGREGADO, default: "CONCRETO" },
      { key: "masa_sss_g", label: "Masa SSS (g)", type: "number", default: 2000 },
      { key: "masa_seca_g", label: "Masa seca al horno (g)", type: "number", default: 1958 },
      { key: "masa_sumergida_g", label: "Masa sumergida (g)", type: "number", default: 1222 },
      { key: "perdida_LA_pct", label: "Desgaste Los Ángeles (%)", type: "number", required: false, default: 28.5 },
      { key: "particulas_planas_pct", label: "Partículas planas (%)", type: "number", required: false },
      { key: "particulas_alargadas_pct", label: "Partículas alargadas (%)", type: "number", required: false },
    ],
  },
  {
    id: "agregado_fino",
    label: "Agregado fino (arena)",
    grupo: "Agregados",
    descripcion: "Densidad SSS, absorción y módulo de finura de arena para concreto.",
    normaRef: "NTC 174 · NTC 237 · NTC 77",
    submit: verificarAgregadoFino,
    fields: [
      { key: "id_muestra", label: "ID de muestra", type: "text", default: "AF-01" },
      { key: "masa_sss_g", label: "Masa SSS (g)", type: "number", default: 500 },
      { key: "masa_seca_g", label: "Masa seca al horno (g)", type: "number", default: 487 },
      { key: "masa_frasco_agua", label: "Masa frasco + agua (g)", type: "number", default: 670 },
      { key: "masa_frasco_agua_muestra", label: "Masa frasco + agua + muestra (g)", type: "number", default: 984 },
      { key: "modulo_finura", label: "Módulo de finura", type: "number", default: 2.75 },
      { key: "impurezas_organicas", label: "Impurezas orgánicas (colorimetría)", type: "select", options: IMPUREZAS, default: "CLARO" },
    ],
  },
  {
    id: "mezcla",
    label: "Diseño de mezcla",
    grupo: "Agregados",
    descripcion: "Proporciones de mezcla de concreto por m³ (método ACI 211.1, referencial).",
    normaRef: "ACI 211.1",
    submit: disenarMezcla,
    fields: [
      { key: "fc_MPa", label: "f'c de diseño (MPa)", type: "number", default: 21 },
      { key: "zona_sismica", label: "Zona sísmica", type: "select", options: ZONA_SISMICA, default: "ALTA" },
      { key: "tamaño_max_agregado_mm", label: "Tamaño máximo de agregado (mm)", type: "number", default: 19 },
      { key: "asentamiento_mm", label: "Asentamiento objetivo (mm)", type: "number", default: 75 },
      { key: "densidad_fino", label: "Densidad agregado fino (kg/L)", type: "number", default: 2.65 },
      { key: "densidad_grueso", label: "Densidad agregado grueso (kg/L)", type: "number", default: 2.7 },
    ],
  },
];
