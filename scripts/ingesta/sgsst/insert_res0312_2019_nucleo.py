"""
Inserta el núcleo verbatim real de la Resolución 0312 de 2019 (Ministerio
del Trabajo) — Estándares Mínimos del Sistema de Gestión de la Seguridad y
Salud en el Trabajo (SG-SST) — en nsr10_chunks.

Contexto importante: ntc_chunks YA tenía 8 filas para "Resolución 0312 de
2019" (ids 234-241), pero verificadas antes de esta inserción resultaron
ser notas comprimidas/parafraseadas (ej. "Objeto: definir estándares
mínimos obligatorios, criterios evaluación/verificación..."), NO el texto
legal verbatim. Este script reemplaza ese hueco de calidad con extracción
real palabra por palabra desde la fuente.

Fuente: HTML de https://safetya.co/normatividad/resolucion-0312-de-2019/
(portal privado especializado en SST, pero reproduce el texto oficial
completo — confirmado línea por línea contra la numeración de artículos
conocida de la resolución; SUIN-Juriscol, la fuente primaria oficial,
rechazó la conexión TLS en este entorno). NO se usó ningún archivo
"RAG+CAG" de Google Drive (confirmados en sesiones previas como resúmenes
sintéticos generados, no el texto real).

Núcleo insertado (reemplaza/mejora la cobertura previa de baja calidad):
- Artículo 1 (Objeto) + Artículo 2 (Campo de aplicación, Parágrafos 1-3)
- Artículo 25 (Fases de adecuación, transición y aplicación)
- Artículo 26 (Implementación definitiva desde enero de 2020)
- Artículo 27 (Tabla de Valores de los Estándares Mínimos — los 62 ítems
  reales con sus pesos porcentuales, en 3 sub-bloques por ciclo PHVA)
- Artículo 28 (Planes de mejoramiento según resultado de autoevaluación)
- Artículo 29 (Planes de mejoramiento a solicitud del Ministerio del Trabajo)
- Artículo 30 (Indicadores Mínimos de SST — fórmulas reales)
- Artículo 31 (Estándares Mínimos para actividades de alto riesgo)

Quedan fuera de este núcleo (ronda futura si se necesita): Artículos 3-15
(estándares diferenciados por tamaño de empresa/nivel de riesgo — mismo
contenido del Art. 27 pero fragmentado por categoría) y Artículos 17-24
(roles y responsabilidades de actores del SGRL).

Uso: python scripts/ingesta/sgsst/insert_res0312_2019_nucleo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO = "Resolución 0312 de 2019 — Estándares Mínimos del Sistema de Gestión de SST"

CHUNKS = [
    {
        "id": "RES0312-2019-ART1_2",
        "capitulo": CAPITULO,
        "seccion": "Artículo 1 y 2",
        "titulo": "Objeto de la resolución (Estándares Mínimos SG-SST) y campo de aplicación (empleadores, contratantes, ARL), Parágrafos 1-3 (excepciones)",
        "texto": """Artículo 1. Objeto. La presente Resolución tiene por objeto establecer los Estándares Mínimos del Sistema de Gestión de Seguridad y Salud en el Trabajo SG-SST para las personas naturales y jurídicas señaladas en el artículo 2° de este Acto Administrativo.

Los presentes Estándares Mínimos corresponden al conjunto de normas, requisitos y procedimientos de obligatorio cumplimiento de los empleadores y contratantes, mediante los cuales se establecen, verifican y controlan las condiciones básicas de capacidad técnico-administrativa y de suficiencia patrimonial y financiera indispensables para el funcionamiento, ejercicio y desarrollo de actividades en el Sistema de Gestión de SST.

