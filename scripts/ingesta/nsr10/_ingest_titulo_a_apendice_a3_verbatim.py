"""
Ingesta verbatim del Apéndice A-3 del Título A de NSR-10 (Procedimiento no
lineal estático de plastificación progresiva "Push-Over"), páginas A-147 a
A-152. Fase 4 del plan de cierre del Título A (2026-11-08).

Fuente: NSR-10-191-218.pdf, páginas PDF 1 a 6 (A-147 a A-152), leídas
visualmente con Read pages= sobre el PDF nativo. La página PDF 7 (A-153) ya es
el Apéndice A-4 y no se toca aquí.

Fidelidad: las ecuaciones A-3.2-1 a A-3.2-5 se transcriben en notación lineal
(el PDF las tiene como imagen/símbolos). δ = desplazamiento, Σ = sumatoria.

Uso: python _ingest_titulo_a_apendice_a3_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"
PREFIJO = "NSR10-A-APA3"
CAB = "NSR-10 — Apéndice A-3 — Procedimiento no lineal estático de plastificación progresiva \"Push-Over\"\n\n"

CHUNKS = [
    {
        "id": f"{PREFIJO}_prefacio",
        "seccion": "A-3 — Prefacio",
        "titulo": "Apéndice A-3, prefacio: el análisis no lineal estático (push-over) no es obligatorio; antecedentes FEMA 350, FEMA 356, ATC 40, HAZUS.",
        "texto": CAB + (
            "APÉNDICE A-3 — PROCEDIMIENTO NO LINEAL ESTÁTICO DE PLASTIFICACIÓN PROGRESIVA \"PUSH-OVER\"\n\n"
            "PREFACIO — Este apéndice trata del análisis no lineal estático, un procedimiento de análisis sísmico también conocido algunas veces como análisis \"push-over\", el método de capacidad, o método de la curva de capacidad.\n\n"
            "Este apéndice no es de carácter obligatorio y se ha incluido con el fin de que se estudie preliminarmente con el fin de adoptarlo en ediciones futuras del Reglamento si se considera conveniente.\n\n"
            "Aunque el análisis estático no lineal se ha incluido solo recientemente en las disposiciones de diseño y construcción de edificaciones, el procedimiento en sí no es nuevo y ha sido utilizado durante muchos años tanto en investigación como en aplicaciones de diseño. Por ejemplo, el análisis no lineal estático ha sido utilizado durante muchos años como metodología estándar en el diseño de estructuras para plataformas marinas para efectos hidrodinámicos, y ha sido adoptado recientemente en varias metodologías estándar para la evaluación y rehabilitación sísmica de edificaciones, incluyendo los Criterios Recomendados de Diseño Sísmico para Edificios con Estructura de Acero Resistente a Momentos (FEMA-350, 2000a), Pre-estándar y Comentarios para la Rehabilitación Sísmica de Edificios (FEMA 356, 2000b) y Evaluación Sísmica y Mejoramiento de Edificios (ATC 40, 1996). El análisis no lineal estático constituye el fundamento para los procedimientos de estimación de pérdidas por sismos contenida en HAZUS (NIBS, 1999), que es el modelo de estimación de pérdidas sísmicas de la oficina de atención de desastres norteamericana (FEMA). Aunque no aparece explícitamente en el Reglamento, la metodología del análisis no lineal estático también constituye la base para los procedimientos de la fuerza lateral equivalente contenidos en las disposiciones para estructuras aisladas en la base y estructuras con disipadores de energía.\n\n"
            "Una de las objeciones a la introducción de una metodología de esta naturaleza en el Reglamento se relaciona con la determinación de la deformación límite (llamada algunas veces desplazamiento de desempeño). Se han propuesto diferentes metodologías para determinar el desplazamiento inducido a la estructura por los movimientos del terreno producidos por un sismo y algunas de ellas han sido adoptadas como procedimiento normativo en diferentes países. El tratamiento presentado en este apéndice se basa en correlaciones estadísticas de los desplazamientos cuya predicción se ha realizado utilizando metodologías de análisis lineal y no lineal de la estructura, las cuales son similares a las contenidas en FEMA 356. Un segundo motivo de discusión tiene que ver con la falta de uniformidad de criterio respecto a la bondad del diseño una vez se han estimado las fuerzas y deformaciones producidas por el sismo de diseño. Se debe tener en cuenta que esta limitación aplica igualmente al tratamiento contra el tiempo de la respuesta no lineal, la cual ya ha sido adoptada en el Reglamento.\n\n"
            "El análisis no lineal estático corresponde a un método simplificado para evaluar directamente la respuesta no lineal de estructuras a movimientos fuertes del terreno causados por un sismo. Esta es una alternativa atractiva en comparación a los procedimientos más complejos del análisis de respuesta no lineal contra el tiempo. Se espera que la consideración de esta metodología a través de su inclusión en este apéndice permitirá el desarrollo del consenso necesario para permitir una posterior integración en el Reglamento como tal."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_1_general",
        "seccion": "A-3.1 — General (A-3.1.1 a A-3.1.3)",
        "titulo": "Apéndice A-3, A-3.1: propósito, alcance y definiciones del push-over (curva de capacidad, desplazamiento objetivo, punto de control, resistencia efectiva a fluencia).",
        "texto": CAB + (
            "A-3.1 — GENERAL\n\n"
            "A-3.1.1 — Propósito — En el presente Apéndice se dan recomendaciones para realizar un análisis no lineal estático, también conocido como procedimiento \"push-over\". Este apéndice no tiene carácter obligatorio dentro del reglamento.\n\n"
            "A-3.1.2 — Alcance — Los requisitos del presente Apéndice pueden emplearse en el análisis y diseño sismo resistente de edificaciones existentes y nuevas. Se dan los parámetros de análisis y diseño sismo resistente de una forma compatible con lo que se requiere en el Título A del Reglamento.\n\n"
            "A-3.1.3 — Definiciones\n\n"
            "Base (Base) — Véase Capítulo A.13\n\n"
            "Carga Muerta (Dead load) — Véase Capítulo A.13\n\n"
            "Carga Viva (Live load) — Véase Capítulo A.13\n\n"
            "Componente (Component) — Una parte o elemento de un sistema arquitectónico, eléctrico, mecánico o estructural.\n\n"
            "Corte Basal (Base shear) — Véase Capítulo A.13\n\n"
            "Curva de Capacidad (Capacity curve) — Un gráfico de la fuerza lateral total Vf confrontada contra el desplazamiento lateral del punto de control, tal como se determina en un análisis no lineal estático.\n\n"
            "Desplazamiento de fluencia efectivo (Effective yield displacement) — El desplazamiento del punto de control en la intersección de la primera y segunda ramas de una curva bilineal que se ajusta a la curva de capacidad de acuerdo con la Sección A-3.2.3\n\n"
            "Desplazamiento Objetivo — Un estimado del desplazamiento máximo esperado del punto de control calculado para el sismo de diseño de acuerdo con la sección A-3.2.5\n\n"
            "Diafragma (Diaphragm) — Véase Capítulo A.13\n\n"
            "Diseñador Estructural (Structural engineer of record) — Véase Capítulo A.13\n\n"
            "Edificación (Building) — Véase Capítulo A.13\n\n"
            "Estructura (Structure) — Véase Capítulo A.13\n\n"
            "Movimientos sísmicos de diseño (Design earthquake ground motion) — Véase Capítulo A.13\n\n"
            "Piso (Story) — Véase Capítulo A.13\n\n"
            "Punto de Control (Control point) — Un punto utilizado para indexar el desplazamiento lateral de la estructura en un análisis no lineal estático, determinado de acuerdo con la Sección A-3.2.1\n\n"
            "Resistencia efectiva a fluencia (Effective yield strength) — Es la fuerza lateral total aplicada en la intersección de la primera y segunda ramas de una curva bilineal que se ajusta a la curva de capacidad de acuerdo con la Sección A-3.2.3\n\n"
            "Sistema de Resistencia Sísmica (Seismic-force-resisting system) — Véase Capítulo A.13"
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_1_4_nomenclatura",
        "seccion": "A-3.1.4 — Nomenclatura",
        "titulo": "Apéndice A-3, A-3.1.4: nomenclatura (Cs, C0, C1, R, Rd, Sa, T1, Tc, Te, Vj, V1, Vy, δ1, δy, δT, φi, Ωo).",
        "texto": CAB + (
            "A-3.1.4 — Nomenclatura\n\n"
            "Cs = coeficiente de respuesta sísmica, resultado de dividir Sa por R.\n"
            "C0 = un factor de modificación para relacionar el desplazamiento del punto de control con el desplazamiento de un sistema representativo de un grado simple de libertad, como lo determina la Ecuación A-3.2-3\n"
            "C1 = un factor de modificación para tener en cuenta la influencia del comportamiento inelástico sobre la respuesta del sistema como lo determina la ecuación A-3.2-4\n"
            "g = aceleración de gravedad (9.8 m/s²)\n"
            "j = el incremento de la carga lateral\n"
            "M = masa total de la edificación\n"
            "mi = la porción de la masa total M de la edificación, al Nivel i\n"
            "R = coeficiente de capacidad de disipación de energía para ser empleado en el diseño, corresponde al coeficiente de disipación de energía básico, R0, multiplicado por los coeficientes de reducción de capacidad de disipación de energía por irregularidades en altura, en planta, y por ausencia de redundancia en el sistema estructural de resistencia sísmica (R = φa φp φr R0).\n"
            "Rd = el factor de ductilidad del sistema analizado por \"push-over\" como lo determina la ecuación A-3.2-5\n"
            "Sa = valor del espectro de aceleraciones de diseño para un período de vibración dado. Máxima aceleración horizontal de diseño, expresada como una fracción de la gravedad, para un sistema de un grado de libertad con un período de vibración T. Está definido en A.2.6.\n"
            "T1 = el periodo fundamental de la estructura en la dirección que está bajo consideración determinado en la primera iteración del análisis de \"push-over\".\n"
            "Tc = período de vibración, en segundos, correspondiente a la transición entre la zona de aceleración constante del espectro de diseño, para períodos cortos, y la parte descendiente del mismo. Véase A.2.6.\n"
            "Te = el periodo fundamental efectivo de la estructura en la dirección que se está considerando, como se determina en la Sección A-3.2.3\n"
            "Vj = la fuerza lateral total aplicada al incremento de carga j\n"
            "V1 = la fuerza lateral total aplicada al primer incremento de la carga lateral\n"
            "Vy = resistencia efectiva a la fluencia determinada de una curva bilineal ajustada a la curva de capacidad de acuerdo con la Sección A-3.2.3\n"
            "Δ = deriva del piso como se determina la Sección A-3.2.6\n"
            "γi = las deformaciones del miembro i\n"
            "δj = el desplazamiento del punto de control a un incremento de carga j\n"
            "δT = el desplazamiento objetivo del punto de control determinado de acuerdo con la Sección A-3.2.5\n"
            "δ1 = el desplazamiento del punto de control al primer incremento de la carga lateral\n"
            "δy = el desplazamiento efectivo de fluencia del punto de control determinado de acuerdo con la Sección A-3.2.3 de una curva bilineal ajustada a la curva de capacidad.\n"
            "φi = la amplitud del vector característico de forma al Nivel i, determinada de acuerdo con la Sección A-3.2.4\n"
            "Ωo = coeficiente de sobreresistencia. Véase A.3.3.9."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_1_modelacion",
        "seccion": "A-3.2 y A-3.2.1 — Procedimiento no lineal estático; modelación",
        "titulo": "Apéndice A-3, A-3.2.1: modelación del push-over (efectos P-Delta, modelo bidimensional o tridimensional, fisuración, punto de control).",
        "texto": CAB + (
            "A-3.2 — PROCEDIMIENTO NO LINEAL ESTÁTICO\n\n"
            "Se deben utilizar los requisitos de esta sección cuando se use el procedimiento no lineal estático para diseñar estructuras.\n\n"
            "A-3.2.1 — Modelación — Se debe definir un modelo matemático de la estructura que represente adecuadamente la distribución espacial de la masa y de la rigidez del sistema estructural considerando los efectos de la no linealidad de los componentes para los niveles de deformación que excedan el límite proporcional. Se deben incluir los efectos P-Delta en el análisis.\n\n"
            "Para estructuras regulares con sistemas de resistencia sísmica ortogonales, se permite usar modelos independientes bi-dimensionales para representar cada sistema. Para estructuras que tienen irregularidades en planta Tipos 4P y 5P, como se define en la Tabla A.3-6 o estructuras con sistemas ortogonales independientes se debe usar un modelo tridimensional que incorpore un mínimo de tres grados de libertad para cada nivel de la estructura, consistentes en la translación en dos direcciones ortogonales y la rotación torsional respecto al eje vertical. Cuando los diafragmas no son rígidos comparados con los elementos verticales del sistema de resistencia sísmica, el modelo debe incluir la representación de la flexibilidad del diafragma.\n\n"
            "A menos que el análisis indique que el componente permanece en el rango elástico, se debe usar un modelo fuerza-deformación no lineal para representar la rigidez de los componentes antes de llegar a la fluencia, la resistencia a la fluencia y las propiedades de rigidez de los componentes a diferentes niveles de deformación después de la fluencia. Las propiedades de los componentes de los modelos no lineales deben ser consistentes con los principios de la mecánica o con datos experimentales. Las propiedades que representan el comportamiento de los componentes antes de la fluencia deben ser consistentes con lo indicado en el Capítulo A.5. La resistencia de los elementos no debe exceder los valores esperados teniendo en cuenta la sobre resistencia del material y el endurecimiento por deformación. Las propiedades de los elementos y componentes más allá de fluencia deben tener en cuenta la degradación de la resistencia y la rigidez de acuerdo con los principios de la mecánica estructural o los resultados de ensayos experimentales. El modelo para las columnas debe tener en cuenta la influencia de la carga axial cuando se excede el 15% de la resistencia a la compresión. Igualmente se deben considerar los efectos de fisuración de la sección en el caso de las propiedades de rigidez de elementos de concreto y mampostería, así como la contribución de las deformaciones de las zonas de panel para los desplazamientos generalizados de piso en los pórticos de acero resistentes a momentos. Se debe suponer que la estructura tiene una base fija o alternativamente se debe permitir usar consideraciones reales con relación a la rigidez y a las características de capacidad de carga de las fundaciones, consistentemente con los datos del suelo específico del sitio y los principios racionales de la mecánica de suelos.\n\n"
            "Se debe seleccionar un punto de control para cada modelo. Para estructuras sin altillos el punto de control debe ser en el centro de la masa del nivel más alto de la estructura. Para estructuras con altillos, el punto de control debe estar en el centro de la masa del nivel en la base del altillo."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_2_analisis",
        "seccion": "A-3.2.2 — Análisis",
        "titulo": "Apéndice A-3, A-3.2.2: análisis push-over (25 % de carga viva, fuerzas proporcionales al primer modo, hasta 150 % del desplazamiento objetivo, 125 %).",
        "texto": CAB + (
            "A-3.2.2 — Análisis — La estructura se debe analizar para la aplicación de las acciones sísmicas ocurriendo simultáneamente con los efectos de carga muerta combinadas con no menos del 25 por ciento de las cargas vivas requeridas por el diseño, reducidas como se permita para el área de un piso individual. Las fuerzas laterales se deben aplicar al centro de la masa de cada nivel y deben ser proporcionales a la distribución obtenida de un análisis modal para el modo fundamental de respuesta en la dirección que se está considerando. Las cargas laterales se deben incrementar de manera monotónica.\n\n"
            "Al incremento j de la carga lateral, el total de la fuerza lateral aplicada al modelo se debe caracterizar por el término Vj. Los aumentos de la fuerza lateral se deben realizar en incrementos que sean lo suficientemente pequeños para permitir detectar cambios significativos en el comportamiento de los componentes individuales (tales como fluencia, pandeo o falla). El primer incremento en la carga lateral debe producir un comportamiento elástico. En cada paso del análisis se debe registrar el total de la fuerza lateral aplicada Vj, el desplazamiento lateral del punto de control δj y las fuerzas y deformaciones de cada componente. El análisis se debe continuar hasta que el desplazamiento del punto de control sea por lo menos 150% del desplazamiento objetivo determinado de acuerdo con la Sección A-3.2.5. La estructura se debe diseñar para que el total de la fuerza lateral aplicada no disminuya en ningún paso del análisis para los desplazamientos del punto de control en un valor menor o igual al 125% del desplazamiento objetivo."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_3_resistencia_periodo",
        "seccion": "A-3.2.3 — Resistencia efectiva a la fluencia y periodo efectivo (ecuación A-3.2-1)",
        "titulo": "Apéndice A-3, A-3.2.3: curva bilineal (primer segmento al 60 % de la capacidad efectiva a la fluencia), Vy, δy y periodo efectivo Te = T1·raíz((V1/δ1)/(Vy/δy)).",
        "texto": CAB + (
            "A-3.2.3 — Resistencia efectiva a la fluencia y periodo efectivo — Se debe ajustar una curva bilineal a la curva de capacidad, de tal manera que el primer segmento de la curva bilineal coincida con la curva de capacidad al 60% de la capacidad efectiva a la fluencia; el segundo segmento debe coincidir con la curva de capacidad en el desplazamiento objetivo y el área bajo la curva bilineal debe ser igual al área bajo la curva de capacidad entre el origen y el desplazamiento objetivo. La resistencia efectiva a la fluencia Vy, corresponde al total de la fuerza lateral aplicada en la intersección de los dos segmentos. El desplazamiento efectivo de fluencia δy, corresponde al desplazamiento del punto de control en la intersección de los dos segmentos de línea.\n\n"
            "El periodo efectivo fundamental Te se debe determinar utilizando la siguiente ecuación:\n\n"
            "Te = T1 · raíz cuadrada [ (V1/δ1) / (Vy/δy) ]    (A-3.2-1)\n\n"
            "Donde: V1, δ1, y T1 se determinan para el primer incremento de la carga lateral.\n\n"
            "A-3.2.4 — Vector característico de forma — El vector característico de forma debe ser igual a la forma del primer modo de la estructura en la dirección que se está considerando, determinada por medio de un análisis modal de la estructura con las propiedades del primer incremento de la carga lateral, y normalizado para tener una amplitud unitaria en el nivel del punto de control. Se permite sustituir la forma deflectada de la estructura en el incremento en el que el desplazamiento del punto de control sea igual al desplazamiento efectivo de fluencia en lugar de la forma del modo, para determinar el vector de forma."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_5_desplazamiento_objetivo",
        "seccion": "A-3.2.5 — Desplazamiento objetivo (ecuaciones A-3.2-2 a A-3.2-5)",
        "titulo": "Apéndice A-3, A-3.2.5: desplazamiento objetivo δT = C0·C1·Sa·(Te/2π)²·g, C0 = Σmiφi/Σmiφi², C1 = (1/Rd)(1+(Rd−1)Tc/Te), Rd = Sa·M·g/Vy.",
        "texto": CAB + (
            "A-3.2.5 — Desplazamiento Objetivo — El desplazamiento objetivo del punto de control δT, se debe determinar utilizando la ecuación A-3.2-2 de la siguiente manera:\n\n"
            "δT = C0 · C1 · Sa · (Te / 2π)² · g    (A-3.2-2)\n\n"
            "Donde la aceleración espectral Sa, se determina como dice la Sección A.2.6 para el periodo fundamental efectivo Te, g es la aceleración de gravedad, y los coeficientes C0 y C1 se determinan de la siguiente manera:\n"
            "El coeficiente C0 se debe calcular utilizando la ecuación A-3.2-3 como:\n\n"
            "C0 = (Σ mi φi) / (Σ mi φi²)    (A-3.2-3)\n\n"
            "con las sumatorias para i = 1 hasta n.\n\n"
            "Donde:\n"
            "mi = la porción de la masa total M localizada en el Nivel i\n"
            "φi = la amplitud del vector característico de forma al Nivel i\n\n"
            "Cuando el periodo fundamental efectivo de la estructura en la dirección bajo consideración, Te, es mayor que Tc como lo define el numeral A.2.6.1.1, el coeficiente C1 se debe tomar como 1.0. De lo contrario el valor del coeficiente C1 se debe calcular utilizando la ecuación A-3.2-4 así:\n\n"
            "C1 = (1 / Rd) · [ 1 + (Rd − 1) · Tc / Te ]    (A-3.2-4)\n\n"
            "Donde Rd es dado por la ecuación A-3.2-5 de la siguiente manera:\n\n"
            "Rd = (Sa · M · g) / Vy    (A-3.2-5)\n\n"
            "Tc y Vy se definen arriba, Sa es la aceleración espectral del diseño en el periodo efectivo fundamental, Te es el periodo efectivo fundamental definido en la sección A-3.2.3 y M se define en la Sección A-3.1.4."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_6_a_3_2_8",
        "seccion": "A-3.2.6 a A-3.2.8 — Deriva de piso, resistencia de los elementos, distribución de fuerzas",
        "titulo": "Apéndice A-3, A-3.2.6 a A-3.2.8: deriva de piso al desplazamiento objetivo (límite de A.6.4.1), resistencia de elementos con sobreresistencia Ωo·Fs/R, distribución de fuerzas.",
        "texto": CAB + (
            "A-3.2.6 — Deriva de Piso — La deriva de piso Δ, tomada como el valor obtenido para cada piso al paso en el cual se alcanza el desplazamiento objetivo no debe exceder el límite de la deriva especificada en la Sección A.6.4.1.\n\n"
            "A-3.2.7 — Resistencia de los elementos — Además de satisfacer los requisitos de este apéndice, la resistencia de los elementos también debe satisfacer los requerimientos del paso 11 del numeral A.1.3.4 utilizando E = 0, excepto que el numeral A.3.3.9 deba aplicarse cuando el presente Reglamento específicamente requiere la consideración de sobreresistencia estructural en la fuerza sísmica de diseño.\n\n"
            "Cuando este Reglamento requiere la consideración de sobreresistencia estructural de acuerdo con el numeral A.3.3.9, el valor de la fuerza individual del miembro obtenida del análisis al nivel del desplazamiento objetivo debe ser substituida por Ωo·Fs/R.\n\n"
            "A-3.2.8 — Distribución de las fuerzas sísmicas de diseño — Las fuerzas laterales utilizadas para diseñar los elementos se deben aplicar a la masa de cada nivel y deben ser proporcionales a la distribución obtenida de un análisis modal para el modo fundamental de respuesta en la dirección que se está considerando."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_9_evaluacion_detallada",
        "seccion": "A-3.2.9 — Evaluación detallada (A-3.2.9.1 y A-3.2.9.2)",
        "titulo": "Apéndice A-3, A-3.2.9: evaluación detallada, cuándo no es necesaria (Vy mayor que factor de las Tablas A.3-1 a A.3-4 por Cs con Te), fuerzas y deformaciones requeridas, límites de deformación de elementos (dos tercios).",
        "texto": CAB + (
            "A-3.2.9 — Evaluación Detallada — No hay necesidad de cumplir con la Sección A-3.2.9.1 y la Sección A-3.2.9.2 si la resistencia efectiva de fluencia excede el producto del factor de sobreresistencia del sistema dado en las Tablas A.3-1 a A.3-4 del Capítulo A.3 y el cortante sísmico en la base determinado en la Sección A.4.3.1 del Capítulo A.4 modificada para usar el periodo Te fundamental efectivo, en lugar de T para la determinación de Cs.\n\n"
            "A-3.2.9.1 — Fuerza y deformación requeridas para el elemento — Para cada análisis estático no lineal los parámetros de respuesta del diseño, incluyendo las fuerzas individuales del elemento y las deformaciones del elemento γi, deben ser tomadas como los valores obtenidos del análisis en la iteración en la cual el desplazamiento objetivo se alcanza.\n\n"
            "A-3.2.9.2 — Elementos — La competencia de los elementos individuales y sus conexiones para resistir las fuerzas y las deformaciones de los elementos γi, se debe evaluar con base en datos de ensayos de laboratorio para componentes similares. Los efectos de gravedad y demás cargas sobre la capacidad de deformación de los elementos se deben considerar en estas evaluaciones. La deformación de un elemento para soportar las cargas de gravedad no debe exceder:\n\n"
            "(i) Dos tercios de la deformación que resulta en pérdida de capacidad para soportar cargas de gravedad.\n"
            "(ii) Dos tercios de la deformación a la cual la resistencia del elemento se ha deteriorado a menos del 70% de la resistencia pico del modelo del componente. La deformación de un elemento no requerida para soportar las cargas gravitacionales no debe exceder los dos tercios del valor al cual la resistencia del elemento se ha deteriorado a menos del 70% de la resistencia pico del modelo del componente. Alternativamente, se permite considerar la deformación del elemento como aceptable si la deformación no excede el valor determinado que establecen los criterios de aceptación para procedimientos no lineales dados en el Pre-Estándar y Comentario para la Rehabilitación Sísmica de Edificios (FEMA 356) para el nivel de desempeño de Seguridad de la Vida.\n\n"
            "Las fuerzas del elemento se deben considerar aceptables si no exceden las capacidades esperadas."
        ),
    },
    {
        "id": f"{PREFIJO}_A_3_2_10_revision_referencias",
        "seccion": "A-3.2.10 — Revisión del diseño; Referencias",
        "titulo": "Apéndice A-3, A-3.2.10: revisión independiente del diseño por comité de al menos dos ingenieros (Ley 400 de 1997); referencias ATC 40, FEMA 250, FEMA 356, HAZUS, ASCE/SEI 31 y 41.",
        "texto": CAB + (
            "A-3.2.10 — Revisión del Diseño — Un comité independiente integrado por al menos dos miembros, compuesto por ingenieros facultados según la Ley 400 de 1997 para diseñar en las disciplinas apropiadas y otros con experiencia en métodos de análisis sísmico y en la teoría y aplicación de análisis sísmico no lineal y comportamiento estructural bajo cargas sísmicas, debe llevar a cabo la revisión del diseño sismo resistente y los análisis estructurales de soporte. La revisión del diseño debe incluir:\n\n"
            "(i) Revisión de cualquier criterio sísmico específico para el sitio empleado en el análisis, incluyendo, de ser el caso, el desarrollo del espectro específico del sitio y\n"
            "(ii) Revisión de la determinación del desplazamiento objetivo y la resistencia efectiva de fluencia de la estructura.\n\n"
            "Para aquellas estructuras con resistencia efectiva de fluencia inferior al producto del factor de sobreresistencia del sistema como lo suministra las tablas A.3-1 a A.3-4 del Capítulo A.3 y el cortante sísmico en la base determinado en la Sección A.4.3.1 del Capítulo A.4, modificada para usar el periodo fundamental efectivo Te en lugar de T para la determinación de Cs, la revisión de diseño además debe incluir pero no se debe limitar a lo siguiente:\n\n"
            "(1) Revisión de los criterios de aceptación utilizados para demostrar la idoneidad de los elementos estructurales y de los sistemas para resistir la fuerza calculada y las demandas de deformación, junto con datos de laboratorio y demás datos usados para soportar tales criterios. Revisión de los criterios de aceptación para procedimientos no lineales dados en el Pre-Estándar y Comentario para la Rehabilitación Sísmica de Edificios (FEMA 356) es discrecional por parte del equipo de revisión del diseño.\n"
            "(2) Revisión del diseño final de todo el sistema estructural y todos los análisis de soporte. El equipo de revisión del diseño debe producir un informe que identifique, dentro del alcance de la revisión, las preocupaciones significativas y cualquier discrepancia de cumplimiento general con las disposiciones del Reglamento.\n\n"
            "REFERENCIAS\n\n"
            "ATC 40 (SSC, 1996) Seismic Evaluation and Retrofit of Concrete Buildings, SSC Report No. 96-01, Seismic Safety Commission, State of California, Sacramento, California, Developed by the Applied Technology Council, Redwood City, California.\n"
            "FEMA 250 (FEMA 2000a), Recommended Seismic Design Criteria for New Steel Moment-Frame Buildings, Federal Emergency Management Agency, Washington D.C.\n"
            "FEMA 356 (FEMA, 2000b), Prestandard and Commentary for Seismic Rehabilitation of Buidings, Federal Emergency Management Agency, Washington D.C.\n"
            "HAZUS (NIBS, 1999), HAZUS99 Technical Manual, National Institute of Building Science, Washington D.C. Developed by the Federal Emergency Management Agency through agreements with the National Institute of Building Sciences.\n"
            "ASCE/SEI (2003), \"Seismic Evaluation of Existing Buildings\", ASCE/SEI 31-03, American Society of Civil Engineers, Reston, Virginia, USA, 2003\n"
            "ASCE/SEI (2006), \"Seismic Rehabilitation of Existing Buildings\", ASCE/SEI 41-06, American Society of Civil Engineers, Reston, Virginia, USA, 2006"
        ),
    },
]


def main():
    print(f"{len(CHUNKS)} chunks padre definidos (se suben via el script de re-troceo).")


if __name__ == "__main__":
    main()
