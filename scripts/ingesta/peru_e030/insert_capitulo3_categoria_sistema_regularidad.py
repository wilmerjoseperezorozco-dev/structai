"""
Inserta el núcleo verbatim real del Capítulo III (Categoría, Sistema
Estructural y Regularidad de las Edificaciones, Artículos 15-23) de la
norma E.030 de Perú en peru_e030_chunks. Tercer bloque del corpus, después
de los Capítulos I y II (ver insert_capitulo1_disposiciones_generales.py
e insert_capitulo2_peligro_sismico.py -- mismo texto oficial del MVCS,
misma base legal de citación verbatim, Art. 9(b) del Decreto Legislativo
N° 822).

Cubre: categoría de edificaciones y factor de uso U (Tabla N°5), sistemas
estructurales por material -- concreto armado, acero, albañilería, madera,
tierra (Artículo 16), categoría vs. sistema estructural permitido por zona
(Tabla N°6), coeficiente básico de reducción R0 por sistema (Tabla N°7),
regularidad estructural y factores de irregularidad en altura/planta
(Tablas N°8 y N°9), restricciones a la irregularidad por categoría/zona
(Tabla N°10), el coeficiente de reducción R = R0·Ia·Ip (Artículo 22), y
aislamiento sísmico/disipación de energía (Artículo 23).

Es el capítulo con más tablas de toda la norma (6) -- cada sistema
estructural real que un ingeniero peruano puede elegir para un proyecto
está acá, con su coeficiente de reducción sísmica exacto.

Uso: python scripts/ingesta/peru_e030/insert_capitulo3_categoria_sistema_regularidad.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo III — Categoría, Sistema Estructural y Regularidad de las Edificaciones"

CHUNKS = [
    {
        "id": "E030-CAP3-ART15-CATEGORIA_TABLA5",
        "seccion": "Artículo 15",
        "titulo": "Categoría de las Edificaciones y Factor de Uso U (Tabla N°5: A1, A2, B, C, D)",
        "texto": """Artículo 15.- Categoría de las Edificaciones y Factor de Uso (U)

Cada estructura está clasificada de acuerdo con las categorías indicadas en la Tabla N° 5. El factor de uso o importancia (U), definido en la Tabla N° 5 se usa según la clasificación que se haga. Para edificios con aislamiento sísmico en la base se puede considerar U = 1.

Tabla N° 5 — Categoría de las Edificaciones y Factor "U": Categoría A1 (Establecimientos del sector salud, segundo y tercer nivel, según el Ministerio de Salud) → factor U según nota 1. Categoría A2 (edificaciones esenciales para el manejo de emergencias, funcionamiento del gobierno, o que puedan servir de refugio tras un desastre: establecimientos de salud no A1, puertos, aeropuertos, estaciones ferroviarias de pasajeros, sistemas masivos de transporte, locales municipales, centrales de comunicaciones, estaciones de bomberos, cuarteles de fuerzas armadas y policía, instalaciones de generación/transformación eléctrica, reservorios, plantas de tratamiento de agua, instituciones educativas e institutos superiores/universidades, edificaciones cuyo colapso represente riesgo adicional como hornos/fábricas/depósitos de inflamables o tóxicos, y edificios que almacenen archivos e información esencial del Estado) → U = 1,5. Categoría B, Edificaciones Importantes (cines, teatros, estadios, coliseos, centros comerciales, terminales de buses, establecimientos penitenciarios, museos, bibliotecas, depósitos de granos y almacenes importantes para abastecimiento) → U = 1,3. Categoría C, Edificaciones Comunes (viviendas, oficinas, hoteles, restaurantes, depósitos e instalaciones industriales cuya falla no acarree incendios o fugas de contaminantes) → U = 1,0. Categoría D, Edificaciones Temporales (construcciones provisionales para depósitos, casetas y similares) → U según nota 2.

Nota 1: Las nuevas edificaciones de categoría A1 tienen aislamiento sísmico en la base cuando se encuentren en las zonas sísmicas 4 y 3. En las zonas sísmicas 1 y 2, la entidad responsable puede decidir si usa o no aislamiento sísmico. Si no se utiliza aislamiento sísmico en las zonas sísmicas 1 y 2, el valor de U es como mínimo 1,5.

Nota 2: En las edificaciones temporales se provee resistencia y rigidez adecuadas para acciones laterales, a criterio del proyectista.""",
    },
    {
        "id": "E030-CAP3-ART16_1-CONCRETO_ARMADO",
        "seccion": "Artículo 16.1",
        "titulo": "Sistemas Estructurales — Estructuras de Concreto Armado (Pórticos, Muros, Dual, EMDL)",
        "texto": """Artículo 16.- Sistemas Estructurales

