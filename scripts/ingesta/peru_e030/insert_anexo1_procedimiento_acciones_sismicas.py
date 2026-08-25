"""
Inserta el núcleo verbatim real del Anexo I (Procedimiento Sugerido para
la Determinación de las Acciones Sísmicas) de la norma E.030 de Perú en
peru_e030_chunks. Décimo bloque del corpus, después de los Capítulos I-IX
(ver los otros insert_capituloN_*.py -- mismo texto oficial del MVCS,
misma base legal de citación verbatim, Art. 9(b) del Decreto Legislativo
N° 822).

El Anexo I es distinto a los capítulos anteriores: no introduce reglas
nuevas, es una SÍNTESIS procedimental de 18 pasos organizados en 4 etapas
(Peligro Sísmico, Caracterización del Edificio, Análisis Estructural,
Validación de la Estructura) que referencia y encadena TODO el cuerpo
normativo ya cargado (Capítulos II-V). Es, en la práctica, el "algoritmo"
completo que un ingeniero sigue de principio a fin para diseñar
sismorresistentemente una edificación en Perú -- alto valor para
respuestas tipo "¿cuáles son los pasos para calcular...?".

Nota de transcripción honesta (mismo criterio que en el Capítulo IV, ver
insert_capitulo4_analisis_estructural.py): el Paso 13B de este Anexo
menciona escalar los resultados del análisis dinámico "considerando un
cortante mínimo en el primer entrepiso que es un porcentaje del cortante
calculado para el método estático (numeral 28.3)" -- el numeral 28.3 es
en realidad la Distribución de la Fuerza Sísmica en Altura, no el cálculo
de la fuerza cortante total en la base (que es el numeral 28.2). Puede ser
una referencia intencional (la distribución en altura sí depende de V) o
una imprecisión de numeración similar a la ya encontrada en el Artículo
29.4.1. Se transcribe tal cual aparece en el documento fuente, sin
corregir en silencio.

Uso: python scripts/ingesta/peru_e030/insert_anexo1_procedimiento_acciones_sismicas.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Anexo I — Procedimiento Sugerido para la Determinación de las Acciones Sísmicas"

CHUNKS = [
    {
        "id": "E030-ANEXO1-INTRO_ETAPA1-PELIGRO_SISMICO",
        "seccion": "Introducción y Etapa 1",
        "titulo": "Introducción y Etapa 1: Peligro Sísmico (Pasos 1-4 — factor Z, perfil de suelo, parámetros S/TP/TL, función C vs T)",
        "texto": """ANEXO I — PROCEDIMIENTO SUGERIDO PARA LA DETERMINACIÓN DE LAS ACCIONES SÍSMICAS

Las acciones sísmicas para el diseño estructural dependen de la zona sísmica (Z), del perfil de suelo (S, TP, TL), del uso de la edificación (U), del sistema sismorresistente (R) y las características dinámicas de la edificación (T, C) y de su peso (P).

ETAPA 1: PELIGRO SÍSMICO (Capítulo II) — Los pasos de esta etapa dependen solamente del lugar y las características del terreno de fundación del proyecto. No dependen de las características del edificio.

Paso 1 — Factor de Zona Z (Artículo 10): Determinar la zona sísmica donde se encuentra el proyecto en base al mapa de zonificación sísmica (Figura N°1) o a la Tabla de provincias y distritos del Anexo II. Determinar el factor de zona (Z) de acuerdo a la Tabla N°1.

Paso 2 — Perfil de Suelo (Artículo 12): De acuerdo a los resultados del Estudio de Mecánica de Suelos (EMS) se determina el tipo de perfil de suelo según el numeral 12.1 donde se definen 5 perfiles de suelo. La clasificación se hace en base a los parámetros indicados en la Tabla N°2 considerando promedios para los estratos de los primeros 30 m bajo el nivel de cimentación. Cuando no se conozcan las propiedades del suelo hasta la profundidad de 30 m, el profesional responsable del EMS determina el tipo de perfil de suelo sobre la base de las condiciones geotécnicas conocidas.

