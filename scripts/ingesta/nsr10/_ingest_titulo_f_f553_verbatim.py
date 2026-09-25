"""
Ingesta verbatim de NSR-10 Título F.5.5.3 completo (Láminas
Multi-Rigidizadas -- Estructuras de Aluminio): compresión uniforme
(F.5.5.3.1), momento en su plano (F.5.5.3.2), gradiente de esfuerzos
longitudinal (F.5.5.3.3) y cortante (F.5.5.3.4). Fase 4 del plan de
cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-509 a F-511), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: la Figura F.5.5.3-1 (coeficiente de pandeo
crítico al corte en el rango elástico, v1) es una curva de interpolación
gráfica (familia de curvas paramétricas por relación a/d) sin ecuación
cerrada -- no se transcriben valores numéricos leídos de la curva, mismo
criterio ya aplicado a las figuras de F.5.4.7 en la Fase 1.

Uso: python _ingest_titulo_f_f553_verbatim.py
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
        "id": "NSR10-F-F_5_5_3_intro_1", "seccion": "F.5.5.3.1",
        "titulo": "F.5.5.3 — Láminas Multi-Rigidizadas. F.5.5.3.1 — Sujetas a compresión uniforme: revisión por fluencia (a) y como columna (b), ecuación F.5.5.3-1",
        "texto": (
            "Los tratamientos dados anteriormente (F.5.5.2) se invalidan si la sección transversal contiene "
            "elementos salientes que se clasifiquen como esbeltos. "
            "Cuando la construcción consiste de láminas planas con rigidizadores superpuestos, la resistencia a "
            "esfuerzo directo transversal puede tomarse igual a la de una lámina no rigidizada. Con construcción "
            "corrugada, ésto es despreciable. "
            "F.5.5.3.1 — Láminas multi-rigidizadas sujetas a compresión uniforme — Se deben hacer dos revisiones, "
            "una por fluencia y otra como columna. La sección transversal debe clasificarse como compacta o "
            "esbelta de acuerdo con F.5.4.3.3, considerando todos los elementos componentes antes de llevar a cabo "
            "cada revisión. No se permiten elementos esbeltos salientes. "
            "(a) Revisión por fluencia — La sección completa debe ser revisada para aplastamiento local en la "
            "misma forma que se hace para miembros a compresión (véase F.5.4.7.6). La resistencia PRS se debe "
            "tomar con base en la sección transversal menos favorable considerando el pandeo local y el "
            "ablandamiento de la zona afectada por el calor, si es necesario, y también los agujeros no rellenos. "
            "(b) Revisión como columna — La lámina se trata como un ensamblaje de subunidades idénticas de "
            "columna, cada una conteniendo un rigidizador o una corrugación centralmente cargado y con un ancho "
            "igual a la separación w. La resistencia axial de diseño PRS se toma como: PRS = φ ps A  (F.5.5.3-1). "
            "Donde: ps = esfuerzo de pandeo para una sub-unidad de columna. A = área bruta de la sección "
            "transversal completa de la lámina. φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1). "
            "El esfuerzo ps debe leerse en la curva apropiada de la figura F.5.4.5-3, pertinente al pandeo como "
            "columna de la sub-unidad como un miembro a compresión simple, fuera del plano de la lámina. "
            "El parámetro de esbeltez λ, necesario para la figura F.5.4.5-3, se debe basar en una longitud "
            "efectiva l igual a la menor de: la distancia entre posiciones de soporte lateral efectivo tales como "
            "soportes en los extremos o rigidizadores transversales efectivos, o la mitad de la longitud de onda "
            "del pandeo elástico ortotrópico. "
            "La parte de la figura F.5.4.5-3 (a), (b) o (c) usada depende de la forma de la sección de la "
            "sub-unidad y de si ésta contiene soldadura longitudinal (véase la tabla F.5.4.7-3), la curva real es "
            "la que intercepta el eje de esfuerzos en un valor p1, como se define en F.5.4.7.5. Se debe considerar "
            "lo siguiente para determinar el área efectiva Ae (necesaria para encontrar p1): "
            "el valor de kL para elementos tales como los E de la figura F.5.5.1-2, debe basarse en sus "
            "dimensiones totales aunque estén cortados en dos por la formación de subunidades; el ablandamiento en "
            "la zona afectada por el calor debido a soldaduras en los extremos cargados o en rigidizadores "
            "transversales puede ignorarse para encontrar Ae."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_3_2", "seccion": "F.5.5.3.2",
        "titulo": "F.5.5.3.2 — Láminas multi-rigidizadas sujetas a momento en su plano: clasificación (a), fluencia (b), revisión como columna (c) con ecuación F.5.5.3-2",
        "texto": (
            "F.5.5.3.2 — Láminas multi-rigidizadas sujetas a momento en su plano — Se deben hacer dos revisiones: "
            "por fluencia y como columna. "
            "(a) Clasificación de la sección y pandeo local — Para realizar cada revisión, primero ha de "
            "clasificarse la sección como compacta o esbelta (véase F.5.4.3.3). "
            "Para el propósito de clasificar elementos individuales, y también para determinar kL para elementos "
            "esbeltos, generalmente se puede suponer que cada elemento está sometido a compresión uniforme "
            "tomando g=1 en el literal (a) de F.5.4.3.2. Sin embargo, en el caso de la revisión únicamente por "
            "fluencia, se permite basar g en el patrón de esfuerzos real en los elementos que conforman la región "
            "más extrema de la lámina y repetir ese valor para los elementos correspondientes más interiores. Esto "
            "puede ser favorable cuando el número de rigidizadores o corrugaciones es pequeño. No se deben "
            "permitir elementos esbeltos salientes. "
            "(b) Revisión por fluencia — La sección transversal completa de la lámina debe tratarse como una viga "
            "sujeta a flexión en su plano (véase el literal (b) de F.5.4.5.2). La resistencia a momento de diseño "
            "MRS debe tomarse con base en la sección transversal menos favorable, teniendo en cuenta el pandeo "
            "local y el ablandamiento en la zona afectada por el calor, si es necesario, y también los agujeros. "
            "(c) Revisión como columna — La lámina se considera como un ensamblaje de subunidades de columna en la "
            "misma manera que para compresión axial (véase el literal (b) de F.5.5.3.1), la resistencia a momento "
            "de diseño MRS se toma de acuerdo con: MRS = φ ps Z B / (2y)  (F.5.5.3-2). Donde: ps = esfuerzo de "
            "pandeo para una sub-unidad de columna. Z = módulo elástico de la sección transversal completa de la "
            "lámina para flexión en su plano. B = ancho total de la lámina. y = distancia desde el centro de la "
            "lámina hasta el centro del rigidizador más lejano. φ = coeficiente de reducción de capacidad (véase "
            "tabla F.5.3.3-1). "
            "El esfuerzo ps debe leerse en la figura F.5.4.5-3 del mismo modo que para compresión uniforme (véase "
            "el literal (b) de F.5.5.3.1)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_3_3", "seccion": "F.5.5.3.3",
        "titulo": "F.5.5.3.3 — Gradiente de esfuerzos longitudinal en láminas multi-rigidizadas: fluencia (a) vs. columna con x=0.4·longitud pandeo efectiva (b)",
        "texto": (
            "F.5.5.3.3 — Gradiente de esfuerzos longitudinal en láminas multi-rigidizadas — En este numeral se "
            "describen los casos en que la acción aplicada P o M sobre una lámina multi-rigidizada varía en la "
            "dirección de los rigidizadores o corrugaciones. "
            "(a) Revisión por fluencia — La resistencia de diseño en cualquier sección transversal no debe ser "
            "menor que la acción generada en esa sección bajo carga mayorada. "
            "(b) Revisión como columna — Para la revisión como columna es suficiente comparar la resistencia de "
            "diseño con la acción generada bajo carga mayorada a una distancia x del extremo más cargado de un "
            "panel, donde x es 0.4 veces la longitud de pandeo efectiva l."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_3_4_a_b", "seccion": "F.5.5.3.4",
        "titulo": "F.5.5.3.4 — Láminas multi-rigidizadas sometidas a cortante: 5 condiciones de aplicabilidad, revisión por fluencia (a) y pandeo (b, ecuación F.5.5.3-3)",
        "texto": (
            "F.5.5.3.4 — Láminas multi-rigidizadas sometidas a cortante — Se debe hacer una revisión por fluencia y "
            "una revisión por pandeo. Los métodos dados en los literales (a) y (b) de este numeral son válidos "
            "siempre y cuando ocurra lo siguiente: "
            "el espaciamiento w de los rigidizadores o corrugaciones no debe exceder 0.3L (véase la figura "
            "F.5.5.1-2); cualquier elemento saliente de la sección se clasifica como compacto en términos de "
            "resistencia axial (véase el literal (c) de F.5.4.3.3); cualquier elemento interno se clasifica como "
            "compacto en términos de resistencia al cortante (véase el literal (a) de F.5.4.5.3); los "
            "rigidizadores o corrugaciones, lo mismo que la lámina completa, están: (1) efectivamente conectados al "
            "entramado transversal en cada extremo; (2) continuos en cualquier posición de rigidizador "
            "transversal. "
            "(a) Revisión por fluencia — La resistencia a fuerza cortante de diseño VRS se toma igual a la de una "
            "lámina plana no rigidizada con el mismo aspecto general (LxB) y el mismo espesor general t. Se "
            "encuentra de acuerdo con el literal (a) de F.5.5.2.4. "
            "(b) Revisión por pandeo — La resistencia de diseño a fuerza cortante se encuentra usando la siguiente "
            "expresión: VRS = φ v1 pv B t  (F.5.5.3-3). Donde: pv = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2). B = ancho de la lámina (véase la figura F.5.5.1-2). t = espesor general de la lámina. "
            "φ = coeficiente de reducción de capacidad (véase la tabla F.5.3.3-1). v1 = coeficiente de pandeo "
            "crítico al corte en el rango elástico (véase la figura F.5.5.3-1)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_3_4_figura", "seccion": "F.5.5.3-1",
        "titulo": "Figura F.5.5.3-1 — Coeficiente de pandeo crítico al corte v1 (curva gráfica por a/d, NO transcrita) + fórmulas para calcular v1 (ecuación F.5.5.3-4)",
        "texto": (
            "Figura F.5.5.3-1 — Coeficiente de pandeo crítico al corte en el rango elástico, v1: curva de "
            "interpolación gráfica (eje vertical v1 de 0 a 1.0, eje horizontal d/te de 0 a más de 280, familia de "
            "curvas paramétricas por relación a/d de 0.50 a 2.5). Nota del original: para paneles rigidizados "
            "longitudinalmente, d debe tomarse como la altura del mayor subpanel. Es una lectura gráfica sin "
            "ecuación cerrada — no se transcriben valores numéricos de la curva, deben leerse directamente del PDF "
            "original (página F-511). "
            "Para calcular v1 deben usarse los siguientes valores: a = B. d = 0.61 (w t³ / ISU)^0.375  "
            "(F.5.5.3-4). Donde: l = longitud efectiva de la lámina. w = separación entre rigidizadores o "
            "corrugaciones. ISU = segundo momento del área de una sub-unidad de lámina (como se define en el "
            "literal (b) de F.5.5.3.1) respecto al eje centroidal paralelo al plano de la lámina. "
            "ε = (15/pv)^(1/2). "
            "La longitud efectiva l puede tomarse seguramente como la longitud no soportada L (véase la figura "
            "F.5.5.1-2). Cuando L excede ampliamente a B, se puede obtener un resultado más favorable haciendo l "
            "igual a la mitad de la longitud de onda del pandeo por cortante elástico ortotrópico. En la revisión "
            "por pandeo no es necesario tener en cuenta el ablandamiento en la zona afectada por el calor."
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
