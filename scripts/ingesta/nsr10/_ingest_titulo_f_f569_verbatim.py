"""
Ingesta verbatim de NSR-10 Título F.5.6.9 completo (Resistencia de
Diseño de Soldaduras -- Estructuras de Aluminio): metal de soldadura a
tope (.9.1, ec. F.5.6.9-1 a -4), metal de soldadura de filete (.9.2, ec.
F.5.6.9-5 a -7) y zonas afectadas por el calor (.9.3, ec. F.5.6.9-8 a
-16). Fase 9 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-531 a F-534, más el
tramo inicial de F.5.6.9.1 ya visto en la Fase 8 en F-530/531), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.6.9-1, F.5.6.9-2 y
F.5.6.6.9-3 son diagramas/curvas gráficas (geometría de carga sobre
soldadura, curva de longitud efectiva lf/L vs. L/gt) -- solo se
transcriben verbatim las definiciones textuales de sus variables y, para
la Figura F.5.6.6.9-3, la nota de aplicabilidad (L/gt < 50), no los
valores leídos de la curva.

Uso: python _ingest_titulo_f_f569_verbatim.py
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
        "id": "NSR10-F-F_5_6_9_1", "seccion": "F.5.6.9.1",
        "titulo": "F.5.6.9 — Resistencia de Diseño de Soldaduras. F.5.6.9.1 — Metal de soldadura a tope: ec. F.5.6.9-1/2/3/4, cargas perpendicular/oblicua/paralela",
        "texto": (
            "F.5.6.9 — RESISTENCIA DE DISEÑO DE SOLDADURAS. "
            "F.5.6.9.1 — Metal de soldadura a tope — Una soldadura a tope de penetración parcial o completa solo "
            "se usarán para piezas resistentes cuando se verifique mediante ensayos que no se manifiestan defectos "
            "de soldadura. Para una soldadura a tope sometida a cortante y carga axial debe proporcionarse de modo "
            "que: (σ1² + 3τ2²)^(1/2) ≤ φ pw  (F.5.6.9-1). "
            "Donde: σ1 = esfuerzo normal perpendicular a la sección de la garganta bajo carga mayorada. "
            "τ2 = esfuerzo cortante que actúa sobre la sección de la garganta paralela al eje de la soldadura bajo "
            "carga mayorada. pw = esfuerzo límite del metal de aporte (véase F.5.6.8.2). φ = coeficiente de "
            "reducción de capacidad para el metal de aporte (véase la tabla F.5.3.3-1). "
            "Para una soldadura a tope con una carga de tensión oblicua (véase la figura F.5.6.9-1), la "
            "resistencia de diseño PRB está dada por: PRB = φ pw le te (1 + 2 cos²θ)^(-1/2)  (F.5.6.9-2). "
            "Donde: le = longitud efectiva de la soldadura. La longitud efectiva de la soldadura es la longitud "
            "total de la soldadura cuando se evitan las imperfecciones en los extremos mediante el uso de platinas "
            "de arranque y terminación. De otro modo, es la longitud total menos dos veces el ancho de soldadura "
            "(véase la figura F.5.6.9-1). te = espesor de garganta efectivo de la soldadura (véase F.5.6.7.7). "
            "θ = ángulo entre la línea de la soldadura a tope y la línea de acción de la carga externa (véase la "
            "figura F.5.6.9-1). "
            "El esfuerzo de diseño del metal de aporte a compresión puede ser tomado igual al de tensión, excepto "
            "cuando pueda ocurrir pandeo. "
            "Cuando el material base es de diferente espesor en cada lado de la soldadura, se debe investigar la "
            "posibilidad de un efecto de concentración de esfuerzos. "
            "Cuando la soldadura está sometida a flexión en su plano, la resistencia de diseño por unidad de "
            "longitud puede encontrarse omitiendo le en la expresión para PRB. "
            "Para una unión sin fuerzas de cortante externas y con la línea de la soldadura a tope perpendicular a "
            "la línea de acción de la carga externa, θ=90°, τ2=0 y la resistencia de diseño será: "
            "PRB = φ pw le te  (F.5.6.9-3). "
            "Para una fuerza cortante externa paralela a la línea de la soldadura a tope, la resistencia de diseño "
            "será: PRB = φ pw le te / √3  (F.5.6.9-4). "
            "Figura F.5.6.9-1 — Diseño de soldadura a tope: geometría 3D de una placa con soldadura a tope, "
            "mostrando la acción de carga externa S en el plano de las láminas, el ángulo θ y las componentes σ1/"
            "τ2. Diagrama geométrico, no se transcribe la geometría, solo las definiciones ya dadas arriba."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_9_2", "seccion": "F.5.6.9.2",
        "titulo": "F.5.6.9.2 — Metal de soldadura de filete: ec. F.5.6.9-5/6/7, transversal simple vs. longitudinal simple, Figura F.5.6.6.9-3 longitud efectiva lf (curva NO transcrita)",
        "texto": (
            "F.5.6.9.2 — Metal de soldadura de filete — Para el cálculo de una soldadura de filete, la sección de "
            "la garganta deberá ser tomada en base al espesor dominante de las partes a unir, dado que la "
            "resistencia real de una soldadura de filete queda definida por la garganta y las fuerzas actuantes en "
            "dicha sección. Una soldadura de filete debe proporcionarse de modo que se satisfaga la siguiente "
            "expresión: [σ1² + 3(τ1² + τ2²)]^(1/2) ≤ φ 0.85 pw  (F.5.6.9-5). "
            "Donde: pw, σ1, τ2, φ definidos en F.5.6.9.1. τ1 = esfuerzo cortante que actúa sobre la sección de "
            "garganta perpendicular al eje de la soldadura. "
            "La relación entre σ1, τ1 y τ2 está gobernada por la dirección de la acción de carga externa, S, en el "
            "sitio de la soldadura (véase la figura F.5.6.9-2). "
            "Para una soldadura de filete transversal simple (carga aplicada perpendicularmente a la longitud de "
            "la soldadura), σ1=τ1, τ2=0 y la resistencia de diseño se obtiene como sigue: "
            "PRF = φ 0.85 pw le gt / √2  (F.5.6.9-6). Donde: le es la longitud efectiva de la soldadura (igual que "
            "en soldaduras a tope). "
            "Para una soldadura de filete longitudinal simple (carga aplicada paralelamente a la longitud de la "
            "soldadura), σ1=τ1=0 y la resistencia de diseño depende sólo de τ2: "
            "PRF = φ 0.85 pw lf gt / √3  (F.5.6.9-7). Donde: lf es la longitud efectiva de la soldadura de filete. "
            "El valor de lf está influenciado por la longitud total de la soldadura, como se indica en la figura "
            "F.5.6.9-3, la que da una guía sobre la variación de lf con L, donde L es la longitud total de "
            "soldadura. La figura F.5.6.9-3 se basa en resultados experimentales. "
            "Figura F.5.6.9-3 — Longitud efectiva de soldaduras de filete longitudinales: curva de interpolación "
            "gráfica (eje vertical lf/L de 0.5 a 1.0, eje horizontal L/gt de 0 a 50). Nota del original: esta "
            "figura sólo se aplica si L/gt < 50. Es una lectura gráfica sin ecuación cerrada — no se transcriben "
            "valores numéricos de la curva, deben leerse directamente del PDF original (página F-533). "
            "Cuando la distribución de esfuerzos a lo largo de la soldadura corresponde a la del material base "
            "adyacente como, por ejemplo, en el caso de una soldadura que conecta la aleta y el alma de una viga "
            "ensamblada, la longitud efectiva se toma como si fuera una soldadura a tope. Si la soldadura está "
            "sometida a flexión en su plano, la resistencia de diseño por unidad de longitud puede ser encontrada "
            "omitiendo le o lf en la expresión de PRF. "
            "Figura F.5.6.9-2 — Diseño de soldadura de filete: geometría 3D de un filete con área efectiva de la "
            "sección transversal, componentes S/Sa/Sb de la acción de carga externa, ángulo de 45°, garganta de la "
            "soldadura. Diagrama geométrico, no se transcribe la geometría."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_9_3_a_b", "seccion": "F.5.6.9.3",
        "titulo": "F.5.6.9.3 — Zonas afectadas por el calor: fuerza de tensión directa (a, ec. F.5.6.9-8 a -11) y fuerza cortante (b, ec. F.5.6.9-12 a -15), soldadura a tope y de filete",
        "texto": (
            "F.5.6.9.3 — Zonas afectadas por el calor — La resistencia de diseño de una zona afectada por el calor "
            "adyacente a una soldadura (véanse las figuras F.5.6.7-1, F.5.6.7-2 y F.5.6.7-3) está dada por: "
            "(a) Fuerza de tensión directa normal al plano de falla (véase la figura F.5.6.7-3): "
            "(1) Soldadura a tope: PRFB = φ paz L te (en la frontera de fusión)  (F.5.6.9-8). "
            "PRTB = φ paz L t (en el borde de la soldadura, véase la figura F.5.6.7-3)  (F.5.6.9-9). "
            "Donde: PRFB y PRTB = resistencias directas de diseño de la zona afectada por el calor adyacente a una "
            "soldadura a tope. paz = esfuerzo directo límite en la zona afectada por el calor. L = longitud total "
            "de la soldadura. "
            "(2) Soldadura de filete: PRFF = φ paz L g1 (en la frontera de fusión)  (F.5.6.9-10). "
            "PRTF = φ paz L t (en el borde de la soldadura, véase la figura F.5.6.7-3 y F.5.6.9.3 (d))  "
            "(F.5.6.9-11). Donde: PRFF, PRTF = resistencias directas de diseño de la zona afectada por el calor "
            "adyacente a una soldadura de filete. "
            "(b) Fuerza cortante en el plano de falla: "
            "(1) Soldadura a tope: VRFB = φ pvz L t (en la frontera de fusión)  (F.5.6.9-12). "
            "VRTB = φ pvz L t (en el borde de la soldadura, véase la figura F.5.6.7-3)  (F.5.6.9-13). "
            "Donde: VRFB, VRTB = resistencias de diseño a cortante de la zona afectada por el calor adyacente a "
            "una soldadura a tope. "
            "(2) Soldadura de filete: VRFF = φ pvz L g1 (en la frontera de fusión)  (F.5.6.9-14). "
            "VRTF = φ pvz L t (en el borde de la soldadura, véase la figura F.5.6.7-3 y F.5.6.9.3 (d))  "
            "(F.5.6.9-15). Donde: VRFF, VRTF = resistencias de diseño a cortante de la zona afectada por el calor "
            "adyacente a una soldadura de filete."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_9_3_c_a_f", "seccion": "F.5.6.9.3",
        "titulo": "F.5.6.9.3(c) — Combinación cortante+fuerza directa: (Sa/PRZ)²+(Sb/VRZ)²≤1 (ec. F.5.6.9-16). (d)(e)(f) — Notas: espesor efectivo, flexión en el plano, combinación cortante+directo",
        "texto": (
            "(c) Cuando hay una combinación de cortante y fuerza directa sobre la zona afectada por el calor, "
            "estas fuerzas deben limitarse de acuerdo con la siguiente ecuación: "
            "(Sa/PRZ)² + (Sb/VRZ)² ≤ 1  (F.5.6.9-16). "
            "Donde: Sa, Sb = acciones de carga externas de cargas mayoradas directa y cortante, sobre la zona "
            "afectada por el calor. PRZ, VRZ = resistencias de diseño de carga directa y cortante de la zona "
            "afectada por el calor. "
            "(d) Cuando se revisa la resistencia de diseño de una soldadura de filete en el borde de la soldadura, "
            "se debe tener en cuenta que, para secciones más gruesas, la zona afectada por el calor no se extiende "
            "en todo el espesor y debe tomarse un valor de t más pequeño (véase la figura F.5.4.4-1 (i) y el "
            "literal (a) de F.5.4.4.3). "
            "(e) Cuando el plano de falla está sometido a flexión en su plano, la resistencia de diseño puede "
            "expresarse en términos de resistencia por unidad de longitud, omitiendo L en las anteriores "
            "ecuaciones. "
            "(f) Cuando el plano de falla está sometido a flexión en su plano y cortante, la resistencia de diseño "
            "por unidad de longitud debe reducirse para tener en cuenta los efectos combinados de cortante y "
            "esfuerzo directo (véase F.5.6.9.3 (c))."
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