16.1. Estructuras de Concreto Armado — Todos los elementos de concreto armado que conforman el sistema estructural sismorresistente cumplen con lo previsto en la Norma Técnica E.060 Concreto Armado del RNE.

a) Pórticos — Por lo menos el 80% de la fuerza cortante en la base actúa sobre las columnas de los pórticos. En caso se tengan muros estructurales, éstos se diseñan para resistir una fracción de la acción sísmica total de acuerdo con su rigidez.

b) Muros Estructurales — Sistema en el que la resistencia sísmica está dada predominantemente por muros estructurales sobre los que actúa por lo menos el 70% de la fuerza cortante en la base.

c) Dual — Las acciones sísmicas son resistidas por una combinación de pórticos y muros estructurales. La fuerza cortante que toman los muros es mayor que 20% y menor que 70% del cortante en la base del edificio.

d) Edificaciones de Muros de Ductilidad Limitada (EMDL) — Edificaciones que se caracterizan por tener un sistema estructural donde la resistencia sísmica y de cargas de gravedad está dada por muros de concreto armado de espesores reducidos, en los que se prescinde de extremos confinados y el refuerzo vertical se dispone en una sola capa. Con este sistema se puede construir como máximo ocho pisos.""",
    },
    {
        "id": "E030-CAP3-ART16_2-ACERO",
        "seccion": "Artículo 16.2",
        "titulo": "Sistemas Estructurales — Estructuras de Acero (SMF, IMF, OMF, SCBF, OCBF, EBF)",
        "texto": """16.2. Estructuras de Acero — Los Sistemas que se indican a continuación forman parte del Sistema Estructural Resistente a Sismos:

a) Pórticos Especiales Resistentes a Momentos (SMF) — Estos pórticos proveen una significativa capacidad de deformación inelástica a través de la fluencia por flexión de las vigas y limitada fluencia en las zonas de panel de las columnas. Las columnas son diseñadas para tener una resistencia mayor que las vigas cuando estas incursionan en la zona de endurecimiento por deformación.

b) Pórticos Intermedios Resistentes a Momentos (IMF) — Estos pórticos proveen una limitada capacidad de deformación inelástica en sus elementos y conexiones.

c) Pórticos Ordinarios Resistentes a Momentos (OMF) — Estos pórticos proveen una mínima capacidad de deformación inelástica en sus elementos y conexiones.

d) Pórticos Especiales Concéntricamente Arriostrados (SCBF) — Estos pórticos proveen una significativa capacidad de deformación inelástica a través de la resistencia post-pandeo en los arriostres en compresión y fluencia en los arriostres en tracción.

e) Pórticos Ordinarios Concéntricamente Arriostrados (OCBF) — Estos pórticos proveen una limitada capacidad de deformación inelástica en sus elementos y conexiones.

f) Pórticos Excéntricamente Arriostrados (EBF) — Estos pórticos proveen una significativa capacidad de deformación inelástica principalmente por fluencia en flexión o corte en la zona entre arriostres.""",
    },
    {
        "id": "E030-CAP3-ART16_3_A_5-ALBANILERIA_MADERA_TIERRA",
        "seccion": "Artículo 16.3 a 16.5",
        "titulo": "Sistemas Estructurales — Estructuras de Albañilería, Madera y Tierra",
        "texto": """16.3. Estructuras de Albañilería — Edificaciones cuyos elementos sismorresistentes son muros a base de unidades de albañilería de arcilla o concreto. Para efectos de esta Norma no se hace diferencia entre estructuras de albañilería confinada o de albañilería armada.

16.4. Estructuras de Madera — Se consideran en este grupo las edificaciones cuyos elementos resistentes son principalmente a base de madera. Se incluyen sistemas entramados y estructuras arriostradas tipo poste y viga.

16.5. Estructuras de Tierra — Son edificaciones cuyos muros son hechos con unidades de albañilería de tierra o tierra apisonada in situ.""",
    },
    {
        "id": "E030-CAP3-ART17-CATEGORIA_SISTEMA_TABLA6",
        "seccion": "Artículo 17",
        "titulo": "Categoría y Sistemas Estructurales permitidos por zona (Tabla N°6)",
        "texto": """Artículo 17.- Categoría y Sistemas Estructurales

De acuerdo a la categoría de una edificación y la zona donde se ubique, ésta se proyecta empleando el sistema estructural que se indica en la Tabla N° 6 y respetando las restricciones a la irregularidad de la Tabla N° 10.