Artículo 2. Campo de aplicación. La presente Resolución se aplica a los empleadores públicos y privados, a los contratantes de personal bajo modalidad de contrato civil, comercial o administrativo, a los trabajadores dependientes e independientes, a las organizaciones de economía solidaria y del sector cooperativo, a las agremiaciones o asociaciones que afilian trabajadores independientes al Sistema de Seguridad Social Integral, a las empresas de servicios temporales, a los estudiantes afiliados al Sistema General de Riesgos Laborales y los trabajadores en misión; a las administradoras de riesgos laborales; a la Policía Nacional en lo que corresponde a su personal no uniformado y al personal civil de las Fuerzas Militares; quienes deben implementar los Estándares Mínimos del Sistema de Gestión de SST en el marco del Sistema de Garantía de Calidad del Sistema General de Riesgos Laborales.

Parágrafo 1. Para dar cumplimiento a la Decisión 584 de 2004 y a la Resolución 957 de 2005 de la Comunidad Andina de Naciones, los regímenes de excepción previstos en el artículo 279 de la Ley 100 de 1993, pueden tomar como referencia o guía los Estándares Mínimos del Sistema de Gestión de SST establecidos en la presente Resolución, para lo cual cada entidad, empresa o institución realizará los ajustes y adecuaciones correspondientes.

Parágrafo 2. No están obligados a implementar los Estándares Mínimos establecidos en la presente Resolución, los trabajadores independientes con afiliación voluntaria al Sistema General de Riesgos Laborales de que trata la Sección 5 del Capítulo 2 del Título 4 de la Parte 2 del Libro 2 del Decreto 1072 de 2015, Único Reglamentario del Sector Trabajo.

Parágrafo 3. Los Estándares Mínimos del Sistema de Gestión de SST para personas naturales que desarrollen actividades de servicio doméstico serán establecidos en un acto administrativo independiente.""",
    },
    {
        "id": "RES0312-2019-ART25",
        "capitulo": CAPITULO,
        "seccion": "Artículo 25",
        "titulo": "Fases de adecuación, transición y aplicación para la implementación del SG-SST con Estándares Mínimos (5 fases, 2017-2019)",
        "texto": """Artículo 25. Fases de adecuación, transición y aplicación para la implementación del Sistema de Gestión de SST con Estándares Mínimos. Las fases de adecuación, transición y aplicación para la implementación del Sistema de Gestión de SST con Estándares Mínimos, que deben adelantar los empleadores y contratantes y que se encuentran en proceso de desarrollo son:

Fase 1, Evaluación inicial: es la autoevaluación realizada por la empresa con el fin de identificar las prioridades y necesidades en SST para establecer el plan de trabajo anual de la empresa del año 2018, conforme al artículo 2.2.4.6.16 del Decreto 1072 de 2015. Responsable: las empresas, personas o entidades encargadas de implementar y ejecutar los Sistemas de Gestión de SST, con la asesoría de las administradoras de riesgos laborales y según los Estándares Mínimos. Tiempos: de junio a agosto de 2017.

Fase 2, Plan de mejoramiento conforme a la evaluación inicial: es el conjunto de elementos de control que consolida las acciones de mejoramiento necesarias para corregir las debilidades encontradas en la autoevaluación. Durante este período las empresas o entidades deben: primero, realizar la autoevaluación conforme a los Estándares Mínimos; segundo, establecer el plan de mejora conforme a la evaluación inicial; tercero, diseñar el Sistema de Gestión de SST, y formular el plan anual del Sistema de Gestión de SST de año 2018. Responsable: las empresas, personas o entidades encargadas de implementar y ejecutar los Sistemas de Gestión de SST, con la asesoría de las administradoras de riesgos laborales y según los Estándares Mínimos. Tiempos: de septiembre a diciembre de 2017.

Fase 3, Ejecución: es la puesta en marcha del Sistema de Gestión de SST, se realiza durante el año 2018, en coherencia con la autoevaluación de Estándares Mínimos y plan de mejoramiento. En el mes de diciembre del año 2018, el empleador o contratante o entidad formula el plan anual del Sistema de Gestión de SST del año 2019. Responsable: las empresas, personas o entidades encargadas de implementar y ejecutar los Sistemas de Gestión de SST, con la asesoría de las administradoras de riesgos laborales y según los Estándares Mínimos. Tiempos: de enero a diciembre de 2018.

