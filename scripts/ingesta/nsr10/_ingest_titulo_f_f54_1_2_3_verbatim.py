"""
Ingesta verbatim de NSR-10 Titulo F.5.4.1 + F.5.4.2 + F.5.4.3
(Estructuras de Aluminio -- Diseno Estatico de Miembros: Generalidades,
Esfuerzos Limites, Clasificacion de la Seccion y Pandeo Local).

Fuente: NSR-10-1083-1182.pdf (paginas internas F-461 a F-471), ya
descargado localmente en scripts/ingesta/nsr10/raw/ (gitignored).
Texto transcrito verbatim leyendo el PDF nativo pagina por pagina
(nunca el texto plano exportado, corrompe subindices/formulas).

Sistema de unidades: kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Uso: python _ingest_titulo_f_f54_1_2_3_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"
TITULO_F5 = "F.5 — Estructuras de Aluminio"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_4_1_1_estado_limite_resistencia_estatica",
        "seccion": "F.5.4.1.1 — Estado límite de resistencia estática",
        "titulo": "F.5.4 Diseño Estático de Miembros — F.5.4.1 Generalidades",
        "texto": (
            "F.5.4 — DISEÑO ESTATICO DE MIEMBROS\n\n"
            "F.5.4.1 — GENERALIDADES — Todos los miembros deben satisfacer "
            "los estados límite de resistencia estática y de deformación. "
            "En F.5.4.9 se trata la deformación.\n\n"
            "Cuando se hace referencia a curvas de diseño, se permite, en "
            "su lugar, usar las fórmulas con las que se derivaron dichas "
            "curvas (véase el apéndice F.5.I).\n\n"
            "Los miembros están usualmente formados por extrusiones, "
            "planchas, láminas delgadas, tuberías o una combinación de "
            "ellos. Las normas siguientes no se aplican a piezas coladas "
            "y, por lo tanto, los diseñadores que deseen emplear este "
            "tipo de piezas deben consultar con los fabricantes al "
            "respecto.\n\n"
            "F.5.4.1.1 — Estado límite de resistencia estática — La "
            "resistencia de diseño de un miembro frente a una "
            "acción-efecto específica no debe ser menor que la magnitud "
            "de dicha acción-efecto generada bajo carga mayorada. A "
            "continuación se dan las reglas para obtener la resistencia "
            "frente a diferentes acciones:\n\n"
            "(a) Para vigas (resistencia a momento y fuerza cortante) "
            "(véase F.5.4.5)\n"
            "(b) Para riostras (resistencia a tensión axial) (véase "
            "F.5.4.6)\n"
            "(c) Para puntales (resistencia a compresión axial) (véase "
            "F.5.4.7)\n"
            "(d) La posibilidad de un cambio de uso de la estructura "
            "durante su vida\n\n"
            "En F.5.4.8 se define el procedimiento para calcular la "
            "interacción de momento y carga axial en miembros sujetos a "
            "acciones combinadas.\n\n"
            "Las fórmulas dadas contienen los esfuerzos límites (po, pa, "
            "pv) relacionados con las propiedades del material y que "
            "deben ser tomados de acuerdo con F.5.4.2. También contienen "
            "el coeficiente de reducción de capacidad φ que debe ser "
            "leído en la tabla F.5.3.3-1.\n\n"
            "La resistencia de un miembro puede reducirse como resultado "
            "del pandeo local, dependiendo de la esbeltez de la sección "
            "transversal. Un diseño propuesto se revisa (excepto para "
            "miembros bajo tensión axial) clasificando la sección en "
            "términos de su susceptibilidad a este tipo de falla. En "
            "F.5.4.3, se da un método para verificar el pandeo local "
            "incluyendo la clasificación de la sección."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_1_2_3_zonas_calor_diseno_avanzado",
        "seccion": "F.5.4.1.2/1.3 — Zonas afectadas por el calor, diseño avanzado",
        "titulo": "F.5.4.1 Generalidades",
        "texto": (
            "F.5.4.1.2 — Zonas afectadas por el calor — El material de "
            "aluminio estructural generalmente se debilita en la zona "
            "afectada por el calor adyacente a las soldaduras y esto "
            "debe ser tenido en cuenta en el diseño. No es necesario "
            "aplicar esto cuando el material base está en la condición "
            "O ó T4, o cuando está en la condición F y el diseño se "
            "basa en las propiedades de la condición O.\n\n"
            "En F.5.4.4, se dan reglas para estimar la severidad y "
            "extensión del ablandamiento en la zona afectada por el "
            "calor y los numerales siguientes muestran cómo tener en "
            "cuenta el efecto de este ablandamiento en la resistencia "
            "del miembro.\n\n"
            "Es importante darse cuenta de que una soldadura pequeña "
            "como la que se usa, por ejemplo, para colocar un pequeño "
            "aditamento, puede causar una reducción considerable en la "
            "resistencia del miembro debido al ablandamiento de parte "
            "de la sección transversal. En vigas, es a menudo benéfico "
            "localizar las soldaduras en áreas de bajo esfuerzo como, "
            "por ejemplo, cerca del eje neutro o lejos de la región de "
            "momento pico.\n\n"
            "F.5.4.1.3 — Diseño avanzado — Los miembros pueden ser "
            "diseñados para un comportamiento seguro usando las "
            "recomendaciones de esta sección y algunos apéndices "
            "apropiados. Otros apéndices tratan profundamente ciertos "
            "aspectos específicos del comportamiento del miembro y "
            "pueden conducir a diseños más livianos."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_2_esfuerzos_limites_definiciones",
        "seccion": "F.5.4.2 — Esfuerzos Límites, definiciones",
        "titulo": "F.5.4.2 Esfuerzos límites po, pa, pv, ps",
        "texto": (
            "F.5.4.2 — ESFUERZOS LÍMITES — Los cálculos de resistencia "
            "para miembros se hacen suponiendo los siguientes esfuerzos "
            "límites:\n\n"
            "po = esfuerzo límite para flexión y fluencia total\n"
            "pa = esfuerzo límite para capacidad local de la sección a "
            "tensión o compresión\n"
            "pv = esfuerzo límite a cortante\n"
            "ps = esfuerzo límite para estabilidad al pandeo general\n\n"
            "Los valores de po, pa y pv dependen de las propiedades del "
            "material y deben ser tomados de acuerdo con las tablas "
            "F.5.4.2-1 y F.5.4.2-2. Para materiales no cubiertos en "
            "estas tablas, refiérase al apéndice F.5.C.\n\n"
            "Los valores de ps deben determinarse de acuerdo con "
            "F.5.4.5.6(c) o F.5.4.7.5."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_2_tabla1_esfuerzos_limite_tratadas_calor",
        "seccion": "Tabla F.5.4.2-1 (Esfuerzos límite, aleaciones tratadas en caliente)",
        "titulo": "6061-T6: po 22.5-24, pa 26.0-26.5, pv 13.5-14.5. 6063: T4 6.5-9.5, T6 16.0-18.0. 6082: T4 10.5-11.5, T6 24.0-27.5. 7020: T4 16.0-18.5, T6 27.0-28.0 kgf/mm².",
        "texto": (
            "Tabla F.5.4.2-1 — Esfuerzos límite, aleaciones tratadas en "
            "caliente (Aleación, Condición, Producto, Espesor desde-hasta "
            "mm, Esfuerzo límite po/pa/pv en kgf/mm²).\n\n"
            "6061 — T6, Extrusión: hasta 150mm, po 24, pa 26.0, pv 14.5. "
            "T6, Tubería extruída: hasta 6mm, po 24, pa 26.5, pv 14.5; "
            "6-10mm, po 22.5, pa 26.0, pv 13.5.\n\n"
            "6063 — T4, Extrusión: hasta 150mm, po 6.5, pa 8.5, pv 4.0. "
            "T4, Tubería extruída: hasta 10mm, po 9.5, pa 12.0, pv 6.0. "
            "T4, Forjados: hasta 150mm, po 8, pa 10.0, pv 5.0. T5, "
            "Extrusión: hasta 25mm, po 11, pa 13.0, pv 6.5. T6, "
            "Extrusión: hasta 150mm, po 16, pa 17.5, pv 9.5. T6, "
            "Tubería extruída: hasta 10mm, po 18, pa 19.0, pv 11.0. T6, "
            "Forjados: hasta 150mm, po 16, pa 17.0, pv 9.5.\n\n"
            "6082 — T4, Extrusión: hasta 150mm, po 11.5, pa 14.5, pv "
            "7.0. T4, Lámina: 0.2-3mm, po 11.5, pa 14.5, pv 7.0. T4, "
            "Plancha: 3-25mm, po 10.5, pa 14.0, pv 6.5. T4, Tubería "
            "extruída: hasta 10mm, po 10.5, pa 14.0, pv 6.5. T4, "
            "Forjados: hasta 150mm, po 11.5, pa 14.5, pv 7.0. T6, "
            "Extrusión: hasta 20mm, po 25.5, pa 27.5, pv 15.5; 20-150mm, "
            "po 27, pa 29.0, pv 16.0. T6, Lámina: 0.2-3mm, po 25.5, pa "
            "27.5, pv 15.5. T6, Plancha: 3-25mm, po 24, pa 26.5, pv "
            "14.5. T6, Tubería extruída: hasta 6mm, po 25.5, pa 28.0, "
            "pv 15.5; 6-10mm, po 24, pa 27.5, pv 14.5. T6, Forjados: "
            "hasta 120mm, po 25.5, pa 27.5, pv 15.5.\n\n"
            "7020 — T4, Extrusión: hasta 25mm, po 18.5, pa 23.0, pv "
            "11.0. T4, Lámina/Plancha: 0.2-25mm, po 16, pa 20.5, pv "
            "9.5. T6, Extrusión: hasta 25mm, po 28, pa 31.0, pv 17.0. "
            "T6, Lámina/Plancha: 0.2-25mm, po 27, pa 29.5, pv 16.0."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_2_tabla2_esfuerzos_limite_no_tratadas_calor",
        "seccion": "Tabla F.5.4.2-2 (Esfuerzos límite, aleaciones no tratadas en caliente)",
        "titulo": "1200/3103/3105: po 9.0-19.0. 5083: po 6.5-23.5. 5154A: po 6.5-22.5. 5251: po 12.5-22.0. 5454: po 6.0-20.0 kgf/mm² según condición.",
        "texto": (
            "Tabla F.5.4.2-2 — Esfuerzos límite, aleaciones no tratadas "
            "en caliente (Aleación, Condición, Producto, Espesor "
            "desde-hasta mm, Esfuerzo límite po/pa/pv en kgf/mm²).\n\n"
            "1200 — H14, Lámina: 0.2-12.5mm, po 9.0, pa 9.5, pv 5.5.\n\n"
            "3103 — H14, Lámina: 0.2-12.5mm, po 11.0, pa 12.0, pv 6.5. "
            "H18, Lámina: 0.2-3mm, po 15.0, pa 15.0, pv 8.5.\n\n"
            "3105 — H14, Lámina: 0.2-3mm, po 14.5, pa 15.0, pv 8.5. "
            "H16, Lámina: 0.2-3mm, po 17.0, pa 17.5, pv 10.0. H18, "
            "Lámina: 0.2-3mm, po 19.0, pa 20.0, pv 11.5.\n\n"
            "5083 — O/F, Extrusión: hasta 150mm, po 10.5, pa 15.0, pv "
            "6.5. O, Lámina/Plancha: 0.2-80mm, po 10.5, pa 15.0, pv "
            "6.5. O, Tubería extruída: hasta 10mm, po 10.5, pa 15.0, "
            "pv 6.5. F, Lámina/Plancha: 3-25mm, po 13.0, pa 17.0, pv "
            "7.5. H22, Lámina/Plancha: 0.2-6mm, po 23.5, pa 27.0, pv "
            "14.0. H22, Tubería extruída: hasta 10mm, po 23.5, pa 27.0, "
            "pv 14.0.\n\n"
            "5154A — O/F, Extrusión: hasta 150mm, po 6.5, pa 10.0, pv "
            "4.0. O, Lámina/Plancha: 0.2-6mm, po 6.5, pa 10.0, pv 4.0. "
            "O, Tubería extruída: hasta 6mm, po 6.5, pa 10.0, pv 4.0. "
            "H22, Lámina/Plancha: 0.2-6mm, po 16.0, pa 20.0, pv 9.5. "
            "H24, Lámina/Plancha: 0.2-6mm, po 22.5, pa 25.0, pv 13.5.\n\n"
            "5251 — F, Tubería extruída: hasta 10mm, po 20.0, pa 22.0, "
            "pv 9.5. H22, Tubería soldada: 0.8-2mm, po 22.0, pa 23.0, "
            "pv 13.0. H24, Lámina/Plancha: 0.2-6mm, po 12.5, pa 15.5, "
            "pv 7.5.\n\n"
            "5454 — O/F, Lámina/Plancha: 0.2-6mm, po 17.5, pa 20.0, pv "
            "10.5. O, Extrusión: hasta 150mm, po 6.5, pa 10.0, pv 4.0. "
            "F, Lámina/Plancha: 0.2-6mm, po 6.0, pa 9.5, pv 3.5. H22, "
            "Lámina: 0.2-3mm, po 18.0, pa 21.5, pv 11.0. H24, Lámina: "
            "0.2-3mm, po 20.0, pa 23.5, pv 12.0."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_1_a_b_generalidades_tipos_elementos",
        "seccion": "F.5.4.3.1 — Generalidades: clasificación, tipos de elementos",
        "titulo": "F.5.4.3 Clasificación de la Sección y Pandeo Local",
        "texto": (
            "F.5.4.3 — CLASIFICACION DE LA SECCION Y PANDEO LOCAL\n\n"
            "F.5.4.3.1 — Generalidades\n\n"
            "(a) Clasificación de la sección — La resistencia de los "
            "miembros sometidos a momento o compresión axial puede "
            "reducirse por pandeo local si la esbeltez de sus elementos "
            "componentes es alta. El primer paso en la verificación de "
            "tales miembros es establecer la clasificación de la "
            "sección, esto es, su susceptibilidad al pandeo local. Para "
            "hacerlo, y también para tener en cuenta el efecto del "
            "pandeo local (cuando sea necesario), el diseñador debe "
            "considerar la esbeltez de los elementos individuales que "
            "componen la sección.\n\n"
            "(b) Tipos de elementos — Se identifican los siguientes "
            "tipos básicos de elementos de pared delgada: elemento "
            "plano saliente, elemento plano interno y elemento curvo "
            "interno.\n\n"
            "Estos son, a menudo, no reforzados, o sea que no son "
            "rigidizados longitudinalmente (véase la figura "
            "F.5.4.3-1(a)). La estabilidad de elementos planos puede "
            "mejorarse bastante mediante la colocación de costillas "
            "rigidizadoras longitudinales o pestañas, véase la figura "
            "F.5.4.3-1(b) en cuyo caso los elementos se denominan "
            "reforzados.\n\n"
            "Figura F.5.4.3-1 — Tipos de elementos planos: (a) No "
            "reforzados (secciones I, canal, cajón, con salientes O y "
            "elementos internos I) — (b) Reforzados (con pestañas o "
            "labios de refuerzo en los bordes). Convenciones: O = "
            "saliente, I = Interno.\n\n"
            "(c) Almas sometidas a cortante — El pandeo de almas a "
            "cortante se trata por separado (véase el literal (c) de "
            "F.5.4.5.3 y F.5.5)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_2_a_esbeltez_elementos_no_reforzados",
        "seccion": "F.5.4.3.2(a) — Parámetro de esbeltez β, elementos planos no reforzados",
        "titulo": "β=b/t compresión uniforme; β=0.35d/t o gb/t gradiente de esfuerzos",
        "texto": (
            "F.5.4.3.2 — Parámetro de esbeltez β — La susceptibilidad "
            "al pandeo local de un elemento de una viga (resistencia a "
            "momento) o en un miembro a compresión (resistencia a "
            "fuerza axial) depende del parámetro β como se define en "
            "los literales (a) a (d) de este numeral.\n\n"
            "(a) Elementos planos no reforzados — El parámetro β "
            "depende de la relación b/t o d/t del elemento considerado; "
            "t es el espesor del elemento, b es generalmente el ancho "
            "del elemento y d es la altura del elemento del alma en una "
            "viga. Los valores de b y d deben ser tomados como el ancho "
            "del elemento plano medido hasta el comienzo de un filete o "
            "hasta el borde de una soldadura.\n\n"
            "β se define como sigue:\n\n"
            "• Elemento sometido a compresión uniforme: β = b/t\n"
            "• Elemento sometido a un gradiente de esfuerzos:\n"
            "  (1) Elemento interno con un gradiente de esfuerzos que "
            "resulta en un eje neutro en el centro: β = 0.35d/t o, "
            "β = 0.35b/t\n"
            "  (2) Para cualquier otro gradiente de esfuerzos: β = gb/t "
            "o, β = gd/t\n\n"
            "donde g es el coeficiente de gradiente de esfuerzos que se "
            "lee en la figura F.5.4.3-2. En la figura F.5.4.3-2, yc y yo "
            "son las distancias desde el eje neutro de la sección bruta "
            "hasta el extremo más fuertemente comprimido y hasta el "
            "otro extremo del elemento respectivamente; son tomadas "
            "como positivas hacia el lado comprimido. Deben ser "
            "generalmente medidas desde el eje neutro elástico pero en "
            "la verificación de si una sección es totalmente compacta "
            "se permite usar el eje neutro plástico.\n\n"
            "Figura F.5.4.3-2 — Elementos planos bajo gradiente de "
            "esfuerzos, valor de g: gráfica con curva A (elementos "
            "internos o salientes, compresión pico en la raíz) y línea "
            "B (elementos salientes, compresión pico en el borde), en "
            "función de yo/yc, con valor límite g=1.0 en yo/yc=0 y "
            "valor 0.5g marcado en el eje."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_2_b_esbeltez_elementos_reforzados_modos",
        "seccion": "F.5.4.3.2(b) — Elementos planos reforzados: modos de pandeo 1, 2, 3",
        "titulo": "Modo 1 (unidad con refuerzo), Modo 2 (subelementos), Modo 3 (combinación superpuesta)",
        "texto": (
            "(b) Elementos planos reforzados — Se deben considerar dos "
            "modos posibles de pandeo (véase la figura F.5.4.3-3) y se "
            "deben encontrar valores diferentes de β para cada uno de "
            "ellos:\n\n"
            "• modo 1 — el elemento reforzado se pandea como una "
            "unidad llevándose consigo el refuerzo\n"
            "• modo 2 — los subelementos, abarcando el elemento "
            "reforzado, se pandean como elementos individuales "
            "mientras las uniones entre ellos permanecen rectas\n"
            "• modo 3 — esta es una combinación de los Modos 1 y 2 en "
            "los cuales el pandeo de los sub elementos está súper "
            "puesto al pandeo del elemento entero, esto se indica en la "
            "Figura F.5.4.3-3.(c)\n\n"
            "Figura F.5.4.3-3 — Modos de pandeo de elementos planos "
            "reforzados: (a) Modo 1, el elemento completo se pandea "
            "como unidad; (b) Modo 2, los subelementos se pandean "
            "individualmente entre uniones rectas; (c) Modo 3, pandeo "
            "de subelementos superpuesto al pandeo del elemento entero.\n\n"
            "En el modo 2 de pandeo, β se encuentra por separado para "
            "cada subelemento de acuerdo con el literal (a) de "
            "F.5.4.3.2. En el modo 1, β se determina, generalmente, "
            "como sigue (véase F.5.4.3.2 para lo que se relaciona con "
            "elementos salientes en vigas)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_2_b_modo1_refuerzo_estandar_general",
        "seccion": "F.5.4.3.2(b) — Modo 1 compresión uniforme: refuerzo estándar, no estándar, método general",
        "titulo": "β=hb/t refuerzo estándar (F.5.4.3-1); β=(b/t)(σcro/σcr)^0.4 método general (F.5.4.3-2)",
        "texto": (
            "Modo 1, compresión uniforme:\n\n"
            "(1) Refuerzo estándar — Se define como el refuerzo "
            "consistente en una costilla o pestaña unilateral con "
            "espesor igual al del elemento, t, y localizado como se "
            "muestra en la figura F.5.4.3-4:\n\n"
            "β = hb/t  (F.5.4.3-1)\n\n"
            "Donde:\n"
            "b y t = se definen como en el literal (a) de F.5.4.3.2\n"
            "h = se lee en la figura F.5.4.3-4 (a), (b) o (c) según sea "
            "apropiado\n\n"
            "En la figura F.5.4.3-4, c debe tomarse como la altura "
            "libre de la costilla o pestaña medida hasta la superficie "
            "de la lámina.\n\n"
            "(2) Refuerzo no estándar — Con cualquier otra forma de "
            "refuerzo, β debe encontrarse reemplazándolo con una "
            "costilla o pestaña equivalente de forma estándar y "
            "procediendo como en (1). El valor de c para la costilla o "
            "pestaña equivalente se escoge de modo que su segundo "
            "momento del área alrededor del plano medio de la lámina "
            "sea igual al del refuerzo verdadero.\n\n"
            "(3) Método general — Para casos no cubiertos por (1) y "
            "(2), β se debe tomar de acuerdo con:\n\n"
            "β = (b/t)(σcro/σcr)^0.4  (F.5.4.3-2)\n\n"
            "Donde:\n"
            "σcr y σcro = esfuerzos elásticos críticos, suponiendo "
            "soporte en un solo borde, con y sin el refuerzo\n\n"
            "Modo 1, gradiente de esfuerzos — β debe encontrarse "
            "usando la expresión general dada en el numeral (3) en la "
            "cual σcr y σcro ahora se refieren al esfuerzo en el borde "
            "más comprimido del elemento.\n\n"
            "Figura F.5.4.3-4 — Elementos reforzados, valor de h: tres "
            "gráficas (a), (b), (c) de h en función de c/t, para "
            "distintas configuraciones de refuerzo unilateral/bilateral "
            "igualmente espaciado, con familias de curvas parametrizadas "
            "por b/t (20, 40, 60...)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_2_c_d_elementos_curvos_tubos_redondos",
        "seccion": "F.5.4.3.2(c)(d) — Elementos curvos internos, tubos redondos",
        "titulo": "β=(b/t)/[1+(0.006b^4/R^2t^2)]^0.5 curvos (F.5.4.3-3); β=3(D/t)^0.5 tubos redondos (F.5.4.3-4)",
        "texto": (
            "(c) Elementos curvos internos — En elementos curvos de "
            "poca altura sometidos a compresión uniforme, β debe "
            "determinarse usando:\n\n"
            "β = (b/t) / [1 + (0.006 b^4 / R^2 t^2)]^(1/2)  (F.5.4.3-3)\n\n"
            "Donde:\n"
            "R = radio de curvatura hasta la parte media del metal\n"
            "b = ancho de desarrollo del elemento en la parte media del "
            "metal\n"
            "t = espesor\n\n"
            "En elementos curvos sometidos a un gradiente de esfuerzos "
            "se puede tomar un valor de β más favorable obtenido "
            "factorando el valor anterior por g (obtenido en la figura "
            "F.5.4.3-2).\n\n"
            "El tratamiento anterior es válido siempre que R/b no sea "
            "menor que 0.1b/t. Las secciones que contienen elementos de "
            "mayor curvatura requieren estudio especial.\n\n"
            "(d) Tubos redondos — β se debe calcular de acuerdo con lo "
            "siguiente, sin hacer distinción entre compresión axial y "
            "flexión:\n\n"
            "β = 3(D/t)^(1/2)  (F.5.4.3-4)\n\n"
            "Donde:\n"
            "D = diámetro hasta la parte media del metal\n"
            "t = espesor"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_3_clasificacion_seccion_a_b_c",
        "seccion": "F.5.4.3.3 — Clasificación de la sección",
        "titulo": "Totalmente compacta / semi-compacta / esbelta; β≤β1/β1<β≤β0/β>β0",
        "texto": (
            "F.5.4.3.3 — Clasificación de la sección — El procedimiento "
            "consiste en clasificar los elementos individuales que "
            "conforman la sección, exceptuando cualquier elemento "
            "sometido totalmente a tensión. La clasificación de la "
            "sección se toma como la del elemento menos favorable. Los "
            "elementos individuales se clasifican de acuerdo con los "
            "literales (c) o (d) de este numeral.\n\n"
            "(a) Secciones — vigas y miembros a compresión — Para la "
            "sección de una viga (resistencia a momento) o de un "
            "miembro a compresión (resistencia a fuerza axial) se "
            "aplican las siguientes clasificaciones.\n\n"
            "Resistencia a momento:\n"
            "(1) Totalmente compacta — el pandeo local puede ignorarse\n"
            "(2) Semi-compacta — la sección puede desarrollar un "
            "momento igual a po veces el módulo elástico de la sección\n"
            "(3) Esbelta — la resistencia a momento se reduce por "
            "pandeo local prematuro con un esfuerzo en la fibra extrema "
            "menor que po.\n\n"
            "Resistencia a compresión axial:\n"
            "(1) Compacta — se puede ignorar el pandeo local\n"
            "(2) Esbelta — el pandeo local disminuye la resistencia\n\n"
            "(b) Secciones sometidas a acciones combinadas — Véase el "
            "literal (a) de F.5.4.8.2 para la clasificación de "
            "secciones sometidas a flexión biaxial o a flexión y "
            "fuerza axial simultáneas.\n\n"
            "(c) Clasificación de elementos — La clasificación de un "
            "elemento individual depende del valor de β (véase "
            "F.5.4.3.2):\n\n"
            "elementos de vigas (resistencia a momento):\n"
            "β ≤ β1 → totalmente compacta\n"
            "β1 < β ≤ β0 → semi-compacta\n"
            "β > β0 → esbelta\n\n"
            "elementos de miembros a compresión (resistencia axial):\n"
            "β ≤ β0 → compacta\n"
            "β > β0 → esbelta\n\n"
            "donde β0 y β1 están dados en la tabla F.5.4.3-1."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_3_tabla1_valores_limite_beta",
        "seccion": "Tabla F.5.4.3-1 (Valores límite de β) + (d) elementos de aleta subesforzados",
        "titulo": "Elementos salientes: β0=7ε(no soldado)/6ε(soldado), β1=6ε/5ε. Internos: β0=22ε/18ε, β1=18ε/15ε",
        "texto": (
            "Tabla F.5.4.3-1 — Valores límite de β:\n\n"
            "Elementos salientes — No soldado: β0=7ε, β1=6ε. Soldado: "
            "β0=6ε, β1=5ε.\n"
            "Elementos internos — No soldado: β0=22ε, β1=18ε. Soldado: "
            "β0=18ε, β1=15ε.\n\n"
            "NOTA 1. El valor de ε se toma generalmente como "
            "ε = (25/po)^(1/2) (excepto para ciertos elementos de aleta "
            "en vigas, véase F.5.4.3.3(d)). po es el esfuerzo límite en "
            "kgf/mm² (véanse las tablas F.5.4.2-1 y F.5.4.2-2).\n\n"
            "NOTA 2. Un elemento se considera soldado si contiene "
            "soldadura en un borde o en cualquier punto de su ancho. "
            "Sin embargo, cuando se evalúa la estabilidad de la sección "
            "transversal particular de un miembro, se permite "
            "considerar el elemento como no soldado si no contiene "
            "soldadura en esa sección aunque esté soldado en cualquier "
            "otro lugar de su longitud.\n\n"
            "NOTA 3. En un elemento soldado, la clasificación es "
            "independiente de la extensión de la zona afectada por el "
            "calor.\n\n"
            "(d) Elementos de aleta subesforzados — Se puede utilizar "
            "una clasificación más favorable para elementos de aleta en "
            "miembros sometidos a flexión o a flexión más fuerza axial "
            "que sean:\n\n"
            "• Paralelos al eje de flexión; y\n"
            "• Menos altamente esforzados que las fibras más "
            "severamente esforzadas de la sección.\n\n"
            "Se permite entonces, usando la tabla F.5.4.3-1, tomar un "
            "valor modificado de ε según:\n\n"
            "ε = (25 y1 / po y2)^(1/2)  (F.5.4.3-5)\n\n"
            "donde y1 y y2 son, respectivamente, las distancias desde "
            "el eje neutro de la sección bruta hasta las fibras más "
            "severamente esforzadas y hasta el elemento. Deben ser, "
            "por lo general, medidas desde el eje neutro elástico; no "
            "obstante, en la revisión de si la sección es totalmente "
            "compacta se permite usar el eje neutro plástico."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_4_pandeo_local_kl_tabla2",
        "seccion": "F.5.4.3.4 — Pandeo local, determinación de kL",
        "titulo": "Tabla F.5.4.3-2: curvas A/B salientes, C/D internas, E tubería (soldado/no soldado)",
        "texto": (
            "F.5.4.3.4 — Pandeo local — La posibilidad de pandeo local "
            "en miembros clasificados como esbeltos es generalmente "
            "tenida en cuenta reemplazando la sección real por una "
            "sección efectiva. La sección efectiva se obtiene empleando "
            "un coeficiente de pandeo local kL para reducir el espesor; "
            "esto es aplicable a cualquier elemento esbelto de espesor "
            "uniforme que esté total o parcialmente sometido a "
            "compresión. Los elementos que no tienen espesor uniforme "
            "requieren un estudio especial.\n\n"
            "(a) Determinación de kL — El coeficiente kL, que se "
            "encuentra por separado para los diferentes elementos de la "
            "sección, se lee de la curva apropiada de la figura "
            "F.5.4.3-5 seleccionada de acuerdo con la tabla F.5.4.3-2. "
            "Se debe determinar, como se muestra a continuación, el "
            "valor correcto de β/ε para poder seleccionar la curva "
            "correcta:\n\n"
            "Tabla F.5.4.3-2 — Selección de la curva de la figura "
            "F.5.4.3-5 (pandeo local):\n\n"
            "Elementos salientes planos — No soldado: Curva A. Soldado: "
            "Curva B.\n"
            "Elementos internos (planos o curvos) — No soldado: Curva "
            "C. Soldado: Curva D.\n"
            "Tubería redonda — No soldado: la inferior entre las curvas "
            "C y E. Soldado: la inferior entre las curvas D y E.\n\n"
            "NOTA: En un elemento soldado, la clasificación es "
            "independiente de la extensión de la zona afectada por el "
            "calor.\n\n"
            "β = se encuentra según F.5.4.3.2\n"
            "ε = (25/po)^(1/2) generalmente (véase la nota 3 del "
            "literal (c) de F.5.4.5.2 para aletas a compresión de "
            "vigas)\n"
            "Donde:\n"
            "po = esfuerzo límite del material en kgf/mm², sin "
            "considerar el efecto de la zona afectada por el calor\n\n"
            "Para decidir si un elemento se debe tomar como no soldado "
            "o soldado en la tabla F.5.4.4, véase la nota 2 de la tabla "
            "F.5.4.3.\n\n"
            "En el caso de elementos planos reforzados es importante "
            "considerar ambos modos posibles de pandeo (véase figura "
            "F.5.4.3) y tomar el más crítico. En el caso del modo 1, el "
            "coeficiente de pandeo kL se debe aplicar al área del "
            "refuerzo tanto como al espesor básico de la lámina."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_3_4_b_figura5_secciones_combinadas",
        "seccion": "F.5.4.3.4(b) — Figura F.5.4.3-5, secciones con acciones combinadas",
        "titulo": "Figura F.5.4.3-5: curvas kL vs β/ε para elementos salientes (A/B) e internos/tubería (C/D/E)",
        "texto": (
            "Figura F.5.4.3-5 — Coeficiente de pandeo local kL:\n\n"
            "(a) Para elementos planos salientes — gráfica de kL "
            "(0-1.0) contra β/ε (0-30), Curva A: elementos salientes, "
            "no soldados; Curva B: elementos salientes, soldados. "
            "Ambas curvas parten de kL=1.0 en β/ε bajo y decrecen "
            "gradualmente.\n\n"
            "(b) Para elementos internos y tubos redondos — gráfica de "
            "kL (0-1.0) contra β/ε (0-80), Curva C: elementos internos, "
            "no soldados; Curva D: elementos internos, soldados; Curva "
            "E: tubos redondos. NOTA: véase la nota 3 de la tabla "
            "F.5.4.3-1.\n\n"
            "(b) Secciones sometidas a acciones combinadas — Véase el "
            "literal (b) de F.5.4.8.2 para determinar kL en secciones "
            "sometidas a flexión biaxial o a flexión y fuerza axial "
            "simultáneas."
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

    print(f"\nOK: {len(rows)} chunks de F.5.4.1-F.5.4.3 cargados.")
    max_len = max(len(c["texto"]) for c in CHUNKS)
    print(f"Chunk más largo: {max_len} caracteres.")


if __name__ == "__main__":
    main()
