"""
Inserta el núcleo verbatim real del Capítulo IV (Análisis Estructural,
Artículos 24-30) de la norma E.030 de Perú en peru_e030_chunks. Cuarto
bloque del corpus, después de los Capítulos I-III (ver los otros
insert_capituloN_*.py -- mismo texto oficial del MVCS, misma base legal de
citación verbatim, Art. 9(b) del Decreto Legislativo N° 822).

Es el capítulo más denso en fórmulas de toda la norma: fuerza cortante en
la base (V = Z·U·C·S/R·P), distribución de fuerza sísmica en altura,
período fundamental de vibración (T = hn/CT, con tabla de CT por sistema
estructural), análisis dinámico modal espectral (aceleración espectral Sa,
combinación cuadrática completa CQC), y análisis dinámico tiempo-historia.

Nota de transcripción honesta (verificar antes de tratar como definitivo):
el numeral 29.4.1 del PDF fuente parece referenciar "el artículo 25" para
el valor de fuerza cortante mínima, cuando por contexto normativo (fuerza
cortante calculada, no el modelo de análisis) se esperaría una referencia
al artículo 28 (Análisis Estático, que es donde se calcula V). Se
transcribe TAL CUAL aparece en el documento fuente -- no se "corrige" en
silencio una posible errata sin confirmar contra una segunda fuente o
edición oficial más nítida. Marcado explícitamente en el chunk
correspondiente para que quien lo use sepa que ese número de artículo
específico no está 100% verificado.

Uso: python scripts/ingesta/peru_e030/insert_capitulo4_analisis_estructural.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo IV — Análisis Estructural"

CHUNKS = [
    {
        "id": "E030-CAP4-ART24-CONSIDERACIONES_GENERALES",
        "seccion": "Artículo 24",
        "titulo": "Consideraciones Generales para el Análisis (direcciones ortogonales, solicitaciones verticales)",
        "texto": """Artículo 24.- Consideraciones Generales para el Análisis

24.1. Para estructuras regulares, el análisis puede hacerse considerando que el total de la fuerza sísmica actúa independientemente en dos direcciones ortogonales predominantes. Para estructuras irregulares se supone que la acción sísmica ocurre en la dirección que resulte más desfavorable para el diseño.

24.2. Las solicitaciones sísmicas verticales se consideran en el diseño de los elementos verticales, en elementos horizontales de gran luz, en elementos post o pre tensados y en los voladizos o salientes de un edificio. Se considera que la fuerza sísmica vertical actúa en los elementos simultáneamente con la fuerza sísmica horizontal y en el sentido más desfavorable para el análisis.""",
    },
    {
        "id": "E030-CAP4-ART25-MODELOS_ANALISIS",
        "seccion": "Artículo 25",
        "titulo": "Modelos para el Análisis (diafragmas rígidos, tabiquería, interacción de muros)",
        "texto": """Artículo 25.- Modelos para el Análisis

25.1. El modelo para el análisis considera una distribución espacial de masas y rigideces que sean adecuadas para representar los aspectos más significativos del comportamiento dinámico de la estructura.

25.2. Para propósitos de esta Norma, las estructuras de concreto armado y albañilería pueden ser analizadas considerando las inercias de las secciones brutas, ignorando la fisuración y el refuerzo.

25.3. Para edificios en los que se pueda razonablemente suponer que los sistemas de piso funcionan como diafragmas rígidos, se puede usar un modelo con masas concentradas y tres grados de libertad por diafragma, asociados a dos componentes ortogonales de traslación horizontal y una rotación. En tal caso, las deformaciones de los elementos se compatibilizan mediante la condición de diafragma rígido y la distribución en planta de las fuerzas horizontales se hace en función a las rigideces de los elementos resistentes.

25.4. Se verifica que los diafragmas tengan la rigidez y resistencia suficiente para asegurar la distribución antes mencionada, en caso contrario, se toma en cuenta su flexibilidad para la distribución de las fuerzas sísmicas.

25.5. El modelo estructural incluye la tabiquería que no esté debidamente aislada.

25.6. Para los pisos que no constituyan diafragmas rígidos, los elementos resistentes son diseñados para las fuerzas horizontales que directamente les corresponde.