Tabla N° 6 — Categoría y Sistema Estructural de las Edificaciones: Categoría A1, zonas 4 y 3 → Aislamiento Sísmico con cualquier sistema estructural; zonas 2 y 1 → Estructuras de acero tipo SCBF y EBF, estructuras de concreto Sistema Dual o Muros de Concreto Armado, Albañilería Armada o Confinada. Categoría A2, zonas 4, 3 y 2 → Estructuras de acero tipo SCBF y EBF, estructuras de concreto Sistema Dual o Muros de Concreto Armado, Albañilería Armada o Confinada; zona 1 → Cualquier sistema. Categoría B, zonas 4, 3 y 2 → Estructuras de acero tipo SMF, IMF, SCBF, OCBF y EBF, estructuras de concreto Pórticos/Sistema Dual/Muros de Concreto Armado, Albañilería Armada o Confinada, Estructuras de madera; zona 1 → Cualquier sistema. Categoría C, zonas 4, 3, 2 y 1 → Cualquier sistema.

Notas de la Tabla N° 6: para edificaciones con cobertura liviana se podrá usar cualquier sistema estructural; para pequeñas construcciones rurales, como escuelas y postas médicas, se puede usar materiales tradicionales siguiendo las recomendaciones de las normas correspondientes a dichos materiales.""",
    },
    {
        "id": "E030-CAP3-ART18-COEFICIENTE_R0_TABLA7",
        "seccion": "Artículo 18",
        "titulo": "Coeficiente Básico de Reducción de las Fuerzas Sísmicas R0 por sistema estructural (Tabla N°7)",
        "texto": """Artículo 18.- Sistemas Estructurales y Coeficiente Básico de Reducción de las Fuerzas Sísmicas (R0)

18.1. Los sistemas estructurales se clasifican según los materiales usados y el sistema de estructuración sismorresistente en cada dirección de análisis, tal como se indica en la Tabla N° 7.

18.2. Cuando en la dirección de análisis, la edificación presente más de un sistema estructural, se toma el menor coeficiente R0 que corresponda.

Tabla N° 7 — Sistemas Estructurales y su Coeficiente Básico de Reducción R0: Acero — Pórticos Especiales Resistentes a Momentos (SMF) → R0=8; Pórticos Intermedios Resistentes a Momentos (IMF) → R0=5; Pórticos Ordinarios Resistentes a Momentos (OMF) → R0=4; Pórticos Especiales Concéntricamente Arriostrados (SCBF) → R0=7; Pórticos Ordinarios Concéntricamente Arriostrados (OCBF) → R0=4; Pórticos Excéntricamente Arriostrados (EBF) → R0=8. Concreto Armado — Pórticos → R0=8; Dual → R0=7; De muros estructurales → R0=6; Muros de ductilidad limitada → R0=4. Albañilería Armada o Confinada → R0=3. Madera → R0=7 (para diseño por esfuerzos admisibles).

Notas de la Tabla N° 7: estos coeficientes se aplican únicamente a estructuras en las que los elementos verticales y horizontales permitan la disipación de la energía manteniendo la estabilidad de la estructura, no se aplican a estructuras tipo péndulo invertido.

18.3. Para construcciones de tierra se remite a la Norma E.080 "Diseño y Construcción con Tierra Reforzada" del RNE. Este tipo de construcción no se recomienda en suelos S3, ni se permite en suelos S4.""",
    },
    {
        "id": "E030-CAP3-ART19_20-REGULARIDAD_INTRO",
        "seccion": "Artículos 19 y 20 (introducción)",
        "titulo": "Regularidad Estructural y Factores de Irregularidad Ia/Ip — criterio general",
        "texto": """Artículo 19.- Regularidad Estructural

19.1. Las estructuras se clasifican como regulares o irregulares para los fines siguientes: a) Cumplir las restricciones de la Tabla N° 10. b) Establecer los procedimientos de análisis. c) Determinar el coeficiente R de reducción de fuerzas sísmicas.

19.2. Estructuras Regulares son las que, en su configuración resistente a cargas laterales, no presentan las irregularidades indicadas en las Tablas N° 8 y N° 9. En estos casos, el factor Ia e Ip es igual a 1,0.

19.3. Estructuras Irregulares son aquellas que presentan una o más de las irregularidades indicadas en las Tablas N° 8 y N° 9.

Artículo 20.- Factores de Irregularidad (Ia, Ip)

20.1. El factor Ia se determina como el menor de los valores de la Tabla N° 8 correspondiente a las irregularidades estructurales existentes en altura en las dos direcciones de análisis.

