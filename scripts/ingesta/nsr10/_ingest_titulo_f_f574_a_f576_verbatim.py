"""
Ingesta verbatim de NSR-10 Título F.5.7.4 completo (Carga de Fatiga),
F.5.7.5 completo (Esfuerzos: derivación y parámetros) y F.5.7.6 completo
(Derivación de los Espectros de Esfuerzos: conteo de ciclos y derivación
del espectro) -- Estructuras de Aluminio. Fase 12 del plan de cierre de
Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-544 a F-547), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.7.6-1, F.5.7.6-2, F.5.7.6-3 y
F.5.7.6-4 son diagramas de distribución de esfuerzos en soldaduras y
uniones -- se transcriben verbatim las fórmulas y notas textuales que
las acompañan (ej. flujo máximo de cortante Md/I0), no la geometría
gráfica.

Uso: python _ingest_titulo_f_f574_a_f576_verbatim.py
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
        "id": "NSR10-F-F_5_7_4", "seccion": "F.5.7.4",
        "titulo": "F.5.7.4 — Carga de fatiga: 4 fuentes (a-d), espectro de carga de diseño, límite de confianza = media - 2 desviaciones estándar",
        "texto": (
            "F.5.7.4 — CARGA DE FATIGA — Todas las fuentes de esfuerzo fluctuante en la estructura deben ser "
            "identificadas: "
            "(a) Cargas móviles superpuestas, incluyendo vibraciones de maquinaria en estructuras estacionarias. "
            "(b) Cargas ambientales tales como viento, olas, etc. "
            "(c) Fuerzas de aceleración en estructuras móviles. "
            "(d) Cambios de temperatura. "
            "La carga para fatiga normalmente se describe en términos de un espectro de carga de diseño que "
            "define un rango de intensidades de un evento de carga viva específico y el número de veces que cada "
            "nivel de intensidad es aplicado durante la vida de diseño de la estructura. Si dos o más eventos de "
            "carga viva independientes son de probable ocurrencia entonces será necesario especificar el desfase "
            "entre ellos. "
            "Una guía sobre la carga específica para el estimativo de la fatiga se puede obtener en normas "
            "expedidas por entidades de reconocida autoridad. "
            "Un estimativo realista de la carga de fatiga es crucial para el cálculo de la vida de la estructura. "
            "Cuando no hayan datos publicados sobre la carga viva, hay que recurrir a obtener datos de estructuras "
            "existentes sujetas a efectos similares. Registrando la deformación continua o midiendo la deflexión "
            "durante un período apropiado de tiempo, se pueden inferir los datos de carga mediante el análisis "
            "subsecuente de la respuesta. Se debe dar especial atención a determinar los efectos de magnificación "
            "dinámica cuando las frecuencias de carga son cercanas a una de las frecuencias naturales de la "
            "estructura (véase F.5.8.4.2). "
            "El espectro de carga de diseño debe seleccionarse teniendo en cuenta que es un estimativo del límite "
            "superior de las condiciones de servicio acumuladas sobre la vida de diseño completa de la estructura. "
            "Se deben considerar todos los efectos ambientales y operacionales generados por el uso previsto de "
            "la estructura durante ese período. El límite de confianza del espectro de carga de diseño debe "
            "basarse en la media menos 2 límites de desviación estándar tanto para amplitud como para frecuencia."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_5_1_2", "seccion": "F.5.7.5.1",
        "titulo": "F.5.7.5 — Esfuerzos. F.5.7.5.1 — Derivación de esfuerzos: teoría elástica, sin redistribución plástica. F.5.7.5.2 — Parámetros de esfuerzo (intro)",
        "texto": (
            "F.5.7.5 — ESFUERZOS. "
            "F.5.7.5.1 — Derivación de esfuerzos — Se debe usar la teoría elástica para modelar la estructura "
            "cuando se desea calcular la respuesta de esfuerzo a partir de eventos de carga específicos. Las "
            "propiedades de la sección no se deben reducir por efectos de la zona afectada por el calor o de "
            "pandeo local (pero véase F.5.7.5.2 (a) (4)). La modelación de la rigidez elástica de miembros y "
            "uniones debe ser exacta e incluir los efectos de cualquier material no estructural permanente que "
            "pueda modificarla. No se debe permitir la redistribución plástica de esfuerzos. "
            "Cuando los datos de respuesta de esfuerzo van a ser obtenidos por medidas de deformación de una "
            "estructura similar, se debe poner cuidado especial para situar los transductores de deformación "
            "para asegurar que el parámetro de esfuerzo correcto está siendo medido (véase F.5.7.5.2). En F.5.8.4 "
            "se amplía la información sobre medida de datos de deformación. "
            "F.5.7.5.2 — Parámetros de esfuerzo — El esfuerzo a usar en los procedimientos de estimar la fatiga "
            "en F.5.7.3 depende del sitio de iniciación de la grieta y del camino de propagación, así:"
        ),
    },
    {
        "id": "NSR10-F-F_5_7_5_2_a", "seccion": "F.5.7.5.2(a)",
        "titulo": "F.5.7.5.2(a) — Material base y soldaduras a tope de penetración total: efectos geométricos mayores no lineales (6 casos 1-6), esfuerzos residuales",
        "texto": (
            "(a) Material base y soldaduras a tope de penetración total — Las grietas se inician en la "
            "intersección de la soldadura con el metal base, en los agujeros para los sujetadores, en las "
            "superficies de empalme o traslapo, etc. y se propagan a través del material base o del metal "
            "completamente penetrado de la soldadura y deben ser evaluadas usando el rango nominal de esfuerzo "
            "principal en el miembro en ese punto. "
            "Los efectos de concentración local de esfuerzos del perfil de soldadura, de los agujeros de "
            "remaches y tornillos, etc. deben ignorarse ya que ellos son tomados en cuenta en los datos de "
            "resistencia fr-N para la clase de detalle apropiada y por lo tanto no necesitan ser calculados "
            "(véanse las tablas F.5.7.2-1 a F.5.7.2-3). Si se utilizan modelos detallados con elementos finitos "
            "de las uniones, la malla no debe ser más fina que los esfuerzos locales usados (véase también el "
            "literal (a) de F.5.8.4.4). "
            "Se deben tomar en cuenta otros efectos geométricos mayores que pueden generar distribuciones no "
            "lineales de esfuerzos en ciertas circunstancias (véase la figura F.5.7.2). Esta situación se "
            "presenta en: "
            "(1) Cambios bruscos en la forma de la sección transversal, por ejemplo en destijeres. "
            "(2) Cambios bruscos en la rigidez de la sección transversal, por ejemplo en uniones a ángulo entre "
            "miembros de pared delgada. "
            "(3) Cambios en dirección o alineamiento más allá de lo permitido en las tablas F.5.7.2-1 a "
            "F.5.7.3-2. "
            "(4) Esfuerzos de flexión secundarios generados por la rigidez de uniones en estructuras en celosía. "
            "(5) Ineficiencia de transmisión de esfuerzos por cortante, distorsión y alabeo en miembros anchos "
            "formados con láminas y miembros huecos. "
            "(6) Efectos de flexión no lineal fuera del plano en componentes esbeltos tales como láminas planas "
            "donde el esfuerzo estático es cercano al esfuerzo crítico elástico, por ejemplo el campo tensionado "
            "en almas. "
            "La presencia de esfuerzos residuales en uniones soldadas puede ignorarse ya que éstos están ya "
            "incluidos en los datos fr-N. En uniones mecánicas, siempre que cualquier esfuerzo residual de "
            "tensión sea tenido en cuenta, esa parte del rango de esfuerzos que está en compresión general puede "
            "reducirse un 40%."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_5_2_b_c", "seccion": "F.5.7.5.2(b)",
        "titulo": "F.5.7.5.2(b) — Soldaduras de filete y a tope de penetración parcial: raíz de soldadura, garganta efectiva. F.5.7.5.2(c) — Sujetadores roscados a carga axial: raíz de rosca",
        "texto": (
            "(b) Soldaduras de filete y a tope de penetración parcial — Las grietas se inician en la raíz de la "
            "soldadura y se propagan a través de la garganta. Deben ser estimadas usando la suma vectorial de "
            "los esfuerzos de corte en el metal de aporte de la soldadura basándose en la dimensión de garganta "
            "efectiva (véase la figura F.5.7.6-2). "
            "En uniones traslapadas en un plano, el esfuerzo por unidad de longitud de soldadura puede calcularse "
            "con base en el área promedio para fuerzas axiales y un módulo elástico polar del grupo de "
            "soldaduras para momentos en el plano (véase la figura F.5.7.6-3). "
            "En uniones en T, cualquier efecto de rigidez axial diferente a lo largo de la unión debe ser "
            "considerado. "
            "Cuando filetes simples o soldaduras a tope de penetración incompleta están sujetos a momentos de "
            "flexión fuera de su plano, los esfuerzos en la raíz deben calcularse usando una distribución lineal "
            "de esfuerzos a través de la garganta (véase la figura F.5.7.6-4). "
            "No se puede permitir el contacto de apoyo sobre la cara de la raíz en uniones soldadas con "
            "penetración parcial. "
            "(c) Sujetadores roscados bajo carga axial — Las grietas se inician en las raíces de las roscas y "
            "deben ser evaluadas usando el esfuerzo medio axial en el área del núcleo de la rosca. Cuando hay "
            "también presencia de flexión, se debe usar el esfuerzo pico calculado sobre el módulo elástico del "
            "núcleo."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_6_1_2", "seccion": "F.5.7.6",
        "titulo": "F.5.7.6 — Derivación de los espectros de esfuerzos: conteo de ciclos por método del embalse/escorrentía (.6.1), derivación del espectro por bandas (.6.2), Figuras 6-1 a 6-4",
        "texto": (
            "F.5.7.6 — DERIVACION DE LOS ESPECTROS DE ESFUERZOS. "
            "F.5.7.6.1 — Conteo de ciclos — El conteo de ciclos es un procedimiento para convertir una historia "
            "de esfuerzo compleja en un espectro de ciclos conveniente en términos de amplitud fr y frecuencia n "
            "(véase la figura F.5.7.2-1). Hay varios métodos en uso, para historias de esfuerzo cortas en las que "
            "eventos simples de carga se repiten varias veces se recomienda el método del embalse que es simple "
            "de visualizar y simple de usar (véase la figura F.5.7.7-1). Cuando se tienen que usar historias de "
            "esfuerzo largas, tales como las obtenidas con las deformaciones medidas en estructuras reales (véase "
            "F.5.8.4), se recomienda el método de la escorrentía. Ambos métodos son apropiados para el análisis "
            "con computador. "
            "F.5.7.6.2 — Derivación del espectro de esfuerzos — El listado de los ciclos en orden descendente de "
            "amplitud fr da como resultado el espectro de esfuerzos. Por facilidad de cálculo puede ser necesario "
            "simplificar el espectro con una menor cantidad de bandas; un método conservador consiste en agrupar "
            "las bandas en grupos mayores que contienen el mismo número total de ciclos pero cuya amplitud es "
            "igual a la de la mayor banda en el grupo. Con mayor exactitud, puede calcularse el promedio "
            "ponderado de todas las bandas en un grupo usando la potencia m, donde m es la pendiente inversa de "
            "la curva fr-N más apropiada (véase la figura F.5.7.7-2). El uso del valor de la media aritmética "
            "siempre da resultados no conservadores. "
            "Figura F.5.7.6-1 — Parámetro de esfuerzos para el material parenteral: (a) concentrador de esfuerzo "
            "local en una conexión con rango de esfuerzos de diseño fr = (P+M)/(A/Z), sitio de iniciación de la "
            "grieta, distribución lineal de esfuerzos supuesta; (b) concentrador de gran esfuerzo (abertura "
            "grande), mostrando esfuerzo medio neto fr, distribución no lineal de esfuerzos, esfuerzo de diseño "
            "en el sitio de iniciación X, accesorio soldado, abertura grande o esquina entrante. Diagrama "
            "explicativo, no se transcribe la geometría gráfica. "
            "Figura F.5.7.6-2 — Esfuerzos en gargantas de soldadura: geometría de filete con Pw y Hw (esfuerzos "
            "por unidad de longitud), y diagrama vectorial del esfuerzo resultante fp = combinación de Pw/2gt y "
            "Hw/2gt. Diagrama explicativo, no se transcribe la geometría gráfica. "
            "Figura F.5.7.6-3 — Esfuerzos en uniones traslapadas: distribución de esfuerzos debido a carga "
            "directa P y debida al momento M sobre un filete con área traslapada. Nota: flujo máximo de cortante "
            "a lo largo de las soldaduras = Md/I0, donde I0 = segundo momento polar del área respecto al "
            "centroide del grupo de soldaduras, d = distancia máxima al centroide de un punto dentro del grupo de "
            "soldaduras. "
            "Figura F.5.7.6-4 — Esfuerzos en la raíz de un filete: geometría de una unión en T con filete "
            "sometido a momento M, mostrando la distribución triangular de esfuerzos en la raíz de la soldadura. "
            "Diagrama explicativo, no se transcribe la geometría gráfica."
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
