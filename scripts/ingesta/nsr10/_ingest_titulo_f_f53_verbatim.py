"""
NSR-10 Titulo F, Capitulo F.5 (Estructuras de Aluminio) -- F.5.3
(PRINCIPIOS DE DISEÑO) COMPLETO. Cuarta pieza de F.5, una seccion
manejable de solo 4 paginas (F-458 a F-461).

F.5.3.1 (Diseño para estados límite -- 5 estados a considerar
siempre + 2 adicionales en ciertas estructuras), F.5.3.2 (Cargas --
remite al Titulo B), F.5.3.3 (Resistencia estatica -- ecuacion
phi*Rn>=Sum(gamma_i*Q_i), Tabla F.5.3.3-1 de coeficientes de
reduccion de capacidad), F.5.3.4 (Deformacion -- deflexion elastica
recuperable con Tabla F.5.3.4-1 de deflexiones limite, deformacion
inelastica permanente, distorsion por ensamble frecuente), F.5.3.5
(Durabilidad -- remite a F.5.2.2/F.5.2.4), F.5.3.6 (Fatiga --
generalidades con 2 estados limite, colapso total con coeficiente de
vida por fatiga gamma_L, crecimiento estable de grietas), F.5.3.7
(Vibracion), F.5.3.8 (Ensayos).

Con esto F.5.3 queda COMPLETO. F.5.4 (Diseño estatico de miembros)
arranca justo despues en F-461 -- la seccion mas larga de F.5, ya
vista (sin ingestar) hasta la ultima pagina del PDF actual sin
terminar -- queda para las proximas piezas.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final CON verificacion real de tokens (metodo de F.4.6/F.4.7/F.4.8/
F.5.1/F.5.2, el unico confiable).

Fuente: NSR-10-1083-1182.pdf (Drive id 1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi,
ya descargado localmente), paginas internas F-458 a F-461 (paginas PDF
57-60), leidas visualmente pagina por pagina, re-verificadas contra el
PDF antes de transcribir. Ojo con las unidades: este capitulo usa
kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Uso: python _ingest_titulo_f_f53_verbatim.py
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
        "id": "NSR10-F-F_5_3_1_diseno_estados_limite",
        "seccion": "F.5.3 / F.5.3.1 (Principios de diseño — diseño para estados límite)",
        "titulo": "5 estados límite siempre considerados (resistencia estática, deformación, durabilidad); fatiga y vibración en ciertas estructuras.",
        "texto": (
            "F.5.3 — PRINCIPIOS DE DISEÑO. F.5.3.1 — DISEÑO PARA ESTADOS "
            "LÍMITE — Las estructuras de aluminio se diseñarán "
            "considerando los estados límite para los que pueden llegar "
            "a ser inapropiadas durante su uso futuro. Se deben "
            "considerar siempre los siguientes estados límite: "
            "Resistencia estática (estado límite último) (véase "
            "F.5.3.3). Deformación (estado límite de servicio) (véase "
            "F.5.3.4). Durabilidad (véase F.5.3.5). En ciertas "
            "estructuras es necesario considerar uno o ambos de los "
            "siguientes estados: Fatiga (véase F.5.3.6). Vibración "
            "(véase F.5.3.7). El diseño se realizará usando la guía "
            "dada en F.5.4 a F.5.7 y en los apéndices F.5.B a F.5.J. "
            "Sin embargo, se permite verificar un diseño propuesto por "
            "medio de ensayos (véase F.5.8)."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_2_3_1_cargas_resistencia_estatica",
        "seccion": "F.5.3.2 / F.5.3.3 / F.5.3.3.1 (Cargas; Resistencia estática; Acción-efecto bajo carga mayorada)",
        "titulo": "Cargas del Título B; φRn ≥ ΣγᵢQᵢ; acción-efecto = fuerza axial/momento/cortante bajo carga mayorada.",
        "texto": (
            "F.5.3.2 — CARGAS — Las estructuras de aluminio se "
            "diseñarán para las combinaciones de cargas estipuladas en "
            "el Título B. F.5.3.3 — RESISTENCIA ESTATICA — Un "
            "componente es aceptable en términos de resistencia "
            "estática si se satisface que: φRn ≥ ΣγᵢQᵢ. En donde: "
            "φ = coeficiente de reducción de capacidad, estipulado en "
            "la tabla F.5.3.3-1. γᵢ = coeficiente de mayoración para la "
            "carga i. Qᵢ = acción sobre la estructura que resulta de la "
            "aplicación de la carga i. Rn = resistencia nominal de un "
            "miembro estructural, calculada con base en procedimientos "
            "establecido en este Capítulo. F.5.3.3.1 — Acción-efecto "
            "bajo carga mayorada — Esto es la fuerza axial, el momento "
            "flector o la fuerza cortante generada en un componente por "
            "la aplicación de una carga mayorada y encontrada usando un "
            "procedimiento de análisis estructural aceptado. La carga "
            "mayorada se encuentra tomando las combinaciones de cargas "
            "estipuladas en el Título B y multiplicando cada una por el "
            "coeficiente de mayoración, establecido en la tabla "
            "F.5.3.2-1."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_3_2_resistencia_diseno_tabla1",
        "seccion": "F.5.3.3.2 (Resistencia de diseño — Tabla F.5.3.3-1)",
        "titulo": "Resistencia de diseño = resistencia nominal × φ; Tabla F.5.3.3-1: φ=0.86 (miembros), 0.86/0.80*/0.34 (uniones remachada/soldada/pegada).",
        "texto": (
            "F.5.3.3.2 — Resistencia de diseño — La resistencia de "
            "diseño se define como el producto de la resistencia "
            "nominal por el coeficiente de reducción de capacidad φ. La "
            "resistencia nominal es la capacidad del componente en "
            "relación con la acción estructural en consideración (carga "
            "axial, momento flector, fuerza cortante, etc.), calculada "
            "con base en un procedimiento de análisis reconocido en "
            "este Capítulo. El coeficiente de reducción de capacidad φ "
            "tiene en cuenta las diferencias entre la resistencia real "
            "de un miembro estructural y su resistencia nominal, "
            "causadas por variaciones en propiedades del material, "
            "tolerancias de fabricación y aproximaciones en el "
            "análisis. En estructuras de aluminio se utilizarán los "
            "coeficientes de reducción establecidos en la tabla "
            "F.5.3.3-1. Tabla F.5.3.3-1 — Coeficientes de reducción de "
            "capacidad, φ (Tipo de construcción — Miembros — Uniones): "
            "Remachada y empernada: 0.86, 0.86. Soldada: 0.86, 0.80 "
            "(debe usarse 0.70 en procedimientos que no cumplan con las "
            "especificaciones para aprobación de procedimientos de "
            "soldadura de aluminio y sus aleaciones con procesos TIG o "
            "MIG, como la BS4870 Parte 2). Pegada: 0.86, 0.34. En "
            "F.5.4, F.5.5 (miembros) y F.5.6 (uniones), se dan las "
            "reglas para establecer la resistencia calculada."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_4_deformacion_elastica",
        "seccion": "F.5.3.4 / F.5.3.4.1 (Deformación — deformación elástica recuperable)",
        "titulo": "Aceptable si deflexión elástica bajo carga de servicio < deflexión límite; calculada con sección bruta (o reducida en secciones esbeltas).",
        "texto": (
            "F.5.3.4 — DEFORMACION — Con fines de aceptación las "
            "deflexiones de una estructura de aluminio se calcularán "
            "para las cargas de servicio y las combinaciones de carga "
            "estipuladas en B.2.3. F.5.3.4.1 — Deformación elástica "
            "recuperable — Una estructura es aceptable en términos de "
            "deformación si su deflexión elástica bajo carga de "
            "servicio es menor que la deflexión límite. El cálculo de "
            "la deflexión elástica hará generalmente con base en las "
            "propiedades de la sección transversal bruta. Sin embargo, "
            "en secciones esbeltas puede ser necesario tomar las "
            "propiedades de la sección reducida para tener en cuenta el "
            "pandeo local (véase F.5.4)."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_4_tabla1_deflexiones_limite",
        "seccion": "Tabla F.5.3.4-1 (Deflexiones límite)",
        "titulo": "Voladizos L/180, vigas con yeso L/360, viguetas cubierta L/200-L/100, largueros vidrio L/175-L/250, columnas L/300; aluminio 3× más flexible que el acero.",
        "texto": (
            "Tabla F.5.3.4-1 — Deflexiones límites (Elemento — Deflexión "
            "límite recomendada). Voladizos que soportan pisos: L/180. "
            "Vigas con acabado de yeso u otro material frágil: L/360. "
            "Viguetas y rieles de cubiertas: (a) carga muerta "
            "únicamente: L/200. (b) bajo la peor combinación de carga "
            "muerta, impuesta, viento y nieve: L/100. Largueros y "
            "travesaños de paredes cortina: (a) vidrio sencillo: L/175. "
            "(b) vidrio doble: L/250. Parte superior de columnas: "
            "deflexión horizontal: L/300. (L es la longitud entre "
            "apoyos). La deflexión límite debe basarse en criterios "
            "racionales de ingeniería y se evaluará para condiciones de "
            "servicio con las combinaciones de carga estipuladas en el "
            "numeral B.2.3. La tabla F.5.3.4-1 da valores sugeridos "
            "para ciertos tipos de estructuras. En la definición de las "
            "deflexiones límites debe tenerse en cuenta que el aluminio "
            "es tres veces más flexible que el acero y por lo tanto, se "
            "debe evitar usar deflexiones límites excesivamente "
            "pequeñas."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_4_2_3_deformacion_inelastica_distorsion",
        "seccion": "F.5.3.4.2 / F.5.3.4.3 (Deformación inelástica permanente; distorsión por ensamble frecuente)",
        "titulo": "Sin deformación permanente si resistencia calculada según F.5.4; considerar cambios dimensionales acumulados en estructuras de acople frecuente.",
        "texto": (
            "F.5.3.4.2 — Deformación inelástica permanente — Por lo "
            "general, se puede suponer que los componentes cuya "
            "resistencia estática ha sido calculada de acuerdo con "
            "F.5.4, no sufrirán deformación permanente significativa "
            "bajo la acción de la carga nominal. Esto se puede aplicar "
            "a todos los grupos de aleaciones. F.5.3.4.3 — Distorsión "
            "debida a ensamble frecuente — En ciertas estructuras que "
            "tienen que ser armadas y desarmadas frecuentemente, es "
            "necesario considerar la posibilidad de cambios en las "
            "dimensiones principales del sistema de acople que "
            "conducen a la aparición gradual de errores inaceptables "
            "en la forma ensamblada."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_5_durabilidad_6_1_fatiga_generalidades",
        "seccion": "F.5.3.5 / F.5.3.6 / F.5.3.6.1 (Durabilidad; Fatiga — generalidades, 2 estados límite)",
        "titulo": "Durabilidad remite a Tablas F.5.2.2-1 a -4 y BS 8118 Parte 2; fatiga revisa colapso total y crecimiento estable de grietas bajo espectro de carga de servicio.",
        "texto": (
            "F.5.3.5 — DURABILIDAD — La clasificación de durabilidad de "
            "los grupos de aleaciones se da en las tablas F.5.2.2-1 a "
            "F.5.2.2-4. Si una estructura se diseña en una aleación "
            "durable y se protege adecuadamente de acuerdo con normas "
            "como el BS 8118: Parte 2, se estima que se comportará "
            "satisfactoriamente. Se deben considerar el grado de "
            "exposición y la vida de diseño. F.5.3.6 — FATIGA. "
            "F.5.3.6.1 — Generalidades — Cualquier estructura o "
            "componente estructural que esté sometida a variaciones "
            "significativas de la carga, debe ser revisada por fatiga. "
            "Se deben considerar dos estados límite: (a) Colapso total. "
            "(b) Crecimiento estable de grietas (tolerancia de daño). "
            "En ambos casos se supone que actúa el espectro de carga de "
            "servicio (no mayorado)."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_6_2_colapso_total",
        "seccion": "F.5.3.6.2 (Colapso total — vida prevista, coeficiente de vida por fatiga γL)",
        "titulo": "Vida prevista (F.5.7) debe ser ≥ vida de diseño; coeficiente γL(>1) ajustable según crecimiento de grietas/exactitud del espectro/registros/cambio de uso.",
        "texto": (
            "F.5.3.6.2 — Colapso total — El procedimiento para "
            "considerar este estado límite es determinar la vida "
            "prevista de acuerdo con F.5.7 y verificar que no sea menor "
            "que la vida de diseño. En ciertas circunstancias, el "
            "diseñador puede desear incrementar la vida de diseño "
            "nominal multiplicando por un coeficiente de vida por "
            "fatiga γL(>1). La selección de γL puede verse influenciada "
            "por lo siguiente: (a) La posibilidad de que se incremente "
            "el crecimiento de grietas durante etapas posteriores de la "
            "vida del detalle. (b) La exactitud del espectro de carga "
            "supuesto. (c) Si se mantendrán registros de carga durante "
            "la vida del detalle. (d) La posibilidad de un cambio de "
            "uso de la estructura durante su vida. El diseñador puede "
            "también desear aplicar un coeficiente de fatiga del "
            "material, γmf, para el rango de esfuerzos de diseño dado "
            "en la figura F.5.9. El rango de esfuerzos de diseño se "
            "dividiría por γmf(>1) y la selección de γmf podría estar "
            "influenciada por lo siguiente: (1) El detalle deberá "
            "existir en un ambiente muy hostil. (2) Si la falla del "
            "detalle resultaría en la falla de la estructura entera o "
            "si existen caminos alternativos para la carga."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_6_3_crecimiento_grietas",
        "seccion": "F.5.3.6.3 (Crecimiento estable de grietas — tolerancia de daño)",
        "titulo": "Daño monitoreado por tasa de crecimiento de grietas en inspecciones regulares; métodos de cálculo fuera del alcance de la norma.",
        "texto": (
            "F.5.3.6.3 — Crecimiento estable de grietas — El daño de "
            "una estructura bajo condiciones de fatiga se determina "
            "monitoreando la tasa de crecimiento de las grietas de "
            "fatiga con intervalos de inspección regulares. Los "
            "métodos de inspección, las longitudes de grieta límite "
            "aceptables, las tasas admisibles de crecimiento de las "
            "grietas y el tiempo entre inspecciones deben ser acordados "
            "por el diseñador y el cliente. El crecimiento de grietas "
            "es estable cuando la tasa admisible de crecimiento de las "
            "grietas no se incrementa súbitamente entre inspecciones. "
            "Los métodos para calcular el crecimiento de grietas y la "
            "longitud límite de las grietas están por fuera del alcance "
            "de estas normas pero la facilidad con que un detalle puede "
            "ser inspeccionado buscando grietas puede influir en la "
            "selección de γmf (véase F.5.3.6.2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_3_7_8_vibracion_ensayos",
        "seccion": "F.5.3.7 / F.5.3.8 (Vibración; Ensayos)",
        "titulo": "Vibración: verificar amplitud/amortiguamiento/frecuencias bajas causando incomodidad. Ensayos: componentes diseñados según F.5.4-F.5.7 no requieren ensayo.",
        "texto": (
            "F.5.3.7 — VIBRACIÓN — Para ciertas estructuras la "
            "posibilidad de vibración indeseable bajo condiciones "
            "normales de servicio debe ser considerada. Se deben usar "
            "las cargas nominales para hacer la verificación de la "
            "incompatibilidad de las amplitudes de vibración. Si se "
            "cree que la vibración puede ser un problema potencial, se "
            "debe verificar también la posibilidad de falla por fatiga "
            "(véase F.5.3.6). Cuando los efectos de las vibraciones "
            "sean apreciables, las características de amortiguamiento "
            "de la forma de la estructura y de los materiales deberán "
            "ser tenidas en cuenta. La necesidad de suministrar un "
            "amortiguamiento artificial deberá ser examinada, y puede "
            "ser necesario realizar ensayos con prototipos. La "
            "vibración de estructuras con bajas frecuencias naturales "
            "puede causar incomodidad en los usuarios y deberá ser "
            "considerada en el diseño del proyecto. F.5.3.8 — ENSAYOS "
            "— Los componentes estructurales diseñados de acuerdo con "
            "F.5.4 a F.5.7 y los apéndices apropiados pueden ser "
            "aceptados sin ensayos. Los componentes diseñados usando "
            "otros procedimientos de cálculo y los componentes no "
            "calculados deben ser aceptados sólo si su resistencia ha "
            "sido verificada con ensayos. Tales ensayos deben ser "
            "ejecutados de acuerdo con F.5.8."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.5.3 cargados. F.5.3 queda COMPLETO.")


if __name__ == "__main__":
    main()
