"""
Inserta el núcleo verbatim real del Capítulo IX (Instrumentación,
Artículos 50-53) de la norma E.030 de Perú en peru_e030_chunks. Noveno y
ÚLTIMO bloque del cuerpo principal del corpus, después de los Capítulos
I-VIII (ver los otros insert_capituloN_*.py -- mismo texto oficial del
MVCS, misma base legal de citación verbatim, Art. 9(b) del Decreto
Legislativo N° 822). Con este capítulo, toda la norma E.030 (excepto los
Anexos I y II) queda cargada verbatim en Supabase.

Cubre: qué es una estación acelerométrica y cuándo es obligatoria (área
techada ≥10.000 m², o edificios de más de 20 pisos / con aislamiento o
disipación sísmica requieren una segunda estación en la azotea),
requisitos de ubicación, mantenimiento a cargo del propietario supervisado
por el IGP (responsabilidad de 10 años), y disponibilidad pública de los
datos registrados vía la Red Sísmica Nacional.

Uso: python scripts/ingesta/peru_e030/insert_capitulo9_instrumentacion.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo IX — Instrumentación"

CHUNKS = [
    {
        "id": "E030-CAP9-ART50-ESTACIONES_ACELEROMETRICAS",
        "seccion": "Artículo 50",
        "titulo": "Estaciones Acelerométricas (obligatorias en edificios ≥10.000 m², segunda estación en azotea si >20 pisos o con aislamiento/disipación)",
        "texto": """CAPÍTULO IX — INSTRUMENTACIÓN

Artículo 50.- Estaciones Acelerométricas

50.1. Una estación acelerométrica es un espacio seguro con un área adecuada, que contiene un sensor triaxial de aceleraciones, un sistema de registro, almacenamiento y transmisión de la señal, desde el punto de registro al centro de procesamiento. La estación debe poseer las condiciones apropiadas para el correcto registro de las vibraciones sísmicas, control de tiempo y energía eléctrica estable y segura.

50.2. Las estaciones acelerométricas son provistas por el propietario y deben cumplir con las especificaciones técnicas establecidas por el Instituto Geofísico del Perú (IGP), conforme al documento "Especificaciones Técnicas para Registradores Acelerométricos y requisitos mínimos para su instalación, operación y mantenimiento".

50.3. Las edificaciones que, individualmente o en forma conjunta, tengan un área techada igual o mayor que 10 000 m², cuentan con una estación acelerométrica, instalada a nivel del terreno natural o en la base del edificio.

50.4. En edificaciones con más de 20 pisos o en aquellas con dispositivos de disipación sísmica o de aislamiento en la base, de cualquier altura, se requiere además de una estación acelerométrica en la base, otra adicional en la azotea o en el nivel inferior al techo.

50.5. La implementación de lo establecido en el presente artículo forma parte de las otras instalaciones en funcionamiento de los bienes y servicios comunes del nivel casco habitable de la edificación.""",
    },
    {
        "id": "E030-CAP9-ART51-REQUISITOS_UBICACION",
        "seccion": "Artículo 51",
        "titulo": "Requisitos para la Ubicación de la Estación Acelerométrica (acceso, alejada de ruido antrópico, plan de instrumentación en planos)",
        "texto": """Artículo 51.- Requisitos para su Ubicación

51.1. La estación acelerométrica se instala en un área adecuada, con acceso fácil para su mantenimiento y apropiada iluminación, ventilación, suministro de energía eléctrica estabilizada.

51.2. El área está alejada de fuentes generadoras de cualquier tipo de ruido antrópico.

51.3. El plan de instrumentación es preparado por los proyectistas de cada especialidad, indicándose claramente en los planos de arquitectura, estructuras e instalaciones del edificio.""",
    },
    {
        "id": "E030-CAP9-ART52_53-MANTENIMIENTO_DISPONIBILIDAD",
        "seccion": "Artículos 52 y 53",
        "titulo": "Mantenimiento (responsabilidad del propietario por 10 años, supervisado por el IGP) y Disponibilidad Pública de los Datos (Red Sísmica Nacional)",
        "texto": """Artículo 52.- Mantenimiento

El mantenimiento operativo de las partes, de los componentes, del material fungible, así como el servicio de los instrumentos, son provistos por los propietarios del edificio y/o departamentos, bajo control de la municipalidad y es supervisado por el IGP. La responsabilidad del propietario se mantiene por 10 años.

Artículo 53.- Disponibilidad de Datos

La información registrada por los instrumentos es integrada a la base de datos de la Red Sísmica Nacional, a cargo del IGP y se encuentra a disposición del público en general.""",
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
