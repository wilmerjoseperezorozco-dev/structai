"""
Ingesta verbatim de NSR-10 Titulo F.5.4.6 (Estructuras de Aluminio --
Diseno Estatico de Miembros: MIEMBROS A TENSION).

Fuente: NSR-10-1083-1182.pdf (paginas internas F-488 a F-490), ya
descargado localmente en scripts/ingesta/nsr10/raw/ (gitignored).
Texto transcrito verbatim leyendo el PDF nativo pagina por pagina
(nunca el texto plano exportado, corrompe subindices/formulas).

Sistema de unidades: kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Uso: python _ingest_titulo_f_f546_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_4_6_1_a_fluencia_general",
        "seccion": "F.5.4.6.1(a) — Resistencia a tensión, fluencia general",
        "titulo": "F.5.4.6 Miembros a Tensión",
        "texto": (
            "F.5.4.6 — MIEMBROS A TENSION — La tensión P generada bajo "
            "carga mayorada en miembros axialmente cargados a tensión "
            "(tirantes) no debe exceder la resistencia de diseño a "
            "tensión PRS de la sección.\n\n"
            "Para miembros a tensión conectados excéntricamente en los "
            "extremos, es generalmente necesario referirse a F.5.4.8 "
            "para tener en cuenta la interacción entre la carga axial y "
            "los momentos introducidos. Sin embargo, en ciertos casos "
            "(véase F.5.4.6.2) se permite usar un procedimiento "
            "simplificado.\n\n"
            "F.5.4.6.1 — Resistencia a tensión — La resistencia a "
            "tensión de diseño PRS se debe tomar como el menor de los "
            "dos valores correspondientes a:\n\n"
            "• Fluencia general a lo largo del miembro\n"
            "• Falla local en una sección crítica\n\n"
            "(a) Fluencia general — El valor de PRS se basa en la "
            "sección transversal general del miembro a lo largo de su "
            "longitud, ignorando el efecto de las conexiones de los "
            "extremos, agujeros ocasionales o regiones afectadas por el "
            "calor localizadas, de la siguiente manera:\n\n"
            "Para un miembro libre de ablandamiento en la zona afectada "
            "por el calor o únicamente afectado en posiciones "
            "localizadas a lo largo de su longitud:\n\n"
            "PRS = φ po A  (F.5.4.6-1)\n\n"
            "Para un miembro en el cual la sección contiene material "
            "afectado por el calor generalmente a lo largo de su "
            "longitud, como con soldaduras longitudinales:\n\n"
            "PRS = φ po Ae  (F.5.4.6-2)\n\n"
            "Donde:\n"
            "po = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "A = área de la sección bruta\n"
            "Ae = área de la sección efectiva\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n\n"
            "El valor de Ae se encuentra tomando un área reducida igual "
            "a kz veces el área real para una zona ablandada, tomando "
            "kz como se indica en F.5.4.4.2 y la extensión de la zona "
            "de acuerdo con F.5.4.4.3."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_6_1_b_falla_local",
        "seccion": "F.5.4.6.1(b) — Falla local",
        "titulo": "PRS=φpaAn eq F.5.4.6-3 (sin ablandamiento); PRS=φpaAne eq F.5.4.6-4 (con ablandamiento)",
        "texto": (
            "(b) Falla local — El valor de PRS se basa en la sección "
            "más crítica como se indica enseguida:\n\n"
            "Para una sección libre de ablandamiento en la zona "
            "afectada por el calor:\n"
            "PRS = φ pa An  (F.5.4.6-3)\n\n"
            "Para una sección que contiene material afectado por el "
            "calor:\n"
            "PRS = φ pa Ane  (F.5.4.6-4)\n\n"
            "Donde:\n"
            "pa = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "An = área de la sección neta, con reducción por agujeros\n"
            "Ane = área de la sección neta efectiva\n"
            "φ = coeficiente de reducción de capacidad (véase F.5.3.1)\n\n"
            "El valor de Ane se encuentra en la misma forma que el de "
            "Ae (véase el literal (a) de F.5.4.6.1) pero con la "
            "apropiada reducción por agujeros, si es necesaria. La "
            "reducción por agujeros en las regiones afectadas por el "
            "calor puede hacerse con base en el espesor reducido kz t."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_6_1_c_agujeros_escalonados",
        "seccion": "F.5.4.6.1(c) — Agujeros escalonados",
        "titulo": "H=ΣAh-Σx²t/4y eq F.5.4.6-5",
        "texto": (
            "(c) Agujeros escalonados — Cuando hay agujeros escalonados, "
            "se deben calcular valores alternos de An o Ane usando las "
            "siguientes indicaciones y el valor menor será luego usado "
            "en el literal (b) de este mismo numeral.\n\n"
            "• An o Ane se toma como la sección transversal más "
            "desfavorable.\n"
            "• Se considera una sección diagonal o en zig-zag "
            "encontrando An o Ane como sigue:\n\n"
            "An = A - H o, Ane = Ae - H\n\n"
            "Donde:\n\n"
            "H = ΣAh - (Σx²t) / 4y  (F.5.4.6-5)\n\n"
            "x, y = separación longitudinal y transversal, "
            "respectivamente, de los agujeros\n"
            "t = espesor de la lámina o espesor efectivo de la lámina\n"
            "ΣAh = suma de las áreas de agujero en la sección diagonal "
            "o en zig-zag considerada"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_6_1_d_2_hibridas_tirantes_excentricos",
        "seccion": "F.5.4.6.1(d) — Secciones híbridas; F.5.4.6.2 — Tirantes conectados excéntricamente",
        "titulo": "Ángulos por una aleta, canales por el alma, T por la aleta; 0.6Ao / 0.2Ao",
        "texto": (
            "(d) Secciones híbridas — La capacidad a tensión de una "
            "sección híbrida que contiene materiales de diferente "
            "resistencia, se debe encontrar sumando las resistencias de "
            "las varias partes obtenidas en el literal (b) de este "
            "numeral.\n\n"
            "F.5.4.6.2 — Tirantes conectados excéntricamente — Los "
            "tirantes conectados excéntricamente incluyen lo siguiente:\n\n"
            "• Ángulos conectados únicamente por una aleta\n"
            "• Canales conectados por el alma\n"
            "• Secciones T conectadas por la aleta\n\n"
            "Los miembros a tensión de estos tres tipos con un sólo "
            "vano pueden diseñarse como cargados axialmente y la "
            "variación de esfuerzo en el lado o los lados salientes "
            "puede ignorarse, siempre y cuando al determinar el área An "
            "o Ane requerida para la revisión local (véase el literal "
            "(b) de F.5.4.6.1), parte del área del lado saliente se "
            "sustraiga del área bruta, lo mismo que cualquier reducción "
            "por agujeros o por efectos de zona afectada por el calor. "
            "La cantidad de lado sobresaliente a ser restada se toma "
            "como se indica a continuación:\n\n"
            "(1) Componente único conectado por un lado a una cartela: "
            "0.6Ao\n"
            "(2) Componente doble simétricamente conectado a cada lado "
            "de una cartela: 0.2Ao\n\n"
            "donde Ao es el área efectiva del lado o lados salientes "
            "del elemento conectado, ignorando cualquier filete.\n\n"
            "Cuando tales miembros son continuos sobre varios vanos, "
            "sólo hay que aplicar el tratamiento anterior a los "
            "extremos exteriores de los vanos extremos. En cualquier "
            "otro lugar, la resistencia local a tensión puede "
            "encontrarse de acuerdo con el literal (b) de F.5.4.6.1 sin "
            "ninguna reducción por aleta saliente.\n\n"
            "La revisión a fluencia general debe ser hecha de acuerdo "
            "con el literal (a) de F.5.4.6.1."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks...")
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print(f"\nSubiendo {len(rows)} chunks a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks de F.5.4.6 cargados.")
    max_len = max(len(c["texto"]) for c in CHUNKS)
    print(f"Chunk más largo: {max_len} caracteres.")


if __name__ == "__main__":
    main()
