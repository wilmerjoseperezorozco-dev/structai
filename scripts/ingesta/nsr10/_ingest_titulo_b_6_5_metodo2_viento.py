"""
NSR-10 Titulo B, Capitulo B.6 (Fuerzas de viento) -- cierra el hueco mas
grande de contenido pendiente en todo el proyecto (~61 paginas reales,
B-21 a B-82 del PDF fuente): el Metodo 2 - Procedimiento Analitico
completo (B.6.5) mas el Metodo 3 - Procedimiento de Tunel de Viento
(B.6.6).

Ya estaban cargados antes de esta ronda: B.6.1 (Alcance), B.6.2-B.6.4
(definiciones + Metodo 1 Simplificado completo) y B.6.5.6.3
(categorias de exposicion B/C/D). Este script cubre el resto de B.6.5.1
a B.6.5.15 y B.6.6.1 a B.6.6.4.1 -- es decir, todo el texto normativo
(clausulas) del Metodo 2 y el Metodo 3.

Fuera de alcance deliberadamente (ver nota "PENDIENTE" en cada chunk
donde aplica): las ~19 figuras graficas B.6.5-1 a B.6.5-19 (tablas de
coeficientes Cp/GCp/GCpf/Cf, factor topografico Kzt tabulado, etc.) y
las Tablas B.6.5-1 (factor de importancia por grupo de uso) y B.6.5-2
(constantes zmin/c/A/eps/b/alpha para el factor de rafaga) -- son
contenido grafico/tabular denso que el extractor de PDF no capturo
como texto limpio; requieren digitalizacion manual dedicada en una
ronda futura, igual que se dejo anotado en el chunk B.6.5.6 ya
existente.

Nota de fidelidad: dos pasajes del PDF fuente llegaron con el orden de
palabras alterado por el extractor OCR (fragmentacion tipica de
formulas con fracciones/subindices). Se reconstruyeron por dos vias:
(a) para el parrafo de B.6.5.12.4.2 sobre vidrios/aberturas, cruzando
contra el parrafo paralelo casi identico de B.6.5.12.2.1 (misma
clausula, se repite para los dos umbrales de altura del edificio);
(b) para las formulas con fracciones muy fragmentadas (ecuaciones
B.6.5-2 a B.6.5-12 del factor de rafaga, y B.6.5-19 de excentricidad),
se conservan los numeros de ecuacion y las variables pero se advierte
explicitamente que el formato exacto de la fraccion debe verificarse
contra el documento fuente antes de usarse en un calculo real.

Fuente: mismo archivo Drive usado para B.6.1-B.6.4 el 2026-08-20
(id 1ZLlTm7J__ucSvEt99qizpl3AocB12naL, rango_paginas_drive 240-301),
paginas internas B-26 a B-38 aprox (capitulo B.6 completo).

Uso: python _ingest_titulo_b_6_5_metodo2_viento.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título B — Cargas (Capítulo B.6, Fuerzas de viento)"

CHUNKS = [
    {
        "id": "NSR10-B-B_6_5_1_a_3",
        "seccion": "B.6.5.1 a B.6.5.3",
        "titulo": (
            "Metodo 2 Analitico de viento: alcance (edificio regular, sin "
            "respuesta transversal/vortices), limitaciones (usar literatura "
            "reconocida o tunel de viento B.6.6 si no aplica) y "
            "procedimiento de diseno paso a paso (a-j) que enumera todas "
            "las secciones B.6.5.4 a B.6.5.15."
        ),
        "texto": (
            "NSR-10 Título B — Cargas. Capítulo B.6 — Fuerzas de viento. "
            "B.6.5 — Método 2 — Procedimiento Analítico.\n\n"
            "B.6.5.1 — ALCANCE — Un edificio cuyas cargas de viento de "
            "diseño sean determinadas de acuerdo con esta sección deberá "
            "cumplir las siguientes condiciones:\n"
            "(a) El edificio o estructura sea de forma regular como se "
            "define en la sección B.6.2.\n"
            "(b) El edificio o estructura no tiene características de "
            "respuesta que den lugar a cargas transversales de viento, "
            "generación de vórtices, inestabilidad debida a golpeteo o "
            "aleteo y que por su ubicación, tampoco deben merecer "
            "consideración especial los efectos de canalización o "
            "sacudimiento por la estela producida por las obstrucciones a "
            "barlovento.\n\n"
            "B.6.5.2 — LIMITACIONES — Las especificaciones de la sección "
            "B.6.5 consideran el efecto del aumento de cargas producto de "
            "la resonancia entre ráfagas y vibraciones en la dirección del "
            "viento en edificios flexibles y otras estructuras. Los "
            "edificios o estructuras que no cumplan las consideraciones de "
            "la sección B.6.5.1 o aquellos que tengan forma irregular o "
            "características de respuesta inusuales, deberán ser "
            "diseñados usando literatura reconocida que documente esos "
            "efectos de las cargas de viento o deberán ser diseñados "
            "usando el procedimiento de túnel de viento especificado en "
            "la sección B.6.6.\n\n"
            "B.6.5.2.1 — Protección de otras edificaciones — No se harán "
            "reducciones de presiones de velocidad producto del "
            "apantallamiento de otras estructuras aledañas o producto de "
            "las características del terreno.\n\n"
            "B.6.5.2.2 — Revestimientos Permeables — Para determinar las "
            "cargas aplicables a revestimientos permeables se usarán las "
            "especificaciones de la sección B.6.5 a menos que se "
            "demuestre con ensayos aprobados o literatura reconocida que "
            "las cargas son menores.\n\n"
            "B.6.5.3 — PROCEDIMIENTO DE DISEÑO\n"
            "(a) La velocidad básica de viento V, y el factor de "
            "dirección de viento Kd se determinarán de acuerdo con la "
            "sección B.6.5.4.\n"
            "(b) El factor de importancia I se determinará de acuerdo con "
            "la sección B.6.5.5.\n"
            "(c) Se determinará para cada dirección de viento una o unas "
            "categorías de exposición Kz y un coeficiente de exposición "
            "para la presión por velocidad Kh, de acuerdo con la sección "
            "B.6.5.6.\n"
            "(d) El factor topográfico Kzt se determinará de acuerdo con "
            "la sección B.6.5.7.\n"
            "(e) El factor de efecto de ráfaga G o Gf, según aplique, se "
            "determinará de acuerdo con la sección B.6.5.8.\n"
            "(f) La clasificación de cerramiento se determinará de "
            "acuerdo con la sección B.6.5.9.\n"
            "(g) El Coeficiente de Presión Interna GCpi se determinará de "
            "acuerdo con la sección B.6.5.11.1.\n"
            "(h) El Coeficiente de Presión Externo Cp o GCpf o los "
            "Coeficientes de Fuerza Cf, según aplique, se determinarán de "
            "acuerdo con la sección B.6.5.11.2 o B.6.5.11.3 "
            "respectivamente.\n"
            "(i) La presión por velocidad qz o qh, según aplique, se "
            "determinará de acuerdo con la sección B.6.5.10.\n"
            "(j) La Carga de Viento de Diseño p o F se determinará de "
            "acuerdo con las secciones B.6.5.12, B.6.5.13, B.6.5.14 y "
            "B.6.5.15, según aplique."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_4",
        "seccion": "B.6.5.4 (Velocidad de viento básica)",
        "titulo": (
            "Velocidad basica de viento V se toma de la Fig. B.6.4-1 "
            "(mapa de zonas de amenaza eolica de Colombia, ya cargado); "
            "regiones especiales, estimacion a partir de datos climaticos "
            "regionales con procedimientos estadisticos aprobados, "
            "tornados excluidos, factor de direccion de viento Kd "
            "(Tabla B.6.5-4)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.4 — VELOCIDAD DE VIENTO "
            "BÁSICA — La velocidad de viento básica, V, usada en la "
            "determinación de las cargas de viento de diseño de edificios "
            "y otras estructuras se tomará de la Fig. B.6.4-1, excepto con "
            "lo especificado en las secciones B.6.5.4.1 y B.6.5.4.2. Se "
            "supondrá que el viento proviene de cualquier dirección "
            "horizontal.\n\n"
            "B.6.5.4.1 — Regiones Especiales para Viento — La velocidad "
            "básica de viento se incrementará donde existan registros o "
            "la experiencia indique velocidades de viento mayores que las "
            "expresadas en la fig. B.6.4-1. Terrenos montañosos, "
            "precipicios y las regiones especiales de la figura B.6.4-1 "
            "se deberán estudiar para determinar si existen condiciones "
            "de viento inusuales. La autoridad respectiva ajustará los "
            "valores de la fig. B.6.4-1 para reflejar velocidades de "
            "viento locales mayores. Este ajuste se debe hacer basado en "
            "información meteorológica y en una estimación de la "
            "velocidad básica del viento según las especificaciones de la "
            "sección B.6.5.4.2.\n\n"
            "B.6.5.4.2 — Estimación de la Velocidad Básica del Viento a "
            "partir de Información Climática Regional — Los datos "
            "climáticos regionales se pueden usar en lugar de las "
            "velocidades básicas de viento dadas en la figura B.6.4-1 "
            "solamente cuando la autoridad competente considere que se "
            "han cumplido las siguientes condiciones:\n"
            "B.6.5.4.2.1 — Se han utilizado procedimientos estadísticos "
            "aprobados para el análisis de valores extremos en el "
            "tratamiento de los datos, y\n"
            "B.6.5.4.2.2 — Se han tenido en cuenta la longitud de "
            "registros, el error de muestreo, el tiempo promedio, la "
            "altura del anemómetro, la calidad de los datos y la "
            "exposición del terreno.\n\n"
            "B.6.5.4.3 — Limitaciones — Los tornados NO se han "
            "considerado en los cálculos de la velocidad de viento "
            "básica.\n\n"
            "B.6.5.4.4 — Factor de Dirección de Viento — El Factor de "
            "Dirección de Viento, Kd, se determinará con la tabla "
            "B.6.5-4. Este factor solo aplicará cuando se use "
            "conjuntamente con las combinaciones de carga especificadas "
            "en las secciones B.2.3 y B.2.4."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_5",
        "seccion": "B.6.5.5 (Factor de importancia)",
        "titulo": (
            "Factor de importancia I para viento se determina de la Tabla "
            "B.6.5-1 segun grupos de uso de la seccion A.2.5. NOTA: los "
            "valores numericos de la tabla son contenido grafico no "
            "capturado en esta ronda."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.5 — FACTOR DE "
            "IMPORTANCIA — El factor de importancia, I, para el edificio "
            "u otra estructura debe determinarse de la tabla B.6.5-1, de "
            "acuerdo con los grupos de uso presentados en la sección "
            "A.2.5.\n\n"
            "PENDIENTE: la Tabla B.6.5-1 (valores numéricos de I por "
            "grupo de uso I/II/III/IV) es una tabla gráfica que no quedó "
            "capturada como texto en esta extracción; se referencia por "
            "número pero sus valores deben verificarse contra el PDF "
            "original antes de usarse en un cálculo. Los grupos de uso "
            "(I a IV) ya están cargados en el Título A (sección A.2.5)."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_6_1_2",
        "seccion": "B.6.5.6, B.6.5.6.1, B.6.5.6.2",
        "titulo": (
            "Exposicion al viento: se evalua por 2 sectores de 45 grados a "
            "barlovento de cada direccion de viento (B.6.5.6.1); "
            "categorias de RUGOSIDAD de terreno B/C/D segun tipo de "
            "obstrucciones (B.6.5.6.2) -- paso previo a asignar la "
            "categoria de EXPOSICION (B.6.5.6.3, ya cargada)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.6 — EXPOSICIÓN — Para "
            "cada dirección de viento considerada, la categoría de "
            "exposición a barlovento se determinará con base en la "
            "rugosidad del terreno que a su vez es determinada por la "
            "topografía natural, la vegetación y las estructuras "
            "construidas en éste.\n\n"
            "B.6.5.6.1 — Direcciones de Viento y Sectores — Para cada "
            "dirección de viento seleccionada para la evaluación de "
            "cargas de viento, se debe determinar la exposición del "
            "edificio o la estructura para los dos sectores a barlovento "
            "que se extienden a 45° a cada lado de la dirección de viento "
            "elegida. Las exposiciones en estos dos sectores se deben "
            "determinar de acuerdo con las secciones B.6.5.6.2 y "
            "B.6.5.6.3. La exposición que produzca las mayores cargas de "
            "viento se usará para representar el viento de esa "
            "dirección.\n\n"
            "B.6.5.6.2 — Categorías de Rugosidad de Terreno — Escogiendo "
            "entre las categorías de este numeral, se determinará la "
            "rugosidad del terreno dentro de cada sector de 45° para una "
            "distancia viento arriba como se define en la sección "
            "B.6.5.6.3. Esto se hace con el propósito de asignarle al "
            "terreno una categoría de exposición como se define en la "
            "sección B.6.5.6.3.\n\n"
            "Rugosidad de Terreno B — Áreas urbanas y suburbanas, áreas "
            "boscosas u otros terrenos con numerosas obstrucciones del "
            "tamaño, iguales o mayores al de una vivienda unifamiliar y "
            "con poca separación entre ellas.\n\n"
            "Rugosidad de Terreno C — Terreno abierto con pocas "
            "obstrucciones y con alturas inferiores a 9.0 m. Esta "
            "categoría incluye campos planos abiertos, praderas y todas "
            "las superficies acuáticas en zonas propensas a huracanes.\n\n"
            "Rugosidad de Terreno D — Áreas planas y no obstruidas y "
            "superficies acuáticas por fuera de regiones propensas a "
            "huracanes. Esta categoría incluye pantanos, salinas y "
            "superficies de hielo."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_6_4_a_6",
        "seccion": "B.6.5.6.4 a B.6.5.6.6",
        "titulo": (
            "Categorias de exposicion aplicadas al SPRFV (edificios en "
            "general vs. edificios bajos), a componentes/revestimientos, "
            "y el coeficiente de exposicion de presion por velocidad Kz/Kh "
            "de la Tabla B.6.5-3 (permite interpolar en zonas de "
            "transicion)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.6.4 — Categorías de "
            "Exposición para el SPRFV.\n\n"
            "B.6.5.6.4.1 — Edificios y Otras Estructuras — Las cargas de "
            "viento para el diseño del SPRFV determinadas de la fig. "
            "B.6.5-3 deberán basarse en las categorías de exposición "
            "definidas en la sección B.6.5.6.3, para cada dirección de "
            "viento considerada.\n\n"
            "B.6.5.6.4.2 — Edificios Bajos — Las cargas de viento para el "
            "diseño del SPRFV de edificios bajos se determinarán usando "
            "una presión por velocidad qh basada en la categoría de "
            "exposición que produzca las mayores cargas de viento para "
            "cualquier dirección de viento donde se usen los coeficientes "
            "de presión externa GCpf dados en la fig. B.6.5-7.\n\n"
            "B.6.5.6.5 — Categoría de Exposición para Componentes y "
            "Elementos de Revestimiento — Las presiones de diseño para "
            "componentes y elementos de revestimiento, en edificios y "
            "otras estructuras, deberán basarse en la exposición que dé "
            "por resultado las mayores cargas de viento en cualquier "
            "dirección de viento.\n\n"
            "B.6.5.6.6 — Coeficiente de Exposición de Presión por "
            "velocidad — Basado en la categoría de exposición "
            "determinada en la sección B.6.5.3, se define de la Tabla "
            "B.6.5-3 un coeficiente de exposición de presión por "
            "velocidad Kz o Kh, según aplique. Para una edificación que "
            "se ubique en una zona de transición entre categorías de "
            "exposición, es decir cerca a un cambio de rugosidad de "
            "terreno, se permitirá tomar valores intermedios de Kz o Kh, "
            "siempre y cuando se determinen por medio de un método "
            "racional de análisis definido en la literatura reconocida.\n\n"
            "PENDIENTE: la Tabla B.6.5-3 (valores numéricos de Kz/Kh por "
            "altura y categoría de exposición) es una tabla gráfica no "
            "capturada como texto en esta ronda."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_7",
        "seccion": "B.6.5.7 (Efectos topográficos)",
        "titulo": (
            "Factor topografico Kzt para aumento de velocidad de viento "
            "sobre colinas/escarpes aisladas; 5 condiciones de "
            "aplicabilidad (a-e) sobre geometria del terreno; ecuacion "
            "B.6.5-1: Kzt=(1+K1*K2*K3)^2, o Kzt=1.0 si no se cumplen las "
            "condiciones."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.7 — EFECTOS "
            "TOPOGRÁFICOS.\n\n"
            "B.6.5.7.1 — Aumento de velocidad sobre Colinas o Escarpes — "
            "Se deben incluir en el diseño los efectos de aumento de "
            "velocidad del viento sobre colinas aisladas, o escarpes, que "
            "constituyan cambios abruptos en la topografía general. Los "
            "edificios, las condiciones del sitio y la localización deben "
            "cumplir TODAS las siguientes condiciones:\n"
            "(a) Que la colina o escarpe esté aislada y sin obstrucciones "
            "en barlovento, por otros accidentes topográficos de altura "
            "cercana a 100 veces su altura (100H) o 3 km, la que sea "
            "menor. La distancia se mide horizontalmente del punto desde "
            "el cual se mide la altura H de la loma, colina o escarpe.\n"
            "(b) Que la colina o escarpe sobresalga por encima del "
            "terreno viento arriba por un factor de 2 o más, dentro de un "
            "radio de 3 km.\n"
            "(c) Que la estructura esté localizada en la mitad superior "
            "de la colina o cerca de la cresta del escarpe (fig. "
            "B.6.5-1).\n"
            "(d) Que H/Lh ≥ 0.2.\n"
            "(e) H es mayor o igual a 4.5 m para la Exposición C y D, y "
            "18 m para la Exposición B.\n\n"
            "B.6.5.7.2 — Factor Topográfico — El efecto de aumento de "
            "velocidad de viento se incluirá en el cálculo de cargas de "
            "viento de diseño usando el factor Kzt:\n\n"
            "Kzt = (1 + K1·K2·K3)² (Ecuación B.6.5-1)\n\n"
            "Donde K1, K2 y K3 se dan en la Fig. B.6.5-1 (multiplicadores "
            "topográficos por forma de colina/escarpe y exposición — "
            "tabla gráfica no capturada en esta ronda). Si el sitio o la "
            "localización de la estructura NO cumple las condiciones "
            "especificadas en la sección B.6.5.7.1, entonces Kzt = 1.0."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_8",
        "seccion": "B.6.5.8 (Factor de efecto ráfaga)",
        "titulo": (
            "Factor de efecto rafaga G para estructuras rigidas (valor "
            "simplificado 0.85 o calculado con la Ec. B.6.5-2, intensidad "
            "de turbulencia Iz Ec. B.6.5-3) y Gf para estructuras "
            "flexibles/dinamicamente sensibles (Ecs. B.6.5-6 a B.6.5-12: "
            "resonancia gR, factor de respuesta R, velocidad Vz); "
            "alternativa: analisis racional (8.3); limitacion cuando ya "
            "viene combinado en tablas GCp/GCpi/GCpf (8.4)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.8 — FACTOR DE EFECTO "
            "RÁFAGA.\n\n"
            "B.6.5.8.1 — Estructuras Rígidas — Para estructuras rígidas "
            "como se definen en la sección B.6.2, el factor de efecto "
            "ráfaga se tomará como G = 0.85, o se calculará con la "
            "fórmula de la Ecuación B.6.5-2 (función de gQ, Iz y gv, con "
            "gQ = gv = 3.4), usando la intensidad de turbulencia Iz de la "
            "Ecuación B.6.5-3 evaluada a la altura equivalente z = 0.6h "
            "(no menor que zmin). Para cada exposición, zmin y la "
            "constante c se listan en la Tabla B.6.5-2. La respuesta del "
            "entorno Q se define con la Ecuación B.6.5-4, en función de B "
            "y h (sección B.6.3) y de la longitud integral a escala de la "
            "turbulencia Lz (Ecuación B.6.5-5, con constantes A y "
            "ε de la Tabla B.6.5-2).\n\n"
            "B.6.5.8.2 — Estructuras Flexibles o Dinámicamente Sensibles "
            "— Para estructuras flexibles o dinámicamente sensibles "
            "(sección B.6.2), el factor efecto ráfaga Gf se calcula con "
            "la Ecuación B.6.5-6 (gQ = gv = 3.4; gR se calcula con la "
            "Ecuación B.6.5-7, función del logaritmo de 3600·n1, la "
            "frecuencia natural del edificio). El factor de respuesta de "
            "resonancia R se calcula con la Ecuación B.6.5-8, que "
            "depende del coeficiente de amortiguamiento β, y de los "
            "factores Rn (Ecuación B.6.5-9, función de N1 — Ecuación "
            "B.6.5-10), Rh, RB y RL (todos con la forma de la Ecuación "
            "B.6.5-11, evaluados con η igual a 4.6·n1·h/Vz, "
            "4.6·n1·B/Vz y 15.4·n1·L/Vz respectivamente). Vz es la "
            "velocidad de viento promediada por hora a la altura z "
            "(Ecuación B.6.5-12, con constantes b y α de la Tabla "
            "B.6.5-2, y V la velocidad básica de viento en m/s).\n\n"
            "B.6.5.8.3 — Análisis Racional — En lugar de los "
            "procedimientos de las secciones B.6.5.8.1 y B.6.5.8.2, se "
            "permite determinar el factor efecto ráfaga por medio de "
            "cualquier método racional definido en literatura "
            "reconocida.\n\n"
            "B.6.5.8.4 — Limitaciones — Donde aparezcan en tablas "
            "coeficientes de presión y factores de efecto ráfaga "
            "combinados (GCp, GCpi y GCpf), NO se calculará el factor "
            "efecto ráfaga por separado.\n\n"
            "PENDIENTE / NOTA DE FIDELIDAD: las Ecuaciones B.6.5-2 a "
            "B.6.5-12 usan fracciones y subíndices que el extractor de "
            "PDF fragmentó; se conservan aquí los números de ecuación, "
            "las variables y su significado, pero el formato exacto de "
            "cada fracción (numerador/denominador) debe verificarse "
            "contra el documento fuente antes de usarse en un cálculo "
            "real. La Tabla B.6.5-2 (constantes zmin, c, A, ε, b, α por "
            "categoría de exposición) es una tabla gráfica no capturada."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_9",
        "seccion": "B.6.5.9 (Clasificación de cerramientos)",
        "titulo": (
            "Clasificacion de cerramientos (cerrado/parcialmente "
            "cerrado/abierto) para coeficientes de presion interna; "
            "vidrios en zonas propensas a huracanes deben protegerse "
            "(ASTM E1886/E1996) salvo excepciones por altura o categoria "
            "de uso I; regla de clasificaciones multiples."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.9 — CLASIFICACIONES DE "
            "LOS CERRAMIENTOS.\n\n"
            "B.6.5.9.1 — General — Para efectos de la determinación de "
            "coeficientes de presión interna, todos los edificios se "
            "deben clasificar como cerrados, parcialmente cerrados o "
            "abiertos de acuerdo con la sección B.6.2.\n\n"
            "B.6.5.9.2 — Aberturas — Se deben cuantificar las aberturas "
            "en el cerramiento del edificio para determinar la "
            "clasificación de cerramiento como se define en la sección "
            "B.6.5.9.1.\n\n"
            "B.6.5.9.3 — Zonas propensas a huracanes — Los vidrios de "
            "edificios localizados en zonas propensas a huracanes, "
            "deberán protegerse con una cobertura resistente a impacto o "
            "ser vidrios resistentes a impactos de acuerdo con los "
            "requerimientos de las normas ASTM E1886 y ASTM E1996 u "
            "otros métodos de ensayo aprobados y criterios de "
            "desempeño.\n"
            "EXCEPCIONES:\n"
            "(a) Podrán no estar protegidos los vidrios en edificios de "
            "categoría II, III o IV localizados a más de 18.0 m por "
            "encima del nivel del suelo y a más de 9.0 m sobre cubiertas "
            "con superficies de agregado localizados a 450 m al interior "
            "del edificio.\n"
            "(b) Se permiten los vidrios sin protección en edificios de "
            "categoría I.\n\n"
            "B.6.5.9.4 — Clasificaciones Múltiples — Si por definición un "
            "edificio cumple con los parámetros de edificio “abierto” y "
            "“parcialmente cerrado”, se clasificará como un edificio "
            "“abierto”. Un edificio que no cumpla con las definiciones de "
            "edificio “abierto” o “parcialmente cerrado” se clasificará "
            "como un edificio “cerrado”."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_10_11",
        "seccion": "B.6.5.10, B.6.5.11",
        "titulo": (
            "Presion por velocidad qz = 0.613*Kz*Kzt*Kd*V^2 (Ec. "
            "B.6.5-13, coef. numerico 0.613 salvo mejor dato "
            "climatologico); coeficientes de presion interna GCpi "
            "(11.1, con factor de reduccion Ri para edificios de gran "
            "volumen Ec. B.6.5-14) y externa Cp/GCpf/GCp para SPRFV y "
            "componentes/revestimientos (11.2), coeficientes de fuerza "
            "Cf (11.3), cornisas (11.4) y parapetos (11.5) -- remiten a "
            "figuras."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.10 — PRESIÓN POR "
            "VELOCIDAD — La presión por velocidad, qz, evaluada a la "
            "altura z se calculará con:\n\n"
            "qz = 0.613 · Kz · Kzt · Kd · V² en N/m²; V en m/s "
            "(Ecuación B.6.5-13)\n\n"
            "Donde Kd es el factor de dirección de viento (sección "
            "B.6.5.4.4), Kz es el coeficiente de exposición de presión "
            "por velocidad (sección B.6.5.6.6), Kzt es el factor "
            "topográfico (sección B.6.5.7.2), y qh es la presión por "
            "velocidad calculada con la Ecuación B.6.5-13 a la altura "
            "media de la cubierta, h. El coeficiente numérico 0.613 se "
            "usará siempre que no haya suficientes registros climáticos "
            "para justificar la selección de otro valor.\n\n"
            "B.6.5.11 — COEFICIENTES DE PRESIÓN Y FUERZA.\n\n"
            "B.6.5.11.1 — Coeficiente de Presión Interna — Los "
            "coeficientes de presión interna, GCpi, se determinan de la "
            "Figura B.6.5-2 según la clasificación de cerramientos "
            "(sección B.6.5.9).\n"
            "B.6.5.11.1.1 — Factor de Reducción para edificios de gran "
            "volumen, Ri — Para un edificio parcialmente cerrado con un "
            "solo espacio sin particiones, GCpi se multiplica por Ri "
            "(Ecuación B.6.5-14, ≤ 1.0), donde Aog = área total de "
            "aberturas en el cerramiento (m²) y Vi = volumen interno sin "
            "particiones (m³).\n\n"
            "B.6.5.11.2 — Coeficientes de Presión Externa.\n"
            "B.6.5.11.2.1 — SPRFV — Los coeficientes de presión externa, "
            "Cp, para el Sistema Principal de Resistencia de Fuerzas de "
            "Viento se dan en las figs. B.6.5-3, B.6.5-4 y B.6.5-5. Las "
            "combinaciones de coeficientes de presión externa y factores "
            "de efecto ráfaga, GCpf, para edificios bajos se dan en la "
            "fig. B.6.5-7 y no se toman por separado.\n"
            "B.6.5.11.2.2 — Revestimiento y Componentes — Las "
            "combinaciones GCp para elementos de revestimiento y "
            "componentes se dan en las figs. B.6.5-8A a B.6.5-14 y no se "
            "toman por separado.\n\n"
            "B.6.5.11.3 — Coeficientes de Fuerza, Cf — Se dan en las "
            "figs. B.6.5-17 a B.6.5-19.\n\n"
            "B.6.5.11.4 — Cornisas de cubiertas.\n"
            "B.6.5.11.4.1 — SPRFV — Los aleros a barlovento se diseñan "
            "con presión positiva en la cara inferior (Cp = 0.8) más las "
            "presiones de las figs. B.6.5-3 y B.6.5-5.\n"
            "B.6.5.11.4.2 — Revestimiento y Componentes — Los aleros se "
            "diseñan con los coeficientes de presión de las figs. "
            "B.6.5-8B, C y D.\n\n"
            "B.6.5.11.5 — Parapetos.\n"
            "B.6.5.11.5.1 — SPRFV — Coeficientes de presión de la "
            "sección B.6.5.12.2.4.\n"
            "B.6.5.11.5.2 — Revestimiento y Componentes — Se toman de las "
            "tablas de coeficientes de cubiertas y paredes (sección "
            "B.6.5.12.4.4).\n\n"
            "PENDIENTE: las figuras B.6.5-2 a B.6.5-19 (tablas gráficas "
            "de coeficientes) no están capturadas como texto en esta "
            "ronda."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_12_1_2",
        "seccion": "B.6.5.12.1, B.6.5.12.2",
        "titulo": (
            "Formula general de fuerzas de viento en edificios cerrados o "
            "parcialmente cerrados: p = qGCp - qi(GCpi) para edificios "
            "rigidos (Ec. B.6.5-15), version simplificada para edificios "
            "bajos con GCpf (Ec. B.6.5-16), version para edificios "
            "flexibles con Gf (Ec. B.6.5-17), y formula de parapetos "
            "pp = qpGCpn con GCpn=+1.5/-1.0 (Ec. B.6.5-18)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.12 — FUERZAS DE VIENTO "
            "DE DISEÑO EN EDIFICIOS CERRADOS O PARCIALMENTE CERRADOS.\n\n"
            "B.6.5.12.1 — General.\n"
            "B.6.5.12.1.1 — Convención de Signos — Las presiones "
            "positivas actúan hacia la superficie en estudio y las "
            "negativas actúan hacia afuera de la superficie en "
            "estudio.\n"
            "B.6.5.12.1.2 — Condición de Carga Crítica — Los valores de "
            "presiones internas y externas se combinan algebraicamente "
            "para determinar el caso de carga más crítico.\n"
            "B.6.5.12.1.3 — Áreas Aferentes Mayores de 65 m² — Los "
            "elementos de revestimiento y componentes con área aferente "
            "mayor a 65 m² se pueden diseñar usando las especificaciones "
            "del SPRFV.\n\n"
            "B.6.5.12.2 — Sistemas Principales de Resistencia de Fuerzas "
            "de Viento.\n"
            "B.6.5.12.2.1 — Edificios Rígidos de Cualquier Altura — "
            "Presión de diseño:\n\n"
            "p = qGCp − qi(GCpi) en N/m² (Ecuación B.6.5-15)\n\n"
            "Donde: q = qz para paredes a barlovento (evaluada a altura "
            "z); q = qh para paredes a sotavento, laterales y cubiertas "
            "(altura h); qi = qh para todas las paredes y cubiertas de "
            "edificios cerrados y para presiones internas negativas en "
            "edificios parcialmente cerrados; qi = qz para presiones "
            "internas positivas en edificios parcialmente cerrados, "
            "donde z es el nivel de la abertura más elevada que podría "
            "afectar la presión interna positiva. En regiones donde el "
            "viento pueda arrastrar fragmentos, los vidrios en los 20 m "
            "inferiores que no sean resistentes al impacto (ni estén "
            "protegidos) se tratan como una abertura del edificio "
            "(sección B.6.5.9.3); para la evaluación conservadora de la "
            "presión interna positiva, qi se puede evaluar a la altura h "
            "(qi = qh). G = factor de efecto ráfaga (sección B.6.5.8); "
            "Cp = coeficientes de presión externa (figs. B.6.5-3 o "
            "B.6.5-5); GCpi = coeficientes de presión interna (fig. "
            "B.6.5-2). q y qi se evalúan con la exposición de la sección "
            "B.6.5.6.3; las presiones se aplican simultáneamente en "
            "paredes a barlovento/sotavento y cubiertas.\n\n"
            "B.6.5.12.2.2 — Edificios Bajos — Alternativa:\n\n"
            "p = qh[(GCpf) − (GCpi)] en N/m² (Ecuación B.6.5-16)\n\n"
            "Donde qh se evalúa a la altura media de la cubierta con la "
            "exposición de B.6.5.6.3; GCpf de la fig. B.6.5-7; GCpi de "
            "la fig. B.6.5-2.\n\n"
            "B.6.5.12.2.3 — Edificios Flexibles:\n\n"
            "p = qGfCp − qi(GCpi) en N/m² (Ecuación B.6.5-17)\n\n"
            "Donde q, qi y GCpi se definen igual que en B.6.5.12.2.1, y "
            "Gf es el factor de efecto ráfaga de estructuras flexibles "
            "(sección B.6.5.8.2).\n\n"
            "B.6.5.12.2.4 — Parapetos — Para SPRFV de edificios rígidos, "
            "bajos o flexibles con cubiertas planas, a dos o cuatro "
            "aguas:\n\n"
            "pp = qpGCpn en N/m (Ecuación B.6.5-18)\n\n"
            "Donde pp = presión neta combinada en el parapeto (positiva "
            "hacia el frente, negativa hacia afuera); qp = presión por "
            "velocidad evaluada en la parte más alta del parapeto; GCpn "
            "= coeficiente de presión neta combinada = +1.5 para "
            "parapeto a barlovento, = −1.0 para parapeto a sotavento."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_12_3_4",
        "seccion": "B.6.5.12.3, B.6.5.12.4",
        "titulo": (
            "Casos de carga de viento de diseno (4 casos de la fig. "
            "B.6.5-6, incl. excentricidad para estructuras flexibles Ec. "
            "B.6.5-19, con excepcion para edificios pequenos/livianos) y "
            "formulas de presion para elementos de revestimiento y "
            "componentes segun altura (Ecs. B.6.5-20 a B.6.5-22): "
            "h<=18m, h>18m, alternativa 18-27m, y parapetos."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.12.3 — CASOS DE CARGA "
            "DE VIENTO DE DISEÑO — El SPRFV de edificios de cualquier "
            "altura, cuyas cargas se hayan determinado bajo las "
            "secciones B.6.5.12.2.1 y B.6.5.12.2.3, se debe diseñar "
            "considerando los 4 casos de carga de la fig. B.6.5-6 "
            "(Caso 1: presión total sobre cada eje principal por "
            "separado; Caso 2: 3/4 de la presión sobre cada eje principal "
            "junto con un momento torsional; Caso 3: Caso 1 más el 75% "
            "del valor especificado actuando simultáneamente; Caso 4: "
            "Caso 2 más el 75% del valor especificado). La excentricidad "
            "eQ para estructuras rígidas se mide desde el centro "
            "geométrico de la cara del edificio en cada eje; para "
            "estructuras flexibles, la excentricidad e se determina con "
            "la Ecuación B.6.5-19 (función de eQ, eR — distancia entre el "
            "centro de cortante elástico y el centro de masa por piso —, "
            "Iz, gQ, Q, gR y R, definidos en la sección B.6.5.8). La "
            "excentricidad e será positiva o negativa, la que produzca "
            "el efecto de carga más severo.\n"
            "EXCEPCIÓN — Edificios de un piso con h < 9.0 m, edificios de "
            "dos pisos o menos con pórticos de construcción liviana, y "
            "edificios de dos pisos o menos con diafragmas flexibles, se "
            "pueden diseñar solo con los casos de carga 1 y 3.\n\n"
            "B.6.5.12.4 — Elementos de Revestimiento y Componentes.\n"
            "B.6.5.12.4.1 — Edificios Bajos y Edificios con h ≤ 18.0 m:\n\n"
            "p = qh[(GCp) − (GCpi)] en N/m² (Ecuación B.6.5-20)\n\n"
            "Donde qh se evalúa a la altura media del edificio con la "
            "exposición de B.6.5.6.3; GCp de las figs. B.6.5-8 a "
            "B.6.5-13; GCpi de la fig. B.6.5-2.\n\n"
            "B.6.5.12.4.2 — Edificios con h > 18.0 m:\n\n"
            "p = q(GCp) − qi(GCpi) en N/m² (Ecuación B.6.5-21)\n\n"
            "Donde q = qz para muros a barlovento (altura z); q = qh "
            "para muros a sotavento, laterales y cubiertas (altura h); "
            "qi = qh para muros/cubiertas de edificios cerrados y para "
            "presiones internas negativas en parcialmente cerrados; qi = "
            "qz para presiones internas positivas en edificios "
            "parcialmente cerrados (z = nivel de la abertura más alta "
            "que podría afectar la presión interna positiva). En "
            "regiones donde el viento pueda arrastrar fragmentos, los "
            "vidrios no resistentes al impacto (ni protegidos) se tratan "
            "como una abertura del edificio (sección B.6.5.9.3); para la "
            "evaluación conservadora de la presión interna positiva, qi "
            "se puede evaluar a la altura h (qi = qh). GCp de la fig. "
            "B.6.5-14; GCpi de la fig. B.6.5-2; q y qi se evalúan con la "
            "exposición de B.6.5.6.3.\n\n"
            "B.6.5.12.4.3 — Alternativa para Edificios con 18.0 m < h < "
            "27 m — Como alternativa a B.6.5.12.4.2, se pueden usar los "
            "valores de las figs. B.6.5-8 a B.6.5-14 (con relación "
            "altura/ancho ≤ 1, salvo excepción de la Nota 6 de la fig. "
            "B.6.5-14) aplicando la Ecuación B.6.5-20.\n\n"
            "B.6.5.12.4.4 — Parapetos:\n\n"
            "p = qp(GCp − GCpi) (Ecuación B.6.5-22)\n\n"
            "Donde qp = presión por velocidad en la parte superior del "
            "parapeto; GCp de las figs. B.6.5-8 a B.6.5-14; GCpi de la "
            "fig. B.6.5-2 según la porosidad del revestimiento del "
            "parapeto. Se consideran dos Casos de Carga (A: presión "
            "positiva de muros en la cara frontal + presión negativa de "
            "borde/esquina en la posterior; B: al revés), evaluando "
            "ambos bajo presiones internas negativas y positivas si "
            "corresponde.\n\n"
            "NOTA DE FIDELIDAD: el pasaje sobre vidrios/aberturas de "
            "B.6.5.12.4.2 llegó con el orden de palabras alterado por el "
            "extractor OCR del PDF fuente; se reconstruyó cruzándolo con "
            "el pasaje casi idéntico de B.6.5.12.2.1 (misma cláusula "
            "repetida para el umbral h > 18 m). La Ecuación B.6.5-19 "
            "también llegó fragmentada; se conserva el número de "
            "ecuación y las variables, pero debe verificarse contra el "
            "documento fuente."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_13",
        "seccion": "B.6.5.13",
        "titulo": (
            "Cargas de viento en edificios ABIERTOS con cubiertas a una, "
            "dos aguas o en artesa: p = qhGCn para SPRFV (Ec. B.6.5-23) y "
            "para revestimiento/componentes (Ec. B.6.5-24), con "
            "coeficientes CN de figuras B.6.5-15/16; fascia tratada como "
            "parapeto invertido."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.13 — CARGAS DE VIENTO "
            "DE DISEÑO EN EDIFICIOS ABIERTOS CON CUBIERTAS A UNA, DOS "
            "AGUAS Y EN ARTESA.\n\n"
            "B.6.5.13.1 — General.\n"
            "B.6.5.13.1.1 — Convención de Signos — Presiones positivas "
            "hacia la superficie en estudio, negativas hacia afuera.\n"
            "B.6.5.13.1.2 — Condición de Carga Crítica — Los coeficientes "
            "de presión neta CN incluyen los aportes de las superficies "
            "superior e inferior; se deben investigar todos los casos de "
            "carga mostrados para cada ángulo de cubierta.\n\n"
            "B.6.5.13.2 — Sistemas Principales de Resistencia a Fuerzas "
            "de Viento — Presión de diseño neta para el SPRFV:\n\n"
            "p = qhGCN (Ecuación B.6.5-23)\n\n"
            "Donde qh = presión por velocidad a la altura promedio de la "
            "cubierta, usando la exposición (sección B.6.5.6.3) que "
            "resulte en las mayores cargas para cualquier dirección de "
            "viento del sitio; G = factor de efecto ráfaga (sección "
            "B.6.5.8); CN = coeficiente de presión neta de las figs. "
            "B.6.5-15A a B.6.5-15D. Para cubiertas libres con ángulo θ ≤ "
            "5° con paneles de fascia, éstos se consideran un parapeto "
            "invertido; el aporte de cargas al SPRFV por la fascia se "
            "determina usando la sección B.6.5.12.2.4 con qp = qh.\n\n"
            "B.6.5.13.3 — Elementos de Revestimiento y Componentes — "
            "Presión neta de diseño:\n\n"
            "p = qhGCN (Ecuación B.6.5-24)\n\n"
            "Donde qh, G se definen igual que en B.6.5.13.2; CN de las "
            "figs. B.6.5-16A a B.6.5-16C."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_14",
        "seccion": "B.6.5.14",
        "titulo": (
            "Cargas de viento en muros libres y vallas macizas: "
            "F = qhGCfAs (Ec. B.6.5-25)."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.14 — CARGAS DE VIENTO "
            "DE DISEÑO EN MUROS LIBRES Y VALLAS MACIZAS — La fuerza de "
            "viento de diseño se determina con:\n\n"
            "F = qhGCfAs en N (Ecuación B.6.5-25)\n\n"
            "Donde: qh = presión por velocidad evaluada a la altura h "
            "(definida en la fig. B.6.5-17), usando la exposición de la "
            "sección B.6.5.6.4.1; G = factor de efecto ráfaga (sección "
            "B.6.5.8); Cf = coeficiente de fuerza neta de la fig. "
            "B.6.5-17; As = área bruta del muro libre y sólido o la "
            "valla sólida, en m²."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_15",
        "seccion": "B.6.5.15, B.6.5.15.1",
        "titulo": (
            "Cargas de viento en OTRAS estructuras (no edificios): "
            "F = qzGCfAf (Ec. B.6.5-26); estructuras/equipos sobre "
            "cubiertas en edificios h<=18m con factor de amplificacion "
            "hasta 1.9 para areas pequenas."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.5.15 — CARGAS DE VIENTO "
            "DE DISEÑO EN OTRAS ESTRUCTURAS — La fuerza de viento de "
            "diseño para otras estructuras se determina con:\n\n"
            "F = qzGCfAf en N (Ecuación B.6.5-26)\n\n"
            "Donde: qz = presión por velocidad evaluada a la altura z "
            "del centroide del área Af, usando la exposición de la "
            "sección B.6.5.6.3; G = factor de efecto ráfaga (sección "
            "B.6.5.8); Cf = coeficientes de fuerza de las figs. B.6.5-18 "
            "a B.6.5-19; Af = área proyectada normal al viento, excepto "
            "donde Cf se haya especificado para la superficie real, en "
            "m².\n\n"
            "B.6.5.15.1 — Estructuras y Equipos sobre Cubiertas en "
            "Edificios con h ≤ 18.0 m — La fuerza en estructuras y "
            "equipos sobre cubiertas, con Af menor de (0.1Bh), "
            "localizados en edificios con h ≤ 18.0 m, se determina con "
            "la fuerza calculada multiplicada por un factor de 1.9. Este "
            "factor se puede reducir linealmente desde 1.9 hasta 1.0 a "
            "medida que Af aumenta de (0.1Bh) a (Bh)."
        ),
    },
    {
        "id": "NSR10-B-B_6_6",
        "seccion": "B.6.6 (Método 3 — Túnel de viento)",
        "titulo": (
            "Metodo 3 - Procedimiento de Tunel de Viento: alcance "
            "(permitido en lugar de Metodos 1/2 para cualquier "
            "edificio), 7 condiciones que deben cumplir los ensayos "
            "(capa de borde, escalas de turbulencia, similitud "
            "geometrica, bloqueo <8%, gradiente de presion, numero de "
            "Reynolds, instrumentacion), respuesta dinamica, y "
            "limitacion de velocidades de viento por direccion."
        ),
        "texto": (
            "NSR-10 Título B, Capítulo B.6 — B.6.6 — MÉTODO 3 — "
            "PROCEDIMIENTO DE TÚNEL DE VIENTO.\n\n"
            "B.6.6.1 — ALCANCE — Los ensayos de túnel de viento deben "
            "ser usados donde sea requerido de acuerdo con la sección "
            "B.6.5.2. Estos ensayos deben permitirse en lugar de los "
            "Métodos 1 y 2 para cualquier edificio o estructura.\n\n"
            "B.6.6.2 — CONDICIONES DE ENSAYOS — Los ensayos de túnel de "
            "viento que empleen fluidos diferentes al aire para "
            "determinar las cargas de diseño de viento para cualquier "
            "edificio u otra estructura, deben ser realizados de acuerdo "
            "con los requisitos de esta sección. Los ensayos para "
            "determinar las variaciones y el promedio de las fuerzas y "
            "presiones deben reunir las siguientes condiciones:\n"
            "B.6.6.2.1 — La capa de borde para la atmósfera natural se "
            "ha modelado teniendo en cuenta la variación de la velocidad "
            "del viento con la altura.\n"
            "B.6.6.2.2 — Las escalas relevantes de macro y "
            "micro-longitud de la componente longitudinal de la "
            "turbulencia atmosférica se modelan aproximadamente a la "
            "misma escala que se ha usado para modelar el edificio o la "
            "estructura.\n"
            "B.6.6.2.3 — El edificio u otra estructura modelada y las "
            "estructuras y topografía de los alrededores son "
            "geométricamente similares a sus contrapartes de escala "
            "natural, excepto que, para edificios bajos que reúnen las "
            "condiciones de la sección B.6.5.1, los ensayos deben ser "
            "permitidos para los edificios escalados en una sola "
            "categoría de exposición como se define en la sección "
            "B.6.5.6.3.\n"
            "B.6.6.2.4 — El área proyectada del edificio u otra "
            "estructura modelada y sus alrededores es menor que el 8% "
            "del área de la sección transversal de ensayo a menos que "
            "se haga una corrección por bloqueo.\n"
            "B.6.6.2.5 — El gradiente de presión longitudinal en la "
            "sección de ensayo del túnel de viento debe ser "
            "considerado.\n"
            "B.6.6.2.6 — Los efectos del número de Reynolds sobre las "
            "presiones y fuerzas se minimizan.\n"
            "B.6.6.2.7 — Las características de respuesta de la "
            "instrumentación del túnel de viento son consistentes con "
            "las mediciones requeridas.\n\n"
            "B.6.6.3 — RESPUESTA DINÁMICA — Los ensayos con el propósito "
            "de determinar la respuesta dinámica del edificio o de otra "
            "estructura deben estar de acuerdo con la sección B.6.6.2. "
            "El modelo estructural y el análisis respectivo deben tener "
            "en cuenta la distribución de masa, la rigidez y el "
            "amortiguamiento.\n\n"
            "B.6.6.4 — LIMITACIONES.\n"
            "B.6.6.4.1 — Limitaciones en velocidades de viento — La "
            "variación de velocidades básicas de viento con la "
            "dirección no se debe permitir a menos que el análisis para "
            "velocidades de viento esté de acuerdo con los requisitos de "
            "la sección B.6.5.4.2."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in CHUNKS]
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

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks de B.6.5 (Método 2) + B.6.6 (Método 3) cargados con embedding.")


if __name__ == "__main__":
    main()
