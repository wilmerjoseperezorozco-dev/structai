/**
 * AquAI — especificación de los 11 módulos RAS 2000
 * Formularios data-driven: cada módulo declara sus campos una sola vez y
 * `AquAIPanel` los renderiza genéricamente (evita 11 formularios casi
 * idénticos copy-pasteados).
 */
import {
  proyectarPoblacion,
  calcularCaudales,
  calcularHazenWilliams,
  calcularHidrologia,
  calcularManning,
  calcularAriete,
  calcularBombeo,
  calcularPTAP,
  calcularPTAR,
  calcularTarifa,
  generarReporteSUI,
} from "@/lib/aquai-api";

export type FieldType = "number" | "text" | "select";

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
  min?: number;
  max?: number;
  required?: boolean; // default true — si es false y queda vacío, se omite del payload
  help?: string;
}

export interface ModuleSpec {
  id: string;
  label: string;
  grupo: "Demanda" | "Hidráulica" | "Hidrología" | "Saneamiento" | "Tarifario";
  descripcion: string;
  normaRef: string;
  fields: FieldSpec[];
  submit: (payload: Record<string, unknown>) => Promise<Record<string, unknown>>;
  /** Recompone el payload crudo del formulario antes de enviarlo (para campos agrupados, ej. suscriptores_por_estrato) */
  transform?: (raw: Record<string, string>) => Record<string, unknown>;
}

// ── Opciones de enums compartidas (deben calzar exacto con schemas*.py) ───────

const NIVEL_COMPLEJIDAD: FieldOption[] = [
  { value: "bajo", label: "Bajo" },
  { value: "medio", label: "Medio" },
  { value: "medio_alto", label: "Medio-alto" },
  { value: "alto", label: "Alto" },
];

const CLIMA: FieldOption[] = [
  { value: "frio", label: "Frío (< 12°C)" },
  { value: "templado", label: "Templado (12–24°C)" },
  { value: "calido", label: "Cálido (> 24°C)" },
];

const METODO_POBLACION: FieldOption[] = [
  { value: "geometrico", label: "Geométrico" },
  { value: "aritmetico", label: "Aritmético" },
  { value: "exponencial", label: "Exponencial" },
];

const MATERIAL_TUBERIA: FieldOption[] = [
  { value: "PVC", label: "PVC" },
  { value: "HDPE", label: "HDPE" },
  { value: "concreto", label: "Concreto" },
  { value: "concreto_reforzado", label: "Concreto reforzado" },
  { value: "acero", label: "Acero" },
  { value: "grp", label: "GRP (fibra de vidrio)" },
  { value: "gres", label: "Gres vitrificado" },
];

const MATERIAL_HAZEN: FieldOption[] = [
  { value: "PVC", label: "PVC" },
  { value: "HDPE", label: "HDPE" },
  { value: "ACERO", label: "Acero" },
  { value: "AC", label: "Asbesto-cemento" },
  { value: "CONCRETO", label: "Concreto" },
];

const REGION_IDF: FieldOption[] = [
  { value: "caribe", label: "Caribe" },
  { value: "andina_norte", label: "Andina norte" },
  { value: "andina_sur", label: "Andina sur" },
  { value: "pacifico", label: "Pacífico" },
  { value: "orinoquia", label: "Orinoquía" },
  { value: "amazonia", label: "Amazonía" },
];

const METODO_TC: FieldOption[] = [
  { value: "kirpich", label: "Kirpich" },
  { value: "temez", label: "Témez" },
  { value: "bransby_williams", label: "Bransby-Williams" },
];

const TIPO_FLUIDO: FieldOption[] = [
  { value: "agua_potable", label: "Agua potable" },
  { value: "agua_cruda", label: "Agua cruda" },
  { value: "agua_residual", label: "Agua residual" },
];

const COAGULANTE: FieldOption[] = [
  { value: "alumbre", label: "Alumbre (sulfato de aluminio)" },
  { value: "pac", label: "PAC (poli-cloruro de aluminio)" },
  { value: "sulfato_ferrico", label: "Sulfato férrico" },
  { value: "cloruro_ferrico", label: "Cloruro férrico" },
];

