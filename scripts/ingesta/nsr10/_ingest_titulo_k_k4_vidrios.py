"""
NSR-10 Titulo K, Capitulo K.4 -- Requisitos especiales para vidrios, productos
de vidrio y sistemas vidriados. Capitulo COMPLETO faltante en el corpus (el
Titulo K solo tenia K.1-K.3 cargados; K.4 -- practico y de seguridad, sobre
vidrios/ventanales/fachadas -- no tenia ni un chunk).

Fuente: NSR-10-1571-1625.pdf (Drive, id 1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z),
paginas internas K-33 a K-58+ (K.4.1 a K.4.3.9). 4 chunks single-topic.

Uso: python _ingest_titulo_k_k4_vidrios.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título K — Requisitos Complementarios"

CHUNKS = [
    {
        "id": "NSR10-K-K_4_1_alcance_definiciones",
        "seccion": "K.4.1 (Alcance y definiciones)",
        "titulo": (
            "Requisitos especiales para vidrios, productos de vidrio y "
            "sistemas vidriados: alcance (vidrios/ventanales/fachadas/pisos "
            "de vidrio) y definiciones clave -- vidrio de seguridad "
            "(templado/laminado/con recubrimiento organico), grado de "
            "desempeno GD, sistema de baranda, muro cortina."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — Requisitos especiales para "
            "vidrios, productos de vidrio y sistemas vidriados.\n\n"
            "K.4.1.1 Alcance — aplica a: (a) vidrios, vidrieras, ventanales "
            "y productos de vidrio en edificaciones; (b) láminas de vidrio "
            "verticales e inclinadas en sistemas vidriados de fachada; "
            "(c) láminas de vidrio para pisos y elementos estructurales de "
            "vidrio; (d) elementos complementarios de sistemas de "
            "vidriado.\n\n"
            "K.4.1.2 Definiciones clave (glosario completo más extenso en "
            "la fuente):\n"
            "  VIDRIO DE SEGURIDAD (Safety glass) — vidrio fabricado, "
            "tratado o combinado de tal forma que al romperse por contacto "
            "humano reduce la probabilidad/gravedad de cortes; debe cumplir "
            "ANSI Z97.1-2004e. El vidrio MONOLÍTICO RECOCIDO de cualquier "
            "espesor NO se considera vidrio de seguridad.\n"
            "  VIDRIO TEMPLADO (Fully tempered) — tratado térmicamente a "
            "alta compresión superficial; al romperse se fragmenta en "
            "pedazos pequeños de bordes romos (ASTM C1048-04).\n"
            "  VIDRIO LAMINADO (Laminated) — al menos 2 láminas de vidrio "
            "adheridas con una entrecapa orgánica; al romperse los "
            "fragmentos se adhieren a la entrecapa (ASTM C1172:09).\n"
            "  VIDRIO RECOCIDO (Annealed) — lámina plana monolítica con "
            "esfuerzos superficiales residuales cercanos a cero — el más "
            "básico, NO es vidrio de seguridad.\n"
            "  VIDRIO ARMADO (Wired glass) — con malla de alambre incluida "
            "(NTC 1909:2009).\n"
            "  GRADO DE DESEMPEÑO — GD (Performance Grade — PG) — indicador "
            "numérico del comportamiento de un producto vidriado para "
            "tragaluces/claraboyas, según ensayos AAMA/WDMA/CSA "
            "101/I.S.2/A440-08.\n"
            "  SISTEMA DE BARANDA (Guard System) — protección a lo largo de "
            "bordes de terrazas, balcones, techos, plataformas, rampas, "
            "escaleras o descansos, diseñada para minimizar caídas "
            "accidentales.\n"
            "  MURO CORTINA o FACHADA FLOTANTE (Curtain Wall) — sistema de "
            "aislamiento (luz/calor/ruido/viento) que agrega carga a la "
            "estructura sin ser parte del sistema de resistencia sísmica.\n"
            "  UNIDAD DE DOBLE VIDRIADO — 2 láminas separadas por cavidad "
            "sellada permanentemente (ASTM E2190-08).\n"
            "  TRAGALUZ/VIDRIO INCLINADO/CLARABOYA (Skylight) — vidrio "
            "plano instalado a más de 15° de la vertical en el exterior."
        ),
    },
    {
        "id": "NSR10-K-K_4_2_requisitos_diseno",
        "seccion": "K.4.2 (Requisitos de diseño)",
        "titulo": (
            "Requisitos de diseno de vidrios: elementos no estructurales "
            "cumplen A.9 + K.4.2-4.4, elementos estructurales cumplen A.8 + "
            "K.4.2.3-4.4. Espesores segun ASTM E1300-09a para cargas "
            "combinadas <=10 kPa, cargas de viento (Titulo B) y sismo (A.2/"
            "A.9), esfuerzos termicos (rotura espontanea de vidrio "
            "templado)."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.2, Requisitos de Diseño.\n\n"
            "K.4.2.1 Marco normativo — los elementos NO ESTRUCTURALES de "
            "vidrio (ventanas, fachadas decorativas) deben cumplir el "
            "Capítulo A.9 (elementos no estructurales) además de K.4.2.2, "
            "K.4.2.3, K.4.3 y K.4.4. Los elementos ESTRUCTURALES de vidrio "
            "(pisos de vidrio, elementos que forman parte del sistema "
            "resistente) deben cumplir el Capítulo A.8 además de K.4.2.3, "
            "K.4.3 y K.4.4.\n\n"
            "K.4.2.2 Marcos — se diseñan según las especificaciones del "
            "material empleado; los elementos de soporte metálicos cumplen "
            "el Título F (estructuras metálicas). Tabla K.4.2-0 — "
            "propiedades físicas convencionales del vidrio: densidad 2500 "
            "kg/m³, dureza 6 (escala Mohs), módulo de Young E=7×10^10 Pa, "
            "índice de Poisson 0.2, coeficiente de dilatación lineal "
            "9×10⁻⁶ K⁻¹ (20-300°C).\n\n"
            "K.4.2.3 Espesores de láminas de vidrio — se determinan según "
            "dimensiones, relación largo/ancho, lados apoyados, "
            "probabilidad de rotura, deflexiones máximas permitidas y "
            "cargas de viento u otra causa. Para cargas combinadas de "
            "viento+empozamiento+peso propio <=10 kPa, se permite el "
            "método de la norma ASTM E1300-09a. Deben considerarse además: "
            "esfuerzos térmicos, rotura espontánea de vidrios templados, "
            "efectos de escombros llevados por el viento, efectos sísmicos, "
            "flujo de calor, atenuación de ruido, y comportamiento de "
            "fragmentos tras la rotura.\n\n"
            "K.4.2.4 Cargas:\n"
            "  K.4.2.4.1 Cargas de viento — los componentes exteriores "
            "vidriados se diseñan para las presiones de viento evaluadas "
            "según el Título B.\n"
            "  K.4.2.4.2 Efectos sísmicos — se evalúan según el Capítulo "
            "A.2 (elementos estructurales) o A.9 (elementos no "
            "estructurales); cuando se usa A.9, la fuerza sísmica actúa "
            "perpendicular al plano del sistema vidriado. Clasificación por "
            "Grado de Desempeño sísmico (A.9.2): Superior (daño mínimo, sin "
            "interferencia operativa), Bueno (daño reparable, posible "
            "interferencia temporal), Bajo (daños graves, incluso no "
            "reparables).\n"
            "  K.4.2.4.3 Esfuerzos térmicos — deben evaluarse (rotura "
            "espontánea de vidrio templado por choque térmico); requiere "
            "estimar niveles de exposición solar/sombra y determinar una "
            "probabilidad de rotura acumulada — el límite práctico de "
            "diseño es que esa probabilidad no supere el 0.8%.\n"
            "  K.4.2.4.4 Otras cargas — adicionales a viento y sismo, según "
            "el Título B."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_seguridad_general",
        "seccion": "K.4.3.1 a K.4.3.8 (Seguridad — disposiciones generales)",
        "titulo": (
            "Disposiciones generales de seguridad para vidrios: exigencia "
            "de vidrio de seguridad (templado/laminado/recubierto) en los "
            "espacios de K.4.3.9, prohibicion de vidrios con fallas/"
            "defectos, sellado con neopreno/silicona, ensayos segun NTC "
            "1578, minimo 2 soportes blandos en la parte inferior de cada "
            "unidad."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.1 a K.4.3.8, Seguridad "
            "(disposiciones generales, previas al detalle de impacto "
            "humano de K.4.3.9).\n\n"
            "K.4.3.1 — deben establecerse medidas y características de "
            "seguridad de los materiales vidriados para que puedan usarse "
            "sin riesgo para ocupantes y transeúntes.\n\n"
            "K.4.3.2 — se EXIGE el uso EXCLUSIVO de vidrios de seguridad "
            "(laminados, templados o recubiertos) en los espacios "
            "señalados en K.4.3.9 (requerimientos de impacto humano).\n\n"
            "K.4.3.3 — NO deben emplearse vidrios con fallas o defectos que "
            "afecten sus propiedades físicas indispensables.\n\n"
            "K.4.3.4 — vidrios fijos con pisavidrios deben sellarse con "
            "empaques de neopreno, silicona u otro sellador garantizado a "
            "todo el contorno, para evitar vibraciones que causen rotura o "
            "ruido molesto.\n\n"
            "K.4.3.5 — los ensayos para tipos de vidrio de seguridad se "
            "realizan según la Norma NTC 1578.\n\n"
            "K.4.3.6 — los sistemas de vidriado deben diseñarse para que no "
            "haya humedad prolongada en los canales de fijación.\n\n"
            "K.4.3.7 — para evitar roturas por peso propio o deformaciones/"
            "protuberancias del marco (tornillos, soldaduras), se exige "
            "colocar en la parte INFERIOR, como mínimo, DOS soportes "
            "blandos por cada unidad de vidrio.\n\n"
            "K.4.3.8 — deben emplearse empaques NO duros (neopreno o "
            "similares) cuando el vidrio esté sometido a impactos, altas "
            "presiones normales, choques térmicos, vibraciones o "
            "filtraciones."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_9_impacto_humano",
        "seccion": "K.4.3.9 (Requerimientos de seguridad ante impacto humano)",
        "titulo": (
            "Requerimientos de seguridad ante impacto humano en vidrieras: "
            "zonas de riesgo hasta 2000mm de altura (alto/mediano/bajo/no "
            "riesgo), bandas de visibilidad, reglas por tipo de puerta y "
            "panel lateral, casos especiales (escuelas/guarderias, banos/"
            "spas, alto riesgo), y vidrio como proteccion de desnivel "
            ">=1000mm (funcion de baranda) via Tabla K.4.3-7."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.9, Requerimientos de "
            "seguridad ante el impacto humano. Regula visibilidad, "
            "puertas, paneles laterales y divisiones en vidrierías con "
            "riesgo de impacto humano (vidrieras hasta 2000 mm de altura "
            "sobre el nivel del piso).\n\n"
            "Niveles de riesgo por altura (Figura K.4.3-0): Alto riesgo (0-"
            "300 mm y 300-500 mm desde el piso), Mediano riesgo (500-1200 "
            "mm), Bajo riesgo (1200-2000 mm), No riesgo (>2000 mm).\n\n"
            "K.4.3.9.1 Visibilidad — si un vidrio transparente puede "
            "confundirse con el vano de una puerta o un trayecto despejado, "
            "debe hacerse visible con una BANDA OPACA de más de 20 mm de "
            "alto, ubicada entre 700 mm (borde superior mínimo) y 1000 mm "
            "(borde inferior máximo) desde el piso — o con un adorno/"
            "tratamiento decorativo equivalente. Excepciones sin banda: "
            "panel <=1000 mm de altura, <=500 mm de ancho, sin vidrio hasta "
            "500 mm del piso, panel con perfil protector, o vidrio de "
            "seguridad en viviendas.\n"
            "  Identificación obligatoria: cada lámina de vidrio de "
            "seguridad debe marcarse de forma legible y permanente con "
            "fabricante, tipo (T=templado, L=laminado), estándar de prueba "
            "y clasificación de impacto (A/B/C).\n\n"
            "K.4.3.9.2 Puertas — el vidriado se hace con vidrio de "
            "seguridad según la Tabla K.4.3-1, con excepciones específicas "
            "por tipo: puertas batientes/giratorias permiten vidrio "
            "recocido hasta 0.5 m²; puertas corredizas permiten recocido "
            "de 5 mm mínimo con travesaño horizontal; puertas con vidrio a "
            "tope requieren templado de seguridad de 10 mm mínimo; puertas "
            "de duchas/baños según K.4.3.9.6.\n\n"
            "K.4.3.9.3 Paneles laterales — un panel con borde vertical "
            "visible <300 mm del vano de una puerta, dentro de 30° del "
            "plano de la puerta cerrada. Los enmarcados generalmente "
            "requieren vidrio de seguridad salvo excepciones por tamaño "
            "pequeño o riel protector; los SIN enmarcar (bordes expuestos) "
            "requieren vidrio TEMPLADO de seguridad de mínimo 10 mm.\n\n"
            "Casos especiales:\n"
            "  ESCUELAS Y GUARDERÍAS (K.4.3.9.1.9): todo panel hasta 800 mm "
            "de altura debe ser vidrio de seguridad — el umbral más "
            "estricto de todo el capítulo, y aplica también a vidrieras a "
            "menos de 5 m de zonas deportivas/recreativas.\n"
            "  ÁREAS DE ALTO RIESGO (K.4.3.9.1.10): gimnasios, piscinas, "
            "spas, vestíbulos, balcones/miradores públicos, estadios — "
            "vidrio de seguridad según tablas K.4.3-1 o K.4.3-4.\n"
            "  BAÑOS, SPAS Y JACUZZIS (K.4.3.9.6): vidrio de seguridad "
            "obligatorio según tabla K.4.3-1; puertas de ducha sin enmarcar "
            "con reglas de espesor específicas.\n\n"
            "K.4.3.9.7 VIDRIO COMO PROTECCIÓN DE DESNIVEL (función de "
            "baranda) — cuando una vidriera protege a los ocupantes contra "
            "un desnivel de 1000 mm o MÁS desde el piso, debe cumplir la "
            "Tabla K.4.3-7: TIPO A (unidades familiares) — espesor de "
            "vidrio seleccionado por carga de viento según Tabla K.4.3-3 "
            "(requisito mínimo); TIPO B/C (todas las demás edificaciones) — "
            "vidrio de seguridad según Tabla K.4.3-1, o vidrio recocido "
            "según columnas de la Tabla K.4.3-2 con 5 mm de espesor "
            "mínimo. Nota de diseño explícita en la norma: los rieles de "
            "protección deben diseñarse para DISUADIR que la gente se "
            "siente sobre ellos. Para vanos de escalera aplica además "
            "K.4.3.9.11 (regla específica no cubierta en este resumen)."
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
    print(f"OK: {len(rows)} chunks K.4 (vidrios) cargados con embedding.")


if __name__ == "__main__":
    main()