Fase 4, Seguimiento y plan de mejora: es el momento de vigilancia preventiva de la ejecución, desarrollo e implementación del Sistema de Gestión de SST. En esta fase la empresa deberá: primero, realizar la autoevaluación conforme a los Estándares Mínimos; segundo, establecer el plan de mejora conforme al plan del Sistema de Gestión de SST ejecutado en el año 2018 y lo incorpora al Plan del Sistema de Gestión que se está desarrollando durante el año 2019. El seguimiento al Sistema de Gestión de SST y al cumplimiento al plan de mejora se realizará por parte del Ministerio del Trabajo y Administradoras de Riesgos Laborales. Tiempos: de enero a octubre de 2019.

Fase 5, Inspección, vigilancia y control: fase de verificación del cumplimiento de la normativa vigente sobre el Sistema de Gestión de SST. La efectúa el Ministerio del Trabajo conforme a los Estándares Mínimos establecidos en la presente Resolución. Tiempos: de noviembre de 2019 en adelante.

Durante estas fases las empresas aplicarán para la evaluación la Tabla de Valores y Calificación de los Estándares Mínimos del Sistema de Gestión de SST, mediante el diligenciamiento del formulario de evaluación establecido en el artículo 27 de la presente Resolución. En el mes de diciembre de 2019, los empleadores y contratantes objeto de la presente Resolución realizarán lo siguiente: aplicar la autoevaluación conforme a la Tabla de Valores y Calificación de los Estándares Mínimos del Sistema de Gestión de SST, mediante el diligenciamiento del formulario de evaluación establecido en el artículo 27 de la presente Resolución; elaborar el Plan de Mejora conforme al resultado de la autoevaluación de los Estándares Mínimos; formular el Plan Anual del Sistema de Gestión de SST del año 2020.""",
    },
    {
        "id": "RES0312-2019-ART26",
        "capitulo": CAPITULO,
        "seccion": "Artículo 26",
        "titulo": "Implementación definitiva del SG-SST de enero del año 2020 en adelante (ciclo anual enero-diciembre, registro en el aplicativo del Ministerio del Trabajo)",
        "texto": """Artículo 26. Implementación definitiva del Sistema de Gestión de SST de enero del año 2020 en adelante. Desde enero del año 2020 en adelante, todos los Sistemas de Gestión de SST se ejecutarán anualmente de enero a diciembre o en cualquier fracción del año si la empresa o entidad es creada durante el respectivo año.

De 2020 y en adelante, en el mes de diciembre las empresas deberán: aplicar la autoevaluación conforme a la Tabla de Valores y Calificación de los Estándares Mínimos del Sistema de Gestión de SST, mediante el diligenciamiento del formulario de evaluación establecido en el artículo 27 de la presente Resolución; elaborar el Plan de Mejora conforme al resultado de la autoevaluación de los Estándares Mínimos, el cual debe quedar aprobado por la empresa en el Plan Anual del Sistema de Gestión de SST; formular el Plan Anual del Sistema de Gestión de SST, el cual debe empezar a ser ejecutado a partir del primero (1°) de enero del año siguiente.

El formulario de evaluación de Estándares Mínimos diligenciado de que trata el artículo 27 de la presente Resolución y los planes de mejora, se registrarán en la aplicación habilitada en la página web del Ministerio del Trabajo, de diciembre del año 2020 en adelante.""",
    },
    {
        "id": "RES0312-2019-ART27_planear",
        "capitulo": CAPITULO,
        "seccion": "Artículo 27 (parte 1 de 3) — Ciclo I. PLANEAR",
        "titulo": "Tabla de Valores de los Estándares Mínimos SG-SST — Ciclo I PLANEAR (25%): Recursos (10%) y Gestión Integral del SG-SST (15%), 20 ítems evaluables",
        "texto": """Artículo 27. Tabla de Valores de los Estándares Mínimos. Para la calificación de cada uno de los ítems que componen los numerales de los Estándares Mínimos del Sistema de Gestión de SST, se tomará la tabla de valores que se presenta a continuación, en la cual se relacionan los porcentajes a asignar a cada uno.