20.2. El factor Ip se determina como el menor de los valores de la Tabla N° 9 correspondiente a las irregularidades estructurales existentes en planta en las dos direcciones de análisis.

20.3. Si al aplicar las Tablas N° 8 y 9 se obtuvieran valores distintos de los factores Ia o Ip para las dos direcciones de análisis, se toma para cada factor el menor valor entre los obtenidos para las dos direcciones.""",
    },
    {
        "id": "E030-CAP3-TABLA8-IRREGULARIDAD_ALTURA",
        "seccion": "Tabla N°8",
        "titulo": "Irregularidades Estructurales en Altura y su Factor Ia (piso blando/débil, masa, geométrica, discontinuidad de sistemas)",
        "texto": """Tabla N° 8 — Irregularidades Estructurales en Altura:

Irregularidad de Rigidez – Piso Blando: existe cuando, en cualquiera de las direcciones de análisis, en un entrepiso la rigidez lateral es menor que 70% de la rigidez lateral del entrepiso inmediato superior, o es menor que 80% de la rigidez lateral promedio de los tres niveles superiores adyacentes (las rigideces laterales pueden calcularse como la razón entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relativo en el centro de masas, ambos evaluados para la misma condición de carga). Irregularidad de Resistencia – Piso Débil: existe cuando, en cualquiera de las direcciones de análisis, la resistencia de un entrepiso frente a fuerzas cortantes es inferior a 80% de la resistencia del entrepiso inmediato superior. Factor Ia = 0,75.

Irregularidad Extrema de Rigidez (ver Tabla N° 10): existe cuando, en cualquiera de las direcciones de análisis, en un entrepiso la rigidez lateral es menor que 60% de la rigidez lateral del entrepiso inmediato superior, o es menor que 70% de la rigidez lateral promedio de los tres niveles superiores adyacentes. Irregularidad Extrema de Resistencia (ver Tabla N° 10): existe cuando la resistencia de un entrepiso frente a fuerzas cortantes es inferior a 65% de la resistencia del entrepiso inmediato superior. Factor Ia = 0,50.

Irregularidad de Masa o Peso: se tiene cuando el peso de un piso, determinado según el artículo 26, es mayor que 1,5 veces el peso de un piso adyacente. Este criterio no se aplica en azoteas ni en sótanos. Factor Ia = 0,90.

Irregularidad Geométrica Vertical: la configuración es irregular cuando, en cualquiera de las direcciones de análisis, la dimensión en planta de la estructura resistente a cargas laterales es mayor que 1,3 veces la correspondiente dimensión en un piso adyacente. Este criterio no se aplica en azoteas ni en sótanos. Factor Ia = 0,90.

Discontinuidad en los Sistemas Resistentes: se califica a la estructura como irregular cuando en cualquier elemento que resista más de 10% de la fuerza cortante se tiene un desalineamiento vertical, tanto por un cambio de orientación, como por un desplazamiento del eje de magnitud mayor que 25% de la correspondiente dimensión del elemento. Factor Ia = 0,80.

Discontinuidad Extrema de los Sistemas Resistentes (ver Tabla N° 10): existe cuando la fuerza cortante que resisten los elementos discontinuos según se describen en el ítem anterior, supere el 25% de la fuerza cortante total. Factor Ia = 0,60.""",
    },
    {
        "id": "E030-CAP3-TABLA9-IRREGULARIDAD_PLANTA",
        "seccion": "Tabla N°9",
        "titulo": "Irregularidades Estructurales en Planta y su Factor Ip (torsional, esquinas entrantes, diafragma, sistemas no paralelos)",
        "texto": """Tabla N° 9 — Irregularidades Estructurales en Planta:

Irregularidad Torsional: existe cuando, en cualquiera de las direcciones de análisis, el máximo desplazamiento relativo de entrepiso en un extremo del edificio (Δmax) en esa dirección, calculado incluyendo excentricidad accidental, es mayor que 1,3 veces el desplazamiento relativo promedio de los extremos del mismo entrepiso para la misma condición de carga (Δprom). Este criterio sólo se aplica en edificios con diafragmas rígidos y sólo si el máximo desplazamiento relativo de entrepiso es mayor que 50% del desplazamiento permisible indicado en la Tabla N° 11. Factor Ip = 0,75.