25.7. En los edificios cuyos elementos estructurales predominantes sean muros, se considera un modelo que tome en cuenta la interacción entre muros en direcciones perpendiculares (muros en H, muros en T y muros en L).""",
    },
    {
        "id": "E030-CAP4-ART26-ESTIMACION_PESO",
        "seccion": "Artículo 26",
        "titulo": "Estimación del Peso (P) — porcentaje de carga viva según categoría de edificación",
        "texto": """Artículo 26.- Estimación del Peso (P)

El peso (P) se calcula adicionando a la carga permanente y total de la edificación un porcentaje de la carga viva o sobrecarga que se determina de la siguiente manera: a) En edificaciones de las categorías A y B, se toma el 50% de la carga viva. b) En edificaciones de la categoría C, se toma el 25% de la carga viva. c) En depósitos, se toma el 80% del peso total que es posible almacenar. d) En azoteas y techos en general se toma el 25% de la carga viva. e) En estructuras de tanques, silos y estructuras similares se considera el 100% de la carga que puede contener.""",
    },
    {
        "id": "E030-CAP4-ART27-PROCEDIMIENTOS_ANALISIS",
        "seccion": "Artículo 27",
        "titulo": "Procedimientos de Análisis Sísmico (estático, dinámico modal espectral, tiempo-historia complementario)",
        "texto": """Artículo 27.- Procedimientos de Análisis Sísmico

27.1. Se utiliza uno de los procedimientos siguientes: a) Análisis estático o de fuerzas estáticas equivalentes (artículo 28). b) Análisis dinámico modal espectral (artículo 29).

27.2. El análisis se hace considerando un modelo de comportamiento lineal y elástico con las solicitaciones sísmicas reducidas.

27.3. El procedimiento de análisis dinámico tiempo-historia, descrito en el artículo 30, puede usarse con fines de verificación, pero en ningún caso es exigido como sustituto de los procedimientos indicados en los artículos 28 y 29.""",
    },
    {
        "id": "E030-CAP4-ART28_1_2-GENERALIDADES_CORTANTE_BASE",
        "seccion": "Artículo 28.1 y 28.2",
        "titulo": "Análisis Estático — Generalidades y Fuerza Cortante en la Base (fórmula V = Z·U·C·S/R·P)",
        "texto": """Artículo 28.- Análisis Estático o de Fuerzas Estáticas Equivalentes

28.1. Generalidades. 28.1.1. Este método representa las solicitaciones sísmicas mediante un conjunto de fuerzas actuando en el centro de masas de cada nivel de la edificación. 28.1.2. Pueden analizarse mediante este procedimiento todas las estructuras regulares o irregulares ubicadas en la zona sísmica 1. En las otras zonas sísmicas puede emplearse este procedimiento para las estructuras clasificadas como regulares, según el artículo 19, de no más de 30 m de altura, y para las estructuras de muros portantes de concreto armado y albañilería armada o confinada de no más de 15 m de altura, aun cuando sean irregulares.

28.2. Fuerza Cortante en la Base. 28.2.1. La fuerza cortante total en la base de la estructura, correspondiente a la dirección considerada, se determina por la siguiente expresión: V = (Z · U · C · S / R) · P. 28.2.2. El valor de C/R no se considera menor que: C/R ≥ 0,11.""",
    },
    {
        "id": "E030-CAP4-ART28_3-DISTRIBUCION_ALTURA",
        "seccion": "Artículo 28.3",
        "titulo": "Distribución de la Fuerza Sísmica en Altura (fórmula Fi = αi·V, exponente k)",
        "texto": """28.3. Distribución de la Fuerza Sísmica en Altura. 28.3.1. Las fuerzas sísmicas horizontales en cualquier nivel i, correspondientes a la dirección considerada, se calculan mediante: Fi = αi · V, donde αi = Pi·(hi)^k / (suma de Pj·(hj)^k para j=1 hasta n).

28.3.2. Donde n es el número de pisos del edificio, k es un exponente relacionado con el período fundamental de vibración de la estructura (T), en la dirección considerada, que se calcula de acuerdo a: a) Para T menor o igual a 0,5 segundos: k = 1,0. b) Para T mayor que 0,5 segundos: k = (0,75 + 0,5·T) ≤ 2,0.""",
    },
    {
        "id": "E030-CAP4-ART28_4-PERIODO_FUNDAMENTAL",
        "seccion": "Artículo 28.4",
        "titulo": "Período Fundamental de Vibración (T = hn/CT, tabla de CT=35/45/60 por sistema, fórmula alternativa de Rayleigh)",
        "texto": """28.4. Período Fundamental de Vibración. 28.4.1. El período fundamental de vibración para cada dirección se estima con la siguiente expresión: T = hn / CT.