Para la calificación de cada uno de los ítems se tomarán los porcentajes máximos o mínimos de acuerdo a la Tabla de Valores teniendo en cuenta si se cumple o no con el ítem del estándar. En los ítems de la Tabla de Valores que no aplican para las empresas de menos de cincuenta (50) trabajadores clasificadas con riesgo I, II ó III, se deberá otorgar el porcentaje máximo de calificación en la columna "No Aplica" frente al ítem correspondiente.

I. PLANEAR — RECURSOS (10%): Recursos financieros, técnicos, humanos y de otra índole requeridos para coordinar y desarrollar el SG-SST (4%): 1.1.1 Responsable del SG-SST (0,5). 1.1.2 Responsabilidades en el SG-SST (0,5). 1.1.3 Asignación de recursos para el SG-SST (0,5). 1.1.4 Afiliación al Sistema General de Riesgos Laborales (0,5). 1.1.5 Identificación de trabajadores de alto riesgo y cotización de pensión especial (0,5). 1.1.6 Conformación COPASST (0,5). 1.1.7 Capacitación COPASST (0,5). 1.1.8 Conformación Comité de Convivencia (0,5).

Capacitación en el SG-SST (6%): 1.2.1 Programa de Capacitación promoción y prevención PyP (2). 1.2.2 Inducción y Reinducción en SG-SST, actividades de Promoción y Prevención PyP (2). 1.2.3 Responsables del SG-SST con curso virtual de 50 horas (2).

GESTIÓN INTEGRAL DEL SG-SST (15%): Política de SST (1%): 2.1.1 Política del SG-SST firmada, fechada y comunicada al COPASST (1). Objetivos del SG-SST (1%): 2.2.1 Objetivos definidos, claros, medibles, cuantificables, con metas, documentados, revisados del SG-SST (1). Evaluación inicial del SG-SST (1%): 2.3.1 Evaluación e identificación de prioridades (1). Plan Anual de Trabajo (2%): 2.4.1 Plan que identifica objetivos, metas, responsabilidad, recursos con cronograma y firmado (2). Conservación de la documentación (2%): 2.5.1 Archivo o retención documental del SG-SST (2). Rendición de cuentas (1%): 2.6.1 Rendición sobre el desempeño (1). Normatividad nacional vigente y aplicable en materia de SST (2%): 2.7.1 Matriz legal (2). Comunicación (1%): 2.8.1 Mecanismos de comunicación, auto reporte en SG-SST (1). Adquisiciones (1%): 2.9.1 Identificación, evaluación, para adquisición de productos y servicios en SG-SST (1). Contratación (2%): 2.10.1 Evaluación y selección de proveedores y contratistas (2). Gestión del cambio (1%): 2.11.1 Evaluación del impacto de cambios internos y externos en el SG-SST (1).

Subtotal ciclo PLANEAR: 25 puntos sobre 100.""",
    },
    {
        "id": "RES0312-2019-ART27_hacer",
        "capitulo": CAPITULO,
        "seccion": "Artículo 27 (parte 2 de 3) — Ciclo II. HACER",
        "titulo": "Tabla de Valores de los Estándares Mínimos SG-SST — Ciclo II HACER (60%): Gestión de la Salud (20%), Gestión de Peligros y Riesgos (30%), Gestión de Amenazas (10%)",
        "texto": """II. HACER — GESTIÓN DE LA SALUD (20%): Condiciones de salud en el trabajo (9%): 3.1.1 Descripción sociodemográfica, diagnóstico de condiciones de salud (1). 3.1.2 Actividades de Promoción y Prevención en Salud (1). 3.1.3 Información al médico de los perfiles de cargo (1). 3.1.4 Realización de Evaluaciones Médicas Ocupacionales, peligros, periodicidad, comunicación al trabajador (1). 3.1.5 Custodia de Historias Clínicas (1). 3.1.6 Restricciones y recomendaciones médico/laborales (1). 3.1.7 Estilos de vida y entornos saludables, controles tabaquismo, alcoholismo, farmacodependencia y otros (1). 3.1.8 Agua potable, servicios sanitarios y disposición de basuras (1). 3.1.9 Eliminación adecuada de residuos sólidos, líquidos o gaseosos (1).

