"""
Inserta el núcleo verbatim real de NSR-10 Título H (Estudios Geotécnicos) y
Título I (Supervisión Técnica) en nsr10_chunks — mismo patrón y mismas
fuentes que Título D (ver insert_titulo_d_nucleo.py): texto oficial
extraído directamente de los PDF fuente en Google Drive (carpeta
METADATOS, nsr10_catalogo_maestro.json con rangos de página verificados
uno-a-uno), NO del "PDF" RAG+CAG sintético en packages/knowledge/nsr10/.

Núcleo insertado:
- H.1 (introducción: objetivo/alcance, obligatoriedad, referencias cruzadas)
- H.2 (definiciones: tipos de estudio, factores de seguridad con Tabla
  H.2.4-1, suelos cohesivos/no cohesivos, normas NTC/ASTM)
- H.3.1-H.3.2 (clasificación de unidades de construcción por categoría con
  Tabla H.3.1-1, número mínimo de sondeos con Tabla H.3.2-1)
- I.1 (generalidades: definiciones, obligatoriedad de la supervisión,
  cualidades del supervisor)
- I.2.1-I.2.4 (alcance de la supervisión técnica: documentación, alcance
  mínimo, controles exigidos)

H.3.3 en adelante y el resto de I (I.3-I.4) quedan para una siguiente ronda.

Uso: python scripts/ingesta/nsr10/insert_titulo_h_i_nucleo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CHUNKS = [
    # ── TÍTULO H — ESTUDIOS GEOTÉCNICOS ────────────────────────────────
    {
        "id": "NSR10-H-H_1",
        "capitulo": "NSR-10 Título H — Estudios Geotécnicos",
        "seccion": "H.1",
        "titulo": "Capítulo H.1 — Introducción (objetivo y alcance, obligatoriedad de los estudios geotécnicos, firma y responsabilidad)",
        "texto": """CAPÍTULO H.1 INTRODUCCIÓN

H.1.1 — REQUISITOS GENERALES

H.1.1.1 — OBJETIVO Y ALCANCE — Establecer criterios básicos para realizar estudios geotécnicos de edificaciones, basados en la investigación del subsuelo y las características arquitectónicas y estructurales de las edificaciones, con el fin de proveer las recomendaciones geotécnicas de diseño y construcción de excavaciones y rellenos, estructuras de contención, cimentaciones, rehabilitación o reforzamiento de edificaciones existentes y la definición de espectros de diseño sismorresistente, para soportar los efectos por sismos y por otras amenazas geotécnicas desfavorables.

H.1.1.2 — OBLIGATORIEDAD DE LOS ESTUDIOS GEOTÉCNICOS — Los estudios geotécnicos definitivos son obligatorios para todas las edificaciones urbanas y suburbanas de cualquier grupo de uso, y para las edificaciones en terrenos no aptos para el uso urbano de los grupos de uso II, III y IV definidos en el Título A de este Reglamento.

H.1.1.2.1 — Firma de los Estudios — Siguiendo los artículos 26 y 27 de la Ley 400 de 1997, modificada y adicionada por la Ley 1229 de 2008, los estudios geotécnicos para cimentaciones de edificaciones deben ser dirigidos y avalados por Ingenieros Civiles, titulados, matriculados en el COPNIA y con tarjeta profesional vigente. Todos los informes de los estudios geotécnicos y todos los planos de diseño y construcción que guarden alguna relación con estos estudios deben llevar la aprobación del ingeniero director del estudio. Los profesionales que realicen estos estudios deben poseer una experiencia mayor de cinco (5) años en diseño geotécnico de cimentaciones, contados a partir de la expedición de la tarjeta profesional, bajo la dirección de un profesional facultado para tal fin, o acreditar estudios de posgrado en geotecnia.

H.1.1.2.2 — Cumplimiento y Responsabilidad — El cumplimiento de estas Normas no exime al ingeniero responsable de la ejecución del estudio geotécnico de realizar todas las investigaciones y análisis necesarios para la identificación de las amenazas geotécnicas, la adecuada caracterización del subsuelo, y los análisis de estabilidad de la edificación, construcciones vecinas e infraestructura existente.

