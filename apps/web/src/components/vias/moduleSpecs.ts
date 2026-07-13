/**
 * Vías — especificación de módulos: diseño geométrico, pavimentos, mantenimiento,
 * topografía y verificación de materiales NTC (15 normas).
 * Mismo enfoque data-driven que components/geopot/moduleSpecs.ts.
 */
import {
  validarDisenoGeometrico,
  disenarPavimento,
  diagnosticarMantenimiento,
  verificarCierreNivelacion,
  verificarNTC2017,
  verificarNTC4342,
  verificarNTC121,
  verificarNTC1299,
  verificarNTC1362,
  verificarNTC3459,
  verificarNTC3493,
  verificarNTC3502,
  verificarNTC3760,
  verificarNTC4018,
  verificarNTC4024,
  verificarNTC4924Agregado,
  verificarNTC4924Mamposteria,
  verificarNTC5147,
  buscarTerminoNTC6008,
} from "@/lib/vias-api";

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
  grupo: "Geométrico" | "Topografía" | "Pavimentos" | "Mantenimiento" | "NTC Materiales";
  descripcion: string;
  normaRef: string;
  fields: FieldSpec[];
  submit: (payload: Record<string, unknown>) => Promise<Record<string, unknown>>;
  transform?: (raw: Record<string, string>) => Record<string, unknown>;
}

const TIPO_VIA: FieldOption[] = [
  { value: "primaria", label: "Primaria" },
  { value: "secundaria", label: "Secundaria" },
  { value: "terciaria", label: "Terciaria" },
];

const TOPOGRAFIA: FieldOption[] = [
  { value: "plano", label: "Plano" },
  { value: "ondulado", label: "Ondulado" },
  { value: "montanoso", label: "Montañoso" },
  { value: "escarpado", label: "Escarpado" },
];

const TIPO_SUPERFICIE: FieldOption[] = [
  { value: "asfaltica", label: "Asfáltica" },
  { value: "concreto", label: "Concreto" },
  { value: "afirmado", label: "Afirmado" },
];

const TIPO_PAVIMENTO: FieldOption[] = [
  { value: "asfaltico", label: "Asfáltico" },
  { value: "concreto", label: "Concreto" },
];

const TIPO_MANTENIMIENTO: FieldOption[] = [
  { value: "rutinario", label: "Rutinario" },
  { value: "periodico", label: "Periódico" },
  { value: "emergencia", label: "Emergencia" },
];

const TIPO_DETERIORO: FieldOption[] = [
  { value: "bache", label: "Bache" },
  { value: "grieta", label: "Grieta" },
  { value: "ahuellamiento", label: "Ahuellamiento" },
  { value: "craquelado", label: "Craquelado" },
  { value: "hundimiento", label: "Hundimiento" },
  { value: "desplazamiento_borde", label: "Desplazamiento de borde" },
  { value: "losa_fragmentada", label: "Losa fragmentada" },
  { value: "fisura", label: "Fisura" },
];

const GRAVEDAD_DETERIORO: FieldOption[] = [
  { value: "baja", label: "Baja" },
  { value: "media", label: "Media" },
  { value: "alta", label: "Alta" },
  { value: "critica", label: "Crítica" },
];

const ESTANDAR_NIVELACION: FieldOption[] = [
  { value: "invias", label: "INVIAS (C=10)" },
  { value: "idu", label: "IDU (C=5)" },
  { value: "igac", label: "IGAC (C=2)" },
];

const APLICACION_ADOQUIN: FieldOption[] = [
  { value: "peatonal", label: "Peatonal" },
  { value: "vehicular_liviano", label: "Vehicular liviano" },
  { value: "vehicular_pesado", label: "Vehicular pesado" },
  { value: "portuario", label: "Portuario" },
  { value: "industrial", label: "Industrial" },
];

const TIPO_ADOQUIN_2017: FieldOption[] = [
  { value: "no_biselado", label: "No biselado" },
  { value: "con_bisel", label: "Con bisel" },
  { value: "prismatico", label: "Prismático" },
];

const TIPO_GEOTEXTIL: FieldOption[] = [
  { value: "no_tejido", label: "No tejido" },
  { value: "tejido", label: "Tejido" },
  { value: "punzonado_por_agujas", label: "Punzonado por agujas" },
];

const TIPO_CEMENTO: FieldOption[] = [
  { value: "UG", label: "UG — Uso General" },
  { value: "ART", label: "ART — Alta Resistencia Temprana" },
  { value: "RS", label: "RS — Resistente a Sulfatos" },
  { value: "CH", label: "CH — Bajo Calor de Hidratación" },
  { value: "AR", label: "AR — Baja Reactividad Álcali-Sílice" },
  { value: "A", label: "A — Con Incorporadores de Aire" },
];

const TIPO_ADITIVO: FieldOption[] = [
  { value: "A", label: "A — Plastificante" },
  { value: "B", label: "B — Retardante" },
  { value: "C", label: "C — Acelerante" },
  { value: "D", label: "D — Plastificante retardante" },
  { value: "E", label: "E — Plastificante acelerante" },
  { value: "F", label: "F — Superplastificante" },
  { value: "G", label: "G — Superplastificante retardante" },
  { value: "H", label: "H — Superplastificante acelerante" },
];

