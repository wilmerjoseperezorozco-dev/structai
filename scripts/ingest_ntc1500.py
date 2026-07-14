"""
Carga la ficha técnica / índice de la NTC 1500 (Código Colombiano de
Instalaciones Hidráulicas y Sanitarias, ICONTEC) a motor_chunks (motor=
'aquai'). NO es el texto normativo completo — NTC 1500 es una norma
comercial de ICONTEC, no de acceso público como RAS 2000/Res. 0330; las
3 fuentes disponibles en Drive (Google Doc, .txt, .pdf) coinciden en dar
la misma ficha técnica de 13 puntos (objeto/alcance, historial de
actualizaciones, estructura de 14 capítulos + anexos A-F, relación con
RAS/NSR-10), no las tablas de diseño ni requisitos técnicos por capítulo.

Cada chunk se etiqueta explícitamente "Ficha técnica" (no "Capítulo N")
para que el RAG nunca dé a entender que tiene el contenido normativo
completo de un capítulo cuando solo tiene su título/tema — ver
normas_registro.notas_vigencia (codigo='NTC-1500') para el detalle.

Uso: python scripts/ingest_ntc1500.py
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
        "seccion": "Ficha técnica — Objeto y alcance",
        "titulo": "Objeto y alcance",
        "contenido": (
            "NTC 1500 (Código Colombiano de Instalaciones Hidráulicas y Sanitarias, ICONTEC): "
            "establece los requisitos mínimos para el diseño, construcción, instalación, "
            "modificación, reparación, reemplazo, extensión, uso y mantenimiento de los sistemas "
            "de instalaciones hidráulicas y sanitarias en edificaciones. Su propósito es "
            "salvaguardar la vida, la propiedad, la salud y el bienestar público."
        ),
    },
    {
        "seccion": "Ficha técnica — Correspondencia y actualización",
        "titulo": "Historial de actualizaciones",
        "contenido": (
            "NTC 1500 cuenta con Segunda actualización (2004-11-03), Tercera actualización "
            "(2017-08-16) y Cuarta actualización (2020, vigente). Código ICS 91.140.60. "
            "Descriptores: suministro de agua; sistema de desagüe; instalación sanitaria; "
            "fontanería."
        ),
    },
    {
        "seccion": "Ficha técnica — Estructura de la norma",
        "titulo": "Capítulos principales (NTC 1500:2020)",
        "contenido": (
            "La NTC 1500:2020 está organizada en 14 capítulos: 1. Alcance y aplicación, "
            "2. Referencias normativas, 3. Términos y definiciones, 4. Requisitos generales, "
            "5. Aparatos, griferías y accesorios, 6. Calentadores de agua, 7. Suministro y "
            "distribución de agua, 8. Desagüe sanitario, 9. Vertimientos especiales o "
            "indirectos, 10. Ventilaciones, 11. Sifones, interceptores y separadores, "
            "12. Desagüe de aguas lluvias, 13. Sistema de agua no potable, 14. Sistemas de "
            "riego del subsuelo. NOTA: solo se tiene el título/tema de cada capítulo, no su "
            "contenido normativo completo (tablas de diseño, requisitos técnicos detallados)."
        ),
    },
    {
        "seccion": "Ficha técnica — Anexos",
        "titulo": "Anexos de la norma",
        "contenido": (
            "La NTC 1500:2020 incluye los anexos: A. Seguridad estructural, B. Dimensionamiento "
            "del sistema de tuberías hidráulicas, C. Fuerza tractiva, D. Adopción modificada del "
            "documento de referencia, E. Resumen de cambios entre la tercera y la cuarta "
            "actualización, F. Bibliografía."
        ),
    },
    {
        "seccion": "Ficha técnica — Espacios prohibidos",
        "titulo": "Restricciones de ubicación",
        "contenido": (
            "Las instalaciones hidráulicas y sanitarias no deben ser instaladas en la caja del "
            "ascensor ni en el cuarto de máquinas."
        ),
    },
    {
        "seccion": "Ficha técnica — Sistemas de suministro de agua",
        "titulo": "Suministro de agua (Capítulo 7)",
        "contenido": (
            "Todo aparato hidrosanitario, dispositivo o artefacto que requiera el uso de agua "
            "para su funcionamiento debe conectarse al sistema de suministro de agua. La norma "
            "establece los componentes básicos de la red de suministro: tuberías, accesorios, "
            "válvulas y dispositivos de control. NOTA: no se tiene el detalle técnico "
            "(diámetros, presiones, velocidades) — ver Anexo B para dimensionamiento."
        ),
    },
    {
        "seccion": "Ficha técnica — Sistemas de desagüe sanitario",
        "titulo": "Desagüe sanitario (Capítulo 8)",
        "contenido": (
            "La norma establece los componentes básicos de la red de desagüe: tuberías, "
            "accesorios, trampas, sifones, interceptores y separadores. Incluye disposiciones "
            "para vertimientos especiales o indirectos (Capítulo 9)."
        ),
    },
    {
        "seccion": "Ficha técnica — Sistemas de ventilación",
        "titulo": "Ventilación (Capítulo 10)",
        "contenido": (
            "El sistema de ventilación es obligatorio en las instalaciones hidráulicas y "
            "sanitarias para garantizar el correcto funcionamiento de los desagües, prevenir el "
            "sifonaje y permitir la evacuación de gases."
        ),
    },
    {
        "seccion": "Ficha técnica — Pruebas y ensayos",
        "titulo": "Pruebas y ensayos obligatorias",
        "contenido": (
            "El sistema de tuberías de instalaciones hidráulicas y sanitarias debe ser probado "
            "con agua o, para sistemas de tuberías que no sean de plástico, con aire. Todas las "
            "instalaciones deben ser inspeccionadas, probadas y aprobadas en obra antes de ser "
            "recubiertas."
        ),
    },
    {
        "seccion": "Ficha técnica — Aguas lluvias",
        "titulo": "Desagüe de aguas lluvias (Capítulo 12)",
        "contenido": (
            "La norma incluye disposiciones específicas para el manejo, la conducción y la "
            "evacuación de aguas lluvias en edificaciones, estableciendo requisitos para "
            "canales, bajantes y sistemas de recolección."
        ),
    },
    {
        "seccion": "Ficha técnica — Relación con RAS",
        "titulo": "Relación con la Resolución 0330 de 2017 (RAS vigente)",
        "contenido": (
            "NTC 1500 se complementa con el Reglamento Técnico del Sector de Agua Potable y "
            "Saneamiento Básico (RAS, hoy Resolución 0330 de 2017) para proyectos que involucren "
            "sistemas de acueducto y alcantarillado — el RAS establece requisitos adicionales "
            "para sistemas de mayor escala (red pública), mientras NTC 1500 cubre la instalación "
            "hidrosanitaria dentro de la edificación."
        ),
    },
    {
        "seccion": "Ficha técnica — Relación con NSR-10",
        "titulo": "Relación con NSR-10",
        "contenido": (
            "NTC 1500 debe complementarse con la NSR-10 para aspectos estructurales y de "
            "seguridad. El Anexo A de la NTC 1500:2020 está dedicado a la Seguridad Estructural, "
            "asegurando que las instalaciones hidrosanitarias no comprometan la estabilidad de "
            "la edificación."
        ),
    },
    {
        "seccion": "Ficha técnica — Aplicación en APU",
        "titulo": "Base normativa para APU de fontanería",
        "contenido": (
            "NTC 1500 es la base normativa para la elaboración de APU de fontanería y "
            "saneamiento: define los requisitos mínimos de materiales, equipos, sistemas y "
            "procedimientos de instalación. Las pruebas especificadas son obligatorias para la "
            "entrega y recepción de los sistemas."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "NTC-1500").execute()
    if not norma_row.data:
        raise RuntimeError("NTC-1500 no existe en normas_registro — correr la migración de vigencia primero")
    norma_id = norma_row.data[0]["id"]

    rows = [{
        "seccion": f["seccion"],
        "titulo": f["titulo"],
        "norma_ref": "NTC 1500 (ficha técnica — no es el texto normativo completo)",
        "contenido": f["contenido"],
        "norma_id": norma_id,
        "motor": "aquai",
    } for f in FICHA_TECNICA]

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando ficha técnica previa de NTC 1500 (idempotente, por norma_id)...")
    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    sb.table("motor_chunks").insert(rows).execute()
    print(f"OK: {len(rows)} chunks de ficha técnica NTC 1500 cargados (motor='aquai', norma_id={norma_id})")


if __name__ == "__main__":
    main()
