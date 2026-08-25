"""
Inserta el núcleo verbatim real de la Sección 10.1 (Origen de los
datos) de la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks --
el apéndice de zonificación pedido explícitamente por el usuario
("sigamos con los apéndices de zonificación de Ecuador").

Verificado antes de escribir: 10.2 (Tabla 16, poblaciones/factor Z) ya
estaba cargada de una sesión anterior. 10.3 (Mapa de zonas sísmicas,
Figura 15) y 10.4 (Curvas de peligro sísmico, Figuras 16-38, una por
capital de provincia) son PURAMENTE GRÁFICOS -- el texto extraído del
PDF trae solo las leyendas de las figuras, sin ninguna tabla numérica
para transcribir. No se inventan datos de esas gráficas; su contenido
narrativo equivalente (qué representan las curvas, para qué sirven) ya
está cubierto por el chunk NECSEDS-S3_1_2-CURVAS_PELIGRO_SISMICO
cargado en una sesión anterior. 10.5 (Memoria de cálculo) y 10.6
(Procedimientos de determinación de la geología local) son temas
distintos a zonificación, quedan fuera del alcance de este pedido.

Cubre: 10.1.1 (origen y metodología real del mapa de zonificación
sísmica -- reevaluación de sismicidad histórica, fuentes sismogenéticas,
geodesia GPS, catálogo sísmico unificado de 8.923 eventos, modelación
de Poisson, saturación a 0,50g en zona VI), 10.1.2 (metodología de
establecimiento de los espectros de diseño -- registros reales de la
Red Nacional de Acelerógrafos, simulación estocástica, comparación con
ASCE7-10 y NSR-10 de Colombia, decisión de eliminar el ramal izquierdo
de ascenso del espectro).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion10_1_origen_zonificacion.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 10.1 — Origen de los Datos (Apéndice de Zonificación)"

CHUNKS = [
    {
        "id": "NECSEDS-S10_1_1-ORIGEN_MAPA_ZONIFICACION-01_CRITERIOS",
        "seccion": "10.1.1",
        "titulo": "Origen del mapa de zonas sísmicas: estudio de peligro sísmico 2011 + criterios de uniformidad/practicidad/protección de ciudades/compatibilidad con países vecinos; subducción de la placa de Nazca",
        "texto": (
            "NEC-SE-DS, Sección 10.1.1 — Mapa de zonificación (origen de "
            "los datos). El mapa de zonas sísmicas para diseño incluido "
            "en la norma proviene de: un estudio completo que considera "
            "fundamentalmente los resultados de los estudios de peligro "
            "sísmico del Ecuador actualizados al año 2011; y ciertos "
            "criterios adicionales relacionados con la uniformidad del "
            "peligro en ciertas zonas del país, criterios de "
            "practicidad en el diseño, protección de ciudades "
            "importantes, irregularidad en curvas de definición de "
            "zonas sísmicas, suavizado de zonas de límites inter-zonas, "
            "y compatibilidad con mapas de peligro sísmico de los "
            "países vecinos.\n\n"
            "El mapa reconoce que la subducción de la placa de Nazca "
            "bajo la placa Sudamericana es la principal fuente de "
            "generación de energía sísmica en Ecuador. A esto se suma "
            "un complejo sistema de fallas locales superficiales que "
            "produce sismos importantes en gran parte del territorio "
            "ecuatoriano."
        ),
    },
    {
        "id": "NECSEDS-S10_1_1-ORIGEN_MAPA_ZONIFICACION-02_METODOLOGIA_ESTUDIO",
        "seccion": "10.1.1",
        "titulo": "Metodología del estudio de peligro sísmico: reevaluación histórica (Bakun & Wentworth), geodesia GPS, catálogo unificado de 8.923 eventos independientes (M4,5-8,8), modelación de Poisson",
        "texto": (
            "El estudio de peligro sísmico se realizó de manera "
            "integral para todo el territorio nacional, según "
            "metodologías actuales usadas a nivel mundial y la "
            "información disponible localmente, incluyendo:\n"
            "  Evaluación de los principales eventos históricos, con "
            "re-evaluación moderna de magnitud y localización usando el "
            "método de Bakun & Wentworth (Beauval et al., 2010).\n"
            "  Estudio de las principales fuentes sísmicas conocidas "
            "(corticales y de subducción) y sus mecanismos focales, que "
            "junto con la sismicidad y neotectónica permitió modelar la "
            "geometría de las fuentes sismogenéticas y sus parámetros "
            "(rumbo, buzamiento, magnitud mínima de homogeneidad, tasa "
            "media de actividad sísmica, magnitud máxima probable, "
            "tasas de recurrencia).\n"
            "  Esa modelación se alimentó del campo de velocidades del "
            "Ecuador por GPS de precisión y de modelos de acoplamiento "
            "de segmentos de la subducción.\n"
            "  Análisis de homogeneidad y completitud de los catálogos "
            "sísmicos históricos, con un catálogo sísmico instrumental "
            "unificado a partir del catálogo del Instituto Geofísico de "
            "la Escuela Politécnica Nacional (incluye microsísmicos) y "
            "catálogos internacionales (Centennial/EHB, ISC, NEIC/USGS "
            "PDE, GCMT/HRV), homogeneizando las magnitudes "
            "instrumentales a Mw.\n"
            "  Modelación de más de 30.000 eventos; tras filtrar "
            "réplicas, premonitores, sismos volcánicos y enjambres, se "
            "obtuvieron 8.923 eventos sísmicos independientes (magnitud "
            "mínima de homogeneidad 4,5, máxima 8,8) usados para el "
            "análisis.\n"
            "  Estudio de incertidumbres en los distintos parámetros "
            "utilizados, particularmente las ecuaciones de predicción.\n"
            "  Modelación de la ocurrencia de sismos como proceso de "
            "Poisson, obteniendo curvas de iso-aceleración en "
            "afloramiento rocoso para diferentes niveles de "
            "probabilidad anual de excedencia (inverso del período de "
            "retorno)."
        ),
    },
    {
        "id": "NECSEDS-S10_1_1-ORIGEN_MAPA_ZONIFICACION-03_SATURACION_CARACTER_DINAMICO",
        "seccion": "10.1.1",
        "titulo": "El mapa (Figura 1) sale del estudio a 475 años, con saturación a 0,50g en zona VI (litoral) por razones económicas; carácter dinámico del estudio, se actualizará con más información",
        "texto": (
            "El mapa de zonificación sísmica para diseño (Figura 1, "
            "sección 3.1) proviene del resultado del estudio de peligro "
            "sísmico para 10% de excedencia en 50 años (período de "
            "retorno 475 años), que incluye una saturación a 0,50g de "
            "los valores de aceleración sísmica en roca en el litoral "
            "ecuatoriano que caracteriza la zona VI. Se reconoce "
            "explícitamente que los verdaderos resultados de peligro "
            "sísmico para 475 años en la zona VI son en realidad "
            "mayores a 0,50g, y que fueron saturados a ese valor para "
            "uso en estructuras de edificación normal, por razones "
            "económicas.\n\n"
            "Se reconoce también que los resultados de los estudios de "
            "peligro sísmico tienen carácter dinámico, pues reflejan el "
            "estado actual del conocimiento en sismología y "
            "neotectónica del Ecuador. A medida que haya más "
            "información de las redes de sismógrafos y acelerógrafos "
            "actuales y en instalación, del conocimiento de fallas "
            "activas y de mejores ecuaciones de predicción, esa "
            "información se incluirá en versiones posteriores de la "
            "norma."
        ),
    },
    {
        "id": "NECSEDS-S10_1_2-ESTABLECIMIENTO_ESPECTROS-01_CRITERIOS",
        "seccion": "10.1.2",
        "titulo": "Metodología de los espectros de diseño: 3 criterios — registros reales de la Red Nacional de Acelerógrafos, simulación estocástica de acelerogramas artificiales, comparación con ASCE7-10 y NSR-10 de Colombia",
        "texto": (
            "NEC-SE-DS, Sección 10.1.2 — Establecimiento de los "
            "espectros. Para establecer el espectro de diseño y sus "
            "límites, se consideraron 3 criterios:\n\n"
            "1) Estudio de las formas espectrales elásticas de sismos "
            "ecuatorianos registrados en la Red Nacional de "
            "Acelerógrafos: a partir de los registros de aceleración "
            "disponibles (especialmente en roca y suelo firme), se "
            "estudiaron las formas espectrales con técnicas de "
            "promediado espectral (Yépez, F. et al., 2000).\n\n"
            "2) Simulación estocástica de acelerogramas artificiales y "
            "estudio de formas espectrales: a partir de registros "
            "reales disponibles y de la información sismológica del "
            "sismo real y del sismo mayor a simular (caída de "
            "esfuerzos, momento sísmico), se simularon registros "
            "artificiales mediante procesos estocásticos y funciones de "
            "Green. La simulación de varias familias de registros "
            "permitió estudiar la forma espectral de sismos mayores "
            "(Yépez, F. et al., 2000).\n\n"
            "3) Estudio de las formas espectrales elásticas de las "
            "normativas ASCE 7-10 de Estados Unidos y NSR-10 de "
            "Colombia (ambas de 2010), a base de Dickenson (1994), Seed "
            "et al. (1997 y 2001), Tsang et al. (2006), Tena-Colunga et "
            "al. (2009), Vera Grunauer (2010) y Huang et al. (2010): se "
            "estudiaron las formas espectrales, los factores de "
            "amplificación dinámica de las aceleraciones espectrales, "
            "las frecuencias fundamentales de vibración, la meseta "
            "máxima, la ecuación de la curva de caída, y los factores "
            "de comportamiento inelástico de suelos."
        ),
    },
    {
        "id": "NECSEDS-S10_1_2-ESTABLECIMIENTO_ESPECTROS-02_MESETA_SIN_RAMAL_IZQUIERDO",
        "seccion": "10.1.2",
        "titulo": "Decisión de eliminar el ramal izquierdo de ascenso del espectro elástico y extender la meseta hasta períodos cercanos a cero (por imposibilidad de usar ductilidad en el análisis estático/modal fundamental)",
        "texto": (
            "Debido a la imposibilidad de utilizar la ductilidad para "
            "disminuir la ordenada espectral elástica en períodos "
            "cortos con fines de diseño, y únicamente para el análisis "
            "sísmico estático y para el análisis sísmico dinámico del "
            "modo fundamental de vibración, se eliminó el ramal "
            "izquierdo de ascenso de los espectros elásticos de "
            "respuesta típicos, y se estableció que la meseta máxima "
            "llegue hasta valores de períodos de vibración cercanos a "
            "cero. Esta decisión metodológica explica por qué el "
            "espectro de diseño de la NEC-SE-DS (sección 3.3.1) es "
            "constante (η·Z·Fa) desde T=0 hasta T=TC, en vez de crecer "
            "linealmente desde el origen como en formulaciones clásicas "
            "con ramal ascendente."
        ),
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
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
                "titulo": chunk["titulo"][:500],
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
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("ecuador_nec_se_ds_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en ecuador_nec_se_ds_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