Valores de CT: CT = 35 para edificios cuyos elementos resistentes en la dirección considerada sean únicamente: a) Pórticos de concreto armado sin muros de corte. b) Pórticos dúctiles de acero con uniones resistentes a momentos, sin arriostramiento. CT = 45 para edificios cuyos elementos resistentes sean: a) Pórticos de concreto armado con muros en las cajas de ascensores y escaleras. b) Pórticos de acero arriostrados. CT = 60 para edificios de albañilería y para todos los edificios de concreto armado duales, de muros estructurales, y muros de ductilidad limitada.

28.4.2. Alternativamente puede usarse la siguiente expresión (fórmula de Rayleigh): T = 2π · raíz cuadrada de [(suma de Pi·di², i=1 a n) / (g · suma de fi·di, i=1 a n)]. Donde fi es la fuerza lateral en el nivel i correspondiente a una distribución en altura semejante a la del primer modo en la dirección de análisis, y di es el desplazamiento lateral del centro de masa del nivel i en traslación pura (restringiendo los giros en planta) debido a las fuerzas fi. Los desplazamientos se calculan suponiendo comportamiento lineal elástico de la estructura y, para el caso de estructuras de concreto armado y de albañilería, considerando las secciones sin fisurar.

28.4.3. Cuando el análisis no considere la rigidez de los elementos no estructurales, el período fundamental T se toma como 0,85 del valor obtenido con la fórmula precedente.""",
    },
    {
        "id": "E030-CAP4-ART28_5_6-EXCENTRICIDAD_FUERZAS_VERTICALES",
        "seccion": "Artículo 28.5 y 28.6",
        "titulo": "Excentricidad Accidental (momento torsor Mti) y Fuerzas Sísmicas Verticales",
        "texto": """28.5. Excentricidad Accidental. Para estructuras con diafragmas rígidos, se supone que la fuerza en cada nivel (Fi) actúa en el centro de masas del nivel respectivo y se considera además de la excentricidad propia de la estructura el efecto de excentricidades accidentales (en cada dirección de análisis) como se indica a continuación: a) En el centro de masas de cada nivel, además de la fuerza lateral estática actuante, se aplica un momento torsor accidental (Mti) que se calcula como: Mti = ± Fi · ei. Para cada dirección de análisis, la excentricidad accidental en cada nivel (ei), se considera como 0,05 veces la dimensión del edificio en la dirección perpendicular a la dirección de análisis. b) Se puede suponer que las condiciones más desfavorables se obtienen considerando las excentricidades accidentales con el mismo signo en todos los niveles. Se consideran únicamente los incrementos de las fuerzas horizontales no así las disminuciones.

28.6. Fuerzas Sísmicas Verticales. 28.6.1. La fuerza sísmica vertical se considera como una fracción del peso igual a 2/3 · Z · U · S. 28.6.2. En elementos horizontales de grandes luces, incluyendo volados, se requiere un análisis dinámico con los espectros definidos en el numeral 29.2.""",
    },
    {
        "id": "E030-CAP4-ART29_1_2-MODOS_ACELERACION_ESPECTRAL",
        "seccion": "Artículo 29.1 y 29.2",
        "titulo": "Análisis Dinámico Modal Espectral — Modos de Vibración y Aceleración Espectral (fórmula Sa = Z·U·C·S/R·g)",
        "texto": """Artículo 29.- Análisis Dinámico Modal Espectral

Cualquier estructura puede ser diseñada usando los resultados de los análisis dinámicos por combinación modal espectral según lo especificado en este numeral.

29.1. Modos de Vibración. 29.1.1. Los modos de vibración pueden determinarse por un procedimiento de análisis que considere apropiadamente las características de rigidez y la distribución de las masas. 29.1.2. En cada dirección se consideran aquellos modos de vibración cuya suma de masas efectivas sea por lo menos el 90% de la masa total, pero toma en cuenta por lo menos los tres primeros modos predominantes en la dirección de análisis.

