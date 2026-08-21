"""
Primer chunk de F.3 (NSR-10, Provisiones sismicas para estructuras de acero):
F.3.1 Provisiones generales (alcance, clasificacion DES/DMO/DMI de sistemas,
limites de Fy del acero, factores Ry/Rt de resistencia esperada).

F.3 es un capitulo enorme (F-208 a F-299, ~90 paginas, equivalente en
alcance a todo el estandar AISC 341 -- Seismic Provisions for Structural
Steel Buildings -- como documento aparte). Este batch cubre solo F.3.1
(alcance + materiales); F.3.2 a F.3.11 (requisitos especificos por sistema:
PRM, PA, PAE, PAPR, PRMC, muros compuestos, conexiones precalificadas,
control de calidad) quedan pendientes de una sesion dedicada futura --
documentado explicitamente en notas_vigencia, no se inventa cobertura que
no existe.

Fuente: NSR-10-841-900.pdf (Drive, id 116BU3sPl1kJfQxYct7AaS2wf9-kMPzgF),
paginas internas F-208 a F-219.

Uso: python _ingest_titulo_f_f3_batch1.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-F-F_3_1",
    "capitulo": "NSR-10 Título F — Estructuras Metálicas",
    "seccion": "F.3.1",
    "titulo": (
        "Provisiones sismicas para acero (F.3), alcance y materiales: aplica junto con "
        "F.2 a portico resistente a momento/arriostrado/muros de cortante en acero o "
        "acero-concreto compuesto. Clasificacion DES/DMO/DMI de sistemas sismicos. Limite "
        "de Fy=345 MPa (380 MPa para sistemas DMI) en miembros con comportamiento "
        "inelastico esperado, 450 MPa en columnas de sistemas DES. Factores Ry/Rt de "
        "resistencia esperada del material por tipo de acero (Tabla F.3.1.4-1). Primer "
        "gap real cerrado de F.3 -- capitulo completo tiene ~90 paginas, F.3.2 en "
        "adelante (PRM, PA, PAE, PAPR, PRMC, muros compuestos) sigue pendiente."
    ),
    "texto": (
        "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para estructuras de acero "
        "con perfiles laminados, armados y tubería estructural. F.3.1 — Provisiones "
        "generales.\n\n"
        "F.3.1.1 Alcance: estos requisitos sísmicos especiales se aplican CONJUNTAMENTE "
        "con el Capítulo F.2 (no lo reemplazan), y aplican al diseño, fabricación y "
        "montaje de miembros y conexiones de los sistemas de resistencia sísmica, "
        "empalmes y bases de columnas en sistemas de carga de gravedad, en edificaciones "
        "con pórticos resistentes a momento, pórticos arriostrados y muros de cortante, "
        "construidos con perfiles de acero únicamente O con acero actuando en forma "
        "compuesta con concreto reforzado. En sistemas compuestos, los miembros de "
        "concreto reforzado se diseñan según el Título C. Si el análisis estructural es "
        "elástico, los miembros compuestos/concreto deben modelarse con sección fisurada "
        "y los de acero con sección completa (permite usar la reducción de derivas de "
        "A.6.4.1.1; si se usa sección completa del concreto, no aplica esa reducción).\n\n"
        "Clasificación de sistemas por capacidad de disipación de energía (misma "
        "nomenclatura que Título A y Capítulo C.21):\n"
        "  DES = capacidad ESPECIAL — diseñado para acción inelástica significativa\n"
        "  DMO = capacidad MODERADA — acción inelástica moderada\n"
        "  DMI = capacidad MÍNIMA — acción inelástica limitada\n\n"
        "Sistemas cubiertos por F.3 (siglas usadas en todo el capítulo): PRM (pórtico "
        "resistente a momento, F.3.5), PA (pórtico arriostrado — PAC concéntrico F.3.6.1/"
        "6.2, PAE excéntrico F.3.6.3, PAPR con arriostramientos de pandeo restringido "
        "F.3.6.4), PRMC (pórtico compuesto resistente a momento, F.3.7), PACC/PAEC "
        "(pórticos compuestos arriostrados, F.3.8.1-8.3), MCA/MCAC/MCC (muros de cortante "
        "de placa de acero, simples/compuestos, F.3.8.4-8.6), PCD (pórticos con cerchas "
        "dúctiles, F.3.5.4).\n\n"
        "F.3.1.4.1 Especificaciones del material: la resistencia a la fluencia especificada "
        "para miembros de acero donde se espera comportamiento inelástico NO debe exceder "
        "345 MPa (sistemas de F.3.5, F.3.6, F.3.7, F.3.8) ni 380 MPa para los sistemas de "
        "capacidad mínima (F.3.5.1, F.3.6.1, F.3.7.1, F.3.8.1, F.3.8.4), salvo comportamiento "
        "certificado por pruebas. Para columnas en sistemas DES/DMO específicos "
        "(F.3.5.3, F.3.5.4, F.3.7.3, F.3.8.1-8.3, y todos los de F.3.6), Fy no debe exceder "
        "450 MPa. El acero para estos sistemas debe cumplir NTC 1920 (A36/A36M), A53/A53M, "
        "NTC 1986 (A500 Grados B/C), NTC 2374 (A501), A529/A529M, NTC 1985 (A572/A572M "
        "Grados 42/50/55), NTC 2012 (A588/A588M), A913/A913M (Grados 50/60/65), A992/A992M, "
        "A1011 Grado 55, A1043/A1043M. Placas de base de columnas: las mismas normas, o "
        "NTC 2633 (A283/A283M Grado D). Se permiten otros aceros en PAPR si cumplen "
        "F.3.6.4 y F.3.11.3.\n\n"
        "F.3.1.4.2 Resistencia esperada del material: cuando se requiere diseñar por "
        "capacidad (p.ej. resistencia nominal de la viga fuera del vínculo en PAE, rotura "
        "por bloque de cortante o área neta en riostras de PAC-DES), se usa el esfuerzo de "
        "fluencia esperado Ry*Fy (en vez de Fy) y la resistencia a rotura esperada Rt*Fu "
        "(en vez de Fu), donde Ry = relación entre fluencia esperada y mínima especificada, "
        "Rt = relación entre rotura esperada y mínima especificada. Para elementos "
        "conectados y otros miembros se sigue usando la resistencia especificada normal "
        "(Fy, Fu), no la esperada.\n\n"
        "Tabla F.3.1.4-1 — Valores de Ry y Rt por tipo de acero:\n"
        "  Secciones laminadas: A36/A36M: Ry=1.5, Rt=1.2\n"
        "  A1043/A1043M Grado 36: Ry=1.3, Rt=1.1\n"
        "  A572/A572M Grado 50 o 55: Ry=1.1, Rt=1.1\n"
        "  A913/A913M Grado 50/60/65: Ry=1.1, Rt=1.1\n"
        "  A588/A588M, A992/A992M, A1011 HSLAS Grado 55: Ry=1.1, Rt=1.1\n"
        "  A1043/A1043M Grado 50: Ry=1.2, Rt=1.1\n"
        "  A529 Grado 50: Ry=1.2, Rt=1.2\n"
        "  A529 Grado 55: Ry=1.1, Rt=1.2\n"
        "  Perfiles tubulares (PTE) A500 Grado B/C, A501: Ry=1.4, Rt=1.3\n"
        "  Tubería de acero A53/A53M: Ry=1.6, Rt=1.2"
    ),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vec = model.encode([CHUNK["texto"]], normalize_embeddings=True)[0]

    row = dict(CHUNK)
    row["embedding"] = vec.tolist()
    row["titulo"] = row["titulo"][:500]

    sb.table("nsr10_chunks").upsert(row, on_conflict="id").execute()
    print(f"OK: {CHUNK['id']} cargado con embedding ({len(CHUNK['texto'])} chars).")


if __name__ == "__main__":
    main()
