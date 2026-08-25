"""
Inserta el núcleo verbatim real de las 3 últimas secciones pendientes de
la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks: Sección 2
(Alcances del capítulo y objetivos de seguridad sísmica, 2 páginas),
Sección 8 (Sistemas de control y aislamiento a la base, 2 páginas), y
Sección 9 (Estructuras diferentes a las de edificación, 3 páginas --
9.3.7/Tabla 15 ya estaba cargada de una sesión anterior, confirmado por
consulta directa antes de escribir este script, no se repite).

Con este script, el CUERPO PRINCIPAL COMPLETO de la NEC-SE-DS de
Ecuador (Secciones 1-9, 10.2 poblaciones) queda 100% cargado en
Supabase -- mismo hito que ya se alcanzó con la E.030 de Perú.

Cubre: 2.1 (objetivos y alcances, niveles de amenaza), 2.2 (actores y
responsabilidades, cumplimiento obligatorio nacional), 2.3 (bases del
diseño); 8 (fuente BSSC 2004/FEMA 450), 8.1 (alcance: aislamiento
sísmico/disipación pasiva/control activo), 8.2.1-8.2.2 (requisito de
sistema estructural base, método estático, nota Z≥0,30 requiere no
lineal paso a paso), 8.3 (requisitos mínimos de aislamiento sísmico,
SD1/SM1), 8.4 (requisitos de disipación pasiva de energía); 9.1
(introducción, estructuras distintas a edificación), 9.2.1-9.2.3
(estructuras portuarias PIANC, puentes AASHTO, tanques con fondo
apoyado), 9.3.1-9.3.6 (peso W, período T, límites de deriva, efectos
de interacción, fórmula de fuerzas laterales V=η·Z·Fa·I·W para
estructuras rígidas, distribución de fuerzas).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_secciones2_8_9_cierre.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Secciones 2, 8, 9 — Alcances, Aislamiento y Estructuras No-Edificación"

CHUNKS = [
    {
        "id": "NECSEDS-S2_1-OBJETIVOS_ALCANCES",
        "seccion": "2.1",
        "titulo": "Objetivo del capítulo: evitar pérdida de vidas impidiendo el colapso; protección adicional de funcionalidad para estructuras esenciales/especiales; 4 niveles de amenaza sísmica",
        "texto": (
            "NEC-SE-DS, Sección 2.1 — Objetivos y alcances. Se aplica la "
            "filosofía tradicional de diseño (sección 4.2). El objetivo "
            "de desempeño de esta filosofía es evitar la pérdida de "
            "vidas impidiendo el colapso de todo tipo de estructura. "
            "Para estructuras de ocupación especial y esencial, se "
            "añade el objetivo de mayor protección y garantía de "
            "funcionalidad tras un evento sísmico extremo (sección "
            "4.2.2). Las tendencias actuales a nivel mundial buscan "
            "además proteger la propiedad y cumplir diversos niveles de "
            "desempeño sísmico para cualquier tipo de estructura.\n\n"
            "Las especificaciones de este capítulo son requisitos "
            "mínimos para el cálculo y diseño de edificios y, en segundo "
            "lugar, de otras estructuras, frente a eventos sísmicos, "
            "basados en comportamiento elástico lineal y no lineal. Para "
            "estructuras distintas a edificación (reservorios, tanques, "
            "silos, puentes, torres de transmisión, muelles, estructuras "
            "hidráulicas, presas, tuberías, etc., con comportamiento "
            "dinámico distinto), se deben aplicar consideraciones "
            "adicionales que complementen estos requisitos mínimos "
            "(sección 9).\n\n"
            "Niveles de frecuencia y amenaza sísmica considerados "
            "(sección 4.2.2): Frecuente (menor), Ocasional (moderado), "
            "Raro (severo) = sismo de diseño, período de retorno 475 "
            "años, y Muy raro (extremo) = para estructuras esenciales y "
            "de ocupación especial, período de retorno 2.500 años "
            "(sección 4.1)."
        ),
    },
    {
        "id": "NECSEDS-S2_2-ACTORES_RESPONSABILIDADES",
        "seccion": "2.2",
        "titulo": "Cumplimiento obligatorio a nivel nacional para todos los profesionales, empresas e instituciones públicas y privadas",
        "texto": (
            "NEC-SE-DS, Sección 2.2 — Actores y responsabilidades. Los "
            "requisitos establecidos en este capítulo son de "
            "cumplimiento obligatorio a nivel nacional. Todos los "
            "profesionales, empresas e instituciones públicas y privadas "
            "tienen la obligación de cumplir y hacer cumplir los "
            "requisitos mínimos aquí establecidos."
        ),
    },
    {
        "id": "NECSEDS-S2_3-BASES_DEL_DISENO",
        "seccion": "2.3",
        "titulo": "Bases del diseño: factor de zona Z, características del suelo, coeficiente de importancia I, y verificación inelástica para estructuras esenciales/especiales",
        "texto": (
            "NEC-SE-DS, Sección 2.3 — Bases del diseño. La respuesta de "
            "una edificación a solicitaciones sísmicas se caracteriza "
            "por aceleraciones, velocidades y desplazamientos de sus "
            "elementos (en particular los pisos, en edificios). Los "
            "procedimientos y requisitos de este capítulo se determinan "
            "considerando:\n"
            "  la zona sísmica del Ecuador y el factor de zona Z "
            "correspondiente (sección 3.1.2) y las curvas de peligro "
            "sísmico (secciones 3.1.2 y 10.3);\n"
            "  las características del suelo del sitio (sección 3.2);\n"
            "  el tipo de uso, destino e importancia (coeficiente de "
            "importancia I, sección 4.1);\n"
            "  las estructuras de uso normal deben diseñarse para "
            "soportar los desplazamientos laterales del sismo de "
            "diseño, considerando respuesta inelástica, redundancia, "
            "sobrerresistencia estructural inherente y ductilidad;\n"
            "  las estructuras de ocupación especial y esenciales "
            "aplican verificaciones de comportamiento inelástico para "
            "diferentes niveles de terremoto.\n\n"
            "La resistencia mínima de diseño para todas las estructuras "
            "se basa en las fuerzas sísmicas de diseño de este capítulo, "
            "considerando: el nivel de desempeño sísmico (sección "
            "4.2.4), el tipo de sistema y configuración estructural "
            "(sección 5.3), y los métodos de análisis empleados "
            "(secciones 6 y 7)."
        ),
    },
    {
        "id": "NECSEDS-S8-INTRO_ALCANCE_AISLAMIENTO",
        "seccion": "8 / 8.1",
        "titulo": "Sistemas de control y aislamiento a la base: fuente BSSC 2004/FEMA 450; 3 tipos — aislamiento sísmico, disipación pasiva de energía, control activo",
        "texto": (
            "NEC-SE-DS, Sección 8 — Sistemas de control y aislamiento a "
            "la base. Las fuentes principales de esta sección son los "
            "Capítulos 13 y 15 del BSSC (2004) 'NEHRP Recommended "
            "Provisions and Commentary for Seismic Regulations for New "
            "Buildings and Other Structures' (FEMA 450) — ver sección "
            "1.4.2.\n\n"
            "Sección 8.1 — Alcance. Los sistemas de control estructural "
            "para diseño sismo resistente no convencional (definidos en "
            "sección 1.2.2) se clasifican en: sistemas de aislamiento "
            "sísmico, sistemas de disipación pasiva de energía, y "
            "sistemas de control activo."
        ),
    },
    {
        "id": "NECSEDS-S8_2-REQUISITOS_DISENO_GENERALES",
        "seccion": "8.2",
        "titulo": "Sistema estructural sismo resistente base obligatorio (Tabla 12); si Z≥0,30 se requiere análisis no lineal paso a paso por profesional calificado",
        "texto": (
            "NEC-SE-DS, Sección 8.2.1 — Requisito de sistema estructural. "
            "Toda estructura que use sistemas de control sísmico debe "
            "poseer un sistema estructural sismo resistente básico de "
            "los tipos de la Tabla 12: Sistemas Estructurales Dúctiles "
            "(duales y pórticos resistentes a momentos) o Sistemas "
            "Estructurales de Ductilidad Limitada (pórticos resistentes "
            "a momento y muros estructurales portantes). El objetivo del "
            "cálculo es determinar el cortante basal mínimo.\n\n"
            "Sección 8.2.2 — Métodos de cálculo. El cálculo se hace con "
            "el método de cálculo estático de fuerzas sísmicas. Nota: si "
            "Z ≥ 0,30 (factor de zona), independientemente del método de "
            "análisis adoptado, la respuesta máxima de la estructura "
            "requiere un método de análisis no lineal paso a paso, "
            "realizado por personal profesional calificado en cálculo "
            "inelástico de estructuras con sistemas de control sísmico."
        ),
    },
    {
        "id": "NECSEDS-S8_3-REQUISITOS_AISLAMIENTO_SISMICO",
        "seccion": "8.3",
        "titulo": "Requisitos mínimos de aislamiento sísmico: Capítulo 13 del BSSC 2004/FEMA 450; parámetros SD1 (475 años) y SM1 (2.500 años)",
        "texto": (
            "NEC-SE-DS, Sección 8.3 — Requisitos mínimos de diseño de "
            "sistemas de aislamiento sísmico. El diseño sísmico de "
            "edificios con aislamiento sísmico usa como requisitos "
            "mínimos las especificaciones del Capítulo 13 del BSSC "
            "(2004) 'NEHRP Recommended Provisions...' (FEMA 450). Sin "
            "influencia del uso o la ocupación del edificio: el "
            "parámetro SD1 corresponde a la aceleración espectral para "
            "T=1s, período de retorno 475 años; el parámetro SM1 "
            "corresponde a la aceleración espectral para T=1s, período "
            "de retorno 2.500 años, tomando en cuenta el efecto del "
            "suelo de cimentación."
        ),
    },
    {
        "id": "NECSEDS-S8_4-REQUISITOS_DISIPACION_PASIVA",
        "seccion": "8.4",
        "titulo": "Requisitos de disipación pasiva de energía (amortiguadores sísmicos): Capítulo 15 del BSSC 2004/FEMA 450; espectro de diseño 475 años vs. espectro máximo considerado 2.500 años",
        "texto": (
            "NEC-SE-DS, Sección 8.4 — Requisitos de diseño de sistemas "
            "de disipación pasiva de energía. El diseño sísmico de "
            "edificios con disipación pasiva de energía (ej. "
            "amortiguadores sísmicos) usa como requerimientos mínimos "
            "las especificaciones del Capítulo 15 del BSSC (2004) "
            "'NEHRP Recommended Provisions...' (FEMA 450). Los espectros "
            "de amenaza sísmica se generan según las secciones "
            "anteriores de este capítulo. El espectro de diseño se "
            "refiere a un terremoto de período de retorno 475 años; el "
            "espectro máximo considerado se refiere a un período de "
            "retorno de 2.500 años."
        ),
    },
    {
        "id": "NECSEDS-S9_1-INTRODUCCION_ESTRUCTURAS_NO_EDIFICACION",
        "seccion": "9.1",
        "titulo": "Estructuras autoportantes distintas a edificios: reservorios, tanques, silos, torres de transmisión, tuberías, naves industriales — diseño complementario a las secciones anteriores",
        "texto": (
            "NEC-SE-DS, Sección 9.1 — Introducción. Las estructuras "
            "distintas a las de edificación incluyen todas las "
            "estructuras autoportantes que no son edificios, que "
            "soportan cargas verticales y deben resistir efectos "
            "sísmicos: reservorios, tanques, silos, torres de "
            "transmisión, estructuras hidráulicas, tuberías, naves "
            "industriales, etc., con comportamiento dinámico distinto al "
            "de las estructuras de edificación. Se diseñan para resistir "
            "las fuerzas laterales mínimas de esta sección, "
            "complementadas con consideraciones adicionales especiales "
            "por tipo de estructura. El diseño se hace conforme a los "
            "requisitos aplicables de las secciones anteriores, "
            "modificados según los numerales de esta sección. Para "
            "puentes y presas, se aplican las normas ecuatorianas "
            "correspondientes y, en su ausencia, las internacionalmente "
            "aceptadas."
        ),
    },
    {
        "id": "NECSEDS-S9_2-PORTUARIAS_PUENTES_TANQUES",
        "seccion": "9.2.1-9.2.3",
        "titulo": "Estructuras portuarias (guías PIANC), puentes (AASHTO Guide Specifications), tanques con fondo apoyado (análisis espectral o código internacional)",
        "texto": (
            "NEC-SE-DS, Sección 9.2.1 — Estructuras portuarias. Se "
            "adoptan los objetivos de desempeño, nivel de amenaza "
            "sísmica (probabilidad de excedencia o período de retorno) y "
            "niveles de desempeño estructural (estados límites) del "
            "PIANC (Permanent International Association for Navigation "
            "Congresses), Guías de diseño sísmico para estructuras "
            "portuarias. Los espectros de diseño se desarrollan con las "
            "curvas de amenaza sísmica del apéndice 10.3.\n\n"
            "Sección 9.2.2 — Puentes. Se adoptan los objetivos de "
            "desempeño, nivel de amenaza sísmica y niveles de desempeño "
            "estructural del AASHTO, Guide Specifications for LRFD "
            "Seismic Bridge Design. Espectros de diseño también con base "
            "en el apéndice 10.3.\n\n"
            "Sección 9.2.3 — Tanques con fondo apoyado. Los tanques con "
            "fondo apoyado directamente (o bajo) sobre el suelo, u "
            "apoyados sobre otros elementos estructurales, se diseñan "
            "con el procedimiento para estructuras rígidas (sección "
            "9.3.6), incluyendo todo el peso del tanque y su contenido. "
            "Alternativamente: análisis espectral (incluyendo el sismo "
            "esperado y los efectos de inercia de los fluidos), o un "
            "procedimiento de código internacional reconocido para "
            "tanques."
        ),
    },
    {
        "id": "NECSEDS-S9_3_1_a_9_3_4-PESO_PERIODO_DERIVA_INTERACCION",
        "seccion": "9.3.1-9.3.4",
        "titulo": "Peso W (incluye cargas muertas + contenido en operación normal), período T (Método 2/DBD), límites de deriva no obligatorios pero con verificación P-Δ, efectos de interacción si elementos flexibles >25% del peso",
        "texto": (
            "NEC-SE-DS, Sección 9.3.1 — Peso W. Incluye todas las cargas "
            "muertas. Para el cálculo de fuerzas laterales de diseño, W "
            "debe incluir todos los pesos de los contenidos de la "
            "estructura, en condiciones de operación normal.\n\n"
            "Sección 9.3.2 — Período fundamental T. Se calcula con "
            "métodos reconocidos de dinámica estructural, como el "
            "Método 2 (DBD, sección 7).\n\n"
            "Sección 9.3.3 — Límites de deriva. Los límites de deriva de "
            "edificios NO son obligatorios para este tipo de "
            "estructuras. Se deben establecer límites de deriva para "
            "elementos estructurales y no estructurales cuya falla "
            "podría poner en peligro la vida y seguridad. Sin embargo, "
            "los efectos P-Δ deben calcularse si las derivas exceden los "
            "límites establecidos para estructuras de edificación.\n\n"
            "Sección 9.3.4 — Efectos de interacción. Las estructuras que "
            "soportan elementos no estructurales flexibles cuyo peso "
            "combinado excede el 25% del peso de la estructura deben "
            "diseñarse considerando los efectos de interacción entre la "
            "estructura y esos elementos."
        ),
    },
    {
        "id": "NECSEDS-S9_3_5_9_3_6-FUERZAS_LATERALES_DISTRIBUCION",
        "seccion": "9.3.5-9.3.6",
        "titulo": "Fórmula de fuerza lateral para estructuras rígidas (T<0,6s): V=η·Z·Fa·I·W; distribución según distribución de masas, en cualquier dirección horizontal",
        "texto": (
            "NEC-SE-DS, Sección 9.3.5 — Fuerzas laterales. Para sistemas "
            "estructurales similares a edificaciones, se diseñan con los "
            "procedimientos de cálculo de fuerzas laterales últimas de "
            "edificación. Para estructuras rígidas (período menor a 0,6 "
            "s), se diseñan (incluidos sus anclajes) con la fuerza "
            "lateral:\n\n"
            "V = η · Z · Fa · I · W\n\n"
            "Donde: V = cortante total en la base de la estructura para "
            "el DBF; η = razón entre la aceleración espectral Sa(T=0,1s) "
            "y el PGA para el período de retorno seleccionado; Z = "
            "aceleración máxima en roca esperada para el sismo de "
            "diseño (fracción de g); Fa = coeficiente de amplificación "
            "de suelo en la zona de período corto; I = coeficiente de "
            "importancia; W = carga sísmica reactiva.\n\n"
            "Sección 9.3.6 — Distribución de las fuerzas laterales. La "
            "fuerza V calculada debe distribuirse según la distribución "
            "de masas, y debe aplicarse en cualquier dirección "
            "horizontal.\n\n"
            "Nota: 9.3.7 (Factor de reducción de respuesta R para "
            "estructuras diferentes a edificación, Tabla 15) ya está "
            "cargada en el corpus desde una sesión anterior — no se "
            "repite aquí."
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