const TECNOLOGIA_PTAR: FieldOption[] = [
  { value: "uasb", label: "UASB (reactor anaerobio)" },
  { value: "lodos_activados", label: "Lodos activados" },
  { value: "filtro_percolador", label: "Filtro percolador" },
  { value: "laguna_facultativa", label: "Laguna facultativa" },
];

const CUERPO_RECEPTOR: FieldOption[] = [
  { value: "rio", label: "Río" },
  { value: "quebrada", label: "Quebrada" },
  { value: "lago", label: "Lago" },
  { value: "suelo", label: "Suelo (infiltración)" },
];

const TIPO_PRESTADOR: FieldOption[] = [
  { value: "grande", label: "Grande (> 5.000 suscriptores)" },
  { value: "pequeno", label: "Pequeño (≤ 5.000 suscriptores)" },
  { value: "rural", label: "Rural (esquema diferencial)" },
];

const SERVICIO: FieldOption[] = [
  { value: "acueducto", label: "Acueducto" },
  { value: "alcantarillado", label: "Alcantarillado" },
  { value: "ambos", label: "Ambos" },
];

// ── Los 11 módulos ─────────────────────────────────────────────────────────

export const AQUAI_MODULES: ModuleSpec[] = [
  {
    id: "poblacion",
    label: "1. Población",
    grupo: "Demanda",
    descripcion: "Proyección de población de diseño por método aritmético, geométrico o exponencial.",
    normaRef: "RAS 2000 Título B.2",
    submit: proyectarPoblacion,
    fields: [
      { key: "poblacion_censal", label: "Población censal", type: "number", default: 8000 },
      { key: "anio_censo", label: "Año del censo", type: "number", default: 2018 },
      { key: "anio_diseno", label: "Año de diseño", type: "number", default: 2045 },
      { key: "tasa_crecimiento", label: "Tasa de crecimiento anual (decimal)", type: "number", step: 0.001, required: false, help: "Ej. 0.022 = 2.2%. Si se omite, se estima por nivel de complejidad." },
      { key: "nivel_complejidad", label: "Nivel de complejidad", type: "select", options: NIVEL_COMPLEJIDAD, default: "medio_alto" },
      { key: "metodo", label: "Método", type: "select", options: METODO_POBLACION, default: "geometrico" },
    ],
  },
  {
    id: "caudales",
    label: "2. Caudales",
    grupo: "Demanda",
    descripcion: "Dotación neta/bruta y caudales de diseño Qmd, Qmh y contra incendio.",
    normaRef: "RAS 2000 Título B.2–B.7",
    submit: calcularCaudales,
    fields: [
      { key: "poblacion_diseno", label: "Población de diseño", type: "number", default: 13784 },
      { key: "nivel_complejidad", label: "Nivel de complejidad", type: "select", options: NIVEL_COMPLEJIDAD, default: "medio_alto" },
      { key: "clima", label: "Clima", type: "select", options: CLIMA, default: "calido" },
      { key: "dotacion_manual", label: "Dotación manual (L/hab/día)", type: "number", required: false, help: "Si se provee, omite la tabla RAS." },
      { key: "perdidas_pct", label: "Pérdidas en la red (%)", type: "number", default: 25 },
    ],
  },
  {
    id: "hidraulica",
    label: "3. Hazen-Williams",
    grupo: "Hidráulica",
    descripcion: "Diámetro, velocidad y pérdida de carga en tuberías de conducción/distribución.",
    normaRef: "RAS 2000 Título B.6.4",
    submit: calcularHazenWilliams,
    fields: [
      { key: "caudal_ls", label: "Caudal de diseño (L/s)", type: "number", default: 32.5 },
      { key: "longitud_m", label: "Longitud del tramo (m)", type: "number", default: 500 },
      { key: "diametro_mm", label: "Diámetro nominal (mm)", type: "number", required: false, help: "Si se omite, el motor calcula el mínimo que cumple." },
      { key: "cota_inicio_m", label: "Cota piezométrica aguas arriba (m)", type: "number", default: 0 },
      { key: "presion_minima_mca", label: "Presión mínima requerida (m.c.a.)", type: "number", default: 10 },
      { key: "presion_maxima_mca", label: "Presión máxima permitida (m.c.a.)", type: "number", default: 60 },
      { key: "material", label: "Material", type: "select", options: MATERIAL_HAZEN, default: "PVC" },
    ],
  },
  {
    id: "hidrologia",
    label: "4. Hidrología",
    grupo: "Hidrología",
    descripcion: "Caudal de diseño por el Método Racional usando curvas IDF regionales.",
    normaRef: "RAS 2000 Título D.4 · Res. 0330/2017",
    submit: calcularHidrologia,
    fields: [
      { key: "area_cuenca_ha", label: "Área de la cuenca (ha)", type: "number", default: 45 },
      { key: "longitud_cauce_m", label: "Longitud del cauce principal (m)", type: "number", default: 850 },
      { key: "pendiente_media", label: "Pendiente media del cauce (m/m)", type: "number", step: 0.001, default: 0.02 },
      { key: "periodo_retorno", label: "Período de retorno (años)", type: "number", default: 25 },
      { key: "coeficiente_escorrentia", label: "Coeficiente de escorrentía C", type: "number", step: 0.01, default: 0.55 },
      { key: "region_idf", label: "Región IDF", type: "select", options: REGION_IDF, default: "caribe" },
      { key: "metodo_tc", label: "Método tiempo de concentración", type: "select", options: METODO_TC, default: "kirpich" },
    ],
  },
  {
    id: "manning",
    label: "5. Manning (alcantarillado)",
    grupo: "Hidráulica",
    descripcion: "Verificación hidráulica a flujo parcial en tuberías de alcantarillado a gravedad.",
    normaRef: "RAS 2000 Título D.3",
    submit: calcularManning,
    fields: [
      { key: "caudal_diseno_ls", label: "Caudal de diseño (L/s)", type: "number", default: 18 },
      { key: "pendiente_m_m", label: "Pendiente longitudinal (m/m)", type: "number", step: 0.001, default: 0.008 },
      { key: "material", label: "Material", type: "select", options: MATERIAL_TUBERIA, default: "PVC" },
      { key: "diametro_nominal_mm", label: "Diámetro nominal (mm)", type: "number", required: false, help: "Si se omite, el motor selecciona el mínimo." },
      { key: "relacion_tirante_max", label: "Relación tirante máxima d/D", type: "number", step: 0.05, default: 0.75 },
    ],
  },
  {
    id: "ariete",
    label: "6. Golpe de ariete",
    grupo: "Hidráulica",
    descripcion: "Sobrepresión transitoria (Joukowski) y riesgo de cavitación ante cierre de válvula.",
    normaRef: "RAS 2000 Título B",
    submit: calcularAriete,
    fields: [
      { key: "caudal_ls", label: "Caudal circulante (L/s)", type: "number", default: 32.5 },
      { key: "diametro_interno_mm", label: "Diámetro interno (mm)", type: "number", default: 200 },
      { key: "longitud_m", label: "Longitud de la línea (m)", type: "number", default: 800 },
      { key: "velocidad_cierre_s", label: "Tiempo de cierre válvula/paro bomba (s)", type: "number", default: 2 },
      { key: "material", label: "Material", type: "select", options: MATERIAL_TUBERIA, default: "PVC" },
      { key: "espesor_pared_mm", label: "Espesor de pared (mm)", type: "number", default: 6 },
      { key: "presion_estatica_m", label: "Presión estática de trabajo (m.c.a.)", type: "number", default: 45 },
      { key: "temperatura_agua_c", label: "Temperatura del agua (°C)", type: "number", default: 20 },
    ],
  },
  {
    id: "bombeo",
    label: "7. Estación de bombeo",
    grupo: "Hidráulica",
    descripcion: "TDH, potencia y NPSH disponible para configurar la estación de bombeo.",
    normaRef: "RAS 2000 Título B.8",
    submit: calcularBombeo,
    fields: [
      { key: "caudal_diseno_ls", label: "Caudal de diseño (L/s)", type: "number", default: 32.5 },
      { key: "altura_geometrica_m", label: "Altura geométrica Hg (m)", type: "number", default: 25 },
      { key: "longitud_succion_m", label: "Longitud línea succión (m)", type: "number", default: 10 },
      { key: "longitud_descarga_m", label: "Longitud línea impulsión (m)", type: "number", default: 600 },
      { key: "diametro_succion_mm", label: "Diámetro succión (mm)", type: "number", default: 200 },
      { key: "diametro_descarga_mm", label: "Diámetro descarga (mm)", type: "number", default: 150 },
      { key: "material_succion", label: "Material succión", type: "select", options: MATERIAL_TUBERIA, default: "HDPE" },
      { key: "material_descarga", label: "Material descarga", type: "select", options: MATERIAL_TUBERIA, default: "HDPE" },
      { key: "n_accesorios_codos", label: "N° codos", type: "number", default: 2 },
      { key: "n_accesorios_valvulas", label: "N° válvulas", type: "number", default: 2 },
      { key: "altitud_msnm", label: "Altitud de la estación (msnm)", type: "number", default: 15 },
      { key: "tipo_fluido", label: "Tipo de fluido", type: "select", options: TIPO_FLUIDO, default: "agua_potable" },
      { key: "eficiencia_bomba_pct", label: "Eficiencia hidráulica bomba (%)", type: "number", default: 75 },
      { key: "eficiencia_motor_pct", label: "Eficiencia motor eléctrico (%)", type: "number", default: 92 },
      { key: "n_bombas_paralelo", label: "N° bombas en paralelo", type: "number", default: 1 },
    ],
  },
  {
    id: "ptap",
    label: "8. PTAP",
    grupo: "Saneamiento",
    descripcion: "Dimensionamiento de planta de potabilización: coagulación, floculación, filtración y desinfección.",
    normaRef: "Res. 0330/2017 Título C · Res. 2115/2007",
    submit: calcularPTAP,
    fields: [
      { key: "caudal_diseno_ls", label: "Caudal de diseño Qmd (L/s)", type: "number", default: 32.5 },
      { key: "turbidez_cruda_ntu", label: "Turbidez agua cruda (NTU)", type: "number", default: 80 },
      { key: "color_crudo_uc", label: "Color aparente agua cruda (UC)", type: "number", default: 15 },
      { key: "ph_crudo", label: "pH agua cruda", type: "number", step: 0.1, default: 7 },
      { key: "temperatura_c", label: "Temperatura media del agua (°C)", type: "number", default: 27 },
      { key: "coagulante", label: "Coagulante", type: "select", options: COAGULANTE, default: "alumbre" },
      { key: "nivel_complejidad", label: "Nivel de complejidad", type: "select", options: NIVEL_COMPLEJIDAD, default: "medio_alto" },
    ],
  },
  {
    id: "ptar",
    label: "9. PTAR",
    grupo: "Saneamiento",
    descripcion: "Dimensionamiento de planta de tratamiento de aguas residuales y balance de lodos.",
    normaRef: "RAS 2000 Título E · Res. 0631/2015",
    submit: calcularPTAR,
    fields: [
      { key: "poblacion_diseno", label: "Población de diseño", type: "number", default: 13784 },
      { key: "caudal_acueducto_ls", label: "Caudal acueducto Qmd (L/s)", type: "number", default: 32.5 },
      { key: "factor_retorno", label: "Factor de retorno", type: "number", step: 0.01, default: 0.8 },
      { key: "dbo5_cruda_mg_l", label: "DBO₅ cruda (mg/L)", type: "number", required: false, help: "Si se omite, se estima per cápita." },
      { key: "sst_crudo_mg_l", label: "SST crudo (mg/L)", type: "number", required: false },
      { key: "tecnologia", label: "Tecnología", type: "select", options: TECNOLOGIA_PTAR, default: "uasb" },
      { key: "nivel_complejidad", label: "Nivel de complejidad", type: "select", options: NIVEL_COMPLEJIDAD, default: "medio_alto" },
      { key: "tipo_cuerpo_receptor", label: "Cuerpo receptor", type: "select", options: CUERPO_RECEPTOR, default: "rio" },
      { key: "eficiencia_requerida_dbo_pct", label: "Eficiencia mínima remoción DBO (%)", type: "number", required: false, help: "Si se omite, se calcula desde la Res. 0631/2015." },
    ],
  },
  {
    id: "tarifas",
    label: "10. Tarifas CRA",
    grupo: "Tarifario",
    descripcion: "Cargo fijo y cargo por consumo por estrato según metodología tarifaria CRA.",
    normaRef: "CRA 688/2014 · CRA 825/2017 · Ley 142/1994",
    submit: calcularTarifa,
    fields: [
      { key: "tipo_prestador", label: "Tipo de prestador", type: "select", options: TIPO_PRESTADOR, default: "pequeno" },
      { key: "clima", label: "Clima", type: "select", options: CLIMA, default: "calido" },
      { key: "servicio", label: "Servicio", type: "select", options: SERVICIO, default: "acueducto" },
      { key: "costo_medio_inversion_cmi", label: "CMI — costo medio inversión ($/m³)", type: "number", default: 1800 },
      { key: "costo_medio_operacion_cmo", label: "CMO — costo medio operación ($/m³)", type: "number", default: 900 },
      { key: "costo_medio_administracion_cma", label: "CMA — costo medio admin. ($/suscriptor/mes)", type: "number", default: 4500 },
      { key: "consumo_medio_facturado_m3", label: "Consumo medio facturado (m³/mes)", type: "number", default: 15 },
      { key: "factor_perdidas", label: "Factor de pérdidas (IANC)", type: "number", step: 0.01, default: 0.25 },
      { key: "anio_calculo", label: "Año de cálculo", type: "number", default: 2026 },
    ],
  },
  {
    id: "sui",
    label: "11. Reporte SUI",
    grupo: "Tarifario",
    descripcion: "Estructura de indicadores lista para el portal SUI: IANC, IRCA y alertas regulatorias.",
    normaRef: "Res. CRA · Res. 2115/2007",
    submit: generarReporteSUI,
    fields: [
      { key: "municipio", label: "Municipio", type: "text", default: "Tubará" },
      { key: "departamento", label: "Departamento", type: "text", default: "Atlántico" },
      { key: "nit_prestador", label: "NIT del prestador", type: "text", default: "" },
      { key: "periodo", label: "Período (YYYY-MM)", type: "text", default: "2026-06" },
      { key: "servicio", label: "Servicio", type: "select", options: SERVICIO, default: "acueducto" },
      { key: "suscriptores_totales", label: "Suscriptores totales", type: "number", default: 3200 },
      { key: "estrato_1", label: "Suscriptores estrato 1", type: "number", default: 900 },
      { key: "estrato_2", label: "Suscriptores estrato 2", type: "number", default: 1400 },
      { key: "estrato_3", label: "Suscriptores estrato 3", type: "number", default: 700 },
      { key: "estrato_4", label: "Suscriptores estrato 4", type: "number", default: 150 },
      { key: "estrato_5", label: "Suscriptores estrato 5", type: "number", default: 30 },
      { key: "estrato_6", label: "Suscriptores estrato 6", type: "number", default: 20 },
      { key: "volumen_producido_m3", label: "Volumen producido en el período (m³)", type: "number", default: 42000 },
      { key: "volumen_facturado_m3", label: "Volumen facturado (m³)", type: "number", default: 31500 },
      { key: "recaudo_total_cop", label: "Recaudo total (COP)", type: "number", default: 45000000 },
      { key: "irca_promedio", label: "IRCA promedio (0–100)", type: "number", required: false },
      { key: "muestras_tomadas", label: "Muestras tomadas", type: "number", required: false },
      { key: "muestras_no_conformes", label: "Muestras no conformes", type: "number", required: false },
      { key: "tarifa_cargo_fijo_estrato3", label: "Tarifa cargo fijo estrato 3 ($/mes)", type: "number", default: 8500 },
      { key: "tarifa_cargo_consumo_basico_estrato3", label: "Tarifa cargo consumo básico estrato 3 ($/m³)", type: "number", default: 3200 },
    ],
    transform: (raw) => {
      const suscriptores_por_estrato: Record<string, number> = {
        "1": Number(raw.estrato_1 || 0),
        "2": Number(raw.estrato_2 || 0),
        "3": Number(raw.estrato_3 || 0),
        "4": Number(raw.estrato_4 || 0),
        "5": Number(raw.estrato_5 || 0),
        "6": Number(raw.estrato_6 || 0),
      };
      const { estrato_1, estrato_2, estrato_3, estrato_4, estrato_5, estrato_6, ...rest } = raw;
      void estrato_1; void estrato_2; void estrato_3; void estrato_4; void estrato_5; void estrato_6;
      return { ...rest, suscriptores_por_estrato };
    },
  },
];