H.1.2 — REFERENCIAS — Las disposiciones del Título H se relacionan de manera directa con otras secciones del Reglamento que tratan aspectos geotécnicos: Título A (A.1.3.2 estudios geotécnicos, A.1.3.5 diseño de la cimentación, A.1.5.4 estudio geotécnico, A.2.4 efectos locales y tipos de perfil de suelo, A.7 interacción suelo-estructura, A.12 requisitos para edificaciones indispensables); Título B (B.1.2.1.3 fuerzas por deformaciones impuestas, B.2.3 combinaciones de carga para esfuerzos de trabajo, B.5 empuje de tierra y presión hidrostática); Título C (C.1.1.6 pilotes/pilas/cajones, C.1.1.7 losas sobre el terreno, C.15 cimentaciones, C.21.9 elementos de fundación, C.22.7 zapatas); Título D (D.4.4 requisitos constructivos para cimentaciones); Título E (E.2 cimentaciones, E.6.2 cimentaciones en mampostería confinada); Título I (I.1 generalidades de supervisión, I.2.3-I.2.4.6 alcance y control de ejecución, I.4 recomendaciones para el ejercicio de la supervisión técnica).""",
    },
    {
        "id": "NSR10-H-H_2_definiciones_tipos",
        "capitulo": "NSR-10 Título H — Estudios Geotécnicos",
        "seccion": "H.2.1 a H.2.3",
        "titulo": "Capítulo H.2 — Definiciones: estudio geotécnico preliminar y definitivo, contenido obligatorio, asesoría geotécnica, agua subterránea",
        "texto": """CAPÍTULO H.2 DEFINICIONES

H.2.1 — ESTUDIO GEOTÉCNICO. H.2.1.1 — DEFINICIÓN — Conjunto de actividades que comprenden el reconocimiento de campo, la investigación del subsuelo, los análisis y recomendaciones de ingeniería necesarios para el diseño y construcción de las obras en contacto con el suelo, garantizando un comportamiento adecuado de la edificación, protegiendo ante todo la integridad de las personas, además de proteger vías, instalaciones de servicios públicos, predios y construcciones vecinas. H.2.1.1.1 — Investigación del Subsuelo — Comprende el estudio del origen geológico, la exploración del subsuelo (apiques, trincheras, perforación y sondeo) y los ensayos de campo y laboratorio necesarios para identificar y clasificar los suelos y rocas y cuantificar sus características físico-mecánicas e hidráulicas. H.2.1.1.2 — Análisis y Recomendaciones — Interpretación técnica conducente a la caracterización del subsuelo y evaluación de mecanismos de falla y deformación, para suministrar los parámetros y recomendaciones de diseño y construcción de cimentación y contención.

H.2.2 — TIPOS DE ESTUDIOS. H.2.2.1 — ESTUDIO GEOTÉCNICO PRELIMINAR — Actividades para aproximarse a las características geotécnicas de un terreno: condiciones que limitan su aprovechamiento, problemas potenciales, criterios y parámetros generales para el proyecto. No es de presentación obligatoria, pero es recomendable para proyectos especiales o de magnitud considerable; no reemplaza al estudio geotécnico definitivo. H.2.2.2 — ESTUDIO GEOTÉCNICO DEFINITIVO — Trabajo para un proyecto específico donde el ingeniero geotecnista precisa las condiciones físico-mecánicas del subsuelo y las recomendaciones particulares de diseño y construcción, conforme a los Títulos A y H. Su presentación es obligatoria. H.2.2.2.1 — Contenido mínimo: (a) del proyecto (nombre, localización, objetivo, cargas — no se acepta como definitivo un estudio con cargas preliminares o solo cargas de gravedad); (b) del subsuelo (reconocimiento de campo, morfología, origen geológico, niveles freáticos); (c) de cada unidad geológica (identificación, espesor, parámetros de campo y laboratorio, según H.3, y análisis de suelos expansivos/dispersivos/colapsables); (d) de los análisis geotécnicos (criterios adoptados, estabilidad de taludes temporales, sistemas de contención); (e) de las recomendaciones de diseño (tipo de cimentación, presiones admisibles, asentamientos, perfil sísmico); (f) de las recomendaciones para protección de predios vecinos; (g) del sistema constructivo (documento de obligatoria elaboración por el geotecnista, verificado por la autoridad de licencias); (h) anexos (planos, registros de perforación, memoria de cálculo). H.2.2.3 — ASESORÍA GEOTÉCNICA EN DISEÑO Y CONSTRUCCIÓN — Para proyectos categoría Media, Alta o Especial, se requiere asesoría en la etapa de diseño por un ingeniero civil especialista en geotecnia, y acompañamiento de un Ingeniero Geotecnista durante la ejecución (niveles y estratos de cimentación, excavaciones, rellenos, estabilización de laderas), con acta de vecindad previa al inicio del proyecto. H.2.2.4 — ESTUDIO DE ESTABILIDAD DE LADERAS Y TALUDES — Debe incluirse en el estudio preliminar o definitivo, según H.5, considerando características geológicas, hidráulicas y de pendiente.

