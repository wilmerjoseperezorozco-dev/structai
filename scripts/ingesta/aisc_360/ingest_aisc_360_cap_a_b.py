"""
Carga ficha técnica curada de AISC 360-2010 (Cap. A — Disposiciones
Generales, y el arranque del Cap. B — Requisitos de Diseño: cargas,
base LRFD/ASD, clasificación de secciones) a ntc_chunks.

Primera fuente de diseño en acero de StructAI -- antes de esto no había
ninguna cobertura de acero estructural (solo concreto vía NSR-10/ACI 318
y geotecnia/hidráulica/vías).

Por qué solo Cap. A y el arranque de B: el PDF fuente
(packages/construdata/normativa_raw/aisc_360/, ignorado por git,
11.3MB) supera el límite de 10MB de la herramienta de descarga
disponible esta sesión (2026-08-20) -- no se pudo bajar el binario
completo como sí se hizo con ACI 318-05 (7.5MB). La extracción vía
lectura de Drive (que sí funcionó) se cortó en 252.524 caracteres,
justo al llegar a la Tabla B4.1 de clasificación de secciones -- nunca
alcanzó los capítulos D-H (diseño por capacidad: tracción, compresión,
flexión, corte, combinadas), que es donde está el valor real de cálculo
para un ingeniero. Cada entrada de este lote sí se verificó contra el
texto extraído real (no se inventó ningún valor); las ecuaciones B3-1/
B3-2 en particular se copiaron literalmente porque son simples
(desigualdades lineales), sin el problema de subíndices revueltos que
tuvo ACI 318 en sus fórmulas más complejas.

Uso: python scripts/ingesta/aisc_360/ingest_aisc_360_cap_a_b.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


FICHA = [
    {
        "seccion": "Cap. A1 — Alcance",
        "titulo": "A qué estructuras aplica la Especificación",
        "contenido": (
            "AISC 360 (Especificación para Edificios de Acero, ANSI/AISC 360) aplica al "
            "diseño de sistemas estructurales en acero, y a sistemas con acero estructural "
            "actuando en estructuras compuestas con concreto armado. Cubre edificios y "
            "'otras estructuras' diseñadas, fabricadas y montadas de forma similar a "
            "edificios. Cuando el código de construcción aplicable no define cargas o "
            "combinaciones de carga, AISC 360 remite a ASCE/SEI 7. Para diseño "
            "sismorresistente en acero se exige aplicar además ANSI/AISC 341 (Seismic "
            "Provisions for Structural Steel Buildings) -- AISC 360 por sí sola no cubre "
            "los requisitos sísmicos especiales."
        ),
    },
    {
        "seccion": "Cap. A3.1a — Materiales, aceros estructurales",
        "titulo": "Designaciones ASTM más usadas en la práctica",
        "contenido": (
            "AISC 360 permite un listado extenso de designaciones ASTM para acero "
            "estructural. En la práctica, ASTM A992 es la especificación más comúnmente "
            "referenciada para perfiles W (nota del propio texto: 'ASTM A992 is the most "
            "commonly referenced specification for W-shapes'). ASTM A36 sigue siendo de "
            "uso general para planchas y perfiles no-W. Para secciones tubulares (HSS) se "
            "usa ASTM A500. Para pernos de alta resistencia, las designaciones son ASTM "
            "A325/A325M y A490/A490M (o los conectores de control de torsión F1852/F2280). "
            "Para varillas de anclaje, ASTM F1554 es la especificación más comúnmente "
            "referenciada -- el grado y la soldabilidad deben especificarse aparte."
        ),
    },
    {
        "seccion": "Cap. B2 — Cargas y combinaciones de cargas",
        "titulo": "Origen de las cargas de diseño",
        "contenido": (
            "AISC 360 no define sus propias combinaciones de carga: remite a la normativa "
            "de edificación aplicable, y en ausencia de esta, al estándar ASCE/SEI 7. Para "
            "diseño LRFD (Sección B3.3) se usan las combinaciones de ASCE/SEI 7 Sección "
            "2.3; para diseño ASD (Sección B3.4), las de ASCE/SEI 7 Sección 2.4 -- son "
            "conjuntos de combinaciones distintos, no la misma combinación con un factor "
            "de conversión."
        ),
    },
    {
        "seccion": "Cap. B3.3 — Diseño por LRFD",
        "titulo": "Ecuación de verificación LRFD (B3-1)",
        "contenido": (
            "En Diseño en Base a Factores de Carga y Resistencia (LRFD), la verificación "
            "es Ru ≤ φ·Rn (Ecuación B3-1), donde Ru es la resistencia requerida bajo las "
            "combinaciones de carga LRFD, Rn la resistencia nominal (especificada en los "
            "Capítulos B a K según el tipo de solicitación) y φ el factor de resistencia "
            "(también especificado por capítulo). El producto φ·Rn es la 'resistencia de "
            "diseño'."
        ),
    },
    {
        "seccion": "Cap. B3.4 — Diseño por ASD",
        "titulo": "Ecuación de verificación ASD (B3-2)",
        "contenido": (
            "En Diseño en Base a Resistencias Admisibles (ASD), la verificación es "
            "Ra ≤ Rn/Ω (Ecuación B3-2), donde Ra es la resistencia requerida bajo las "
            "combinaciones de carga ASD, Rn la resistencia nominal y Ω el factor de "
            "seguridad. El cociente Rn/Ω es la 'resistencia admisible'. AISC 360 permite "
            "usar LRFD o ASD indistintamente -- ambos métodos parten de la misma "
            "resistencia nominal Rn, solo difiere cómo se aplica el margen de seguridad "
            "(factor de resistencia que reduce la resistencia vs. factor de seguridad que "
            "la divide, sobre cargas ya factoradas de forma distinta en cada combinación)."
        ),
    },
    {
        "seccion": "Cap. B4 — Clasificación de secciones por pandeo local",
        "titulo": "Sección compacta, no compacta y de elementos esbeltos",
        "contenido": (
            "AISC 360 clasifica la sección transversal de un miembro en compresión según "
            "su susceptibilidad al pandeo local, comparando la relación ancho/espesor de "
            "cada elemento contra límites λp y λr: Sección compacta -- capaz de desarrollar "
            "totalmente la distribución de tensiones plásticas antes de pandear localmente. "
            "Sección no compacta -- puede alcanzar la tensión de fluencia en compresión "
            "antes del pandeo local, pero no tiene capacidad de rotación suficiente para "
            "una redistribución plástica completa. Sección de elementos esbeltos -- tiene "
            "elementos tipo placa con esbeltez suficiente para que el pandeo local ocurra "
            "en rango elástico, antes de alcanzar la fluencia. Esta clasificación (Tabla "
            "B4.1) determina qué ecuaciones de resistencia nominal Mn/Fcr aplican en los "
            "capítulos de diseño por flexión y compresión."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "AISC-360-2010").execute()
    if not norma_row.data:
        raise RuntimeError("AISC-360-2010 no existe en normas_registro -- registrarlo primero")
    norma_id = norma_row.data[0]["id"]

    norma_label = "AISC 360-2010 (ficha técnica curada -- Cap. A y arranque de B, no es el texto completo verbatim)"
    rows = [{
        "seccion": f["seccion"],
        "titulo": f["titulo"],
        "norma": norma_label,
        "contenido": f["contenido"],
        "norma_id": norma_id,
    } for f in FICHA]

    print(f"Total chunks: {len(rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando ficha técnica previa de AISC-360-2010 (idempotente, por norma_id)...")
    borrado = sb.table("ntc_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a ntc_chunks...")
    sb.table("ntc_chunks").insert(rows).execute()
    print(f"OK: {len(rows)} chunks de ficha técnica AISC 360-2010 cargados (norma_id={norma_id})")


if __name__ == "__main__":
    main()
