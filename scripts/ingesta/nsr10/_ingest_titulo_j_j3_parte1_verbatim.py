"""
Título J — re-ingesta verbatim, Capítulo J.3 (parte 1 de 3): J.3.1 a J.3.3.3.13.
Continúa la re-ingesta tras cerrar J.1 y J.2 completos.

Fuente: NSR-10-1501-1570.pdf, páginas J-11 a J-14 (páginas reales 44-47).
Extraído visualmente por el mismo bloqueo de codificación del PDF.

Reemplaza los chunks obsoletos NSR10-J-J_3_2_r1..r3 y
NSR10-J-J_3_3_1_a_J_3_3_2_r1..r3 (resumen condensado, sin tildes).
J.3.1, J.3.3.3.x nunca tuvieron chunk previo (huecos reales nuevos).
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
    "NSR10-J-J_3_2_r1", "NSR10-J-J_3_2_r2", "NSR10-J-J_3_2_r3",
    "NSR10-J-J_3_3_1_a_J_3_3_2_r1", "NSR10-J-J_3_3_1_a_J_3_3_2_r2", "NSR10-J-J_3_3_1_a_J_3_3_2_r3",
]

CHUNKS = [
    {
        "id": "NSR10-J-J_3_1_1", "seccion": "J.3.1.1",
        "titulo": "J.3.1.1 — Alcance del Capítulo J.3: protección contra el fuego de elementos estructurales, acabados y vías de evacuación",
        "texto": "J.3.1 — ALCANCE. J.3.1.1 — A continuación se presentan los requisitos de protección contra el fuego de edificaciones y las especificaciones mínimas que deben cumplir los elementos estructurales y los materiales utilizados con el propósito de proteger contra el fuego los elementos estructurales, los acabados y las vías de evacuación.",
    },
    {
        "id": "NSR10-J-J_3_2_1", "seccion": "J.3.2.1",
        "titulo": "J.3.2.1 — Definiciones del Título J: barrera contra el fuego, carga de fuego, muro cortafuego, resistencia al fuego, tiempo equivalente, etc.",
        "texto": (
            "J.3.2 — DEFINICIONES. J.3.2.1 — Las siguientes definiciones se aplican en este Capítulo: "
            "Barrera contra el fuego — Ensamblaje horizontal o vertical (muro, viga, losa, columna, etc.), con una "
            "resistencia al fuego determinada y cuyos materiales están diseñados para restringir la propagación del "
            "fuego y en la cual las aberturas existentes están protegidas (IBC, 2006). "
            "Carga de fuego ó potencial combustible — Se refiere al efecto ocasionado por un material combustible, "
            "debido a la energía calorífica que puede liberar, en función de su calidad y de su volumen. La energía "
            "disponible se mide en MJ (1 MJ = 0,28 kw/h = 0,239 Mcal), expresada como la suma del poder calorífico de "
            "todos los materiales contenidos en un recinto, dividida por el área del piso. Es usual expresarla en "
            "función de su equivalencia en masa de madera por unidad de área, sabiendo que 1 kg tiene una energía "
            "calorífica equivalente a 18 MJ. "
            "Distancia de separación al fuego — Distancia medida desde la fachada del edificio hasta el eje de la "
            "calle, vía pública o a una línea imaginaria entre dos edificios. La distancia debe ser medida "
            "perpendicularmente a la fachada y al eje de la vía (IBC, 2006). "
            "Fuego patrón — Fuego con variación de temperatura controlada con el tiempo, utilizado durante pruebas "
            "normalizadas. "
            "Junta resistente al fuego — Ensamblaje de productos diseñados para sello de juntas, ensayados y "
            "clasificados según su resistencia al fuego, de acuerdo con UL 2079, para resistir un determinado período "
            "de tiempo el paso de calor, humo y fuego. (IBC, 2006). "
            "Material no combustible — Material que no arde indefinidamente hasta consumirse, ya sea porque deja de "
            "arder al apartársele de la fuente de calor, caso en el cual puede clasificarse como difícilmente "
            "combustible, o porque no arde al ser expuesto a la llama, caso en el cual el material se clasifica como "
            "incombustible. "
            "Muro cortafuego — Muro sólido, o con vanos protegidos, con un determinado tiempo de protección contra el "
            "fuego, que restringe la propagación del fuego y que además es continuo desde la cimentación hasta el "
            "techo, con suficiente estabilidad estructural tal que, bajo exposición al fuego, no colapse. "
            "Protección pasiva — Es el proceso mediante el cual un elemento se protege contra el fuego "
            "recubriéndolo con un material que le provea un mayor aislamiento térmico. "
            "Protección activa — Tipo de protección contra el fuego consistente en la instalación de mecanismos "
            "automáticos de detección y de extinción de fuego. Algunos de ellos son: detectores de humo con alarmas "
            "sonoras, sistemas de extinción con productos químicos y rociadores de agua entre otros. "
            "Potencial combustible — Energía calorífica disponible por unidad de área de piso. También llamada carga "
            "de fuego. "
            "Prueba normalizada de incendio — Procedimiento estipulado en normas como las NTC 1480 e ISO 834, entre "
            "otras, en el cual la temperatura se eleva en forma controlada, siguiendo una ecuación definida en "
            "función del tiempo del fuego patrón. "
            "Resistencia al fuego — Período de tiempo en que un edificio o los componentes de este mantienen su "
            "función estructural o dan la posibilidad de confinar el fuego, medido como el tiempo que resiste un "
            "material expuesto directamente al fuego, sin producir llamas, gases tóxicos ni deformaciones excesivas. "
            "Resistencia requerida al fuego — Tiempo mínimo de resistencia al fuego, exigido por la autoridad "
            "competente, que debe resistir un miembro estructural u otro elemento de una edificación, en una prueba "
            "normalizada de incendio. "
            "Tiempo equivalente — Tiempo que tarda un elemento determinado en alcanzar, en la prueba normalizada de "
            "incendio, el máximo calentamiento que experimentaría en un incendio real."
        ),
    },
    {
        "id": "NSR10-J-J_3_3_1", "seccion": "J.3.3.1",
        "titulo": "J.3.3.1 — Categorías de riesgo de las edificaciones (I/II/III) según grupo de ocupación de Tabla J.1.1-1",
        "texto": "J.3.3 — CLASIFICACIÓN DE EDIFICACIONES EN FUNCIÓN DEL RIESGO DE PÉRDIDA DE VIDAS HUMANAS O AMENAZA DE COMBUSTIÓN. J.3.3.1 — CATEGORIAS DE RIESGO DE LAS EDIFICACIONES — Con el fin de evaluar la resistencia requerida al fuego todas las edificaciones se clasificarán, en función de los grupos de ocupación definidos en la tabla J.1.1-1, en una de las categorías de riesgo de pérdida de vidas humanas o amenaza de combustión que se definen a continuación.",
    },
    {
        "id": "NSR10-J-J_3_3_1_1", "seccion": "J.3.3.1.1",
        "titulo": "J.3.3.1.1 — Categoría I: mayor riesgo de pérdida de vidas humanas o alta amenaza de combustión (A-1,F-1,I-2,I-4,P y edificios >10 pisos)",
        "texto": "J.3.3.1.1 — Categoría I — Esta categoría comprende las edificaciones con mayor riesgo de pérdidas de vidas humanas o con alta amenaza de combustión. En ellas se incluyen: (a) Grupos de Ocupación (A-1), (F-1), (I-2), (I-4), (P). (b) Bodegas, depósitos e industrias de cualquier magnitud que manejen madera, pinturas, plásticos, algodón, combustible o explosivos de cualquier tipo. (c) Edificios de más de 10 pisos que no cumplan con los requisitos del numeral J.3.3.1.2, literal (a).",
    },
    {
        "id": "NSR10-J-J_3_3_1_2", "seccion": "J.3.3.1.2",
        "titulo": "J.3.3.1.2 — Categoría II: riesgo intermedio (edificios >10 pisos con alarma/rociadores; I-1,I-3,I-5,C-1,C-2,E,L,M,R-2,R-3)",
        "texto": "J.3.3.1.2 — Categoría II — Esta categoría comprende edificaciones de riesgo intermedio, tales como: (a) Edificios para cualquier ocupación, de más de 10 pisos, que dispongan de sistemas de alarma contra incendio, visuales y sonoros e independientes entre sí, que sean probados por lo menos cada 60 días y cuenten con rociadores de agua automáticos a satisfacción de la autoridad competente. (b) Grupos de Ocupación (I-1), (I-3), (I-5), (C-1), (C-2), (E), (L), (M), (R-2) y (R-3). Entre otros ancianatos, bares, restaurantes, cárceles, oficinas, centros comerciales, guarderías, colegios, universidades, hoteles, museos, teatros, salas de cine y salones de reunión.",
    },
    {
        "id": "NSR10-J-J_3_3_1_3", "seccion": "J.3.3.1.3",
        "titulo": "J.3.3.1.3 — Categoría III: baja capacidad de combustión (R-1 hasta 10 pisos; A-2, F-2, bodegas/industriales no incluidos en J.3.3.1.1.b)",
        "texto": "J.3.3.1.3 — Categoría III — Esta categoría comprende las edificaciones con baja capacidad de combustión. Incluye: (a) Grupos de Ocupación (R-1), edificaciones para viviendas con 10 pisos o menos. (b) Grupos de Ocupación (A-2), (F-2) y en general bodegas y edificios industriales no comprendidos en el numeral J.3.3.1.1, literal (b).",
    },
    {
        "id": "NSR10-J-J_3_3_2", "seccion": "J.3.3.2",
        "titulo": "J.3.3.2 — Clasificación de edificaciones en categoría de riesgo según Tabla J.3.3-1 (área/pisos) o Tabla J.3.3-2 (potencial combustible)",
        "texto": "J.3.3.2 — CLASIFICACIÓN DE LAS EDIFICACIONES EN UNA CATEGORIA DE RIESGO — Toda edificación debe clasificarse en una de las categorías de riesgo definidas en J.3.3.1. Dependiendo del grupo de uso de la edificación bajo estudio, esta clasificación se hace en función del área construida, de acuerdo con la tabla J.3.3-1, o en función del potencial combustible, de acuerdo con la tabla J.3.3-2, estimado con base en las especificaciones contenidas en los numerales J.3.4.2 y J.3.4.3.",
    },
    {
        "id": "NSR10-J-Tabla_J_3_3_1", "seccion": "J.3.3.2 (Tabla J.3.3-1)",
        "titulo": "Tabla J.3.3-1 — Categorización de edificaciones por resistencia al fuego según grupo de ocupación, área construida y número de pisos (I/II/III)",
        "texto": (
            "Tabla J.3.3-1 — Categorización de las edificaciones para efectos de resistencia contra el fuego de "
            "acuerdo con su uso, área total construida AT (m²), y número de pisos. Columnas de número de pisos: "
            "1, 2, 3, 4, 5, 6, 7 o más — celda en blanco significa que esa combinación de pisos no está definida "
            "en la tabla original para esa fila (no se rellena con una categoría). "
            "(C-1), AT>1500 m²: III, III, II, II, II, I, I. "
            "(C-1), AT<1500 m²: III, III, III, II, II, I, I. "
            "(C-2), AT>500 m²: II, I, I, I, I, I, I. "
            "(C-2), AT<500 m²: en blanco, II, I, I, I, I, I. "
            "(E), sin límite de área: III, III, III, II, II, I, I. "
            "(I-2),(I-4), AT>1000 m²: III, II, II, I, I, I, I. "
            "(I-2),(I-4), 500<AT<1000 m²: III, II, II, I, I, I, I. "
            "(I-2),(I-4), AT<500 m²: III, III, III, II, II, I, I. "
            "(I-3), AT>1000 m²: II, II, I, I, I, I, I. "
            "(I-3), AT<1000 m²: en blanco, III, II, I, I, I, I. "
            "(L-1),(L-2),(L-3),(L-4), AT>1000 m²: en blanco, I, I, I, I, I, I. "
            "(L-5),(I-1),(I-5), 500<AT<1000 m²: II, II, I, I, I, I, I. "
            "(L-5),(I-1),(I-5), AT<500 m²: III, III, III, II, II, I, I. "
            "(R-1),(R-2), unidades >140 m²: en blanco, en blanco, en blanco, II, I, I, I. "
            "(R-1),(R-2), unidades <=140 m²: en blanco, en blanco, en blanco, en blanco, III, II, I. "
            "(R-3), AT>5000 m²: III, II, I, I, I, I, I. "
            "(R-3), AT<5000 m²: III, III, II, I, I, I, I. "
            "Nota 1: en edificios para vivienda, el límite de 140 m² por unidad corresponde al promedio aritmético "
            "de las áreas de todas las unidades, sin tener en cuenta las zonas comunes. "
            "Nota de verificación: transcripción cuidadosa de una tabla matricial densa (PDF fuente con problema de "
            "codificación que impidió extracción mecánica, ver contexto del script) — ante cualquier decisión de "
            "diseño real, confirmar la celda específica contra el documento oficial, página J-13."
        ),
    },
    {
        "id": "NSR10-J-Tabla_J_3_3_2", "seccion": "J.3.3.2 (Tabla J.3.3-2)",
        "titulo": "Tabla J.3.3-2 — Categorización de edificaciones por potencial combustible Cc (MJ/m²) y número de pisos requiriendo protección (I/II/III)",
        "texto": (
            "Tabla J.3.3-2 — Categorización de las edificaciones para efectos de resistencia contra el fuego de "
            "acuerdo con su uso, densidad de carga combustible Cc (MJ/m²), y el número de pisos que requieren "
            "protección: 1, 2, 3, 4, 5 o más. NOTA: 1 MJ = 0,28 kW/h = 0,239 Mcal. "
            "(A-1),(A-2), Cc>8000: II, II, I, I, I. "
            "(A-1),(A-2), 4000<Cc<8000: III, II, II, I, I. "
            "(A-1),(A-2), Cc<4000: III, III, III, II, I. "
            "(F-1),(F-2), Cc>8000: I, I, I, I, I. "
            "(F-1),(F-2), 4000<Cc<8000: II, II, I, I, I. "
            "(F-1),(F-2), 2000<Cc<4000: III, III, II, II, I. "
            "(F-1),(F-2), Cc<2000: no aplica a esta fila según la tabla (rango cubierto por 2000<Cc<4000 hacia "
            "abajo). "
            "(P), Cc>8000: I, I, I, I, I. "
            "(P), 4000<Cc<8000: II, II, I, I, I. "
            "(P), Cc<4000: III, II, I, I, I. "
            "Nota de verificación: transcripción cuidadosa de una tabla matricial densa (PDF fuente con problema de "
            "codificación que impidió extracción mecánica) — ante cualquier decisión de diseño real, confirmar la "
            "celda específica contra el documento oficial, página J-13."
        ),
    },
    {
        "id": "NSR10-J-J_3_3_3_intro", "seccion": "J.3.3.3",
        "titulo": "J.3.3.3 — Edificaciones que NO requieren cuantificación de resistencia contra el fuego (introducción, siguen sujetas a Capítulo J.4)",
        "texto": "J.3.3.3 — EDIFICACIONES QUE NO REQUIEREN CUANTIFICACIÓN DE LA RESISTENCIA CONTRA EL FUEGO — Las edificaciones cuyas características las eximen del requisito de la cuantificación de su resistencia contra el fuego se listan a continuación. Independientemente de esta excepción, toda estructura está sujeta a las especificaciones para detección y extinción de incendios dadas en el Capítulo J.4.",
    },
    {
        "id": "NSR10-J-J_3_3_3_1", "seccion": "J.3.3.3.1",
        "titulo": "J.3.3.3.1 — Exención: grupo C (Comercial), máximo 2 pisos, área construida <=500 m² por piso",
        "texto": "J.3.3.3.1 — Edificaciones clasificadas en el grupo de ocupación C (Comercial), de acuerdo con J.1.1.2, que no tengan más de dos (2) pisos y cuya área construida no exceda 500 m² por piso.",
    },
    {
        "id": "NSR10-J-J_3_3_3_2", "seccion": "J.3.3.3.2",
        "titulo": "J.3.3.3.2 — Exención: subgrupo I-3 (Educación), un solo piso, área construida <=1200 m²",
        "texto": "J.3.3.3.2 — Edificaciones clasificadas en el subgrupo de ocupación I-3 (Educación), que tengan un solo piso y cuya área construida no exceda 1 200 m².",
    },
    {
        "id": "NSR10-J-J_3_3_3_3", "seccion": "J.3.3.3.3",
        "titulo": "J.3.3.3.3 — Exención: R-1 y R-2 (Residencial) de máximo 3 pisos, sin importar área construida",
        "texto": "J.3.3.3.3 — Edificaciones clasificadas en los subgrupos de ocupación R-1 y R-2 (Residencial), que no tengan más de tres (3) pisos, independientemente de la magnitud del área construida.",
    },
    {
        "id": "NSR10-J-J_3_3_3_4", "seccion": "J.3.3.3.4",
        "titulo": "J.3.3.3.4 — Exención: grupo E (Especial), máximo 2 pisos",
        "texto": "J.3.3.3.4 — Edificaciones clasificadas en el grupo de ocupación E (Especial), que no tengan más de dos (2) pisos.",
    },
    {
        "id": "NSR10-J-J_3_3_3_5", "seccion": "J.3.3.3.5",
        "titulo": "J.3.3.3.5 — Exención: edificios de estacionamiento sin cerramiento en al menos 40% de fachadas (según área construida)",
        "texto": "J.3.3.3.5 — Edificios para estacionamiento que no tengan cerramiento en por lo menos el 40 % de: a) Dos (2) de sus fachadas, para edificios con menos de 3 000 m² de área construida. b) Tres (3) de sus fachadas para edificios con área construida entre 3 000 m² y 3 750 m².",
    },
    {
        "id": "NSR10-J-J_3_3_3_6", "seccion": "J.3.3.3.6",
        "titulo": "J.3.3.3.6 — Exención: grupo F (Fabril e industrial) sin explosivos/inflamables, máximo 2 pisos, <=1000 m² por piso",
        "texto": "J.3.3.3.6 — Edificaciones clasificadas en el grupo de ocupación F (Fabril e industrial), que no contengan materiales explosivos o inflamables, que no tengan más de dos (2) pisos y cuya área construida no exceda 1 000 m² por piso.",
    },
    {
        "id": "NSR10-J-J_3_3_3_7", "seccion": "J.3.3.3.7",
        "titulo": "J.3.3.3.7 — Exención: grupo F un solo piso con espacios vacíos de más de 10m alrededor, sin importar área",
        "texto": "J.3.3.3.7 — Edificaciones clasificadas en el grupo de ocupación F (Fabril e industrial), que tengan un solo piso y con espacios vacíos de más de 10 metros a todo su alrededor, independientemente de la magnitud del área construida.",
    },
    {
        "id": "NSR10-J-J_3_3_3_8", "seccion": "J.3.3.3.8",
        "titulo": "J.3.3.3.8 — Exención: estructuras de material incombustible con densidad de carga combustible <=250 MJ/m²",
        "texto": "J.3.3.3.8 — Edificaciones con estructuras de material incombustible y que tienen una densidad de carga combustible de 250 MJ/m² o menos, independientemente de su uso y altura.",
    },
    {
        "id": "NSR10-J-J_3_3_3_9", "seccion": "J.3.3.3.9",
        "titulo": "J.3.3.3.9 — Exención: grupo T (Temporal y misceláneo), cuando el uso sea estrictamente temporal",
        "texto": "J.3.3.3.9 — Edificaciones clasificadas en el grupo de ocupación T (Temporal y misceláneo), cuando su uso sea estrictamente temporal.",
    },
    {
        "id": "NSR10-J-J_3_3_3_10", "seccion": "J.3.3.3.10",
        "titulo": "J.3.3.3.10 — Incremento de área máxima exenta por espacios libres adyacentes >6m de ancho, Tabla J.3.3-3",
        "texto": "J.3.3.3.10 — Las áreas máximas construidas para clasificar las edificaciones que no requieren cuantificación de la resistencia contra el fuego según los numerales J.3.3.3.1 a J.3.3.3.6, podrán aumentarse para edificios adyacentes a calles o espacios libres de más de 6.0 m de ancho, en los porcentajes del área construida presentados en la tabla J.3.3-3 por cada metro en exceso de 6. La consideración de espacios libres no incluye lotes vacantes que puedan alojar construcciones futuras. Tabla J.3.3-3 — Porcentajes de incremento de área máxima para clasificación de edificaciones que no requieren cuantificación de la resistencia contra el fuego (Calles o espacios libres — Incremento): Adyacentes en 2 lados — 4%. Adyacentes en 3 lados — 8%. Adyacentes en 4 lados — 16%.",
    },
    {
        "id": "NSR10-J-J_3_3_3_11", "seccion": "J.3.3.3.11",
        "titulo": "J.3.3.3.11 — Exención: recintos con aberturas en al menos 2 muros que representen más del 50% del área total de dichos muros",
        "texto": "J.3.3.3.11 — Los recintos de edificios con aberturas en por lo menos dos de sus muros, que representen más del 50% del área total de dichos muros no requieren protección especial contra el fuego.",
    },
    {
        "id": "NSR10-J-J_3_3_3_12", "seccion": "J.3.3.3.12",
        "titulo": "J.3.3.3.12 — Exención: estructuras de cubierta de material incombustible a 7.5m o más de altura sobre el piso",
        "texto": "J.3.3.3.12 — Las estructuras de cubierta de material incombustible que estén a una altura sobre el piso de 7.5 m o más.",
    },
    {
        "id": "NSR10-J-J_3_3_3_13", "seccion": "J.3.3.3.13",
        "titulo": "J.3.3.3.13 — Edificios de uso mixto: se considera siempre la altura total del edificio, no solo la del uso particular",
        "texto": "J.3.3.3.13 — Cuando se trate de edificios de uso mixto, se debe considerar siempre la altura total del edificio analizado y no solamente la altura destinada a un uso particular. (a) Cuando un edificio sea de uso mixto, pero los sectores de distinto uso estén separados en planta, se aplicarán las respectivas tablas por separado para cada uno de dichos sectores y por lo tanto podrá tener distintos estándares en cada sector. (b) Cuando el edificio esté destinado a distintos usos y según la aplicación de cada uno por separado resulten estándares diferentes y no haya separación en planta para los sectores de distintos usos, se deberá satisfacer siempre el estándar más exigente.",
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
        print(f"Borrados {len(IDS_OBSOLETOS)} chunks obsoletos: {IDS_OBSOLETOS}")


if __name__ == "__main__":
    main()
