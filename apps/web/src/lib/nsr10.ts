// Catálogo de la NSR-10 para la pestaña de consulta rápida (/nsr10).
//
// IMPORTANTE: esta lista se reconstruyó el 2026-08-21 a partir de un conteo
// REAL contra Supabase (nsr10_chunks: capítulo/sección agrupados por
// numeral X.N real, ej. "SELECT substring(seccion from '^[A-Z]\.[0-9]+')
// ... GROUP BY"), no son cifras inventadas. La versión anterior tenía
// nombres de capítulo y conteos de "artículos" completamente fabricados
// (ej. decía que C.3 era "Flexión y carga axial" con 25 artículos — el C.3
// real es "Materiales" y el conteo no correspondía a nada cargado en la
// base). "fragmentos" = fragmentos verbatim indexados para ese numeral, no
// "artículos" en sentido estricto (un fragmento puede cubrir parte de un
// artículo o varios numerales cortos) — se etiqueta así a propósito para no
// prometer una granularidad que no se tiene.
//
// Si se reingesta contenido nuevo de NSR-10, actualizar esta lista con el
// mismo tipo de consulta contra nsr10_chunks en vez de editar a mano.

export interface TituloNSR {
  id: string;
  letra: string;
  nombre: string;
  descripcion: string;
  color: string;
  capitulos: CapituloNSR[];
}

export interface CapituloNSR {
  id: string;
  codigo: string;
  nombre: string;
  articulos_count: number;
}

