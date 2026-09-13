"""
Título J — re-ingesta verbatim, Capítulo J.2 (parte 1 de 2): J.2.1 a J.2.5.2.4.
Continuación del lote J.1 (_ingest_titulo_j_j1_verbatim.py).

Fuente: NSR-10-1501-1570.pdf, páginas J-3 a J-7 (páginas reales del PDF 32-36).
Extraído VISUALMENTE (Read con render de imagen) por el mismo motivo que J.1:
pdftotext y fitz devuelven el carácter de reemplazo "�" en vez de tildes en
este PDF específico.

Reemplaza (no complementa) los chunks obsoletos NSR10-J-J_2_2_a_J_2_3_r1..r3
y NSR10-J-J_2_4_r1..r4 (resumen condensado, sin tildes) por 1 chunk verbatim
por numeral real. J.2.5.1 y J.2.5.2 no tenían chunk previo en absoluto para
estos numerales específicos -- son huecos reales nuevos, no reemplazo.

Numerales de esta parte: J.2.1, J.2.1.1, J.2.2 (+.1/.2/.2.1/.3), J.2.3 (intro
+ .1/.1.1/.1.2/.1.3/.1.4), J.2.4 (+.1 a .8, Tabla J.2.4-1), J.2.5 (+.1 con
J.2.5.1.1 a .10, .2 con J.2.5.2.1 a .4, Tablas J.2.5-2 y J.2.5-3).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título J — Requisitos de Protección Contra Incendios en Edificaciones"

IDS_OBSOLETOS = [
    "NSR10-J-J_2_2_a_J_2_3_r1", "NSR10-J-J_2_2_a_J_2_3_r2", "NSR10-J-J_2_2_a_J_2_3_r3",
    "NSR10-J-J_2_4_r1", "NSR10-J-J_2_4_r2", "NSR10-J-J_2_4_r3", "NSR10-J-J_2_4_r4",
]

CHUNKS = [
    {
        "id": "NSR10-J-J_2_1_1", "seccion": "J.2.1.1",
        "titulo": "J.2.1.1 — Alcance del Capítulo J.2: requisitos generales de configuración arquitectónica, estructural, eléctrica e hidráulica",
        "texto": "J.2.1 — ALCANCE. J.2.1.1 — A continuación se presentan los requisitos generales de configuración arquitectónica, estructural, eléctrica e hidráulica necesarios para la protección contra incendios en edificaciones y las especificaciones mínimas que deben cumplir los materiales utilizados con el propósito de proteger contra la propagación del fuego en el interior y hacia estructuras aledañas.",
    },
    {
        "id": "NSR10-J-J_2_2_1", "seccion": "J.2.2.1",
        "titulo": "J.2.2.1 — Dispositivos de interrupción de gas, electricidad y combustibles de fácil acceso al Cuerpo de Bomberos",
        "texto": "J.2.2 — REDES ELÉCTRICAS, DE GAS, Y OTROS FLUIDOS COMBUSTIBLES, INFLAMABLES O CARBURANTES. J.2.2.1 — En el interior de una edificación y en un lugar de fácil acceso para el Cuerpo de Bomberos deben instalarse dispositivos para interrumpir el suministro de gas, electricidad y otros fluidos combustibles, inflamables o comburentes.",
    },
    {
        "id": "NSR10-J-J_2_2_2", "seccion": "J.2.2.2",
        "titulo": "J.2.2.2 — Protección de instalaciones eléctricas: RETIE y Código Eléctrico Colombiano NTC 2050",
        "texto": "J.2.2.2 — Para la protección de las instalaciones eléctricas deben cumplirse los requisitos dados en el Reglamento Técnico de Instalaciones Eléctricas, RETIE, y en el Código Eléctrico Colombiano–NTC 2050.",
    },
    {
        "id": "NSR10-J-J_2_2_2_1", "seccion": "J.2.2.2.1",
        "titulo": "J.2.2.2.1 — Sistemas eléctricos en ambientes con peligro de incendio/explosión: Capítulo 5 NTC 2050 y RETIE",
        "texto": "J.2.2.2.1 — Los sistemas eléctricos en zonas donde pueda existir el peligro de incendio o explosión debido a gases o vapores inflamables, líquidos inflamables, polvo combustible, etc., deben cumplir con los requisitos adicionales dados en el Capítulo 5 del Código Eléctrico Colombiano–NTC 2050, \"Ambientes Especiales\" y en el Reglamento Técnico de Instalaciones Eléctricas, RETIE.",
    },
    {
        "id": "NSR10-J-J_2_2_3", "seccion": "J.2.2.3",
        "titulo": "J.2.2.3 — Estaciones de servicio de gasolina y combustibles: Decreto 4299 de 2005 y Ministerio de Minas y Energía",
        "texto": "J.2.2.3 — Las estaciones de servicio de gasolina y combustibles, deberán cumplir las normas específicas de seguridad reglamentadas por el Decreto Nacional 4299 de 2005 y la reglamentación específica del Ministerio de Minas y Energía.",
    },
    {
        "id": "NSR10-J-J_2_3_intro", "seccion": "J.2.3",
        "titulo": "J.2.3 — Requisitos de acceso a la edificación (introducción): planeamiento urbanístico, vanos en fachada, redes de suministro de agua",
        "texto": "J.2.3 — REQUISITOS DE ACCESO A LA EDIFICACIÓN. Tanto el planeamiento urbanístico, como las condiciones de diseño y construcción de las edificaciones, en particular su entorno inmediato, sus vanos en fachada y la configuración de las redes de suministro de agua, deben posibilitar y facilitar la intervención de los servicios de extinción de incendios, para lo cual se deben cumplir los requisitos de localización y ubicación, que se prescriben a continuación:",
    },
    {
        "id": "NSR10-J-J_2_3_1_1", "seccion": "J.2.3.1.1",
        "titulo": "J.2.3.1.1 — Acceso Frontal: 8% del perímetro con frente a vía o espacio frontal de acceso para bomberos",
        "texto": "J.2.3.1 — ACCESO A LA EDIFICACIÓN — Toda edificación debe proveerse de áreas de acceso adecuadas para el Cuerpo de Bomberos, de acuerdo con las normas siguientes: J.2.3.1.1 — Acceso Frontal — Toda edificación debe tener, al menos, el 8% de su perímetro total medido al nivel del piso de mayor área encerada con frente directamente a una vía o espacio frontal de acceso, en donde debe disponerse de vanos que permitan el acceso desde el exterior al personal del cuerpo de bomberos.",
    },
    {
        "id": "NSR10-J-J_2_3_1_2", "seccion": "J.2.3.1.2",
        "titulo": "J.2.3.1.2 — Acceso sobre el nivel del terreno: vanos mínimos 120x80cm, distancia máxima 25m entre vanos consecutivos",
        "texto": "J.2.3.1.2 — Sobre el Nivel del Terreno — El acceso debe proporcionarse directamente desde el exterior a cada planta localizada por debajo de una altura de 30 m. Los niveles localizados por encima de 30 m de altura deben tener accesos internos a los medios de evacuación hasta llegar a los niveles en los que exista acceso directo desde el exterior (Véase K.3.1.4 para la definición de Medios de Evacuación). En todo caso, los accesos deben proporcionar una abertura de por lo menos 120 cm de altura por 80 cm de ancho y cuyo reborde o antepecho no sobrepase una altura de 90 cm por encima del nivel de cada piso interior. La distancia máxima entre los ejes verticales de dos vanos consecutivos no debe exceder 25 metros, medidos sobre la fachada. No deben instalarse elementos que impidan o dificulten el acceso al interior del edificio a través de dichos vanos.",
    },
    {
        "id": "NSR10-J-J_2_3_1_3", "seccion": "J.2.3.1.3",
        "titulo": "J.2.3.1.3 — Acceso bajo el nivel del terreno: escaleras/puertas/ventanas con abertura mínima 120x80cm",
        "texto": "J.2.3.1.3 — Bajo el Nivel del Terreno — El acceso debe proporcionarse directamente desde el exterior a la primera planta o semisótano localizado bajo el nivel del terreno. Tal acceso debe consistir en escaleras, puertas, ventanas, paneles o cualquier otro medio que proporcione una abertura de por lo menos 120 cm de altura por 80 cm de ancho y cuyo reborde o antepecho no sobrepase una altura mayor de 90 cm por encima del nivel del piso interior.",
    },
    {
        "id": "NSR10-J-J_2_3_1_4", "seccion": "J.2.3.1.4",
        "titulo": "J.2.3.1.4 — Excepciones al requisito de acceso bajo el nivel del terreno (R-1 y R-2 con condiciones)",
        "texto": "J.2.3.1.4 — Los requisitos que figuran en el numeral J.2.3.1.3 pueden obviarse en los siguientes casos: (a) En edificaciones del Grupo de Ocupación \"Residencial Unifamiliar o Bifamiliar\" (R-I). (b) En cualquier edificación clasificada en el Grupo de Ocupación \"Residencial Multifamiliar\" (R-2), con menos de tres pisos de altura y con un número de unidades de vivienda no superior a dos por cada piso, cuando su sótano o semisótano se utiliza para ocupaciones adicionales al simplemente residencial.",
    },
    {
        "id": "NSR10-J-J_2_4_1", "seccion": "J.2.4.1",
        "titulo": "J.2.4.1 — Separación vertical entre aberturas de muros de fachadas (Grupos A/C/F/P, >3 pisos)",
        "texto": "J.2.4 — PREVENCION DE LA PROPAGACION DEL FUEGO HACIA EL EXTERIOR. J.2.4.1 — SEPARACION VERTICAL ENTRE ABERTURAS DE MUROS DE FACHADAS — Para las edificaciones de los Grupos de Ocupación de Almacenamiento (A), Comercial (C), Fabril e Industrial (F) y Alta Peligrosidad (P) que tengan más de tres pisos de altura, todas las aberturas exteriores en planos verticales deben tener separaciones entre otras aberturas a su alrededor, de por lo menos 1 m, o estar separadas por dichas aberturas por un escudo horizontal o vertical que se proyecte por lo menos 60 cm desde la pared, a lo largo de toda la longitud de la abertura. Se excluye de esta exigencia a las edificaciones que cuenten con un sistema completo de extinción de incendios.",
    },
    {
        "id": "NSR10-J-J_2_4_2", "seccion": "J.2.4.2",
        "titulo": "J.2.4.2 — Parapetos de mínimo 1m sobre muros de fachada (Grupos A/F/P)",
        "texto": "J.2.4.2 — PARAPETOS SOBRE MUROS DE FACHADA — Deben construirse parapetos, de por lo menos 1 m de altura, sobre los muros de fachada de cualquier edificación de los grupos de ocupación de Almacenamiento (A), Fabril e Industrial (F) y Alta Peligrosidad (P).",
    },
    {
        "id": "NSR10-J-J_2_4_3", "seccion": "J.2.4.3",
        "titulo": "J.2.4.3 — Construcciones sobre el techo: materiales incombustibles, excepciones astas/antenas/plataformas <20%",
        "texto": "J.2.4.3 — CONSTRUCCIONES SOBRE EL TECHO — Toda construcción sobre el techo de una edificación, debe hacerse con materiales incombustibles, a excepción de las astas para bandera, soportes para antenas y estructuras para el tendido de ropa, así como plataformas que no cubran más del 20% del área total del techo.",
    },
    {
        "id": "NSR10-J-J_2_4_4_y_tabla", "seccion": "J.2.4.4",
        "titulo": "J.2.4.4 — Hidrantes por área construida, Tabla J.2.4-1 completa (área/hidrante y caudal por tipo de edificación)",
        "texto": "J.2.4.4 — HIDRANTES — Debe instalarse, por lo menos, un hidrante para cada cantidad de área especificada en la tabla J.2.4-1. Cada hidrante debe tener suministro permanente de agua y debe tener, por lo menos, el caudal especificado en la tabla J.2.4-1. Para edificaciones no listadas en la tabla, debe proveerse con por lo menos un hidrante por cada 5 000 m² de área construida. Tabla J.2.4-1 — Área construida y caudal mínimo requerido por cada hidrante que debe instalarse (Edificación — Área/hidrante m² — Caudal/hidrante L/s): Edificios cuya altura de evacuación descendente sea más de 28 metros o ascendente de más de 6 metros — 500 — 32. Cines, teatros, auditorios y discotecas — 500 — 63. Recintos deportivos — 500 — 63. Locales comerciales — 1 000 — 63. Estacionamientos — 1 000 — 63. Hospitales — 500 — 63. Residencias — 5 000 — 32. Atención al público — 500 — 63. Educación — 1 000 — 63. Almacenamiento — 500 — 63.",
    },
    {
        "id": "NSR10-J-J_2_4_4_1", "seccion": "J.2.4.4.1",
        "titulo": "J.2.4.4.1 — Color del hidrante según caudal: rojo <=32 L/s, amarillo 32-63 L/s, verde >63 L/s",
        "texto": "J.2.4.4.1 — HIDRANTES - Color del Hidrante — La parte superior del hidrante debe pintarse de acuerdo con su caudal y siguiendo normas internacionales, tal como se establece a continuación: Rojo: Caudales hasta de 32 litros por cada segundo (L/s). Amarillo: Caudales entre 32 L/s y 63 L/s. Verde: Caudales superiores a 63 L/s.",
    },
    {
        "id": "NSR10-J-J_2_4_5", "seccion": "J.2.4.5",
        "titulo": "J.2.4.5 — Al menos un hidrante a no más de 100m de un acceso al edificio, demás repartidos y accesibles",
        "texto": "J.2.4.5 — Por lo menos un hidrante debe estar situado a no más de 100 m de distancia de un acceso al edificio. Los demás deberán estar razonablemente repartidos por el perímetro de la edificación y ser accesibles para los vehículos del servicio del cuerpo de bomberos.",
    },
    {
        "id": "NSR10-J-J_2_4_6", "seccion": "J.2.4.6",
        "titulo": "J.2.4.6 — Hidrantes de la red pública pueden contarse para cumplir J.2.4.4",
        "texto": "J.2.4.6 — Los hidrantes de la red pública pueden tenerse en cuenta para efectos del cumplimiento de lo especificado en J.2.4.4.",
    },
    {
        "id": "NSR10-J-J_2_4_7", "seccion": "J.2.4.7",
        "titulo": "J.2.4.7 — Edificios de más de 5 pisos: red contra incendio con válvula de retención, NFPA 14 y NTC 1669",
        "texto": "J.2.4.7 — Todo edificio de más de cinco (5) pisos deberá contar con la instalación de una red contra incendio, con válvula de retención, de uso exclusivo del cuerpo de bomberos, con por lo menos una salida por piso, de fácil acceso a la boca de entrada, para conexión de los carros bomba y en cada piso para la conexión de mangueras. Las características técnicas de esta red serán las especificadas por las Normas Técnicas NFPA 14 y NTC 1669.",
    },
    {
        "id": "NSR10-J-J_2_4_8", "seccion": "J.2.4.8",
        "titulo": "J.2.4.8 — Materiales de redes contra incendio: listados en Capítulo 2 NFPA 13, Tubería y Accesorios",
        "texto": "J.2.4.8 — Para las redes contra incendios, en todas las edificaciones que lo requieran, podrán utilizarse solamente los materiales listados para servicio contra incendio en el Capítulo 2, Componentes y Accesorios del Sistema, bajo el numeral sobre Tubería y Accesorios, de la norma técnica NFPA 13. Su uso queda condicionado a las limitaciones relacionadas con tipo de riesgo y tipo de protección requerida, además de todos los requisitos particulares de instalación.",
    },
    {
        "id": "NSR10-J-J_2_5_1_1", "seccion": "J.2.5.1.1",
        "titulo": "J.2.5.1.1 — Áreas >1000m² divididas por muros cortafuego (ladrillo macizo/concreto), espesores Tablas J.3.5-2/7/8",
        "texto": "J.2.5 — PREVENCION DE LA PROPAGACION DEL FUEGO EN EL INTERIOR. J.2.5.1 — REQUISITOS GENERALES — Los siguientes son los requisitos generales que deben cumplir las edificaciones para prevenir la propagación del fuego en su interior. J.2.5.1.1 — Toda área mayor de 1 000 m², debe dividirse en áreas menores por medio de muros cortafuego, hechos de ladrillos macizos o de concreto, con los espesores mínimos prescritos en las tablas J.3.5-2, J.3.5-7 y J.3.5-8. Se permite la utilización de materiales y espesores diferentes en la construcción de muros cortafuego, siempre y cuando se demuestre que presentan un comportamiento general equivalente al de los muros especificados en las tablas J.3.5-2, J.3.5-7 y J.3.5-8.",
    },
    {
        "id": "NSR10-J-J_2_5_1_2", "seccion": "J.2.5.1.2",
        "titulo": "J.2.5.1.2 — Áreas >1000m² no divisibles: rociadores y extinguidores según distancias K.3.6",
        "texto": "J.2.5.1.2 — Las áreas mayores de 1.000 m² que por su uso no puedan dividirse en la forma estipulada, deben equiparse con medios de extinción de fuego consistentes en rociadores y extinguidores. Estos últimos deben estar al alcance de los usuarios, dentro de las distancias de recorrido especificadas para las salidas en K.3.6.",
    },
    {
        "id": "NSR10-J-J_2_5_1_3", "seccion": "J.2.5.1.3",
        "titulo": "J.2.5.1.3 — Exención de muros cortafuego para recintos polideportivos/hipermercados/iglesias con condiciones (90% un piso, 75% fachada)",
        "texto": "J.2.5.1.3 — Se eximirán de cumplir con los requisitos del numeral J.2.5.1.1 los recintos polideportivos, hipermercados, pabellones para ferias y exposiciones, iglesias, terminales de transporte y otras edificaciones destinadas al acceso público, siempre y cuando por lo menos el 90% de su área construida, cualquiera que sea su magnitud, se desarrolle en una sola planta, que sus salidas comuniquen directamente con el exterior, que al menos el 75% de su perímetro sea fachada y que no exista sobre dicho recinto ninguna zona habitable.",
    },
    {
        "id": "NSR10-J-J_2_5_1_4", "seccion": "J.2.5.1.4",
        "titulo": "J.2.5.1.4 — Muros cortafuego no pueden atravesarse con conducciones que permitan paso del fuego/humo",
        "texto": "J.2.5.1.4 — Los muros cortafuego no podrán atravesarse con conducciones u otro elemento que permita el paso del fuego y del humo, ni con materiales que disminuyan su resistencia al fuego.",
    },
    {
        "id": "NSR10-J-J_2_5_1_5", "seccion": "J.2.5.1.5",
        "titulo": "J.2.5.1.5 — Aberturas en muros cortafuego solo para circulaciones horizontales con cierre hermético de 1 hora",
        "texto": "J.2.5.1.5 — Los muros cortafuego podrán tener aberturas solamente para dar continuidad a circulaciones horizontales, siempre y cuando se tengan un sistema de cierre hermético contra el paso de humo, que asegure como mínimo una resistencia contra fuego de una hora y con las características de apertura y cierre consignadas en J.2.5.1.9.",
    },
    {
        "id": "NSR10-J-J_2_5_1_6", "seccion": "J.2.5.1.6",
        "titulo": "J.2.5.1.6 — Muros cortafuego del último piso deben sobresalir 0.5m sobre la cubierta, salvo excepciones",
        "texto": "J.2.5.1.6 — Los muros cortafuego para el último piso deben sobresalir por lo menos 0.5 m por encima de la cubierta de techo más alta, a menos que el recinto almacene materiales no inflamables o que la cubierta de la edificación esté hecha y soportada con materiales no combustibles.",
    },
    {
        "id": "NSR10-J-J_2_5_1_7", "seccion": "J.2.5.1.7",
        "titulo": "J.2.5.1.7 — Edificios >3 pisos: núcleo de escaleras de evacuación continuo, ancho mínimo 1.2m (0.9m con excepción K.3.8.3.3)",
        "texto": "J.2.5.1.7 — Todo edificio de más de tres (3) pisos deberá tener por lo menos un núcleo de escaleras para evacuación vertical continuo hasta el nivel de evacuación a la calle, con una anchura mínima de 1.2 m y construidas con materiales que no tengan resistencia al fuego menores de una hora. Los muros que conforman los medios de evacuación deben cumplir con las especificaciones para muros cortafuegos contenidas en J.2.5.1.1. La continuidad del medio de evacuación vertical implica que no hay desplazamientos horizontales intermedios distintos que los descansos en las escaleras (Véase K.3.2 para definición de Medios de Evacuación). La anchura mínima se puede reducir a 0.90 m, si cumple los requisitos de K.3.8.3.3 carga de ocupación menor a 50 personas por piso. Los muros pueden diseñarse de acuerdo con la Norma NFPA 221, Norma para paredes a prueba de incendios.",
    },
    {
        "id": "NSR10-J-J_2_5_1_8", "seccion": "J.2.5.1.8",
        "titulo": "J.2.5.1.8 — Puertas de acceso/egreso: apertura manual fácil, cierre automático, resistencia al fuego 1 hora (NFPA 80)",
        "texto": "J.2.5.1.8 — Las puertas de acceso o egreso principales y las que dan a la salida, conformada por el núcleo de evacuación o la escalera en todos los pisos, deberán ser de apertura manual fácil, de cierre automático y tener una resistencia a la acción del fuego no inferior a una hora. Las puertas pueden diseñarse de acuerdo con la Norma NFPA 80, Norma para puertas y ventanas a prueba de incendios.",
    },
    {
        "id": "NSR10-J-J_2_5_1_9", "seccion": "J.2.5.1.9",
        "titulo": "J.2.5.1.9 — Sellos cortafuego en penetraciones de muros/pisos: normas ASTM E814, UL 1479, UL 2079, resistencia mínima 1 hora",
        "texto": "J.2.5.1.9 — Cualquier espacio entre particiones, muros, pisos, techos o escaleras, que permita el paso de llamas o gases de un ambiente a un piso a otro, tal como las penetraciones para cables, bandejas de cables, conductos para cables, tuberías, tubos, ventilaciones de combustión y de respiración, conductores eléctricos y elementos similares que atraviesan muros o pisos, o de un área encerrada a otra, debe rellenarse con materiales cortafuego que hayan sido aprobados para tal efecto mediante las normas internacionales ASTM E814 \"Método de ensayo normalizado para los ensayos de incendios de sellos cortafuego en perforaciones pasantes\", la UL 1479 \"Norma para ensayos de incendios de sellos cortafuego en perforaciones pasantes\", ASTM E814, \"Método de ensayo normalizado para los sistemas de juntas resistentes al fuego\", o la UL 2079 \"Norma para ensayos de resistencia al fuego de sistemas de juntas en edificios\" u otras normas equivalente, reconocidas internacionalmente. Los materiales utilizados deben tener una resistencia al fuego igual o superior a la del elemento estructural o no estructural en que quedarán embebidos, pero nunca menor a una (1) hora.",
    },
    {
        "id": "NSR10-J-J_2_5_1_10", "seccion": "J.2.5.1.10",
        "titulo": "J.2.5.1.10 — Ductos dentro de la edificación: salida vertical al exterior, distancias a madera, buzones/tolvas de basura",
        "texto": "J.2.5.1.10 — Los ductos que se instalen dentro de la edificación deben fabricarse y colocarse de manera que no se promueva la propagación del fuego, de acuerdo con los siguientes requisitos: (a) Todo ducto que conduzca humo o gases deberá salir verticalmente al exterior y sobrepasar el nivel de cubierta, en el punto de perforación, por lo menos 1,5 m. Estos ductos se construirán en toda su altura con elementos cuya resistencia mínima a la acción del fuego sea de una (1) hora. (b) No se permitirá la colocación de vigas o tirantes de madera a una distancia menor de 0,20 m de la superficie interior de los ductos que conduzcan humo o gases sujetos a altas temperaturas como buitrones con chimeneas, campanas extractoras o ductos que puedan conducir gases a más de 80 °C. En el espacio de separación deberá permitirse la circulación de aire. (c) Los buzones o tolvas, y sus ductos, para descarga de basuras, deberán fabricarse con materiales que tengan resistencia a la acción del fuego de mínimo una (1) hora. Además, dispondrán de ventilación adecuada en su parte superior, y de un sistema que permita la descarga de agua desde sus extremos superior e inferior, para poder utilizarse en casos de atascamiento de basuras o de conato de incendio, y que puedan activarse desde un lugar de fácil acceso ubicado en el primer piso.",
    },
    {
        "id": "NSR10-J-J_2_5_2_1", "seccion": "J.2.5.2.1",
        "titulo": "J.2.5.2.1 — Acabados interiores: prohibido producir sustancias tóxicas en concentración superior a papel/madera al arder",
        "texto": "J.2.5.2 — ACABADOS INTERIORES — Los materiales que se utilicen en acabados interiores, deben cumplir las reglamentaciones prescritas en este numeral. J.2.5.2.1 — Para los acabados interiores no deben emplearse materiales que al ser expuestos al fuego produzcan, por descomposición o combustión, sustancias tóxicas en concentraciones superiores a las provenientes del papel o la madera, bajo las mismas condiciones.",
    },
    {
        "id": "NSR10-J-J_2_5_2_2_y_tabla", "seccion": "J.2.5.2.2",
        "titulo": "J.2.5.2.2 — Clasificación de acabados interiores por propagación de llama, Tabla J.2.5-2 completa (4 clases, índice NTC 1691)",
        "texto": "J.2.5.2.2 — Los materiales para acabados interiores, deben clasificarse, con base en sus características de propagación de la llama, de acuerdo con la tabla J.2.5-2. Tabla J.2.5-2 — Clasificación del material según su característica de propagación de la llama (Clase — Índice de propagación de la llama): 1 — 0 a 25. 2 — 26 a 75. 3 — 76 a 225. 4 — Más de 225. Nota: Clasificación obtenida de acuerdo con la norma NTC 1691.",
    },
    {
        "id": "NSR10-J-J_2_5_2_3_y_tabla", "seccion": "J.2.5.2.3",
        "titulo": "J.2.5.2.3 — Índice de propagación de llama (ASTM E84/UL 723), Tabla J.2.5-3 completa (materiales por clase 1 a 4)",
        "texto": "J.2.5.2.3 — El índice de propagación de llama es una medida comparativa, expresada de manera adimensional, como una calificación visual de la propagación de la llama en el tiempo, para cada material ensayado de acuerdo con ASTM E 84. En la tabla J.2.5-3, se muestra una clasificación indicativa de distintos materiales utilizados para acabados interiores, en cuanto a su índice de propagación de llama. Alternativamente se puede utilizar la norma UL 723. Tabla J.2.5-3 — Clasificación de algunos materiales utilizados para acabados interiores según índice de propagación de la llama, por Clase: Clase 1 — Pañetes de cemento; cartón de fibro-cemento; fibro–asfalto; placas planas de fibrocemento; placas planas de fibrosilicato; ladrillo; baldosas de cerámica; lana de vidrio sin aglutinantes ni aditivos; vidrio; algunos azulejos antiacústicos. Clase 2 — Hoja de aluminio sobre respaldo apropiado; cartón de fibra o yeso con revestimiento de papel; madera tratada mediante impregnación; algunos pañetes antisonoros; algunos azulejos antiacústicos. Clase 3 — Madera de espesor nominal de 2,5 cm o más; planchas de fibra con revestimiento a prueba de fuego; azulejo antiacústicos, combustible, con revestimiento a prueba de fuego; cartón endurecido; algunos plásticos. Clase 4 — Papel asfáltico; tela; viruta; superficies cubiertas con aceite o parafina; papel; plásticos, sin grado que permita asignarlos a otras clases; algodón. Nota: Clasificación obtenida siguiendo procedimiento de la \"Prueba de Túnel\", Norma NTC 1691, en su versión más reciente.",
    },
    {
        "id": "NSR10-J-J_2_5_2_4", "seccion": "J.2.5.2.4",
        "titulo": "J.2.5.2.4 — Remisión a Tabla J.2.5-4: clasificación de acabado interior requerida según Grupo de Ocupación y ubicación",
        "texto": "J.2.5.2.4 — En la tabla J.2.5-4, se especifica la clasificación requerida para el material de acabado interior que debe utilizarse, de acuerdo con el Grupo de Ocupación en que se clasifique la edificación y con la ubicación del acabado.",
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")

    if IDS_OBSOLETOS:
        sb.table("nsr10_chunks").delete().in_("id", IDS_OBSOLETOS).execute()
        print(f"Borrados {len(IDS_OBSOLETOS)} chunks obsoletos (resumen sin tildes): {IDS_OBSOLETOS}")


if __name__ == "__main__":
    main()
