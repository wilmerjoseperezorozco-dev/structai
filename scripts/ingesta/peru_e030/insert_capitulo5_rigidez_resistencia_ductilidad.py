"""
Inserta el núcleo verbatim real del Capítulo V (Requisitos de Rigidez,
Resistencia y Ductilidad, Artículos 31-35) de la norma E.030 de Perú en
peru_e030_chunks. Quinto bloque del corpus, después de los Capítulos I-IV
(ver los otros insert_capituloN_*.py -- mismo texto oficial del MVCS,
misma base legal de citación verbatim, Art. 9(b) del Decreto Legislativo
N° 822).

Cubre: cálculo de desplazamientos laterales (0,75R para estructuras
regulares, 0,85R para irregulares), límites de distorsión de entrepiso por
material (Tabla N°11), separación mínima entre edificios (fórmula
s=0,006h≥0,03m), redundancia estructural (elemento que toma ≥30% del
cortante se diseña para 125%), y verificación de resistencia última
(remisión opcional a ASCE/SEI 41).

Es el capítulo más corto de la norma en número de artículos, pero la Tabla
N°11 (límites de distorsión) es de las tablas más consultadas en la
práctica -- define directamente si un diseño pasa o no la verificación de
derivas.

Uso: python scripts/ingesta/peru_e030/insert_capitulo5_rigidez_resistencia_ductilidad.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo V — Requisitos de Rigidez, Resistencia y Ductilidad"

CHUNKS = [
    {
        "id": "E030-CAP5-ART31-DESPLAZAMIENTOS_LATERALES",
        "seccion": "Artículo 31",
        "titulo": "Determinación de Desplazamientos Laterales (0,75R regulares, 0,85R irregulares)",
        "texto": """Artículo 31.- Determinación de Desplazamientos Laterales

31.1. Para estructuras regulares, los desplazamientos laterales se calculan multiplicando por 0,75 R los resultados obtenidos del análisis lineal y elástico con las solicitaciones sísmicas reducidas. Para estructuras irregulares, los desplazamientos laterales se calculan multiplicando por 0,85 R los resultados obtenidos del análisis lineal elástico.

31.2. Para el cálculo de los desplazamientos laterales no se consideran los valores mínimos de C/R indicados en el numeral 28.2 ni el cortante mínimo en la base especificado en el numeral 29.4.""",
    },
    {
        "id": "E030-CAP5-ART32-DISTORSION_TABLA11",
        "seccion": "Artículo 32",
        "titulo": "Desplazamientos Laterales Relativos Admisibles (Tabla N°11: límites de distorsión por material)",
        "texto": """Artículo 32.- Desplazamientos Laterales Relativos Admisibles

El máximo desplazamiento relativo de entrepiso, calculado según el artículo 31, no excede la fracción de la altura de entrepiso (distorsión) que se indica en la Tabla N° 11.

Tabla N° 11 — Límites para la Distorsión del Entrepiso (Δi/hei): Concreto Armado → 0,007. Acero → 0,010. Albañilería → 0,005. Madera → 0,010. Edificios de concreto armado con muros de ductilidad limitada → 0,005.

Nota de la Tabla N° 11: los límites de la distorsión (deriva) para estructuras de uso industrial son establecidos por el proyectista, pero en ningún caso exceden el doble de los valores de esta Tabla.""",
    },
    {
        "id": "E030-CAP5-ART33-SEPARACION_EDIFICIOS",
        "seccion": "Artículo 33",
        "titulo": "Separación entre Edificios (s) — fórmula s=0,006h≥0,03m, retiro de límites de propiedad",
        "texto": """Artículo 33.- Separación entre Edificios (s)

33.1. Toda estructura está separada de las estructuras vecinas, desde el nivel del terreno natural, una distancia mínima s para evitar el contacto durante un movimiento sísmico.

33.2. Esta distancia no es menor que los 2/3 de la suma de los desplazamientos máximos de los edificios adyacentes ni menor que: s = 0,006·h ≥ 0,03 m. Donde h es la altura medida desde el nivel del terreno natural hasta el nivel considerado para evaluar s.

33.3. El edificio se retira de los límites de propiedad adyacentes a otros lotes edificables, o con edificaciones, distancias no menores que 2/3 del desplazamiento máximo calculado según el artículo 31 ni menores que s/2 si la edificación existente cuenta con una junta sísmica reglamentaria.

33.4. En caso de que no exista la junta sísmica reglamentaria, el edificio se separa de la edificación existente el valor de s/2 que le corresponde más el valor s/2 de la estructura vecina.""",
    },
    {
        "id": "E030-CAP5-ART34_35-REDUNDANCIA_RESISTENCIA_ULTIMA",
        "seccion": "Artículos 34 y 35",
        "titulo": "Redundancia (diseño al 125% si un elemento toma ≥30% del cortante) y Verificación de Resistencia Última (ASCE/SEI 41, opcional)",
        "texto": """Artículo 34.- Redundancia

Cuando sobre un solo elemento de la estructura, muro o pórtico, actúa una fuerza de 30% o más del total de la fuerza cortante horizontal en cualquier entrepiso, dicho elemento se diseña para el 125% de dicha fuerza.

Artículo 35.- Verificación de Resistencia Última

En caso se realice un análisis de la resistencia última se puede utilizar las especificaciones del ASCE/SEI 41 "Seismic Rehabilitation of Existing Buildings". Esta disposición no constituye una exigencia de la presente Norma.""",
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