Paso 3 — Parámetros de Sitio S, TP y TL (Artículo 13): El factor de amplificación del suelo se obtiene de la Tabla N°3 y depende de la zona sísmica y el tipo de perfil de suelo. Los períodos TP y TL se obtienen de la Tabla N°4 y solo dependen del tipo de perfil de suelo.

Paso 4 — Construir la función Factor de Amplificación Sísmica C versus Período T (Artículo 14): Depende de los parámetros de sitio TP y TL. Se definen tres tramos, períodos cortos, intermedios y largos, y se aplica para cada tramo las expresiones de este numeral.""",
    },
    {
        "id": "E030-ANEXO1-ETAPA2-CARACTERIZACION_EDIFICIO",
        "seccion": "Etapa 2",
        "titulo": "Etapa 2: Caracterización del Edificio (Pasos 5-10 — categoría/uso, sistema estructural, R0, irregularidad Ia/Ip, restricciones, R=R0·Ia·Ip)",
        "texto": """ETAPA 2: CARACTERIZACIÓN DEL EDIFICIO (Capítulo III) — Los pasos de esta etapa dependen de las características de la edificación, como son su categoría, sistema estructural y configuración regular o irregular.

Paso 5 — Categoría de la Edificación y el Factor de Uso U (Artículo 15): La categoría de la edificación y el factor de uso (U) se obtienen de la Tabla N°5.

Paso 6 — Sistema Estructural (Artículos 16 y 17): Se determina el sistema estructural de acuerdo a las definiciones que aparecen en el artículo 16. En la Tabla N°6 (artículo 17) se definen los sistemas estructurales permitidos de acuerdo a la categoría de la edificación y a la zona sísmica en la que se encuentra.

Paso 7 — Coeficiente Básico de Reducción de Fuerzas Sísmicas, R0 (Artículo 18): De la Tabla N°7 se obtiene el valor del coeficiente R0, que depende únicamente del sistema estructural.

Paso 8 — Factores de Irregularidad Ia, Ip (Artículo 20): El factor Ia se determina como el menor de los valores de la Tabla N°8 correspondiente a las irregularidades existentes en altura. El factor Ip se determina como el menor de los valores de la Tabla N°9 correspondiente a las irregularidades existentes en planta. En la mayoría de los casos se puede determinar si una estructura es regular o irregular a partir de su configuración estructural, pero en los casos de Irregularidad de Rigidez e Irregularidad Torsional se comprueba con los resultados del análisis sísmico según se indica en la descripción de dichas irregularidades.

Paso 9 — Restricciones a la Irregularidad (Artículo 21): Verificar las restricciones a la irregularidad de acuerdo a la categoría y zona de la edificación en la Tabla N°10. Modificar la estructuración en caso que no se cumplan las restricciones de esta Tabla.

Paso 10 — Coeficiente de Reducción de la Fuerza Sísmica R (Artículo 22): Se determina R = R0 · Ia · Ip.""",
    },
    {
        "id": "E030-ANEXO1-ETAPA3-ANALISIS_ESTRUCTURAL",
        "seccion": "Etapa 3",
        "titulo": "Etapa 3: Análisis Estructural (Pasos 11-13B — modelo, estimación de peso, análisis estático y dinámico modal espectral paso a paso)",
        "texto": """ETAPA 3: ANÁLISIS ESTRUCTURAL (Capítulo IV) — En esta etapa se desarrolla el análisis estructural. Se sugieren criterios para la elaboración del modelo matemático de la estructura, se indica cómo se calcula el peso de la edificación y se definen los procedimientos de análisis.

Paso 11 — Modelos de Análisis (Artículo 25): Desarrollar el modelo matemático de la estructura. Para estructuras de concreto armado y albañilería considerar las propiedades de las secciones brutas ignorando la fisuración y el refuerzo.

Paso 12 — Estimación del Peso P (Artículo 26): Se determina el peso (P) para el cálculo de la fuerza sísmica adicionando a la carga permanente total un porcentaje de la carga viva que depende del uso y la categoría de la edificación, definido de acuerdo a lo indicado en este numeral.

Paso 13 — Procedimientos de Análisis Sísmico (Artículos 27 al 30): Se definen los procedimientos de análisis considerados en esta Norma, que son análisis estático (artículo 28) y análisis dinámico modal espectral (artículo 29).

