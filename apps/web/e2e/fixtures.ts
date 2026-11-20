import type { ConsultarResponse } from "../src/lib/api";

/**
 * Respuestas de /consultar con la forma exacta de ConsultarResponse
 * (src/lib/api.ts). Los textos fijos (aviso de responsabilidad, etiquetas de
 * dominio, aviso de vigencia) se copian del backend
 * (packages/construdata/rag_multi_norma.py: AVISO_RESPONSABILIDAD_PROFESIONAL,
 * MOTOR_LABEL, _advertencia_a4_modificado) para que la prueba falle si el
 * frontend deja de mostrar lo que el backend realmente manda.
 */

export const AVISO_RESPONSABILIDAD =
  "Este valor es una referencia técnica basada en la norma citada, no un " +
  "diseño aprobado para construcción. Todo cálculo o especificación que " +
  "vaya a obra debe ser revisado y firmado por un ingeniero matriculado " +
  "(COPNIA), conforme a la Ley 842 de 2003.";

const LABEL_GEOPOT = "GeoPot (sísmica NSR-10 y laboratorio de suelos/concreto/agregados)";
const LABEL_VIVIENDA =
  "Vulnerabilidad Vivienda (checklist AIS, Título E NSR-10, vivienda de mampostería 1-2 pisos)";
const LABEL_PRECIOS = "Precios de construcción (Barranquilla/Atlántico + INVIAS nacional, 140 provincias)";

const base = {
  normas_citadas: [] as string[],
  fuentes: [],
  chunks_usados: 0,
  latencia_ms: 1800,
  consulta_id: null,
};

export const sincelejo: ConsultarResponse = {
  ...base,
  dominio: "geopot",
  dominio_label: LABEL_GEOPOT,
  respuesta:
    "Para **Sincelejo (Sucre)** el Apéndice A-4 de la NSR-10 fija:\n\n" +
    "- **Aa = 0.10**\n- **Av = 0.15**\n- Zona de amenaza sísmica **Baja**\n\n" +
    "Fuente: servicio de amenaza sísmica del SGC y NSR-10 Apéndice A-4.",
  normas_citadas: ["NSR-10 Apéndice A-4", "NSR-10 A.2"],
  fuentes: [
    {
      norma: "NSR-10 Apéndice A-4",
      seccion: "A-4 Sucre",
      contenido_preview: "Sincelejo 70001 Aa 0.10 Av 0.15 Zona Baja",
      score: 0.91,
    },
    {
      norma: "NSR-10 A.2",
      seccion: "A.2.3",
      contenido_preview: "Zonas de amenaza sísmica: baja, intermedia y alta según Aa y Av.",
      score: 0.74,
    },
  ],
  chunks_usados: 2,
  aviso_responsabilidad: AVISO_RESPONSABILIDAD,
  consulta_id: "c0000000-0000-4000-8000-000000000001",
};

export const AVISO_VIGENCIA_SUPIA =
  "VIGENCIA NORMATIVA: el Apéndice A-4 de la NSR-10, modificado por el Decreto 1711 de 2021 " +
  "(anexo técnico, pág. 4 del PDF oficial de MinVivienda), fija para Supía (Caldas) Aa = 0.25, " +
  "Av = 0.3, Ae = 0.2, Ad = 0.1 (zona Alta). El servicio del SGC aún muestra Aa = 0.15, que es el " +
  "valor de 2010. Para diseño rige el valor vigente del reglamento.";

export const supia: ConsultarResponse = {
  ...base,
  dominio: "geopot",
  dominio_label: LABEL_GEOPOT,
  respuesta: "Para **Supía (Caldas)**: **Aa = 0.25**, Av = 0.30, zona **Alta**.\n\n" + AVISO_VIGENCIA_SUPIA,
  normas_citadas: ["NSR-10 Apéndice A-4", "Decreto 1711 de 2021"],
  fuentes: [
    {
      norma: "NSR-10 Apéndice A-4",
      seccion: "A-4 Caldas",
      contenido_preview: "Supía 17777 Aa 0.25 Av 0.30 Zona Alta (modificado por Decreto 1711 de 2021)",
      score: 0.88,
    },
  ],
  chunks_usados: 1,
  aviso_responsabilidad: AVISO_RESPONSABILIDAD,
};

export const vivienda: ConsultarResponse = {
  ...base,
  dominio: "vulnerabilidad_vivienda",
  dominio_label: LABEL_VIVIENDA,
  respuesta:
    "Para revisar la vulnerabilidad de una casa de mampostería de 2 pisos usa el **checklist AIS 2004**: " +
    "15 criterios, cada uno calificado BAJA / MEDIA / ALTA.\n\n" +
    "1. **Aspectos geométricos:** irregularidad en planta y en altura.\n" +
    "2. **Aspectos constructivos:** calidad de las juntas de mortero y de las piezas.\n" +
    "3. **Aspectos estructurales:** muros confinados, vigas de amarre, cubierta.\n\n" +
    "La clasificación final la calcula el endpoint /vulnerabilidad-vivienda/evaluar.",
  normas_citadas: ["AIS 2004", "NSR-10 Título E"],
  fuentes: [
    {
      norma: "AIS 2004",
      seccion: "Capítulo II",
      contenido_preview: "Manual de evaluación, rehabilitación y refuerzo de vivienda de bahareque y mampostería.",
      score: 0.82,
    },
  ],
  chunks_usados: 1,
  aviso_responsabilidad: AVISO_RESPONSABILIDAD,
};

export const abstencion: ConsultarResponse = {
  ...base,
  dominio: "normativa_general",
  dominio_label: "Normativa general (NSR-10 / NTC)",
  respuesta:
    "No encontré en las normas cargadas en StructAI un requisito que responda esta pregunta. " +
    "Prefiero no inventar un valor; revisa la norma original o reformula la pregunta.",
  aviso_responsabilidad: AVISO_RESPONSABILIDAD,
};

export const precios: ConsultarResponse = {
  ...base,
  dominio: "apu_precios",
  dominio_label: LABEL_PRECIOS,
  respuesta: "El **cemento gris** (bulto de 50 kg) en Barranquilla está en **$ 32.900**.",
  normas_citadas: ["Construdata 2026"],
  fuentes: [
    {
      norma: "Construdata 2026 — Barranquilla",
      seccion: "Cemento gris 50 kg — $ 32.900 / bulto",
      contenido_preview: "",
      score: 1,
    },
  ],
  chunks_usados: 1,
  aviso_responsabilidad: null,
};

export const linkPeligroso: ConsultarResponse = {
  ...base,
  dominio: "normativa_general",
  dominio_label: "Normativa general (NSR-10 / NTC)",
  respuesta: "Mira [este enlace](javascript:alert(1)) o la [norma oficial](https://www.minvivienda.gov.co).",
  aviso_responsabilidad: AVISO_RESPONSABILIDAD,
};