const TIPO_CEMENTO_BLANCO: FieldOption[] = [
  { value: "I", label: "I — Uso General" },
  { value: "II", label: "II — Moderada Resistencia a Sulfatos" },
  { value: "III", label: "III — Alta Resistencia Temprana" },
];

const FUENTE_AGUA: FieldOption[] = [
  { value: "potable", label: "Potable" },
  { value: "natural", label: "Natural" },
  { value: "lluvia", label: "Lluvia" },
  { value: "reciclada", label: "Reciclada" },
  { value: "industrial_tratada", label: "Industrial tratada" },
];

const CLASE_ADITIVO_MINERAL: FieldOption[] = [
  { value: "N", label: "N — Puzolana natural" },
  { value: "S", label: "S — Puzolana natural (subclase)" },
  { value: "F", label: "F — Ceniza volante (bajo calcio)" },
  { value: "C", label: "C — Ceniza volante (alto calcio)" },
];

const BOOL_OPTIONS: FieldOption[] = [
  { value: "true", label: "Sí" },
  { value: "false", label: "No" },
];

const TIPO_ADITIVO_AIRE: FieldOption[] = [
  { value: "liquido", label: "Líquido" },
  { value: "polvo", label: "Polvo" },
  { value: "pasta", label: "Pasta" },
];

const PRESENTACION_PIGMENTO: FieldOption[] = [
  { value: "polvo", label: "Polvo" },
  { value: "granular", label: "Granular" },
  { value: "liquido", label: "Líquido" },
];

const TIPO_PIGMENTO: FieldOption[] = [
  { value: "oxido_hierro", label: "Óxido de hierro" },
  { value: "oxido_cobalto", label: "Óxido de cobalto" },
  { value: "oxido_cromo", label: "Óxido de cromo" },
  { value: "dioxido_titanio", label: "Dióxido de titanio" },
];

const GRADO_ESCORIA: FieldOption[] = [
  { value: "80", label: "Grado 80" },
  { value: "100", label: "Grado 100" },
  { value: "120", label: "Grado 120" },
];

const TIPO_PREFABRICADO: FieldOption[] = [
  { value: "bloque", label: "Bloque" },
  { value: "ladrillo", label: "Ladrillo" },
  { value: "chapa", label: "Chapa" },
  { value: "gramoquin", label: "Gramoquín" },
  { value: "loseta", label: "Loseta" },
  { value: "otro", label: "Otro" },
];

const TIPO_AGREGADO_LIVIANO: FieldOption[] = [
  { value: "arcilla_expandida", label: "Arcilla expandida" },
  { value: "esquisto_expandido", label: "Esquisto expandido" },
  { value: "puzolana_expandida", label: "Puzolana expandida" },
  { value: "escoría_expandida", label: "Escoria expandida" },
  { value: "otro", label: "Otro" },
];

const TIPO_UNIDAD_MAMPOSTERIA: FieldOption[] = [
  { value: "bloque", label: "Bloque" },
  { value: "ladrillo", label: "Ladrillo" },
  { value: "chapa", label: "Chapa" },
  { value: "otro", label: "Otro" },
];

const TIPO_MATERIAL_ABRASION: FieldOption[] = [
  { value: "adoquin", label: "Adoquín" },
  { value: "loseta", label: "Loseta" },
  { value: "prefabricado", label: "Prefabricado" },
  { value: "otro", label: "Otro" },
];

/** Convierte texto multilínea "edad,resistencia" por línea en {edad: resistencia}. */
function parseEdadResistencia(text: string): Record<string, number> {
  const result: Record<string, number> = {};
  text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .forEach((l) => {
      const [edad, valor] = l.split(",").map((v) => Number(v.trim()));
      if (Number.isFinite(edad) && Number.isFinite(valor)) result[String(edad)] = valor;
    });
  return result;
}

function numOrUndef(v?: string): number | undefined {
  if (v === undefined || v === "") return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
}

