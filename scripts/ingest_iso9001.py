"""
Carga la ficha técnica / índice de ISO 9001:2015 (Sistemas de gestión de la
calidad — Requisitos) a motor_chunks (motor='gerencia'). NO es el texto
normativo completo — ISO 9001 es un estándar comercial protegido por
copyright (© ISO 2015), el PDF real en Drive trae el texto completo pero
NO se extrae ni se carga: solo la estructura real de cláusulas (1-10 +
Anexos A/B), redactada con descripciones propias, sin reproducir el texto
de los requisitos de ISO. Mismo criterio ya aplicado con NTC 1500.

Cada chunk se etiqueta explícitamente "Ficha técnica" para que el RAG
nunca dé a entender que tiene el contenido normativo completo — ver
normas_registro.notas_vigencia (codigo='ISO-9001-2015') para el detalle
de la decisión de alcance.

Uso: python scripts/ingest_iso9001.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


FICHA_TECNICA = [
    {
        "seccion": "Ficha técnica — Objeto y campo de aplicación",
        "titulo": "Objeto y campo de aplicación (Cláusula 1)",
        "contenido": (
            "ISO 9001:2015 especifica los requisitos para un sistema de gestión de la calidad "
            "aplicable cuando una organización necesita demostrar su capacidad para proporcionar "
            "regularmente productos y servicios que satisfagan los requisitos del cliente y los "
            "legales/reglamentarios aplicables, y aspira a aumentar la satisfacción del cliente. "
            "Es aplicable a cualquier organización, independientemente de su tamaño, tipo o "
            "producto/servicio."
        ),
    },
    {
        "seccion": "Ficha técnica — Estructura de alto nivel (Anexo SL)",
        "titulo": "Cláusulas principales de la norma",
        "contenido": (
            "ISO 9001:2015 sigue la estructura de alto nivel común a las normas de sistemas de "
            "gestión ISO (Anexo SL), organizada en 10 cláusulas: 1. Objeto y campo de aplicación, "
            "2. Referencias normativas, 3. Términos y definiciones, 4. Contexto de la "
            "organización, 5. Liderazgo, 6. Planificación, 7. Apoyo, 8. Operación, 9. Evaluación "
            "del desempeño, 10. Mejora. Las cláusulas 4 a 10 contienen los requisitos "
            "certificables; 1 a 3 son introductorias. NOTA: solo se tiene la estructura/tema de "
            "cada cláusula, no el texto normativo completo de los requisitos."
        ),
    },
    {
        "seccion": "Ficha técnica — Contexto de la organización (Cláusula 4)",
        "titulo": "Contexto de la organización",
        "contenido": (
            "Cubre la comprensión de la organización y su contexto, la comprensión de las "
            "necesidades y expectativas de las partes interesadas, la determinación del alcance "
            "del sistema de gestión de la calidad, y el propio sistema de gestión de la calidad "
            "y sus procesos."
        ),
    },
    {
        "seccion": "Ficha técnica — Liderazgo (Cláusula 5)",
        "titulo": "Liderazgo",
        "contenido": (
            "Cubre el liderazgo y compromiso de la alta dirección (incluido el enfoque al "
            "cliente), el establecimiento y comunicación de la política de la calidad, y la "
            "asignación de roles, responsabilidades y autoridades dentro de la organización."
        ),
    },
    {
        "seccion": "Ficha técnica — Planificación (Cláusula 6)",
        "titulo": "Planificación",
        "contenido": (
            "Cubre las acciones para abordar riesgos y oportunidades, el establecimiento de "
            "objetivos de la calidad y la planificación para lograrlos, y la planificación de "
            "los cambios al sistema de gestión de la calidad."
        ),
    },
    {
        "seccion": "Ficha técnica — Apoyo (Cláusula 7)",
        "titulo": "Apoyo",
        "contenido": (
            "Cubre los recursos necesarios (personas, infraestructura, ambiente de operación, "
            "recursos de seguimiento y medición, conocimientos organizacionales), la competencia "
            "del personal, la toma de conciencia, la comunicación, y el control de la "
            "información documentada."
        ),
    },
    {
        "seccion": "Ficha técnica — Operación (Cláusula 8)",
        "titulo": "Operación",
        "contenido": (
            "La cláusula más extensa de la norma. Cubre la planificación y control operacional; "
            "los requisitos para productos y servicios (comunicación con el cliente, "
            "determinación y revisión de requisitos); el diseño y desarrollo de productos y "
            "servicios; el control de procesos/productos/servicios suministrados externamente; "
            "la producción y provisión del servicio (identificación, trazabilidad, preservación, "
            "actividades posteriores a la entrega); la liberación de productos y servicios; y el "
            "control de las salidas no conformes."
        ),
    },
    {
        "seccion": "Ficha técnica — Evaluación del desempeño (Cláusula 9)",
        "titulo": "Evaluación del desempeño",
        "contenido": (
            "Cubre el seguimiento, medición, análisis y evaluación (incluida la satisfacción del "
            "cliente), la auditoría interna, y la revisión por la dirección (entradas y salidas "
            "del proceso de revisión)."
        ),
    },
    {
        "seccion": "Ficha técnica — Mejora (Cláusula 10)",
        "titulo": "Mejora",
        "contenido": (
            "Cubre las disposiciones generales de mejora continua, el tratamiento de no "
            "conformidades y acciones correctivas, y la mejora continua del sistema de gestión "
            "de la calidad."
        ),
    },
    {
        "seccion": "Ficha técnica — Anexos informativos",
        "titulo": "Anexos A y B",
        "contenido": (
            "Anexo A (informativo): aclaración de la nueva estructura, terminología y conceptos "
            "introducidos respecto a la edición anterior de la norma. Anexo B (informativo): "
            "relación con otras normas internacionales sobre gestión de la calidad y sistemas de "
            "gestión de la calidad desarrolladas por el Comité Técnico ISO/TC 176."
        ),
    },
    {
        "seccion": "Ficha técnica — Aplicación en Gerencia de proyectos",
        "titulo": "Relación con la gestión de proyectos de construcción",
        "contenido": (
            "ISO 9001 es referenciada frecuentemente en manuales de contratación pública "
            "colombianos (ej. sistemas de gestión de calidad exigidos a contratistas de obra "
            "pública) como marco de referencia para el control de calidad de procesos, no como "
            "un requisito técnico de diseño estructural. Su enfoque de gestión por procesos y "
            "mejora continua complementa (no reemplaza) las normas técnicas específicas de cada "
            "motor (NSR-10, RAS, INVIAS)."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "ISO-9001-2015").execute()
    if not norma_row.data:
        raise RuntimeError("ISO-9001-2015 no existe en normas_registro — registrarlo primero")
    norma_id = norma_row.data[0]["id"]

    rows = [{
        "seccion": f["seccion"],
        "titulo": f["titulo"],
        "norma_ref": "ISO 9001:2015 (ficha técnica — no es el texto normativo completo, protegido por copyright)",
        "contenido": f["contenido"],
        "norma_id": norma_id,
        "motor": "gerencia",
    } for f in FICHA_TECNICA]

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando ficha técnica previa de ISO 9001 (idempotente, por norma_id)...")
    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    sb.table("motor_chunks").insert(rows).execute()
    print(f"OK: {len(rows)} chunks de ficha técnica ISO 9001 cargados (motor='gerencia', norma_id={norma_id})")


if __name__ == "__main__":
    main()
