/**
 * Gerencia — especificación de módulos: EVM (PMBOK) + ML predictivo sobre series de avance.
 * Mismo enfoque data-driven que components/geopot/moduleSpecs.ts.
 */
import {
  calcularSnapshot,
  analizarPortafolio,
  calcularRiesgo,
  calcularForecast,
  calcularFechaTermino,
  detectarAnomalias,
  calcularCorrelacion,
} from "@/lib/gerencia-api";

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
  grupo: "EVM" | "Predicción ML";
  descripcion: string;
  normaRef: string;
  fields: FieldSpec[];
  submit: (payload: Record<string, unknown>) => Promise<Record<string, unknown>>;
  transform?: (raw: Record<string, string>) => Record<string, unknown>;
}

const KPI_OPTIONS: FieldOption[] = [
  { value: "cpi", label: "CPI — Costo" },
  { value: "spi", label: "SPI — Cronograma" },
  { value: "qpi", label: "QPI — Calidad" },
  { value: "ppi", label: "PPI — Productividad" },
];

const SNAPSHOTS_DEFAULT =
  "Ene,80000,75000,82000,95,10,10,1\n" +
  "Feb,160000,150000,168000,92,10,9,2\n" +
  "Mar,240000,220000,250000,90,10,9,3\n" +
  "Abr,320000,290000,330000,88,10,8,4";

const SNAPSHOTS_HELP =
  "Una línea por período: period,pv,ev,ac,quality_pct,resources_planned,resources_actual,incidents";

/** Parsea "period,pv,ev,ac,quality_pct,resources_planned,resources_actual,incidents" por línea. */
function parseSnapshots(text: string): Record<string, unknown>[] {
  return text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => {
      const parts = l.split(",").map((v) => v.trim());
      const [period, pv, ev, ac, quality_pct, resources_planned, resources_actual, incidents] = parts;
      return {
        period,
        pv: Number(pv),
        ev: Number(ev),
        ac: Number(ac),
        quality_pct: Number(quality_pct),
        resources_planned: Number(resources_planned),
        resources_actual: Number(resources_actual),
        incidents: Number(incidents || 0),
      };
    })
    .filter((s) => s.period && Number.isFinite(s.pv) && Number.isFinite(s.ev) && Number.isFinite(s.ac));
}

const PROJECT_FIELDS: FieldSpec[] = [
  { key: "id", label: "ID de obra", type: "text", default: "OBRA-A" },
  { key: "name", label: "Nombre de la obra", type: "text", default: "Puente Río Grande" },
  { key: "bac", label: "BAC — Presupuesto total (Budget at Completion)", type: "number", default: 1000000 },
  { key: "duration_months", label: "Duración planificada (meses)", type: "number", default: 12 },
  { key: "snapshots", label: "Snapshots por período", type: "pairs", default: SNAPSHOTS_DEFAULT, help: SNAPSHOTS_HELP },
];

function buildProject(raw: Record<string, string>) {
  return {
    id: raw.id,
    name: raw.name,
    bac: Number(raw.bac),
    duration_months: Number(raw.duration_months),
    snapshots: parseSnapshots(raw.snapshots || ""),
  };
}

