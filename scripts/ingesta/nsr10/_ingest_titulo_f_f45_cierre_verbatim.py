"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.5 (Conexiones y Uniones) -- CIERRE,
completa lo que quedo pendiente de _ingest_titulo_f_f45_verbatim.py:
resto de F.4.5.4.3 (ecuacion F.4.5.4-6), F.4.5.4.3.3 (cortante en
tornillos), F.4.5.4.4 completo (tension en tornillos, desgarramiento
del tornillo y del material, arandelas tipo (a)/(b)/(c)), F.4.5.4.5
(comportamiento combinado cortante+desgarramiento), F.4.5.5 (ROTURA --
a cortante, a tension, por bloque de cortante) y F.4.5.6 (CONEXIONES A
OTROS MATERIALES -- apoyo, tension/arrancamiento, cortante). Con esto
F.4.5 queda COMPLETO. Sexta pieza de F.4/F.5.

F.4.6 (ENSAYOS PARA CASOS ESPECIALES) empieza justo despues de F.4.5.6
en el mismo PDF (pagina F-396) y F.4.7 (Tableros metalicos) arranca en
F-401, la ultima pagina de este PDF -- queda para otra sesion, no es
parte de F.4.5.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final igual que F.4.2/F.4.3/F.4.4/F.4.5 (parcial).

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
paginas internas F-393 a F-396 (paginas PDF 93-96), leidas visualmente
pagina por pagina.

