"""
Inserta el núcleo verbatim real de la Resolución 5018 de 2019 (Ministerio
del Trabajo) — Lineamientos en Seguridad y Salud en el Trabajo para los
Procesos de Generación, Transmisión, Distribución y Comercialización de la
Energía Eléctrica — en nsr10_chunks.

Contexto: esta norma no tenía NINGUNA fila en nsr10_chunks ni en ntc_chunks
antes de esta inserción (confirmado por consulta directa: 'norma in (...)'
sobre ntc_chunks no traía ningún registro con '5018').

Fuente: HTML de
https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=88299
(Régimen Legal de Bogotá D.C. — SISJUR, Secretaría Jurídica Distrital).
SUIN-Juriscol no tenía esta resolución indexada bajo búsqueda directa.
NO se usó ningún archivo "RAG+CAG" de Google Drive.

Alcance real de la norma: a diferencia de la Res. 0312/2019 o la Res.
4272/2021, el cuerpo articulado de la Res. 5018/2019 es corto (solo 5
artículos) — el contenido técnico detallado (requisitos específicos de
seguridad eléctrica) vive en un "Anexo Técnico" que forma parte integral
de la resolución pero que SISJUR no publica como texto navegable en esta
página (aparece solo como "Nota: Ver anexo." sin enlace descargable). Este
núcleo cubre el cuerpo articulado COMPLETO (los 5 artículos: objeto, campo
de aplicación, periodo de transición, sanciones, vigencia y derogatoria).
El Anexo Técnico queda pendiente para una ronda futura si se localiza una
fuente verbatim navegable.

Uso: python scripts/ingesta/sgsst/insert_res5018_2019_nucleo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO = "Resolución 5018 de 2019 — SST en Generación, Transmisión, Distribución y Comercialización de Energía Eléctrica"

CHUNKS = [
    {
        "id": "RES5018-2019-ART1_2",
        "capitulo": CAPITULO,
        "seccion": "Artículo 1 y 2",
        "titulo": "Objeto (lineamientos SST para el sector eléctrico) y campo de aplicación (empresas de generación/transmisión/distribución/comercialización y terceros con peligro eléctrico)",
        "texto": """Artículo 1°. Objeto. La presente resolución tiene por objeto expedir los lineamientos en seguridad y salud en el trabajo para las actividades ejecutadas en los procesos de generación de energía a través de fuentes convencionales y no convencionales de generación, transmisión, distribución y comercialización de energía eléctrica, para las empresas que presten o hagan uso del sistema eléctrico colombiano contenido en el anexo técnico que forma parte integral de la misma.

El Ministerio del Trabajo realizará los ajustes y actualizaciones técnicas de los lineamientos en Seguridad y Salud en el trabajo en los Procesos de Generación, Transmisión, Distribución y Comercialización de la energía eléctrica conforme al desarrollo científico, tecnológico e industrial.

Artículo 2°. Campo de aplicación. Los lineamientos en seguridad y salud en el trabajo para los procesos de generación, transmisión, distribución y comercialización de la energía eléctrica, para las empresas que presten o hagan uso del sistema eléctrico colombiano contenidos en la presente resolución, los cuales serán de obligatorio cumplimiento en todo proceso de generación, transmisión, distribución, y comercialización de energía eléctrica, que adelanten las empresas públicas y privadas, contratantes de personal bajo modalidad de contrato civil, comercial o administrativo, trabajadores dependientes e independientes, organizaciones de economía solidaria y del sector cooperativo, a las agremiaciones o asociaciones que afilien trabajadores independientes al Sistema de Seguridad Social, a las empresas de servicios temporales, Administradoras de Riesgos Laborales (ARL); la Policía Nacional en lo que corresponde a su personal no uniformado y al personal civil de las Fuerzas Militares; y demás personas que tengan que ver con estos procesos que involucren peligro eléctrico.

También aplica para toda actividad económica que involucre peligros eléctricos, como es el caso de la intervención sobre o en cercanía de las redes eléctricas, por ejemplo: redes de telecomunicaciones, construcciones civiles, montajes, iluminación y alumbrado, entre otras.""",
    },
    {
        "id": "RES5018-2019-ART3_4_5",
        "capitulo": CAPITULO,
        "seccion": "Artículo 3, 4 y 5",
        "titulo": "Período de transición (12 meses), sanciones (remisión a Decreto 1295/1994 y Ley 1562/2012) y vigencia (deroga la Resolución 1348 de 2009)",
        "texto": """Artículo 3°. Período de transición. Se establece un período máximo de doce (12) meses contados a partir de la fecha de publicación de la presente resolución, para la implementación de los lineamientos de Seguridad y Salud en el Trabajo en los procesos de generación, transmisión, distribución y comercialización de energía eléctrica, por parte de las empresas descritas en el artículo 2°.

Artículo 4°. Sanciones. El incumplimiento a lo establecido en la presente resolución y demás normas que la adicionen, modifiquen o sustituyan, será sancionado en los términos previstos en el artículo 91 del Decreto 1295 de 1994, modificado parcialmente y adicionado por el artículo 13 de la Ley 1562 de 2012, en armonía con el Capítulo 11 del Título 4 de la Parte 2 del Libro 2 del Decreto 1072 de 2015 y demás normas legales remisorias vigentes.

Artículo 5°. Vigencia. La presente resolución rige a partir de su publicación y deroga la Resolución 1348 del 2009 o la norma que la modifique, adicione o sustituya.

La resolución fue expedida en Bogotá D.C. el 20 de noviembre de 2019 y firmada por Alicia Arango Olmos, Ministra del Trabajo. Fecha de entrada en vigencia: 22 de noviembre de 2019.""",
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Mismo chunker validado en insert_titulo_h_i_nucleo.py / insert_res0312_2019_nucleo.py:
    divide por parrafo -> oracion -> coma hasta respetar el limite real de
    tokens del tokenizer (no una aproximacion por caracteres)."""
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
                "capitulo": chunk["capitulo"],
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
        rows.append({**f, "embedding": emb})

    print(f"{len(CHUNKS)} bloques originales (Res. 5018/2019) -> {len(rows)} subchunks reales:")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en nsr10_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
