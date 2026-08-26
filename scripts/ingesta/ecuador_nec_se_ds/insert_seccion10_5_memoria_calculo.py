"""
Inserta el núcleo verbatim real de la Sección 10.5 (Memoria de cálculo)
de la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks -- a
pedido explícito del usuario ("sigamos con 10.5, memoria de cálculo").

Verificado antes de escribir: no había NADA de 10.5 en el corpus
todavía (búsqueda por id '%S10_5%'/'%MEMORIA_CALCULO%' vacía).

Sección corta (1 página, 127) pero con contenido de valor práctico
directo: los requisitos mínimos de contenido de la memoria de cálculo
estructural que el diseñador debe adjuntar a los planos -- lo más
cercano en esta norma a un checklist de entregable profesional, lo que
la hace especialmente citable para el chat real de StructAI.

Cubre: contenido general de la memoria (materiales, sistema
estructural, aprobación municipal, suelo de cimentación, cargas,
parámetros sísmicos de diseño, derivas), el estudio geotécnico mínimo
que debe acompañarla, y el requisito adicional de revisión del
comportamiento inelástico (obligatorio para estructuras esenciales y
de ocupación especial).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion10_5_memoria_calculo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 10.5 — Memoria de Cálculo"

CHUNKS = [
    {
        "id": "NECSEDS-S10_5-CONTENIDO_GENERAL_MEMORIA",
        "seccion": "10.5",
        "titulo": "Contenido mínimo de la memoria de cálculo: materiales, sistema estructural, aprobación municipal, suelo de cimentación, cargas, parámetros sísmicos, derivas",
        "texto": (
            "NEC-SE-DS, Sección 10.5 — Memoria de cálculo. La memoria de "
            "cálculo que el diseñador debe adjuntar a los planos "
            "estructurales incluirá una descripción de:\n"
            "  los materiales a utilizarse y sus especificaciones "
            "técnicas;\n"
            "  el sistema estructural escogido (deberá ser suscrito y "
            "aprobado por la autoridad competente de los municipios);\n"
            "  el tipo, características y parámetros mecánicos del "
            "suelo de cimentación considerado (estipulado en la memoria "
            "del estudio geotécnico);\n"
            "  el tipo y nivel de cargas seleccionadas, así como sus "
            "combinaciones;\n"
            "  los parámetros utilizados para definir las fuerzas "
            "sísmicas de diseño;\n"
            "  el espectro de diseño o cualquier otro método de "
            "definición de la acción sísmica utilizada;\n"
            "  los desplazamientos y derivas máximas que presente la "
            "estructura."
        ),
    },
    {
        "id": "NECSEDS-S10_5-ESTUDIO_GEOTECNICO_MINIMO",
        "seccion": "10.5",
        "titulo": "El estudio geotécnico que acompaña la memoria debe incluir: exploración, ensayos de laboratorio, caracterización del subsuelo, estados límite de falla, capacidad de carga, asentamientos estimados",
        "texto": (
            "La memoria de cálculo se acompaña del estudio geotécnico, "
            "que debe contener como mínimo:\n"
            "  una descripción de la exploración geotécnica;\n"
            "  los resultados de los ensayos de laboratorio de mecánica "
            "de suelos;\n"
            "  la caracterización geotécnica del subsuelo;\n"
            "  los análisis de los estados límite de falla;\n"
            "  su capacidad de carga;\n"
            "  los asentamientos estimados de la cimentación "
            "seleccionada durante su vida útil, tanto ante cargas "
            "permanentes como accidentales."
        ),
    },
    {
        "id": "NECSEDS-S10_5-REVISION_COMPORTAMIENTO_INELASTICO",
        "seccion": "10.5",
        "titulo": "Requisito adicional: descripción de la revisión del comportamiento inelástico (diseño por capacidad o verificación de desempeño); obligatoria para estructuras esenciales/ocupación especial ante eventos severos",
        "texto": (
            "Adicionalmente, la memoria debe incluir una descripción de "
            "la revisión del comportamiento inelástico, acorde con la "
            "filosofía de diseño de la sección 4.2 — ya sea con "
            "criterios de diseño por capacidad de elementos "
            "estructurales y sus conexiones, o mediante la verificación "
            "del correcto desempeño de la estructura en el rango "
            "inelástico, al someterse a los niveles de eventos sísmicos "
            "especificados en la norma.\n\n"
            "La verificación del correcto desempeño en el rango "
            "inelástico ante eventos sísmicos severos es indispensable "
            "para estructuras de ocupación especial y esenciales, con "
            "los requisitos definidos en la sección 4.2.4 de esta norma."
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
