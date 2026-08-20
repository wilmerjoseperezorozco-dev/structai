/**
 * Diagnóstico de vulnerabilidad sísmica para autoconstrucción.
 *
 * Contexto (2026-08-19/20): terremoto real M7.4 en Colombia el 10-ago-2026
 * (287+ fallecidos). Expertos coincidieron esa misma semana en que el daño
 * se agravó por informalidad constructiva (40-60% de la vivienda en
 * Colombia es autoconstruida) y falta de estudios de suelo — no por un
 * repunte anómalo de actividad sísmica (USGS: dentro de rango normal).
 *
 * Este NO es un peritaje estructural. Es una herramienta de tamizaje
 * (screening) en lenguaje sencillo para alguien SIN ingeniero, basada en
 * los factores de vulnerabilidad más documentados en colapsos reales:
 * falta de confinamiento, piso blando/irregular, ampliaciones sin
 * ingeniería, mal suelo, deterioro visible, falta de dirección técnica.
 * Cada pregunta evita afirmar coeficientes o fórmulas — son señales
 * observables por una persona sin formación técnica, no cálculos.
 *
 * Puntaje: 1 punto por respuesta riesgosa. Las preguntas marcadas
 * `critica: true` fuerzan como mínimo el nivel "Alto" aunque el puntaje
 * total sea bajo — hay factores (piso blando, sin confinamiento) que por
 * sí solos son causa documentada de colapso, promediarlos con el resto
 * diluiría una señal que no debería diluirse.
 */

export type RespuestaPregunta = "si" | "no" | "no_se";

export interface Pregunta {
  id: string;
  categoria: string;
  texto: string;
  ayuda?: string;
  /** Cuál respuesta suma riesgo. La mayoría es "si", algunas están invertidas. */
  respuestaRiesgosa: RespuestaPregunta;
  /** "no_se" también cuenta como riesgo cuando la pregunta es sobre algo que
   * debería saberse si se hizo bien (ej. estudio de suelos) */
  noSeEsRiesgo?: boolean;
  critica?: boolean;
}

export const PREGUNTAS: Pregunta[] = [
  {
    id: "confinamiento",
    categoria: "Estructura",
    texto: "¿Tu casa tiene columnas y vigas de concreto reforzado en las esquinas y cruces de las paredes?",
    ayuda: "Si no sabes, mira si en las esquinas hay una franja de concreto distinta al bloque/ladrillo — eso es el confinamiento.",
    respuestaRiesgosa: "no",
    noSeEsRiesgo: true,
    critica: true,
  },
  {
    id: "piso_blando",
    categoria: "Estructura",
    texto: "¿El primer piso tiene un local, garaje o espacio muy abierto (pocas paredes), y los pisos de arriba son más cerrados y pesados?",
    ayuda: "Esto se llama \"piso blando\" — es una de las causas más comunes de colapso total en terremotos.",
    respuestaRiesgosa: "si",
    critica: true,
  },
  {
    id: "ampliaciones",
    categoria: "Estructura",
    texto: "¿Se han construido pisos o cuartos adicionales después de que la casa ya estaba hecha, sin que un ingeniero revisara si la base los aguanta?",
    respuestaRiesgosa: "si",
  },
  {
    id: "irregularidad",
    categoria: "Estructura",
    texto: "¿La forma de la casa es muy irregular (en L, con partes que sobresalen mucho, patios internos grandes)?",
    respuestaRiesgosa: "si",
  },
  {
    id: "estudio_suelo",
    categoria: "Terreno",
    texto: "¿Sabes si se hizo un estudio de suelos antes de construir?",
    respuestaRiesgosa: "no",
    noSeEsRiesgo: true,
  },
  {
    id: "ubicacion_riesgo",
    categoria: "Terreno",
    texto: "¿La casa está en una ladera/pendiente, sobre terreno de relleno, o muy cerca de un caño, quebrada o arroyo?",
    respuestaRiesgosa: "si",
  },
  {
    id: "deterioro",
    categoria: "Estado actual",
    texto: "¿Hay grietas visibles en paredes o columnas, o varillas de acero oxidadas y expuestas?",
    respuestaRiesgosa: "si",
  },
  {
    id: "materiales",
    categoria: "Estado actual",
    texto: "¿Hasta donde sabes, se usó arena de mar/playa (no de río) o una mezcla muy pobre de cemento en la construcción?",
    ayuda: "La arena de mar acelera la oxidación del acero por dentro del concreto — un problema real y conocido en zonas costeras.",
    respuestaRiesgosa: "si",
    noSeEsRiesgo: false,
  },
  {
    id: "direccion_tecnica",
    categoria: "Cómo se construyó",
    texto: "¿La construcción tuvo un maestro de obra con experiencia real, o un ingeniero/arquitecto a cargo?",
    respuestaRiesgosa: "no",
    noSeEsRiesgo: true,
  },
  {
    id: "antiguedad_sin_revision",
    categoria: "Cómo se construyó",
    texto: "¿La casa tiene más de 20 años y nunca le han hecho una revisión estructural?",
    respuestaRiesgosa: "si",
  },
];

