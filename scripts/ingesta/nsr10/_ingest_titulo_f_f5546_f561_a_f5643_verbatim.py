"""
Ingesta verbatim de NSR-10 Título F.5.5.4.6 (cierra F.5.5 completo) y
F.5.6.1 a F.5.6.4.3 (Diseño Estático de Uniones -- Estructuras de
Aluminio: generalidades, uniones remachadas/empernadas -- consideraciones
de diseño y geométricas, resistencia de sujetadores individuales
diferentes de pernos de alta resistencia a fricción). Fase 6 del plan de
cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-520 a F-523), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.5.4-4 (sección efectiva de
rigidizador) y F.5.5.4-5 (diagramas de interacción momento-cortante) son
diagramas/curvas visuales -- solo se transcribe la definición textual de
las variables que las acompañan (MRS, MRF, VRS, VRW), no la geometría de
las curvas.

Uso: python _ingest_titulo_f_f5546_f561_a_f5643_verbatim.py
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

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

TABLA_F_5_6_4_1 = (
    "Tabla F.5.6.4-1 — Esfuerzo límite para sujetadores de aluminio pf, por tipo de sujetador, aleación, condición, "
    "método de colocación, diámetro (mm) y pf (kgf/mm²). "
    "Pernos: aleación 6082 T6, sin condición, diámetro menor o igual a 6 mm, pf=16.5; mismo 6082 T6, diámetro 6 a "
    "12 mm, pf=17.5; aleación 6061 T8, diámetro menor o igual a 12 mm, pf=17.5; aleación 5056A H24, diámetro menor "
    "o igual a 12 mm, pf=17.5. "
    "Remaches: aleación 5154A condición O/F, colocación en frío o caliente, diámetro menor o igual a 25 mm, "
    "pf=12.0; aleación 5154A H22, colocación en frío, diámetro menor o igual a 25 mm, pf=14.0; aleación 6082 T4, "
    "colocación en frío, diámetro menor o igual a 25 mm, pf=11.0; aleación 6082 T6, colocación en frío, diámetro "
    "menor o igual a 25 mm, pf=16.5; aleación 5056A condición O/F, colocación en frío o caliente, diámetro menor o "
    "igual a 25 mm, pf=14.5; aleación 5056A H22, colocación en frío, diámetro menor o igual a 25 mm, pf=15.5."
)

CHUNKS = [
    {
        "id": "NSR10-F-F_5_5_4_6", "seccion": "F.5.5.4.6",
        "titulo": "F.5.5.4.6 — Vigas sujetas a momento y cortante combinados: variables de los diagramas de interacción (MRS/MRF/VRS/VRW), Figuras F.5.5.4-4/5 (cierra F.5.5)",
        "texto": (
            "Figura F.5.5.4-4 — Sección efectiva de rigidizador: tres configuraciones esquemáticas (rigidizador "
            "plano, rigidizador en cruz, rigidizador tipo sombrero) mostrando el ancho be de lámina de alma "
            "efectiva y la distancia b1 desde el punto de fijación. Diagrama visual, no se transcribe la geometría. "
            "F.5.5.4.6 — VIGAS SUJETAS A MOMENTO Y CORTANTE COMBINADOS — Las figuras F.5.5.4-5 (a) y (b) muestran "
            "esquemáticamente la forma del diagrama de interacción momento-cortante para vigas ensambladas "
            "cubriendo: vanos incapaces de sostener un campo tensionado; vanos con acción de campo tensionado. "
            "Tales diagramas pueden construirse para cualquier vano dado entre rigidizadores transversales para "
            "determinar la resistencia de diseño a momento MRSO, en presencia de una fuerza cortante coincidente V "
            "(generada bajo carga mayorada). La notación es la siguiente: "
            "Figura F.5.5.4-5 — Diagramas de interacción esquemáticos para vigas ensambladas: (a) Sin campo "
            "tensionado — eje vertical momento (MRSO en la parte superior, escalones en MRS y MRF), eje horizontal "
            "fuerza cortante V (con marcas en 0.5·VRS y VRS). (b) Con campo tensionado — mismo tipo de eje "
            "vertical, eje horizontal V con marcas en 0.5·VRW, VRW y VRS. Ambos son diagramas visuales de "
            "interacción, no se transcribe la geometría de las curvas — solo la definición textual de sus "
            "variables: MRS = resistencia de diseño a momento en ausencia de cortante (véanse F.5.5.4.1 y el "
            "literal (b) de F.5.5.4.3). MRF = valor reducido de MRS para las aletas por sí solas, omitiendo el "
            "alma. VRS = resistencia de diseño a fuerza cortante (véanse F.5.5.4.2 y F.5.5.4.3). VRW = valor "
            "reducido de VRS obtenido haciendo m=0."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_1", "seccion": "F.5.6.1",
        "titulo": "F.5.6 — Diseño Estático de Uniones. F.5.6.1 — Generalidades: tipos de sujetador, tipos de conexión (a/b/c), estados límite, sujetadores para inversión de carga",
        "texto": (
            "F.5.6 — DISEÑO ESTATICO DE UNIONES. "
            "F.5.6.1 — GENERALIDADES — En esta sección se trata el diseño de uniones mediante sujetadores, "
            "adhesivos o soldadura. Se discuten los siguientes tipos de sujetador: remaches, pernos negros, pernos "
            "de precisión, pernos de alta resistencia para trabajo por fricción, conectores especiales y pasadores. "
            "Se define la resistencia de diseño de uniones soldadas con soldadura a tope o de filete. El diseño de "
            "uniones entre elementos colados o forjados se debe hacer conjuntamente con el fabricante. "
            "Los siguientes tipos de conexión se denominan uniones: "
            "(a) Conexiones entre miembros estructurales, por ejemplo, viga a columna. "
            "(b) Conexiones entre elementos de un miembro ensamblado, por ejemplo, almas a aletas, empalmes. "
            "(c) Conexiones entre detalles localizados y miembros estructurales, por ejemplo, ménsula a viga, "
            "anillos y abrazaderas de miembros a tensión. "
            "Todos los tipos de conexión deben diseñarse para cumplir con los estados límite de resistencia y "
            "fatiga. No se requiere revisión para estados límite de servicio, excepto para uniones con pasadores en "
            "estructuras que son frecuentemente armadas y desarmadas, para uniones en las que las deflexiones son "
            "críticas o en uniones con pernos a fricción en las que se debe evitar el deslizamiento. La carga "
            "mayorada sobre una unión debe calcularse usando los coeficientes de carga dados en F.5.3. Los "
            "sujetadores sometidos a inversión de cargas deben ser pernos de precisión o pernos de barril "
            "giratorio, remaches sólidos, pernos de alta resistencia a fricción, o conectores especiales que "
            "impidan el movimiento. "
            "Los remaches huecos y otros conectores especiales, pueden usarse siempre que su comportamiento haya "
            "sido satisfactoriamente demostrado mediante ensayos u otros medios. En su diseño y espaciamiento debe "
            "haber cooperación entre el diseñador y el fabricante. Se debe demostrar previamente, mediante ensayos "
            "u otros medios, el comportamiento del material insertado roscado para sujetadores de acero que deban "
            "ser usados en cualquier elemento roscado de aluminio en una unión desmontable."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_2_1_a_3", "seccion": "F.5.6.2",
        "titulo": "F.5.6.2 — Uniones remachadas y empernadas, consideraciones de diseño: grupos de sujetadores (.2.1), efecto de áreas en capas sucesivas (.2.2), uniones largas (.2.3)",
        "texto": (
            "F.5.6.2 — UNIONES REMACHADAS Y EMPERNADAS: CONSIDERACIONES DE DISEÑO — Las uniones usando remaches o "
            "pernos deben diseñarse de modo que, bajo carga mayorada, la acción de carga en cualquier posición de "
            "sujetador no exceda la resistencia de diseño del sujetador allí localizado. "
            "F.5.6.2.1 — Grupos de sujetadores — Los grupos de remaches, pernos o conectores especiales, conocidos "
            "colectivamente como \"sujetadores\", que forman una conexión, deben diseñarse sobre la base de una "
            "suposición realista de la distribución de las fuerzas internas, observando la rigidez relativa. Es "
            "esencial que se mantenga el equilibrio con las cargas externas mayoradas. "
            "F.5.6.2.2 — Efecto de las áreas de sección transversal en capas sucesivas — El diseño de las capas "
            "sucesivas en secciones que contienen agujeros para sujetadores debe basarse en las áreas netas "
            "mínimas, excepto para remaches a compresión. En ciertas uniones empernadas a fricción, el estado "
            "límite es determinado por la capacidad a fricción de la unión y, en estas circunstancias, el diseño "
            "debe basarse en las áreas brutas mínimas. "
            "F.5.6.2.3 — Uniones largas — Cuando la longitud de una unión, medida entre centros de sujetadores "
            "finales, es más de 15 df (donde df es el diámetro nominal del sujetador), o cuando el número de "
            "sujetadores en esta dirección es mayor de cinco, el diseñador debe tomar en cuenta la reducción en la "
            "resistencia promedio de los sujetadores individuales debida a una distribución irregular de la carga "
            "entre ellos."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_3_1_2", "seccion": "F.5.6.3.1",
        "titulo": "F.5.6.3 — Uniones remachadas/empernadas, consideraciones geométricas. F.5.6.3.1 — Espaciamiento mínimo (2.5d/3.0d). F.5.6.3.2 — Espaciamiento máximo (16t/200mm, etc.)",
        "texto": (
            "F.5.6.3 — UNIONES REMACHADAS Y EMPERNADAS: CONSIDERACIONES GEOMETRICAS Y OTRAS CONSIDERACIONES "
            "GENERALES. "
            "F.5.6.3.1 — Espaciamiento mínimo — El espaciamiento entre centros de pernos y remaches en la dirección "
            "de la transmisión de la carga no debe ser menor que 2.5 veces el diámetro del perno o remache, en "
            "situaciones extremas no deberá ser menor de 2.2 veces el diámetro, siempre que la tensión de "
            "aplastamiento se reduzca adecuadamente. El espaciamiento entre centros de pernos y remaches medido "
            "perpendicularmente a la dirección de transmisión de la carga no debe ser menor que 3.0 veces el "
            "diámetro del perno o remache, en situaciones extremas no deberá ser menor de 2.4 veces el diámetro, "
            "siempre que la tensión de aplastamiento se reduzca. Para los pernos de alta resistencia a fricción se "
            "permite un espaciamiento menor limitado por el tamaño de la arandela, la cabeza de los pernos y la "
            "llave de pernos, y la necesidad de cumplir con los estados límite. "
            "F.5.6.3.2 — Espaciamiento máximo — El espaciamiento entre pernos o remaches adyacentes sobre una línea "
            "en la dirección del esfuerzo en miembros a tensión, no debe exceder 16t o 200 mm, donde t es el "
            "espesor de la capa exterior más delgada. En miembros a compresión o cortante, no debe exceder 14t o "
            "200 mm. Adicionalmente, el espaciamiento entre pernos o remaches adyacentes sobre una línea adyacente "
            "y paralela a un borde de una capa exterior, no debe exceder 8t o 100 mm. Si los remaches o pernos "
            "están escalonados sobre líneas adyacentes, y las líneas no están separadas más de 75 mm, los límites "
            "anteriores pueden incrementarse 50%. "
            "En cualquier caso, el espaciamiento entre remaches o pernos adyacentes, escalonados o no, no debe "
            "exceder 32t o 300 mm en miembros a tensión y 20t o 300 mm en miembros a compresión o cortante. "
            "Estas recomendaciones se aplican únicamente a uniones, entre láminas planas, traslapadas y con "
            "cubreplaca. El espaciamiento de pernos y remaches en uniones de campana y espigo, uniones entre "
            "miembros tubulares y entre partes de espesor muy desigual, debe ser determinado considerando la "
            "geometría local y la carga sobre la unión."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_3_3_a_6", "seccion": "F.5.6.3.3",
        "titulo": "F.5.6.3.3 — Distancia al borde (1.5d). F.5.6.3.4 — Carga fluctuante. F.5.6.3.5 — Empaquetadura. F.5.6.3.6 — Avellanado (2/3 de resistencia)",
        "texto": (
            "F.5.6.3.3 — Distancia al borde — La distancia al borde, medida desde el centro del remache o perno, "
            "para bordes extruídos, laminados o acabados a máquina, no debe ser menor de 1.5 veces el diámetro del "
            "perno o remache. Si, sobre el lado de apoyo, la distancia al borde es menor que dos veces el diámetro, "
            "la capacidad por aplastamiento debe reducirse (véase F.5.6.4.4). Si los bordes son cortados, los "
            "límites anteriores se pueden incrementar 3 mm. "
            "La distancia al borde lateral no debe exceder la máxima necesaria para poder cumplir los requisitos de "
            "pandeo local de un elemento exterior. Este requisito no se aplica a elementos de fijación que unan los "
            "componentes traccionados. La distancia al extremo frontal no se verá afectada por este requisito. "
            "F.5.6.3.4 — Pernos sometidos a carga fluctuante — Los pernos que transmitan cargas fluctuantes, "
            "diferentes de cargas de viento, deben ser de precisión o de alta resistencia a fricción. "
            "F.5.6.3.5 — Empaquetadura — Cuando los sujetadores soportan cortante a través de un empaque, se debe "
            "tomar en cuenta una reducción de la resistencia de diseño si el espesor del empaque excede el 25% del "
            "diámetro del sujetador o el 50% del espesor de la capa. "
            "F.5.6.3.6 — Avellanado — La mitad de la altura de cualquier avellanado de un remache o perno debe "
            "despreciarse cuando se calcula su longitud en aplastamiento. No es necesaria ninguna reducción para "
            "remaches y pernos a cortante. La resistencia de diseño a tensión axial de un perno o remache avellanado "
            "debe tomarse como dos tercios de la de un perno o remache plano del mismo diámetro. La profundidad de "
            "avellanado no debe exceder el espesor de la parte avellanada menos 4 mm, de otro modo, el "
            "comportamiento debe demostrarse mediante ensayos."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_3_7_a_9", "seccion": "F.5.6.3.7",
        "titulo": "F.5.6.3.7 — Remaches largos (5 veces diámetro agujero). F.5.6.3.8 — Arandelas/aseguramiento. F.5.6.3.9 — Intersecciones (ejes centroidales concurrentes)",
        "texto": (
            "F.5.6.3.7 — Remaches largos — La longitud de agarre de los remaches no debe exceder el valor de cinco "
            "veces el diámetro del agujero. "
            "F.5.6.3.8 — Arandelas y dispositivos de aseguramiento — Deben usarse dispositivos de aseguramiento "
            "siempre que existan tuercas susceptibles de aflojarse debido a vibración o fluctuación de esfuerzos. "
            "F.5.6.3.9 — Intersecciones — Los miembros que convergen en una unión deben ser normalmente dispuestos "
            "de modo que sus ejes centroidales se encuentren en un punto. En el caso de estructuras empernadas "
            "compuestas de ángulos y secciones en T, las líneas de colocación de los pernos pueden ser usadas en "
            "lugar del eje centroidal. "
            "Cuando exista excentricidad en una unión, deberá tenerse en cuenta, excepto en el caso particular de "
            "estructuras en las que se haya demostrado que no es necesaria dicha consideración."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_4_1", "seccion": "F.5.6.4.1",
        "titulo": "F.5.6.4 — Resistencia de sujetadores individuales (no pernos de alta resistencia a fricción). F.5.6.4.1 — Esfuerzos límite: acero (a), acero inoxidable (b), aluminio (c) con Tabla F.5.6.4-1",
        "texto": (
            "F.5.6.4 — RESISTENCIA DE DISEÑO DE REMACHES Y PERNOS INDIVIDUALES DIFERENTES DE LOS PERNOS DE ALTA "
            "RESISTENCIA A FRICCION. "
            "F.5.6.4.1 — Esfuerzos límite — El esfuerzo límite pf para remaches sólidos y pernos se define como "
            "sigue: "
            "(a) Sujetadores de acero — pf es el esfuerzo de fluencia mínimo garantizado para el lote de pernos o "
            "remaches. "
            "(b) Pernos y remaches de acero inoxidable — pf es el menor de 0.5(f0.2 + fu) y 1.2 f0.2. "
            "(c) Pernos y remaches de aluminio — los valores de pf para las aleaciones de aluminio de la tabla "
            "F.5.2.2-3, se dan en la tabla F.5.6.4-1. Puede usarse, cuando esté disponible, el valor de la "
            "resistencia a cortante obtenido mediante ensayos sobre el perno o remache en la condición de como "
            "colocado. En este caso, el valor de αs en la expresión de VRS en F.5.6.4.2 debe reducirse de 0.6 a "
            "0.33. "
            + TABLA_F_5_6_4_1
        ),
    },
    {
        "id": "NSR10-F-F_5_6_4_2", "seccion": "F.5.6.4.2",
        "titulo": "F.5.6.4.2 — Cortante: VRS=φ·αs·pf·Aes·K1 (ecuación F.5.6.4-1), áreas para pernos/remaches, K1 por tipo",
        "texto": (
            "F.5.6.4.2 — Cortante — La resistencia de diseño (VRS) de un solo remache o perno sometido a cortante "
            "simple se toma como: VRS = φ αs pf Aes K1  (F.5.6.4-1). "
            "Donde: pf = definido en F.5.6.4.1. αs = 0.6 para pernos y remaches de aluminio; 0.7 para pernos y "
            "remaches de acero. φ = coeficiente de reducción de capacidad, igual a 0.8 para todos los pernos y "
            "remaches, esto es, aluminio, acero y acero inoxidable (véase la tabla F.5.3.3-1). "
            "Para pernos: Aes = Atb (área de esfuerzo de la parte roscada del perno), cuando el plano de corte pasa "
            "por esa área, o Aes = ASH (área del vástago), cuando el plano de corte pasa por el vástago. "
            "Para remaches: Aes = Ah (área del agujero). K1 = 1.0 para remaches. K1 = 0.95 para pernos de "
            "precisión. K1 = 0.85 para pernos de holgura normal."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_4_3", "seccion": "F.5.6.4.3",
        "titulo": "F.5.6.4.3 — Tensión axial: PRT=φ·a·pf·Atb (ecuación F.5.6.4-2), a=1.0 acero/inox vs. a=0.6 aluminio, remaches de aluminio no recomendados a tensión",
        "texto": (
            "F.5.6.4.3 — Tensión axial — La resistencia de diseño, PRT, de un solo sujetador sometido a tensión "
            "axial se toma como: PRT = φ a pf Atb  (F.5.6.4-2). "
            "Donde: pf, Atb, φ tal como se definen en F.5.6.4.1 y F.5.6.4.2. a = 1.0 para pernos y remaches de "
            "acero y acero inoxidable. a = 0.6 para pernos de aluminio. "
            "No se recomienda el uso de remaches de aluminio a tensión."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
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


if __name__ == "__main__":
    main()
