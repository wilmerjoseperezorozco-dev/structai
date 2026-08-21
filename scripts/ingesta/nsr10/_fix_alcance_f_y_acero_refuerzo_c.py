"""
Reemplaza el texto de dos chunks sinteticos/no-verbatim detectados en la
auditoria del issue #5 (26-ago-2026 -> corregido 21-ago-2026) por texto
verbatim real de la NSR-10, y regenera su embedding (el UPDATE de texto vía
SQL directo NO actualiza el vector -- este script lo hace, siguiendo el
mismo patron de _ingest_titulo_c_batch2.py).

- NSR10-ALCANCE-F: tenia un resumen tecnico parafraseado del alcance del
  Titulo F. Reemplazado por F.1.0.1/F.1.0.2/F.1.1.1/F.1.1.2 verbatim
  (Capitulo F.1 - Requisitos Generales completo), fuente IDRD.
- C-SEC2-TAB2: tenia una "tabla" fabricada de grados de acero (280/420/550
  MPa) que NO existe asi en el texto oficial. Reemplazado por C.3.5/C.3.5.3
  verbatim (Acero de refuerzo, incl. Tablas C.3.5.3-1 y C.3.5.3-2 reales de
  dimensiones de barras), fuente CAMACOL.

Ambas fuentes: PDFs oficiales descargados en vivo el 2026-08-21 desde
idrd.gov.co y camacol.co (ver comentario capitulo en cada fila para URL).

El texto ya fue escrito en Supabase via SQL (execute_sql) en la misma
sesion -- este script solo recalcula y sube el embedding correspondiente
para que el retrieval (match_nsr10_chunks) indexe el contenido nuevo, no
el viejo. Se deja aqui versionado para que quede registrado como el resto
de la ingesta del proyecto.

Uso: python _fix_alcance_f_y_acero_refuerzo_c.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNKS = [
    {
        "id": "NSR10-ALCANCE-F",
        "capitulo": (
            "NSR-10 Título F — Estructuras Metálicas, Capítulo F.1 — Requisitos "
            "Generales (texto verbatim, fuente oficial: IDRD, PDF Título F NSR-10 "
            "del Decreto 926 de 2010, "
            "https://www.idrd.gov.co/sites/default/files/documentos/Construcciones/"
            "6titulo-f-nsr-100.pdf, verificado 2026-08-21)"
        ),
        "seccion": "F.1.0.1 a F.1.1.2",
        "titulo": (
            "F.1.0.1 — Alcance, F.1.0.2 — Zonas Sísmicas, F.1.1 — Límites de "
            "Aplicabilidad (Título F, Capítulo F.1 — Requisitos Generales)"
        ),
        "texto": (
            "F.1.0 — GENERALIDADES\n\n"
            "F.1.0.1 — ALCANCE — Las normas contenidas en el Título F de este "
            "Reglamento son aplicables al diseño de estructuras conformadas por "
            "elementos de acero o de aluminio, soldados, atornillados, o "
            "remachados.\n\n"
            "F.1.0.2 — ZONAS SÍSMICAS — Los requisitos para estructuras metálicas "
            "que se dan en el presente Título de este Reglamento, deben aplicarse "
            "a cada una de las Zonas de Amenaza Sísmica que se definen en A.2.3 "
            "del Título A de este Reglamento.\n\n"
            "F.1.1 — LIMITES DE APLICABILIDAD\n\n"
            "F.1.1.1 — ESTRUCTURAS DE ACERO — El término acero estructural "
            "empleado en la presente norma se refiere a los elementos de acero "
            "estructural esenciales para resistir las cargas de diseño.\n\n"
            "El diseño de estructuras de acero con miembros hechos con perfiles "
            "laminados está cubierto por los Capítulos F.1 a F.3. Tales miembros "
            "se enumeran en forma general en 2.1 del \"Código de Práctica "
            "Estándar para Estructuras Metálicas\" del Instituto Americano para "
            "Construcción en Acero (AISC).\n\n"
            "El diseño de estructuras metálicas con miembros formados en frío se "
            "trata en el Capítulo F.4.\n\n"
            "F.1.1.2 — ESTRUCTURAS DE ALUMINIO — El término aluminio estructural "
            "empleado en la presente norma se refiere a los elementos de aluminio "
            "estructural esenciales para resistir las cargas de diseño.\n\n"
            "El diseño de estructuras metálicas con elementos de aluminio "
            "estructural se hará conforme al Capítulo F.5."
        ),
    },
    {
        "id": "NSR10-F-F_1",
        "capitulo": (
            "NSR-10 Título F — Estructuras Metálicas, Capítulo F.1 — Requisitos "
            "Generales (texto verbatim, fuente oficial: IDRD, PDF Título F NSR-10 "
            "del Decreto 926 de 2010, "
            "https://www.idrd.gov.co/sites/default/files/documentos/Construcciones/"
            "6titulo-f-nsr-100.pdf, verificado 2026-08-21; duplicado de "
            "NSR10-ALCANCE-F corregido en la misma auditoría, se deja como registro "
            "separado en vez de borrar)"
        ),
        "seccion": "F.1.0.1 a F.1.1.2",
        "titulo": (
            "F.1.0.1 — Alcance, F.1.0.2 — Zonas Sísmicas, F.1.1 — Límites de "
            "Aplicabilidad (Título F, Capítulo F.1 — Requisitos Generales)"
        ),
        "texto": (
            "F.1.0 — GENERALIDADES\n\n"
            "F.1.0.1 — ALCANCE — Las normas contenidas en el Título F de este "
            "Reglamento son aplicables al diseño de estructuras conformadas por "
            "elementos de acero o de aluminio, soldados, atornillados, o "
            "remachados.\n\n"
            "F.1.0.2 — ZONAS SÍSMICAS — Los requisitos para estructuras metálicas "
            "que se dan en el presente Título de este Reglamento, deben aplicarse "
            "a cada una de las Zonas de Amenaza Sísmica que se definen en A.2.3 "
            "del Título A de este Reglamento.\n\n"
            "F.1.1 — LIMITES DE APLICABILIDAD\n\n"
            "F.1.1.1 — ESTRUCTURAS DE ACERO — El término acero estructural "
            "empleado en la presente norma se refiere a los elementos de acero "
            "estructural esenciales para resistir las cargas de diseño.\n\n"
            "El diseño de estructuras de acero con miembros hechos con perfiles "
            "laminados está cubierto por los Capítulos F.1 a F.3. Tales miembros "
            "se enumeran en forma general en 2.1 del \"Código de Práctica "
            "Estándar para Estructuras Metálicas\" del Instituto Americano para "
            "Construcción en Acero (AISC).\n\n"
            "El diseño de estructuras metálicas con miembros formados en frío se "
            "trata en el Capítulo F.4.\n\n"
            "F.1.1.2 — ESTRUCTURAS DE ALUMINIO — El término aluminio estructural "
            "empleado en la presente norma se refiere a los elementos de aluminio "
            "estructural esenciales para resistir las cargas de diseño.\n\n"
            "El diseño de estructuras metálicas con elementos de aluminio "
            "estructural se hará conforme al Capítulo F.5."
        ),
    },
    {
        "id": "C-SEC2-TAB2",
        "capitulo": (
            "NSR-10 Título C — Concreto Estructural, Capítulo C.3 — Materiales, "
            "C.3.5 Acero de Refuerzo (texto verbatim, fuente oficial: CAMACOL, "
            "PDF Título C NSR-10 del Decreto 926 de 2010, "
            "https://camacol.co/sites/default/files/descargables/"
            "T%C3%ADtulo%20C%20NSR-10%20del%20Decreto%20926%20del%2019032010_0.pdf, "
            "verificado 2026-08-21)"
        ),
        "seccion": "C.3.5 a C.3.5.3.2",
        "titulo": (
            "C.3.5 y C.3.5.3 — Acero de Refuerzo, Tablas C.3.5.3-1 y C.3.5.3-2 — "
            "Dimensiones nominales de las barras de refuerzo (Título C, "
            "Capítulo C.3 — Materiales)"
        ),
        "texto": (
            "C.3.5 — Acero de refuerzo\n\n"
            "C.3.5.1 — El refuerzo debe ser corrugado. El refuerzo liso solo "
            "puede utilizarse en estribos, espirales o tendones, y refuerzo de "
            "repartición y temperatura. Además, se pueden utilizar cuando el "
            "Título C del Reglamento NSR-10 así lo permita: refuerzo consistente "
            "en pernos con cabeza para refuerzo de cortante, perfiles de acero "
            "estructural o en tubos, o elementos tubulares de acero. Además, se "
            "pueden utilizar fibras de acero deformadas dispersas solamente para "
            "resistir cortante bajo las condiciones indicadas en C.11.4.6.1(f).\n\n"
            "C.3.5.2 — La soldadura de barras de refuerzo debe realizarse de "
            "acuerdo con la norma NTC 4040 (AWS D1.4). La ubicación y tipo de los "
            "empalmes soldados y otras soldaduras requeridas en las barras de "
            "refuerzo deben estar indicados en los planos de diseño o en las "
            "especificaciones del proyecto. Las normas NTC para barras de "
            "refuerzo, excepto NTC 2289 (ASTM A706M), deben ser complementadas "
            "para requerir un informe de las propiedades necesarias del material "
            "para cumplir con los requisitos de NTC 4040 (AWS D1.4).\n\n"
            "C.3.5.3 — Refuerzo corrugado\n\n"
            "C.3.5.3.1 — Las barras de refuerzo corrugado deben ser de acero de "
            "baja aleación que cumplan con la norma NTC 2289 (ASTM A706M). Se "
            "permite el uso de barras de acero inoxidable fabricadas bajo la "
            "norma ASTM A955M siempre y cuando cumplan a su vez los requisitos "
            "de NTC 2289 (ASTM A706M). Además deben tenerse en cuenta los "
            "siguientes aspectos:\n"
            "(a) La resistencia a la fluencia debe corresponder a la determinada "
            "por ensayos sobre barras de tamaño completo. Los esfuerzos "
            "obtenidos por medio del ensayo de tracción deben calcularse "
            "utilizando el área nominal de la barra tal como se indica en las "
            "Tablas C.3.5.3-1 y C.3.5.3-2.\n"
            "(b) No se permite el uso de acero corrugado de refuerzo fabricado "
            "bajo la norma NTC 245, ni ningún otro tipo de acero que haya sido "
            "trabajado en frío o trefilado, a menos que esté explícitamente "
            "permitido por la norma bajo la cual se fabrica cualquiera de los "
            "materiales permitidos por el Reglamento NSR-10.\n\n"
            "TABLA C.3.5.3-1 — DIMENSIONES NOMINALES DE LAS BARRAS DE REFUERZO "
            "(Diámetros basados en milímetros)\n"
            "Designación | Diámetro mm | Área mm² | Perímetro mm | Masa kg/m\n"
            "6M | 6.0 | 28.3 | 18.85 | 0.222\n"
            "8M | 8.0 | 50.3 | 25.14 | 0.394\n"
            "10M | 10.0 | 78.5 | 31.42 | 0.616\n"
            "12M | 12.0 | 113.1 | 37.70 | 0.887\n"
            "16M | 16.0 | 201.1 | 50.27 | 1.577\n"
            "18M | 18.0 | 254.5 | 56.55 | 1.996\n"
            "20M | 20.0 | 314.2 | 62.83 | 2.465\n"
            "22M | 22.0 | 380.1 | 69.12 | 2.982\n"
            "25M | 25.0 | 490.9 | 78.54 | 3.851\n"
            "30M | 30.0 | 706.9 | 94.25 | 5.544\n"
            "32M | 32.0 | 804.2 | 100.53 | 6.309\n"
            "36M | 36.0 | 1017.9 | 113.10 | 7.985\n"
            "45M | 45.0 | 1590.4 | 141.37 | 12.477\n"
            "55M | 55.0 | 2375.8 | 172.79 | 18.638\n"
            "Nota: La M indica que son diámetros nominales en mm.\n\n"
            "TABLA C.3.5.3-2 — DIMENSIONES NOMINALES DE LAS BARRAS DE REFUERZO "
            "(Diámetros basados en octavos de pulgada)\n"
            "Designación | Diámetro de referencia pulgadas | Diámetro mm | "
            "Área mm² | Perímetro mm | Masa kg/m\n"
            "No. 2 | 1/4\" | 6.4 | 32 | 20.0 | 0.250\n"
            "No. 3 | 3/8\" | 9.5 | 71 | 30.0 | 0.560\n"
            "No. 4 | 1/2\" | 12.7 | 129 | 40.0 | 0.994\n"
            "No. 5 | 5/8\" | 15.9 | 199 | 50.0 | 1.552\n"
            "No. 6 | 3/4\" | 19.1 | 284 | 60.0 | 2.235\n"
            "No. 7 | 7/8\" | 22.2 | 387 | 70.0 | 3.042\n"
            "No. 8 | 1\" | 25.4 | 510 | 80.0 | 3.973\n"
            "No. 9 | 1-1/8\" | 28.7 | 645 | 90.0 | 5.060\n"
            "No. 10 | 1-1/4\" | 32.3 | 819 | 101.3 | 6.404\n"
            "No. 11 | 1-3/8\" | 35.8 | 1006 | 112.5 | 7.907\n"
            "No. 14 | 1-3/4\" | 43.0 | 1452 | 135.1 | 11.380\n"
            "No. 18 | 2-1/4\" | 57.3 | 2581 | 180.1 | 20.240\n"
            "Nota: El No. de la barra indica el número de octavos de pulgada del "
            "diámetro de referencia.\n\n"
            "C.3.5.3.2 — Las barras corrugadas deben cumplir con una de las "
            "normas NTC o ASTM enumeradas en C.3.5.3.1, excepto que para barras "
            "con fy mayor que 420 MPa, la resistencia a la fluencia debe tomarse "
            "como el esfuerzo correspondiente a una deformación unitaria del "
            "0.35 por ciento. Véase C.9.4."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    sb = create_client(supabase_url, supabase_key)

    print(f"Chunks a corregir: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local (paraphrase-multilingual-MiniLM-L12-v2)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": chunk["capitulo"],
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks corregidos con embedding real.")


if __name__ == "__main__":
    main()
