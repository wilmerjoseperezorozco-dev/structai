"""
AIS 2004 -- Capitulo IV: Rehabilitacion de las viviendas (reparacion,
reforzamiento, reconstruccion). Matriz de decision Vulnerabilidad x Dano ->
tipo de intervencion, mas catalogo de tecnicas constructivas reales de
reparacion (A.1-A.9) y reforzamiento (B.1-B.6) con materiales, equipo,
ejecucion, control de calidad y limitaciones -- el nivel de detalle
constructivo que complementa los factores abstractos K de Build Change.

Fuente: mismo documento AIS 2004 ya registrado (ver AIS-2004 en
normas_registro), paginas internas 4-1 a 4-47 (Capitulo IV). Resumen
tecnico en palabras propias con atribucion, no reproduccion literal
extensa; no se distribuye el PDF a traves de la app.

Uso: python _ingest_ais2004_cap4_rehabilitacion.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo Resistente de Viviendas de Mampostería (base histórica de AIS 410-23, financiado por el FOREC tras el terremoto del Eje Cafetero 1999)"

CHUNKS = [
    {
        "id": "AIS2004-cap4-marco_decision_reparacion",
        "seccion": "Capítulo IV.A — Marco de decisión y reparación de viviendas",
        "titulo": (
            "Definiciones de Reparacion/Reforzamiento/Reconstruccion, matriz de decision "
            "Vulnerabilidad (Cap.II) x Dano (Cap.III) que determina el tipo de "
            "intervencion requerida, y tecnicas de REPARACION con detalle constructivo "
            "real: panete cosmetico, reparacion de juntas de mortero, reemplazo de muros "
            "(procedimiento con puntales, picado de superficie, anclaje epoxico, tiempos "
            "de contraccion), reparacion de elementos de confinamiento, reemplazo de "
            "entrepiso/cubierta de madera."
        ),
        "texto": (
            "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo "
            "Resistente de Viviendas de Mampostería. Capítulo IV — Rehabilitación de las "
            "viviendas.\n\n"
            "TRES TIPOS DE INTERVENCIÓN (definiciones): (a) REPARACIONES — obras para "
            "restaurar la capacidad de carga ORIGINAL ante afectaciones por terremoto u "
            "otro efecto; (b) REFORZAMIENTO — obras para dar MAYOR capacidad de carga, "
            "sin que necesariamente existan daños previos; (c) RECONSTRUCCIÓN — obras "
            "para reconstituir partes gravemente afectadas, con capacidad de carga igual "
            "o superior a la original. Una vivienda requiere rehabilitación cuando "
            "presenta daño estructural de consideración, o tiene deficiencias "
            "constructivas evidentes que pongan en peligro su seguridad. Si está en buen "
            "estado sin daños ni deficiencias, NO es necesaria la rehabilitación (incluso "
            "si fue sometida a un sismo intenso sin sufrir daños de consideración).\n\n"
            "MATRIZ DE DECISIÓN — el grado de intervención se define cruzando el grado de "
            "VULNERABILIDAD (Capítulo II) contra el NIVEL DE DAÑO (Capítulo III):\n"
            "  Vulnerabilidad Baja + Daño Leve → Intervención menor: reparaciones "
            "cosméticas\n"
            "  Vulnerabilidad Media + Daño Leve → Reforzamiento moderado\n"
            "  Vulnerabilidad Alta + Daño Leve → Reforzamiento\n"
            "  Vulnerabilidad Media + Daño Moderado → Reparación estructural + "
            "Reforzamiento\n"
            "  Vulnerabilidad Alta + Daño Moderado → Reforzamiento + Reconstrucción\n"
            "  Vulnerabilidad Alta + Daño Severo → Reconstrucción\n"
            "  (Nota importante: si la vivienda presenta daños moderados y/o severos, se "
            "clasifica AUTOMÁTICAMENTE como vulnerabilidad media o alta, incluso si el "
            "checklist cualitativo del Capítulo II hubiera dado un resultado menor — el "
            "daño observado siempre gobierna sobre la evaluación teórica.)\n\n"
            "A. REPARACIÓN DE VIVIENDAS — se ejecutan según el daño observado, no según "
            "la vulnerabilidad teórica:\n\n"
            "Reparaciones COSMÉTICAS (mejoran apariencia visual, protección a humedad, "
            "NO restauran capacidad estructural):\n"
            "  A.1 Pañete: capa de material (pintura, papel, yeso, polímeros orgánicos, "
            "estuco) sobre la superficie para ocultar grietas. LIMITACIÓN CRÍTICA: solo "
            "es efectivo si la grieta es INACTIVA (causada por un evento sísmico aislado, "
            "no por contracción o temperatura, que seguirían moviéndose). Requiere "
            "limpieza previa con chorro de arena o grata metálica para lograr adherencia.\n"
            "  A.2 Reparación de juntas de mortero: retirar mortero deteriorado y "
            "reemplazarlo con nuevo mortero de color/textura/tamaño de grano similar al "
            "original. Vida útil de pocos años; NO es sustituto de una reparación "
            "estructural, y nunca debe usarse en construcciones históricas.\n"
            "  A.3 Inyección de grietas con epóxico: reparación cosmética para grietas "
            "finas inactivas.\n\n"
            "Reparaciones ESTRUCTURALES (mejoran las propiedades estructurales reales):\n"
            "  A.4 Inyección de grietas (estructural), A.5 Roturas y estilladuras del "
            "material, A.6 Reemplazo de barras de refuerzo.\n"
            "  A.7 Reemplazo de muros: se remueve el muro afectado (instalando puntales "
            "si es muro de carga) y se construye uno nuevo lo más similar posible al "
            "existente. Procedimiento: picar la superficie de contacto en amplitudes del "
            "orden de 6 mm; las barras de refuerzo nuevas se anclan en perforaciones con "
            "epóxico a la estructura existente (consultar al fabricante la profundidad de "
            "empotramiento); usar concreto tradicional o preferiblemente concreto "
            "lanzado. IMPORTANTE: el nuevo concreto/mortero se contraerá por secado (la "
            "estructura existente no), generando una fisura en el punto de contacto — "
            "esta fisura de retracción se sella con epóxico DESPUÉS de 2 a 4 meses "
            "(cuando ya ocurrió la mayor parte de la contracción). LIMITACIÓN: si el muro "
            "era de mampostería NO reforzada, debe reemplazarse con el MISMO tipo de "
            "mampostería (probablemente la vivienda deba reforzarse aparte).\n"
            "  A.8 Reparación de elementos de confinamiento de concreto reforzado: "
            "retirar TODO el concreto fisurado dejando expuesto el refuerzo completo; "
            "identificar y reemplazar el refuerzo afectado (fluido, deformado o dañado) "
            "por refuerzo de características similares al original; retirar concreto "
            "suficiente para garantizar los empalmes requeridos; amarrar el nuevo "
            "refuerzo al existente antes de fundir. Curado por humedecimiento continuo "
            "los primeros 5 días, al menos 3 veces diarias.\n"
            "  A.9 Reemplazo de elementos de entrepiso/cubierta de madera: para pisos de "
            "material rígido (ladrillo), apuntalar las zonas inmediatas ANTES de retirar "
            "la viga afectada para evitar colapso; la viga se corta a 20-30 cm de "
            "distancia de los muros donde está empotrada; se pica el muro para extraer la "
            "parte embebida, se instala la nueva viga apuntalada, se rellenan las zonas "
            "de apoyo y se deja fraguar antes de retirar el apuntalamiento. Vigas de "
            "madera nuevas requieren sustancias preservantes de buena penetrabilidad, "
            "evaluando su toxicidad y capacidad fitotóxica."
        ),
    },
    {
        "id": "AIS2004-cap4-tecnicas_reforzamiento",
        "seccion": "Capítulo IV.B — Reforzamiento de viviendas",
        "titulo": (
            "Tecnicas de REFORZAMIENTO con detalle constructivo real: vigas/columnas de "
            "confinamiento nuevas empotradas en muro existente, revestimiento estructural "
            "en concreto lanzado (anclajes epoxicos cada 2-3 veces el espesor del muro, "
            "barras <=No.5, curado 7 dias), refuerzo de cimentacion, confinamiento de "
            "aberturas (4 barras No.3 + estribos No.3@20cm), reemplazo de muros no "
            "estructurales por estructurales, revestimiento con fibras de carbono/vidrio "
            "y resina epoxica."
        ),
        "texto": (
            "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo "
            "Resistente de Viviendas de Mampostería. Capítulo IV.B — Reforzamiento de "
            "viviendas (dar MAYOR capacidad de carga, con o sin daño previo).\n\n"
            "B.1 Construcción de vigas y columnas de confinamiento en concreto reforzado: "
            "se pica el muro donde se colocarán los nuevos elementos, se coloca el acero "
            "de refuerzo verificando su disposición, se instalan formaletas y se funde "
            "cuidando el vibrado para evitar hormigueros. Detalle típico observado: "
            "refuerzo adicional con ganchos cada 20 cm (2 barras No.4) ancla la nueva "
            "columna al muro existente de mampostería no reforzada. El curado sigue las "
            "indicaciones generales del Capítulo I del manual.\n\n"
            "B.2 Revestimiento estructural en concreto reforzado: se aplica en una o "
            "AMBAS caras del muro (recomendado ambas), unido a la estructura existente "
            "para lograr comportamiento monolítico. Dos procesos de aplicación: concreto "
            "lanzado (neumático, mezcla húmeda o mezcla seca) o capas moldeadas en sitio. "
            "Procedimiento: la superficie existente se pica/escarifica (evitando cambios "
            "abruptos de dimensión) y se prehumedece; el acero de refuerzo se ancla con "
            "epóxico atravesando el muro de lado a lado, con espaciamiento de anclajes de "
            "2 a 3 VECES EL ESPESOR DEL MURO; se instalan alambres guía para controlar el "
            "alineamiento del espesor de aplicación. Para concreto lanzado: la boquilla "
            "se orienta PERPENDICULAR a la superficie, con flujo firme ininterrumpido "
            "desde la base del muro hacia arriba, en espesor ligeramente superior al "
            "indicado por los alambres guía; curado húmedo mínimo 1 día, preferiblemente "
            "7 días. LIMITACIÓN IMPORTANTE: las barras de refuerzo deben ser ≤ No.5 (si "
            "se requieren más grandes, el constructor debe demostrar mediante ensayos que "
            "el concreto lanzado puede colocarse correctamente alrededor de ellas); los "
            "traslapos entre barras deben alternarse para no coincidir en una misma "
            "sección; NO se recomienda el uso de agentes adherentes (el concreto lanzado "
            "se adhiere bien a superficies de mampostería/concreto limpias sin ellos). "
            "Control de calidad: paneles de ensayo al inicio de cada día y de cada "
            "vaciada, curados igual que los muros, con núcleos/cubos para verificar "
            "resistencia — la calidad depende fuertemente de la habilidad del operador "
            "de boquilla.\n\n"
            "B.3 Refuerzo de la cimentación: se construyen vigas de cimentación en "
            "concreto reforzado (o se reemplazan barras de refuerzo afectadas siguiendo "
            "el procedimiento de A.6). Se excava a lo largo del muro ~10 cm a cada lado; "
            "se pica la porción del muro empotrada en el suelo para colocar el refuerzo "
            "vertical y el que atraviesa la nueva viga de cimentación (barras que pasan "
            "el muro, formando anillos amarrados con la cimentación existente en piedra o "
            "concreto ciclópeo).\n\n"
            "B.4 Confinamiento de aberturas: se construyen elementos de concreto reforzado "
            "alrededor de aberturas en muros (puertas/ventanas) para lograr buen "
            "confinamiento. Detalle típico: 4 barras No.3 (refuerzo superior e inferior), "
            "estribos No.3 espaciados cada 20 cm, ancho de elemento ~12 cm.\n\n"
            "B.5 Reemplazo de muros no estructurales (o muros con aberturas) por muros "
            "estructurales: procedimiento similar a A.7 (reemplazo de muros), pero el "
            "nuevo muro SÍ debe contener acero de refuerzo (a diferencia de una simple "
            "reparación). Mismo manejo de fisuras de retracción — sellado con epóxico "
            "entre 2 y 4 meses después de construido.\n\n"
            "B.6 Revestimiento estructural mediante fibras compuestas: fibras delgadas de "
            "vidrio o carbono aplicadas a la superficie del muro con resina epóxica "
            "aglutinante, orientadas en una o dos direcciones. Actúan como refuerzo A "
            "TENSIÓN del muro — incrementan la RESISTENCIA pero en general NO aumentan la "
            "RIGIDEZ del muro que refuerzan (distinción importante frente al "
            "revestimiento de concreto reforzado, que sí añade rigidez). Preparación: las "
            "grietas se reparan primero con inyección de mortero epóxico, roturas y "
            "estilladuras se reparan, y la superficie se limpia con grata metálica o "
            "chorro de arena suave antes de aplicar la fibra.\n\n"
            "TABLA DE CORRESPONDENCIA aspecto de vulnerabilidad → técnica de "
            "intervención recomendada (Capítulo IV, indicaciones referentes al grado de "
            "vulnerabilidad): irregularidad en planta/altura y cantidad insuficiente de "
            "muros → construcción de vigas/columnas de confinamiento + reemplazo de "
            "muros no estructurales por estructurales; mala calidad de juntas/materiales "
            "→ revestimiento estructural en concreto o fibras compuestas; falta de "
            "confinamiento o vigas de amarre → construcción de vigas/columnas de "
            "confinamiento; aberturas mal detalladas → confinamiento de aberturas; "
            "problemas de cimentación/suelo/entorno → refuerzo de cimentación (en casos "
            "críticos de entorno, evaluar la reubicación de la vivienda en vez de "
            "reforzarla en el sitio)."
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
    print(f"OK: {len(rows)} chunks AIS 2004 Cap IV cargados con embedding.")


if __name__ == "__main__":
    main()
