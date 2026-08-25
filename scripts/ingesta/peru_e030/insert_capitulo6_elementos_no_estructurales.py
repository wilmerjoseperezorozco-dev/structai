"""
Inserta el núcleo verbatim real del Capítulo VI (Elementos No
Estructurales, Apéndices y Equipos, Artículos 36-43) de la norma E.030 de
Perú en peru_e030_chunks. Sexto bloque del corpus, después de los
Capítulos I-V (ver los otros insert_capituloN_*.py -- mismo texto oficial
del MVCS, misma base legal de citación verbatim, Art. 9(b) del Decreto
Legislativo N° 822).

Cubre: qué se considera elemento no estructural (cercos, tabiques,
cielos rasos, vidrios, instalaciones hidráulicas/eléctricas/de gas,
equipos mecánicos, mobiliario riesgoso), responsabilidad profesional
explícita de proveerles resistencia sísmica adecuada, fuerzas de diseño
(fórmula F = ai/g·C1·Pe con la Tabla N°12 de valores C1 por tipo de
elemento), fuerza horizontal mínima, fuerzas sísmicas verticales,
elementos en la base/sótanos/cercos, otras estructuras (letreros,
chimeneas, antenas), y el factor de conversión 0,8 para diseño por
esfuerzos admisibles.

Uso: python scripts/ingesta/peru_e030/insert_capitulo6_elementos_no_estructurales.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo VI — Elementos No Estructurales, Apéndices y Equipos"

CHUNKS = [
    {
        "id": "E030-CAP6-ART36-GENERALIDADES",
        "seccion": "Artículo 36",
        "titulo": "Generalidades — qué se considera elemento no estructural (cercos, tabiques, instalaciones, equipos, mobiliario)",
        "texto": """Artículo 36.- Generalidades

36.1. Se consideran como elementos no estructurales aquellos que, estando conectados o no al sistema resistente a fuerzas horizontales, aportan masa al sistema pero su aporte a la rigidez no es significativo.

36.2. Para los elementos no estructurales que estén unidos al sistema estructural sismorresistente y acompañen la deformación de la estructura se asegura que en caso de falla no causen daños.

36.3. Dentro de los elementos no estructurales que tienen adecuada resistencia y rigidez para acciones sísmicas se incluyen: a) Cercos, tabiques, parapetos, paneles prefabricados. b) Elementos arquitectónicos y decorativos entre ellos cielos rasos, enchapes. c) Vidrios y muro cortina. d) Instalaciones hidráulicas y sanitarias. e) Instalaciones eléctricas. f) Instalaciones de gas. g) Equipos mecánicos. h) Mobiliario cuya inestabilidad signifique un riesgo.""",
    },
    {
        "id": "E030-CAP6-ART37_38-RESPONSABILIDAD_FUERZAS_DISENO",
        "seccion": "Artículos 37 y 38",
        "titulo": "Responsabilidad Profesional y Fuerzas de Diseño (fórmula F=ai/g·C1·Pe, Tabla N°12 de valores C1)",
        "texto": """Artículo 37.- Responsabilidad Profesional

Los profesionales que elaboran los diferentes proyectos son responsables de proveer a los elementos no estructurales la adecuada resistencia y rigidez para acciones sísmicas.

Artículo 38.- Fuerzas de Diseño

38.1. Los elementos no estructurales, sus anclajes, y sus conexiones se diseñan para resistir una fuerza sísmica horizontal en cualquier dirección (F) asociada a su peso (Pe), cuya resultante puede suponerse aplicada en el centro de masas del elemento: F = (ai/g) · C1 · Pe. Donde ai es la aceleración horizontal en el nivel donde el elemento no estructural está soportado o anclado al sistema estructural de la edificación; esta aceleración depende de las características dinámicas del sistema estructural de la edificación y se evalúa mediante un análisis dinámico de la estructura.

Alternativamente puede utilizarse la siguiente ecuación: F = (Fi/Pi) · C1 · Pe. Donde Fi es la fuerza lateral en el nivel donde se apoya o se ancla el elemento no estructural, calculada de acuerdo al artículo 28, y Pi el peso de dicho nivel. Los valores de C1 se toman de la Tabla N° 12.

Tabla N° 12 — Valores de C1: elementos que al fallar puedan precipitarse fuera de la edificación y cuya falla entrañe peligro para personas u otras estructuras → C1=3,0. Muros y tabiques dentro de una edificación → C1=2,0. Tanques sobre la azotea, casa de máquinas, pérgolas, parapetos en la azotea → C1=3,0. Equipos rígidos conectados rígidamente al piso → C1=1,5.

38.2. Para calcular las solicitaciones de diseño en muros, tabiques, parapetos y en general elementos no estructurales con masa distribuida, la fuerza F se convierte en una carga uniformemente distribuida por unidad de área. Para muros y tabiques soportados horizontalmente en dos niveles consecutivos, se toma el promedio de las aceleraciones de los dos niveles.""",
    },
    {
        "id": "E030-CAP6-ART39_40-FUERZA_MINIMA_VERTICAL",
        "seccion": "Artículos 39 y 40",
        "titulo": "Fuerza Horizontal Mínima (0,5·Z·U·S·Pe) y Fuerzas Sísmicas Verticales",
        "texto": """Artículo 39.- Fuerza Horizontal Mínima

En ningún nivel del edificio la fuerza F calculada con el artículo 38 es menor que: 0,5 · Z · U · S · Pe.

Artículo 40.- Fuerzas Sísmicas Verticales

40.1. La fuerza sísmica vertical se considera como 2/3 de la fuerza horizontal.

40.2. Para equipos soportados por elementos de grandes luces, incluyendo volados, se requiere un análisis dinámico con los espectros definidos en el subnumeral 29.2.2.""",
    },
    {
        "id": "E030-CAP6-ART41_42_43-BASE_OTRAS_ESTRUCTURAS_ESFUERZOS",
        "seccion": "Artículos 41, 42 y 43",
        "titulo": "Elementos en la Base/Sótanos/Cercos, Otras Estructuras (letreros, chimeneas, antenas), y Diseño por Esfuerzos Admisibles",
        "texto": """Artículo 41.- Elementos no Estructurales Localizados en la Base de la Estructura, por Debajo de la Base y Cercos

Los elementos no estructurales localizados a nivel de la base de la estructura o por debajo de ella (sótanos) y los cercos se diseñan con una fuerza horizontal calculada con: F = 0,5 · Z · U · S · Pe.

Artículo 42.- Otras Estructuras

Para letreros, chimeneas, torres y antenas de comunicación instaladas en cualquier nivel del edificio, la fuerza de diseño se establece considerando las propiedades dinámicas del edificio y de la estructura a instalar. La fuerza de diseño no es menor que la correspondiente a la calculada con la metodología propuesta en este capítulo con un valor de C1 mínimo de 3,0.

Artículo 43.- Diseño Utilizando el Método de los Esfuerzos Admisibles

Cuando el elemento no estructural o sus anclajes se diseñen utilizando el Método de los Esfuerzos Admisibles, las fuerzas sísmicas definidas en este Capítulo se multiplican por 0,8.""",
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