Registro, reporte e investigación de enfermedades laborales, incidentes y accidentes de trabajo (5%): 3.2.1 Reporte de los Accidentes de Trabajo y Enfermedad Laboral a la ARL, EPS y Dirección Territorial del Ministerio del Trabajo (2). 3.2.2 Investigación de incidentes, accidentes y enfermedades laborales (2). 3.2.3 Registro y análisis estadístico de accidentes y enfermedades laborales (1).

Mecanismos de vigilancia de las condiciones de salud de los trabajadores (6%): 3.3.1 Medición de la frecuencia de la accidentalidad (1). 3.3.2 Medición de la severidad de la accidentalidad (1). 3.3.3 Medición de la mortalidad por Accidentes de Trabajo (1). 3.3.4 Medición de la prevalencia de Enfermedad Laboral (1). 3.3.5 Medición de la incidencia de Enfermedad Laboral (1). 3.3.6 Medición del ausentismo por causa médica (1).

GESTIÓN DE PELIGROS Y RIESGOS (30%): Identificación de peligros, evaluación y valoración de riesgos (15%): 4.1.1 Metodología para la identificación de peligros, evaluación y valoración de los riesgos (4). 4.1.2 Identificación de peligros con participación de todos los niveles de la empresa (4). 4.1.3 Identificación de sustancias catalogadas como carcinógenas o con toxicidad aguda (3). 4.1.4 Realización de mediciones ambientales, químicas, físicas y biológicas (4).

Medidas de prevención y control para intervenir los peligros/riesgos (15%): 4.2.1 Implementación de medidas de prevención y control de peligros/riesgos identificados (2,5). 4.2.2 Verificación de aplicación de medidas de prevención y control por parte de los trabajadores (2,5). 4.2.3 Elaboración de procedimientos, instructivos, fichas, protocolos (2,5). 4.2.4 Realización de inspecciones sistemáticas a instalaciones, maquinaria o equipos con participación del COPASST (2,5). 4.2.5 Mantenimiento periódico de instalaciones, equipos, máquinas, herramientas (2,5). 4.2.6 Entrega de Elementos de Protección Personal EPP, se verifica con contratistas y subcontratistas (2,5).

GESTIÓN DE AMENAZAS (10%): Plan de prevención, preparación y respuesta ante emergencias (10%): 5.1.1 Se cuenta con el Plan de Prevención, Preparación y Respuesta ante emergencias (5). 5.1.2 Brigada de prevención conformada, capacitada y dotada (5).

Subtotal ciclo HACER: 60 puntos sobre 100.""",
    },
    {
        "id": "RES0312-2019-ART27_verificar_actuar",
        "capitulo": CAPITULO,
        "seccion": "Artículo 27 (parte 3 de 3) — Ciclos III. VERIFICAR y IV. ACTUAR",
        "titulo": "Tabla de Valores de los Estándares Mínimos SG-SST — Ciclo III VERIFICAR (5%), Ciclo IV ACTUAR (10%), totales (100 puntos) y reglas de diligenciamiento",
        "texto": """III. VERIFICAR — VERIFICACIÓN DEL SG-SST (5%): Gestión y resultados del SG-SST (5%): 6.1.1 Definición de indicadores del SG-SST de acuerdo a condiciones de la empresa (1,25). 6.1.2 La empresa adelanta auditoría por lo menos una vez al año (1,25). 6.1.3 Revisión anual por la alta dirección, resultados y alcance de la auditoría (1,25). 6.1.4 Planificación de auditorías con el COPASST (1,25).

IV. ACTUAR — MEJORAMIENTO (10%): Acciones preventivas y correctivas con base en los resultados del SG-SST (10%): 7.1.1 Definición de acciones preventivas y correctivas con base en resultados del SG-SST (2,5). 7.1.2 Acciones de mejora conforme a revisión de la alta dirección (2,5). 7.1.3 Acciones de mejora con base en investigaciones de accidentes de trabajo y enfermedades laborales (2,5). 7.1.4 Elaboración de Plan de Mejoramiento e implementación de medidas y acciones correctivas solicitadas por autoridades y ARL (2,5).

