"""
NSR-10 Titulo G, numerales hoja reales confirmados sin chunk propio en
la re-auditoria estricta 2026-09-09 (ver docs/fuentes-normativas.md,
fila de Titulo G, ~24 de 488 numerales, ~5%).

De los 27 candidatos originales del diff crudo, 18 se confirmaron con
spot-check leyendo el PDF real (encabezado + contenido verbatim
localizado); 9 se descartaron por ser ruido de extraccion (referencias
de tabla/ecuacion embebidas en celdas de coeficientes -- mismo patron
"numero de ecuacion confundido con numeral" ya visto en Titulo C -- o
citas cruzadas sin encabezado propio localizable en los 3 PDF fuente:
G.2.2.4, G.2.2.5, G.2.3, G.3.3.4.4, G.4.3.10, G.4.6.2.8, G.5.1.1,
G.12.16, G.32).

Hallazgo real de un typo del documento fuente, corregido y documentado
(mismo criterio que la mislabeling de A.3.6 en Titulo A): el PDF
imprime "G.12.4.2.2" para un numeral que por su posicion real (entre
G.12.3.2.1 y G.12.3.2.3, dentro de "G.12.3.2 -- CLASIFICACION VISUAL
POR DEFECTOS") es en realidad G.12.3.2.2 -- se ingesta con el id
correcto G.12.3.2.2, con nota del typo en el titulo del chunk.

Fuente: NSR-10-1284-1320.pdf y NSR-10-1321-1400.pdf (mismos 2 PDF ya
descargados en la auditoria original, mas las primeras 38 paginas de
NSR-10-1401-1450.pdf que no se necesitaron aqui), paginas confirmadas
leyendo visualmente cada una.

Uso: python _ingest_titulo_g_24_numerales_faltantes.py
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

CAPITULO = "NSR-10 Título G — Estructuras de Madera y de Guadua"

CHUNKS = [
    {
        "id": "NSR10-G-G_2_1_6_limite_temperatura",
        "seccion": "G.2.1.6 (Límite de Temperatura para Estructuras de Madera)",
        "titulo": "Prohibición de usar estructuras de madera en ambientes que excedan 65°C.",
        "texto": (
            "NSR-10 Título G, Capítulo G.2 — G.2.1.6 — En ningún caso se deben "
            "utilizar estructuras de madera cuando la temperatura a la cual van "
            "a estar sometidas exceda 65°C."
        ),
    },
    {
        "id": "NSR10-G-G_6_2_3_a_5_definiciones_uniones",
        "seccion": "G.6.2.3 y G.6.2.5 (Pieza Solicitada y Borde Descargado)",
        "titulo": "Definiciones de pieza solicitada (mayor desviación entre fuerza y fibra) y borde descargado, dentro del capítulo de uniones.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.2.3 — PIEZA SOLICITADA — Pieza "
            "de la unión que presenta la mayor desviación, entre la fuerza "
            "trasmitida y la dirección de la fibra. G.6.2.5 — BORDE DESCARGADO "
            "— Borde que no corresponde a la definición de borde cargado (G.6.2.4: "
            "borde de la pieza afectado por la acción de la fuerza que transmite "
            "el medio de unión)."
        ),
    },
    {
        "id": "NSR10-G-G_6_7_7_capacidad_cortante_multiple",
        "seccion": "G.6.7.7 (Capacidad Admisible en Cortante Múltiple)",
        "titulo": "Ecuación G.6.7-3 para la capacidad admisible por clavo en uniones de cortante múltiple.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.7.7 — En uniones de cortante "
            "múltiple la capacidad admisible Pem, de cada clavo, será calculada "
            "por la siguiente fórmula: Pem = (m − 0.25) Pes (G.6.7-3). En donde: "
            "Pem = capacidad de carga de un clavo en uniones de cortante "
            "múltiple, en N. Pes = capacidad de carga de un clavo en uniones de "
            "cortante simple en N. m = número de planos de cortante que "
            "atraviesa el clavo."
        ),
    },
    {
        "id": "NSR10-G-G_6_7_11_tableros_contrachapados",
        "seccion": "G.6.7.11 (Uniones Clavadas de Tableros Contrachapados Fenólicos)",
        "titulo": "Espesor mínimo requerido (t ≥ 4d) en uniones clavadas de tableros contrachapados fenólicos de al menos 4 chapas.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.7.11 — En uniones clavadas de "
            "tableros contrachapados fenólicos de al menos 4 chapas, el espesor "
            "será, t ≥ 4d."
        ),
    },
    {
        "id": "NSR10-G-G_6_9_2_clavos_lanceros",
        "seccion": "G.6.9.2 (Carga Lateral Admisible para Clavos Lanceros)",
        "titulo": "Factor de reducción (0.83) para clavos lanceros sobre los valores de la Tabla G.6.9-1.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.9.2 — La carga lateral admisible "
            "para clavos lanceros podrá tomarse como (0.83), de los valores de "
            "la tabla G.6.9-1."
        ),
    },
    {
        "id": "NSR10-G-G_6_14_1_3_penetracion_tirafondos",
        "seccion": "G.6.14.1.3 (Penetración Mínima de Tirafondos)",
        "titulo": "Penetración mínima de cuatro veces el diámetro del vástago más la longitud de la punta, para tirafondos.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.14.1.3 — Los tirafondo deberán "
            "tener una penetración mínima de cuatro (4) veces el diámetro del "
            "vástago más la longitud de la punta."
        ),
    },
    {
        "id": "NSR10-G-G_6_15_3_a_4_tornillos_goloso",
        "seccion": "G.6.15.3 y G.6.15.4 (Penetración Mínima y Cantidad Mínima de Tornillos Golosos)",
        "titulo": "Penetración mínima (6 veces el diámetro) y cantidad mínima (3 tornillos) por unión, para tornillos golosos.",
        "texto": (
            "NSR-10 Título G, Capítulo G.6 — G.6.15.3 — Los tornillos deberán "
            "tener una penetración mínima de seis (6) veces el diámetro del "
            "vástago. G.6.15.4 — Cada unión deberá contar con un mínimo de tres "
            "(3) tornillos."
        ),
    },
    {
        "id": "NSR10-G-G_12_3_2_2_conicidad_guadua",
        "seccion": "G.12.3.2.2 (Conicidad Máxima de Piezas de Guadua Estructural — nota de typo del documento fuente)",
        "titulo": "Límite de conicidad (1.0%) para piezas de guadua estructural — el PDF fuente lo imprime erróneamente como \"G.12.4.2.2\", corregido a G.12.3.2.2 por su posición real entre G.12.3.2.1 y G.12.3.2.3.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.3.2 — CLASIFICACIÓN VISUAL POR "
            "DEFECTOS — G.12.3.2.2 — Las piezas de guadua estructural no deben "
            "presentar una conicidad superior al 1.0%. (Nota: el documento fuente "
            "imprime este numeral como \"G.12.4.2.2\" por error tipográfico — su "
            "ubicación real, entre G.12.3.2.1 y G.12.3.2.3, confirma que el "
            "numeral correcto es G.12.3.2.2)."
        ),
    },
    {
        "id": "NSR10-G-G_12_3_2_6_a_7_pudricion_preservacion",
        "seccion": "G.12.3.2.6 y G.12.3.2.7 (Pudrición y Preservación/Secado de Guadua)",
        "titulo": "Prohibición de guaduas con pudrición y remisión a la norma NTC 5301 para preservación y secado.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.3.2.6 — No se aceptan guaduas "
            "que presenten algún grado de pudrición. G.12.3.2.7 — Todo proceso de "
            "preservación y secado de piezas de guadua rolliza debe seguir lo "
            "estipulado en la norma NTC 5301."
        ),
    },
    {
        "id": "NSR10-G-G_12_6_2_1_a_5_requisitos_calidad_guadua",
        "seccion": "G.12.6.2.1 y G.12.6.2.5 (Requisitos de Diseñador Profesional y Uso Constante de la Estructura de Guadua)",
        "titulo": "Requisito de diseño por profesional habilitado (Ley 400 de 1997) y de mantener el mismo uso durante la vida útil de la estructura de guadua.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.6.2 — REQUISITOS DE CALIDAD "
            "PARA LAS ESTRUCTURAS EN GUADUA — G.12.6.2.1 — Las estructuras sean "
            "diseñadas por un profesional que cumpla los requisitos al respecto "
            "de la Ley 400 de 1997. G.12.6.2.5 — La estructura debe tener durante "
            "toda su vida útil el mismo uso para el cual fue diseñada."
        ),
    },
    {
        "id": "NSR10-G-G_12_6_7_limite_temperatura_guadua",
        "seccion": "G.12.6.7 (Límite de Temperatura para Estructuras de Guadua)",
        "titulo": "Prohibición de usar estructuras de guadua en ambientes que excedan 65°C — mismo límite que G.2.1.6 para madera.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.6.7 — En ningún caso de debe "
            "utilizar estructuras de guadua cuando la temperatura a la cual van "
            "a estar sometidas exceda 65° C."
        ),
    },
    {
        "id": "NSR10-G-G_12_7_5_coeficientes_modificacion",
        "seccion": "G.12.7.5 (Coeficientes de Modificación para Guadua)",
        "titulo": "Ecuación G.12.7-3 y glosario de los 8 coeficientes de modificación (CD, Cm, Ct, CL, CF, Cr, Cp, Cc) aplicados a esfuerzos admisibles de guadua.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.7.5 — COEFICIENTES DE "
            "MODIFICACIÓN — Con base en los valores de esfuerzos admisibles de "
            "la tabla G.12.7-1 y los módulos de elasticidad de la tabla G.12.7-2, "
            "afectados por los coeficientes de modificación a que haya lugar por "
            "razón del tamaño, nudos, grietas, contenido de humedad, duración de "
            "carga, esbeltez y cualquier otra condición modificatoria, se "
            "determinan las solicitaciones admisibles de todo miembro "
            "estructural, según las prescripciones de los numerales siguientes, "
            "con los esfuerzos admisibles modificados de acuerdo con la fórmula "
            "general: F'i = Fi·CD·Cm·Ct·CL·CF·Cr·Cp·Cc (G.12.7-3). Donde: i = "
            "tiene el mismo significado que en el numeral anterior. CD = "
            "coeficiente de modificación por duración de carga. Cm = coeficiente "
            "de modificación por contenido de humedad. Ct = coeficiente de "
            "modificación por temperatura. CL = coeficiente de modificación por "
            "estabilidad lateral de vigas. CF = coeficiente de modificación por "
            "forma. Cr = coeficiente de modificación por redistribución de "
            "cargas, acción conjunta. Cp = coeficiente de modificación por "
            "estabilidad de columnas. Cc = coeficiente de modificación por "
            "cortante. Fi = esfuerzo admisible en la solicitación i. F'i = "
            "esfuerzo admisible modificado para la solicitación i. Los "
            "coeficientes de modificación de aplicación general se indican en "
            "los numerales siguientes; los que dependen de la clase de "
            "solicitación se estipulan en las secciones del Capítulo G.12 "
            "correspondientes."
        ),
    },
    {
        "id": "NSR10-G-G_12_8_6_3_tamano_max_perforacion",
        "seccion": "G.12.8.6.3 (Tamaño Máximo de Perforación en Vigas de Guadua)",
        "titulo": "Límite de 3.81 mm para el tamaño máximo de perforaciones permitidas en vigas de guadua.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.8.6.3 — El tamaño máximo de "
            "la perforación será de 3.81 mm."
        ),
    },
    {
        "id": "NSR10-G-G_12_8_10_2_coeficientes_flexion",
        "seccion": "G.12.8.10.2 (Coeficientes de Modificación Particulares para Flexión)",
        "titulo": "Remisión introductoria a los coeficientes de modificación específicos de flexión, desarrollados en los numerales siguientes.",
        "texto": (
            "NSR-10 Título G, Capítulo G.12 — G.12.8.10 — FLEXIÓN — G.12.8.10.2 "
            "— Los coeficientes de modificación particulares para flexión son "
            "los que se indican a continuación."
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
    tokenizer = model.tokenizer

    print("\nSub-particionando por tokens REALES (limite 128, medido con el tokenizer)...")
    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            n_tok = len(tokenizer.encode(pieza, add_special_tokens=True))
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })
            print(f"  {chunk['id'] + sufijo:60s} {n_tok:3d} tokens")
    print(f"\n{len(CHUNKS)} piezas originales -> {len(piezas_finales)} piezas reales tras troceo.")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for pieza, vec in zip(piezas_finales, vectores):
        rows.append({
            "id": pieza["id"],
            "capitulo": CAPITULO,
            "seccion": pieza["seccion"],
            "titulo": pieza["titulo"][:500],
            "texto": pieza["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de los 14 grupos (18 numerales) de Título G cargados.")


if __name__ == "__main__":
    main()
