"""
Ingesta verbatim de NSR-10 Título F.5.4.8 (cierre) + F.5.4.9 (Estructuras
de Aluminio -- Diseño Estático de Miembros): completa F.5.4.8.2 (cola,
cortada a mitad de párrafo en el PDF anterior), F.5.4.8.3 (Revisión de la
sección), F.5.4.8.4 (Revisión por pandeo general, casos A/B/C/D) y F.5.4.9
(Deformación, estado límite de servicio, con F.5.4.9.1).

Con esto queda CERRADO todo F.5.4 (Diseño estático de miembros de
aluminio: F.5.4.1 a F.5.4.9).

Fuente: NSR-10-1183-1283.pdf (páginas internas F-502 a F-503), recién
descargado desde Google Drive (id 1xuOZukeQsLIV957z59BK2eJqpZ5qu__b) y
guardado en scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset
confirmado en la Fase 1: página_F = página_real - 681 (equivalente a
página_interna_del_PDF + 501, sin discontinuidad de texto respecto al
corte del PDF anterior -- verificado que la primera frase del nuevo
archivo es la continuación literal de la última frase cortada del
archivo anterior).

Uso: python _ingest_titulo_f_f548_f549_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_4_8_2", "seccion": "F.5.4.8.2",
        "titulo": "F.5.4.8.2 — Clasificación de la sección y pandeo local bajo acciones combinadas (cierre): valor β para momento vs. para resistencia axial",
        "texto": (
            "F.5.4.8.2 — Clasificación de la sección y pandeo local bajo acciones combinadas (continuación) — "
            "(g=1). Mientras que para hallar la resistencia a momento, se toma un valor β que se relaciona con el "
            "patrón de esfuerzo en el elemento cuando la sección está bajo flexión pura."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_8_3", "seccion": "F.5.4.8.3",
        "titulo": "F.5.4.8.3 — Revisión de la sección: fórmula general caso D (ec. F.5.4.8-1), otros casos con cantidad igualada a cero",
        "texto": (
            "F.5.4.8.3 — Revisión de la sección. "
            "(a) Fórmula general (caso D) — La sección transversal es adecuada si lo siguiente se satisface en "
            "cualquier posición a lo largo de la longitud, todas las seis cantidades se toman como positivas: "
            "P/PRS + Mx/MRSx + My/MRSy ≤ 1.0  (F.5.4.8-1). "
            "(b) Otros casos — Para los casos A, B o C (véase F.5.4.8.1) se debe usar la fórmula F.5.4.8-1, con la "
            "cantidad apropiada del numerador igualada a cero."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_8_4_intro_a_b", "seccion": "F.5.4.8.4",
        "titulo": "F.5.4.8.4 — Revisión por pandeo general: Caso A (ec. F.5.4.8-2/3) y Caso B (ec. F.5.4.8-4)",
        "texto": (
            "F.5.4.8.4 — Revisión por pandeo general — Para miembros sujetos a tensión axial combinada con flexión, "
            "la presencia de la fuerza axial debe ser ignorada en la revisión para pandeo general. Para miembros "
            "sujetos a compresión axial con flexión, o a flexión biaxial, las fórmulas de interacción apropiadas "
            "(véanse los literales (a) a (d) de este numeral) deben ser satisfechas en cualquier longitud no "
            "soportada susceptible de pandeo. "
            "Todas las cantidades en las fórmulas de interacción se deben tomar positivas. "
            "(a) Caso A (flexión respecto al eje mayor con compresión axial) — Para el caso A, ambas condiciones, "
            "siguientes deben cumplirse: "
            "(1) Prevención del pandeo respecto al eje mayor: P/PRx + M̄x/MRSx + PM̄x/(2PRxMRSx) ≤ 1.0  (F.5.4.8-2). "
            "(2) Prevención del pandeo respecto al eje menor: P/PRy + M̄x/MRx ≤ 1.0  (F.5.4.8-3). "
            "Donde: M̄x = momento uniforme equivalente respecto al eje mayor, obtenido en el literal (b) de F.5.4.5.6. "
            "PRx, PRy = resistencias axiales de diseños a pandeo como columna general, alrededor de los ejes mayor "
            "y menor respectivamente (véanse F.5.4.7.2 y F.5.4.7.3). "
            "(b) Caso B (flexión respecto al eje menor con compresión axial) — Para el caso B, se debe satisfacer la "
            "siguiente única condición (prevención del pandeo respecto al eje menor): "
            "P/PRy + M̄y/MRSy + PM̄y/(2PRyMRSy) ≤ 1.0  (F.5.4.8-4). "
            "Donde: M̄y = momento uniforme equivalente respecto al menor eje obtenido como en el literal (b) de "
            "F.5.4.5.6 (nota: el documento fuente imprime aquí \"F.7.4.5.6\" por error tipográfico; la referencia "
            "correcta y consistente con el resto del numeral es F.5.4.5.6)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_8_4_c_d", "seccion": "F.5.4.8.4",
        "titulo": "F.5.4.8.4 — Caso C flexión biaxial (ec. F.5.4.8-5) y Caso D flexión biaxial con fuerza axial (ec. F.5.4.8-6)",
        "texto": (
            "(c) Caso C (flexión biaxial) — Para el caso C se debe satisfacer la siguiente única condición "
            "(prevención del pandeo respecto al eje menor): M̄x/MRx + M̄y/MRSy ≤ 1.0  (F.5.4.8-5). "
            "(d) Caso D (flexión biaxial con fuerza axial) — Para el caso D se debe satisfacer la siguiente "
            "condición: M̄x/MRPx + M̄y/MRPy ≤ 1.0  (F.5.4.8-6). "
            "Donde: MRPx = valor de M̄x que sería aceptable en combinación con P pero en ausencia de flexión "
            "respecto al eje menor, como está dado en el caso B (valor menor). MRPy = valor similar de M̄y en "
            "ausencia de flexión respecto al eje mayor, como está dado en el caso C."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_9_1", "seccion": "F.5.4.9",
        "titulo": "F.5.4.9 — Deformación (estado límite de servicio): deflexión elástica recuperable bajo carga nominal (F.5.3.4)",
        "texto": (
            "F.5.4.9 — DEFORMACION (ESTADO LIMITE DE SERVICIO) — La deflexión elástica recuperable bajo carga "
            "nominal (no mayorada) no debe exceder el valor límite (véase F.5.3.4). "
            "Si el estado límite último (resistencia estática) se ha satisfecho, usando F.5.4.2 a F.5.4.8, se puede "
            "suponer que la deformación inelástica permanente en servicio será despreciable. Generalmente no se "
            "requiere una revisión por separado para ésto."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_9_1_a_b", "seccion": "F.5.4.9.1",
        "titulo": "F.5.4.9.1 — Deflexión elástica recuperable: secciones compactas (a) vs. esbeltas (b), 3 procedimientos alternos",
        "texto": (
            "F.5.4.9.1 — Deflexión elástica recuperable. "
            "(a) Secciones compactas — La deflexión elástica de estas secciones puede calcularse usando las "
            "propiedades de la sección bruta, ignorando los agujeros y los efectos de zona afectada por el calor. "
            "Para vigas ésto se aplica para secciones totalmente compactas y semi-compactas. "
            "(b) Secciones esbeltas — Los cálculos de deflexión deben ser realizados generalmente usando las "
            "propiedades de la sección calculadas para una sección efectiva que tiene en cuenta el pandeo local "
            "pero ignora cualquier efecto de ablandamiento causado por el calor o de agujeros. La sección efectiva "
            "supuesta puede tomarse conservadoramente con base en el espesor reducido como está dado en el literal "
            "(c.1) de F.5.4.5.2 para flexión o en el literal (a.1) de F.5.4.7.5 para compresión axial, también "
            "puede adoptarse el siguiente procedimiento más favorable: "
            "(1) Reclasificar un elemento esbelto usando un valor modificado de ε en el literal (c) de F.5.4.3.3, "
            "obtenido tomando po igual a 2/3 del valor normal dado en las tablas F.5.4.2-1 y F.5.4.2-2. "
            "(2) Si la sección ya no resulta ser esbelta, se toman las propiedades de la sección bruta. "
            "(3) Si después de la reclasificación, resulta aún esbelta, se supone una nueva sección efectiva "
            "basada en los valores de kL encontrados usando el valor modificado de ε de (a) en la figura F.5.4.3-5."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")


if __name__ == "__main__":
    main()
