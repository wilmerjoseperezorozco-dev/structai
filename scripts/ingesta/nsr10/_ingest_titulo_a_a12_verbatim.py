"""
Ingesta verbatim de Título A, Capítulo A.12 (Requisitos especiales
para edificaciones indispensables de los grupos de uso III y IV) --
NSR-10. Fase 7 (última) del plan de cierre del Título A (2026-09-22),
auditoría real de numerales confirmó A.12 en 0/34 (faltan 34) --
capítulo corto pero completamente ausente hasta hoy.

Fuente: NSR-10-160-166.pdf completo, páginas PDF 1-7 (A-117 a A-123,
capítulo completo). Leídas visualmente con Read pages= sobre el PDF
nativo -- nunca extracción mecánica (pypdf). La Figura A.12.2-1 (mapa
de valores de Ad por región de Colombia) y la Figura A.12.3-1 (curva
del espectro de aceleraciones del umbral de daño) son gráficos -- no
se transcriben como imagen; los valores numéricos que representan ya
están íntegros en las Tablas A.12.2-1/A.12.2-2 y en las ecuaciones
A.12.3-1 a A.12.3-6 del texto, que sí se transcriben completos.

Uso: python _ingest_titulo_a_a12_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"

CHUNKS = [
    {
        "id": "NSR10-A-A_12_0_nomenclatura",
        "seccion": "A.12.0 — Nomenclatura del Capítulo A.12",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "CAPÍTULO A.12 — REQUISITOS ESPECIALES PARA EDIFICACIONES "
            "INDISPENSABLES DE LOS GRUPOS DE USO III Y IV\n\n"
            "A.12.0 — NOMENCLATURA\n\n"
            "Ad = coeficiente que representa la aceleración pico "
            "efectiva, para el umbral de daño, dado en A.12.2.\n"
            "Ed = fuerzas sísmicas del umbral de daño.\n"
            "Fv = coeficiente de amplificación que afecta la aceleración "
            "en la zona de períodos intermedios, debida a los efectos de "
            "sitio, adimensional, dado en A.2.4.5.\n"
            "g = aceleración debida a la gravedad (9.8 m/s²).\n"
            "hpi = altura del piso i, medida desde la superficie del "
            "diafragma del piso i hasta la superficie del diafragma del "
            "piso inmediatamente inferior, i-1.\n"
            "I = coeficiente de importancia definido en A.2.5.2\n"
            "M = masa total de la edificación - M se expresa en kg. "
            "Debe ser igual a la masa total de la estructura más la "
            "masa de aquellos elementos tales como muros divisorios y "
            "particiones, equipos permanentes, tanques y sus "
            "contenidos, etc. En depósitos o bodegas debe incluirse "
            "además un 25 por ciento de la masa correspondiente a los "
            "elementos que causan la carga viva del piso. Capítulos A.4 "
            "y A.5.\n"
            "S = coeficiente de sitio dado en A.12.3.\n"
            "S̄ = coeficiente de sitio para ser empleado en el espectro "
            "sísmico del umbral de daño (S̄ = 1.25S).\n"
            "Sad = valor del espectro sísmico del umbral de daño, para "
            "un período de vibración dado. Máxima aceleración "
            "horizontal para el umbral de daño, expresada como una "
            "fracción de la aceleración de la gravedad, para un sistema "
            "de un grado de libertad con un período de vibración T.\n"
            "T = período de vibración del sistema elástico, en "
            "segundos.\n"
            "TCd = período de vibración, en segundos, correspondiente a "
            "la transición entre la zona de aceleración constante del "
            "espectro sísmico del umbral de daño, para períodos cortos "
            "y la parte descendiente del mismo. Véase A.12.\n"
            "TLd = período de vibración, en segundos, correspondiente a "
            "la transición entre la zona de desplazamiento constante "
            "del espectro sísmico del umbral de daño, para períodos "
            "largos. Véase A.12.3\n"
            "Vs = cortante sísmico en la base de la estructura, "
            "calculado por el método de la fuerza horizontal "
            "equivalente del Capítulo A.4.\n"
            "Vsd = cortante sísmico en la base, para las fuerzas "
            "sísmicas del umbral de daño. Véase A.12.4."
        ),
    },
    {
        "id": "NSR10-A-A_12_1_general_proposito_alcance_metodologia_procedimiento",
        "seccion": "A.12.1 — General (propósito, alcance, metodología y procedimiento de verificación con los pasos A a D)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.1 — GENERAL\n\n"
            "A.12.1.1 — PROPÓSITO — El presente Capítulo contiene los "
            "requisitos adicionales, a los contenidos en los capítulos "
            "restantes del presente Título, que se deben cumplir en el "
            "diseño y construcción sismo resistente de las edificaciones "
            "pertenecientes al grupo de uso IV, definido en A.2.5.1.1, y "
            "las incluidas en los literales (a), (b), (c) y (d) del "
            "grupo de uso III, tal como lo define A.2.5.1.2, esenciales "
            "para la recuperación de la comunidad con posterioridad a la "
            "ocurrencia de una emergencia, incluyendo un sismo, con el "
            "fin de garantizar que puedan operar durante y después de la "
            "ocurrencia de un temblor. En relación con las edificaciones "
            "incluidas en los literales (e) y (f) del Grupo III, como lo "
            "define A.2.5.1.2, queda a decisión del propietario en el "
            "primer caso o de la autoridad competente en el segundo "
            "definir si se requiere adelantar el diseño de ellas según "
            "los requisitos especiales del Capítulo A.12.\n\n"
            "A.12.1.2 — ALCANCE — Los requisitos del presente Capítulo "
            "deben emplearse en el diseño de las edificaciones "
            "indispensables enumeradas en A.2.5.1.1, las incluidas en "
            "los literales (a), (b), (c) y (d) del grupo de Uso III, tal "
            "como lo define A.2.5.1.2 y de las demás que la comunidad "
            "designe como tales.\n\n"
            "A.12.1.3 — METODOLOGÍA — La determinación de la operatividad "
            "de la edificación con posterioridad a la ocurrencia de un "
            "sismo se realiza verificando que la edificación se "
            "mantiene dentro del rango elástico de respuesta al verse "
            "sometida a unas solicitaciones sísmicas correspondientes al "
            "inicio del daño, o umbral de daño.\n\n"
            "A.12.1.4 — PROCEDIMIENTO DE VERIFICACIÓN — Además de los "
            "pasos que deben cumplirse en el diseño de la edificación "
            "presentados en A.1.3.4, deben realizarse los siguientes "
            "pasos adicionales, con el fin de verificar que la "
            "estructura y los elementos no estructurales se mantienen "
            "dentro del rango elástico de respuesta cuando se presenten "
            "los movimientos sísmicos correspondientes al umbral de "
            "daño:\n\n"
            "Paso A — Movimientos sísmicos correspondientes al umbral de "
            "daño — Determinación de los movimientos sísmicos del "
            "umbral de daño para el lugar, de acuerdo con lo establecido "
            "en A.12.2.\n\n"
            "Paso B — Fuerzas sísmicas correspondientes al umbral de "
            "daño — Obtención de las fuerzas sísmicas del umbral de "
            "daño bajo las cuales debe verificarse el comportamiento de "
            "la estructura de la edificación como de los elementos no "
            "estructurales.\n\n"
            "Paso C — Análisis de la estructura para las fuerzas "
            "sísmicas correspondientes al umbral de daño — El análisis "
            "de la estructura por medio de un modelo matemático "
            "apropiado. El análisis se lleva a cabo aplicando los "
            "movimientos sísmicos correspondientes al umbral de daño, "
            "tal como se define en A.12.4. Deben determinarse los "
            "desplazamientos máximos que imponen los movimientos "
            "sísmicos del umbral de daño a la estructura y las fuerzas "
            "internas que se derivan de ellos.\n\n"
            "Paso D — Verificación para el umbral de daño — Comprobación "
            "de que las deflexiones para el umbral de daño no exceden "
            "los límites establecidos por este Reglamento. Si se exceden "
            "los límites de las derivas máximas para el umbral de daño, "
            "establecidas en A.12.5, la estructura debe ser rigidizada "
            "hasta cuando cumpla la comprobación."
        ),
    },
    {
        "id": "NSR10-A-A_12_2_movimientos_sismicos_umbral_dano",
        "seccion": "A.12.2 — Movimientos sísmicos del umbral de daño (Tablas A.12.2-1 y A.12.2-2, valores de Ad)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.2 — MOVIMIENTOS SÍSMICOS DEL UMBRAL DE DAÑO\n\n"
            "A.12.2.1 — Los movimientos sísmicos del umbral de daño, se "
            "definen para una probabilidad del ochenta por ciento de "
            "ser excedidos en un lapso de cincuenta años, en función de "
            "la aceleración pico efectiva al nivel del umbral de daño, "
            "representada por el parámetro Ad. El valor de este "
            "coeficiente, para efectos del presente Reglamento, debe "
            "determinarse de acuerdo con A.12.2.2 y A.12.2.3.\n\n"
            "A.12.2.2 — Se determina el número de la región en donde "
            "está localizada la edificación usando el Mapa de la figura "
            "A.12.2-1. El valor de Ad se obtiene de la tabla A.12.2-1, "
            "en función del número de la región, o para las ciudades "
            "capitales de departamento utilizando la tabla A.12.2-2 y "
            "para los municipios del país en el Apéndice A-4, incluido "
            "al final del presente Título.\n\n"
            "A.12.2.3 — Alternativamente cuando el municipio o distrito, "
            "realice un estudio de microzonificación sísmica, o "
            "disponga de una red acelerográfica local; con base en el "
            "estudio de microzonificación o en los registros obtenidos, "
            "es posible variar, por medio de una ordenanza municipal, el "
            "valor de Ad, con respecto a los valores dados aquí, pero en "
            "ningún caso este valor podrá se menor al dado en el "
            "presente Reglamento.\n\n"
            "Tabla A.12.2-1 — Valores de Ad según la región del mapa de "
            "la figura A.12.2-1:\n"
            "Región 7: Ad = 0.13 – 0.14\n"
            "Región 6: Ad = 0.11 – 0.12\n"
            "Región 5: Ad = 0.09 – 0.10\n"
            "Región 4: Ad = 0.07 – 0.08\n"
            "Región 3: Ad = 0.05 – 0.06\n"
            "Región 2: Ad = 0.03 – 0.04\n"
            "Región 1: Ad = 0.00 – 0.02\n"
            "(Nota: las regiones representan rangos de valores. Debe "
            "consultarse el Apéndice A-4 para determinar el valor de Ad "
            "en cada municipio.)\n\n"
            "Tabla A.12.2-2 — Valores de Ad para las ciudades capitales "
            "de departamento:\n"
            "Arauca 0.04, Neiva 0.08, Armenia 0.10, Pasto 0.08, "
            "Barranquilla 0.03, Pereira 0.10, Bogotá 0.06, Popayán "
            "0.08, Bucaramanga 0.09, Puerto Carreño 0.02, Cali 0.09, "
            "Puerto Inírida 0.02, Cartagena 0.03, Quibdó 0.13, Cúcuta "
            "0.10, Riohacha 0.04, Florencia 0.05, San Andrés (Isla) "
            "0.03, Ibagué 0.06, San José del Guaviare 0.02, Leticia "
            "0.02, Santa Marta 0.04, Manizales 0.10, Sincelejo 0.04, "
            "Medellín 0.07, Tunja 0.07, Mitú 0.02, Valledupar 0.03, "
            "Mocoa 0.10, Villavicencio 0.07, Montería 0.04, Yopal "
            "0.06.\n\n"
            "Figura A.12.2-1 — Mapa de valores de Ad: mapa geográfico de "
            "Colombia con isolíneas que delimitan las 7 regiones de la "
            "Tabla A.12.2-1 (gráfico, no se transcribe; los valores "
            "numéricos por región y por ciudad ya están íntegros en las "
            "Tablas A.12.2-1 y A.12.2-2)."
        ),
    },
    {
        "id": "NSR10-A-A_12_3_espectro_sismico_umbral_dano",
        "seccion": "A.12.3 — Espectro sísmico para el umbral de daño (ecuaciones A.12.3-1 a A.12.3-6)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.3 — ESPECTRO SÍSMICO PARA EL UMBRAL DE DAÑO\n\n"
            "A.12.3.1 — Los parámetros para determinar el espectro de "
            "aceleraciones horizontales para el umbral de daño en el "
            "campo elástico, para un amortiguamiento crítico de dos por "
            "ciento (2%), que se debe utilizar en las verificaciones del "
            "umbral de daño, se dan en la figura A.12.3-1. El espectro "
            "del umbral de daño se define por medio de la ecuación "
            "A.12.3-1, en la cual el valor T es el mismo que se utilizó "
            "para obtener el espectro sísmico de diseño de la "
            "edificación en el Capítulo A.2 y el valor de S̄ es igual a "
            "1.25Fv, siendo Fv el valor del coeficiente de amplificación "
            "que afecta la aceleración en la zona de períodos "
            "intermedios debida a los efectos de sitio que se obtiene de "
            "acuerdo con la sección A.2.4, empleando allí para Av el "
            "valor de Ad según A.12.2. Además deben cumplirse las "
            "limitaciones dadas en A.12.3.2 a A.12.3.4.\n\n"
            "Sad = 1.5·Ad·S̄/T       (A.12.3-1)\n\n"
            "A.12.3.2 — Para períodos de vibración menores de 0.25 "
            "segundos, el espectro sísmico del umbral de daño puede "
            "obtenerse de la ecuación A.12.3-2.\n\n"
            "Sad = Ad(1.0 + 8T)       (A.12.3-2)\n\n"
            "A.12.3.3 — Para períodos de vibración mayores de 0.25 "
            "segundos y menores de TCd, calculado de acuerdo con la "
            "ecuación A.12.3-3, el valor de Sad puede limitarse al "
            "obtenido de la ecuación A.12.3-4.\n\n"
            "TCd = 0.5·S̄       (A.12.3-3)\n"
            "y\n"
            "Sad = 3.0·Ad       (A.12.3-4)\n\n"
            "A.12.3.4 — Para períodos de vibración mayores de TLd, "
            "calculado de acuerdo con la ecuación A.12.3-5, el valor de "
            "Sad puede limitarse al obtenido de la ecuación A.12.3-6.\n\n"
            "TLd = 2.4·S̄       (A.12.3-5)\n"
            "y\n"
            "Sad = 1.5·Ad·S̄·TLd/T²       (A.12.3-6)\n\n"
            "Figura A.12.3-1 — Espectro de aceleraciones horizontales "
            "elástico del umbral de daño: la curva Sad(T) parte de Ad en "
            "T=0, sube linealmente por Sad = Ad(1+8T) hasta T=0.25s, se "
            "mantiene constante en Sad = 3.0Ad entre T=0.25s y T=TCd "
            "(=0.5S̄), desciende como Sad = 1.5·Ad·S̄/T entre TCd y TLd "
            "(=2.4S̄), y luego desciende como Sad = 1.5·Ad·S̄·TLd/T² para "
            "T > TLd. Nota: este espectro está definido para un "
            "coeficiente de amortiguamiento del 2 por ciento del "
            "crítico.\n\n"
            "A.12.3.5 — Cuando la ciudad donde se encuentre localizada "
            "la edificación disponga de una reglamentación de "
            "microzonificación sísmica, debe utilizarse el espectro de "
            "umbral de daño definido allí. En su defecto, deben "
            "seguirse las prescripciones contenidas en la presente "
            "sección A.12.3."
        ),
    },
    {
        "id": "NSR10-A-A_12_4_metodologia_analisis",
        "seccion": "A.12.4 — Metodología de análisis (método, rigidez, uso de fuerza horizontal equivalente y análisis dinámico)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.4 — METODOLOGÍA DE ANÁLISIS\n\n"
            "A.12.4.1 — MÉTODO DE ANÁLISIS A UTILIZAR — En la "
            "verificación de la respuesta de la estructura a los "
            "movimientos sísmicos correspondientes al umbral de daño, "
            "como mínimo debe emplearse el método de la fuerza "
            "horizontal equivalente dado en el Capítulo A.4, aunque se "
            "permite el uso del método del análisis dinámico, prescrito "
            "en el Capítulo A.5.\n\n"
            "A.12.4.2 — RIGIDEZ DE LA ESTRUCTURA Y SUS ELEMENTOS — Las "
            "rigideces que se empleen en el análisis estructural para "
            "verificación del umbral de daño deben ser compatibles con "
            "las fuerzas y deformaciones que le imponen los movimientos "
            "sísmicos correspondientes a la estructura. Al nivel de "
            "deformaciones del umbral de daño se considera que la "
            "estructura responde en el rango lineal y elástico de "
            "comportamiento y que los elementos no estructurales pueden "
            "contribuir a la rigidez de la estructura, si no están "
            "aislados de ella. Cuando los elementos no estructurales "
            "interactúan con la estructura al nivel de deformaciones del "
            "umbral de daño, debe tenerse en cuenta esta interacción, "
            "tanto en la estructura como en los elementos no "
            "estructurales.\n\n"
            "A.12.4.3 — USO DEL MÉTODO DE LA FUERZA HORIZONTAL "
            "EQUIVALENTE EN LA EVALUACIÓN DEL UMBRAL DE DAÑO — Cuando se "
            "utilice el método de la fuerza horizontal equivalente en el "
            "análisis de la estructura para los movimientos sísmicos "
            "del umbral de daño deben tener en cuenta los siguientes "
            "aspectos:\n\n"
            "A.12.4.3.1 — Período fundamental de la edificación — Puede "
            "utilizarse el período de vibración fundamental determinado "
            "de acuerdo con los requisitos de A.4.2.\n\n"
            "A.12.4.3.2 — Fuerzas sísmicas horizontales del umbral de "
            "daño — Las fuerzas sísmicas correspondientes a los "
            "movimientos sísmicos del umbral de daño corresponden a la "
            "distribución en la altura de la edificación del cortante "
            "sísmico en la base, Vsd. Este cortante sísmico en la base "
            "es equivalente a la totalidad de los efectos inerciales "
            "horizontales producidos por los movimientos sísmicos del "
            "umbral de daño, en la dirección en estudio, y se obtiene "
            "por medio de la siguiente ecuación:\n\n"
            "Vsd = Sad·g·M       (A.12.4-1)\n\n"
            "El valor de Sad en la ecuación anterior corresponde al "
            "valor de la aceleración leída del espectro sísmico definido "
            "en A.12.3 para el período T de la edificación. La fuerza "
            "sísmica horizontal del umbral de daño en cualquier nivel "
            "puede obtenerse de las ecuaciones A.4.3-1 y A.4.3-2, "
            "utilizando Vsd en vez de Vs.\n\n"
            "A.12.4.3.3 — Análisis de la estructura para las fuerzas "
            "sísmicas horizontales del umbral de daño — Por medio de un "
            "análisis estructural realizado empleando las fuerzas "
            "sísmicas correspondientes al umbral de daño obtenidas como "
            "se indica en A.12.4.3.2, se obtienen las fuerzas internas "
            "de la estructura para el umbral de daño, Ed. Deben "
            "utilizarse los requisitos de A.4.4.1 con la excepción del "
            "literal (f). En las estructuras de concreto reforzado y "
            "mampostería estructural, el grado de fisuración debe ser "
            "compatible con las fuerzas sísmicas del umbral de daño, "
            "tomando en cuenta que la estructura actúa dentro del rango "
            "lineal de respuesta. Como resultados del análisis se deben "
            "obtener los desplazamientos horizontales de la estructura, "
            "incluyendo los efectos torsionales, los cuales se emplean "
            "para evaluar el cumplimiento de los requisitos de deriva "
            "para el umbral de daño. Si los elementos no estructurales "
            "fueron incluidos en el análisis deben determinarse sus "
            "deformaciones y esfuerzos.\n\n"
            "A.12.4.4 — USO DEL MÉTODO DE ANÁLISIS DINÁMICO EN LA "
            "EVALUACIÓN DEL UMBRAL DE DAÑO — Cuando se utilice el "
            "método del análisis dinámico deben emplearse los "
            "requisitos del Capítulo A.5, empleando los movimientos "
            "sísmicos correspondientes al umbral de daño en vez de los "
            "movimientos sísmicos de diseño. El ajuste de los resultados "
            "indicado en A.5.4.5 debe hacerse con respecto al valor de "
            "Vsd, obtenido por medio de la ecuación A.12.4-1, en vez de "
            "Vs."
        ),
    },
    {
        "id": "NSR10-A-A_12_5_requisitos_deriva_umbral_dano",
        "seccion": "A.12.5 — Requisitos de la deriva para el umbral de daño (Tabla A.12.5-1)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.5 — REQUISITOS DE LA DERIVA PARA EL UMBRAL DE DAÑO\n\n"
            "A.12.5.1 — DESPLAZAMIENTOS TOTALES HORIZONTALES PARA EL "
            "UMBRAL DE DAÑO — Los desplazamientos horizontales, en las "
            "dos direcciones principales en planta, que tienen todos los "
            "grados de libertad de la estructura al verse afectada por "
            "los movimientos sísmicos para el umbral de daño, definidos "
            "en A.12.2, se determinan por medio del análisis estructural "
            "realizado utilizando el método de análisis definido en "
            "A.12.4 y con las rigideces indicadas en A.12.4.2. Los "
            "desplazamientos horizontales para el umbral de daño, en "
            "cualquiera de las direcciones principales en planta y para "
            "cualquier grado de libertad de la estructura, se obtienen "
            "por medio de la ecuación A.6.2-1, con la excepción de que "
            "no hay necesidad de incluir los desplazamientos causados "
            "por los efectos P-Delta.\n\n"
            "A.12.5.2 — DERIVA MÁXIMA PARA EL UMBRAL DE DAÑO — La deriva "
            "máxima, para el umbral de daño, en cualquier punto del "
            "piso bajo estudio se obtiene por medio de la ecuación "
            "A.6.3-1.\n\n"
            "A.12.5.3 — LÍMITES DE LA DERIVA PARA EL UMBRAL DE DAÑO — La "
            "deriva máxima, para el umbral de daño, evaluada en "
            "cualquier punto de la estructura, determinada de acuerdo "
            "con el procedimiento de A.12.5.2, no puede exceder los "
            "límites establecidos en la tabla A.12.5-1, en la cual la "
            "deriva máxima se expresa como un porcentaje de la altura de "
            "piso hpi:\n\n"
            "Tabla A.12.5-1 — Derivas máximas para el umbral de daño "
            "como porcentaje de hpi:\n"
            "- Estructuras de concreto reforzado, metálicas, de madera, "
            "y de mampostería que cumplen los requisitos de A.12.5.3.1: "
            "0.40% (Δmax^i ≤ 0.0040 hpi).\n"
            "- Estructuras de mampostería que cumplen los requisitos de "
            "A.12.5.3.2: 0.20% (Δmax^i ≤ 0.0020 hpi).\n\n"
            "A.12.5.3.1 — Se permite emplear el límite de deriva máxima "
            "permisible de 0.0040hpi en edificaciones construidas con "
            "mampostería estructural cuando éstas estén compuestas por "
            "muros cuyo modo prevaleciente de falla sea la flexión ante "
            "fuerzas paralelas al plano del muro, diseñados "
            "esencialmente como elementos verticales esbeltos que "
            "actúan como voladizos apoyados en su base o cimentación y "
            "que se construyen de tal manera que la transferencia de "
            "momento entre muros a través de los elementos horizontales "
            "de acople en los diafragmas de entrepiso, ya sean losas, "
            "vigas de enlace, antepechos o dinteles, sea despreciable.\n\n"
            "A.12.5.3.2 — Cuando se trate de muros de mampostería poco "
            "esbeltos o cuyo modo prevaleciente de falla sea causado por "
            "esfuerzos cortantes, debe emplearse el límite de deriva "
            "máxima permisible de 0.0020hpi."
        ),
    },
    {
        "id": "NSR10-A-A_12_6_verificacion_esfuerzos",
        "seccion": "A.12.6 — Verificación de esfuerzos (elementos estructurales y muros no estructurales)",
        "titulo": "NSR-10 Título A — Capítulo A.12 — Requisitos especiales para edificaciones indispensables de los grupos de uso III y IV",
        "texto": (
            "A.12.6 — VERIFICACIÓN DE ESFUERZOS\n\n"
            "A.12.6.1 — ELEMENTOS ESTRUCTURALES — No hay necesidad de "
            "verificar los elementos estructurales para los esfuerzos "
            "generados por el sismo del umbral de daño.\n\n"
            "A.12.6.2 — MUROS NO ESTRUCTURALES — No hay necesidad de "
            "verificar los elementos no estructurales para los esfuerzos "
            "generados por el sismo del umbral de daño."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks...")
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print(f"\nSubiendo {len(rows)} chunks a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK.")


if __name__ == "__main__":
    main()