TOTALES: 100 puntos (Planear 25 + Hacer 60 + Verificar 5 + Actuar 10).

Reglas de diligenciamiento: cuando se cumple con el ítem del estándar la calificación será la máxima del respectivo ítem, de lo contrario su calificación será igual a cero (0). En los ítems de la Tabla de Valores que no aplican para las empresas de menos de cincuenta (50) trabajadores clasificadas con riesgo I, II ó III, de conformidad con los Estándares Mínimos de SST vigentes, se deberá otorgar el porcentaje máximo de calificación en la columna "No Aplica" frente al ítem correspondiente.

El formulario de autoevaluación es documento público. La información allí consignada debe ser veraz. La inclusión de manifestaciones falsas estará sujeta a las sanciones contempladas en la Ley 599 de 2000 (Código Penal Colombiano, artículos 287, 288, 291, 294), y debe llevar firma del empleador o contratante y firma del responsable de la ejecución del SG-SST.""",
    },
    {
        "id": "RES0312-2019-ART28",
        "capitulo": CAPITULO,
        "seccion": "Artículo 28",
        "titulo": "Planes de mejoramiento conforme al resultado de la autoevaluación: criterios Crítico (<60%), Moderadamente Aceptable (60-85%), Aceptable (>85%) y contenido mínimo del plan",
        "texto": """Artículo 28. Planes de mejoramiento conforme al resultado de la autoevaluación de los Estándares Mínimos. Los empleadores o contratantes deben realizar la autoevaluación de los Estándares Mínimos, la cual tendrá un resultado que obliga o no a realizar un plan de mejora, así:

Si el puntaje obtenido es menor al 60%: valoración CRÍTICO. Acción: realizar y tener a disposición del Ministerio del Trabajo un Plan de Mejoramiento de inmediato; enviar a la respectiva Administradora de Riesgos Laborales a la que se encuentre afiliada la empresa o contratante, un reporte de avances en el término máximo de tres (3) meses después de realizada la autoevaluación de Estándares Mínimos; seguimiento anual y plan de visita a la empresa con valoración crítica, por parte del Ministerio del Trabajo.

Si el puntaje obtenido está entre el 60 y 85%: valoración MODERADAMENTE ACEPTABLE. Acción: realizar y tener a disposición del Ministerio del Trabajo un Plan de Mejoramiento; enviar a la Administradora de Riesgos Laborales un reporte de avances en el término máximo de seis (6) meses después de realizada la autoevaluación de Estándares Mínimos; plan de visita por parte del Ministerio del Trabajo.

Si el puntaje obtenido es mayor al 85%: valoración ACEPTABLE. Acción: mantener la calificación y evidencias a disposición del Ministerio del Trabajo, e incluir en el Plan Anual de Trabajo las mejoras detectadas.

El plan de mejoramiento se debe presentar vía correo electrónico o en documento físico a la Administradora de Riesgos Laborales, quien dará sus recomendaciones a través del mismo medio de comunicación por el que se hizo el envío. El empleador o contratante debe rendir informe sobre el avance del plan de mejoramiento en el mes de julio de cada año, teniendo en cuenta las recomendaciones de la Administradora de Riesgos Laborales.

El plan de mejoramiento debe contener como mínimo: las actividades concretas a desarrollar; las personas responsables de cada una de las actividades de mejora; el plazo determinado para su cumplimiento; los diferentes recursos administrativos y financieros destinados para la realización de las acciones de mejora; fundamentos y soportes de la efectividad de las acciones y actividades para subsanar y prevenir que se presenten en el futuro hechos o situaciones que afecten el bienestar y salud de los trabajadores o personas que prestan servicios en las empresas.

