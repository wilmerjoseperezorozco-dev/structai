"""
NSR-10 Titulo K, Capitulo K.2 completo (K.2.1 a K.2.11) -- Clasificacion de
las edificaciones por grupos de ocupacion, en verbatim real.

Reemplaza el chunk unico NSR10-K-K_2_2_a_K_2_11_resumen (1751 caracteres,
un resumen condensado de 9 numerales + ~20 tablas, mismo patron ya
encontrado y corregido en F.3.5-F.3.11) por 11 chunks reales, uno por
numeral, extraidos leyendo visualmente el PDF oficial (Read con `pages`,
nunca el texto plano de Drive -- mismo metodo ya establecido en el
proyecto).

Fuente: NSR-10-1501-1570.pdf (Drive id 1AXhovLAquw_qFr0I4B7IiTGmuiIl24JP),
paginas internas K-3 a K-8 (paginas PDF 65-70), y NSR-10-1571-1625.pdf
(Drive id 1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z), paginas internas K-9 a K-12
(paginas PDF 1-4). Sin formulas matematicas en este capitulo -- solo
clasificacion narrativa + tablas de ejemplos, texto extraido con
confianza completa.

Uso: python _ingest_titulo_k_k2_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título K — Otros Requisitos Complementarios"

CHUNKS = [
    {
        "id": "NSR10-K-K_2_1_general",
        "seccion": "K.2.1 (General)",
        "titulo": "Alcance del Capítulo K.2 y Tabla K.2.1-1, grupos y subgrupos de ocupación completos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — CLASIFICACIÓN DE LAS EDIFICACIONES POR "
            "GRUPOS DE OCUPACIÓN. K.2.1 — GENERAL. K.2.1.1 — Este Capítulo establece y "
            "controla la clasificación de todas las edificaciones y espacios existentes, "
            "de acuerdo con su uso y ocupación y es aplicable a los Títulos K y J del "
            "presente Reglamento. Debe consultarse, además, el Capítulo A.2 para efectos "
            "de la clasificación por importancia en grupos de uso con respecto a la "
            "sismo resistencia de la edificación. K.2.1.2 — Toda edificación o espacio "
            "que se construya o altere debe clasificarse, para los propósitos de este "
            "Reglamento, en uno de los Grupos de Ocupación dados en la tabla K.2.1-1, de "
            "acuerdo con su ocupación principal o dominante.\n\n"
            "Tabla K.2.1-1 — Grupos y subgrupos de ocupación (Grupo/Subgrupo — "
            "Clasificación — Sección): "
            "A — ALMACENAMIENTO — K.2.2 (A-1 Riesgo moderado; A-2 Riesgo bajo). "
            "C — COMERCIAL — K.2.3 (C-1 Servicios; C-2 Bienes). "
            "E — ESPECIALES — K.2.4. "
            "F — FABRIL E INDUSTRIAL — K.2.5 (F-1 Riesgo moderado; F-2 Riesgo bajo). "
            "I — INSTITUCIONAL — K.2.6 (I-1 Reclusión; I-2 Salud o incapacidad; "
            "I-3 Educación; I-4 Seguridad pública; I-5 Servicio público). "
            "L — LUGARES DE REUNIÓN — K.2.7 (L-1 Deportivos; L-2 Culturales y teatros; "
            "L-3 Sociales y recreativos; L-4 Religiosos; L-5 De transporte). "
            "M — MIXTO Y OTROS — K.2.8. "
            "P — ALTA PELIGROSIDAD — K.2.9. "
            "R — RESIDENCIAL — K.2.10 (R-1 Unifamiliar y bifamiliar; R-2 Multifamiliar; "
            "R-3 Hoteles). "
            "T — TEMPORAL — K.2.11.\n\n"
            "K.2.1.3 — La tabla K.2-1 presenta una lista de grupos y subgrupos de "
            "ocupación destinada a la clasificación de edificaciones y espacios de "
            "acuerdo con las especificaciones de los numerales K.2.2 a K.2.11."
        ),
    },
    {
        "id": "NSR10-K-K_2_2_almacenamiento",
        "seccion": "K.2.2 (Grupo de Ocupación Almacenamiento — A)",
        "titulo": "Subgrupos A-1 (riesgo moderado) y A-2 (riesgo bajo) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.2 — GRUPO DE OCUPACIÓN ALMACENAMIENTO "
            "(A). K.2.2.1 — GENERAL — En el Grupo de Ocupación Almacenamiento (A) se "
            "clasifican las edificaciones o espacios utilizados como almacenamiento de "
            "mercancías, carga o bienes en general, a menos que se clasifiquen en el "
            "Grupo de Ocupación Alta Peligrosidad (P), numeral K.2.9. El Grupo de "
            "Ocupación Almacenamiento (A) está constituido por los Subgrupos de "
            "Ocupación Almacenamiento Riesgo Moderado (A-1) y Almacenamiento Riesgo "
            "Bajo (A-2).\n\n"
            "K.2.2.2 — SUBGRUPO DE OCUPACIÓN ALMACENAMIENTO DE RIESGO MODERADO (A-1) — "
            "En el Subgrupo de Ocupación Almacenamiento de Riesgo Moderado (A-1) se "
            "clasifican las edificaciones o espacios utilizados para almacenamiento de "
            "materiales que, siendo combustibles, arden con rapidez moderada y no "
            "producen gases venenosos ni explosivos. Tabla K.2.2-1 — Subgrupo de "
            "ocupación almacenamiento de riesgo moderado (A-1): Papel, Vestidos, "
            "Zapatos, Paja, Cuero, Cartón, Adhesivos, Cales, Muebles, Maderas, Linóleo, "
            "Azúcares, Seda, Tabaco, Cigarrillos, Granos, Cera, Pieles, Establos y "
            "galpones, Estacionamientos, Talleres mecánicos, Productos fotográficos, "
            "Otros similares.\n\n"
            "K.2.2.3 — SUBGRUPO DE OCUPACIÓN ALMACENAMIENTO DE RIESGO BAJO (A-2) — En "
            "el Subgrupo de Ocupación Almacenamiento de Riesgo Bajo (A-2) se clasifican "
            "las edificaciones o espacios utilizados para el almacenamiento de material "
            "incombustible o de combustión muy lenta. Tabla K.2.2-2 — Subgrupo de "
            "ocupación almacenamiento de riesgo bajo (A-2): Asbestos, Productos "
            "alimenticios, Vidrio, Metales, Porcelana, Talcos, Otros similares."
        ),
    },
    {
        "id": "NSR10-K-K_2_3_comercial",
        "seccion": "K.2.3 (Grupo de Ocupación Comercial — C)",
        "titulo": "Subgrupos C-1 (servicios) y C-2 (bienes y productos) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.3 — GRUPO DE OCUPACIÓN COMERCIAL (C). "
            "K.2.3.1 — GENERAL — En el Grupo de Ocupación Comercial (C) se clasifican "
            "las edificaciones o espacios destinados a la realización de transacciones, "
            "ofrecimiento de servicios profesionales, compra, venta y uso de mercancías, "
            "carga o bienes en general, excepto los incluidos en el Grupo de Ocupación "
            "Alta Peligrosidad (P), numeral K.2.9. El Grupo de Ocupación Comercial (C) "
            "está constituido por los Subgrupos de Ocupación Comercial, Servicios (C-1) "
            "y Comercial de Bienes y Productos (C-2).\n\n"
            "K.2.3.2 — SUBGRUPO DE OCUPACIÓN COMERCIAL, SERVICIOS (C-1) — En el "
            "Subgrupo de Ocupación Comercial, Servicios (C-1) se clasifican las "
            "edificaciones o espacios en donde se realizan transacciones y se ofrecen "
            "servicios profesionales o comerciales, que incidentalmente involucren el "
            "almacenamiento de pequeñas cantidades de bienes para el funcionamiento y "
            "oferta de dichos servicios. Tabla K.2.3-1 — Subgrupo de ocupación comercial "
            "servicios (C-1): Bancos, Consultorios, Salas de belleza y afines, "
            "Aseguradoras, Oficinas, Edificaciones administrativas, Otros similares.\n\n"
            "K.2.3.3 — SUBGRUPO DE OCUPACIÓN COMERCIAL DE BIENES Y PRODUCTOS (C-2) — En "
            "el Subgrupo de Ocupación Comercial de Bienes y Productos (C-2) se "
            "clasifican las edificaciones o espacios utilizados en la exhibición, venta "
            "y comercialización de bienes, productos y mercancías a los cuales tiene "
            "acceso el público comprador. La mercancía altamente combustible debe "
            "limitarse a cantidades pequeñas, de tal manera que la edificación no tenga "
            "necesariamente que cumplir con los requisitos para edificaciones del Grupo "
            "de Ocupación de Alta Peligrosidad (P), numeral K.2.9. Tabla K.2.3-2 — "
            "Subgrupo de ocupación comercial de bienes y productos (C-2): Almacenes, "
            "Mercados, Supermercados, Depósitos menores, Restaurantes, Centros "
            "comerciales, Panaderías, Farmacias, Bodegas, Centros de distribución al "
            "detal y por mayor."
        ),
    },
    {
        "id": "NSR10-K-K_2_4_especiales",
        "seccion": "K.2.4 (Grupo de Ocupación Especiales — E)",
        "titulo": "Definición del grupo Especiales y su tabla de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.4 — GRUPO DE OCUPACIÓN ESPECIALES (E). "
            "K.2.4.1 — GENERAL — En el Grupo de Ocupación, Especiales (E) se clasifican "
            "las edificaciones o espacios de construcción que no clasifiquen en ninguno "
            "de los otros Grupos de Ocupación específicos y que tengan características "
            "técnicas, constructivas o de uso de carácter especial. K.2.4.2 — LISTA DE "
            "OCUPACIONES ESPECIALES — En la tabla K.2.4-1 se presenta una lista "
            "indicativa de edificaciones o espacios que deben clasificarse en el Grupo "
            "de Ocupación Especiales (E). Esta debe incluir, además, todos aquellos "
            "tipos de edificaciones que se proyecten por primera vez y sobre las cuales "
            "no existan reglamentos aprobados. Tabla K.2.4-1 — Grupo de ocupación "
            "especiales (E): Piscinas, Parques de Diversión, Cementerios, Parqueaderos "
            "privados, Parqueaderos públicos, Talleres, Autocinemas, Unidades Móviles, "
            "Establecimientos de Lavado en seco, Helipuertos, Alojamientos y "
            "Tratamiento de Animales."
        ),
    },
    {
        "id": "NSR10-K-K_2_5_fabril",
        "seccion": "K.2.5 (Grupo de Ocupación Fabril e Industrial — F)",
        "titulo": "Subgrupos F-1 (riesgo moderado) y F-2 (riesgo bajo) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.5 — GRUPO DE OCUPACION FABRIL E "
            "INDUSTRIAL (F). K.2.5.1 — GENERAL — En el Grupo de Ocupación, Fabril e "
            "Industrial (F) se clasifican las edificaciones o espacios utilizadas en la "
            "explotación de materia prima, fabricación, ensamblaje, manufacturación, "
            "procesamiento o transformación de productos, materiales o energía; excepto "
            "cuando se trate de productos o materiales altamente combustibles, "
            "inflamables o explosivos, en cuyo caso deben clasificarse en el Grupo de "
            "Ocupación, de Alta Peligrosidad (P), numeral K.2.9. El Grupo de Ocupación "
            "Fabril e Industrial (F) está constituido por los Subgrupos de Ocupación "
            "Fabril e Industrial de Riesgo Moderado (F-1) y Fabril e Industrial de "
            "Riesgo Bajo (F-2).\n\n"
            "K.2.5.2 — SUBGRUPO DE OCUPACION FABRIL E INDUSTRIAL DE RIESGO MODERADO "
            "(F-1) — se clasifican las edificaciones o espacios donde los procesos de "
            "explotación, fabricación, ensamblaje, manufacturación o procesamiento "
            "representan riesgo moderado de incendio, debido a la naturaleza de tales "
            "operaciones y a los materiales involucrados. Tabla K.2.5-1 — Subgrupo de "
            "ocupación fabril e industrial de riesgo moderado (F-1): Plantas de "
            "asfalto, Industria farmacéutica, Lavanderías y tintorerías, Subestaciones "
            "eléctricas, Madera, Elementos fotográficos, Vidrio, Gráficas, Cueros, "
            "Papel, Tabaco, Plásticos y cauchos, Textil, Automotriz, Otros similares, "
            "Industria metal mecánica.\n\n"
            "K.2.5.3 — SUBGRUPO DE OCUPACION FABRIL E INDUSTRIAL DE RIESGO BAJO (F-2) — "
            "se clasifican las edificaciones o espacios donde los procesos de "
            "explotación, fabricación, ensamblaje, manufacturación o procesamiento, "
            "representan riesgos bajos de incendio debido a la naturaleza de tales "
            "operaciones y a los materiales involucrados. Tabla K.2.5-2 — Subgrupo de "
            "ocupación fabril e industrial riesgo bajo (F-2): Industrias alimenticias, "
            "Industria artesanal."
        ),
    },
    {
        "id": "NSR10-K-K_2_6_institucional",
        "seccion": "K.2.6 (Grupo de Ocupación Institucional — I)",
        "titulo": "Subgrupos I-1 a I-5 (reclusión, salud, educación, seguridad pública, servicio público) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.6 — GRUPO DE OCUPACION INSTITUCIONAL "
            "(I). K.2.6.1 — GENERAL — En el Grupo de Ocupación Institucional (I) se "
            "clasifican las edificaciones o espacios utilizados para la reclusión de "
            "personas que adolecen de limitaciones mentales o están sujetas a castigos "
            "penales o correccionales; en el tratamiento o cuidado de personas o en su "
            "reunión con propósitos educativos o de instrucción. De igual manera se "
            "clasifican dentro de este grupo las edificaciones y espacios "
            "indispensables en la atención de emergencias, preservación de la seguridad "
            "de personas y la prestación de servicios públicos y administrativos "
            "necesarios para el buen funcionamiento de las ciudades. El Grupo de "
            "Ocupación Institucional (I) está constituido por los Subgrupos de "
            "Ocupación Institucional de Reclusión (I-1), Institucional de Salud o "
            "Incapacidad (I-2), Institucional de Educación (I-3), Institucional de "
            "Seguridad Pública (I-4) e Institucional de Servicio Público (I-5).\n\n"
            "K.2.6.2 — SUBGRUPO DE OCUPACION INSTITUCIONAL DE RECLUSIÓN (I-1) — "
            "edificaciones o espacios empleados en la reclusión de personas con "
            "libertad restringida por razones penales, correccionales o de limitación "
            "mental. Tabla K.2.6-1: Prisiones, Reformatorios, Cárceles, Manicomios, "
            "Asilos, Otros similares.\n\n"
            "K.2.6.3 — SUBGRUPO DE OCUPACIÓN INSTITUCIONAL DE SALUD O INCAPACIDAD (I-2) "
            "— edificaciones o espacios empleados en el cuidado o tratamiento de "
            "personas con limitaciones físicas por edad avanzada o deficiencias de "
            "salud. Tabla K.2.6-2: Hospitales, Sanatorios, Clínicas, Centros de salud, "
            "Centros para discapacitados, Puestos de primeros auxilios, Orfanatos, "
            "Ancianatos, Guarderías, Dispensarios, Laboratorios clínicos, Hospicios, "
            "Otros similares.\n\n"
            "K.2.6.4 — SUBGRUPO DE OCUPACIÓN INSTITUCIONAL DE EDUCACIÓN (I-3) — "
            "edificaciones o espacios empleados para la reunión de personas con "
            "propósitos educativos y de instrucción. Tabla K.2.6-3: Universidades, "
            "Colegios, Escuelas, Centros de educación, Academias, Jardines infantiles, "
            "Otras instituciones docentes.\n\n"
            "K.2.6.5 — SUBGRUPO DE OCUPACIÓN INSTITUCIONAL DE SEGURIDAD PÚBLICA (I-4) — "
            "edificaciones o espacios indispensables para atender emergencias y "
            "preservar el orden público y la seguridad de las personas. Tabla K.2.6-4: "
            "Estaciones de policía, Estaciones de bomberos, Estaciones de defensa "
            "civil, Instituciones militares, Otros similares.\n\n"
            "K.2.6.6 — SUBGRUPO DE OCUPACIÓN INSTITUCIONAL DE SERVICIO PÚBLICO (I-5) — "
            "edificaciones o espacios destinados a funciones administrativas y "
            "prestación de servicios públicos necesarios para el buen funcionamiento de "
            "las ciudades. Tabla K.2.6-5: Centros de comunicación, Centros "
            "administrativos municipales, distritales y gubernamentales, Centros "
            "administrativos de servicios públicos, Juzgados, Otros similares."
        ),
    },
    {
        "id": "NSR10-K-K_2_7_lugares_reunion",
        "seccion": "K.2.7 (Grupo de Ocupación Lugares de Reunión — L)",
        "titulo": "Subgrupos L-1 a L-5 (deportivos, culturales, sociales/recreativos, religiosos, transporte) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.7 — GRUPO DE OCUPACIÓN LUGARES DE "
            "REUNION (L). K.2.7.1 — GENERAL — En el Grupo de Ocupación Lugares de "
            "Reunión (L) se clasifican las edificaciones o espacios en donde se reúne o "
            "agrupa la gente con fines religiosos, deportivos, políticos, culturales, "
            "sociales, recreativos o de transporte y que, en general, disponen de "
            "medios comunes de salida o de entrada. Se excluyen de este grupo las "
            "edificaciones o espacios del grupo de ocupación Institucional (I). El "
            "Grupo de Ocupación Lugares de Reunión (L) está constituido por los "
            "Subgrupos de Ocupación Lugares de Reunión Deportivos (L-1), Lugares de "
            "Reunión Culturales (L-2), Lugares de Reunión Sociales y Recreativos (L-3), "
            "Lugares de Reunión Religiosos (L-4) y Lugares de Reunión de Transporte "
            "(L-5).\n\n"
            "K.2.7.2 — SUBGRUPO DE OCUPACIÓN LUGARES DE REUNION DEPORTIVOS (L-1) — "
            "edificaciones o espacios utilizados para la realización de cualquier tipo "
            "de deporte, y en general, donde se reúnen o agrupan personas para "
            "presenciar o realizar algún evento deportivo. Tabla K.2.7-1: Estadios, "
            "Gimnasios, Autódromos, Velódromos, Piscinas colectivas, Clubes deportivos, "
            "Carpas y espacios abiertos, Plazas de toros, Hipódromos, Boleras, "
            "Coliseos, Pistas, Polígonos, Otros similares.\n\n"
            "K.2.7.3 — SUBGRUPO DE OCUPACIÓN LUGARES DE REUNION CULTURALES (L-2) — "
            "edificaciones o espacios utilizados para la realización o presentación de "
            "eventos culturales o políticos, y en general, donde se reúnen o agrupan "
            "personas con fines culturales, y existen instalaciones escénicas tales "
            "como proscenios o tablados, cortinas, iluminación especial, cuartos de "
            "proyección y de artistas, dispositivos mecánicos, silletería fija u otros "
            "accesorios o equipos de teatro. Tabla K.2.7-2: Auditorios, Salones de "
            "exhibición, Salones de convención, Salas de cine, Salas de concierto, "
            "Carpas y espacios abiertos, Salas de teatro, Teatros al aire libre, "
            "Cinematecas, Planetarios, Teatros.\n\n"
            "K.2.7.4 — SUBGRUPO DE OCUPACIÓN LUGARES DE REUNION SOCIALES Y RECREATIVOS "
            "(L-3) — edificaciones o espacios en los cuales se reúnen o agrupan "
            "personas para fines de diversión y sociales, para el consumo de comidas o "
            "bebidas, y en general, para la realización de cualquier tipo de actividad "
            "social o recreativa que no requiera la presencia de instalaciones para "
            "representación escénica ni de silletería fija. Tabla K.2.7-3: Clubes "
            "sociales, Clubes nocturnos, Salones de baile, Salones de juego (cartas, "
            "ajedrez, billares, bingo, casinos, etc.), Discotecas, Centros de "
            "recreación, Tabernas, Vestíbulos y salones de reunión de hoteles, "
            "Bibliotecas, salas de lectura, galerías de arte, museos, Otros similares.\n\n"
            "K.2.7.5 — SUBGRUPO DE OCUPACIÓN LUGARES DE REUNIÓN RELIGIOSOS (L-4) — "
            "edificaciones o espacios en los cuales las personas se reúnen o agrupan "
            "con fines religiosos. Tabla K.2.7-4: Iglesias, Capillas, Salones de Culto, "
            "Salones para Agremiaciones Religiosas, Otros similares.\n\n"
            "K.2.7.6 — SUBGRUPO DE OCUPACIÓN LUGARES DE REUNION DE TRANSPORTE (L-5) — "
            "edificaciones o espacios en los cuales las personas se reúnen o agrupan "
            "con el propósito de disponer de un sitio fácil en donde puedan esperar la "
            "llegada y salida de cualquier medio de transporte de pasajeros y de carga. "
            "Tabla K.2.7-5: Terminales de pasajeros, Terminales de metro, Salas de "
            "espera para pasajeros, Terminales de carga, Estaciones."
        ),
    },
    {
        "id": "NSR10-K-K_2_8_mixto",
        "seccion": "K.2.8 (Grupo de Ocupación Mixto y Otros — M)",
        "titulo": "Definición del grupo Mixto y las dos reglas para edificaciones con dos o más ocupaciones.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.8 — GRUPO DE OCUPACION MIXTO Y OTROS "
            "(M). K.2.8.1 — GENERAL — En el Grupo de Ocupación Mixto y Otros (M) se "
            "clasifican las edificaciones o espacios que por tener más de un tipo de "
            "ocupación no clasifican en ninguno de los grupos específicos de este "
            "Capítulo o cuando su ubicación es incierta. Las edificaciones o espacios "
            "correspondientes deben incluirse en el Grupo de Ocupación que en forma más "
            "aproximada represente los riesgos debidos a su ocupación y seguridad.\n\n"
            "K.2.8.2 — DOS O MÁS OCUPACIONES — Cuando una edificación esté destinada a "
            "dos o más ocupaciones es preciso proceder según lo siguiente: (a) Aplicando "
            "las disposiciones de este Capítulo en cada una de las partes de la "
            "edificación según el grupo de ocupación particular en que se clasifica, y "
            "en el caso que haya conflicto de disposiciones, extendiendo a toda la "
            "edificación las que proporcionen mayor seguridad al público. (b) "
            "Independizando completamente las áreas de ocupaciones mixtas mediante "
            "construcciones tales como muros, pisos y cielos rasos, y aplicando en cada "
            "zona, con independencia de las demás, las disposiciones correspondientes a "
            "su grupo de ocupación."
        ),
    },
    {
        "id": "NSR10-K-K_2_9_alta_peligrosidad",
        "seccion": "K.2.9 (Grupo de Ocupación Alta Peligrosidad — P)",
        "titulo": "Definición del grupo Alta Peligrosidad y su tabla de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.9 — GRUPO DE OCUPACIÓN ALTA "
            "PELIGROSIDAD (P). K.2.9.1 — GENERAL — En el Grupo de Ocupación Alta "
            "Peligrosidad (P) se clasifican las edificaciones o espacios empleados en "
            "el almacenamiento, producción, procesamiento, compra, venta o uso de "
            "materiales o productos altamente inflamables o combustibles o "
            "potencialmente explosivos, propensos a incendiarse con extrema rapidez o a "
            "producir gases o vapores irritantes, venenosos o explosivos. Tabla K.2.9-1 "
            "— Grupo de ocupación alta peligrosidad (P): Productos combustibles, "
            "Productos inflamables, Productos explosivos, Productos corrosivos, "
            "Productos tóxicos, Industrias de armas y municiones, Productos químicos "
            "tóxicos, Destilerías, Industrias de pinturas y esmaltes, Industrias de "
            "plásticos, Álcalis, Ácidos, Gas acetileno, Productos piroxílicos, "
            "Estaciones de gasolina, Depósitos de algodón, Kerosene, Expendios de "
            "combustibles, Explosivos, Ropa sintética, Polvorerías, Cerillas, "
            "Procesadoras de papel, Expendios de Cocinol, Aceites."
        ),
    },
    {
        "id": "NSR10-K-K_2_10_residencial",
        "seccion": "K.2.10 (Grupo de Ocupación Residencial — R)",
        "titulo": "Subgrupos R-1 (unifamiliar/bifamiliar), R-2 (multifamiliar) y R-3 (hoteles) con sus tablas de ejemplos.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.10 — GRUPO DE OCUPACIÓN RESIDENCIAL "
            "(R). K.2.10.1 — GENERAL — En el Grupo de Ocupación Residencial (R) se "
            "clasifican las edificaciones o espacios empleados como vivienda familiar o "
            "de grupos de personas o como dormitorios, con o sin instalaciones de "
            "alimentación. Se excluyen de este grupo las edificaciones o espacios de "
            "ocupación Institucional (I). El Grupo de Ocupación Residencial (R) está "
            "constituido por los Subgrupos de Ocupación Residencial Unifamiliar y "
            "Bifamiliar (R-1), Residencial Multifamiliar (R-2) y Residencial Hoteles "
            "(R-3).\n\n"
            "K.2.10.2 — SUBGRUPO DE OCUPACIÓN RESIDENCIAL UNIFAMILIAR Y BIFAMILIAR "
            "(R-1) — edificaciones o espacios empleados principalmente como vivienda o "
            "dormitorio de una o dos familias, o de menos de 20 personas. Tabla "
            "K.2.10-1: Casas, Residencias unifamiliares, Residencias bifamiliares.\n\n"
            "K.2.10.3 — SUBGRUPO DE OCUPACIÓN RESIDENCIAL MULTIFAMILIAR (R-2) — en el "
            "Subgrupo de Ocupación Residencial Multifamiliar (R-2) figuran las "
            "edificaciones o espacios empleados principalmente como vivienda, o como "
            "dormitorio de tres o más familias, o de más de 20 personas. Tabla "
            "K.2.10-2: Edificios de apartamentos, Dormitorios universitarios, "
            "Monasterios y afines, Multifamiliares, Internados.\n\n"
            "K.2.10.4 — SUBGRUPO DE OCUPACIÓN RESIDENCIAL HOTELES (R-3) — en el "
            "Subgrupo de Ocupación Residencial Hoteles (R-3) se clasifican las "
            "edificaciones o espacios, provistas o no de servicios de alimentación, "
            "que sirven para el alojamiento de más de 20 personas durante períodos "
            "cortos de tiempo. Tabla K.2.10-3: Hoteles, Pensiones, Apartahoteles, "
            "Moteles, Hospederías."
        ),
    },
    {
        "id": "NSR10-K-K_2_11_temporal",
        "seccion": "K.2.11 (Grupo de Ocupación Temporal y Misceláneo — T)",
        "titulo": "Definición del grupo Temporal y Misceláneo, cierre del Capítulo K.2.",
        "texto": (
            "NSR-10 Título K, Capítulo K.2 — K.2.11 — GRUPO DE OCUPACIÓN TEMPORAL Y "
            "MISCELANEO (T). En el Grupo de Ocupación Temporal y Misceláneo (T) se "
            "clasifican las edificaciones o espacios que tienen ocupación de carácter "
            "temporal o cuyo tipo de ocupación varía con el tiempo. Las edificaciones "
            "del Grupo de Ocupación Temporal y Misceláneo (T) deben construirse, "
            "equiparse y conservarse de modo que cumplan los requisitos más estrictos "
            "de este Reglamento, de acuerdo con su ocupación específica."
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

    print("\nBorrando el chunk resumen viejo (NSR10-K-K_2_2_a_K_2_11_resumen)...")
    sb.table("nsr10_chunks").delete().eq("id", "NSR10-K-K_2_2_a_K_2_11_resumen").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de K.2 cargados. Capítulo K.2 completo (K.2.1-K.2.11).")


if __name__ == "__main__":
    main()