29.2. Aceleración Espectral. 29.2.1. Para cada una de las direcciones horizontales analizadas se utiliza un espectro inelástico de pseudo-aceleraciones definido por: Sa = (Z · U · C · S / R) · g. 29.2.2. Para el análisis en la dirección vertical puede usarse un espectro con valores iguales a los 2/3 del espectro empleado para las direcciones horizontales, considerando los valores de C definidos en el artículo 14, excepto para la zona de períodos muy cortos (T < 0,2 TP) en la que se considera: C = 1 + 7,5·(T/TP).""",
    },
    {
        "id": "E030-CAP4-ART29_3-CRITERIOS_COMBINACION",
        "seccion": "Artículo 29.3",
        "titulo": "Criterios de Combinación modal — combinación cuadrática completa CQC y expresión alternativa 25%/75%",
        "texto": """29.3. Criterios de Combinación. 29.3.1. Mediante los criterios de combinación que se indican, se puede obtener la respuesta máxima elástica esperada (r) tanto para las fuerzas internas en los elementos componentes de la estructura, como para los parámetros globales del edificio como fuerza cortante en la base, cortantes de entrepiso, momentos de volteo, desplazamientos totales y relativos de entrepiso.

29.3.2. La respuesta máxima elástica esperada (r) correspondiente al efecto conjunto de los diferentes modos de vibración empleados (ri) puede determinarse usando la combinación cuadrática completa (CQC) de los valores calculados para cada modo: r = raíz cuadrada de (suma doble de ri·ρij·rj).

29.3.3. Donde r representa las respuestas modales, desplazamientos o fuerzas, los coeficientes de correlación están dados por: ρij = 8β²(1+λ)λ^(3/2) / [(1-λ²)² + 4β²λ(1+λ)²], donde λ = ωj/ωi. β es la fracción del amortiguamiento crítico, que se puede suponer constante para todos los modos igual a 0,05. ωi, ωj son las frecuencias angulares de los modos i, j.

29.3.4. Alternativamente, la respuesta máxima puede estimarse mediante la siguiente expresión: r = 0,25 · (suma de |ri|) + 0,75 · raíz cuadrada de (suma de ri², i=1 a m).""",
    },
    {
        "id": "E030-CAP4-ART29_4_5-CORTANTE_MINIMA_EXCENTRICIDAD",
        "seccion": "Artículo 29.4 y 29.5",
        "titulo": "Fuerza Cortante Mínima (80%/90% del análisis estático) y Excentricidad Accidental por torsión",
        "texto": """29.4. Fuerza Cortante Mínima. 29.4.1. Para cada una de las direcciones consideradas en el análisis, la fuerza cortante en el primer entrepiso del edificio no puede ser menor que el 80% del valor calculado según el artículo 25 [NOTA DE TRANSCRIPCIÓN: el documento fuente dice literalmente "artículo 25" en este numeral; por contexto normativo (se refiere al cortante calculado por análisis estático) se esperaría una referencia al artículo 28 -- no se corrige en silencio, se deja anotado para verificar contra una segunda fuente antes de tratarlo como definitivo] para estructuras regulares, ni menor que el 90% para estructuras irregulares. 29.4.2. Si fuera necesario incrementar el cortante para cumplir los mínimos señalados, se escalan proporcionalmente todos los otros resultados obtenidos, excepto los desplazamientos.

29.5. Excentricidad Accidental (Efectos de Torsión). La incertidumbre en la localización de los centros de masa en cada nivel, se considera mediante una excentricidad accidental perpendicular a la dirección del sismo igual a 0,05 veces la dimensión del edificio en la dirección perpendicular a la dirección de análisis. En cada caso se considera el signo más desfavorable.""",
    },
    {
        "id": "E030-CAP4-ART30_1-REGISTROS_ACELERACION",
        "seccion": "Artículo 30.1",
        "titulo": "Análisis Dinámico Tiempo-Historia — Registros de Aceleración (mínimo 3 conjuntos, escalado SRSS)",
        "texto": """Artículo 30.- Análisis Dinámico Tiempo-Historia

El análisis dinámico tiempo-historia puede emplearse como un procedimiento complementario a los especificados en los artículos 28 y 29. En este tipo de análisis se utiliza un modelo matemático de la estructura que considere directamente el comportamiento histerético de los elementos, determinándose la respuesta frente a un conjunto de aceleraciones del terreno mediante integración directa de las ecuaciones de equilibrio.