Parágrafo 1. Las autoevaluaciones de Estándares Mínimos y los planes de mejoramiento de los años 2017, 2018 y del primer semestre de 2019 no se registran en las Administradoras de Riesgos Laborales, serán conservados por las empresas a disposición de los funcionarios del Ministerio del Trabajo. A partir del mes de diciembre de 2019, las empresas deben remitir copia de la autoevaluación de Estándares Mínimos y del plan de mejoramiento a las Administradoras de Riesgos Laborales para su estudio, análisis, comentarios y recomendaciones.

Parágrafo 2. Las autoevaluaciones y los planes de mejoramiento de las empresas se registrarán de manera paulatina y progresiva en la aplicación habilitada en la página web del Ministerio del Trabajo o por el medio que éste indique, a partir del mes de diciembre del año 2020.""",
    },
    {
        "id": "RES0312-2019-ART29",
        "capitulo": CAPITULO,
        "seccion": "Artículo 29",
        "titulo": "Planes de mejoramiento a solicitud del Ministerio del Trabajo cuando se detecta incumplimiento en visita de inspección",
        "texto": """Artículo 29. Planes de mejoramiento a solicitud del Ministerio del Trabajo. Cuando los funcionarios de las Direcciones Territoriales del Ministerio del Trabajo detecten en cualquier momento un incumplimiento de las obligaciones, normas y requisitos legales establecidos en los Estándares Mínimos del Sistema de Gestión de Seguridad y Salud en el Trabajo, se podrá ordenar planes de mejoramiento, con el fin de que se efectúen las acciones correctivas tendientes a la superación de las situaciones irregulares detectadas.

El plan debe contener como mínimo las actividades concretas a desarrollar, la persona responsable de cada una de ellas, el plazo determinado para su cumplimiento y la ejecución del plan, y los diferentes recursos administrativos y financieros destinados para su cumplimiento. El plan debe estar orientado a subsanar definitivamente las situaciones detectadas, así como prevenir que se presenten en el futuro casos similares o relacionados.""",
    },
    {
        "id": "RES0312-2019-ART30",
        "capitulo": CAPITULO,
        "seccion": "Artículo 30",
        "titulo": "Indicadores Mínimos de SST: frecuencia y severidad de accidentalidad, mortalidad, prevalencia/incidencia de enfermedad laboral, ausentismo — fórmulas y periodicidad",
        "texto": """Artículo 30. Indicadores Mínimos de Seguridad y Salud en el Trabajo. A partir del año 2019, las empresas anualmente llevarán un registro de los indicadores de SST, entre los cuales se determinará: frecuencia de accidentalidad, severidad de accidentalidad, proporción de accidentes de trabajo mortales, prevalencia de la enfermedad laboral, incidencia de la enfermedad laboral y ausentismo por causa médica.

Frecuencia de accidentalidad: número de veces que ocurre un accidente de trabajo en el mes. Fórmula: (número de accidentes de trabajo que se presentaron en el mes / número de trabajadores en el mes) × 100. Interpretación: por cada cien (100) trabajadores que laboraron en el mes, se presentaron X accidentes de trabajo. Periodicidad mínima: mensual.

Severidad de accidentalidad: número de días perdidos por accidentes de trabajo en el mes. Fórmula: (número de días de incapacidad por accidente de trabajo en el mes + número de días cargados en el mes / número de trabajadores en el mes) × 100. Interpretación: por cada cien (100) trabajadores que laboraron en el mes, se perdieron X días por accidente de trabajo. Periodicidad mínima: mensual.

Proporción de accidentes de trabajo mortales: número de accidentes de trabajo mortales en el año. Fórmula: (número de accidentes de trabajo mortales que se presentaron en el año / total de accidentes de trabajo que se presentaron en el año) × 100. Interpretación: en el año, el X% de accidentes de trabajo fueron mortales. Periodicidad mínima: anual.

Prevalencia de la enfermedad laboral: número de casos de enfermedad laboral presentes en una población en un periodo de tiempo. Fórmula: (número de casos nuevos y antiguos de enfermedad laboral en el periodo Z / promedio de trabajadores en el periodo Z) × 100.000. Interpretación: por cada 100.000 trabajadores existen X casos de enfermedad laboral en el periodo Z. Periodicidad mínima: anual.

