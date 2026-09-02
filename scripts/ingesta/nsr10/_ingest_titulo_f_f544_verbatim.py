"""
Ingesta verbatim de NSR-10 Titulo F.5.4.4 (Estructuras de Aluminio --
Ablandamiento en la Zona Afectada por el Calor Adyacente a la Soldadura).

Fuente: NSR-10-1083-1182.pdf (paginas internas F-472 a F-476), ya
descargado localmente en scripts/ingesta/nsr10/raw/ (gitignored).
Texto transcrito verbatim leyendo el PDF nativo pagina por pagina
(nunca el texto plano exportado, corrompe subindices/formulas).

Sistema de unidades: kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Uso: python _ingest_titulo_f_f544_verbatim.py
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
        "id": "NSR10-F-F_5_4_4_1_generalidades",
        "seccion": "F.5.4.4.1 — Generalidades",
        "titulo": "F.5.4.4 Ablandamiento en la Zona Afectada por el Calor",
        "texto": (
            "F.5.4.4 — ABLANDAMIENTO EN LA ZONA AFECTADA POR EL CALOR "
            "ADYACENTE A LA SOLDADURA\n\n"
            "F.5.4.4.1 — Generalidades — Es necesario considerar en el "
            "diseño el ablandamiento que usualmente se presenta en la "
            "vecindad de las soldaduras. La región más afectada se "
            "localiza inmediatamente alrededor de la soldadura, sin "
            "embargo, las propiedades del material mejoran rápidamente "
            "con la distancia hasta tener las del material original. El "
            "ablandamiento afecta más severamente el esfuerzo de prueba "
            "del 0.2% que la resistencia a tensión.\n\n"
            "Para el diseño es aceptable aproximarse a la condición "
            "real suponiendo que alrededor de cada soldadura existe una "
            "zona afectada por el calor en la que las propiedades de "
            "resistencia están reducidas por un coeficiente constante "
            "kz.\n\n"
            "Por fuera de esta zona, se supone que se pueden aplicar "
            "todas las propiedades originales del material base. La "
            "severidad del ablandamiento en la zona afectada por el "
            "calor, definida por kz, se trata en F.5.4.4.2. La "
            "extensión del ablandamiento de la zona afectada por el "
            "calor, definida por una distancia z, medida desde la "
            "soldadura, se considera en F.5.4.4.3.\n\n"
            "Algunas veces es posible mitigar el efecto del "
            "ablandamiento de la zona afectada por el calor mediante un "
            "tratamiento de envejecimiento artificial aplicado después "
            "de soldar (véase el apéndice F.5.E)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_2_severidad_ablandamiento_kz",
        "seccion": "F.5.4.4.2 — Severidad del ablandamiento, coeficiente kz",
        "titulo": "F.5.4.4.2 Coeficiente kz, material 7020, tiempo de recuperación series 6/7",
        "texto": (
            "F.5.4.4.2 — Severidad del ablandamiento\n\n"
            "(a) Coeficiente de ablandamiento de la zona afectada por "
            "el calor — El coeficiente kz normalmente debe tomarse de "
            "la tabla F.5.4.4-1 pero para ciertos cálculos se permite "
            "usar un valor más favorable, como se explica en el "
            "apéndice F.5.E. Esto se aplica cuando la resistencia de un "
            "miembro está gobernada por pa o pv en lugar de por po. "
            "Para encontrar el coeficiente kz para materiales no "
            "cubiertos en la tabla F.5.4.4-1, véase el apéndice F.5.E.\n\n"
            "(b) Material 7020 — Los valores alternativos de kz dados "
            "en la tabla F.5.4.4-1 para el material 7020 deben ser "
            "normalmente aplicados de acuerdo con la naturaleza del "
            "esfuerzo actuante sobre el material de la zona afectada "
            "por el calor:\n\n"
            "• valor (A) — esfuerzo de tensión actuando "
            "transversalmente al eje de una soldadura a tope o de "
            "filete\n"
            "• valor (B) — cualquier otra condición de esfuerzo, esto "
            "es, esfuerzo longitudinal, compresión transversal, "
            "cortante.\n\n"
            "Algunas veces es posible incrementar el valor (A) a una "
            "cifra superior a la de la tabla dependiendo del grado de "
            "control térmico logrado en la fabricación (véase el "
            "apéndice F.5.E).\n\n"
            "(c) Tiempo de recuperación para aleaciones tratadas en "
            "caliente — Los valores de kz dados en la tabla F.5.4.4-1 "
            "son válidos a partir de los siguientes tiempos después de "
            "soldar, siempre y cuando el material se haya mantenido a "
            "una temperatura no menor de 15°C:\n\n"
            "• Aleaciones de la serie 6*** — 3 días\n"
            "• Aleaciones de la serie 7*** — 30 días\n\n"
            "Para determinar la resistencia de los componentes que "
            "deben ser cargados más tempranamente, pero nunca antes de "
            "24 horas después de soldar, el valor de kz debe reducirse "
            "por un coeficiente f calculado de acuerdo con lo "
            "siguiente:\n\n"
            "• Aleaciones de la serie 6*** — f = 0.9 + 0.1[(n-1)/2]^(1/2) "
            "(F.5.4.4-1)\n"
            "• Aleaciones de la serie 7*** — f = 0.8 + 0.2[(n-1)/29]^(1/2) "
            "(F.5.4.4-2)\n\n"
            "donde n es el tiempo, en días, entre la soldadura y la "
            "carga.\n\n"
            "Si el material se mantiene a una temperatura por debajo de "
            "15°C después de haber soldado, el tiempo de recuperación "
            "se prolongará y esto debe ser advertido."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_tabla1_coeficiente_ablandamiento_kz",
        "seccion": "Tabla F.5.4.4-1 (Coeficiente de ablandamiento de la zona afectada por el calor, kz)",
        "titulo": "No tratadas en caliente: kz 0.13-1.00. Tratadas: 6061-6082 kz 0.35-1.00, 7020 kz 0.60-1.00(B) según valor A/B",
        "texto": (
            "Tabla F.5.4.4-1 — Coeficiente de ablandamiento de la zona "
            "afectada por el calor, kz (Aleación, Condición, Producto — "
            "nota 1: E=extrusión, S=lámina, P=plancha, DT=tubería "
            "extruída, WT=tubería soldada, F=forjados — kz).\n\n"
            "No tratadas en caliente:\n"
            "1200 — H14, S: 0.13.\n"
            "3103 — H14, S: 0.18. H18, S: 0.13.\n"
            "3105 — H14, S: 0.17. H16, S: 0.15. H18, S: 0.13.\n"
            "5083 — O/F, E/S/P/DT: 1.00. H22, S/P: 0.45.\n"
            "5154A — O/F, E/S/P: 1.00. H22, S/P: 0.40. H24, S/P: 0.29.\n"
            "5251 — F, WT: 0.20. F, F: 1.00. H22, S/P: 0.35. H24, S/P: "
            "0.24.\n"
            "5454 — O/F, E/S/P: 1.00. H22, S: 0.35. H24, S: 0.30.\n\n"
            "Tratadas en caliente:\n"
            "6061 — T6, E/DT: 0.50.\n"
            "6063 — T4, E: 1.00. T4, DT: 0.65. T4, F: 0.80. T5, E: "
            "0.75. T6, E/F: 0.50. T6, DT: 0.45.\n"
            "6082 — T4, E/S/P/DT/F: 1.00. T6, E/S/P/DT/F: 0.50.\n"
            "7020 — T4, E/S/P: 0.80(A) / 1.00(B). T6, E/S/P: 0.60(A) / "
            "0.80(B) (nota 2).\n\n"
            "NOTA 1. En la columna de producto, E, S, P, DT, WT y F se "
            "refieren, respectivamente, a extrusión, lámina, plancha, "
            "tubería extruída, tubería soldada y forjados.\n"
            "NOTA 2. Refiérase al literal (b) de F.5.4.4.2 para ver la "
            "aplicabilidad de los valores A y B para material 7020."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_3_a_definicion_extension_z",
        "seccion": "F.5.4.4.3(a) — Definición de la extensión z de la zona afectada por el calor",
        "titulo": "z se extiende transversal/radialmente desde la soldadura, casos (1)-(4)",
        "texto": (
            "F.5.4.4.3 — Extensión de la zona afectada por el calor\n\n"
            "(a) Definición de z — Se supone que la zona afectada por "
            "el calor se extiende una distancia z en cualquier "
            "dirección a partir de la soldadura, medida de acuerdo con "
            "lo siguiente:\n\n"
            "(1) Transversalmente desde la línea central de una "
            "soldadura a tope en línea (véase la figura F.5.4.4-1(a))\n"
            "(2) En soldaduras de filete, transversalmente desde el "
            "punto de intersección de las superficies soldadas (véanse "
            "las figuras F.5.4.4-1(e), (f), (g) y (h))\n"
            "(3) En soldaduras a tope usadas en uniones de esquina, T o "
            "cruciformes, transversalmente desde el punto de "
            "intersección de las superficies soldadas (véanse las "
            "figuras F.5.4.4-1(b), (c) y (d))\n"
            "(4) En cualquier dirección radial desde el extremo de una "
            "soldadura (véanse las figuras F.5.4.4-1(i) y (j))\n\n"
            "Las fronteras de la zona afectada por el calor generalmente "
            "deben ser tomadas como líneas rectas normales a la "
            "superficie del metal, como se muestra en la figura "
            "F.5.4.4-1. Sin embargo, se permite, en su lugar, suponer "
            "una frontera curva de radio z, como se muestra en B (en "
            "lugar de A) en la figura F.5.4.4-1(i). Esto es ventajoso "
            "cuando la soldadura de superficie se aplica a un material "
            "grueso."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_figura1_tabla1b_extension_alfa",
        "seccion": "Figura F.5.4.4-1(a) + Tabla F.5.4.4-1b (coeficiente α)",
        "titulo": "10 configuraciones (a)-(j) de ubicación de z; α=1.0-2.0 según área de depósito y espesor tc",
        "texto": (
            "Figura F.5.4.4-1(a) — Extensión de la zona afectada por "
            "el calor, ubicación de z: 10 configuraciones de unión "
            "soldada (a) a (j) mostrando la medición de z desde la "
            "línea/punto de soldadura — (a) soldadura a tope en línea "
            "recta, (b)(c)(d) uniones de esquina/T/cruciformes, "
            "(e)(f)(g)(h) soldaduras de filete, (i) frontera recta A "
            "vs. curva de radio z opción B, (j) soldadura de "
            "superficie sobre material grueso.\n\n"
            "Tabla F.5.4.4-1b — Extensión de la zona afectada por el "
            "calor, coeficiente α (Caso, Configuración de la unión, "
            "Valor de α para tc≤25mm / tc>25mm):\n\n"
            "P — Soldadura continua substancialmente recta (véanse "
            "figuras F.7.4.6(a),(c),(e),(g)), área total del depósito "
            "menor o igual que 50 mm²: α=1.0 / 1.5.\n"
            "Q — igual configuración, área total del depósito mayor "
            "que 50 mm²: α=1.5 / 2.0.\n"
            "R — Soldadura continua substancialmente recta que tiene "
            "dos o más soldaduras adyacentes (véanse figuras "
            "F.7.4.6(b),(d),(f),(h)): α=1.5 / 2.0.\n"
            "S — Unión con irregularidad local: (a) uniones "
            "miembro-a-miembro en armaduras, (b) soldaduras que "
            "conectan rigidizadores transversales en vigas y vigas "
            "ensambladas, (c) soldaduras usadas para conectar orejas y "
            "otros accesorios: α=1.5 / 2.0.\n\n"
            "(b) Fórmula básica para z — La siguiente expresión general "
            "debe ser usada para estimar el valor de z."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_3_b_c_formula_z_zo",
        "seccion": "F.5.4.4.3(b)(c) — Fórmula básica z=αηzo, determinación de zo",
        "titulo": "z=αηzo (F.5.4.4-b); zo por soldadura a tope o de filete, series 6/7 vs otras",
        "texto": (
            "z = αηzo\n\n"
            "Donde:\n"
            "zo = es el valor básico calculado en (c).\n"
            "α y η = factores de modificación, son determinados en (d) "
            "y (e) o puede referirse al apéndice F.5.E.\n\n"
            "(c) Determinación de zo — El valor básico de zo, el cual "
            "es la relación entre la soldadura depositada en el "
            "material no calienta con la interfase completamente "
            "enfriada, debe tomarse el menor valor de los dos "
            "calculados en i) y ii)\n\n"
            "Para soldadura a tope:\n"
            "para aleaciones de la serie 7*** — (i) zo = 30 - tA/2, "
            "(ii) zo = 4.5tA\n"
            "para otras aleaciones — (i) zo = 20 - tA/3, (ii) zo = "
            "3.0tA\n\n"
            "Para otro tipo de soldadura incluyendo las variaciones de "
            "soldadura de filete:\n"
            "para aleaciones de la serie 7*** — (i) zo = 30 - tA/2, "
            "(ii) zo = 4.5(tB^2)/tA\n"
            "para otras aleaciones — (i) zo = 20 + tA/3, (ii) zo = "
            "3.0(tB^2)tA\n\n"
            "Donde:\n"
            "tA = es el menor valor de 0.5(tB + tC) y 1.5tB\n"
            "tB, tC = son los espesores de los elementos a conectar por "
            "medio de la soldadura, tC es el espesor del elemento mas "
            "grueso a unir."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_3_d_e_alfa_eta_camino_calor",
        "seccion": "F.5.4.4.3(d)(e) — Determinación de α y η, caminos de calor",
        "titulo": "α de tabla F.5.4.4-2; η=1 con 2+ caminos de calor válidos, h≤h1",
        "texto": (
            "(d) Determinación de α — el factor α debe ser tomado de "
            "la tabla F.5.4.4-2, o alternativamente de acuerdo al "
            "apéndice F.5.E. De acuerdo a (c), este numeral suministra "
            "la posibilidad de que en el material empiece la "
            "deposición de la soldadura debido a una elevada "
            "temperatura, debido a otro precalentamiento o a la "
            "depositación previa en la junta o de la soldadura en la "
            "misma junta.\n\n"
            "(e) Determinación de η — El coeficiente η en el literal "
            "(b) de F.5.4.4.3 cubre la posibilidad de acumulación "
            "incremental de calor debida a:\n\n"
            "• proximidad de un borde o de bordes libres; o\n"
            "• otra soldadura en la vecindad.\n\n"
            "El valor de η puede encontrarse como se indica a "
            "continuación en (1) o en (2). Alternativamente refiérase "
            "al apéndice F.5.E.\n\n"
            "(1) Para una unión desde la cual existen al menos dos "
            "caminos de calor válidos:\n\n"
            "η = 1\n\n"
            "Un camino de calor válido es aquel en el que h ≤ h1; "
            "donde h = distancia al borde libre o la mitad de la "
            "distancia a una soldadura cercana"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_4_3_e_continuacion_f_g_traslapo_experimental",
        "seccion": "F.5.4.4.3(e) continuación, (f)(g) — Traslapo de zonas, determinación experimental de z",
        "titulo": "h1=4.5αzo (serie 7) o 3αzo (otras); η=1.50/1.33 según tc; traslapo, ensayo de dureza",
        "texto": (
            "La distancia h debe ser medida desde el punto de "
            "referencia en la soldadura considerado (véase la figura "
            "F.5.4.4-1) y a lo largo del camino de calor relevante a "
            "través del metal en la mitad del espesor. El camino de "
            "calor sigue el perfil de la sección y no tiene que ser "
            "necesariamente recto (véase la figura F.5.4.4-2).\n\n"
            "Figura F.5.4.4-2 — Medición típica del camino de calor: "
            "sección soldada tipo Y invertida (dos aletas inclinadas + "
            "alma vertical), con h medido a lo largo del perfil de la "
            "sección en la mitad del espesor desde el punto de "
            "referencia de la soldadura.\n\n"
            "h1 = 4.5αzo — para aleaciones de la serie 7*** (F.5.4.4-3)\n"
            "h1 = 3αzo — para otras aleaciones (F.5.4.4-4)\n\n"
            "(2) Para una unión desde la cual hay únicamente un camino "
            "de calor válido:\n"
            "tc ≤ 25 mm → η = 1.50\n"
            "tc > 25 mm → η = 1.33\n\n"
            "(f) Traslapo de zonas afectadas por el calor — Cuando dos "
            "uniones se localizan de modo que sus zonas afectadas por "
            "el calor respectivo (determinadas de acuerdo con "
            "F.5.4.4.3) se traslapan, se puede suponer que la "
            "extensión de la zona afectada por el calor en el lado "
            "exterior de cada unión no se altera por la proximidad.\n\n"
            "(g) Determinación experimental de z — Es una alternativa "
            "para estimar la extensión de la zona afectada por el "
            "calor en lugar de hacerlo mediante cálculo. Esto se puede "
            "hacer por medio del examen de dureza de un espécimen "
            "representativo (véase el apéndice F.5.E)."
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

    print(f"\nOK: {len(rows)} chunks de F.5.4.4 cargados.")
    max_len = max(len(c["texto"]) for c in CHUNKS)
    print(f"Chunk más largo: {max_len} caracteres.")


if __name__ == "__main__":
    main()
