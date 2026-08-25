"""
Inserta el núcleo verbatim real del Capítulo I (Disposiciones Generales,
Artículos 1-9) de la norma E.030 "Diseño Sismorresistente" de Perú
(Reglamento Nacional de Edificaciones) en peru_e030_chunks.

Primer corpus del programa de replicabilidad internacional de StructAI
(ver memoria del usuario: project_structai_replicabilidad_paises.md).
Texto extraído directamente del PDF oficial del MVCS (Ministerio de
Vivienda, Construcción y Saneamiento de Perú), versión consolidada tras
la modificación por Resolución Ministerial N° 355-2018-VIVIENDA -- el
mismo PDF trae los sellos de aprobación de la Dirección de Construcción y
la Oficina de Asesoría Jurídica del MVCS, confirmando que es el documento
oficial, no una versión de terceros alterada.

Base legal para citar verbatim sin riesgo de derechos de autor: Art. 9(b)
del Decreto Legislativo N° 822 (Ley sobre el Derecho de Autor de Perú)
excluye "los textos oficiales de carácter legislativo, administrativo o
judicial" de la protección de copyright -- misma categoría legal que la
NSR-10 en Colombia (verificado 2026-08-24, no asumido).

Mismo patrón de chunking token-safe usado en scripts/ingesta/nsr10/ (ver
insert_titulo_d_nucleo.py): el modelo de embeddings
(paraphrase-multilingual-MiniLM-L12-v2) trunca duro a 128 tokens, así que
cada bloque se subdivide respetando el conteo real de tokens del
tokenizer, no una aproximación por caracteres.

Uso: python scripts/ingesta/peru_e030/insert_capitulo1_disposiciones_generales.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo I — Disposiciones Generales"

CHUNKS = [
    {
        "id": "E030-CAP1-ART1_A_3",
        "seccion": "Artículos 1 a 3",
        "titulo": "Objeto, Ámbito de Aplicación, y Filosofía y Principios del Diseño Sismorresistente",
        "texto": """Artículo 1.- Objeto

1.1. Esta Norma establece las condiciones mínimas para el Diseño Sismorresistente de las edificaciones.

1.2. Mientras no se cuente con normas nacionales específicas para estructuras tales como reservorios, tanques, silos, puentes, torres de transmisión, muelles, estructuras hidráulicas, túneles y todas aquellas cuyo comportamiento sísmico difiera del de las edificaciones, se debe utilizar los valores Z y S del Capítulo II amplificados de acuerdo a la importancia de la estructura considerando la práctica internacional.

Artículo 2.- Ámbito de Aplicación

2.1. Es de aplicación obligatoria a nivel nacional.

2.2. Se aplica al diseño de todas las edificaciones nuevas, al reforzamiento de las existentes y a la reparación de las estructuras que resulten dañadas por la acción de los sismos.

Artículo 3.- Filosofía y Principios del Diseño Sismorresistente

3.1. La filosofía del Diseño Sismorresistente consiste en: a) Evitar pérdida de vidas humanas. b) Asegurar la continuidad de los servicios básicos. c) Minimizar los daños a la propiedad.

3.2. Se reconoce que dar protección completa frente a todos los sismos no es técnica ni económicamente factible para la mayoría de las estructuras. En concordancia con tal filosofía, se establecen en la presente Norma los siguientes principios: a) La estructura no debería colapsar ni causar daños graves a las personas, aunque podría presentar daños importantes, debido a movimientos sísmicos calificados como severos para el lugar del proyecto. b) La estructura debería soportar movimientos del suelo calificados como moderados para el lugar del proyecto, pudiendo experimentar daños reparables dentro de límites aceptables. c) Para las edificaciones esenciales, definidas en la Tabla N° 5, se debería tener consideraciones especiales orientadas a lograr que permanezcan en condiciones operativas luego de un sismo severo.""",
    },
    {
        "id": "E030-CAP1-ART4_A_5",
        "seccion": "Artículos 4 a 5",
        "titulo": "Aprobación de otros sistemas estructurales, y Otras medidas de prevención",
        "texto": """Artículo 4.- Aprobación de otros sistemas estructurales

El empleo de sistemas estructurales diferentes a los indicados en el artículo 16, es aprobado por el Ministerio de Vivienda, Construcción y Saneamiento, mediante un estudio que demuestre que la alternativa propuesta produce adecuados resultados de rigidez, resistencia sísmica y ductilidad.

Artículo 5.- Otras medidas de prevención

Además de lo indicado en esta Norma, se debe tomar medidas de prevención contra los desastres que puedan producirse como consecuencia del movimiento sísmico: tsunamis, fuego, fuga de materiales peligrosos, deslizamiento masivo de tierras u otros.""",
    },
    {
        "id": "E030-CAP1-ART6_NOMENCLATURA",
        "seccion": "Artículo 6",
        "titulo": "Nomenclatura (C, CT, Fi, R, S, T, U, V, Z, R0, Ia, Ip, entre otras variables)",
        "texto": """Artículo 6.- Nomenclatura

