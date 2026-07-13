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
    id: "A", letra: "A", nombre: "Requisitos Generales de Diseño",
    descripcion: "Alcance, definiciones, clasificación de edificaciones y requisitos mínimos",
    color: "brand",
    capitulos: [
      { id: "A.1", codigo: "A.1", nombre: "Generalidades y alcance", articulos_count: 12 },
      { id: "A.2", codigo: "A.2", nombre: "Clasificación de edificaciones", articulos_count: 8 },
      { id: "A.3", codigo: "A.3", nombre: "Criterios de diseño", articulos_count: 15 },
    ],
  },
  {
    id: "B", letra: "B", nombre: "Cargas",
    descripcion: "Cargas muertas, vivas, de viento, de sismo y combinaciones",
    color: "orange",
    capitulos: [
      { id: "B.1", codigo: "B.1", nombre: "Cargas muertas", articulos_count: 10 },
      { id: "B.2", codigo: "B.2", nombre: "Cargas vivas", articulos_count: 14 },
      { id: "B.3", codigo: "B.3", nombre: "Cargas de viento", articulos_count: 20 },
      { id: "B.4", codigo: "B.4", nombre: "Cargas sísmicas", articulos_count: 30 },
    ],
  },
  {
    id: "C", letra: "C", nombre: "Concreto Estructural",
    descripcion: "Diseño y construcción de estructuras de concreto reforzado",
    color: "slate",
    capitulos: [
      { id: "C.1", codigo: "C.1", nombre: "Generalidades concreto", articulos_count: 18 },
      { id: "C.2", codigo: "C.2", nombre: "Resistencia y servicio", articulos_count: 22 },
      { id: "C.3", codigo: "C.3", nombre: "Flexión y carga axial", articulos_count: 25 },
      { id: "C.4", codigo: "C.4", nombre: "Cortante y torsión", articulos_count: 20 },
      { id: "C.5", codigo: "C.5", nombre: "Desarrollo y traslapes", articulos_count: 15 },
    ],
  },
  {
    id: "D", letra: "D", nombre: "Mampostería Estructural",
    descripcion: "Diseño de muros y elementos de mampostería confinada y reforzada",
    color: "amber",
    capitulos: [
      { id: "D.1", codigo: "D.1", nombre: "Materiales mampostería", articulos_count: 12 },
      { id: "D.2", codigo: "D.2", nombre: "Mampostería confinada", articulos_count: 18 },
      { id: "D.3", codigo: "D.3", nombre: "Mampostería reforzada", articulos_count: 16 },
    ],
  },
  {
    id: "E", letra: "E", nombre: "Casas de 1 y 2 Pisos",
    descripcion: "Requisitos simplificados para vivienda de uno y dos pisos",
    color: "green",
    capitulos: [
      { id: "E.1", codigo: "E.1", nombre: "Alcance y definiciones", articulos_count: 8 },
      { id: "E.2", codigo: "E.2", nombre: "Diseño simplificado", articulos_count: 20 },
      { id: "E.3", codigo: "E.3", nombre: "Requisitos constructivos", articulos_count: 14 },
    ],
  },
  {
    id: "F", letra: "F", nombre: "Estructuras Metálicas",
    descripcion: "Diseño de estructuras de acero laminado y conformado en frío",
    color: "cyan",
    capitulos: [
      { id: "F.1", codigo: "F.1", nombre: "Materiales acero", articulos_count: 10 },
      { id: "F.2", codigo: "F.2", nombre: "Miembros en tensión", articulos_count: 12 },
      { id: "F.3", codigo: "F.3", nombre: "Miembros en compresión", articulos_count: 14 },
      { id: "F.4", codigo: "F.4", nombre: "Conexiones", articulos_count: 20 },
    ],
  },
  {
    id: "G", letra: "G", nombre: "Estructuras de Madera",
    descripcion: "Diseño y construcción con madera estructural",
    color: "yellow",
    capitulos: [
      { id: "G.1", codigo: "G.1", nombre: "Propiedades de la madera", articulos_count: 10 },
      { id: "G.2", codigo: "G.2", nombre: "Diseño de elementos", articulos_count: 16 },
    ],
  },
  {
    id: "H", letra: "H", nombre: "Estudios Geotécnicos",
    descripcion: "Cimentaciones, taludes, rellenos y licuación de suelos",
    color: "brown",
    capitulos: [
      { id: "H.1", codigo: "H.1", nombre: "Reconocimiento del suelo", articulos_count: 12 },
      { id: "H.2", codigo: "H.2", nombre: "Cimentaciones superficiales", articulos_count: 18 },
      { id: "H.3", codigo: "H.3", nombre: "Cimentaciones profundas", articulos_count: 14 },
      { id: "H.4", codigo: "H.4", nombre: "Estabilidad de taludes", articulos_count: 10 },
    ],
  },
  {
    id: "I", letra: "I", nombre: "Supervisión Técnica",
    descripcion: "Responsabilidades, licencias y control de calidad en obra",
    color: "purple",
    capitulos: [
      { id: "I.1", codigo: "I.1", nombre: "Supervisor técnico", articulos_count: 8 },
      { id: "I.2", codigo: "I.2", nombre: "Control de calidad", articulos_count: 12 },
    ],
  },
  {
    id: "J", letra: "J", nombre: "Requisitos de Protección contra Incendio",
    descripcion: "Resistencia al fuego, compartimentación y evacuación",
    color: "red",
    capitulos: [
      { id: "J.1", codigo: "J.1", nombre: "Resistencia al fuego", articulos_count: 15 },
      { id: "J.2", codigo: "J.2", nombre: "Compartimentación", articulos_count: 10 },
      { id: "J.3", codigo: "J.3", nombre: "Evacuación", articulos_count: 12 },
    ],
  },
  {
    id: "K", letra: "K", nombre: "Requisitos Complementarios",
    descripcion: "Instalaciones, accesibilidad y disposiciones especiales",
    color: "teal",
    capitulos: [
      { id: "K.1", codigo: "K.1", nombre: "Instalaciones y redes", articulos_count: 10 },
      { id: "K.2", codigo: "K.2", nombre: "Accesibilidad", articulos_count: 8 },
    ],
  },
];