H.2.3 — AGUA SUBTERRÁNEA — El problema más frecuente en cimentaciones durante excavación y construcción es la existencia de agua subterránea libre o confinada, que produce disminución de las propiedades de resistencia además de flujo y erosión interna. Los estudios geotécnicos deben analizar agua libre, flujos potenciales de agua subterránea y presencia de paleocauces.""",
    },
    {
        "id": "NSR10-H-H_2_factores_seguridad",
        "capitulo": "NSR-10 Título H — Estudios Geotécnicos",
        "seccion": "H.2.4 a H.2.6",
        "titulo": "Capítulo H.2 — Factores de seguridad geotécnicos (fórmulas H.2.4-1 a H.2.4-7, Tabla H.2.4-1), clasificación de suelos, normas NTC/ASTM",
        "texto": """H.2.4 — FACTORES DE SEGURIDAD. H.2.4.1 — DEFINICIÓN — El Factor de Seguridad FS se define como la relación entre fuerzas resistentes FR y actuantes FA: FS = FR/FA (H.2.4-1), o en esfuerzos FS = τf/τA (H.2.4-2). En Ingeniería Geotécnica el Factor de Seguridad Básico FSB se define como FSB = τf/τA (H.2.4-3), donde τf es el esfuerzo cortante a la falla, expresado con el Criterio de Mohr-Coulomb: τf = c' + σ'·tan(φ') (H.2.4-4), con σ' = σ - UF (H.2.4-5) el esfuerzo normal efectivo. El esfuerzo cortante actuante τA (de trabajo o diseño τD): τA = [c' + σ'·tan(φ')] / FSB (H.2.4-6).

H.2.4.2 — COMPORTAMIENTO APARENTE — Para materiales cohesivos saturados sin fisuración, en términos de esfuerzos totales: c = Su (resistencia no drenada), φ = 0.0, τf = Su, τA = Su/FSBU (H.2.4-7), donde FSBU > FSB. Se permite emplear Su en análisis estáticos de cimentaciones superficiales/profundas y taludes temporales; NO se permite en empujes de tierras, relajación de esfuerzos, taludes permanentes, materiales no saturados/fisurados, ni análisis seudo-estáticos o dinámicos.

H.2.4.3 — VALORES DEL FACTOR DE SEGURIDAD GEOTÉCNICO BÁSICO — La selección debe justificarse considerando: magnitud de la obra, consecuencias de una posible falla, calidad de la información disponible. Los Factores de Seguridad Básicos no deben ser inferiores a los mínimos de la Tabla H.2.4-1 (cargas sin mayorar, R=1.0 para fuerzas sísmicas E); en ningún caso FSBM puede ser inferior a 1.00.

Tabla H.2.4-1 Factores de Seguridad Básicos Mínimos Directos: Carga Muerta + Carga Viva Normal — FSBM diseño 1.50, construcción 1.25; FSBUM diseño 1.80, construcción 1.40. Carga Muerta + Carga Viva Máxima — FSBM diseño 1.25, construcción 1.10; FSBUM diseño 1.40, construcción 1.15. Carga Muerta + Carga Viva Normal + Sismo de Diseño Seudo-estático — FSBM diseño 1.10, construcción 1.00 (no se permite FSBUM). Taludes condición estática con agua subterránea normal — FSBM diseño 1.50, construcción 1.25; FSBUM diseño 1.80, construcción 1.40. Taludes condición seudo-estática con agua subterránea normal — FSBM diseño 1.05, construcción 1.00 (no se permite FSBUM). Nota: los parámetros sísmicos seudo-estáticos de construcción son el 50% de los de diseño.

H.2.4.4 — FACTORES DE SEGURIDAD INDIRECTOS — Se derivan del FSB (factor de seguridad geotécnico real) y se especifican en los capítulos del Título H, pero deben demostrar que implican FSB iguales o superiores a los mínimos FSBM.

H.2.5 — SUELOS NO COHESIVOS/GRANULARES Y COHESIVOS — Según el Sistema de Clasificación Unificada de Suelos (SCUS): no cohesivos/granulares son GW, GP, GW-GM, GP-GM, GW-GC, GP-GC, SW, SP, SW-SM, SP-SM, SW-SC, SP-SC; y GM, GC, GM-GC, SM, SC, SM-SC cuando ≤30% del peso pasa el tamiz No. 200 y límite líquido wL≤30% e índice plástico IP≤10%. Suelos cohesivos son los que no cumplen esas condiciones.

H.2.6 — NORMAS TÉCNICAS. Normas NTC/ASTM que forman parte del Reglamento: NTC 1493/ASTM D4318 (límite plástico e IP), NTC 1494/ASTM D4318 (límite líquido), NTC 1495/ASTM D2216 (contenido de agua), NTC 1503/ASTM D427 (factores de contracción), NTC 1504/ASTM D2487 (clasificación de suelos), NTC 1522 (granulometría por tamizado), NTC 1528/ASTM D2167 (masa unitaria, balón de caucho), NTC 1667/ASTM D1556 (masa unitaria, cono de arena), NTC 1886/ASTM D2974 (humedad/ceniza/materia orgánica), NTC 1917/ASTM D3080 (corte directo), NTC 1936/ASTM D2664 (compresión triaxial en rocas), NTC 1967/ASTM D2435 (consolidación unidimensional), NTC 1974/ASTM D854 (densidad relativa de sólidos), NTC 2041/ASTM D2850 (compresión triaxial suelos cohesivos), NTC 2121/ASTM D1587 (tubos de pared delgada), NTC 2122/ASTM D1883 (relación de soporte CBR), NTC 4630 (límites de Atterberg); y ASTM D2166 (compresión inconfinada), D6066 (resistencia a penetración normalizada), D1143/D3689/D3966/D4945/D5882 (ensayos de pilotes bajo distintos tipos de carga).""",
    },
    {
        "id": "NSR10-H-H_3_clasificacion_sondeos",
        "capitulo": "NSR-10 Título H — Estudios Geotécnicos",
        "seccion": "H.3.1 a H.3.2",
        "titulo": "Capítulo H.3 — Clasificación de unidades de construcción por categoría (Tabla H.3.1-1) y número mínimo de sondeos exploratorios (Tabla H.3.2-1)",
        "texto": """CAPÍTULO H.3 CARACTERIZACIÓN GEOTÉCNICA DEL SUBSUELO. En este Capítulo se define el número y la profundidad mínima de sondeos exploratorios, dependiendo del tamaño de la edificación (unidad de construcción). El ingeniero geotecnista puede aumentar número o profundidad según condiciones locales y resultados iniciales.

H.3.1 — UNIDAD DE CONSTRUCCIÓN. Se define como: (a) una edificación en altura; (b) grupo de construcciones adosadas de máximo 40 m en planta; (c) cada zona separada por juntas de construcción; (d) construcciones adosadas de categoría baja hasta 80 m en planta; (e) cada fracción del proyecto con alturas, cargas o niveles de excavación diferentes. Proyectos que excedan estas longitudes deben fragmentarse en varias unidades de construcción.

H.3.1.1 — CLASIFICACIÓN POR CATEGORÍAS — Baja, Media, Alta y Especial, según número total de niveles (incluye sótanos, terrazas y pisos técnicos) y cargas máximas de servicio (carga muerta + carga viva por uso y ocupación). Se asigna la categoría más desfavorable de la Tabla H.3.1-1.

Tabla H.3.1-1 Clasificación de las unidades de construcción por categorías: Baja — hasta 3 niveles, cargas menores de 800 kN. Media — entre 4 y 10 niveles, cargas entre 801 y 4,000 kN. Alta — entre 11 y 20 niveles, cargas entre 4,001 y 8,000 kN. Especial — más de 20 niveles, cargas mayores de 8,000 kN.

H.3.2 — INVESTIGACIÓN DEL SUBSUELO PARA ESTUDIOS DEFINITIVOS. H.3.2.1 — INFORMACIÓN PREVIA — El ingeniero geotecnista debe recopilar y evaluar datos del sitio (geología, sismicidad, clima, vegetación, edificaciones vecinas) y dar fe de haber visitado el sitio. El ordenante del estudio debe suministrar la información del proyecto necesaria (topografía, tipo de edificación, sistema estructural, niveles de excavación, cargas, redes de servicio, edificaciones vecinas). H.3.2.2 — EXPLORACIÓN DE CAMPO — Apiques, trincheras, perforación o sondeo con muestreo, sondeos estáticos o dinámicos u otros procedimientos reconocidos, para caracterizar el perfil del subsuelo y obtener muestras para laboratorio. En macizos rocosos debe hacerse clasificación por métodos usuales (RMR, Q, GSI) y levantamiento de discontinuidades.

H.3.2.3 — NÚMERO MÍNIMO DE SONDEOS — Definido en la Tabla H.3.2-1 según categoría de la unidad de construcción.

Tabla H.3.2-1 Número mínimo de sondeos y profundidad por categoría: Baja — profundidad mínima 6 m, número mínimo 3 sondeos. Media — profundidad mínima 15 m, número mínimo 4 sondeos. Alta — profundidad mínima 25 m, número mínimo 4 sondeos. Especial — profundidad mínima 30 m, número mínimo 5 sondeos.

H.3.2.4 — CARACTERÍSTICAS Y DISTRIBUCIÓN DE LOS SONDEOS — (a) sondeos con recuperación de muestras: mínimo 50% del total; (b) muestreo cada metro en los primeros 5 m, luego en cada cambio de material o cada 1.5 m; (c) al menos 50% de los sondeos dentro de la proyección de las construcciones; (d) sondeos del estudio preliminar pueden incluirse en el definitivo si cumplen la misma calidad y especificaciones; (e) cobertura completa del área de la unidad de construcción y zonas afectadas por taludes u otras intervenciones; (f) en perforaciones en ríos o mar, reportar elevación referenciada a un datum, considerando mareas y niveles de agua.

H.3.2.5 — PROFUNDIDAD DE LOS SONDEOS — Al menos 50% de los sondeos debe alcanzar la profundidad de la Tabla H.3.2-1, considerada desde el nivel inferior de excavación (o desde el nivel original del terreno para rellenos), afectada por: (a) profundidad donde el incremento de esfuerzo vertical causado por la edificación sea el 10% del esfuerzo vertical en la interfaz suelo-cimentación; (b) 1.5 veces el ancho de la losa corrida de cimentación.""",
    },
    # ── TÍTULO I — SUPERVISIÓN TÉCNICA ──────────────────────────────────
    {
        "id": "NSR10-I-I_1",
        "capitulo": "NSR-10 Título I — Supervisión Técnica",
        "seccion": "I.1",
        "titulo": "Capítulo I.1 — Generalidades: definiciones (supervisor técnico, supervisión continua/itinerante), obligatoriedad de la supervisión técnica",
        "texto": """CAPÍTULO I.1 GENERALIDADES

I.1.1 — DEFINICIONES (transcritas de la Ley 400 de 1997 y la Ley 1229 de 2008, ampliando el Capítulo A.13). Constructor — Profesional (ingeniero civil, arquitecto, o constructor en arquitectura e ingeniería) bajo cuya responsabilidad se adelanta la construcción de la edificación. Diseñador estructural — Ingeniero civil facultado bajo cuya responsabilidad se realizan y firman el diseño y los planos estructurales. Diseñador de elementos no estructurales — Profesional facultado bajo cuya responsabilidad se realizan y firman el diseño y planos de los elementos no estructurales. Ingeniero geotecnista — Ingeniero civil que firma el estudio geotécnico y fija los parámetros de diseño de la cimentación y los efectos de amplificación sísmica por el tipo de suelo. Supervisión técnica — Verificación de la sujeción de la construcción de la estructura a los planos, diseños y especificaciones del diseñador estructural, y de los elementos no estructurales a los del diseñador respectivo, según el grado de desempeño sísmico requerido; puede ser realizada por el interventor cuando el propietario contrate una interventoría. Supervisión técnica continua — Todas las labores de construcción se supervisan de manera permanente. Supervisión técnica itinerante — El supervisor visita la obra con la frecuencia necesaria para verificar el avance adecuado. Supervisor técnico — Profesional (ingeniero civil, arquitecto o constructor de ingeniería/arquitectura) bajo cuya responsabilidad se realiza la supervisión técnica; puede delegar parte de las labores en personal técnico auxiliar bajo su dirección, y puede ser el mismo profesional que realiza la interventoría. Estructura — Ensamblaje de elementos diseñado para soportar cargas gravitacionales y resistir fuerzas horizontales.

I.1.2 — OBLIGATORIEDAD DE LA SUPERVISIÓN TÉCNICA. I.1.2.1 — Según el Artículo 18 del Título V de la Ley 400 de 1997, la construcción de la estructura de edificaciones con área construida mayor de 3000 m², cualquiera sea su uso, debe someterse a supervisión técnica. I.1.2.1.1 — Se excluyen las estructuras diseñadas y construidas según el Título E (casas de uno y dos pisos), siempre que sean menos de 15 unidades de vivienda. I.1.2.1.2 — El diseñador estructural o el ingeniero geotecnista pueden exigir supervisión técnica en edificaciones de cualquier área cuando la complejidad, procedimientos constructivos especiales o materiales lo hagan necesario, consignándolo en los planos o el estudio geotécnico; debe quedar explícito en la licencia de construcción. I.1.2.2 — Cuando no se requiera supervisión técnica, el Artículo 19 de la Ley 400 exige al constructor realizar los controles de calidad exigidos por la Ley y el Reglamento, con registro escrito de resultados. I.1.2.3 — Las edificaciones de atención a la comunidad (Grupos de Uso III y IV), independientemente de su área, deben someterse a supervisión técnica.

I.1.3 — ALCANCE DE LA SUPERVISIÓN TÉCNICA — El alcance mínimo y los controles mínimos exigidos están definidos en el Capítulo I.2.

I.1.4 — CUALIDADES DEL SUPERVISOR TÉCNICO — Debe ser un profesional que reúna las calidades exigidas en el Capítulo 5 del Título VI de la Ley 400 de 1997 y en la Ley 1229 de 2008.

I.1.5 — REGLAMENTACIONES ADICIONALES — El Capítulo I.4 indica el procedimiento recomendado para las labores de supervisión técnica, como guía mientras la Comisión Asesora Permanente del Régimen de Construcciones Sismo Resistentes las reglamenta formalmente.""",
    },
    {
        "id": "NSR10-I-I_2_documentacion_alcance",
        "capitulo": "NSR-10 Título I — Supervisión Técnica",
        "seccion": "I.2.1 a I.2.3",
        "titulo": "Capítulo I.2 — Documentación de las labores de supervisión (registro escrito obligatorio) y alcance mínimo de la supervisión técnica",
        "texto": """CAPÍTULO I.2 ALCANCE DE LA SUPERVISIÓN TÉCNICA

I.2.1 — GENERAL. I.2.1.1 — Este Capítulo fija el alcance mínimo y los controles mínimos de la supervisión técnica. I.2.1.2 — La supervisión técnica solo hace referencia a la construcción del sistema estructural y de los elementos no estructurales cubiertos por el Capítulo A.9.

I.2.2 — DOCUMENTACIÓN DE LAS LABORES DE SUPERVISIÓN TÉCNICA. I.2.2.1 — El supervisor técnico debe llevar registro escrito que incluya como mínimo: (a) las especificaciones de construcción y sus adendas; (b) el programa de control de calidad exigido, confirmado por propietario y constructor; (c) registro fotográfico de la construcción; (d) resultados e interpretación de ensayos de materiales; (e) toda la correspondencia derivada de la supervisión (notificaciones de deficiencias, correctivos ordenados, contestaciones del constructor); (f) conceptos de los diseñadores a las notificaciones; (g) todo documento que permita establecer que la construcción se realizó según lo requerido; (h) constancia del supervisor de que la construcción se realizó de acuerdo con el Reglamento y que las medidas correctivas llevaron la estructura al nivel de calidad requerido — suscrita también por el constructor y el titular de la licencia, y anexada a la solicitud de certificado de permiso de ocupación. I.2.2.2 — El supervisor debe entregar, al culminar sus labores, copia de los planos récord y el registro escrito a la autoridad de control urbano, al propietario y al constructor, conservándolo al menos cinco años. I.2.2.2.1 — En edificaciones bajo régimen de copropiedad, el titular de la licencia debe entregar copia de los documentos de supervisión a la copropiedad.

I.2.3 — ALCANCE DE LA SUPERVISIÓN TÉCNICA. I.2.3.1 — Debe cubrir como mínimo: (a) aprobación del programa de control de calidad propuesto por el constructor; (b) aprobación de los laboratorios de ensayo; (c) realizar los controles exigidos para los materiales estructurales (I.2.4); (d) aprobación de los procedimientos constructivos; (e) exigir a los diseñadores completar o corregir planos incompletos o con errores; (f) solicitar al geotecnista recomendaciones complementarias ante situaciones no previstas; (g) mantener actualizado el registro escrito; (h) velar por la mejor calidad de la obra; (i) prevenir por escrito al constructor sobre deficiencias y vigilar los correctivos; (j) recomendar la suspensión de labores cuando el constructor incumpla, informando a la autoridad competente; (k) rechazar partes de la estructura que no cumplan planos y especificaciones; (l) ordenar estudios para evaluar la seguridad de partes afectadas y las medidas correctivas; (m) recomendar la demolición si no es posible reparar; (n) expedir la constancia de I.2.2.1(h).""",
    },
    {
        "id": "NSR10-I-I_2_controles_exigidos",
        "capitulo": "NSR-10 Título I — Supervisión Técnica",
        "seccion": "I.2.4",
        "titulo": "Capítulo I.2 — Controles exigidos al supervisor técnico: control de planos, especificaciones y materiales (referencia cruzada por sistema estructural)",
        "texto": """I.2.4 — CONTROLES EXIGIDOS. I.2.4.1 — El supervisor técnico debe realizar, dentro del alcance de sus trabajos, los controles de I.2.4.2 a I.2.4.6.

I.2.4.2 — CONTROL DE PLANOS — Consiste en constatar la existencia de todas las indicaciones necesarias para realizar la construcción de forma adecuada, conforme a los planos del proyecto.

I.2.4.3 — CONTROL DE ESPECIFICACIONES — La construcción debe cumplir, como mínimo, las especificaciones técnicas del Reglamento para cada material cubierto, más las emanadas de la Comisión Asesora Permanente del Régimen de Construcciones Sismo Resistentes y las particulares de los diseñadores, que en ningún caso pueden ser contrarias al Reglamento.

I.2.4.4 — CONTROL DE MATERIALES — El supervisor exige que la construcción use materiales que cumplan los requisitos y normas técnicas de calidad del Reglamento para cada material o tipo de elemento estructural. La Tabla I.2.4-1 sirve de guía con referencias cruzadas: para concreto estructural remite a C.1.5/C.3.8 (normas técnicas), C.3.1-C.3.6 (ensayo de materiales cementantes/agregados/agua/acero/aditivos) y C.5.6 (evaluación y aceptación); para mampostería estructural remite a D.2.3 (normas técnicas), D.3.6 (unidades de concreto/arcilla/sílico-calcáreas), D.3.2-D.3.3 (cemento/cal y acero de refuerzo) y D.3.7-D.3.8 (muestreo y ensayos); para casas de uno y dos pisos remite a E.3.2-E.3.3 (unidades de mampostería y morteros), E.4.2 (elementos de confinamiento), E.7.4 (bahareque encementado) y E.9.3 (materiales de cubierta); para estructuras metálicas remite a F.2.1.4-F.2.1.5 (especificaciones y acero estructural), F.3.5/F.4.1.1/F.4.7.2/F.4.8.2 (perfiles), F.2.10.2/F.3.1.4.4 (soldadura), F.2.18.2.3 (protección anticorrosiva) y F.5 (aluminio); para muros divisorios y elementos no estructurales remite a B.3.4-B.3.5 (peso) y al Capítulo A.9 (desempeño sísmico).""",
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Mismo chunker validado en insert_titulo_d_nucleo.py: divide por
    parrafo -> oracion -> coma hasta respetar el limite real de tokens
    del tokenizer (no una aproximacion por caracteres)."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "capitulo": chunk["capitulo"],
                "titulo": chunk["titulo"],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({**f, "embedding": emb})

    print(f"{len(CHUNKS)} bloques originales (H + I) -> {len(rows)} subchunks reales:")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en nsr10_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
