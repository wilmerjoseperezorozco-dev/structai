"""
Ingesta verbatim de Título B, Capítulo B.4 (Cargas vivas) -- NSR-10.
Fase 3 del plan de cierre del Título B (2026-09-23), auditoría real de
numerales confirmó B.4 en 6/25 (faltan 19).

**Hallazgo real**: los chunks ya cargados para B.4.1-B.4.2 y
B.4.4-B.4.5 (`NSR10-B-B_4_1_a_B_4_2_r*`, `NSR10-B-B_4_4_a_B_4_5_r*`)
NO son verbatim -- son texto condensado en viñetas cortas, mismo
patrón "resumen disfrazado de completo" visto en A.3/A.9/A.10.
B.4.3 (Carga parcial), B.4.6 (Puente grúas), B.4.7 (Efectos
dinámicos) y B.4.8 (Cargas de empozamiento de agua y de granizo)
estaban completamente ausentes. Se borran los condensados y se
transcribe el capítulo completo.

Fuente: NSR-10-234-237.pdf completo, páginas PDF 1-4 (B-15 a B-18,
capítulo completo). Leídas visualmente con Read pages= sobre el PDF
nativo -- nunca extracción mecánica (pypdf).

Uso: python _ingest_titulo_b_b4_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

IDS_A_BORRAR_CONDENSADOS = (
    [f"NSR10-B-B_4_1_a_B_4_2_r{i}" for i in range(1, 6)]
    + [f"NSR10-B-B_4_4_a_B_4_5_r{i}" for i in range(1, 5)]
)

CHUNKS = [
    {
        "id": "NSR10-B-B_4_1_definicion",
        "seccion": "B.4.1 — Definición de carga viva",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "CAPÍTULO B.4 — CARGAS VIVAS\n\n"
            "B.4.1 — DEFINICIÓN\n\n"
            "B.4.1.1 — Las cargas vivas son aquellas cargas producidas "
            "por el uso y ocupación de la edificación y no deben "
            "incluir cargas ambientales tales como viento y sismo.\n\n"
            "B.4.1.2 — Las cargas vivas en las cubiertas son aquellas "
            "causadas por:\n"
            "(a) Los materiales, equipos y trabajadores utilizados en "
            "el mantenimiento de la cubierta y\n"
            "(b) Las causadas por objetos móviles, tales como materas "
            "u otros objetos decorativos, y por las personas que "
            "tengan acceso a ellas."
        ),
    },
    {
        "id": "NSR10-B-B_4_2_1_cargas_vivas_requeridas_tabla_1",
        "seccion": "B.4.2.1 — Cargas vivas uniformemente repartidas requeridas (Tabla B.4.2.1-1, primera mitad)",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.2 — CARGAS VIVAS UNIFORMEMENTE REPARTIDAS\n\n"
            "B.4.2.1 — CARGAS VIVAS REQUERIDAS — Las cargas vivas que "
            "se utilicen en el diseño de la estructura deben ser las "
            "máximas cargas que se espera ocurran en la edificación "
            "debido al uso que ésta va a tener. En ningún caso estas "
            "cargas vivas pueden ser menores que las cargas vivas "
            "mínimas que se dan en las tablas B.4.2.1-1 y B.4.2.1-2.\n\n"
            "Tabla B.4.2.1-1 — Cargas vivas mínimas uniformemente "
            "distribuidas (Ocupación o uso | carga uniforme kN/m² | "
            "kgf/m², por m² de área en planta):\n\n"
            "Reunión — Balcones: 5.0 | 500.\n"
            "Reunión — Corredores y escaleras: 5.0 | 500.\n"
            "Reunión — Silletería fija (fijada al piso): 3.0 | 300.\n"
            "Reunión — Gimnasios: 5.0 | 500.\n"
            "Reunión — Vestíbulos: 5.0 | 500.\n"
            "Reunión — Silletería móvil: 5.0 | 500.\n"
            "Reunión — Áreas recreativas: 5.0 | 500.\n"
            "Reunión — Plataformas: 5.0 | 500.\n"
            "Reunión — Escenarios: 7.5 | 750.\n"
            "Oficinas — Corredores y escaleras: 3.0 | 300.\n"
            "Oficinas — Oficinas: 2.0 | 200.\n"
            "Oficinas — Restaurantes: 5.0 | 500.\n"
            "Educativos — Salones de clase: 2.0 | 200.\n"
            "Educativos — Corredores y escaleras: 5.0 | 500.\n"
            "Educativos — Bibliotecas, salones de lectura: 2.0 | 200.\n"
            "Educativos — Bibliotecas, estanterías: 7.0 | 700.\n"
            "Fábricas — Industrias livianas: 5.0 | 500.\n"
            "Fábricas — Industrias pesadas: 10.0 | 1000.\n"
            "Institucional — Cuartos de cirugía, laboratorios: 4.0 | "
            "400.\n"
            "Institucional — Cuartos privados: 2.0 | 200.\n"
            "Institucional — Corredores y escaleras: 5.0 | 500.\n"
            "Comercio — Minorista: 5.0 | 500.\n"
            "Comercio — Mayorista: 6.0 | 600.\n"
            "Residencial — Balcones: 5.0 | 500.\n"
            "Residencial — Cuartos privados y sus corredores: 1.8 | "
            "180.\n"
            "Residencial — Escaleras: 3.0 | 300.\n"
            "Almacenamiento — Liviano: 6.0 | 600.\n"
            "Almacenamiento — Pesado: 12.0 | 1200.\n"
            "Garajes — Garajes para automóviles de pasajeros: 2.5 | "
            "250.\n"
            "Garajes — Garajes para vehículos de carga de hasta 2.000 "
            "kg de capacidad: 5.0 | 500.\n"
            "Coliseos y Estadios — Graderías: 5.0 | 500.\n"
            "Coliseos y Estadios — Escaleras: 5.0 | 500."
        ),
    },
    {
        "id": "NSR10-B-B_4_2_1_tabla_2_cubiertas",
        "seccion": "B.4.2.1 — Tabla B.4.2.1-2: cargas vivas mínimas en cubiertas",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "Tabla B.4.2.1-2 — Cargas vivas mínimas en cubiertas (Tipo "
            "de cubierta | carga uniforme kN/m² | kgf/m², por m² de "
            "área en planta):\n\n"
            "Cubiertas, Azoteas y Terrazas: la misma del resto de la "
            "edificación (Nota-1).\n"
            "Cubiertas usadas para jardines de cubierta o para "
            "reuniones: 5.00 | 500.\n"
            "Cubiertas inclinadas con más de 15° de pendiente en "
            "estructura metálica o de madera con imposibilidad física "
            "de verse sometidas a cargas superiores a la aquí "
            "estipulada: 0.35 | 35.\n"
            "Cubiertas inclinadas con pendiente de 15° o menos en "
            "estructura metálica o de madera con imposibilidad física "
            "de verse sometidas a cargas superiores a la aquí "
            "estipulada: 0.50 | 50.\n\n"
            "Nota-1 — La carga viva de la cubierta no debe ser menor "
            "que el máximo valor de las cargas vivas usadas en el "
            "resto de la edificación, y cuando ésta tenga uso mixto, "
            "tal carga debe ser la mayor de las cargas vivas "
            "correspondientes a los diferentes usos."
        ),
    },
    {
        "id": "NSR10-B-B_4_2_2_empuje_pasamanos_antepechos",
        "seccion": "B.4.2.2 — Empuje en pasamanos y antepechos (barandas, barreras para vehículos)",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.2.2 — EMPUJE EN PASAMANOS Y ANTEPECHOS — Las "
            "barandas, pasamanos de escaleras y balcones, y barras "
            "auxiliares tanto exteriores como interiores, y los "
            "antepechos deben diseñarse para que resistan una fuerza "
            "horizontal de 1.00 kN/m (100 kgf/m) aplicada en la parte "
            "superior de la baranda, pasamanos o antepecho y deben "
            "ser capaces de transferir esta carga a través de los "
            "soportes a la estructura. Para viviendas unifamiliares, "
            "la carga mínima es de 0.4 kN/m (40 kgf/m). En estadios y "
            "coliseos esa carga mínima horizontal de barandas y "
            "antepechos no será menor de 2.5 kN/m (250 kgf/m). En "
            "estos y otros escenarios públicos las barandas deberán "
            "ser sometidas a pruebas de carga, las cuales deben ser "
            "dirigidas y documentadas por el Supervisor Técnico antes "
            "de ser puestas en servicio.\n\n"
            "Las barandas intermedias (todas excepto los pasamanos) y "
            "paneles de relleno se deben diseñar para soportar una "
            "carga normal aplicada horizontalmente de 0.25 kN (25 "
            "kgf) sobre un área que no exceda 0.3 m de lado, "
            "incluyendo aberturas y espacios entre barandas. No es "
            "necesario superponer las acciones debidas a estas cargas "
            "con aquellas de cualquiera de los párrafos "
            "precedentes.\n\n"
            "Los sistemas de barreras para vehículos, en el caso de "
            "automóviles de pasajeros, se deben diseñar para resistir "
            "una única carga de 30 kN (3000 kgf) aplicada "
            "horizontalmente en cualquier dirección al sistema de "
            "barreras, y debe tener anclajes o uniones capaces de "
            "transferir esta carga a la estructura. Para el diseño "
            "del sistema, se debe suponer que la carga va a actuar a "
            "una altura mínima de 0.5 m por encima de la superficie "
            "del piso o rampa sobre un área que no exceda 0.3 m de "
            "lado, y no es necesario suponer que actuará "
            "conjuntamente con cualquier carga para pasamanos o "
            "sistemas de protección especificada en los párrafos "
            "precedentes. Las cargas indicadas no incluyen sistemas "
            "de barreras en garajes para vehículos de transporte "
            "público y camiones; en estos casos se deben realizar los "
            "análisis apropiados que contemplen estas situaciones."
        ),
    },
    {
        "id": "NSR10-B-B_4_3_carga_parcial",
        "seccion": "B.4.3 — Carga parcial",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.3 — CARGA PARCIAL — Cuando la luz de un elemento "
            "esté cargada parcialmente con la carga viva de diseño "
            "produciendo un efecto más desfavorable que cuando está "
            "cargada en la totalidad de la luz, este efecto debe ser "
            "tenido en cuenta en el diseño."
        ),
    },
    {
        "id": "NSR10-B-B_4_4_impacto",
        "seccion": "B.4.4 — Impacto (porcentajes de incremento de carga viva)",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.4 — IMPACTO — Cuando la estructura quede sometida a "
            "carga viva generadora de impacto, la carga viva debe "
            "incrementarse, para efectos de diseño, por los "
            "siguientes porcentajes:\n\n"
            "(a) Soportes de Elevadores y Ascensores: 100%\n"
            "(b) Vigas de puentes grúas con cabina de operación y sus "
            "conexiones: 25%\n"
            "(c) Vigas de puentes grúas operados por control remoto y "
            "sus conexiones: 10%\n"
            "(d) Apoyos de maquinaria liviana, movida mediante motor "
            "eléctrico o por un eje: 20%\n"
            "(e) Apoyos de maquinaria de émbolo o movida por motor a "
            "pistón, no menos de: 50%\n"
            "(f) Tensores que sirvan de apoyo a pisos o balcones "
            "suspendidos y escaleras: 33%"
        ),
    },
    {
        "id": "NSR10-B-B_4_5_reduccion_carga_viva",
        "seccion": "B.4.5 — Reducción de la carga viva (por área aferente, ecuación B.4.5-1, y por número de pisos)",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.5 — REDUCCIÓN DE LA CARGA VIVA\n\n"
            "B.4.5.1 — REDUCCIÓN DE LA CARGA VIVA POR ÁREA AFERENTE — "
            "Cuando el área de influencia del elemento estructural "
            "sea mayor o igual a 35 m² y la carga viva sea superior a "
            "1.80 kN/m² (180 kgf/m²) e inferior a 3.00 kN/m² (300 "
            "kgf/m²), la carga viva puede reducirse utilizando la "
            "ecuación B.4.5-1:\n\n"
            "L = L0(0.25 + 4.6/√Ai)       (B.4.5-1)\n\n"
            "Donde:\n"
            "L = carga viva reducida, en kN/m²\n"
            "L0 = carga viva sin reducir, en kN/m²\n"
            "Ai = área de influencia del elemento en m²\n\n"
            "B.4.5.1.1 — La carga viva reducida no puede ser menor "
            "del 50% de L0 en elementos que soporten un piso ni del "
            "40% de L0 en dos o más pisos.\n\n"
            "B.4.5.1.2 — El área de influencia es el área de los "
            "paneles adyacentes al elemento considerado, en tal forma "
            "que para columnas y vigas equivale al área de los "
            "paneles de placa que tocan el elemento, así:\n\n"
            "vigas centrales: Ai = área de dos paneles\n"
            "vigas de borde: Ai = área de un panel\n"
            "columnas centrales: Ai = área de cuatro paneles\n"
            "columnas de borde: Ai = área de dos paneles\n"
            "columnas de esquina: Ai = área de un panel\n\n"
            "Para elementos que soporten más de un piso deben "
            "sumarse las áreas de influencia de los diferentes "
            "pisos\n\n"
            "B.4.5.2 — REDUCCIÓN POR NÚMERO DE PISOS — "
            "Alternativamente a lo estipulado en el numeral anterior "
            "en edificios de cinco pisos o más la carga viva para "
            "efectos del diseño de las columnas y la cimentación "
            "puede tomarse como la suma de las cargas vivas de cada "
            "piso multiplicadas por el coeficiente r correspondiente "
            "a ese piso:\n\n"
            "r = 1.0       para i = n a i = n-4 (cinco pisos "
            "superiores)\n"
            "r = 1.0 + 0.10(i-n+4)       para i = n-5 a i = n-8\n"
            "r = 0.5       para i = n-9 en adelante\n\n"
            "Donde:\n"
            "n = número de pisos del edificio\n"
            "i = número del piso donde se aplica el coeficiente r"
        ),
    },
    {
        "id": "NSR10-B-B_4_6_puente_gruas",
        "seccion": "B.4.6 — Puente grúas",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.6 — PUENTE GRÚAS — En el diseño de las vigas "
            "carrilera de los puente grúas debe tenerse en cuenta una "
            "fuerza horizontal equivalente a por lo menos el 20% de "
            "la suma de los pesos de la grúa y la carga levantada. En "
            "la suma no entra el peso de las partes estacionarias del "
            "puente grúa. Esta fuerza debe suponerse colocada en la "
            "parte superior de los rieles, normalmente a los mismos y "
            "debe distribuirse entre las vigas teniendo en cuenta la "
            "rigidez lateral de la estructura que soporta los rieles. "
            "Además debe tenerse en cuenta una fuerza horizontal "
            "longitudinal, aplicada al tope del riel, igual al 10% de "
            "las cargas máximas de rueda de la grúa."
        ),
    },
    {
        "id": "NSR10-B-B_4_7_efectos_dinamicos",
        "seccion": "B.4.7 — Efectos dinámicos",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.7 — EFECTOS DINÁMICOS — Las edificaciones expuestas "
            "a excitaciones dinámicas producidas por el público tales "
            "como: estadios, coliseos, teatros, gimnasios, pistas de "
            "baile, centros de reunión o similares, deben ser "
            "diseñadas de tal manera que tengan frecuencias naturales "
            "verticales iguales o superiores a 5 Hz (períodos "
            "naturales verticales menores de 0.2 s)."
        ),
    },
    {
        "id": "NSR10-B-B_4_8_1_a_8_2_empozamiento_agua",
        "seccion": "B.4.8.1 y B.4.8.2 — Cargas de empozamiento de agua y de granizo: generalidades y carga por empozamiento de agua",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.8 — CARGAS EMPOZAMIENTO DE AGUA Y DE GRANIZO\n\n"
            "B.4.8.1 — GENERALIDADES — En el diseño estructural de "
            "cubiertas se deben considerar los efectos de "
            "empozamiento de agua y de granizo. El empozamiento de "
            "agua se produce por obstrucción de los sistemas de "
            "drenaje de la cubierta, el cual puede ocurrir por "
            "residuos, hojas de árboles, u otras fuentes de "
            "obstrucción. La determinación de las cargas por "
            "empozamiento de agua y granizo se realiza de la "
            "siguiente manera:\n\n"
            "(a) Toda cubierta debe disponer de sistema auxiliar de "
            "evacuación del exceso de agua cuando se presenta una "
            "obstrucción de las bajantes normales. Este sistema puede "
            "consistir en gárgolas, rebosaderos u otros implementos "
            "que eviten la acumulación de agua y la evacuen de forma "
            "confiable ante la obstrucción de las bajantes del "
            "sistema de drenaje.\n"
            "(b) La carga de empozamiento de agua, Le, se determina "
            "con base en el volumen de agua que es posible contener "
            "hasta que se alcance el nivel de los elementos del "
            "sistema auxiliar de evacuación del exceso de agua, como "
            "se indica en B.4.8.2.\n\n"
            "B.4.8.2 — CARGA POR EMPOZAMIENTO DE AGUA\n\n"
            "B.4.8.2.1 — El proyecto hidráulico de la edificación "
            "debe incluir el diseño del sistema de drenaje de la "
            "cubierta y del sistema auxiliar de evacuación del "
            "exceso de agua y definirá el volumen de agua que pueda "
            "acumularse antes de que el sistema auxiliar de drenaje "
            "del exceso opere. Es responsabilidad del constructor que "
            "suscribe la licencia de construcción aprobar el proyecto "
            "hidráulico y asegurarse de que los sistemas de drenaje "
            "normal y auxiliar sean apropiados y de suministrar la "
            "información acerca del volumen de agua que pueda "
            "acumularse al diseñador estructural.\n\n"
            "B.4.8.2.2 — Con base en la información suministrada por "
            "el constructor el diseñador estructural determinará las "
            "cargas causadas por el volumen de agua que pueda "
            "acumularse antes de que el sistema auxiliar de drenaje "
            "del exceso opere y su distribución a los elementos "
            "estructurales de soporte de la cubierta realizando su "
            "diseño de tal manera que sean capaces de resistir este "
            "peso sin fallar.\n\n"
            "B.4.8.2.3 — Para cubiertas en estructura metálica, la "
            "revisión del empozamiento debe tener adicionalmente en "
            "cuenta lo indicado en F.2.2.3.9."
        ),
    },
    {
        "id": "NSR10-B-B_4_8_3_carga_granizo",
        "seccion": "B.4.8.3 — Carga de granizo",
        "titulo": "NSR-10 Título B — Capítulo B.4 — Cargas vivas",
        "texto": (
            "B.4.8.3 — CARGA DE GRANIZO\n\n"
            "B.4.8.3.1 — Las cargas de granizo, G, deben tenerse en "
            "cuenta en las regiones del país con más de 2.000 metros "
            "de altura sobre el nivel del mar o en lugares de menor "
            "altura donde la autoridad municipal o distrital así lo "
            "exija.\n\n"
            "B.4.8.3.2 — En los municipios y distritos donde la carga "
            "de granizo deba tenerse en cuenta, su valor es de 1.0 "
            "kN/m² (100 kgf/m²). Para cubiertas con una inclinación "
            "mayor a 15° este valor puede reducirse a 0.5 kN/m² (50 "
            "kgf/m²)."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print(f"Borrando {len(IDS_A_BORRAR_CONDENSADOS)} chunks condensados (no verbatim) de B.4...")
    sb.table("nsr10_chunks").delete().in_("id", IDS_A_BORRAR_CONDENSADOS).execute()

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