30.1. Registros de Aceleración. 30.1.1. Para el análisis se usan como mínimo tres conjuntos de registros de aceleraciones del terreno, cada uno de los cuales incluye dos componentes en direcciones ortogonales. 30.1.2. Cada conjunto de registros de aceleraciones del terreno consiste en un par de componentes de aceleración horizontal, elegidas y escaladas de eventos individuales. Las historias de aceleración son obtenidas de eventos cuyas magnitudes, distancia a las fallas, y mecanismos de fuente sean consistentes con el máximo sismo considerado. Cuando no se cuente con el número requerido de registros apropiados, se pueden usar registros simulados para alcanzar el número total requerido. 30.1.3. Para cada par de componentes horizontales de movimiento del suelo, se construye un espectro de pseudo aceleraciones tomando la raíz cuadrada de la suma de los cuadrados (SRSS) de los valores espectrales calculados para cada componente por separado, con 5% de amortiguamiento. Ambas componentes se escalan por un mismo factor, de modo que en el rango de períodos entre 0,2T y 1,5T (siendo T el período fundamental), el promedio de los valores espectrales SRSS obtenidos para los distintos juegos de registros no sea menor que la ordenada correspondiente del espectro de diseño, calculada según el numeral 29.2 con R=1. 30.1.4. Para la generación de registros simulados se consideran los valores de C definidos en el artículo 14, excepto para la zona de períodos muy cortos (T < 0,2 TP) en la que se considera: C = 1 + 7,5·(T/TP).""",
    },
    {
        "id": "E030-CAP4-ART30_2-MODELO_ANALISIS",
        "seccion": "Artículo 30.2",
        "titulo": "Análisis Dinámico Tiempo-Historia — Modelo para el Análisis (comportamiento histerético, amortiguamiento)",
        "texto": """30.2. Modelo para el Análisis. 30.2.1. El modelo matemático representa correctamente la distribución espacial de masas en la estructura. 30.2.2. El comportamiento de los elementos es modelado de modo consistente con resultados de ensayos de laboratorio y toma en cuenta la fluencia, la degradación de resistencia, la degradación de rigidez, el estrechamiento de los lazos histeréticos, y todos los aspectos relevantes del comportamiento estructural indicado por los ensayos. 30.2.3. La resistencia de los elementos es obtenida en base a los valores esperados sobre resistencia del material, endurecimiento por deformación y degradación de resistencia por la carga cíclica. 30.2.4. Se permite suponer propiedades lineales para aquellos elementos en los que el análisis demuestre que permanecen en el rango elástico de respuesta. 30.2.5. Se admite considerar un amortiguamiento viscoso equivalente con un valor máximo del 5% del amortiguamiento crítico, además de la disipación resultante del comportamiento histerético de los elementos. 30.2.6. Se puede suponer que la estructura está empotrada en la base, o alternativamente considerar la flexibilidad del sistema de cimentación si fuera pertinente.""",
    },
    {
        "id": "E030-CAP4-ART30_3-TRATAMIENTO_RESULTADOS",
        "seccion": "Artículo 30.3",
        "titulo": "Análisis Dinámico Tiempo-Historia — Tratamiento de Resultados (promedios con 7+ registros, límites de distorsión y resistencia)",
        "texto": """30.3. Tratamiento de Resultados. 30.3.1. En caso se utilicen por lo menos siete juegos de registros del movimiento del suelo, las fuerzas de diseño, las deformaciones en los elementos y las distorsiones de entrepiso se evalúan a partir de los promedios de los correspondientes resultados máximos obtenidos en los distintos análisis. Si se utilizaran menos de siete juegos de registros, las fuerzas de diseño, las deformaciones y las distorsiones de entrepiso son evaluadas a partir de los máximos valores obtenidos de todos los análisis. 30.3.2. Las distorsiones máximas de entrepiso no exceden de 1,25 veces los valores indicados en la Tabla N° 11. 30.3.3. Las deformaciones en los elementos no exceden de 2/3 de aquellas para las que perderían la capacidad portante para cargas verticales o para las que se tendría una pérdida de resistencia en exceso a 30%. 30.3.4. Para verificar la resistencia de los elementos se dividen los resultados del análisis entre R=2, empleándose las normas aplicables a cada material.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite se divide por oracion, y si aun asi excede, por
    coma."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens (se truncarian en la busqueda): {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("peru_e030_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en peru_e030_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