Para efectos de la presente Norma Técnica, se considera la siguiente nomenclatura: C Factor de amplificación sísmica. CT Coeficiente para estimar el período fundamental de un edificio. di Desplazamientos laterales del centro de masa del nivel i en traslación pura (restringiendo los giros en planta) debido a las fuerzas fi. ei Excentricidad accidental en el nivel "i". Fi Fuerza sísmica horizontal en el nivel "i". g Aceleración de la gravedad. hi Altura del nivel "i" con relación al nivel del terreno. hei Altura del entrepiso "i". hn Altura total de la edificación en metros. Mti Momento torsor accidental en el nivel "i". m Número de modos usados en la combinación modal. n Número de pisos del edificio. P Peso total de la edificación. Pi Peso del nivel "i". R Coeficiente de reducción de las fuerzas sísmicas. r Respuesta estructural máxima elástica esperada. ri Respuestas elásticas máximas correspondientes al modo "i". S Factor de amplificación del suelo. Sa Espectro de pseudo aceleraciones. T Período fundamental de la estructura para el análisis estático o período de un modo en el análisis dinámico. TP Período que define la plataforma del factor C. TL Período que define el inicio de la zona del factor C con desplazamiento constante. U Factor de uso o importancia. V Fuerza cortante en la base de la estructura. Z Factor de zona. R0 Coeficiente básico de reducción de las fuerzas sísmicas. Ia Factor de irregularidad en altura. Ip Factor de irregularidad en planta. fi Fuerza lateral en el nivel i. V̄s Velocidad promedio de propagación de las ondas de corte. N̄60 Promedio ponderado de los ensayos de penetración estándar. S̄u Promedio ponderado de la resistencia al corte en condición no drenada.""",
    },
    {
        "id": "E030-CAP1-ART7_CONCEPCION_ESTRUCTURAL",
        "seccion": "Artículo 7",
        "titulo": "Concepción Estructural Sismorresistente (simetría, peso mínimo, ductilidad, redundancia)",
        "texto": """Artículo 7.- Concepción Estructural Sismorresistente

Debe tomarse en cuenta la importancia de los siguientes aspectos: a) Simetría, tanto en la distribución de masas como de rigideces. b) Peso mínimo, especialmente en los pisos altos. c) Selección y uso adecuado de los materiales de construcción. d) Resistencia adecuada, en ambas direcciones principales, frente a las cargas laterales. e) Continuidad estructural, tanto en planta como en elevación. f) Ductilidad, entendida como la capacidad de deformación de la estructura más allá del rango elástico. g) Deformación lateral limitada. h) Inclusión de líneas sucesivas de resistencia (redundancia estructural). i) Consideración de las condiciones locales. j) Buena práctica constructiva y supervisión estructural rigurosa.""",
    },
    {
        "id": "E030-CAP1-ART8_CONSIDERACIONES_GENERALES",
        "seccion": "Artículo 8",
        "titulo": "Consideraciones Generales (sismo y viento no simultáneos, tabiques, incursión inelástica)",
        "texto": """Artículo 8.- Consideraciones Generales

8.1. Toda edificación y cada una de sus partes debe ser diseñada y construida para resistir las solicitaciones sísmicas prescritas en esta Norma, siguiendo las especificaciones de las normas pertinentes a los materiales empleados.

8.2. No es necesario considerar simultáneamente los efectos de sismo y viento.

8.3. Se debe considerar el posible efecto de los tabiques, parapetos y otros elementos adosados en el comportamiento sísmico de la estructura. El análisis, el detallado del refuerzo y el anclaje deben hacerse acorde con esta consideración.

8.4. En concordancia con los principios de Diseño Sismorresistente establecidos en el artículo 3, se acepta que las edificaciones tengan incursiones inelásticas frente a solicitaciones sísmicas severas. Por tanto, las fuerzas sísmicas de diseño son una fracción de la solicitación sísmica máxima elástica.""",
    },
    {
        "id": "E030-CAP1-ART9_PRESENTACION_PROYECTO",
        "seccion": "Artículo 9",
        "titulo": "Presentación del Proyecto (firma de ingeniero civil colegiado, contenido mínimo de planos)",
        "texto": """Artículo 9.- Presentación del Proyecto

9.1. Los planos, la memoria descriptiva y las especificaciones técnicas del proyecto estructural son firmados por el ingeniero civil colegiado responsable del diseño, quien es el único autorizado para aprobar cualquier modificación a los mismos.

9.2. Los planos del proyecto estructural incluyen la siguiente información: a) Sistema estructural sismorresistente. b) Período fundamental de vibración en ambas direcciones principales. c) Parámetros para definir la fuerza sísmica o el espectro de diseño. d) Fuerza cortante en la base empleada para el diseño, en ambas direcciones. e) Desplazamiento máximo del último nivel y el máximo desplazamiento relativo de entrepiso. f) La ubicación de las estaciones acelerométricas, si éstas se requieren conforme al Capítulo IX.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable, porque texto denso en símbolos/listas (ej. la
# nomenclatura del Artículo 6) tokeniza más denso que prosa normal.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite (ej. el bloque de nomenclatura del Articulo 6) se
    divide por oracion, y si aun asi excede, por coma."""
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