export type NivelRiesgo = "bajo" | "medio" | "alto" | "critico";

export interface ResultadoDiagnostico {
  puntaje: number;
  puntajeMaximo: number;
  nivel: NivelRiesgo;
  huboFactorCritico: boolean;
  respuestasRiesgosas: string[]; // ids de preguntas que sumaron riesgo
}

export function calcularResultado(respuestas: Record<string, RespuestaPregunta>): ResultadoDiagnostico {
  let puntaje = 0;
  let huboFactorCritico = false;
  const respuestasRiesgosas: string[] = [];

  for (const p of PREGUNTAS) {
    const r = respuestas[p.id];
    if (!r) continue;
    const esRiesgo = r === p.respuestaRiesgosa || (r === "no_se" && p.noSeEsRiesgo === true);
    if (esRiesgo) {
      puntaje += 1;
      respuestasRiesgosas.push(p.id);
      if (p.critica) huboFactorCritico = true;
    }
  }

  let nivel: NivelRiesgo;
  if (huboFactorCritico) {
    nivel = puntaje >= 5 ? "critico" : "alto";
  } else if (puntaje <= 1) {
    nivel = "bajo";
  } else if (puntaje <= 3) {
    nivel = "medio";
  } else if (puntaje <= 5) {
    nivel = "alto";
  } else {
    nivel = "critico";
  }

  return {
    puntaje,
    puntajeMaximo: PREGUNTAS.length,
    nivel,
    huboFactorCritico,
    respuestasRiesgosas,
  };
}

export const NIVEL_INFO: Record<NivelRiesgo, { label: string; color: string; bg: string; border: string; mensaje: string; acciones: string[] }> = {
  bajo: {
    label: "Riesgo bajo",
    color: "text-green-300",
    bg: "bg-green-950/30",
    border: "border-green-700",
    mensaje: "No se identificaron señales de alarma en este tamizaje. Eso NO significa que tu casa esté certificada como segura — solo que no aparecieron las señales más comunes de vulnerabilidad severa.",
    acciones: [
      "Igual conviene una revisión visual profesional cada pocos años, sobre todo tras un sismo fuerte.",
      "Si vas a ampliar o modificar la casa, hazlo siempre con respaldo de un ingeniero.",
    ],
  },
  medio: {
    label: "Riesgo medio",
    color: "text-amber-300",
    bg: "bg-amber-950/30",
    border: "border-amber-700",
    mensaje: "Aparecieron algunas señales de vulnerabilidad. Vale la pena que un profesional revise tu vivienda con más detalle, sin que sea necesariamente urgente.",
    acciones: [
      "Busca una evaluación estructural con un ingeniero civil matriculado.",
      "Prioriza corregir lo que identificaste como riesgo en las preguntas de \"Estado actual\" (grietas, óxido).",
    ],
  },
  alto: {
    label: "Riesgo alto",
    color: "text-orange-300",
    bg: "bg-orange-950/30",
    border: "border-orange-700",
    mensaje: "Se identificó al menos un factor de alto riesgo documentado en colapsos reales (falta de confinamiento y/o piso blando). Esto merece atención seria, no solo curiosidad.",
    acciones: [
      "Consigue una evaluación estructural presencial con un ingeniero civil lo antes posible — este diagnóstico no reemplaza esa visita.",
      "Mientras tanto, evita cargas adicionales (no construyas más pisos, no llenes de materiales pesados el techo).",
      "Si vives en zona de amenaza sísmica alta o intermedia, súmale urgencia a la revisión.",
    ],
  },
  critico: {
    label: "Riesgo crítico",
    color: "text-red-300",
    bg: "bg-red-950/40",
    border: "border-red-700",
    mensaje: "Se combinan varios factores de alto riesgo. Este es exactamente el patrón que los expertos señalaron como agravante en las viviendas más dañadas del terremoto de agosto de 2026.",
    acciones: [
      "Busca cuanto antes una evaluación estructural presencial con un ingeniero civil matriculado — no lo dejes para después.",
      "Si notas grietas nuevas creciendo, sonidos extraños en la estructura, o inclinación visible, considera desalojar mientras se evalúa.",
      "Contacta a la oficina de gestión del riesgo de tu municipio para orientación gratuita si no puedes costear una evaluación privada.",
    ],
  },
};