Paso 13A — Análisis Estático (Artículo 28): Este procedimiento solo es aplicable a las estructuras que cumplen lo indicado en el numeral 28.1. El análisis estático tiene los siguientes pasos: calcular la fuerza cortante en la base V=(Z·U·C·S/R)·P para cada dirección de análisis (numeral 28.2); para determinar el valor de C (Paso 4 o artículo 14) se estima el período fundamental de vibración de la estructura (T) en cada dirección (numeral 28.4); determinar la distribución en la altura de la fuerza sísmica de cada dirección (numeral 28.3); aplicar las fuerzas obtenidas en el centro de masas de cada piso, considerando además el momento torsor accidental (numeral 28.5); considerar fuerzas sísmicas verticales (numeral 28.6) para los elementos en los que sea necesario.

Paso 13B — Análisis Dinámico (Artículo 29): Si se elige o es un requerimiento desarrollar un análisis dinámico modal espectral se debe: determinar los modos de vibración y sus correspondientes períodos naturales y masas participantes mediante análisis dinámico del modelo matemático (numeral 29.1); calcular el espectro inelástico de pseudo aceleraciones Sa=(Z·U·C·S/R)·g para cada dirección de análisis (numeral 29.2); considerar excentricidad accidental (numeral 29.5); determinar todos los resultados de fuerzas y desplazamientos para cada modo de vibración; determinar la respuesta máxima esperada correspondiente al efecto conjunto de los modos considerados (numeral 29.3); escalar todos los resultados obtenidos para fuerzas considerando un cortante mínimo en el primer entrepiso que es un porcentaje del cortante calculado para el método estático (numeral 28.3 -- ver nota de transcripción en el docstring del script sobre esta referencia), sin escalar los resultados para desplazamientos; considerar fuerzas sísmicas verticales (numeral 29.2) usando un espectro con valores iguales a 2/3 del espectro más crítico para las direcciones horizontales, para los elementos que sea necesario.""",
    },
    {
        "id": "E030-ANEXO1-ETAPA4-VALIDACION_ESTRUCTURA",
        "seccion": "Etapa 4",
        "titulo": "Etapa 4: Validación de la Estructura (Pasos 14-18 — revisión de hipótesis, restricciones a la irregularidad, desplazamientos, distorsión admisible, separación)",
        "texto": """ETAPA 4: VALIDACIÓN DE LA ESTRUCTURA — De acuerdo a los resultados del análisis, se determina si la estructura planteada es válida, para lo cual cumple con los requisitos de regularidad y rigidez indicados en este capítulo.

Paso 14 — Revisión de las Hipótesis del Análisis: Con los resultados de los análisis se revisan los factores de irregularidad aplicados en el paso 8. En base a éstos se verifica si los valores de R se mantienen o son modificados. En caso de haberse empleado el procedimiento de análisis estático se verifica lo señalado en el numeral 28.1.

Paso 15 — Restricciones a la Irregularidad (Artículo 21): Verificar las restricciones a la irregularidad de acuerdo a la categoría y zona de la edificación en la Tabla N°10. De existir irregularidades o irregularidades extremas en edificaciones que no están permitidas según esa Tabla, se modifica la estructuración y se repite el análisis hasta lograr un resultado satisfactorio.

Paso 16 — Determinación de Desplazamientos Laterales (Artículo 31): Se calculan los desplazamientos laterales de acuerdo a las indicaciones de este numeral.

Paso 17 — Distorsión Admisible (Artículo 32): Verificar que la distorsión máxima de entrepiso que se obtiene en la estructura con los desplazamientos calculados en el paso anterior sea menor que lo indicado en la Tabla N°11. De no cumplir se revisa la estructuración y repite el análisis hasta cumplir con el requerimiento.

Paso 18 — Separación entre Edificios (Artículo 33): Determinar la separación mínima a otras edificaciones o al límite de propiedad de acuerdo a las indicaciones de este numeral.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite (ej. cada paso del Anexo, redactado como un solo
    parrafo denso) se divide por oracion, y si aun asi excede, por coma."""
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
