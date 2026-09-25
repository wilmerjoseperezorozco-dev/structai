"""
Ingesta verbatim de NSR-10 Título F.5.5.1 (Generalidades) y F.5.5.2
completo (Láminas No Rigidizadas -- Estructuras de Aluminio: esfuerzo
directo, momento en el plano, gradiente longitudinal, cortante, acciones
combinadas). Fase 3 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-503 a F-508), ya
descargado desde Google Drive en la Fase 2 (id
1xuOZukeQsLIV957z59BK2eJqpZ5qu__b), en scripts/ingesta/nsr10/raw/
(gitignored). Mismo offset confirmado: página_F = página_real - 681.

Uso: python _ingest_titulo_f_f551_f552_verbatim.py
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
        "id": "NSR10-F-F_5_5_1", "seccion": "F.5.5.1",
        "titulo": "F.5.5 — Láminas y Vigas Ensambladas. F.5.5.1 — Generalidades: láminas no rigidizadas/multi-rigidizadas, vigas ensambladas (figuras F.5.5.1-1/2/3)",
        "texto": (
            "F.5.5 — LÁMINAS Y VIGAS ENSAMBLADAS. "
            "F.5.5.1 — GENERALIDADES — Esta sección cubre la resistencia estática (estado límite último) de los "
            "siguientes componentes estructurales: "
            "(a) Láminas no rigidizadas (véase F.5.5.2 y la figura F.5.5.1-1). "
            "(b) Láminas multi-rigidizadas (véase F.5.5.3 y la figura F.5.5.1-2). "
            "(c) Vigas ensambladas (véase F.5.5.4 y la figura F.5.5.1-3). "
            "Figura F.5.5.1-1 — Lámina no rigidizada: panel plano de ancho d y longitud a, sometido a momento M, "
            "fuerza axial P y cortante V aplicados en su plano. "
            "Figura F.5.5.1-2 — Lámina multi-rigidizada: panel de ancho B y longitud L reforzado con rigidizadores "
            "longitudinales intermedios igualmente espaciados (separación w, posición y), representado también con "
            "su perfil corrugado tipo sombrero. "
            "Figura F.5.5.1-3 — Viga ensamblada: alma esbelta de altura d entre paneles rigidizados por atiesadores "
            "transversales (separación a), con patines A y rigidizadores intermedios C y de apoyo B. "
            "Para (a) y (c), la resistencia obtenida tiende a ser más favorable que la basada en las reglas más "
            "simples de F.5.4, especialmente si se consideran láminas o almas esbeltas de baja relación de (a/d). "
            "El numeral F.5.4 no cubre las láminas multi-rigidizadas."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_intro", "seccion": "F.5.5.2",
        "titulo": "F.5.5.2 — Láminas No Rigidizadas: alcance de F.5.5.2.1 a F.5.5.2.5, espesor t",
        "texto": (
            "F.5.5.2 — LAMINAS NO RIGIDIZADAS — Las láminas no rigidizadas sujetas a esfuerzo directo pueden "
            "diseñarse de acuerdo con F.5.5.2.1 a F.5.5.2.3, las sujetas a cortante, según F.5.5.2.4. Los efectos "
            "de interacción se discuten en F.5.5.2.5. "
            "El espesor de la lámina se denominará t para todos los casos."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_1_a_b", "seccion": "F.5.5.2.1",
        "titulo": "F.5.5.2.1 — Láminas no rigidizadas bajo esfuerzo directo: clasificación β≤β1/β≤βo (ec. F.5.5.2-1) y resistencia axial totalmente compacta/semi-compacta (ec. F.5.5.2-2/3)",
        "texto": (
            "F.5.5.2.1 — Láminas no rigidizadas bajo esfuerzo directo — La resistencia de una lámina a compresión "
            "uniforme en su plano, P, actuando en la dirección mostrada en la figura F.5.5.1-1, se describe en los "
            "literales (a) a (c) de este numeral. "
            "(a) Clasificación — La lámina se debe clasificar de acuerdo con lo siguiente: β≤β1 totalmente "
            "compacta; β1<β≤βo semi-compacta; β>βo esbelta. Donde: β = d/t  (F.5.5.2-1). βo y β1 dadas en la tabla "
            "F.5.4.3. "
            "(b) Láminas totalmente compactas y semi-compactas — La resistencia axial de diseño PRS a compresión "
            "uniforme debe basarse en la sección transversal menos favorable como se indica a continuación: "
            "totalmente compacta: PRS = pa Ane φ  (F.5.5.2-2). semi-compacta: PRS = po Ane φ  (F.5.5.2-3). "
            "Donde: pa y po = esfuerzos límite (véanse las tablas F.5.4.3-1 y F.5.4.3-2). Ane = área neta efectiva "
            "teniendo en cuenta los agujeros y tomando un espesor reducido kz t en cualquier región afectada por "
            "ablandamiento debido al calor (véanse F.5.4.4.2 y F.5.4.4.3). φ = coeficiente de reducción de "
            "capacidad (véase la tabla F.5.3.3-1)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_1_c", "seccion": "F.5.5.2.1(c)",
        "titulo": "F.5.5.2.1(c) — Láminas esbeltas: revisión por fluencia y por pandeo, factor kL por tratamiento como lámina (ec. F.5.5.2-4) o como columna",
        "texto": (
            "(c) Láminas esbeltas — Se debe hacer una revisión por fluencia y otra por pandeo tomando los "
            "siguientes valores para la resistencia axial de diseño PRS. "
            "(1) Revisión por fluencia — Para una lámina semi-compacta, PRS se obtiene como en el literal (b) de "
            "este numeral ignorando el pandeo. "
            "(2) Revisión por pandeo — PRS = φ po Ae. Donde: po = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2). Ae = área efectiva obtenida teniendo en cuenta el espesor reducido para considerar el "
            "pandeo y el ablandamiento en la zona afectada por el calor, pero ignorando los agujeros. "
            "Para la revisión por pandeo el área efectiva generalmente debe basarse en la sección transversal menos "
            "favorable, tomando un espesor igual al menor de kz t y kL t en las regiones afectadas por el calor, y "
            "kL t en las demás zonas. Sin embargo, en esta revisión se puede ignorar el ablandamiento debido a "
            "soldaduras en los bordes cargados. "
            "El factor kL puede determinarse mediante el más favorable de los siguientes tratamientos: "
            "Tratamiento como lámina — kL se lee en la curva C o D de la figura F.5.4.3-5 tomando: β = d/t y "
            "ε = (25/po)^(1/2)  (F.5.5.2-4). "
            "Tratamiento como columna — kL se toma igual a la relación ps/po, en la que ps es el esfuerzo de pandeo "
            "como columna leído en la figura F.5.4.5-3 (a). La curva apropiada es la que intersecta el eje de "
            "esfuerzos en un valor po. El parámetro de esbeltez λ debe ser normalmente tomado como: λ = 3.5a/t "
            "— este valor corresponde a apoyo simple, aunque se puede tomar un valor menor si es justificado."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_2", "seccion": "F.5.5.2.2",
        "titulo": "F.5.5.2.2 — Láminas no rigidizadas bajo momento en su plano: clasificación (ec. F.5.5.2-6), resistencia compacta/semi-compacta y esbelta",
        "texto": (
            "F.5.5.2.2 — Láminas no rigidizadas bajo momento en su plano — La resistencia de una lámina ante "
            "momento puro en su plano actuando sobre los lados de ancho d (véase la figura F.5.5.1-1) se describe "
            "en los literales (a) a (c) de este numeral. Si el momento varía en la dirección paralela a la "
            "dimensión a, consulte también F.5.5.2.3. "
            "(a) Clasificación — La lámina debe clasificarse de acuerdo con: β≤β1 totalmente compacta; "
            "β1<β≤βo semi-compacta; β>βo esbelta. Donde: β = 0.35d/t  (F.5.5.2-6). βo y β1 están dados en la tabla "
            "F.5.4.3. "
            "(b) Láminas totalmente compactas y semi-compactas — La resistencia de diseño a momento MRS se debe "
            "tomar con base en la sección transversal menos favorable usando la expresión pertinente del literal "
            "(b) de F.5.4.5.2 (numerales F.5.19 a F.5.22) y tomando una sección supuesta tal como lo define el "
            "literal (c) del mismo numeral en las dos primeras partes. "
            "(c) Láminas esbeltas — La resistencia de diseño a momento debe tomarse como el menor de los valores "
            "encontrados en las revisiones por fluencia y pandeo: "
            "(1) Revisión por fluencia — Para una lámina semi-compacta, MRS se obtiene como en el literal (b) de "
            "F.5.5.2.2 ignorando el pandeo. "
            "(2) Revisión por pandeo — Se determina MRS tal como se indica a continuación: "
            "MRS = φ po Ze  (F.5.5.2-7). Donde: Ze = módulo elástico de la sección efectiva. "
            "El cálculo de F.5.5.2-7 debe basarse, por lo general, en la sección efectiva en la posición más "
            "desfavorable, sin reducción por agujeros y tomando un espesor igual al menor entre kz t y kL t en las "
            "regiones afectadas por el calor, y kL t en las demás zonas. Sin embargo, en esta revisión puede "
            "ignorarse el ablandamiento debido a soldaduras en los bordes cargados. "
            "El factor kL debe ser leído en la curva C o D de la figura F.5.4.3-5 tomando: β = 0.35d/t y "
            "ε = (25/po)^(1/2)  (F.5.5.2-8)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_3", "seccion": "F.5.5.2.3",
        "titulo": "F.5.5.2.3 — Gradiente de esfuerzo longitudinal en láminas no rigidizadas: compactas/semi-compactas (a) vs. esbeltas con criterio de distancia x=0.4·(longitud media onda pandeo) (b)",
        "texto": (
            "F.5.5.2.3 — Gradiente de esfuerzo longitudinal en láminas no rigidizadas — Los casos en que la acción "
            "aplicada P o M sobre una lámina no rigidizada varía longitudinalmente en la dirección mostrada en la "
            "figura F.5.5.1-1, se presentan en los siguientes literales. "
            "(a) Láminas totalmente compactas y semi-compactas — La resistencia de diseño en cualquier sección "
            "transversal no debe ser menor que la acción generada en esa sección bajo carga mayorada. "
            "(b) Láminas esbeltas — La revisión por fluencia debe satisfacerse una vez más en cada sección "
            "transversal. Para la revisión por pandeo, es suficiente comparar la resistencia de diseño con la "
            "acción generada a una distancia x del extremo más cargado del panel, donde x es igual a 0.4 veces la "
            "longitud de la media onda de pandeo elástico de la lámina."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_4", "seccion": "F.5.5.2.4",
        "titulo": "F.5.5.2.4 — Láminas no rigidizadas sometidas a cortante: alma compacta (ec. F.5.5.2-9) vs. esbelta (ec. F.5.5.2-10/11)",
        "texto": (
            "F.5.5.2.4 — Láminas no rigidizadas sometidas a cortante — Las láminas no rigidizadas sujetas a "
            "cortante deben clasificarse como compactas o esbeltas de acuerdo con el literal (a) de F.5.4.5.3. "
            "La presencia de agujeros pequeños puede ignorarse en el cálculo de la resistencia al corte siempre y "
            "cuando ellos no ocupen más del 20% del área de la sección transversal sobre el ancho d. "
            "(a) Alma a cortante compacta — La resistencia de diseño a fuerza cortante VRS debe encontrarse usando "
            "lo siguiente: VRS = φ pv Av  (F.5.5.2-9). Donde: pv = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2). φ = coeficiente de reducción de capacidad (véase la tabla F.5.3.3-1). Av = área de "
            "cortante efectiva tomada de acuerdo con: para láminas no soldadas Av = dt. Para láminas totalmente "
            "soldadas a lo largo de uno o más bordes Av = kz dt. Para láminas parcialmente soldadas, Av es el área "
            "efectiva sobre el ancho d encontrada tomando un espesor reducido kz t en las zonas ablandadas (véanse "
            "F.5.4.4.2 y F.5.4.4.3). "
            "(b) Alma a cortante esbelta — La resistencia de diseño a fuerza cortante VRS se debe tomar como el "
            "menor de los dos valores obtenidos como sigue: "
            "(1) Revisión por fluencia — La resistencia se encuentra, como para una lámina compacta, usando el "
            "literal (a) de F.5.5.2.4. "
            "(2) Revisión por pandeo — La resistencia puede encontrarse, seguramente, como se hizo en el literal "
            "(c) de F.5.4.5.3. Alternativamente, la siguiente expresión puede usarse y es más favorable cuando a es "
            "menor que 2.5d: VRS = φ v1 pv dt  (F.5.5.2-10). donde v1 es el coeficiente de pandeo por cortante "
            "elástico leído en la figura F.5.5.3-1 tomando ε = (15/pv)^(1/2)  (F.5.5.2-11). "
            "La expresión del literal (c) de F.5.4.5.3 no tiene en cuenta la acción de campo tensionado. Si se cree "
            "que las condiciones de borde son tales que se tiene un campo tensionado, el diseñador debe referirse a "
            "un tratamiento aún más favorable disponible para paneles tipo 1 en almas de vigas ensambladas (véase "
            "el literal (c) de F.5.5.4.2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_2_5", "seccion": "F.5.5.2.5",
        "titulo": "F.5.5.2.5 — Láminas no rigidizadas: acciones combinadas, fuerza axial con momento (ec. F.5.5.2-12) y esfuerzo directo con cortante elevado (ec. F.5.5.2-13)",
        "texto": (
            "F.5.5.2.5 — Acciones combinadas — Una lámina, sujeta a fuerza axial P combinada con momento M bajo "
            "carga mayorada, debe clasificarse como totalmente compacta, semi-compacta o esbelta, generalmente de "
            "acuerdo con el literal (a) de F.5.4.8.2. Para hacer ésto, el valor de β tomado debe basarse en el "
            "patrón de esfuerzo producido en la lámina cuando P y M actúan conjuntamente, basándose en un valor "
            "apropiado de g (véase la figura F.5.4.3-2). "
            "Cuando la lámina se clasifica como esbelta, cada resistencia individual (PRS y MRS) debe basarse en el "
            "tipo específico de acción considerada, como en el literal (b) de F.5.4.8.2. "
            "(a) Fuerza axial con momento — La siguiente condición debe satisfacerse para una lámina sujeta a "
            "fuerza axial con momento: P/PRS + M/MRS ≤ 1.0  (F.5.5.2-12). Donde: P y M = fuerza axial y momento en "
            "el plano, respectivamente, generados bajo carga mayorada. PRS y MRS = resistencias de diseño a fuerza "
            "axial y momento en el plano, respectivamente, cada una reducida para tener en cuenta cortante elevado "
            "coincidente, si es necesario (véase el literal (c) de F.5.5.2.5). "
            "(b) Esfuerzo directo con cortante bajo — Se puede suponer que una fuerza de cortante coincidente V "
            "(bajo carga mayorada) no tiene efecto sobre la resistencia de la lámina siempre que V no exceda la "
            "mitad de la resistencia a fuerza cortante de diseño VRS. "
            "(c) Esfuerzo directo con cortante elevado — Si V excede 0.5·VRS, la resistencia longitudinal (fuerza "
            "axial, momento) se debe reducir por un coeficiente kv donde: kv = 1.6 - 1.2V/VRS  (F.5.5.2-13)."
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