export const VIAS_MODULES: ModuleSpec[] = [
  {
    id: "geometrico",
    label: "Diseño geométrico",
    grupo: "Geométrico",
    descripcion: "Valida radio de curva, distancias de visibilidad, pendiente longitudinal, ancho de carril y bombeo contra el Manual de Diseño Geométrico INVIAS.",
    normaRef: "INVIAS 2008 / 2025",
    submit: validarDisenoGeometrico,
    fields: [
      { key: "tipo_via", label: "Tipo de vía", type: "select", options: TIPO_VIA, default: "primaria" },
      { key: "velocidad_diseno", label: "Velocidad de diseño (km/h)", type: "number", default: 80, help: "Múltiplo de 10, entre 30 y 120" },
      { key: "topografia", label: "Topografía", type: "select", options: TOPOGRAFIA, default: "ondulado" },
      { key: "volumen_transito", label: "Volumen de tránsito (TPD)", type: "number", default: 3000 },
      { key: "radio_curva", label: "Radio de curva horizontal (m)", type: "number", default: 180, required: false },
      { key: "pendiente_longitudinal", label: "Pendiente longitudinal (%)", type: "number", default: 5, required: false },
      { key: "peralte", label: "Peralte (%)", type: "number", default: 6, required: false },
      { key: "ancho_carril", label: "Ancho de carril (m)", type: "number", default: 3.5, required: false },
      { key: "bombeo", label: "Bombeo (%)", type: "number", default: 2.5, required: false },
      { key: "tipo_superficie", label: "Tipo de superficie", type: "select", options: TIPO_SUPERFICIE, default: "asfaltica", required: false },
    ],
  },
  {
    id: "topografia_cierre",
    label: "Cierre de nivelación",
    grupo: "Topografía",
    descripcion: "Tolerancia de error de cierre en nivelación geométrica: E_max = C·√K, frente a los coeficientes de INVIAS, IDU o IGAC.",
    normaRef: "INVIAS/IDU/IGAC · NTC 6271",
    submit: verificarCierreNivelacion,
    fields: [
      { key: "error_medido_mm", label: "Error de cierre medido (mm)", type: "number", default: 12 },
      { key: "distancia_km", label: "Longitud del circuito/tramo (km)", type: "number", default: 2.5 },
      { key: "estandar", label: "Estándar de referencia", type: "select", options: ESTANDAR_NIVELACION, default: "invias" },
    ],
  },
  {
    id: "pavimentos",
    label: "Diseño de pavimento",
    grupo: "Pavimentos",
    descripcion: "Diseño estructural de pavimento asfáltico o de concreto (número estructural SN o espesor de losa) por método mecánico-empírico AASHTO 93 adaptado.",
    normaRef: "AASHTO 93 (adaptado) · Manual INVIAS",
    submit: disenarPavimento,
    fields: [
      { key: "tipo_pavimento", label: "Tipo de pavimento", type: "select", options: TIPO_PAVIMENTO, default: "asfaltico" },
      { key: "tipo_via", label: "Tipo de vía", type: "select", options: TIPO_VIA, default: "primaria" },
      { key: "tpd", label: "Tránsito Promedio Diario (TPD)", type: "number", default: 5000 },
      { key: "esals_millones", label: "ESALs de diseño (millones)", type: "number", default: 5.0 },
      { key: "cbr_subrasante", label: "CBR de subrasante (%)", type: "number", default: 5 },
      { key: "modulo_subrasante", label: "Módulo resiliente de subrasante (MPa)", type: "number", default: 50, required: false },
      { key: "ip_subrasante", label: "Índice de plasticidad de subrasante (%)", type: "number", default: 12, required: false },
      { key: "temperatura_media", label: "Temperatura media anual (°C)", type: "number", default: 24, required: false },
      { key: "espesor_subbase", label: "Espesor de subbase (cm)", type: "number", default: 20, required: false },
      { key: "espesor_base", label: "Espesor de base (cm)", type: "number", default: 20, required: false },
      { key: "modulo_subbase", label: "Módulo resiliente de subbase (MPa)", type: "number", required: false },
      { key: "modulo_base", label: "Módulo resiliente de base (MPa)", type: "number", required: false },
    ],
  },
  {
    id: "mantenimiento",
    label: "Diagnóstico de mantenimiento",
    grupo: "Mantenimiento",
    descripcion: "Determina gravedad, prioridad de intervención, tipo de mantenimiento y actividades recomendadas según el Manual de Mantenimiento INVIAS.",
    normaRef: "Manual INVIAS 2016 · Res. 04046/2018",
    submit: diagnosticarMantenimiento,
    fields: [
      { key: "tipo_via", label: "Tipo de vía", type: "select", options: TIPO_VIA, default: "primaria" },
      { key: "tipo_mantenimiento", label: "Tipo de mantenimiento", type: "select", options: TIPO_MANTENIMIENTO, default: "rutinario" },
      { key: "deterioro_tipo", label: "Tipo de deterioro", type: "select", options: TIPO_DETERIORO, default: "bache" },
      { key: "deterioro_gravedad", label: "Gravedad del deterioro", type: "select", options: GRAVEDAD_DETERIORO, default: "media" },
      { key: "area_afectada", label: "Área afectada (m²)", type: "number", default: 1.5, required: false },
      { key: "profundidad", label: "Profundidad (cm)", type: "number", default: 4, required: false },
      { key: "longitud", label: "Longitud de grieta (m)", type: "number", required: false },
      { key: "ancho", label: "Ancho de grieta (mm)", type: "number", required: false },
      { key: "indice_condicion", label: "Índice de condición PCI (%)", type: "number", default: 65, required: false },
      { key: "volumen_transito", label: "Volumen de tránsito (TPD)", type: "number", default: 3000, required: false },
    ],
  },
  {
    id: "ntc2017",
    label: "Adoquines (NTC 2017)",
    grupo: "NTC Materiales",
    descripcion: "Verifica espesor mínimo, resistencia a flexotracción y absorción de adoquines de concreto según su aplicación.",
    normaRef: "NTC 2017",
    submit: verificarNTC2017,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AD-01" },
      { key: "aplicacion", label: "Aplicación", type: "select", options: APLICACION_ADOQUIN, default: "vehicular_liviano" },
      { key: "tipo", label: "Tipo de adoquín", type: "select", options: TIPO_ADOQUIN_2017, default: "con_bisel" },
      { key: "largo_mm", label: "Largo (mm)", type: "number", default: 200 },
      { key: "ancho_mm", label: "Ancho (mm)", type: "number", default: 100 },
      { key: "espesor_mm", label: "Espesor (mm)", type: "number", default: 80 },
      { key: "resistencia_flexion_mpa", label: "Resistencia a flexotracción (MPa)", type: "number", default: 5.5 },
      { key: "absorcion_porcentaje", label: "Absorción (%)", type: "number", default: 6.0 },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
  },
  {
    id: "ntc4342",
    label: "Geotextiles (NTC 4342)",
    grupo: "NTC Materiales",
    descripcion: "Verifica retención asfáltica mínima, composición y tipo de geotextil para pavimentos asfálticos (INVIAS D6140).",
    normaRef: "NTC 4342",
    submit: verificarNTC4342,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "GT-01" },
      { key: "tipo", label: "Tipo de geotextil", type: "select", options: TIPO_GEOTEXTIL, default: "no_tejido" },
      { key: "retencion_asfaltica_l_m2", label: "Retención asfáltica (l/m²)", type: "number", default: 1.1 },
      { key: "composicion", label: "Composición", type: "text", default: "Poliéster" },
      { key: "porcentaje_poliolefinas", label: "Poliolefinas/poliéster (%)", type: "number", default: 96 },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
  },
  {
    id: "ntc121",
    label: "Cemento hidráulico (NTC 121)",
    grupo: "NTC Materiales",
    descripcion: "Verifica resistencia a compresión por edad según tipo, fraguado inicial y expansión en autoclave del cemento hidráulico.",
    normaRef: "NTC 121",
    submit: verificarNTC121,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "CE-01" },
      { key: "tipo", label: "Tipo de cemento", type: "select", options: TIPO_CEMENTO, default: "UG" },
      { key: "resistencias", label: "Resistencia por edad (edad_días, MPa) — uno por línea", type: "pairs", default: "3,13\n7,20\n28,29" },
      { key: "tiempo_fraguado_inicial_min", label: "Fraguado inicial (min)", type: "number", default: 120 },
      { key: "tiempo_fraguado_final_min", label: "Fraguado final (min)", type: "number", default: 300 },
      { key: "expansion_autoclave_porcentaje", label: "Expansión en autoclave (%)", type: "number", default: 0.3 },
      { key: "finura_blaine_m2_kg", label: "Finura Blaine (m²/kg)", type: "number", default: 350 },
      { key: "densidad_g_cm3", label: "Densidad (g/cm³)", type: "number", default: 3.15 },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      resistencia_compresion_mpa: parseEdadResistencia(raw.resistencias || ""),
      tiempo_fraguado_inicial_min: raw.tiempo_fraguado_inicial_min,
      tiempo_fraguado_final_min: raw.tiempo_fraguado_final_min,
      expansion_autoclave_porcentaje: raw.expansion_autoclave_porcentaje,
      finura_blaine_m2_kg: raw.finura_blaine_m2_kg,
      densidad_g_cm3: raw.densidad_g_cm3,
      fabricante: raw.fabricante,
    }),
  },
  {
    id: "ntc1299",
    label: "Aditivos químicos (NTC 1299)",
    grupo: "NTC Materiales",
    descripcion: "Clasifica y verifica el tipo de aditivo químico para concreto según la equivalencia con ASTM C494.",
    normaRef: "NTC 1299 (ASTM C494)",
    submit: verificarNTC1299,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AD-Q-01" },
      { key: "tipo", label: "Tipo de aditivo", type: "select", options: TIPO_ADITIVO, default: "F" },
      { key: "descripcion", label: "Descripción", type: "text", default: "Superplastificante para concreto autocompactante" },
      { key: "aplicaciones", label: "Aplicaciones (separadas por coma)", type: "text", default: "Concreto autocompactante, Concreto bombeado" },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
      { key: "dosificacion_recomendada", label: "Dosificación recomendada", type: "text", required: false, default: "0.5-1.5% del peso del cemento" },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      descripcion: raw.descripcion,
      aplicaciones: (raw.aplicaciones || "").split(",").map((s) => s.trim()).filter(Boolean),
      fabricante: raw.fabricante,
      dosificacion_recomendada: raw.dosificacion_recomendada,
    }),
  },
  {
    id: "ntc1362",
    label: "Cemento blanco (NTC 1362)",
    grupo: "NTC Materiales",
    descripcion: "Verifica resistencia a compresión por edad, blancura, fraguado inicial y expansión en autoclave del cemento hidráulico blanco.",
    normaRef: "NTC 1362",
    submit: verificarNTC1362,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "CB-01" },
      { key: "tipo", label: "Tipo de cemento blanco", type: "select", options: TIPO_CEMENTO_BLANCO, default: "I" },
      { key: "resistencias", label: "Resistencia por edad (edad_días, MPa) — uno por línea", type: "pairs", default: "3,13\n7,20\n28,29" },
      { key: "tiempo_fraguado_inicial_min", label: "Fraguado inicial (min)", type: "number", default: 100 },
      { key: "tiempo_fraguado_final_min", label: "Fraguado final (min)", type: "number", default: 280 },
      { key: "expansion_autoclave_porcentaje", label: "Expansión en autoclave (%)", type: "number", default: 0.2 },
      { key: "finura_blaine_m2_kg", label: "Finura Blaine (m²/kg)", type: "number", default: 380 },
      { key: "blancura_porcentaje", label: "Blancura (%)", type: "number", default: 85 },
      { key: "contenido_alcalis_porcentaje", label: "Contenido de álcalis (%)", type: "number", required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      resistencia_mpa: parseEdadResistencia(raw.resistencias || ""),
      tiempo_fraguado_inicial_min: raw.tiempo_fraguado_inicial_min,
      tiempo_fraguado_final_min: raw.tiempo_fraguado_final_min,
      expansion_autoclave_porcentaje: raw.expansion_autoclave_porcentaje,
      finura_blaine_m2_kg: raw.finura_blaine_m2_kg,
      blancura_porcentaje: raw.blancura_porcentaje,
      contenido_alcalis_porcentaje: numOrUndef(raw.contenido_alcalis_porcentaje),
      fabricante: raw.fabricante,
    }),
  },
  {
    id: "ntc3459",
    label: "Agua para concreto (NTC 3459)",
    grupo: "NTC Materiales",
    descripcion: "Verifica sulfatos, cloruros, sólidos, pH e iones comunes de una muestra de agua para elaboración de concreto.",
    normaRef: "NTC 3459",
    submit: verificarNTC3459,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AG-01" },
      { key: "fuente", label: "Fuente", type: "select", options: FUENTE_AGUA, default: "potable" },
      { key: "analisis_sulfatos_mg_l", label: "Sulfatos (mg/L)", type: "number", default: 400 },
      { key: "analisis_cloruros_mg_l", label: "Cloruros (mg/L)", type: "number", default: 300 },
      { key: "analisis_solidos_totales_mg_l", label: "Sólidos totales (mg/L)", type: "number", default: 1200 },
      { key: "analisis_solidos_disueltos_mg_l", label: "Sólidos disueltos (mg/L)", type: "number", default: 800 },
      { key: "analisis_ph", label: "pH", type: "number", default: 7.0 },
      { key: "analisis_turbiedad", label: "Turbiedad (NTU)", type: "number", required: false },
      { key: "analisis_iones_comunes_mg_l", label: "Iones comunes (mg/L)", type: "number", required: false },
      { key: "analisis_observaciones", label: "Observaciones del análisis", type: "text", required: false },
      { key: "fecha_muestreo", label: "Fecha de muestreo", type: "date", required: false },
      { key: "laboratorio", label: "Laboratorio", type: "text", required: false },
      { key: "concreto_preesforzado", label: "¿Concreto pre-esforzado?", type: "select", options: BOOL_OPTIONS, default: "false" },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      fuente: raw.fuente,
      analisis: {
        sulfatos_mg_l: Number(raw.analisis_sulfatos_mg_l),
        cloruros_mg_l: Number(raw.analisis_cloruros_mg_l),
        solidos_totales_mg_l: Number(raw.analisis_solidos_totales_mg_l),
        solidos_disueltos_mg_l: Number(raw.analisis_solidos_disueltos_mg_l),
        ph: Number(raw.analisis_ph),
        turbiedad: numOrUndef(raw.analisis_turbiedad),
        iones_comunes_mg_l: numOrUndef(raw.analisis_iones_comunes_mg_l),
        observaciones: raw.analisis_observaciones || undefined,
      },
      fecha_muestreo: raw.fecha_muestreo || undefined,
      laboratorio: raw.laboratorio || undefined,
      concreto_preesforzado: raw.concreto_preesforzado === "true",
    }),
  },
  {
    id: "ntc3493",
    label: "Cenizas volantes / puzolanas (NTC 3493)",
    grupo: "NTC Materiales",
    descripcion: "Verifica suma de óxidos, pérdida por ignición y retención en malla 325 de un aditivo mineral (equivalente ASTM C618).",
    normaRef: "NTC 3493 (ASTM C618)",
    submit: verificarNTC3493,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AM-01" },
      { key: "clase", label: "Clase", type: "select", options: CLASE_ADITIVO_MINERAL, default: "F" },
      { key: "analisis_sio2_porcentaje", label: "SiO2 (%)", type: "number", default: 50 },
      { key: "analisis_al2o3_porcentaje", label: "Al2O3 (%)", type: "number", default: 20 },
      { key: "analisis_fe2o3_porcentaje", label: "Fe2O3 (%)", type: "number", default: 6 },
      { key: "analisis_perdida_ignicion_porcentaje", label: "Pérdida por ignición (%)", type: "number", default: 4 },
      { key: "analisis_retencion_malla_325_porcentaje", label: "Retención malla No. 325 (%)", type: "number", default: 20 },
      { key: "analisis_finura_blaine_m2_kg", label: "Finura Blaine (m²/kg)", type: "number", required: false },
      { key: "analisis_densidad_g_cm3", label: "Densidad (g/cm³)", type: "number", required: false },
      { key: "analisis_observaciones", label: "Observaciones del análisis", type: "text", required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
      { key: "origen", label: "Origen", type: "text", required: false },
      { key: "tolerancia_loi", label: "¿Tolerancia LOI hasta 12%?", type: "select", options: BOOL_OPTIONS, default: "false" },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      clase: raw.clase,
      analisis: {
        sio2_porcentaje: Number(raw.analisis_sio2_porcentaje),
        al2o3_porcentaje: Number(raw.analisis_al2o3_porcentaje),
        fe2o3_porcentaje: Number(raw.analisis_fe2o3_porcentaje),
        perdida_ignicion_porcentaje: Number(raw.analisis_perdida_ignicion_porcentaje),
        retencion_malla_325_porcentaje: Number(raw.analisis_retencion_malla_325_porcentaje),
        finura_blaine_m2_kg: numOrUndef(raw.analisis_finura_blaine_m2_kg),
        densidad_g_cm3: numOrUndef(raw.analisis_densidad_g_cm3),
        observaciones: raw.analisis_observaciones || undefined,
      },
      fabricante: raw.fabricante,
      origen: raw.origen,
      tolerancia_loi: raw.tolerancia_loi === "true",
    }),
  },
  {
    id: "ntc3502",
    label: "Aditivos incorporadores de aire (NTC 3502)",
    grupo: "NTC Materiales",
    descripcion: "Verifica contenido de aire incorporado y ausencia de cloruros de un aditivo incorporador de aire (equivalente ASTM C260).",
    normaRef: "NTC 3502 (ASTM C260)",
    submit: verificarNTC3502,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AI-01" },
      { key: "tipo", label: "Tipo de aditivo", type: "select", options: TIPO_ADITIVO_AIRE, default: "liquido" },
      { key: "contenido_aire_porcentaje", label: "Contenido de aire incorporado (%)", type: "number", default: 5.5 },
      { key: "dosificacion_recomendada", label: "Dosificación recomendada", type: "text", default: "150-300 ml/100kg cemento" },
      { key: "libre_cloruros", label: "¿Libre de cloruros?", type: "select", options: BOOL_OPTIONS, default: "true" },
      { key: "ph", label: "pH", type: "number", default: 7, required: false },
      { key: "densidad_g_cm3", label: "Densidad (g/cm³)", type: "number", default: 1.02, required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      contenido_aire_porcentaje: raw.contenido_aire_porcentaje,
      dosificacion_recomendada: raw.dosificacion_recomendada,
      libre_cloruros: raw.libre_cloruros === "true",
      ph: raw.ph,
      densidad_g_cm3: raw.densidad_g_cm3,
      fabricante: raw.fabricante,
    }),
  },
  {
    id: "ntc3760",
    label: "Pigmentos para concreto (NTC 3760)",
    grupo: "NTC Materiales",
    descripcion: "Verifica dosificación máxima, resistencia alcalina y a la intemperie de un pigmento para concreto coloreado integralmente.",
    normaRef: "NTC 3760 (ASTM C979)",
    submit: verificarNTC3760,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "PIG-01" },
      { key: "tipo", label: "Tipo de pigmento", type: "select", options: TIPO_PIGMENTO, default: "oxido_hierro" },
      { key: "presentacion", label: "Presentación", type: "select", options: PRESENTACION_PIGMENTO, default: "polvo" },
      { key: "dosificacion_maxima_porcentaje", label: "Dosificación máxima (% del peso del cemento)", type: "number", default: 6 },
      { key: "color", label: "Color", type: "text", default: "Rojo óxido" },
      { key: "resistencia_alcalina", label: "¿Resistente a la alcalinidad?", type: "select", options: BOOL_OPTIONS, default: "true" },
      { key: "resistencia_intemperie", label: "¿Resistente a la intemperie?", type: "select", options: BOOL_OPTIONS, default: "true" },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      presentacion: raw.presentacion,
      dosificacion_maxima_porcentaje: raw.dosificacion_maxima_porcentaje,
      color: raw.color,
      resistencia_alcalina: raw.resistencia_alcalina === "true",
      resistencia_intemperie: raw.resistencia_intemperie === "true",
      fabricante: raw.fabricante,
    }),
  },
  {
    id: "ntc4018",
    label: "Escoria de alto horno (NTC 4018)",
    grupo: "NTC Materiales",
    descripcion: "Verifica el grado y el índice de actividad con cemento Portland a 7 y 28 días de una escoria de alto horno (equivalente ASTM C989).",
    normaRef: "NTC 4018 (ASTM C989)",
    submit: verificarNTC4018,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "ESC-01" },
      { key: "grado", label: "Grado", type: "select", options: GRADO_ESCORIA, default: "100" },
      { key: "analisis_indice_actividad_7dias", label: "Índice de actividad a 7 días (%)", type: "number", default: 78 },
      { key: "analisis_indice_actividad_28dias", label: "Índice de actividad a 28 días (%)", type: "number", default: 102 },
      { key: "analisis_finura_blaine_m2_kg", label: "Finura Blaine (m²/kg)", type: "number", default: 420 },
      { key: "analisis_densidad_g_cm3", label: "Densidad (g/cm³)", type: "number", default: 2.9 },
      { key: "analisis_contenido_azufre_porcentaje", label: "Contenido de azufre (%)", type: "number", default: 1.2, required: false },
      { key: "analisis_perdida_ignicion_porcentaje", label: "Pérdida por ignición (%)", type: "number", required: false },
      { key: "analisis_observaciones", label: "Observaciones del análisis", type: "text", required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
      { key: "origen", label: "Origen", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      grado: Number(raw.grado),
      analisis: {
        indice_actividad_7dias: Number(raw.analisis_indice_actividad_7dias),
        indice_actividad_28dias: Number(raw.analisis_indice_actividad_28dias),
        finura_blaine_m2_kg: Number(raw.analisis_finura_blaine_m2_kg),
        densidad_g_cm3: Number(raw.analisis_densidad_g_cm3),
        contenido_azufre_porcentaje: numOrUndef(raw.analisis_contenido_azufre_porcentaje),
        perdida_ignicion_porcentaje: numOrUndef(raw.analisis_perdida_ignicion_porcentaje),
        observaciones: raw.analisis_observaciones || undefined,
      },
      fabricante: raw.fabricante,
      origen: raw.origen,
    }),
  },
  {
    id: "ntc4024",
    label: "Prefabricados de concreto (NTC 4024)",
    grupo: "NTC Materiales",
    descripcion: "Verifica número de especímenes según tamaño de lote, ensayos realizados y dimensiones de un prefabricado de concreto.",
    normaRef: "NTC 4024",
    submit: verificarNTC4024,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "PREF-01" },
      { key: "tipo", label: "Tipo de prefabricado", type: "select", options: TIPO_PREFABRICADO, default: "bloque" },
      { key: "dim_longitud_mm", label: "Longitud (mm)", type: "number", default: 400 },
      { key: "dim_altura_mm", label: "Altura (mm)", type: "number", default: 200 },
      { key: "dim_espesor_mm", label: "Espesor (mm)", type: "number", default: 100 },
      { key: "dim_espesor_pared_mm", label: "Espesor de pared (mm)", type: "number", default: 25, required: false },
      { key: "dim_espesor_tabique_mm", label: "Espesor de tabique (mm)", type: "number", default: 20, required: false },
      { key: "res_resistencia_compresion_mpa", label: "Resistencia a compresión (MPa)", type: "number", default: 14, required: false },
      { key: "res_absorcion_porcentaje", label: "Absorción (%)", type: "number", default: 9, required: false },
      { key: "res_densidad_g_cm3", label: "Densidad (g/cm³)", type: "number", default: 2.1, required: false },
      { key: "res_contenido_humedad_porcentaje", label: "Contenido de humedad (%)", type: "number", default: 5, required: false },
      { key: "res_observaciones", label: "Observaciones de ensayo", type: "text", required: false },
      { key: "tamano_lote", label: "Tamaño del lote (unidades)", type: "number", default: 5000 },
      { key: "numero_especimenes", label: "Número de especímenes tomados", type: "number", default: 6 },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
      { key: "fecha_muestreo", label: "Fecha de muestreo", type: "date", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      dimensiones: {
        longitud_mm: Number(raw.dim_longitud_mm),
        altura_mm: Number(raw.dim_altura_mm),
        espesor_mm: Number(raw.dim_espesor_mm),
        espesor_pared_mm: numOrUndef(raw.dim_espesor_pared_mm),
        espesor_tabique_mm: numOrUndef(raw.dim_espesor_tabique_mm),
      },
      resultados: {
        resistencia_compresion_mpa: numOrUndef(raw.res_resistencia_compresion_mpa),
        absorcion_porcentaje: numOrUndef(raw.res_absorcion_porcentaje),
        densidad_g_cm3: numOrUndef(raw.res_densidad_g_cm3),
        contenido_humedad_porcentaje: numOrUndef(raw.res_contenido_humedad_porcentaje),
        observaciones: raw.res_observaciones || undefined,
      },
      tamano_lote: raw.tamano_lote,
      numero_especimenes: raw.numero_especimenes,
      fabricante: raw.fabricante,
      fecha_muestreo: raw.fecha_muestreo || undefined,
    }),
  },
  {
    id: "ntc4924_agregado",
    label: "Agregado liviano (NTC 4924)",
    grupo: "NTC Materiales",
    descripcion: "Verifica densidad aparente máxima y absorción de un agregado liviano para unidades de mampostería (equivalente ASTM C331).",
    normaRef: "NTC 4924 (ASTM C331)",
    submit: verificarNTC4924Agregado,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AGL-01" },
      { key: "tipo", label: "Tipo de agregado liviano", type: "select", options: TIPO_AGREGADO_LIVIANO, default: "arcilla_expandida" },
      { key: "densidad_aparente_kg_m3", label: "Densidad aparente (kg/m³)", type: "number", default: 850 },
      { key: "absorcion_porcentaje", label: "Absorción (%)", type: "number", default: 18 },
      { key: "resistencia_compresion_mpa", label: "Resistencia a compresión (MPa)", type: "number", default: 3.5, required: false },
      { key: "tamano_maximo_mm", label: "Tamaño máximo (mm)", type: "number", default: 12.5, required: false },
      { key: "modulo_finura", label: "Módulo de finura", type: "number", default: 3.0, required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
  },
  {
    id: "ntc4924_mamposteria",
    label: "Unidad de mampostería liviana (NTC 4924)",
    grupo: "NTC Materiales",
    descripcion: "Verifica el agregado liviano base y la resistencia a compresión, densidad y absorción de una unidad de mampostería con agregado liviano.",
    normaRef: "NTC 4924",
    submit: verificarNTC4924Mamposteria,
    fields: [
      { key: "nombre", label: "Identificación de la unidad", type: "text", default: "BLQ-01" },
      { key: "tipo", label: "Tipo de unidad", type: "select", options: TIPO_UNIDAD_MAMPOSTERIA, default: "bloque" },
      { key: "agregado_nombre", label: "Agregado — identificación", type: "text", default: "AGL-01" },
      { key: "agregado_tipo", label: "Agregado — tipo", type: "select", options: TIPO_AGREGADO_LIVIANO, default: "arcilla_expandida" },
      { key: "agregado_densidad_aparente_kg_m3", label: "Agregado — densidad aparente (kg/m³)", type: "number", default: 850 },
      { key: "agregado_absorcion_porcentaje", label: "Agregado — absorción (%)", type: "number", default: 18 },
      { key: "agregado_resistencia_compresion_mpa", label: "Agregado — resistencia a compresión (MPa)", type: "number", default: 3.5, required: false },
      { key: "agregado_tamano_maximo_mm", label: "Agregado — tamaño máximo (mm)", type: "number", default: 12.5, required: false },
      { key: "agregado_modulo_finura", label: "Agregado — módulo de finura", type: "number", default: 3.0, required: false },
      { key: "agregado_fabricante", label: "Agregado — fabricante", type: "text", required: false },
      { key: "dim_largo", label: "Dimensión — largo (mm)", type: "number", default: 400 },
      { key: "dim_ancho", label: "Dimensión — ancho (mm)", type: "number", default: 200 },
      { key: "dim_alto", label: "Dimensión — alto (mm)", type: "number", default: 200 },
      { key: "resistencia_compresion_mpa", label: "Resistencia a compresión de la unidad (MPa)", type: "number", default: 6 },
      { key: "densidad_aparente_kg_m3", label: "Densidad aparente de la unidad (kg/m³)", type: "number", default: 1400 },
      { key: "absorcion_porcentaje", label: "Absorción de la unidad (%)", type: "number", default: 12 },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      agregado: {
        nombre: raw.agregado_nombre,
        tipo: raw.agregado_tipo,
        densidad_aparente_kg_m3: Number(raw.agregado_densidad_aparente_kg_m3),
        absorcion_porcentaje: Number(raw.agregado_absorcion_porcentaje),
        resistencia_compresion_mpa: numOrUndef(raw.agregado_resistencia_compresion_mpa),
        tamano_maximo_mm: numOrUndef(raw.agregado_tamano_maximo_mm),
        modulo_finura: numOrUndef(raw.agregado_modulo_finura),
        fabricante: raw.agregado_fabricante || undefined,
      },
      dimensiones_mm: {
        largo: Number(raw.dim_largo),
        ancho: Number(raw.dim_ancho),
        alto: Number(raw.dim_alto),
      },
      resistencia_compresion_mpa: Number(raw.resistencia_compresion_mpa),
      densidad_aparente_kg_m3: Number(raw.densidad_aparente_kg_m3),
      absorcion_porcentaje: Number(raw.absorcion_porcentaje),
      fabricante: raw.fabricante || undefined,
    }),
  },
  {
    id: "ntc5147",
    label: "Resistencia a la abrasión (NTC 5147)",
    grupo: "NTC Materiales",
    descripcion: "Verifica la longitud promedio de huella de abrasión (5 especímenes, disco metálico y arena) frente al máximo de 23 mm.",
    normaRef: "NTC 5147",
    submit: verificarNTC5147,
    fields: [
      { key: "nombre", label: "Identificación de la muestra", type: "text", default: "AB-01" },
      { key: "tipo", label: "Tipo de material", type: "select", options: TIPO_MATERIAL_ABRASION, default: "adoquin" },
      { key: "huella1", label: "Huella 1 (mm)", type: "number", default: 18 },
      { key: "huella2", label: "Huella 2 (mm)", type: "number", default: 19 },
      { key: "huella3", label: "Huella 3 (mm)", type: "number", default: 17.5 },
      { key: "huella4", label: "Huella 4 (mm)", type: "number", default: 18.5 },
      { key: "huella5", label: "Huella 5 (mm)", type: "number", default: 19.2 },
      { key: "observaciones", label: "Observaciones", type: "text", required: false },
      { key: "fecha_ensayo", label: "Fecha de ensayo", type: "date", required: false },
      { key: "laboratorio", label: "Laboratorio", type: "text", required: false },
      { key: "fabricante", label: "Fabricante", type: "text", required: false },
    ],
    transform: (raw) => ({
      nombre: raw.nombre,
      tipo: raw.tipo,
      resultados: {
        longitud_huella_1_mm: Number(raw.huella1),
        longitud_huella_2_mm: Number(raw.huella2),
        longitud_huella_3_mm: Number(raw.huella3),
        longitud_huella_4_mm: Number(raw.huella4),
        longitud_huella_5_mm: Number(raw.huella5),
        observaciones: raw.observaciones || undefined,
      },
      fecha_ensayo: raw.fecha_ensayo || undefined,
      laboratorio: raw.laboratorio || undefined,
      fabricante: raw.fabricante || undefined,
    }),
  },
  {
    id: "ntc6008",
    label: "Terminología de adoquines (NTC 6008)",
    grupo: "NTC Materiales",
    descripcion: "Busca definiciones de terminología y clasificación de adoquines y losetas de concreto en NTC 6008.",
    normaRef: "NTC 6008",
    submit: buscarTerminoNTC6008,
    fields: [
      { key: "termino_busqueda", label: "Término a buscar", type: "text", default: "adoquín drenante" },
    ],
  },
];
