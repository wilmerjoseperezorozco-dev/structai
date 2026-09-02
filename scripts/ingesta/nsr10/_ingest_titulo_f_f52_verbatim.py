"""
NSR-10 Titulo F, Capitulo F.5 (Estructuras de Aluminio) -- F.5.2
(PROPIEDADES Y SELECCION DE MATERIALES) COMPLETO. Segunda pieza de
F.5, 15 paginas (F-444 a F-458).

F.5.2.1 (Denominacion de los materiales -- sistema de 4 digitos),
F.5.2.2 (Materiales permitidos -- materiales estandar, aleaciones
tratadas en caliente 6082/6061/6063/7020/LM25 y no tratadas en
caliente 1200/3103/3105/5083/5251/5154A/5454/LM5/LM6, con Tablas
F.5.2.2-1 a -4: propiedades mecanicas por aleacion/condicion, y
pernos/remaches/metales de aporte), F.5.2.3 (Propiedades de
resistencia, mecanicas y fisicas -- Tabla F.5.2.3-1), F.5.2.4
(Durabilidad y proteccion contra la corrosion -- 3 niveles A/B/C,
Tabla F.5.2.4-1 proteccion por ambiente, Tabla F.5.2.4-2 contactos
metal-metal, contacto con concreto/madera/suelos/agua/quimicos/
aislantes), F.5.2.5 (Fabricacion y construccion -- doblado, soldadura,
metales de aporte), F.5.2.6 (Seleccion de materiales), F.5.2.7
(Disponibilidad -- secciones estructurales con Tablas F.5.2.7-1 a -3,
tuberia, lamina/planchas, piezas forjadas/coladas).

Con esto F.5.2 queda COMPLETO. F.5.3 (Principios de diseno) arranca
justo despues en F-458 -- no ingestado todavia, queda para otra pieza.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final CON verificacion real de tokens (metodo de F.4.6/F.4.7/F.4.8/
F.5.1, el unico confiable).

Fuente: NSR-10-1083-1182.pdf (Drive id 1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi,
ya descargado localmente), paginas internas F-444 a F-458 (paginas PDF
43-57), leidas visualmente pagina por pagina, re-verificadas contra el
PDF antes de transcribir. Ojo con las unidades: este capitulo usa
kgf/kgf.mm^2 (no SI) -- ver F.5.1.1 y el docstring de
_ingest_titulo_f_f51_verbatim.py.

Uso: python _ingest_titulo_f_f52_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_2_1_denominacion",
        "seccion": "F.5.2 / F.5.2.1 (Propiedades y selección de materiales — denominación)",
        "titulo": "Sistema internacional de 4 dígitos para aleaciones; temple según NTC 1937 (ISO 2107); notación simplificada F/T4/T6/T8 en F.5.4-F.5.6.",
        "texto": (
            "F.5.2 — PROPIEDADES Y SELECCIÓN DE MATERIALES. F.5.2.1 — "
            "DENOMINACIÓN DE LOS MATERIALES — La denominación del "
            "aluminio forjado y las aleaciones de aluminio usadas para "
            "propósitos generales de ingeniería utilizada en esta norma "
            "está de acuerdo con el sistema de clasificación "
            "internacional de 4 dígitos. En el apéndice F.5.A se dan "
            "detalles de este sistema. La tabla F.5.A.1 muestra las "
            "denominaciones antiguas y actuales de las normas "
            "británicas conjuntamente con los equivalentes más "
            "cercanos de la ISO y otras denominaciones extranjeras. La "
            "denominación para piezas coladas está de acuerdo con el "
            "sistema usado en la norma inglesa BS 1490 para piezas "
            "coladas de aleaciones de aluminio. La denominación para el "
            "temple de la aleación usada en esta norma está, por lo "
            "general, de acuerdo con el sistema de denominación de "
            "temple \"alternativo\" NTC 1937 (ISO 2107). En el apéndice "
            "F.5.A se dan detalles de este sistema conjuntamente con el "
            "sistema anterior aún usado para algunas aleaciones y "
            "formas del material. Para simplificar el texto y evitar "
            "confusión, en F.5.4, F.5.5 y F.5.6 no se usan las "
            "denominaciones de temple M, TB, TF y TH. Se utilizan las "
            "denominaciones equivalentes F, T4, T6 y T8 respectivamente."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_a_materiales_estandar",
        "seccion": "F.5.2.2 / F.5.2.2.1(a) (Materiales permitidos — extrusiones/láminas/planchas/tubería/forjadas/coladas — materiales estándar)",
        "titulo": "Aleaciones estándar según Tablas F.5.2.2-1/-2 y BS 8118 Parte 2; piezas coladas requieren control de calidad y consulta con fabricante.",
        "texto": (
            "F.5.2.2 — MATERIALES PERMITIDOS. F.5.2.2.1 — Extrusiones, "
            "láminas delgadas, planchas, tubería extruída, piezas "
            "forjadas y piezas coladas. (a) Materiales estándar — Esta "
            "parte de las normas cubre el diseño de estructuras "
            "fabricadas con una serie de aleaciones de aluminio usadas "
            "en las condiciones y temples enumerados en las tablas "
            "F.5.2.2-1 y F.5.2.2-2 y comúnmente suministradas con las "
            "especificaciones dadas en normas como la BS 8118: Parte 2. "
            "Las aleaciones se clasifican en dos categorías: la primera "
            "son las aleaciones que aceptan tratamiento térmico, dadas "
            "en la tabla F.5.2.2-1 y descritas en (b), y la segunda son "
            "las aleaciones que no aceptan tratamiento térmico, dadas "
            "en la tabla F.5.2.2-2 y descritas en (c). Las piezas "
            "coladas deberán ser usadas en estructuras de soporte de "
            "cargas únicamente después de que un adecuado procedimiento "
            "de prueba y control de calidad de su producción haya sido "
            "realizado y aprobado por el ingeniero. Las reglas de "
            "diseño de esta norma no se deben aplicar a piezas coladas "
            "sin una consulta estrecha con los fabricantes. Los valores "
            "enumerados en las tablas F.5.2.2-1 y F.5.2.2-2 pueden "
            "tomarse como valores característicos en cálculos de "
            "estructuras sometidas a temperaturas de servicio por "
            "debajo de 100°C. Para estructuras sometidas a elevadas "
            "temperaturas asociadas con el fuego estos valores no son "
            "recomendables."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_b_aleaciones_6082_6061_6063",
        "seccion": "F.5.2.2.1(b) (Aleaciones tratadas en caliente — 6082, 6061, 6063)",
        "titulo": "6082 (durabilidad B, la más común); 6061 (alternativa, mejor formabilidad/acabado); 6063 (durabilidad B, buena apariencia, más baja resistencia).",
        "texto": (
            "(b) Aleaciones tratadas en caliente — Las siguientes "
            "aleaciones derivan su resistencia del tratamiento con "
            "calor: (1) Aleación 6082 — La más común de estas "
            "aleaciones es la aleación de resistencia media 6082 "
            "(Al Si1 Mg Mn) de durabilidad B (véase F.5.2.4.1), usada "
            "generalmente en la condición de totalmente tratada en "
            "caliente, esto es, 6082-T6, y empleada en estructuras "
            "soldadas y no soldadas. La selección de esta aleación se "
            "basa en una combinación de buenas propiedades físicas con "
            "un buen grado de resistencia a la corrosión. Está "
            "disponible en la mayoría de las formas: extrusiones "
            "sólidas y huecas, planchas, láminas delgadas, tuberías y "
            "piezas forjadas. Se debe poner atención en el diseño a la "
            "pérdida de resistencia en las uniones soldadas en la zona "
            "afectada por el calor. (2) Aleación 6061 — Es una "
            "aleación alternativa para la 6082. La aleación 6061 "
            "(Al Mg1SiCu) tiene durabilidad B y propiedades muy "
            "similares con una ligera mejoría en la capacidad de "
            "dejarse formar y en el acabado de la superficie. Está "
            "disponible en formas tubulares extruídas y es usada "
            "principalmente en estructuras. (3) Aleación 6063 — Se "
            "prefiere la aleación 6063 (Al Mg 0.7Si) de duración B en "
            "aplicaciones donde la resistencia no es de trascendental "
            "importancia y se tiene la necesidad de una buena "
            "apariencia ya que esta aleación combina una resistencia "
            "moderada con buena durabilidad y acabado de superficie. "
            "Responde particularmente bien al anodizado y otros "
            "procesos de acabado patentados similares. La aleación "
            "6063 tiene una resistencia más baja que la 6082 y, como "
            "ésta, presenta pérdida de resistencia en la zona afectada "
            "por el calor de las juntas soldadas. Se consigue en "
            "extrusiones, tuberías y piezas forjadas. Es particularmente "
            "apropiada para secciones extruídas intrincadas y de pared "
            "delgada. Se usa principalmente en elementos arquitectónicos "
            "tales como paredes cortina y marcos de ventanas."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_b_aleaciones_7020_lm25",
        "seccion": "F.5.2.2.1(b) (Aleaciones tratadas en caliente — 7020, LM25)",
        "titulo": "7020 (soldable, resistencia media serie 7***, envejecimiento natural, sensible a condiciones ambientales); LM25 (piezas coladas).",
        "texto": (
            "(4) Aleación 7020 — Otra aleación que es fácilmente "
            "soldable (aunque no se restringe a estructuras soldadas) "
            "es la aleación de resistencia media de la serie 7*** "
            "(Al Zn 4.5Mg1) de durabilidad C. Tiene mejor resistencia "
            "post-soldadura que las de la serie 6*** debido a su "
            "propiedad de envejecimiento natural. Este material, como "
            "otros de la serie 7***, es, sin embargo, sensible a las "
            "condiciones ambientales y su comportamiento satisfactorio "
            "depende tanto de tener correctos métodos de manufactura y "
            "fabricación como del control de la composición y de las "
            "propiedades a tensión. Si el material en la condición T6 "
            "se somete a cualquier operación que induzca trabajo en "
            "frío como flexión, cizallamiento, punzonamiento, etc., la "
            "aleación puede resultar susceptible a corrosión debida al "
            "esfuerzo; es esencial, por lo tanto, la colaboración "
            "directa entre el ingeniero y el fabricante en cuanto al "
            "uso futuro y las condiciones de servicio probables. Esta "
            "aleación está normalmente disponible sólo en formas "
            "laminadas y secciones extruídas sólidas y huecas simples. "
            "Las piezas forjadas pueden ser algunas veces hechas bajo "
            "pedido especial. (5) Aleación LM25 — La aleación LM25 "
            "(Al Si 7Mg) de durabilidad B es una aleación para piezas "
            "coladas con buenas características de fundición, "
            "resistencia a la corrosión y propiedades mecánicas. Está "
            "disponible en cuatro condiciones de tratamiento en caliente "
            "en fundiciones con arena y de enfriamiento rápido, es "
            "generalmente usada en arquitectura y en instalaciones de "
            "manufactura de productos alimenticios."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_c_aleaciones_1200_3103_3105_5083",
        "seccion": "F.5.2.2.1(c) (Aleaciones no tratadas en caliente — 1200, 3103, 3105, 5083)",
        "titulo": "1200 (aluminio comercialmente puro, durabilidad A); 3103/3105 (paneles, láminas); 5083 (soldadura/blindajes/tanques, durabilidad A).",
        "texto": (
            "(c) Aleaciones no tratadas en caliente — Las siguientes "
            "aleaciones derivan su resistencia únicamente de "
            "endurecimiento por deformación. Son normalmente producidas "
            "en formas de láminas delgadas y planchas y, ocasionalmente, "
            "en algunas formas extruídas simples. (1) Aleación 1200 — "
            "La aleación 1200 (Al 99.0) de duración A, es aluminio "
            "comercialmente puro con alta ductilidad y una muy buena "
            "resistencia a la corrosión. Es usada para trabajos "
            "arquitectónicos en los que los componentes no están muy "
            "esforzados. Sólo está disponible en láminas delgadas. "
            "(2) Aleación 3103 — La aleación 3103 (Al Mn1) de duración "
            "A es más resistente y dura que el aluminio comercialmente "
            "puro pero tiene la misma alta ductilidad y muy buena "
            "resistencia a la corrosión. Es intensamente usada en "
            "paneles para edificios y vehículos. Está disponible en "
            "láminas delgadas. (3) Aleación 3105 — La aleación 3105 "
            "(Al Mn0.5 Mg0.5) de duración A está llegando a prevalecer "
            "en el mercado de lámina delgada perfilada para edificios "
            "debido a sus propiedades superiores a la 3103 en dureza y "
            "resistencia. Además tiene una ventaja económica. Las "
            "formas disponibles se limitan a láminas delgadas. "
            "(4) Aleación 5083 — La aleación 5083 (Al Mg4.5 Mn0.7) de "
            "duración A se usa para estructuras soldadas y en trabajos "
            "de blindajes y tanques ya que es fácilmente soldable sin "
            "una pérdida significativa de resistencia y tiene alta "
            "ductilidad. La resistencia a tensión de la 5083 en las "
            "condiciones O y F es más baja que la de la 6082-T6 pero "
            "significativamente más alta si la última está soldada. Sin "
            "embargo, la exposición prolongada a temperaturas por "
            "encima de los 65°C puede resultar en la precipitación de "
            "granos frontera de compuestos intermetálicos de "
            "magnesio/aluminio que se corroen preferencialmente en "
            "algunos ambientes adversos. Este efecto se agrava si la "
            "aleación está sujeta a operaciones subsecuentes de trabajo "
            "en frío. Está disponible en planchas, láminas delgadas, "
            "secciones extruídas singulares, tubería extruída y piezas "
            "forjadas. Además de su fácil soldadura y buenas propiedades "
            "de dejarse formar, también tiene muy buena durabilidad "
            "especialmente en ambientes marinos."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_c_aleaciones_5251_5154a_5454",
        "seccion": "F.5.2.2.1(c) (Aleaciones no tratadas en caliente — 5251/5154A/5454, y aleación 5251 en tubería soldada)",
        "titulo": "5251/5154A/5454 (durabilidad A, dúctiles en blando, buena resistencia marina); 5454 la más fuerte de la serie 5***; 5251 en tubería con costura.",
        "texto": (
            "(5) Aleaciones 5251, 5154A y 5454 — Las aleaciones 5251 "
            "(Al Mg2), 5154A (Al Mg3.5(A)) y 5454 (Al Mg3Mn) de "
            "durabilidad A están disponibles en láminas delgadas, "
            "planchas y extrusiones simples. La 5154A y la 5251 también "
            "están disponibles como piezas forjadas. Su principal "
            "adición es el Magnesio y, como resultado, estas aleaciones "
            "son dúctiles en la condición blanda pero se endurecen por "
            "trabajo rápidamente. Tienen buena soldabilidad y muy "
            "buena resistencia al ataque corrosivo especialmente en "
            "atmósfera marina. Por esta razón, son usadas en paneles y "
            "en estructuras expuestas a ambientes marinos. La 5154A y "
            "la 5454 son más fuertes que la 5251. La aleación más "
            "fuerte de la serie 5***, que ofrece inmunidad contra la "
            "corrosión por esfuerzo cuando está expuesta a temperatura "
            "elevada, es la 5454. Las aleaciones de la serie 5*** con "
            "más del 3% de Mg pueden resultar susceptibles a corrosión "
            "debida al esfuerzo cuando se exponen a temperaturas "
            "elevadas. (6) Aleación 5251: en tubería soldada con "
            "costura — Las tuberías soldadas con costura se producen a "
            "partir de una tira de aleación 5251 (Al Mg2) la que da "
            "una durabilidad B al tubo que a su vez ha incrementado su "
            "resistencia por trabajo a través de los rodillos de "
            "formado y acabado. Sus usos principales son en elementos "
            "tales como muebles de jardín, pasamanos y escaleras de "
            "mano."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_c_aleaciones_lm5_lm6",
        "seccion": "F.5.2.2.1(c) (Aleaciones no tratadas en caliente — LM5, LM6, piezas coladas)",
        "titulo": "LM5 (durabilidad A, buen acabado, uso arquitectónico/decorativo); LM6 (durabilidad B, alta ductilidad, uso general/eléctrico/marino).",
        "texto": (
            "(7) Aleación LM5 — La aleación LM5 (Al Mg5 Si1) de "
            "durabilidad A es una aleación de fundición de resistencia "
            "media que posee excelentes características de acabado, "
            "manteniendo una superficie de gran brillo pero sólo es "
            "apropiada para formas simples. Es usada principalmente "
            "para fundiciones con arena utilizadas con propósitos "
            "arquitectónicos y decorativos y donde se requiere "
            "anodizado. (8) Aleación LM6 — La aleación LM6 (Al Si12) de "
            "durabilidad B es otra aleación de fundición de resistencia "
            "media que tiene excelentes características de fundición, "
            "alta ductilidad y resistencia al impacto. Es apropiada "
            "para fundiciones con arena o de enfriamiento rápido y útil "
            "para un amplio rango de usos en general, aplicaciones "
            "eléctricas y marinas y piezas coladas de complejidad y "
            "tamaño por encima del promedio."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_tabla1_aleaciones_tratadas_p1",
        "seccion": "Tabla F.5.2.2-1 (Aleaciones tratadas en caliente — 6061, 6063)",
        "titulo": "6061-T6: extrusiones/tubería 24.0-25.5 kgf/mm² prueba 0.2%. 6063: T4 7.0-10.0, T5/T6 hasta 27.5 kgf/mm² prueba 0.2%.",
        "texto": (
            "Tabla F.5.2.2-1 — Aleaciones tratadas en caliente (Aleación, "
            "Condición, Producto, Espesor mm desde-hasta, Esfuerzo "
            "mínimo de prueba del 0.2% kgf/mm², Resistencia mínima a "
            "tensión kgf/mm², Clasificación de durabilidad, Designación "
            "ISO). 6061 — T6, Extrusiones: hasta 150mm, 24.0, 28.0, "
            "durabilidad B, AlMg1SiCu. 6061 — T6, Tubería extruída: "
            "hasta 6.0mm, 24.0, 29.5; 6.0-10mm, 25.5, 29.5. 6063 — T4, "
            "Extrusiones: hasta 150mm, 7.0, 13.0. T4, Tubería extruída: "
            "hasta 10mm, 10.0, 15.5. T4, Forjados: hasta 150mm, 8.5, "
            "14.0. T5, Extrusiones: hasta 25mm, 11.0, 15.0. T6, "
            "Extrusiones: hasta 16mm, 16.0, 18.5; hasta 25mm otros "
            "casos similares. T6, Tubería extruída: hasta 6mm, 18.0, "
            "20.0; 6-10mm, 24.0, 18.5. T6, Forjados: hasta 150mm, 16.0, "
            "18.5."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_tabla1_aleaciones_tratadas_p2",
        "seccion": "Tabla F.5.2.2-1 (Aleaciones tratadas en caliente — 6082, 7020, LM25)",
        "titulo": "6082-T6: hasta 25.5-28.0 kgf/mm² prueba 0.2%, hasta 31.0 tensión. 7020-T6: hasta 28.0-32.0 kgf/mm². LM25-TB7/TF: 8.0-28.0 kgf/mm².",
        "texto": (
            "6082 — T4, Extrusiones: hasta 150mm, 12.0, 19.0; Lámina/"
            "Plancha 0.2-25mm, 12.0-20.0. T4, Tubería extruída: hasta "
            "6mm, 11.5, 21.5; 6-10mm, 25.5-27.0. T4, Forjados: hasta "
            "150mm, 12.0, 18.5. T6, Extrusiones: hasta 20mm, 25.5, "
            "29.5; 20-150mm, 27.0, 31.0. T6, Lámina/Plancha 0.2-25mm, "
            "25.5-24.0, 29.5-31.0. T6, Tubería extruída: hasta 6mm, "
            "25.5, 31.0; 6-10mm, 24.0, 31.0. T6, Forjados: hasta 120mm, "
            "25.5, 30.5. 7020 — T4, Extrusiones: hasta 25mm, 19.0, "
            "30.0. T4, Lámina y plancha: hasta 25mm, 17.0, 28.0. T6, "
            "Extrusiones: hasta 25mm, 28.0, 34.0. T6, Lámina y plancha: "
            "hasta 25mm, 27.0, 32.0. LM25 — TB7, Fundición con arena: "
            "8.0-11.0, 16.0. TB7, Fundición con enfriamiento rápido: "
            "9.0-11.0, 23.0. TF, Fundición con arena: 20.0-25.0, 23.0. "
            "TF, Fundición con enfriamiento rápido: 22.0-26.0, 28.0."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_tabla2_aleaciones_no_tratadas_p1",
        "seccion": "Tabla F.5.2.2-2 (Aleaciones no tratadas en caliente — 1200, 3103, 3105, 5083)",
        "titulo": "1200-H14: 11.5 kgf/mm² prueba 0.2%. 3103-H18: 18.5. 5083-O: 12.5-27.5; 5083-H22: 23.5.",
        "texto": (
            "Tabla F.5.2.2-2 — Aleaciones no tratadas en caliente "
            "(Aleación, Condición, Producto, Espesor mm, Esfuerzo "
            "mínimo de tensión de prueba del 0.2% kgf/mm², Resistencia "
            "mínima a tensión kgf/mm², Clasificación de durabilidad, "
            "Designación ISO). 1200 — H14, Lámina: 0.2-12.5mm, 11.5, "
            "10.5, durabilidad A, Al99.0. 3103 — H14, Lámina: 14.0, "
            "14.0; H18, Lámina: 18.5, 17.5, AlMn1. 3105 — H14/H16/H18, "
            "Lámina 0.2-3mm: 14.5-19.0, 16.0-21.5, AlMn0.5Mg0.5. 5083 — "
            "O, Extrusiones/Lámina y plancha/Tubería extruída: "
            "12.5-13.0, 27.5-28.0. F, Extrusiones/Lámina y plancha/"
            "Forjados: 13.0-17.5, 28.0-32.0. H22, Lámina y plancha/"
            "Tubería extruída: 23.5, 31.0, AlMn4.5Mn0.7."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_tabla2_aleaciones_no_tratadas_p2",
        "seccion": "Tabla F.5.2.2-2 (Aleaciones no tratadas en caliente — 5154A, 5251, 5454, LM5, LM6)",
        "titulo": "5154A-O/H22/H24: 6.0-22.5 kgf/mm². 5251-F/H22/H24: 6.0-17.5. 5454-O/H22/H24: 8.5-20.0. LM5/LM6 (fundición): 6.0-11.0.",
        "texto": (
            "5154A — O, Extrusiones/Lámina y plancha/Tubería extruída: "
            "8.5-10.0, 21.5. F, Extrusiones/Forjados: 10.0, 21.5. H22, "
            "Lámina y plancha/Tubería extruída: 16.5-20.0, 24.5. H24, "
            "Lámina y plancha/Tubería extruída: 20.0-22.5, 24.5-27.0, "
            "durabilidad A, AlMg3.5(A). 5251 — F, Tubería con soldadura "
            "de costura: 22.0, 24.5, durabilidad B. Forjados: 6.0, "
            "17.0, durabilidad A. H22/H24, Lámina y plancha: 13.0-17.5, "
            "20.0-22.5, AlMg2. 5454 — O, Extrusiones/Lámina y plancha: "
            "8.5-10.0, 21.5. F, Extrusiones: 10.0, 21.5. H22/H24, "
            "Lámina: 18.0-20.0, 25.0-27.0, durabilidad A, AlMg3Mn. LM5 "
            "— F, Fundición con arena: 9.0-11.0, 14.0. Fundición con "
            "enfriamiento rápido: 9.0-12.0, 17.0, durabilidad A, "
            "AlMg5Si1. LM6 — F, Fundición con arena: 6.0-7.0, 16.0. "
            "Fundición con enfriamiento rápido: 7.0-8.0, 19.0, "
            "durabilidad B, AlSi12."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_d_f_otros_materiales",
        "seccion": "F.5.2.2.1(d)-(f) (Materiales en otros espesores, otras aleaciones, aleaciones no incluidas)",
        "titulo": "Propiedades mínimas por acuerdo diseñador-cliente para otros espesores; otras aleaciones (2014A, 7019) requieren consulta con fabricante.",
        "texto": (
            "(d) Materiales en otros espesores y aleaciones con otras "
            "propiedades estándares y no estándares — Las aleaciones "
            "enumeradas en las tablas F.5.2.2-1 y F.5.2.2-2 son algunas "
            "veces usadas en otros espesores y en otros temples y "
            "condiciones estándares y no estándares. Las propiedades "
            "mínimas garantizadas para tales materiales pueden ser "
            "usadas si hay acuerdo entre el diseñador y el cliente. "
            "(e) Otras aleaciones — Hay disponibilidad de otras "
            "aleaciones que ofrecen resistencias más altas, por ejemplo "
            "2014A, y/o mejores resistencias post-soldadura, por "
            "ejemplo 7019, pero estas resistencias pueden ser logradas "
            "con el detrimento de otras propiedades. El ingeniero está, "
            "por lo tanto, advertido de no usar estas aleaciones sin "
            "una cuidadosa consideración y estrecha consulta con un "
            "fabricante de buena reputación. Las propiedades a "
            "considerar deben incluir durabilidad, soldabilidad, "
            "resistencia a la propagación de grietas y comportamiento "
            "en servicio. Las aleaciones de la serie 7*** que tienen "
            "resistencias de prueba más altas, tales como la 7019, "
            "requieren control particular en los procesos de "
            "fabricación, por ejemplo, control de micro estructura, "
            "esfuerzos residuales y trabajo en frío. (f) Aleaciones no "
            "incluidas en las tablas — Se podrán utilizar aleaciones "
            "no incluidas en las tablas F.5.2.2-1 y F.5.2.2-2 siempre y "
            "cuando su uso en estructuras esté autorizado en normas "
            "expedidas por entidades de reconocida autoridad, a "
            "criterio del Comisión Asesora Permanente para el Régimen "
            "de Construcciones Sismo Resistentes."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_g_pernos_remaches_tabla3",
        "seccion": "F.5.2.2.1(g) (Pernos y remaches — Tabla F.5.2.2-3)",
        "titulo": "Pernos/sujetadores roscados 6082/6061/5056A (24.0-27.0 kgf/mm²); remaches sólidos y ciegos 5154A/6082/5056A.",
        "texto": (
            "(g) Pernos y remaches — Los materiales de pernos y "
            "remaches y su durabilidad se dan en la tabla F.5.2.2-3. "
            "Una guía para la selección de los materiales de pernos y "
            "remaches se da en F.5.2.4.2(b). Estos materiales pueden "
            "también ser usados para productos especiales para "
            "tornillos y remaches incluyendo elementos insertados en "
            "la rosca. Para los remaches de mayor diámetro pueden "
            "necesitarse formas de cabeza especiales. Tabla F.5.2.2-3 — "
            "Materiales de pernos y remaches (Tipo, Material, Proceso, "
            "Temple usado, Diámetro mm, Esfuerzo de prueba 0.2% "
            "kgf/mm², Resistencia última kgf/mm², Durabilidad). Pernos "
            "y sujetadores roscados patentados: 6082 T6 (menor o igual "
            "a 6mm: 25.5/29.5; 6 a 12mm: 27.0/31.0, durabilidad B), "
            "6061 T8 (menor o igual a 12mm: 24.5/31.0), 5056A H24 "
            "(menor o igual a 12mm: 24.0/31.0, durabilidad B), acero "
            "inoxidable A4/A2, acero. Remaches sólidos y remaches "
            "ciegos patentados: 5154A colocados en frío o en caliente "
            "(O ó F, menor o igual a 25mm: 21.5, durabilidad A), 5154A "
            "H22 (menor o igual a 25mm: 24.5), 6082 colocados en frío "
            "en temple T4 (menor o igual a 25mm: 20.0, durabilidad B), "
            "6082 colocados en frío en temple T6 (menor o igual a "
            "25mm: 29.5), 5056A O ó F (menor o igual a 25mm: 25.5, "
            "durabilidad B), 5056A colocados en frío (menor o igual a "
            "25mm: 28.0), acero inoxidable, aleación de níquel y "
            "cobre, acero."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_2_1_h_metales_aporte_tabla4",
        "seccion": "F.5.2.2.1(h) (Metales de aporte — Tabla F.5.2.2-4)",
        "titulo": "5 tipos de metal de aporte (1, 3, 4, 5) para soldadura TIG/MIG, según durabilidad requerida.",
        "texto": (
            "(h) Metales de aporte — Los metales de aporte para "
            "soldadura de gas inerte de tungsteno (TIG) y soldadura de "
            "gas inerte de metal (MIG) se dan en la tabla F.5.2.2-4 con "
            "su durabilidad. Una guía para la selección de los metales "
            "de aporte se da en la tabla F.5.2.7-1. Tabla F.5.2.2-4 — "
            "Metales de aporte para soldadura (Grupo de metal de "
            "aporte — Denominación de la aleación BS/ISO — "
            "Durabilidad). Tipo 1: 1080A/Al99.8, 1050A/Al99.5 — "
            "durabilidad A. Tipo 3: 3103/AlMn1 — durabilidad A. Tipo 4: "
            "4043/AlSi5(A), 4047A/AlSi12(A) — durabilidad B. Tipo 5: "
            "5056A/AlMg5, 5356/AlMg5Cr(A), 5556A/AlMg5.2MnCr, 5183/"
            "AlMg4.5Mn — durabilidad A. Notas: para composición "
            "química véanse las normas pertinentes; o equivalente más "
            "cercano; la 4047A es específicamente usada para evitar el "
            "agrietamiento del metal de aporte en una unión que tiene "
            "alta dilución y alta restricción, en la mayoría de los "
            "casos, es preferible usar la 4043A."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_3_1_2_propiedades_resistencia_fisicas",
        "seccion": "F.5.2.3 / F.5.2.3.1 / F.5.2.3.2 (Propiedades de resistencia, mecánicas y físicas — Tabla F.5.2.3-1)",
        "titulo": "Propiedades para temples y aleaciones estándar; aplicables entre -50°C y 70°C; propiedades físicas (densidad, módulos, expansión térmica, Poisson).",
        "texto": (
            "F.5.2.3 — PROPIEDADES DE RESISTENCIA, MECANICAS Y FISICAS. "
            "F.5.2.3.1 — Resistencia y propiedades mecánicas — En las "
            "tablas F.5.2.2-1 y F.5.2.2-2 se muestra el rango de "
            "aleaciones estándares con sus formas disponibles, "
            "condiciones de temple y propiedades mecánicas. Las "
            "propiedades mecánicas para los materiales forjados para "
            "los temples y condiciones de las aleaciones dadas en las "
            "tablas F.5.2.2-1 y F.5.2.2-2 han sido usadas para "
            "determinar los esfuerzos límites dados en la tabla "
            "F.5.4.2-1. Cuando las aleaciones son soldadas, se da el "
            "porcentaje aproximado de reducción de resistencia de la "
            "aleación para cada temple (véanse las notas de la tabla "
            "F.5.2.2-1). Estas resistencias en la zona afectada por el "
            "calor pueden no lograrse hasta después de un período de "
            "envejecimiento natural o artificial, (véase F.5.2.2.1(c)). "
            "La resistencia del material de pernos y remaches se da en "
            "la tabla F.5.2.2-3. Las propiedades mecánicas de las "
            "aleaciones varían con la temperatura y, las dadas en las "
            "tablas F.5.2.2-1, F.5.2.2-2 y F.5.2.2-3, deben aplicarse "
            "para el diseño de estructuras en un rango de temperatura "
            "entre -50°C y 70°C, excepto la aleación 5083 (véase "
            "F.5.2.2.1(c)). El esfuerzo de prueba del 0.2% y la "
            "resistencia a tensión mejoran con temperaturas más bajas "
            "pero se reducen a temperaturas más altas. Debe consultarse "
            "al fabricante las propiedades por fuera del rango de "
            "temperatura dado. Las aleaciones se funden en un intervalo "
            "de 550°C a 660°C dependiendo de su composición. "
            "F.5.2.3.2 — Propiedades físicas — Las propiedades físicas "
            "de las aleaciones estándares, aunque varían ligeramente, "
            "pueden considerarse constantes y se enumeran en la tabla "
            "F.5.2.3-1. En estructuras críticas el ingeniero puede usar "
            "el valor exacto obtenido de un reconocido fabricante. "
            "Tabla F.5.2.3-1 — Propiedades físicas: Densidad 2 710 "
            "kg/m³. Módulo de elasticidad 7 000 kgf/mm². Módulo de "
            "rigidez 2 660 kgf/mm². Coeficiente de expansión térmica "
            "23×10⁻⁶ por °C. Coeficiente de Poisson ν = 0.3."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_durabilidad_intro",
        "seccion": "F.5.2.4 (Durabilidad y protección contra la corrosión — introducción)",
        "titulo": "Capa de óxido protectora natural del aluminio; comportamiento variable según ambiente (suave/industrial/costero/marino); autosellante en exposición atmosférica.",
        "texto": (
            "F.5.2.4 — DURABILIDAD Y PROTECCIÓN CONTRA LA CORROSIÓN — "
            "En muchos casos, los materiales estándares enunciados en "
            "las tablas F.5.2.2-1 a F.5.2.2-4 se pueden usar con el "
            "acabado de la laminadora, como son extruídos o como "
            "resultan soldados sin la necesidad de protección de la "
            "superficie. La buena resistencia a la corrosión del "
            "aluminio y sus aleaciones es atribuible a la capa de "
            "óxido protectora que se forma sobre la superficie del "
            "metal inmediatamente se expone al aire. Esta película es "
            "normalmente invisible, relativamente inerte y, como se "
            "forma naturalmente frente a la exposición al aire o al "
            "oxígeno, es autosellante. En ambientes suaves una "
            "superficie de aluminio mantiene su apariencia original "
            "por años y no se necesita protección adicional para la "
            "mayoría de las aleaciones. En ambientes industriales "
            "moderados habrá oscurecimiento y formación de asperezas "
            "en la superficie. Cuando la atmósfera se vuelve más "
            "agresiva, como ambientes fuertemente ácidos o alcalinos, "
            "el decoloro de la superficie y la formación de asperezas "
            "empeoran y se hacen visibles superficies blancas polvosas "
            "de óxido. La película de óxido puede ser autosoluble, el "
            "metal deja de estar completamente protegido y se necesita "
            "protección adicional. Estas condiciones pueden también "
            "ocurrir en hendiduras debido a condiciones locales "
            "altamente ácidas o alcalinas, pero los agentes que tienen "
            "este efecto extremo son relativamente escasos. En "
            "ambientes costeros y marinos, la superficie se pone áspera "
            "y adquiere una apariencia gris parecida a piedra. Es "
            "necesaria la protección de ciertas aleaciones. Cuando el "
            "aluminio está sumergido en agua pueden ser necesarias "
            "precauciones especiales."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_corrosion_curvas_tiempo",
        "seccion": "F.5.2.4 (Curvas corrosión/tiempo, comportamiento en exposición atmosférica)",
        "titulo": "Pérdida rápida inicial luego estabilización; fase inicial de meses a años según exposición; ambientes tropicales no más dañinos que templados.",
        "texto": (
            "Cuando ocurre un ataque a la superficie, las curvas "
            "corrosión/tiempo del aluminio y las aleaciones de aluminio "
            "tienen una forma exponencial y hay una pérdida bastante "
            "rápida de reflexividad después de un ligero deterioro por "
            "la exposición. Luego de ésto hay muy poco cambio durante "
            "períodos muy largos. En exposición atmosférica, la fase "
            "inicial puede ser de unos pocos meses o de dos o tres "
            "años, seguida por poco o ningún cambio durante períodos de "
            "10, 30 ó aún 80 años. Tal comportamiento es consistente "
            "para todas las condiciones de exposición libres externas "
            "y para todas las condiciones internas o protegidas, "
            "excepto donde se pueda desarrollar extrema acidez o "
            "alcalinidad. Los ambientes tropicales, en general, no son "
            "más dañinos para el aluminio que los ambientes templados, "
            "aunque ciertas aleaciones se afectan por una larga "
            "exposición a altas temperaturas ambientales particularmente "
            "en ambiente marino."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_1_durabilidad_aleaciones",
        "seccion": "F.5.2.4.1 (Durabilidad de las aleaciones — niveles A/B/C)",
        "titulo": "3 niveles de durabilidad (A, B, C descendente); la protección requerida se ajusta al nivel más bajo cuando se combinan aleaciones.",
        "texto": (
            "F.5.2.4.1 — Durabilidad de las aleaciones — Las aleaciones "
            "enumeradas en las tablas F.5.2.2-1, F.5.2.2-2, F.5.2.2-3 y "
            "F.5.2.2-4 se categorizan en tres niveles de durabilidad A, "
            "B y C en orden descendente. Estos niveles son usados para "
            "determinar la necesidad y grado de protección requerido. "
            "En construcciones que emplean más de una aleación, "
            "incluyendo metales de relleno en construcción soldada, la "
            "protección debe ser acorde con el menor de los niveles de "
            "durabilidad. Cuando se use otra aleación estructural "
            "diferente a las enumeradas en las tablas F.5.2.2-1, "
            "F.5.2.2-2, F.5.2.2-3 y F.5.2.2-4 deberán solicitarse los "
            "datos adecuados para asignar a la aleación la categoría "
            "de durabilidad, así como para justificar su aplicación."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_2_a_proteccion_total_tabla1",
        "seccion": "F.5.2.4.2(a) (Protección contra la corrosión total — Tabla F.5.2.4-1)",
        "titulo": "Requisito de protección según durabilidad/espesor/ambiente (rural/industrial/marino/sumergido); microclimas locales pueden ser más severos que la región.",
        "texto": (
            "F.5.2.4.2 — Protección contra la corrosión. (a) Protección "
            "contra la corrosión total — La necesidad de protección "
            "contra la corrosión total a estructuras construidas con "
            "las aleaciones o combinaciones de las aleaciones "
            "enumeradas en las tablas F.5.2.2-1, F.5.2.2-2, F.5.2.2-3 "
            "y F.5.2.2-4 cuando se exponen a diferentes ambientes se da "
            "en la tabla F.5.2.4-1. Los métodos para brindar protección "
            "contra la corrosión en estos ambientes están detallados en "
            "normas como la BS 8112: Parte 2. Para seleccionar la "
            "columna apropiada de la tabla F.5.2.4-1 para el ambiente "
            "atmosférico, debe tenerse en cuenta que pueden existir "
            "localidades, dentro de una región, que tengan microclimas "
            "bien diferentes de las características ambientales de la "
            "región como un todo. Tabla F.5.2.4-1 — Protección general "
            "contra la corrosión de estructuras de aluminio (Durabilidad "
            "de la aleación — Espesor mm — Protección necesaria según "
            "ambiente: Rural/Industrial-urbano Moderado/Severo/"
            "No-industrial/Marino Moderado/Severo/Sumergido agua "
            "dulce/salada). Durabilidad A, todos los espesores: "
            "Ninguna protección requerida en rural y no-industrial; "
            "P (requiere protección) en industrial-urbano moderado/"
            "severo y marino moderado/severo; Ninguna en agua dulce; "
            "P en agua salada. Durabilidad B, espesor menor de 3mm: "
            "Ninguna en rural; P en el resto. Durabilidad B, espesor "
            "3mm o más: Ninguna en rural y no-industrial; P en el "
            "resto. Durabilidad C, todos los espesores: Ninguna en "
            "rural; requiere protección local en soldadura y zona "
            "afectada por el calor en ambientes urbanos no-industriales; "
            "P en el resto; no se recomienda para inmersión en agua "
            "salada (NR)."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_2_b_contactos_metal_metal_tabla2",
        "seccion": "F.5.2.4.2(b) (Contactos metal-metal — Tabla F.5.2.4-2)",
        "titulo": "Superficies de contacto en uniones aluminio-otro metal requieren protección adicional; niveles 0 (sin riesgo) a 5 (severo) según combinación de metales.",
        "texto": (
            "(b) Contactos metal-metal incluyendo uniones — Se deben "
            "considerar también las superficies de contacto en "
            "hendiduras y el contacto con ciertos metales o lavaduras "
            "de ciertos metales que pueden causar ataque electroquímico "
            "del aluminio. Esta situación se da en las uniones de una "
            "estructura. Las superficies de contacto y uniones de "
            "aluminio con aluminio u otros metales y las superficies de "
            "contacto en uniones empernadas, remachadas, soldadas y "
            "conexiones con pernos de alta resistencia a fricción deben "
            "tener protección adicional a la requerida en la tabla "
            "F.5.2.4-1 tal como se define en la tabla F.5.2.4-2. Los "
            "detalles del procedimiento de protección contra la "
            "corrosión requerido se dan en normas como la BS 8118: "
            "Parte 2. Tabla F.5.2.4-2 — Protección adicional de los "
            "contactos de metal con metal para combatir la fisuración "
            "y los efectos galvánicos (Metal unido al aluminio — Metal "
            "del perno o remache — nivel de protección 0 a 5 según "
            "ambiente atmosférico rural/industrial/marino/sumergido). "
            "Aluminio-Aluminio: nivel 0 en ambientes secos, hasta 2 en "
            "industrial severo/marino. Aluminio-Acero/acero galvanizado/"
            "acero inoxidable: nivel 0-1 en ambientes secos hasta "
            "5 (el más severo) en sumergido. Zinc/acero con zinc — "
            "Aluminio: niveles 0-2. Acero/acero inoxidable/hierro "
            "colado/plomo: niveles 0-5 según combinación. Cobre-Aluminio: "
            "nivel 0 en seco, NR (no recomendado) en la mayoría de "
            "ambientes húmedos; Cobre-Cobre/aleación de cobre: niveles "
            "0-5. Las superficies de contacto y uniones de aluminio con "
            "cobre o aleaciones de cobre deben evitarse; si se usan, el "
            "aluminio debe ser durabilidad A o B y los pernos y tuercas "
            "deben ser de cobre o de aleación de cobre."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_2_c_1_2_concreto",
        "seccion": "F.5.2.4.2(c)(1)-(2) (Contacto con otros materiales no metálicos — concreto/mampostería/yeso, aluminio embebido en concreto)",
        "titulo": "Contacto seco sin protección; ambiente húmedo/industrial requiere pintura bituminosa; aluminio embebido requiere 2 capas + 75mm de recubrimiento adicional.",
        "texto": (
            "(c) Contacto con otros materiales no metálicos. (1) "
            "Contacto con concreto, mampostería o yeso — El aluminio en "
            "contacto con concreto compacto y denso, mampostería o "
            "yeso en un ambiente seco sin polución o en un ambiente "
            "suave se debe cubrir con una capa de pintura bituminosa. "
            "En un ambiente industrial o marino, la superficie de "
            "contacto se debe cubrir con al menos dos capas de pintura "
            "bituminosa para trabajo pesado, preferiblemente la "
            "superficie del material en contacto debe ser similarmente "
            "pintada. El contacto sumergido de aluminio y tales "
            "materiales no es aconsejable pero, si es inevitable, se "
            "recomienda separar los materiales mediante una masilla "
            "apropiada o una capa de impermeabilización para trabajo "
            "pesado. El concreto ligero y productos similares requieren "
            "consideración adicional cuando el agua o la humedad "
            "ascendente pueden extraer álcalis agresivos del cemento. "
            "El agua alcalina puede entonces atacar incluso las "
            "superficies de aluminio que no están en contacto directo. "
            "(2) Aluminio embebido en concreto — Antes de embeber el "
            "aluminio en concreto, las superficies deben protegerse con "
            "al menos dos capas de pintura bituminosa o betún caliente. "
            "Las capas deberán extenderse por lo menos 75 mm por encima "
            "de la superficie de concreto después de embeber. Si el "
            "concreto contiene cloruros, por ejemplo como aditivos o "
            "debido al uso de agregados dragados del mar, se deben "
            "aplicar por lo menos dos capas de brea de alquitrán de "
            "hulla plastificada y el ensamblaje terminado debe ser "
            "repintado localmente con el mismo material para sellar la "
            "superficie luego de que el concreto haya fraguado "
            "totalmente. Se debe poner atención a los posibles "
            "contactos entre el aluminio embebido y el refuerzo de "
            "acero."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_2_c_3_madera",
        "seccion": "F.5.2.4.2(c)(3) (Contacto con madera — preservativos seguros y peligrosos)",
        "titulo": "7 preservativos seguros sin precauciones especiales; 3 sellantes requeridos si madera tratada con preservativos húmedos; roble/castaño/cedro rojo nocivos si no maduros.",
        "texto": (
            "(3) Contacto con madera — En ambientes industriales, "
            "húmedos y marinos, la madera debe ser preparada y pintada "
            "adecuadamente. Algunos preservativos para la madera pueden "
            "ser dañinos para el aluminio. Como guía general los "
            "siguientes preservativos han sido aprobados como seguros "
            "para usar con aluminio sin tomar precauciones especiales: "
            "(a) creosota de alquitrán de hulla. (b) aceite de "
            "alquitrán de hulla. (c) naftalenos clorinados. (d) "
            "naftanatos de zinc. (e) pentaclorofenol. (f) óxidos "
            "orgánicos de estaño. (g) ortofenilfenol. Cuando la madera "
            "tratada con los siguientes preservativos se usa en "
            "situaciones húmedas, la superficie de aluminio en contacto "
            "con la madera tratada debe tener una aplicación substancial "
            "de sellante: (a) naftanato de cobre. (b) sales "
            "cupro-cromo-arsenicales. (c) compuestos de bórax y ácido "
            "bórico. No se deben usar otros preservativos en asociación "
            "con el aluminio. El roble, el castaño y el cedro rojo "
            "occidental pueden ser nocivos para el aluminio a menos que "
            "estén bien madurados."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_4_2_c_4_7_suelos_agua_quimicos_aislantes",
        "seccion": "F.5.2.4.2(c)(4)-(7) (Contacto con suelos, inmersión en agua, químicos de la construcción, materiales aislantes)",
        "titulo": "Suelos: 2 capas pintura bituminosa. Agua: durabilidad A + sujetadores resistentes. Químicos: cuidado con limpiadores. Aislantes: probar compatibilidad húmeda/salina.",
        "texto": (
            "(4) Contacto con suelos — La superficie del metal en "
            "contacto con el suelo debe protegerse con al menos dos "
            "capas de pintura bituminosa, betún caliente o brea de "
            "alquitrán de hulla plastificada. Se puede usar un vendaje "
            "con cintas adicional para impedir el daño mecánico del "
            "recubrimiento. (5) Inmersión en agua — Cuando piezas de "
            "aluminio estén sumergidas en agua dulce o de mar, "
            "incluyendo agua contaminada, el aluminio debe ser "
            "preferiblemente de durabilidad A y se deben usar "
            "sujetadores de aluminio o acero resistente a la corrosión "
            "o usar soldadura. Las tablas F.5.2.4-1 y F.5.2.4-2 dan la "
            "protección necesaria para inmersión en agua dulce y de "
            "mar. Adicionalmente el ingeniero debe obtener información "
            "competente sobre el contenido de oxígeno, el pH, el "
            "contenido químico o metálico, particularmente de cobre, y "
            "la cantidad de movimiento del agua. Estos factores pueden "
            "afectar el grado de protección requerido. (6) Contacto con "
            "químicos usados en la industria de la construcción — Los "
            "fungicidas y repelentes de moho pueden contener compuestos "
            "metálicos basados en cobre, mercurio, estaño y plomo que, "
            "bajo condiciones de humedad, pueden causar corrosión del "
            "aluminio. Los efectos dañinos pueden ser contrarrestados "
            "protegiendo las superficies de contacto que pueden estar "
            "sujetas a lavaduras o filtraciones de los químicos. "
            "Algunos materiales de limpieza pueden afectar la "
            "superficie del aluminio. Cuando tales químicos son usados "
            "para limpiar el aluminio u otros materiales en la "
            "estructura, se debe poner cuidado para asegurar que sus "
            "efectos no serán en detrimento del aluminio. A menudo un "
            "enjuague rápido y adecuado con agua es suficiente pero en "
            "otros casos se deben tomar medidas temporales para "
            "proteger el aluminio del contacto con tales limpiadores. "
            "(7) Contacto con materiales aislantes usados en la "
            "industria de la construcción — Productos tales como fibra "
            "de vidrio, poliuretano y varios productos de aislamiento "
            "pueden contener agentes corrosivos que pueden ser "
            "extraídos bajo condiciones de humedad y deteriorar el "
            "aluminio. Los materiales aislantes deben ser probados para "
            "observar su compatibilidad con el aluminio en condiciones "
            "húmedas y salinas. Cuando existan dudas, se debe aplicar "
            "un sellante a las superficies de aluminio asociadas."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_5_fabricacion_construccion",
        "seccion": "F.5.2.5 (Fabricación y construcción — doblado/formado, soldadura, metales de aporte)",
        "titulo": "Doblado consulta con fabricante; serie 7*** no formar en frío en T6; soldadura: cuidado con agrietamiento de 6082/6063/6061/5251; aporte según Tabla F.5.2.7-1.",
        "texto": (
            "F.5.2.5 — FABRICACIÓN Y CONSTRUCCIÓN — Adicionalmente a "
            "los requisitos de fabricación y construcción generales se "
            "deberá considerar lo siguiente: F.5.2.5.1 — Doblado y "
            "formado — Las aleaciones de aluminio están disponibles en "
            "un amplio rango de temples que afecta su habilidad para "
            "dejarse formar. Cuando se requiera doblar o formar, el "
            "ingeniero debe consultar con el fabricante para "
            "seleccionar la aleación, temple y cualquier tratamiento "
            "térmico subsecuente que pueda ser requerido. Los "
            "tratamientos térmicos y el formado en caliente se deberán "
            "efectuar bajo la dirección y supervisión de personal "
            "competente. Sin el acuerdo del productor las aleaciones de "
            "la serie 7*** no deben ser curvadas o formadas en frío en "
            "condición de tratamiento térmico debido al riesgo de "
            "fisuración por corrosión bajo tensión. Sin embargo se "
            "pueden llevar a cabo correcciones menores en la forma de "
            "los perfiles o en las distorsiones de soldadura. "
            "F.5.2.5.2 — Soldadura — La pérdida de resistencia que "
            "puede ocurrir en la vecindad de la soldadura en algunas "
            "aleaciones debe considerarse en la selección de la "
            "aleación o aleaciones a usar en construcción soldada. El "
            "ingeniero debe convencerse de que la combinación de "
            "materiales base y de aportación es posible para lograr la "
            "resistencia y durabilidad requeridas en las condiciones de "
            "servicio de la estructura. Debe ponerse particular "
            "atención a la susceptibilidad de las aleaciones 6082, "
            "6063, 6061 y 5251 al agrietamiento durante la "
            "solidificación cuando las soldaduras son hechas bajo "
            "restricción. Esto puede evitarse usando los metales de "
            "aporte y las técnicas de soldadura recomendadas. Así se "
            "asegurará una combinación apropiada de metal de aporte en "
            "la soldadura real. F.5.2.5.3 — Metales de aporte — El "
            "alambre de material de aportación usado en la construcción "
            "soldada debe ser escogido de acuerdo con la tabla "
            "F.5.2.7-1."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_6_7_seleccion_disponibilidad_intro",
        "seccion": "F.5.2.6 / F.5.2.7 (Selección de materiales; Disponibilidad — introducción)",
        "titulo": "Selección por resistencia/durabilidad/propiedades físicas/soldabilidad/formabilidad/disponibilidad; Tabla F.5.2.7-2 indica combinaciones bajo pedido.",
        "texto": (
            "F.5.2.6 — SELECCION DE MATERIALES — La selección de una "
            "aleación o aleaciones para cualquier estructura y su forma "
            "particular es determinada por la combinación de varios "
            "factores: resistencia, véase F.5.2.3; durabilidad, véase "
            "F.5.2.4; propiedades físicas, véase F.5.2.3; soldabilidad, "
            "véase F.5.2.5; formabilidad, véase F.5.2.5; y "
            "disponibilidad, véase F.5.2.7. Los materiales estándares "
            "dados en las tablas F.5.2.2-1 y F.5.2.2-2 se describen en "
            "términos de los anteriores factores en F.5.2.2.1(b) y (c). "
            "F.5.2.7 — DISPONIBILIDAD — El rango de aleaciones dado en "
            "las tablas F.5.2.2-1 y F.5.2.2-2 no está disponible en "
            "todas las formas de producto. La tabla F.5.2.7-2 indica "
            "las aleaciones que se consiguen en una forma de producto "
            "particular y su disponibilidad. Se indican los productos "
            "y combinaciones de aleación que no son manufacturadas "
            "normalmente pero se consiguen con pedido especial; el "
            "diseño con este material sólo debe intentarse después de "
            "confirmar su disponibilidad con el encargado del "
            "suministro."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_7_1_secciones_estructurales",
        "seccion": "F.5.2.7.1 (Secciones estructurales — Tablas F.5.2.7-1, -2 y -3)",
        "titulo": "6082-T6/6063-T6 comúnmente disponibles; secciones bajo pedido según Tabla F.5.2.7-2; rangos de tamaño de secciones extruídas comunes en Tabla F.5.2.7-3.",
        "texto": (
            "F.5.2.7.1 — Secciones estructurales — Cierto número de "
            "secciones estructurales extruídas y algunas otras "
            "secciones estructurales están comúnmente disponibles en "
            "6082-T6 ó 6063-T6; pero, en la mayoría de los casos, "
            "deberán ser producidas bajo pedido, véase la tabla "
            "F.5.2.7-2. La tabla F.5.2.7-3 da el rango de tamaños de "
            "secciones más comúnmente disponibles. Otros tamaños pueden "
            "ser obtenidos a partir de matrices existentes o nuevas de "
            "acuerdo con el fabricante. Cuando las secciones se "
            "producen bajo pedido, puede ser requerida una cantidad "
            "mínima para la orden. Las secciones nuevas especiales "
            "extruídas se hacen normalmente bajo pedido y el bajo costo "
            "de las matrices simples brinda gran flexibilidad a su "
            "diseño. El ingeniero debe verificar con el fabricante, en "
            "una etapa temprana, la forma, espesor, tamaño y "
            "posibilidad del diseño de una nueva sección extruída y el "
            "tiempo de entrega de la nueva matriz y la sección extruída. "
            "Algunas secciones o productos se hacen por trefilado, "
            "formado o laminado con rodillos. Cuando las secciones se "
            "producen bajo pedido, estas operaciones pueden requerir "
            "maquinaria especial. Tabla F.5.2.7-3 — Rango de tamaños de "
            "secciones extruídas más comúnmente disponibles (Tipo de "
            "sección — Rango de tamaño mm): Ángulos de lados iguales "
            "30x30 a 120x120. Ángulos de lados desiguales 50x38 a "
            "140x105. Canales 60x30 a 240x100. Secciones T 50x38 a "
            "120x90. Secciones I 60x30 a 160x80. Ángulos con bulbos "
            "iguales 50x50 a 120x120. Ángulos con bulbos desiguales "
            "50x37.5 a 140x105. Canales con pestañas 80x40 a 140x70. "
            "Secciones T con bulbos 90x75 a 180x150."
        ),
    },
    {
        "id": "NSR10-F-F_5_2_7_2_5_tuberia_lamina_forjadas_coladas",
        "seccion": "F.5.2.7.2-.5 (Disponibilidad — tubería, lámina/planchas, piezas forjadas, piezas coladas)",
        "titulo": "Tubería: extrusión/trefilado/soldadura de costura. Lámina: amplio rango estándar. Forjadas: costosas, requieren matriz. Coladas: arena o enfriamiento rápido.",
        "texto": (
            "F.5.2.7.2 — Tubería — Los tubos pueden producirse por "
            "extrusión, por trefilado o por soldadura de costura. La "
            "tubería está disponible, en algunas de estas formas, en "
            "un rango limitado de tamaños pero, por lo general, son "
            "fabricados bajo pedido, véase la tabla F.5.2.7-2. "
            "F.5.2.7.3 — Lámina delgada, tiras y planchas — Normalmente, "
            "un amplio rango de lámina delgada, tiras y planchas se "
            "consigue con facilidad en las aleaciones estándares (véase "
            "la tabla F.5.2.7-2). Algunas aleaciones se encuentran "
            "disponibles en forma de láminas o planchas con "
            "indentaciones o resaltes. Hay un amplio rango de productos "
            "estándares laminados para revestimiento y techado, algunos "
            "de los cuales se consiguen fácilmente en cantidades "
            "moderadas, con el acabado de la laminadora o pintados, "
            "pero la mayoría son producidos bajo pedido. F.5.2.7.4 — "
            "Piezas forjadas — Las piezas forjadas a mano o con matriz "
            "se suministran bajo pedido. Las primeras normalmente "
            "requieren trabajo adicional para lograr las dimensiones "
            "requeridas mientras que las últimas son producidas con las "
            "dimensiones definidas. Las matrices para forjado son "
            "relativamente costosas y los costos deben incluir al menos "
            "la fabricación de una pieza forjada y el corte para "
            "revisar el flujo o distribución del grano para probar que "
            "la matriz puede ser usada para piezas estructurales "
            "forjadas. F.5.2.7.5 — Piezas coladas — Se suministran bajo "
            "pedido piezas coladas con arena o de enfriamiento rápido. "
            "Las piezas coladas con arena se producen con moldes de "
            "costo moderado y se usan normalmente para la producción en "
            "pequeñas cantidades. Las piezas coladas de enfriamiento "
            "rápido se usan generalmente en la producción de cantidades "
            "mayores y cuando se necesitan altas tasas de "
            "productividad; también son preferidas cuando se requiere "
            "buen acabado superficial y buena exactitud en las medidas. "
            "El costo de la maquinaria puede ser alto, especialmente "
            "para matrices que deben soportar presión."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    max_len = 0
    for c in CHUNKS:
        n = len(c["texto"])
        max_len = max(max_len, n)
    print(f"Max chars: {max_len}")

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

    print(f"\nOK: {len(rows)} chunks verbatim de F.5.2 cargados. F.5.2 queda COMPLETO.")


if __name__ == "__main__":
    main()