Irregularidad Torsional Extrema (ver Tabla N° 10): existe cuando el máximo desplazamiento relativo de entrepiso en un extremo del edificio (Δmax), calculado incluyendo excentricidad accidental, es mayor que 1,5 veces el desplazamiento relativo promedio de los extremos del mismo entrepiso (Δprom), bajo las mismas condiciones de aplicación que la irregularidad torsional simple. Factor Ip = 0,60.

Esquinas Entrantes: la estructura se califica como irregular cuando tiene esquinas entrantes cuyas dimensiones en ambas direcciones son mayores que 20% de la correspondiente dimensión total en planta. Factor Ip = 0,90.

Discontinuidad del Diafragma: la estructura se califica como irregular cuando los diafragmas tienen discontinuidades abruptas o variaciones importantes en rigidez, incluyendo aberturas mayores que 50% del área bruta del diafragma. También existe irregularidad cuando, en cualquiera de los pisos y para cualquiera de las direcciones de análisis, se tiene alguna sección transversal del diafragma con un área neta resistente menor que 25% del área de la sección transversal total de la misma dirección calculada con las dimensiones totales de la planta. Factor Ip = 0,85.

Sistemas no Paralelos: se considera que existe irregularidad cuando en cualquiera de las direcciones de análisis los elementos resistentes a fuerzas laterales no son paralelos. No se aplica si los ejes de los pórticos o muros forman ángulos menores que 30° ni cuando los elementos no paralelos resisten menos que 10% de la fuerza cortante del piso. Factor Ip = 0,90.""",
    },
    {
        "id": "E030-CAP3-ART21-RESTRICCIONES_TABLA10",
        "seccion": "Artículo 21",
        "titulo": "Restricciones a la Irregularidad por Categoría y Zona (Tabla N°10) y Sistemas de Transferencia",
        "texto": """Artículo 21.- Restricciones a la Irregularidad

21.1. Categoría de la Edificación e Irregularidad — De acuerdo a su categoría y la zona donde se ubique, la edificación se proyecta respetando las restricciones a la irregularidad de la Tabla N° 10.

Tabla N° 10 — Categoría y Regularidad de las Edificaciones: A1 y A2, zonas 4, 3 y 2 → No se permiten irregularidades; zona 1 → No se permiten irregularidades extremas. Categoría B, zonas 4, 3 y 2 → No se permiten irregularidades extremas; zona 1 → Sin restricciones. Categoría C, zonas 4 y 3 → No se permiten irregularidades extremas; zona 2 → No se permiten irregularidades extremas excepto en edificios de hasta 2 pisos u 8 m de altura total; zona 1 → Sin restricciones.

21.2. Sistemas de Transferencia. 21.2.1. Los sistemas de transferencia son estructuras de losas y vigas que transmiten las fuerzas y momentos desde elementos verticales discontinuos hacia otros del piso inferior. 21.2.2. En las zonas sísmicas 4, 3 y 2 no se permiten estructuras con sistema de transferencia en los que más del 25% de las cargas de gravedad o de las cargas sísmicas en cualquier nivel sean soportadas por elementos verticales que no son continuos hasta la cimentación. Esta disposición no se aplica para el último entrepiso de las edificaciones.""",
    },
    {
        "id": "E030-CAP3-ART22_23-COEFICIENTE_R_AISLAMIENTO",
        "seccion": "Artículos 22 y 23",
        "titulo": "Coeficiente de Reducción R = R0·Ia·Ip, y Sistemas de Aislamiento Sísmico y Disipación de Energía",
        "texto": """Artículo 22.- Coeficiente de Reducción de las Fuerzas Sísmicas, R

El coeficiente de reducción de las fuerzas sísmicas se determina como el producto del coeficiente R0 determinado a partir de la Tabla N° 7 y de los factores Ia, Ip obtenidos de las Tablas N° 8 y N° 9. R = R0 · Ia · Ip.

Artículo 23.- Sistemas de Aislamiento Sísmico y Sistemas de Disipación de Energía

23.1. Se permite la utilización de sistemas de aislamiento sísmico o de sistemas de disipación de energía en la edificación, siempre y cuando se cumplan las disposiciones del capítulo II de esta Norma y, en la medida que sean aplicables, los requisitos del documento "Minimum Design Loads for Building and Other Structures", ASCE/SEI 7, vigente, Structural Engineering Institute of the American Society of Civil Engineers, Reston, Virginia, USA.

23.2. La instalación de sistemas de aislamiento sísmico o de sistemas de disipación de energía se somete a una supervisión técnica especializada a cargo de un ingeniero civil.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite (ej. cada item de la Tabla N°8/N°9, redactado
    como un solo parrafo denso) se divide por oracion, y si aun asi
    excede, por coma."""
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