export const GERENCIA_MODULES: ModuleSpec[] = [
  {
    id: "evm-snapshot",
    label: "KPIs de un período",
    grupo: "EVM",
    descripcion: "CPI, SPI, QPI, PPI, SV, CV, TCPI y EAC de un único snapshot de avance de obra.",
    normaRef: "PMBOK 7ª ed. — Earned Value Management",
    submit: calcularSnapshot,
    fields: [
      { key: "bac", label: "BAC — Presupuesto total", type: "number", default: 1000000 },
      { key: "period", label: "Período", type: "text", default: "Ene" },
      { key: "pv", label: "PV — Valor planificado", type: "number", default: 80000 },
      { key: "ev", label: "EV — Valor ganado", type: "number", default: 75000 },
      { key: "ac", label: "AC — Costo real", type: "number", default: 82000 },
      { key: "quality_pct", label: "% Calidad del período", type: "number", default: 95 },
      { key: "resources_planned", label: "Recursos planificados", type: "number", default: 10 },
      { key: "resources_actual", label: "Recursos reales", type: "number", default: 10 },
      { key: "incidents", label: "Incidentes", type: "number", default: 1 },
    ],
    transform: (raw) => ({
      bac: Number(raw.bac),
      snapshot: {
        period: raw.period,
        pv: Number(raw.pv),
        ev: Number(raw.ev),
        ac: Number(raw.ac),
        quality_pct: Number(raw.quality_pct),
        resources_planned: Number(raw.resources_planned),
        resources_actual: Number(raw.resources_actual),
        incidents: Number(raw.incidents || 0),
      },
    }),
  },
  {
    id: "evm-portafolio",
    label: "Trazabilidad de portafolio",
    grupo: "EVM",
    descripcion: "Rankings, agregados de portafolio y alertas automáticas (CPI/SPI/TCPI/QPI críticos) a partir de la serie histórica de la obra.",
    normaRef: "PMBOK 7ª ed.",
    submit: analizarPortafolio,
    fields: PROJECT_FIELDS,
    transform: (raw) => ({ projects: [buildProject(raw)] }),
  },
  {
    id: "ml-riesgo",
    label: "Score de riesgo",
    grupo: "Predicción ML",
    descripcion: "Score compuesto 0-100 basado en tendencias de CPI, SPI, QPI y PPI (regresión lineal + penalización por umbral).",
    normaRef: "Modelo estadístico propio (sin scikit-learn)",
    submit: calcularRiesgo,
    fields: PROJECT_FIELDS,
    transform: (raw) => ({ project: buildProject(raw) }),
  },
  {
    id: "ml-forecast",
    label: "Forecast de KPIs",
    grupo: "Predicción ML",
    descripcion: "Proyección de CPI/SPI/QPI/PPI para los próximos períodos por regresión lineal, con R² de ajuste.",
    normaRef: "Regresión lineal simple",
    submit: calcularForecast,
    fields: [...PROJECT_FIELDS, { key: "n_ahead", label: "Períodos a proyectar", type: "number", default: 3 }],
    transform: (raw) => ({ project: buildProject(raw), n_ahead: Number(raw.n_ahead || 3) }),
  },
  {
    id: "ml-fecha-termino",
    label: "Fecha de término estimada",
    grupo: "Predicción ML",
    descripcion: "Duración revisada, atraso estimado y probabilidad de término a tiempo según el SPI actual.",
    normaRef: "Earned Schedule (Lipke, 2009)",
    submit: calcularFechaTermino,
    fields: PROJECT_FIELDS,
    transform: (raw) => ({ project: buildProject(raw) }),
  },
  {
    id: "ml-anomalias",
    label: "Detección de anomalías",
    grupo: "Predicción ML",
    descripcion: "Detecta períodos anómalos en la serie de un KPI mediante z-score.",
    normaRef: "Z-score (|z| > umbral)",
    submit: detectarAnomalias,
    fields: [
      ...PROJECT_FIELDS,
      { key: "kpi", label: "KPI a analizar", type: "select", options: KPI_OPTIONS, default: "cpi" },
      { key: "anomaly_threshold", label: "Umbral de z-score", type: "number", default: 2.0 },
    ],
    transform: (raw) => ({
      project: buildProject(raw),
      kpi: raw.kpi,
      anomaly_threshold: Number(raw.anomaly_threshold || 2.0),
    }),
  },
  {
    id: "ml-correlacion",
    label: "Correlación entre KPIs",
    grupo: "Predicción ML",
    descripcion: "Matriz de correlación de Pearson entre CPI, SPI, QPI y PPI (mínimo 3 períodos).",
    normaRef: "Coeficiente de correlación de Pearson",
    submit: calcularCorrelacion,
    fields: PROJECT_FIELDS,
    transform: (raw) => ({ project: buildProject(raw) }),
  },
];