Uso: python _ingest_titulo_f_f45_cierre_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_4_5_4_3_2_ecuacion6_cortante_tornillo",
        "seccion": "F.4.5.4.3.2 (Cortante limitado por distancia al borde — ecuación F.4.5.4-6)",
        "titulo": "Pns = t·e·Fu, φ=0.50, con t=espesor de la parte, e=distancia al borde, Fu=resistencia última.",
        "texto": (
            "Pns = teFu (F.4.5.4-6). φ = 0.50. Donde: t = espesor de la "
            "parte en la cual se mide la distancia al borde. e = distancia "
            "medida en la línea de la fuerza a partir del centro de una "
            "perforación estándar al borde más cercano de la parte "
            "conectada. Fu = resistencia última de la parte en la cual se "
            "mide la distancia al borde."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_3_3_cortante_en_tornillos",
        "seccion": "F.4.5.4.3.3 (Cortante en tornillos)",
        "titulo": "Pss = resistencia nominal a cortante del tornillo, alternativa vía F.4.6.1 con φ/1.25≥0.5.",
        "texto": (
            "F.4.5.4.3.3 — Cortante en tornillos — La resistencia nominal "
            "a cortante del tornillo se tomará como Pss. En lugar de los "
            "valores suministrados en la sección F.4.5.4, se permitirá la "
            "determinación del factor de resistencia mediante lo dispuesto "
            "en la sección F.4.6.1, y debe cumplirse que φ/1.25 ≥ 0.5."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_4_tension_intro",
        "seccion": "F.4.5.4.4 (Tensión — requisito de arandela/cabeza)",
        "titulo": "Diámetro mínimo de cabeza/arandela 8 mm, espesor mínimo de arandela 1.27 mm.",
        "texto": (
            "F.4.5.4.4 — Tensión — Para tornillos que soportan tensión, la "
            "cabeza, o arandela, si se utiliza, tendrá un diámetro dh, o "
            "dw, no menor a 8 mm. Las arandelas deben tener como mínimo un "
            "espesor de 1.27 mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_4_1_desgarramiento_tornillo",
        "seccion": "F.4.5.4.4.1 (Desgarramiento del tornillo — ecuación F.4.5.4-7)",
        "titulo": "Pnot = 0.85·tc·d·Fu2.",
        "texto": (
            "F.4.5.4.4.1 — Desgarramiento del tornillo — La resistencia "
            "nominal al desgarramiento del tornillo, Pnot, se calculará "
            "como sigue: Pnot = 0.85·tc·d·Fu2 (F.4.5.4-7)."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_4_2_desgarramiento_material_a",
        "seccion": "F.4.5.4.4.2 (Desgarramiento del material en contacto con la cabeza o arandela — ecuación F.4.5.4-8, caso (a))",
        "titulo": "Pnov = 1.5·t1·d'w·Fu1; d'w para arandela de acero independiente bajo la cabeza (ecuación F.4.5.4-9).",
        "texto": (
            "F.4.5.4.4.2 — Desgarramiento del material en contacto con la "
            "cabeza o la arandela — La resistencia nominal al "
            "desgarramiento del material en contacto con la cabeza del "
            "tornillo o la arandela, Pnov, se calculará como sigue: "
            "Pnov = 1.5·t1·d'w·Fu1 (F.4.5.4-8). Donde: d'w = diámetro "
            "efectivo al desgarramiento del material en contacto con la "
            "cabeza o la arandela, determinado de acuerdo con (a), (b) ó "
            "(c) como se muestra a continuación: (a) Para un tornillo con "
            "cabeza redonda, cabeza hexagonal (figura F.4.5.4-1(1)), o "
            "cabeza hexagonal con arandela integrada (figura F.4.5.4-1(2)) "
            "con una arandela de acero macizo e independiente debajo de la "
            "cabeza: d'w = dh + 2tw + t1 ≤ dw (F.4.5.4-9). Donde: dh = "
            "diámetro de la cabeza del tornillo ó diámetro de la arandela "
            "en los tornillos de cabeza hexagonal con arandela integrada. "
            "tw = espesor de la arandela de acero. dw = diámetro de la "
            "arandela de acero."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_4_2_desgarramiento_material_bc",
        "seccion": "F.4.5.4.4.2 (Desgarramiento del material — casos (b) sin arandela independiente y (c) arandela tipo domo)",
        "titulo": "d'w=dh (máx 12.7mm) sin arandela independiente; arandela tipo domo con d'w vía F.4.5.4-9, máx 16mm, o por ensayo F.4.6.",
        "texto": (
            "(b) Para un tornillo con cabeza redonda, cabeza hexagonal, o "
            "cabeza hexagonal con arandela integrada sin un arandela "
            "independiente debajo de la cabeza: d'w = dh pero no mayor a "
            "12.7 mm. (c) Para una arandela tipo domo (no maciza e "
            "independiente) debajo de la cabeza del tornillo (figura "
            "F.4.5.4-1(3)), se permite usar d'w como se calcula en la "
            "ecuación F.4.5.4-9, con dh, tw y t1 definidos de acuerdo a la "
            "figura F.4.5.4-1(3). En la ecuación, d'w no puede exceder "
            "16 mm. Alternativamente, se permite el cálculo de los "
            "valores de diseño de resistencia al desgarramiento del "
            "material alrededor de la cabeza para arandelas tipo domo, "
            "incluyendo el factor de resistencia, φ, mediante ensayos de "
            "acuerdo con F.4.6."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_4_3_tension_en_tornillos",
        "seccion": "F.4.5.4.4.3 (Tensión en tornillos)",
        "titulo": "Pts = resistencia nominal a tensión del tornillo, alternativa vía F.4.6.1 con φ/1.25≥0.5.",
        "texto": (
            "F.4.5.4.4.3 — Tensión en tornillos — La resistencia nominal "
            "a tensión del tornillo se tomará como Pts. En lugar de los "
            "valores suministrados en la sección F.4.5.4, se permitirá la "
            "determinación del factor de resistencia mediante lo dispuesto "
            "en la sección F.4.6.1, y debe cumplirse que φ/1.25 ≥ 0.5."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_5_comportamiento_combinado",
        "seccion": "F.4.5.4.5 (Comportamiento combinado entre el Cortante y el desgarramiento — ecuaciones F.4.5.4-10 a -12)",
        "titulo": "Q̄/Pns + 0.71·T̄/Pnov ≤ 1.10φ; Pns=2.7t1dFu1, Pnov=1.5t1dwFu1, φ=0.65, límites de validez y reducción 50% para cargas excéntricas.",
        "texto": (
            "F.4.5.4.5 — Comportamiento combinado entre el Cortante y el "
            "desgarramiento del material en contacto con la cabeza o la "
            "arandela — Para conexiones atornilladas sujetas a una "
            "combinación de fuerzas cortantes y de tensión deben cumplirse "
            "los siguientes requisitos: Q̄/Pns + 0.71·T̄/Pnov ≤ 1.10φ "
            "(F.4.5.4-10). Adicionalmente, Q̄ y T̄ no deben exceder las "
            "correspondientes resistencias de diseño determinadas conforme "
            "a las secciones F.4.5.4.3 y F.4.5.4.4, respectivamente. "
            "Donde: Q̄ = resistencia requerida a cortante de la conexión, "
            "Q̄ = Vu. T̄ = resistencia requerida a tensión de la conexión, "
            "T̄ = Tu. Pns = resistencia nominal a cortante de la conexión "
            "= 2.7·t1·d·Fu1 (F.4.5.4-11). Pnov = resistencia nominal al "
            "desgarramiento del material en contacto con la cabeza o la "
            "arandela de la conexión = 1.5·t1·dw·Fu1 (F.4.5.4-12). Donde: "
            "dw = diámetro más grande de la cabeza del tornillo ó diámetro "
            "de la arandela. φ = 0.65. La ecuación F.4.5.4-10 es válida "
            "para conexiones que estén dentro de los siguientes límites: "
            "(1) 0.724 mm ≤ t1 ≤ 1.130 mm. (2) Tornillos auto-perforantes "
            "No. 12 y No. 14, con y sin arandelas. (3) dw ≤ 19.1 mm. "
            "(4) Fu1 ≤ 483 MPa. (5) t2/t1 ≥ 2.5. Para conexiones cargadas "
            "excéntricamente que produzcan una fuerza no uniforme de "
            "desgarramiento sobre el tornillo, la resistencia nominal al "
            "desgarramiento, Pnov, se debe reducir en un 50%."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_5_1_rotura_a_cortante",
        "seccion": "F.4.5.5.1 (Rotura a cortante — ecuaciones F.4.5.5-1 y -2)",
        "titulo": "Vn = 0.6·Fu·Awn, φ=0.75, Awn=(hwc − n·dh)·t, para aletas recortadas en extremos de vigas.",
        "texto": (
            "F.4.5.5 — ROTURA. F.4.5.5.1 — Rotura a cortante — En "
            "conexiones de extremos de vigas donde una o más aletas están "
            "recortadas y la falla puede ocurrir a lo largo de un plano a "
            "través de los sujetadores, la resistencia nominal a cortante, "
            "Vn, se debe calcular conforme a la ecuación F.4.5.5-1. "
            "Vn = 0.6·Fu·Awn (F.4.5.5-1). φ = 0.75. Donde: "
            "Awn = (hwc − n·dh)·t (F.4.5.5-2). hwc = altura del alma plana "
            "recortada. n = número de perforaciones en el plano crítico. "
            "dh = diámetro de la perforación. Fu = resistencia última de "
            "la parte conectada especificada en la sección F.4.1.2.1 ó "
            "F.4.1.2.2. t = espesor del alma recortada."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_5_2_rotura_a_tension",
        "seccion": "F.4.5.5.2 (Rotura a tensión)",
        "titulo": "Rotura a tensión a lo largo de un patrón, remitido a F.4.5.2.7 (soldadas) o F.4.5.3.2 (pernadas).",
        "texto": (
            "F.4.5.5.2 — Rotura a tensión — La resistencia de diseño a "
            "rotura por tensión a lo largo de un patrón, en los elementos "
            "afectados de los miembros conectados, se determinará de "
            "acuerdo a la sección F.4.5.2.7 ó F.4.5.3.2 para conexiones "
            "soldadas o mediante pernos, respectivamente."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_5_3_rotura_bloque_cortante",
        "seccion": "F.4.5.5.3 (Rotura por bloque de cortante — ecuaciones F.4.5.5-3 y -4)",
        "titulo": "Rn=menor entre 0.6FyAgv+FuAnt y 0.6FuAnv+FuAnt; aplica solo si t<4.76mm; φ=0.65 pernadas, 0.60 soldadas.",
        "texto": (
            "F.4.5.5.3 — Rotura por bloque de cortante — Cuando el espesor "
            "de la parte conectada más delgada sea menor a 4.76 mm, la "
            "resistencia nominal de rotura a bloque de cortante, Rn, se "
            "determinará de acuerdo con lo estipulado en esta sección. Las "
            "conexiones en las cuales el espesor de la parte conectada más "
            "delgada sea igual o mayor a 4.76 mm se deben calcular "
            "conforme al Capítulo F.2 del presente Reglamento. La "
            "resistencia nominal a la ruptura por bloque de cortante, Rn, "
            "se determinará como el menor valor entre las ecuaciones "
            "F.4.5.5-3 y F.4.5.5-4. Rn = 0.6·Fy·Agv + Fu·Ant (F.4.5.5-3). "
            "Rn = 0.6·Fu·Anv + Fu·Ant (F.4.5.5-4). Para conexiones "
            "pernadas φ = 0.65. Para conexiones soldadas φ = 0.60. Donde: "
            "Agv = área bruta sometida a cortante. Anv = área neta "
            "sometida a cortante. Ant = área neta sometida a tensión."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_6_1_apoyo",
        "seccion": "F.4.5.6.1 (Conexiones a otros materiales — Apoyo)",
        "titulo": "Deben proveerse mecanismos de transferencia de cargas de apoyo hacia componentes estructurales de otros materiales.",
        "texto": (
            "F.4.5.6 — CONEXIONES A OTROS MATERIALES. F.4.5.6.1 — Apoyo "
            "— Deben proveerse los mecanismos necesarios para "
            "transferencia de las cargas de apoyo provenientes de "
            "componentes en acero cubiertos por esta especificación a los "
            "componentes estructurales adyacentes hechos en otros "
            "materiales."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_6_2_tension",
        "seccion": "F.4.5.6.2 (Conexiones a otros materiales — Tensión)",
        "titulo": "Considerar cortante de arrancamiento y desgarramiento del sujetador; resistencia de anclaje por normas del producto o ensayo.",
        "texto": (
            "F.4.5.6.2 — Tensión — Debe considerarse el cortante de "
            "arrancamiento producido en la lámina de acero por fuerzas de "
            "tensión alrededor de la cabeza del sujetador, asimismo el "
            "desgarramiento del sujetador resultante de las fuerzas "
            "producidas por cargas axiales y momentos flectores "
            "transmitidos sobre el sujetador o tornillo, provenientes de "
            "varios componentes estructurales adyacentes en el ensamble. "
            "La resistencia nominal a la tensión del sujetador y la "
            "resistencia nominal de anclaje de los componentes "
            "estructurales adyacentes, deben determinarse por medio de las "
            "normas aplicables al producto, sus especificaciones, "
            "literatura pertinente o combinación de estas."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_6_3_cortante",
        "seccion": "F.4.5.6.3 (Conexiones a otros materiales — Cortante)",
        "titulo": "Transferencia de fuerzas cortantes hacia otros materiales, sin exceder valores permitidos por el Reglamento.",
        "texto": (
            "F.4.5.6.3 — Cortante — Deben proveerse los mecanismos "
            "necesarios para transferencia de las fuerzas cortantes "
            "provenientes de los componentes de acero cubiertos por este "
            "Reglamento a los componentes estructurales adyacentes hechos "
            "en otros materiales. La resistencia al cortante y al "
            "aplastamiento sobre los componentes de acero no excederá "
            "aquellos valores permitidos por este Reglamento. No debe ser "
            "excedida la resistencia de diseño a cortante en los "
            "sujetadores y el otro material. Deben cumplirse los "
            "requisitos referentes a los anclajes. Deben seguirse los "
            "procedimientos adecuados para el manejo de las fuerzas "
            "cortantes en combinación con otras fuerzas."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    max_len = 0
    for c in CHUNKS:
        n = len(c["texto"])
        max_len = max(max_len, n)
        print(f"  {c['id']}: {n} chars (~{round(n/4.5)} tokens est.)")
    print(f"\nMax chars: {max_len} (~{round(max_len/4.5)} tokens est.)")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in CHUNKS]
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

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de cierre de F.4.5 cargados. F.4.5 queda COMPLETO.")


if __name__ == "__main__":
    main()