export const TITULOS_NSR10: TituloNSR[] = [
  {
    id: "A", letra: "A", nombre: "Requisitos Generales de Diseño y Construcción Sismo Resistente",
    descripcion: "Zonas de amenaza sísmica, métodos de análisis, deriva, elementos no estructurales y evaluación de edificaciones existentes",
    color: "brand",
    capitulos: [
      { id: "A.1", codigo: "A.1", nombre: "Alcance y aplicabilidad de la NSR-10", articulos_count: 2 },
      { id: "A.2", codigo: "A.2", nombre: "Zonas de amenaza sísmica y efectos locales del suelo", articulos_count: 6 },
      { id: "A.3", codigo: "A.3", nombre: "Requisitos generales de diseño sismo resistente", articulos_count: 9 },
      { id: "A.4", codigo: "A.4", nombre: "Método de la fuerza horizontal equivalente", articulos_count: 5 },
      { id: "A.5", codigo: "A.5", nombre: "Método del análisis dinámico", articulos_count: 4 },
      { id: "A.6", codigo: "A.6", nombre: "Requisitos de la deriva", articulos_count: 6 },
      { id: "A.7", codigo: "A.7", nombre: "Métodos de análisis sísmico permitidos", articulos_count: 1 },
      { id: "A.8", codigo: "A.8", nombre: "Supervisión técnica según grupo de uso", articulos_count: 1 },
      { id: "A.9", codigo: "A.9", nombre: "Elementos no estructurales", articulos_count: 3 },
      { id: "A.10", codigo: "A.10", nombre: "Evaluación e intervención de edificaciones existentes", articulos_count: 2 },
      { id: "A.x", codigo: "A", nombre: "Otros fragmentos verbatim", articulos_count: 5 },
    ],
  },
  {
    id: "B", letra: "B", nombre: "Cargas",
    descripcion: "Combinaciones de carga, cargas muertas y vivas, empuje de tierra y fuerzas de viento (método simplificado, analítico y túnel de viento)",
    color: "orange",
    capitulos: [
      { id: "B.1", codigo: "B.1", nombre: "Alcance y requisitos generales", articulos_count: 2 },
      { id: "B.2", codigo: "B.2", nombre: "Combinaciones de carga mayoradas", articulos_count: 3 },
      { id: "B.3", codigo: "B.3", nombre: "Cargas muertas de elementos no estructurales", articulos_count: 2 },
      { id: "B.4", codigo: "B.4", nombre: "Cargas vivas: impacto y reducción por área", articulos_count: 3 },
      { id: "B.5", codigo: "B.5", nombre: "Empuje de tierra y presión hidrostática", articulos_count: 1 },
      { id: "B.6", codigo: "B.6", nombre: "Fuerzas de viento (simplificado, analítico y túnel de viento)", articulos_count: 20 },
    ],
  },
  {
    id: "C", letra: "C", nombre: "Concreto Estructural",
    descripcion: "Materiales, durabilidad, calidad del concreto, flexión y carga axial, cortante, desarrollo del refuerzo y diseño sismo resistente",
    color: "slate",
    capitulos: [
      { id: "C.1", codigo: "C.1", nombre: "Alcance del Título C", articulos_count: 1 },
      { id: "C.3", codigo: "C.3", nombre: "Materiales — acero de refuerzo (C.3.5)", articulos_count: 1 },
      { id: "C.4", codigo: "C.4", nombre: "Requisitos de durabilidad", articulos_count: 1 },
      { id: "C.5", codigo: "C.5", nombre: "Calidad del concreto", articulos_count: 1 },
      { id: "C.7", codigo: "C.7", nombre: "Detalles del refuerzo", articulos_count: 1 },
      { id: "C.9", codigo: "C.9", nombre: "Requisitos de resistencia y funcionamiento", articulos_count: 1 },
      { id: "C.10", codigo: "C.10", nombre: "Flexión y cargas axiales", articulos_count: 2 },
      { id: "C.11", codigo: "C.11", nombre: "Cortante y torsión", articulos_count: 3 },
      { id: "C.12", codigo: "C.12", nombre: "Desarrollo y longitudes del refuerzo", articulos_count: 2 },
      { id: "C.21", codigo: "C.21", nombre: "Requisitos de diseño sismo resistente", articulos_count: 1 },
      { id: "C.x", codigo: "C", nombre: "Otros fragmentos verbatim", articulos_count: 1 },
    ],
  },
  {
    id: "D", letra: "D", nombre: "Mampostería Estructural",
    descripcion: "Clasificación, determinación de f'm, factores de reducción, diseño a flexión y requisitos geométricos de mampostería confinada y reforzada",
    color: "amber",
    capitulos: [
      { id: "D.1", codigo: "D.1", nombre: "Requisitos generales", articulos_count: 24 },
      { id: "D.2", codigo: "D.2", nombre: "Clasificación de la mampostería y usos permitidos", articulos_count: 34 },
      { id: "D.3", codigo: "D.3", nombre: "Determinación de f'm y evaluación de la mampostería", articulos_count: 49 },
      { id: "D.4", codigo: "D.4", nombre: "Factores de reducción de resistencia φ", articulos_count: 3 },
      { id: "D.5", codigo: "D.5", nombre: "Diseño a flexión en mampostería reforzada", articulos_count: 3 },
      { id: "D.6", codigo: "D.6", nombre: "Requisitos geométricos — mampostería confinada", articulos_count: 3 },
      { id: "D.10", codigo: "D.10", nombre: "Rigidez lateral de muros diafragma", articulos_count: 1 },
    ],
  },
  {
    id: "E", letra: "E", nombre: "Casas de Uno y Dos Pisos",
    descripcion: "Requisitos simplificados para vivienda de mampostería confinada, incluyendo bahareque encementado (entrepisos y cubiertas)",
    color: "green",
    capitulos: [
      { id: "E.1", codigo: "E.1", nombre: "Integridad estructural", articulos_count: 7 },
      { id: "E.2", codigo: "E.2", nombre: "Estructuración de cimientos", articulos_count: 3 },
      { id: "E.3", codigo: "E.3", nombre: "Muros estructurales de mampostería confinada", articulos_count: 8 },
      { id: "E.4", codigo: "E.4", nombre: "Vigas de confinamiento", articulos_count: 5 },
      { id: "E.5", codigo: "E.5", nombre: "Losas de entrepiso", articulos_count: 2 },
      { id: "E.6", codigo: "E.6", nombre: "Recomendaciones de construcción — mampostería confinada", articulos_count: 2 },
      { id: "E.7", codigo: "E.7", nombre: "Bahareque encementado", articulos_count: 6 },
      { id: "E.8", codigo: "E.8", nombre: "Entrepisos en bahareque", articulos_count: 2 },
      { id: "E.9", codigo: "E.9", nombre: "Cubiertas en bahareque", articulos_count: 2 },
    ],
  },
  {
    id: "F", letra: "F", nombre: "Estructuras Metálicas",
    descripcion: "Diseño de estructuras de acero y aluminio (perfiles laminados, formados en frío) y provisiones sísmicas para acero",
    color: "cyan",
    capitulos: [
      { id: "F.1", codigo: "F.1", nombre: "Alcance y límites de aplicabilidad", articulos_count: 2 },
      { id: "F.2", codigo: "F.2", nombre: "Diseño de miembros a flexión", articulos_count: 7 },
      { id: "F.3", codigo: "F.3", nombre: "Provisiones sísmicas para acero", articulos_count: 15 },
      { id: "F.x", codigo: "F", nombre: "Otros fragmentos verbatim", articulos_count: 1 },
    ],
  },
  {
    id: "G", letra: "G", nombre: "Estructuras de Madera y Estructuras de Guadua",
    descripcion: "Diseño por esfuerzos admisibles, deflexiones, conexiones, arriostramiento y fabricación — el título con más contenido verbatim cargado",
    color: "yellow",
    capitulos: [
      { id: "G.1", codigo: "G.1", nombre: "Requisitos generales y materiales", articulos_count: 34 },
      { id: "G.2", codigo: "G.2", nombre: "Método de diseño por esfuerzos admisibles", articulos_count: 21 },
      { id: "G.3", codigo: "G.3", nombre: "Deflexiones admisibles", articulos_count: 55 },
      { id: "G.4", codigo: "G.4", nombre: "Miembros a tensión y flexo-tensión", articulos_count: 41 },
      { id: "G.5", codigo: "G.5", nombre: "Flexión biaxial y carga combinada", articulos_count: 2 },
      { id: "G.6", codigo: "G.6", nombre: "Factores de modificación y ajuste", articulos_count: 66 },
      { id: "G.7", codigo: "G.7", nombre: "Muros de corte — entramado y arriostramiento", articulos_count: 25 },
      { id: "G.8", codigo: "G.8", nombre: "Arriostramiento longitudinal", articulos_count: 15 },
      { id: "G.9", codigo: "G.9", nombre: "Conexiones y protección contra humedad", articulos_count: 8 },
      { id: "G.10", codigo: "G.10", nombre: "Secciones preferenciales", articulos_count: 3 },
      { id: "G.11", codigo: "G.11", nombre: "Fabricación, transporte e instalación", articulos_count: 37 },
      { id: "G.12", codigo: "G.12", nombre: "Módulos de elasticidad y coeficientes", articulos_count: 157 },
    ],
  },
  {
    id: "H", letra: "H", nombre: "Estudios Geotécnicos",
    descripcion: "Obligatoriedad de los estudios, clasificación de suelos, sondeos exploratorios, cimentaciones, pilotes y estabilidad de taludes",
    color: "brown",
    capitulos: [
      { id: "H.1", codigo: "H.1", nombre: "Introducción y obligatoriedad de los estudios", articulos_count: 12 },
      { id: "H.2", codigo: "H.2", nombre: "Factores de seguridad y clasificación de suelos", articulos_count: 28 },
      { id: "H.3", codigo: "H.3", nombre: "Categorías de construcción y sondeos exploratorios", articulos_count: 14 },
      { id: "H.4", codigo: "H.4", nombre: "Espectros de respuesta según tipo de suelo", articulos_count: 1 },
      { id: "H.5", codigo: "H.5", nombre: "Asentamientos en cimentaciones superficiales", articulos_count: 3 },
      { id: "H.6", codigo: "H.6", nombre: "Capacidad de pilotes", articulos_count: 1 },
      { id: "H.7", codigo: "H.7", nombre: "Estabilidad de taludes", articulos_count: 3 },
    ],
  },
  {
    id: "I", letra: "I", nombre: "Supervisión Técnica",
    descripcion: "Obligatoriedad, controles exigidos, idoneidad del supervisor técnico e informe final de supervisión",
    color: "purple",
    capitulos: [
      { id: "I.1", codigo: "I.1", nombre: "Generalidades y obligatoriedad", articulos_count: 12 },
      { id: "I.2", codigo: "I.2", nombre: "Controles exigidos al supervisor técnico", articulos_count: 16 },
      { id: "I.3", codigo: "I.3", nombre: "Idoneidad del supervisor técnico", articulos_count: 1 },
      { id: "I.4", codigo: "I.4", nombre: "Informe final de supervisión", articulos_count: 4 },
    ],
  },
  {
    id: "J", letra: "J", nombre: "Protección contra Incendios en Edificaciones",
    descripcion: "Grupos de ocupación, muros cortafuego, resistencia al fuego de elementos de acero y sistemas de extinción",
    color: "red",
    capitulos: [
      { id: "J.1", codigo: "J.1", nombre: "Propósito, alcance y grupos de ocupación", articulos_count: 2 },
      { id: "J.2", codigo: "J.2", nombre: "Muros cortafuego y evacuación", articulos_count: 6 },
      { id: "J.3", codigo: "J.3", nombre: "Resistencia al fuego de elementos de acero", articulos_count: 8 },
      { id: "J.4", codigo: "J.4", nombre: "Extinción de incendios por grupo de ocupación", articulos_count: 2 },
    ],
  },
  {
    id: "K", letra: "K", nombre: "Otros Requisitos Complementarios",
    descripcion: "Subgrupos de ocupación, protección de medios de evacuación y seguridad ante impacto humano en vidrierías",
    color: "teal",
    capitulos: [
      { id: "K.1", codigo: "K.1", nombre: "Propósito y alcance", articulos_count: 2 },
      { id: "K.2", codigo: "K.2", nombre: "Subgrupos de ocupación", articulos_count: 2 },
      { id: "K.3", codigo: "K.3", nombre: "Protección de medios de evacuación", articulos_count: 11 },
      { id: "K.4", codigo: "K.4", nombre: "Seguridad ante impacto humano en vidrierías", articulos_count: 4 },
    ],
  },
];

/** Total de fragmentos verbatim reales sumados de todos los títulos —
 * derivado de TITULOS_NSR10 en vez de un número aparte para que nunca se
 * desincronice si se actualiza la lista. */
export const TOTAL_FRAGMENTOS_NSR10 = TITULOS_NSR10.reduce(
  (acc, t) => acc + t.capitulos.reduce((sub, c) => sub + c.articulos_count, 0),
  0
);