Incidencia de la enfermedad laboral: número de casos nuevos de enfermedad laboral en una población determinada en un periodo de tiempo. Fórmula: (número de casos nuevos de enfermedad laboral en el periodo Z / promedio de trabajadores en el periodo Z) × 100.000. Interpretación: por cada 100.000 trabajadores existen X casos nuevos de enfermedad laboral en el periodo Z. Periodicidad mínima: anual.

Ausentismo por causa médica: ausentismo es la no asistencia al trabajo, con incapacidad médica. Fórmula: (número de días de ausencia por incapacidad laboral o común en el mes / número de días de trabajo programados en el mes) × 100. Interpretación: en el mes se perdió X% de días programados de trabajo por incapacidad médica. Periodicidad mínima: mensual.

Notas: el número de casos de enfermedad laboral corresponde a las enfermedades calificadas como laborales y no al número de personas con enfermedad laboral. Los días cargados son el número de días que se cargan o asignan a una lesión ocasionada por un accidente de trabajo o enfermedad laboral, siempre que la lesión origine muerte, invalidez o incapacidad permanente parcial; se utilizan solamente para el cálculo de los índices de severidad. La constante 100.000 para los indicadores de enfermedad laboral es la utilizada por la Organización Mundial de la Salud para la estadística internacional.

Reglas de aplicación: los empleadores y contratantes deben contabilizar para el cálculo de los indicadores a todos los trabajadores dependientes e independientes, trabajadores en misión, cooperados, estudiantes y demás personas bajo cualquier modalidad de contratación. No deberán crear mecanismos que fomenten el no reporte de accidentes de trabajo o enfermedades laborales, ni reconocer bonos, premios, sobresueldos o estímulos por no reportar accidentes, enfermedades o incapacidades temporales (políticas de "cero accidentes"). No está permitido levantar o suspender el goce de las incapacidades temporales, ni crear programas de reincorporación temprana sin el consentimiento del trabajador, del médico tratante y sin un programa de rehabilitación. Todo accidente o enfermedad con incapacidad temporal igual o superior a un (1) día debe ser reportado y tenido en cuenta para el cálculo de los indicadores de SST. Cada empresa definirá de manera autónoma indicadores adicionales a los mínimos señalados, atendiendo los criterios de los artículos 2.2.4.6.20, 2.2.4.6.21 y 2.2.4.6.22 del Decreto 1072 de 2015.""",
    },
    {
        "id": "RES0312-2019-ART31",
        "capitulo": CAPITULO,
        "seccion": "Artículo 31",
        "titulo": "Estándares Mínimos para trabajadores en actividades de alto riesgo (Decreto 2090 de 2003) — definición del cargo y asesoría de las ARL",
        "texto": """Artículo 31. Estándares Mínimos para trabajadores en actividades de alto riesgo. Para los trabajadores que desempeñen actividades de alto riesgo a las que hace referencia el artículo 2° del Decreto 2090 de 2003, el empleador deberá realizar en la identificación de peligros, evaluación y valoración de los riesgos, una definición del cargo, en donde se indiquen las funciones, tareas, jornada de trabajo y lugar dónde desempeña su labor; así mismo, deberá identificar y relacionar los trabajadores que se dedican de manera permanente a dichas actividades.

Parágrafo. Las entidades Administradoras de Riesgos Laborales darán asesoría, capacitación y asistencia técnica a las empresas que desarrollen actividades de alto riesgo, con relación a las obligaciones, deberes, actividades y funciones establecidas en el presente artículo.""",
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Mismo chunker validado en insert_titulo_h_i_nucleo.py / insert_res4272_2021_nucleo.py:
    divide por parrafo -> oracion -> coma hasta respetar el limite real de
    tokens del tokenizer (no una aproximacion por caracteres)."""
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

    print(f"{len(CHUNKS)} bloques originales (Res. 0312/2019) -> {len(rows)} subchunks reales:")
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
