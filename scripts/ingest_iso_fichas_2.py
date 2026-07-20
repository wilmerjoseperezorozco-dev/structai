"""
Carga fichas técnicas / índices de 4 normas ISO adicionales a motor_chunks
(motor='gerencia'), mismo criterio que ingest_iso9001.py:

  - NTC-ISO 31000:2018 (Gestión del riesgo) — PDF real: texto completo,
    aviso "Prohibida su reproducción" (ICONTEC).
  - ISO 19011:2011 (Auditoría de sistemas de gestión) — PDF real: texto
    completo, aviso "DOCUMENTO PROTEGIDO POR DERECHOS DE AUTOR © ISO 2011".
  - ISO/IEC 27001:2022 (Seguridad de la información) — el PDF real NO es
    el texto oficial ISO: es una guía de implantación de terceros (NQA).
  - ISO 14001:2015 (Gestión ambiental) — el PDF real NO es el texto
    oficial ISO: es una guía explicativa de terceros (isoTools.us).

En los 4 casos se carga SOLO la estructura real de cláusulas (verificada
contra el índice/TOC real de cada documento), redactada con descripciones
propias — nunca se reproduce el texto normativo ni el de las guías de
terceros. Ver normas_registro.notas_vigencia por código para el detalle
de cada decisión.

Uso: python scripts/ingest_iso_fichas_2.py
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


# ─── NTC-ISO 31000:2018 — Gestión del riesgo ──────────────────────────────────
FICHA_31000 = [
    {
        "seccion": "Ficha técnica NTC-ISO 31000 — Objeto y campo de aplicación",
        "titulo": "Objeto y campo de aplicación (Cláusula 1)",
        "contenido": (
            "NTC-ISO 31000:2018 proporciona directrices sobre la gestión del riesgo a la que se "
            "enfrentan las organizaciones. Es genérica y aplicable a cualquier organización, sector "
            "o actividad, para gestionar riesgos que puedan afectar el logro de sus objetivos. No "
            "está diseñada para propósitos de certificación."
        ),
    },
    {
        "seccion": "Ficha técnica NTC-ISO 31000 — Principios",
        "titulo": "Principios de la gestión del riesgo (Cláusula 4)",
        "contenido": (
            "Establece los principios que deben guiar una gestión del riesgo eficaz: integrada, "
            "estructurada e integral, adaptada al contexto de la organización, inclusiva, dinámica, "
            "basada en la mejor información disponible, que considere factores humanos y culturales, "
            "y sujeta a mejora continua."
        ),
    },
    {
        "seccion": "Ficha técnica NTC-ISO 31000 — Marco de referencia",
        "titulo": "Marco de referencia (Cláusula 5)",
        "contenido": (
            "Cubre el propósito y componentes del marco de referencia para integrar la gestión del "
            "riesgo en la organización: liderazgo y compromiso de la alta dirección, integración en "
            "los procesos organizacionales, diseño del marco (comprensión de la organización, "
            "articulación del compromiso, asignación de roles/autoridades/responsabilidades, "
            "asignación de recursos, establecimiento de comunicación y consulta), implementación, "
            "valoración de la eficacia del marco, y mejora continua del marco mismo."
        ),
    },
    {
        "seccion": "Ficha técnica NTC-ISO 31000 — Proceso",
        "titulo": "Proceso de gestión del riesgo (Cláusula 6)",
        "contenido": (
            "Describe el proceso iterativo de gestión del riesgo: comunicación y consulta con las "
            "partes interesadas a lo largo de todo el proceso; establecimiento del alcance, contexto "
            "y criterios de riesgo; evaluación del riesgo (identificación, análisis y valoración); "
            "tratamiento del riesgo (selección e implementación de opciones); seguimiento y revisión "
            "continuos; y registro e informe del proceso y sus resultados."
        ),
    },
]

# ─── ISO 19011:2011 — Auditoría de sistemas de gestión ────────────────────────
FICHA_19011 = [
    {
        "seccion": "Ficha técnica ISO 19011 — Alcance",
        "titulo": "Alcance (Cláusula 1)",
        "contenido": (
            "ISO 19011:2011 proporciona orientación sobre la gestión de un programa de auditoría, "
            "la planificación y realización de una auditoría de sistema de gestión, así como sobre "
            "la competencia y evaluación de un auditor y de un equipo auditor. Es aplicable a "
            "cualquier organización que necesite planificar y llevar a cabo auditorías internas o "
            "externas de sistemas de gestión, o gestionar un programa de auditoría."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 19011 — Principios de auditoría",
        "titulo": "Principios de auditoría (Cláusula 4)",
        "contenido": (
            "Establece los principios en los que se basa la auditoría eficaz y fiable: integridad, "
            "presentación imparcial, debido cuidado profesional, confidencialidad, independencia, "
            "enfoque basado en la evidencia, y (en revisiones posteriores) enfoque basado en riesgos."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 19011 — Gestión de un programa de auditoría",
        "titulo": "Gestión de un programa de auditoría (Cláusula 5)",
        "contenido": (
            "Cubre el ciclo completo de gestión de un programa de auditoría: establecimiento de los "
            "objetivos del programa, determinación y evaluación de riesgos y oportunidades asociados, "
            "establecimiento del programa (roles/responsabilidades, competencias, alcance, recursos), "
            "implementación del programa, monitoreo del programa, y revisión y mejora del mismo."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 19011 — Realización de la auditoría",
        "titulo": "Realización de una auditoría (Cláusula 6)",
        "contenido": (
            "Describe el desarrollo de una auditoría individual: inicio de la auditoría, preparación "
            "de las actividades (incluido el plan de auditoría), realización de las actividades "
            "(reunión de apertura, recopilación y verificación de la información, generación de "
            "hallazgos, preparación de conclusiones), y preparación y distribución del informe de "
            "auditoría, hasta la finalización de la auditoría y el seguimiento posterior."
        ),
    },
]

# ─── ISO/IEC 27001:2022 — Seguridad de la información ─────────────────────────
FICHA_27001 = [
    {
        "seccion": "Ficha técnica ISO 27001 — Alcance y estructura",
        "titulo": "Alcance y estructura de alto nivel (Anexo SL)",
        "contenido": (
            "ISO/IEC 27001:2022 especifica los requisitos para establecer, implementar, mantener y "
            "mejorar continuamente un Sistema de Gestión de Seguridad de la Información (SGSI). Sigue "
            "la estructura de alto nivel común a las normas de sistemas de gestión ISO (Anexo SL), "
            "organizada en 10 secciones: 1. Alcance, 2. Referencias normativas, 3. Términos y "
            "definiciones, 4. Contexto de la organización, 5. Liderazgo, 6. Planificación, 7. Apoyo, "
            "8. Funcionamiento, 9. Evaluación del rendimiento, 10. Mejora."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 27001 — Contexto, liderazgo y planificación",
        "titulo": "Secciones 4 a 6",
        "contenido": (
            "Cubre la comprensión del contexto de la organización y las partes interesadas, la "
            "determinación del alcance del SGSI, el liderazgo y compromiso de la alta dirección, la "
            "política de seguridad de la información, la asignación de roles y responsabilidades, y "
            "la planificación (tratamiento de riesgos y oportunidades, evaluación y tratamiento del "
            "riesgo de seguridad de la información, objetivos de seguridad y su planificación)."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 27001 — Apoyo, funcionamiento, evaluación y mejora",
        "titulo": "Secciones 7 a 10",
        "contenido": (
            "Cubre recursos, competencia, toma de conciencia, comunicación e información documentada "
            "(Apoyo); planificación y control operacional, evaluación y tratamiento del riesgo en "
            "operación (Funcionamiento); seguimiento, medición, análisis, evaluación, auditoría "
            "interna y revisión por la dirección (Evaluación del desempeño); y no conformidad, acción "
            "correctiva y mejora continua (Mejora). El Anexo A de la norma (no incluido aquí) lista "
            "los controles de referencia de seguridad de la información."
        ),
    },
]

# ─── ISO 14001:2015 — Gestión ambiental ────────────────────────────────────────
FICHA_14001 = [
    {
        "seccion": "Ficha técnica ISO 14001 — Alcance y estructura",
        "titulo": "Alcance y estructura de alto nivel (Anexo SL)",
        "contenido": (
            "ISO 14001:2015 especifica los requisitos para un Sistema de Gestión Ambiental (SGA) que "
            "una organización puede usar para mejorar su desempeño ambiental. Sigue la misma "
            "estructura de alto nivel común a las normas de sistemas de gestión ISO (Anexo SL) que "
            "ISO 9001 e ISO 27001: 1. Alcance, 2. Referencias normativas, 3. Términos y definiciones, "
            "4. Contexto de la organización, 5. Liderazgo, 6. Planificación, 7. Apoyo, 8. Operación, "
            "9. Evaluación del desempeño, 10. Mejora."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 14001 — Ciclo PHVA y enfoque basado en riesgos",
        "titulo": "Modelo de gestión ambiental",
        "contenido": (
            "El SGA se estructura sobre el ciclo PHVA (Planificar-Hacer-Verificar-Actuar): Planificar "
            "establece los objetivos ambientales y procesos necesarios para lograr resultados acordes "
            "con la política ambiental; Hacer implementa los procesos según lo planificado; Verificar "
            "hace seguimiento y mide los procesos frente a la política, objetivos y criterios de "
            "operación; Actuar toma acciones para la mejora continua. La norma permite verificación "
            "de conformidad por autodeterminación/autodeclaración, confirmación por partes "
            "interesadas, certificación por una entidad externa, o certificación del SGA."
        ),
    },
    {
        "seccion": "Ficha técnica ISO 14001 — Aplicación en gestión de proyectos de construcción",
        "titulo": "Relación con motor-gerencia",
        "contenido": (
            "ISO 14001 se referencia frecuentemente junto con ISO 9001 en sistemas integrados de "
            "gestión de proyectos de construcción en Colombia, particularmente para licitaciones "
            "públicas que exigen gestión de impactos ambientales de obra (manejo de residuos, "
            "control de emisiones y vertimientos, gestión de materiales). Complementa, no reemplaza, "
            "la normativa ambiental específica (Res. 0631/2015, Decreto 1076/2015) ya cargada en "
            "otros motores."
        ),
    },
]


def _rows_for(ficha: list[dict], codigo: str, motor: str, norma_ref_suffix: str) -> list[dict]:
    return [{
        "seccion": f["seccion"],
        "titulo": f["titulo"],
        "norma_ref": f"{norma_ref_suffix} (ficha técnica — no es el texto normativo completo, protegido por copyright)",
        "contenido": f["contenido"],
        "motor": motor,
    } for f in ficha]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    fichas = [
        ("NTC-ISO-31000-2018", FICHA_31000, "NTC-ISO 31000:2018"),
        ("ISO-19011-2011", FICHA_19011, "ISO 19011:2011"),
        ("ISO-27001-2022", FICHA_27001, "ISO/IEC 27001:2022"),
        ("ISO-14001-2015", FICHA_14001, "ISO 14001:2015"),
    ]

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    total = 0
    for codigo, ficha, ref in fichas:
        norma_row = sb.table("normas_registro").select("id").eq("codigo", codigo).execute()
        if not norma_row.data:
            raise RuntimeError(f"{codigo} no existe en normas_registro — registrarlo primero")
        norma_id = norma_row.data[0]["id"]

        rows = _rows_for(ficha, codigo, "gerencia", ref)
        for row in rows:
            row["norma_id"] = norma_id

        print(f"Generando embeddings para {codigo} ({len(rows)} chunks)...")
        textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
        vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=False)
        for row, vec in zip(rows, vectores):
            row["embedding"] = vec.tolist()

        borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
        print(f"  {codigo}: limpiados {len(borrado.data)} chunks previos")

        sb.table("motor_chunks").insert(rows).execute()
        print(f"  {codigo}: OK, {len(rows)} chunks de ficha técnica cargados")
        total += len(rows)

    print(f"\nTotal: {total} chunks de ficha técnica cargados en motor_chunks (motor='gerencia')")


if __name__ == "__main__":
    main()
