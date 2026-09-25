"""
Ingesta verbatim de NSR-10 Título F.5.6.7 completo (Uniones Soldadas --
Estructuras de Aluminio: tipos de unión, resistencia estática/fatiga,
corrosión, preparación de bordes, distorsión, información al fabricante,
soldaduras a tope y de filete) y F.5.6.8 completo (Resistencia de Diseño
de Uniones Soldadas: grupos de soldaduras, esfuerzo límite del metal de
aporte con Tabla F.5.6.8-1, esfuerzo límite en la zona afectada por el
calor con Tabla F.5.6.8-2). Fase 8 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-526 a F-530), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.6.7-1, F.5.6.7-2 y F.5.6.7-3
son diagramas de geometría de soldadura (garganta efectiva, planos de
falla) -- se transcriben verbatim las definiciones textuales de sus
variables y convenciones (gr, gt, Pt, W/F/T), no la geometría gráfica en
sí.

Uso: python _ingest_titulo_f_f567_f568_verbatim.py
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

TABLA_F_5_6_8_1 = (
    "Tabla F.5.6.8-1 — Esfuerzos límite del metal de aporte pw (kgf/mm²), por material base. "
    "Aleaciones no tratadas en caliente: 1200 → 5.5; 3103/3105 → 8.0; 5251 → 20.0; 5454 → 19.0; 5154A → 21.0; "
    "5083 → 24.5. Aleaciones tratadas en caliente: 6063 → 15.0; 6061/6082 → 19.0; 7020 → 25.5. "
    "Nota: cuando se usan materiales base disímiles, se debe tomar el menor de los esfuerzos límite para el "
    "material de aporte. Si la soldadura se hace con materiales base no incluidos en la tabla F.5.6.8-1 o en el "
    "apéndice F.5.C, el valor del esfuerzo límite del material de aporte se debe obtener experimentalmente."
)

TABLA_F_5_6_8_2 = (
    "Tabla F.5.6.8-2 — Esfuerzos límite paz y pvz en la zona afectada por el calor (kgf/mm²), paz=esfuerzo límite "
    "directo, pvz=esfuerzo límite de cortante. "
    "Aleaciones no tratadas en caliente (nota 1): 1200 → paz=2.5, pvz=1.5; 3103 → paz=3.5, pvz=2.0; "
    "3015 → paz=4.0, pvz=2.5; 5083 → paz=15.0, pvz=9.0; 5154A → paz=10.0, pvz=6.0; 5251 → paz=7.0, pvz=4.0; "
    "5454 → paz=9.5, pvz=5.5. "
    "Aleaciones tratadas en caliente: 6061 condición T6 → paz=14.5, pvz=8.5; 6063 T4 → paz=8.5, pvz=5.0; "
    "6063 T5 → paz=9.5, pvz=5.5; 6063 T6 → paz=9.5, pvz=5.5; 6082 T4 → paz=14.0, pvz=8.5; 6082 T6 → paz=15.0, "
    "pvz=9.0; 7020 T4 → paz=17.0(A)/18.0(B), pvz=10.0; 7020 T6 → paz=21.0(A)/24.0(B), pvz=12.5/14.5 (nota 2). "
    "Nota 1: se suministran todas las condiciones (véase la tabla F.5.4.4-1). Nota 2: refiérase al literal (b) de "
    "F.5.4.4.2 para ver la aplicabilidad de los valores A y B para el material 7020."
)

CHUNKS = [
    {
        "id": "NSR10-F-F_5_6_7_1_a_3", "seccion": "F.5.6.7",
        "titulo": "F.5.6.7 — Uniones Soldadas: guía MIG/TIG, criterios de selección de unión (a-f). F.5.6.7.1 — Efecto en resistencia estática. F.5.6.7.2 — Efecto en fatiga. F.5.6.7.3 — Corrosión",
        "texto": (
            "F.5.6.7 — UNIONES SOLDADAS — La guía de diseño dada aquí se aplica únicamente a soldaduras hechas "
            "usando las combinaciones recomendadas de material base y de aporte dadas en la tabla F.5.2.8. "
            "Las guías de diseño dadas aquí se aplicarán a procesos de soldadura MIG para todos los espesores y el "
            "TIG solo para espesores de material hasta t=6.0 mm y para reparación. "
            "La versatilidad de la soldadura permite que las uniones entre miembros se hagan en formas diferentes. "
            "Para seleccionar el tipo de unión a usar, el diseñador debe considerar lo siguiente: "
            "(a) El efecto de la unión sobre la resistencia estática del miembro (véase F.5.4.4). "
            "(b) El efecto de la unión sobre la resistencia a la fatiga del miembro (véase F.5.7). "
            "(c) La reducción de la concentración de esfuerzos mediante una apropiada selección de detalles. "
            "(d) La selección del detalle que permita que se hagan buenas soldaduras que se puedan inspeccionar "
            "adecuadamente. "
            "(e) La selección del detalle que evite la corrosión general y la local debida a hendiduras. "
            "(f) Los efectos de distorsión causada por la soldadura. "
            "F.5.6.7.1 — Efecto de la soldadura en la resistencia estática — La soldadura puede afectar la "
            "resistencia del material base en la vecindad de la soldadura, como se describe en detalle en F.5.4. "
            "En aleaciones tratadas en caliente en la condición O ó F, el efecto de ablandamiento es insignificante "
            "y los efectos de la zona afectada por el calor pueden ignorarse. La unión es por lo tanto tan fuerte "
            "como el material base no soldado. La soldadura reduce la resistencia en las aleaciones tratadas en "
            "caliente, en la mayoría de las condiciones de tratamiento en caliente (series 6*** y 7***), y en las "
            "aleaciones no tratadas en caliente en cualquier condición de endurecimiento por trabajo (series 3*** "
            "y 5***). Para excepciones a esta regla general véase la tabla F.5.4.4-1, kz=1. "
            "En miembros fabricados con un material que sufre reducción de resistencia, la soldadura debe ser "
            "preferiblemente paralela a la dirección de la carga aplicada. En lo posible se deben evitar las "
            "soldaduras transversales a la carga aplicada o colocarlas en regiones de bajo esfuerzo. Esta "
            "recomendación incluye los accesorios soldados estén o no requeridos para transmitir carga del "
            "miembro. "
            "F.5.6.7.2 — Efecto de la soldadura en la resistencia a la fatiga — La resistencia a la fatiga de una "
            "unión depende de la severidad de la concentración de esfuerzos que puede generarse por la geometría "
            "general de la unión o por la geometría local de la soldadura. Las clasificaciones por fatiga de "
            "detalles de unión comúnmente usados se encuentran en F.5.7.3. La clasificación por fatiga puede "
            "usarse para seleccionar el detalle apropiado para la aplicación que brinde la mejor resistencia a la "
            "fatiga. "
            "F.5.6.7.3 — Corrosión — Las uniones deben detallarse de modo que se eviten cavidades o hendiduras "
            "inaccesibles que puedan retener humedad o suciedad. Cuando dichas cavidades sean inevitables, deben "
            "sellarse con soldadura o compuestos protectores, o hacerlas accesibles para su inspección y "
            "mantenimiento."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_7_4_a_6", "seccion": "F.5.6.7.4",
        "titulo": "F.5.6.7.4 — Preparaciones de los bordes (BS 3019/BS 3571). F.5.6.7.5 — Distorsión. F.5.6.7.6 — Información dada al fabricante (a-f, notas 1-3)",
        "texto": (
            "F.5.6.7.4 — Preparaciones de los bordes — Las preparaciones de los bordes para uniones soldadas a "
            "tope o de filete, incluyendo el uso de platinas de respaldo permanentes o temporales deberán cumplir "
            "con las normas pertinentes (por ejemplo las normas inglesas BS 3019 parte 1 y BS 3571 parte 1). La "
            "preparación real debe ser aprobada como parte del procedimiento de soldadura. "
            "F.5.6.7.5 — Distorsión — Cada soldadura causa encogimiento y distorsión, y sus efectos son más "
            "marcados en la construcción con aluminio que en las estructuras de acero. El encogimiento y la "
            "distorsión deben ser compensados o balanceados para mantener la forma y dimensión deseadas en la "
            "estructura terminada. El diseñador debe consultar al fabricante, en una fase temprana del diseño, "
            "sobre el método de soldadura, la distorsión y aspectos relacionados tales como secuencias de "
            "soldadura y uso de prensas. "
            "F.5.6.7.6 — Información dada al fabricante — Se deben suministrar planos y especificaciones dando la "
            "siguiente información acerca de cada soldadura: "
            "(a) Material base y de aportación. "
            "(b) Dimensiones de la soldadura. "
            "(c) Preparación de borde y posición de soldadura. "
            "(d) Proceso de soldadura. "
            "(e) Requisitos especiales tales como uniformidad del perfil de soldadura, precalentamiento y "
            "temperatura entre pasadas. "
            "(f) Requisitos de control de calidad para: (1) Aprobación del procedimiento de soldadura. "
            "(2) Aprobación del soldador. (3) Clase de calidad de soldadura (véanse las notas 1 a 3). "
            "(4) Niveles de inspección de uniones soldadas. (5) Niveles de aceptación para calidad de soldadura. "
            "(6) Procedimiento de reparación de soldadura. "
            "NOTA 1 — Cuando no se especifica la clase de calidad de soldadura en los planos, se supone calidad "
            "\"normal\". "
            "NOTA 2 — Cuando las acciones bajo carga mayorada no superan un tercio de la resistencia de diseño del "
            "miembro o de la unión, por ejemplo puede gobernar la rigidez, se acepta una calidad y un grado de "
            "inspección inferiores. Esto se aplica tanto a la resistencia estática como a la fatiga. En este caso "
            "se puede especificar un nivel \"mínimo\" de calidad. "
            "NOTA 3 — Cuando las uniones se diseñan sobre los requisitos de resistencia a la fatiga, consulte "
            "F.5.7.8.5."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_7_7", "seccion": "F.5.6.7.7",
        "titulo": "F.5.6.7.7 — Soldaduras a tope: restricciones a penetración parcial/intermitentes, espesor de garganta efectivo (Figura F.5.6.7-1)",
        "texto": (
            "F.5.6.7.7 — Soldaduras a tope — Soldaduras de penetración parcial en un solo lado y soldaduras a tope "
            "intermitentes no se deben usar para transmitir fuerzas de tensión, ni para transmitir un momento "
            "flector respecto al eje longitudinal de la soldadura. "
            "El espesor de garganta efectivo de una soldadura a tope de penetración parcial (véanse las figuras "
            "F.5.6.7-1 (b) y (c)) debe tomarse como: "
            "(a) La profundidad de la preparación de la soldadura cuando ésta es del tipo J o U. "
            "(b) La profundidad de la preparación de la soldadura menos 3 mm o el 25%, lo que sea menor, cuando es "
            "del tipo V o biselada. "
            "También es posible determinar el espesor de garganta por tanteos. Si se hace ésto, el espesor de la "
            "garganta no debe tomarse mayor que la penetración consistentemente lograda, ignorando el refuerzo de "
            "la soldadura. Se puede suponer penetración total en una soldadura a tope por un solo lado si se usa "
            "una platina de respaldo. Se puede tener en cuenta una soldadura de filete superpuesta en una unión en "
            "T. "
            "Figura F.5.6.7-1 — Garganta efectiva de soldaduras a tope: tres configuraciones esquemáticas de "
            "geometría de junta (a: penetración completa con cordón de raíz; b: penetración parcial tipo bisel; "
            "c: penetración parcial tipo V), cada una marcando el espesor efectivo de garganta te. Diagrama "
            "geométrico, no se transcribe la geometría, solo las reglas textuales de cálculo del espesor ya dadas "
            "arriba."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_7_8", "seccion": "F.5.6.7.8",
        "titulo": "F.5.6.7.8 — Soldaduras de filete: restricciones a un solo lado/intermitentes, garganta gt (Figura F.5.6.7-2), área efectiva",
        "texto": (
            "F.5.6.7.8 — Soldaduras de filete — Soldaduras de filete en un solo lado no deben usarse para "
            "transmitir momentos respecto de sus propios ejes. Pueden usarse soldaduras de filete intermitentes "
            "sólo si la distancia entre los extremos de soldaduras adyacentes, en línea o escalonadas sobre lados "
            "alternos de la pieza, no excede lo menor de lo siguiente: "
            "(a) 10 veces el espesor del material base más delgado o 300 mm, si está a compresión o cortante. "
            "(b) 24 veces ese espesor o 300 mm, si está a tensión. "
            "En una línea de soldaduras intermitentes debe haber una soldadura en cada extremo de la pieza "
            "conectada. La resistencia de diseño de una unión con soldadura de filete se da en F.5.6.9.2. "
            "Una soldadura de filete debe ser continua alrededor de la esquina en el extremo o lado de una pieza, "
            "con una longitud más allá de la esquina de no menos dos veces la longitud del lado de la soldadura. "
            "Véase el literal (f) de F.5.4.4.3 para el efecto de traslapar zonas afectadas por el calor. "
            "Si se usan dos soldaduras de filete longitudinales solas en una conexión de extremo traslapada, la "
            "longitud de cada una no debe ser menor que la distancia entre ellas. "
            "La garganta de una soldadura de filete (gt), véase la figura F.5.6.7-2 (a), es la altura de un "
            "triángulo que puede ser inscrito dentro de la soldadura y medida perpendicular a su lado exterior. "
            "Excepcionalmente, la garganta de una soldadura de filete puede ser tomada incluyendo cualquier "
            "penetración especificada, pt, siempre que los tanteos demuestren satisfactoriamente al diseñador que "
            "dicha penetración puede ser lograda consistentemente. Se puede suponer una garganta grande si los "
            "tanteos durante el procedimiento muestran que la penetración necesaria más allá de la raíz nominal "
            "puede ser consistentemente obtenida, por ejemplo, mediante soldadura automática (véase la figura "
            "F.5.6.7-2 (b)). "
            "El área efectiva de una soldadura de filete es su dimensión de garganta (gt) multiplicada por su "
            "longitud efectiva, excepto que, para soldaduras de filete en agujeros o ranuras, el área efectiva no "
            "debe ser mayor que el área del agujero o ranura. La longitud efectiva se define en F.5.6.9.2. "
            "Figura F.5.6.7-2 — Garganta efectiva de soldaduras de filete: (a) definición geométrica de gr "
            "(longitud de la garganta), gt (longitud del lado) y Pt (penetración); (b) variante con penetración "
            "considerada. Diagrama geométrico, no se transcribe la geometría, solo las definiciones textuales ya "
            "dadas."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_7_3_figura", "seccion": "F.5.6.7-3",
        "titulo": "Figura F.5.6.7-3 — Planos de falla para revisión estática de uniones soldadas: convención W (metal de aporte), F (frontera de fusión), T (borde), zona afectada por el calor",
        "texto": (
            "Figura F.5.6.7-3 — Planos de falla para revisión estática de uniones soldadas: 6 configuraciones "
            "esquemáticas (a: soldadura a tope en línea; b: soldadura de filete traslapada; c: soldadura a tope en "
            "T; d: soldadura de filete en T; e: soldadura a tope en T y soldadura de filete en T; f: líneas de "
            "falla potencial en vista en planta de un extremo de la unión), mostrando las fuerzas Pv/Pa aplicadas "
            "y las líneas de falla potencial marcadas W/F/T. Diagrama geométrico, no se transcribe la geometría "
            "gráfica — solo la convención textual asociada: "
            "Convenciones (véanse las figuras F.5.6.7-1 y F.5.6.7-2): W = metal de aporte. F = zona afectada por "
            "el calor (frontera de fusión). T = zona afectada por el calor (borde). El ancho de la zona es t para "
            "filetes. Para soldadura a tope, el plano es igual al espesor de la lámina. Para soldadura de filete, "
            "el ancho del plano es el ancho de la longitud del lado de la soldadura. El área sombreada es la zona "
            "afectada por el calor."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_8_intro_1_2", "seccion": "F.5.6.8",
        "titulo": "F.5.6.8 — Resistencia de Diseño de Uniones Soldadas. F.5.6.8.1 — Grupos de soldaduras. F.5.6.8.2 — Esfuerzo límite del metal de aporte (Tabla F.5.6.8-1)",
        "texto": (
            "F.5.6.8 — RESISTENCIA DE DISEÑO DE UNIONES SOLDADAS — En el diseño de uniones soldadas se deben "
            "considerar la resistencia del metal de aporte y la resistencia del material en la zona afectada por "
            "el calor adyacente a la frontera de fusión de la soldadura (véase F.5.4.4 y la figura F.5.6.7-3). Los "
            "esfuerzos límites para el material de la zona afectada por el calor se tratan en F.5.6.9. La "
            "capacidad de deformación de la unión se mejora cuando la resistencia de diseño de la soldadura es "
            "mayor que la del material adyacente en la zona afectada por el calor. "
            "F.5.6.8.1 — Grupos de soldaduras — Una unión soldada consistente de un grupo de soldaduras debe "
            "diseñarse sobre la base de una distribución realista de esfuerzos entre las soldaduras relacionada "
            "con su rigidez relativa. Es esencial mantener el equilibrio con las cargas externas mayoradas. "
            "F.5.6.8.2 — Esfuerzo límite del metal de aporte — El alambre de metal de aportación para uso en "
            "construcción soldada debe ser escogido de acuerdo con la tabla F.5.2.7-1. "
            "Los valores del esfuerzo límite del metal de aportación pw (en kgf/mm²) para las combinaciones "
            "permitidas de material base y de aportación mostradas en la tabla F.5.2.7-1, se dan en la tabla "
            "F.5.6.8-1. "
            + TABLA_F_5_6_8_1
        ),
    },
    {
        "id": "NSR10-F-F_5_6_8_3", "seccion": "F.5.6.8.3",
        "titulo": "F.5.6.8.3 — Esfuerzo límite en la zona afectada por el calor: paz (directo) y pvz (cortante), Tabla F.5.6.8-2 por aleación",
        "texto": (
            "F.5.6.8.3 — Esfuerzo límite en la zona afectada por el calor — Los esfuerzos límite paz y pvz para el "
            "material en la zona afectada por el calor se dan en la tabla F.5.6.8-2, donde paz y pvz son, "
            "respectivamente, el esfuerzo límite directo y de cortante. "
            "Pueden necesitarse valores más altos de esfuerzo límite para materiales de aporte particulares (véase "
            "apéndice F.5.C). "
            + TABLA_F_5_6_8_2
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
