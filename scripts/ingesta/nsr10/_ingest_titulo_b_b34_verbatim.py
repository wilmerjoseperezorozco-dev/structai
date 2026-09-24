"""
Ingesta verbatim de Título B, sección B.3.4 (Elementos no
estructurales, dentro de Cargas muertas) -- NSR-10. Fase 3 del plan de
cierre del Título B (2026-09-23) -- ya identificado desde la sesión de
2026-09-08 (ver docstring de `_ingest_titulo_b_b33_b35_b36_verbatim.py`)
como "la referencia de mayor valor práctico pendiente de Título B":
los chunks existentes (`NSR10-B-B_3_4_r1/r2/r3`) son un resumen
condensado con solo 2-3 valores de ejemplo por tabla, no verbatim
completo -- mismo patrón "resumen disfrazado de completo" ya visto
repetidamente en A.3/A.9/A.10 el día anterior.

Fuente: NSR-10-228-233.pdf, páginas PDF 2-6 (B-10 a B-14). Leídas
visualmente con Read pages= sobre el PDF nativo -- nunca extracción
mecánica (pypdf).

Uso: python _ingest_titulo_b_b34_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

IDS_A_BORRAR_CONDENSADOS = ["NSR10-B-B_3_4_r1", "NSR10-B-B_3_4_r2", "NSR10-B-B_3_4_r3"]

CHUNKS = [
    {
        "id": "NSR10-B-B_3_4_intro_horizontales_tabla_1_2",
        "seccion": "B.3.4 y B.3.4.1 — Elementos no estructurales horizontales (Tablas B.3.4.1-1 y B.3.4.1-2: cielo raso y relleno de pisos)",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "B.3.4 — ELEMENTOS NO ESTRUCTURALES — Para el cálculo de "
            "las cargas muertas producidas por materiales de "
            "construcción no estructurales, estos elementos se "
            "dividen en horizontales y verticales.\n\n"
            "B.3.4.1 — ELEMENTOS NO ESTRUCTURALES HORIZONTALES — Los "
            "elementos no estructurales horizontales son aquellos "
            "cuya dimensión vertical es substancialmente menor que "
            "sus dimensiones horizontales, y están aplicados, "
            "soportados, fijados o anclados a las losas o a la "
            "cubierta de la edificación. Estos elementos incluyen, "
            "entre otros: formaletería permanente para losas o "
            "viguetas, morteros de afinado de piso, rellenos de piso, "
            "acabados de piso, rellenos en cubiertas inclinadas, "
            "elementos de cubiertas, tejas, membranas impermeables, "
            "aislamientos térmicos, claraboyas, cielo raso, "
            "alistados, y ductos para servicios.\n\n"
            "Nota: Para propósitos de diseño, las cargas muertas para "
            "los elementos no estructurales horizontales se "
            "consideran como cargas verticales uniformes por unidad "
            "de área de superficie o proyección horizontal, aplicada "
            "en las zonas correspondientes en que se localizan tales "
            "elementos. En la determinación de las cargas muertas "
            "producidas por tales elementos se debe usar la densidad "
            "de masa real de los materiales y un espesor realista. "
            "Como guía, en la tabla B.3.2-1 se sugieren las "
            "densidades de masa mínimas (tales valores deben "
            "multiplicarse por g y por el espesor correspondiente en "
            "m para obtener las cargas muertas en N/m²). En las "
            "tablas B.3.4.1-1 a B.3.4.1-4 se dan valores de cargas "
            "muertas de los materiales típicos en elementos no "
            "estructurales horizontales, los cuales corresponden a "
            "valores mínimos promedio. El diseñador estructural debe "
            "tener en cuenta la posibilidad de variación de estos "
            "valores debido a diferencias en los materiales locales y "
            "en la práctica constructiva.\n\n"
            "Tabla B.3.4.1-1 — Cargas muertas mínimas de elementos no "
            "estructurales horizontales — Cielo raso (kN/m² | kgf/m², "
            "por m² de área en planta):\n"
            "Canales suspendidas de acero: 0.10 | 10.\n"
            "Ductos mecánicos: 0.20 | 20.\n"
            "Entramado metálico suspendido afinado en cemento: 0.70 | "
            "70.\n"
            "Entramado metálico suspendido afinado en yeso: 0.50 | "
            "50.\n"
            "Fibras acústicas: 0.10 | 10.\n"
            "Pañete en yeso o concreto: 0.25 | 25.\n"
            "Pañete en entramado de madera: 0.80 | 80.\n"
            "Tableros de yeso: 0.0080 (por mm de espesor) | 8 (por cm "
            "de espesor).\n"
            "Sistema de suspensión de madera: 0.15 | 15.\n\n"
            "Tabla B.3.4.1-2 — Cargas muertas mínimas de elementos no "
            "estructurales horizontales — Relleno de pisos (kN/m² | "
            "kgf/m², por m² de área en planta):\n"
            "Arena: 0.0150 (por mm de espesor) | 15 (por cm de "
            "espesor).\n"
            "Concreto con escoria: 0.0200 (por mm de espesor) | 20 "
            "(por cm de espesor).\n"
            "Concreto con piedra: 0.0250 (por mm de espesor) | 25 "
            "(por cm de espesor).\n"
            "Concreto ligero: 0.0150 (por mm de espesor) | 15 (por cm "
            "de espesor)."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_1_tabla_3_pisos",
        "seccion": "Tabla B.3.4.1-3 — Elementos no estructurales horizontales: pisos y acabados",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "Tabla B.3.4.1-3 — Cargas muertas mínimas de elementos no "
            "estructurales horizontales — Pisos y acabados (kN/m² | "
            "kgf/m², por m² de área en planta):\n"
            "Acabado de piso en concreto: 0.0200 (por mm de espesor) "
            "| 20 (por cm de espesor).\n"
            "Afinado (25 mm) sobre concreto de agregado pétreo: 1.50 "
            "| 150.\n"
            "Baldosa cerámica (20 mm) sobre 12 mm de mortero: 0.80 | "
            "80.\n"
            "Baldosa cerámica (20 mm) sobre 25 mm de mortero: 1.10 | "
            "110.\n"
            "Baldosa sobre 25 mm de mortero: 1.10 | 110.\n"
            "Bloque de asfalto (50 mm), sobre 12 mm de mortero: 1.50 "
            "| 150.\n"
            "Bloque de madera (75 mm) sin relleno: 0.50 | 50.\n"
            "Bloque de madera (75 mm) sobre 12 mm de mortero: 0.80 | "
            "80.\n"
            "Durmientes de madera, 20 mm: 0.15 | 15.\n"
            "Madera densa, 25 mm: 0.20 | 20.\n"
            "Mármol y mortero sobre concreto de agregado pétreo: 1.60 "
            "| 160.\n"
            "Piso asfáltico o linóleo, 6 mm: 0.05 | 5.\n"
            "Pizarra: 0.030 (por mm de espesor) | 30 (por cm de "
            "espesor).\n"
            "Terrazzo (25 mm), concreto 50 mm: 1.50 | 150.\n"
            "Terrazzo (40 mm) directamente sobre la losa: 0.90 | 90.\n"
            "Terrazzo (25 mm) sobre afinado en concreto: 1.50 | 150."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_1_tabla_4_cubiertas",
        "seccion": "Tabla B.3.4.1-4 — Elementos no estructurales horizontales: cubiertas",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "Tabla B.3.4.1-4 — Cargas muertas mínimas de elementos no "
            "estructurales horizontales — Cubierta (kN/m² | kgf/m², "
            "por m² de área en planta):\n"
            "Cobre o latón: 0.05 | 5.\n"
            "Cubiertas aislantes — Fibra de vidrio: 0.0020 (por mm de "
            "espesor) | 2.0 (por cm de espesor).\n"
            "Cubiertas aislantes — Tableros de fibra: 0.0030 (por mm "
            "de espesor) | 3.0 (por cm de espesor).\n"
            "Cubiertas aislantes — Perlita: 0.0015 (por mm de "
            "espesor) | 1.5 (por cm de espesor).\n"
            "Cubiertas aislantes — Espuma de poliestireno: 0.0005 "
            "(por mm de espesor) | 0.5 (por cm de espesor).\n"
            "Cubiertas aislantes — Espuma de poliuretano: 0.0010 (por "
            "mm de espesor) | 1.0 (por cm de espesor).\n"
            "Cubiertas corrugadas de asbesto-cemento: 0.20 | 20.\n"
            "Entablado de madera: 0.0060 (por mm de espesor) | 6.0 "
            "(por cm de espesor).\n"
            "Láminas de yeso, 12 mm: 0.10 | 10.\n"
            "Madera laminada (según el espesor): 0.0100 (por mm de "
            "espesor) | 10.0 (por cm de espesor).\n"
            "Membranas impermeables — Bituminosa, cubierta de grava: "
            "0.25 | 25.\n"
            "Membranas impermeables — Bituminosa, superficie lisa: "
            "0.10 | 10.\n"
            "Membranas impermeables — Líquido aplicado: 0.05 | 5.\n"
            "Membranas impermeables — Tela asfáltica de una capa: "
            "0.03 | 3.\n"
            "Marquesinas, marco metálico, vidrio de 10 mm: 0.40 | 40.\n"
            "Tableros de fibra, 12 mm: 0.05 | 5.\n"
            "Tableros de madera, 50 mm: 0.25 | 25.\n"
            "Tableros de madera, 75 mm: 0.40 | 40.\n"
            "Tablero metálico, calibre 20 (0.9 mm de espesor "
            "nominal): 0.08 | 8.\n"
            "Tablero metálico, calibre 18 (1.2 mm de espesor "
            "nominal): 0.08 | 8.\n"
            "Tablillas (shingles) de asbesto-cemento: 0.20 | 20.\n"
            "Tablillas (shingles) de asfalto: 0.10 | 10.\n"
            "Tablillas (shingles) de madera: 0.15 | 15.\n"
            "Teja de arcilla, incluyendo el mortero: 0.80 | 80."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_2_verticales_intro_tabla_1_2_3",
        "seccion": "B.3.4.2 — Elementos no estructurales verticales, intro + Tablas B.3.4.2-1 a -3 (recubrimiento de muros, particiones livianas, enchapes)",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "B.3.4.2 — ELEMENTOS NO ESTRUCTURALES VERTICALES — Los "
            "elementos no estructurales verticales son aquellos cuya "
            "dimensión vertical es substancialmente mayor que su "
            "mínima dimensión horizontal y se encuentran erguidos "
            "libremente o soportados por los elementos estructurales "
            "verticales o fijados a ellos o anclados solamente a las "
            "losas de entrepiso. Tales elementos incluyen, entre "
            "otros: fachadas, muros no estructurales, particiones, "
            "recubrimiento de muros, enchapes, ornamentación "
            "arquitectónica, ventanas, puertas, y ductos verticales "
            "de servicios. En las edificaciones en las cuales se "
            "puedan disponer particiones, se debe hacer provisión de "
            "carga para ellas, ya sea que estas figuren o no, en los "
            "planos arquitectónicos.\n\n"
            "Tabla B.3.4.2-1 — Cargas muertas mínimas de elementos no "
            "estructurales verticales — Recubrimiento de muros (kN/m² "
            "| kgf/m², por m² de superficie vertical, multiplicar por "
            "la altura del elemento en m para obtener cargas "
            "distribuidas en kN/m o kgf/m):\n"
            "Baldosín de cemento: 0.80 | 80.\n"
            "Entablado de madera: 0.0060 (por mm de espesor) | 6.0 "
            "(por cm de espesor).\n"
            "Madera laminada (según el espesor): 0.0100 (por mm de "
            "espesor) | 10.0 (por cm de espesor).\n"
            "Tableros aislantes para muros — Espuma de poli estireno: "
            "0.0005 (por mm) | 0.5 (por cm).\n"
            "Tableros aislantes para muros — Espuma de poliuretano: "
            "0.0010 (por mm) | 1.0 (por cm).\n"
            "Tableros aislantes para muros — Fibra o acrílico: 0.0020 "
            "(por mm) | 2.0 (por cm).\n"
            "Tableros aislantes para muros — Perlita: 0.0015 (por mm) "
            "| 1.5 (por cm).\n"
            "Tableros aislantes para muros — Tableros de fibra: "
            "0.0030 (por mm) | 3.0 (por cm).\n"
            "Tableros de fibra, 12 mm: 0.05 | 5.\n"
            "Tableros de yeso, 12 mm: 0.10 | 10.\n\n"
            "Tabla B.3.4.2-2 — Elementos no estructurales verticales — "
            "Particiones livianas (kN/m² | kgf/m², por m² de "
            "superficie vertical):\n"
            "Particiones móviles de acero (altura parcial): 0.50 | "
            "50.\n"
            "Particiones móviles de acero (altura total): 0.20 | 20.\n"
            "Poste en madera o acero, yeso de 12 mm a cada lado: 0.90 "
            "| 90.\n"
            "Poste en madera, 50 x 100, sin pañetar: 0.30 | 30.\n"
            "Poste en madera, 50 x 100, pañete por un lado: 0.60 | "
            "60.\n"
            "Poste en madera, 50 x 100, pañete por ambos lados: 2.00 "
            "| 200.\n\n"
            "Tabla B.3.4.2-3 — Elementos no estructurales verticales — "
            "Enchapes (kN/m² | kgf/m², por m² de superficie "
            "vertical):\n"
            "Enchape cerámico: 0.015 (por mm de espesor) | 15 (por cm "
            "de espesor).\n"
            "Enchape en arenisca: 0.013 (por mm de espesor) | 13 (por "
            "cm de espesor).\n"
            "Enchape en caliza: 0.015 (por mm de espesor) | 15 (por "
            "cm de espesor).\n"
            "Enchape en granito: 0.017 (por mm de espesor) | 17 (por "
            "cm de espesor)."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_2_tabla_4_muros",
        "seccion": "Tabla B.3.4.2-4 — Elementos no estructurales verticales: muros (mampostería de bloque/maciza según espesor)",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "Tabla B.3.4.2-4 — Cargas muertas mínimas de elementos no "
            "estructurales verticales — Muros (kN/m² | kgf/m², por m² "
            "de superficie vertical, multiplicar por la altura del "
            "elemento en m):\n\n"
            "Exteriores de paneles (postes de acero o madera): "
            "Yeso de 15 mm, aislado, entablado de 10 mm: 1.00 | 100.\n"
            "Exteriores con enchape en ladrillo: 2.50 | 250.\n\n"
            "Mampostería de bloque de arcilla (espesor del muro en "
            "mm: 100/150/200/250/300, en cm: 10/15/20/25/30):\n"
            "Pañetado en ambas caras: 1.80 / 2.50 / 3.10 / 3.80 / "
            "4.40 kN/m² (180/250/310/380/440 kgf/m²).\n"
            "Sin pañetar: 1.30 / 2.00 / 2.60 / 3.30 / 3.90 kN/m² "
            "(130/200/260/330/390 kgf/m²).\n\n"
            "Mampostería de bloque de concreto (espesor del muro en "
            "mm: 100/150/200/250/300, en cm: 10/15/20/25/30):\n"
            "Sin relleno: 1.40 / 1.45 / 1.90 / 2.25 / 2.60 kN/m² "
            "(140/145/190/225/260 kgf/m²).\n"
            "Relleno cada 1.2 m: — / 1.70 / 2.25 / 2.70 / 3.15 kN/m² "
            "(—/170/225/270/315 kgf/m²).\n"
            "Relleno cada 1.0 m: — / 1.80 / 2.30 / 2.80 / 3.30 kN/m² "
            "(—/180/230/280/330 kgf/m²).\n"
            "Relleno cada 0.8 m: — / 1.80 / 2.40 / 3.00 / 3.45 kN/m² "
            "(—/180/240/300/345 kgf/m²).\n"
            "Relleno cada 0.6 m: — / 2.00 / 2.60 / 3.20 / 3.75 kN/m² "
            "(—/200/260/320/375 kgf/m²).\n"
            "Relleno cada 0.4 m: — / 2.20 / 2.90 / 3.60 / 4.30 kN/m² "
            "(—/220/290/360/430 kgf/m²).\n"
            "Todas las celdas llenas: — / 3.00 / 4.00 / 5.00 / 6.10 "
            "kN/m² (—/300/400/500/610 kgf/m²).\n\n"
            "Mampostería maciza de arcilla (espesor del muro en mm: "
            "100/150/200/250/300, en cm: 10/15/20/25/30):\n"
            "Sin pañetar: 1.90 / 2.90 / 3.80 / 4.70 / 5.50 kN/m² "
            "(190/290/380/470/550 kgf/m²).\n\n"
            "Mampostería maciza de concreto (espesor del muro en mm: "
            "100/150/200/250/300, en cm: 10/15/20/25/30):\n"
            "Sin pañetar: 2.00 / 3.10 / 4.20 / 5.30 / 6.40 kN/m² "
            "(200/310/420/530/640 kgf/m²)."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_2_tabla_5_ventanas_notas",
        "seccion": "Tabla B.3.4.2-5 y notas — Elementos no estructurales verticales: ventanas y notas de aplicación",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "Tabla B.3.4.2-5 — Cargas muertas mínimas de elementos no "
            "estructurales verticales — Ventanas (kN/m² | kgf/m², por "
            "m² de superficie vertical):\n"
            "Muros cortina de vidrio, entramado y marco: 0.50 | 50.\n"
            "Ventanas, vidrio, entramado y marco: 0.45 | 45.\n\n"
            "Nota: Para propósitos de diseño, las cargas muertas "
            "causadas por los elementos no estructurales verticales "
            "se consideran como cargas concentradas, o distribuidas "
            "por unidad de longitud del elemento no estructural. Como "
            "una guía, se sugieren los valores mínimos de densidad de "
            "masa de la tabla B.3.2-1 (los valores allí dados deben "
            "multiplicarse por g, por el espesor correspondiente en "
            "m, y por la altura del elemento en m, con el fin de "
            "obtener cargas muertas uniformes distribuidas en N/m). "
            "En las tablas B.3.4.2-1 a B.3.4.2-5 se dan los valores "
            "de carga muerta de los materiales típicos empleados en "
            "los elementos no estructurales verticales, en kN por "
            "unidad de área vertical en m². Para obtener las cargas "
            "muertas distribuidas en kN/m, los valores sugeridos en "
            "las tablas B.3.4.2-1 a B.3.4.2-5 deben multiplicarse por "
            "la altura en m del elemento no estructural vertical. Los "
            "valores dados en las tablas B.3.2-1 y B.3.4.2-1 a "
            "B.3.4.2-5, corresponden a valores mínimos promedio; el "
            "diseñador estructural debe tener en cuenta la "
            "posibilidad de variación de estos valores debido a "
            "diferencias en los materiales locales y en la práctica "
            "constructiva.\n\n"
            "Nota: La carga muerta de los elementos no estructurales "
            "verticales internos, como muros y particiones "
            "interiores, puede considerarse como una carga muerta "
            "uniforme vertical por unidad de área cuando los "
            "elementos estructurales secundarios del sistema de piso "
            "sean capaces de soportar las cargas concentradas o "
            "distribuidas causadas por ellas, sin que se afecte el "
            "nivel de resistencia o servicio del sistema de piso del "
            "elemento no estructural. Si los elementos no "
            "estructurales verticales tienen más de un nivel de "
            "altura, sus cargas muertas deben considerarse como "
            "cargas concentradas o distribuidas. La carga muerta de "
            "fachadas y elementos de cerramiento de la edificación "
            "deben considerarse como cargas distribuidas sobre el "
            "borde de la losa."
        ),
    },
    {
        "id": "NSR10-B-B_3_4_3_valores_alternativos_tabla",
        "seccion": "B.3.4.3 — Valores mínimos alternativos para cargas muertas de elementos no estructurales (Tabla B.3.4.3-1, por tipo de ocupación)",
        "titulo": "NSR-10 Título B — Capítulo B.3 — Cargas muertas",
        "texto": (
            "B.3.4.3 — VALORES MÍNIMOS ALTERNATIVOS PARA CARGAS "
            "MUERTAS DE ELEMENTOS NO ESTRUCTURALES — En edificaciones "
            "con alturas entre pisos terminados menores a 3 m, se "
            "pueden utilizar los valores mínimos de carga muerta en "
            "kN/m² de área horizontal en planta, dados en la tabla "
            "B.3.4.3-1 según el tipo de ocupación, en vez de aquellos "
            "obtenidos del análisis detallado de las cargas muertas "
            "causadas por los elementos no estructurales.\n\n"
            "Tabla B.3.4.3-1 — Valores mínimos alternativos de carga "
            "muerta de elementos no estructurales cuando no se "
            "efectúe un análisis más detallado (Ocupación | Fachada y "
            "particiones kN/m² | Afinado de piso y cubierta kN/m² | "
            "Fachada y particiones kgf/m² | Afinado de piso y "
            "cubierta kgf/m²):\n\n"
            "Reunión — edificaciones con un salón de reunión para "
            "menos de 100 personas y sin escenarios: 1.0 | 1.8 | 100 "
            "| 180.\n"
            "Oficinas — particiones móviles de altura total: 1.0 | "
            "1.8 | 100 | 180.\n"
            "Oficinas — particiones fijas de mampostería: 2.0 | 1.8 | "
            "200 | 180.\n"
            "Educativos — salones de clase: 2.0 | 1.5 | 200 | 150.\n"
            "Fábricas — industrias livianas: 0.8 | 1.6 | 80 | 160.\n"
            "Institucional — internados con atención a los "
            "residentes: 2.0 | 1.6 | 200 | 160.\n"
            "Institucional — prisiones, cárceles, reformatorios y "
            "centros de detención: 2.5 | 1.8 | 250 | 180.\n"
            "Institucional — guarderías: 2.0 | 1.6 | 200 | 160.\n"
            "Comercio — exhibición y venta de mercancías: 1.5 | 1.4 "
            "| 150 | 140.\n"
            "Residencial — fachada y particiones de mampostería: 3.0 "
            "| 1.6 | 300 | 160.\n"
            "Residencial — fachada y particiones livianas: 2.0 | 1.4 "
            "| 200 | 140.\n"
            "Almacenamiento — almacenamiento de materiales livianos: "
            "1.5 | 1.5 | 150 | 150.\n"
            "Garajes — garajes para vehículos con capacidad de hasta "
            "2000 kg: 0.2 | 1.0 | 20 | 100."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print(f"Borrando {len(IDS_A_BORRAR_CONDENSADOS)} chunks condensados (no verbatim) de B.3.4...")
    sb.table("nsr10_chunks").delete().in_("id", IDS_A_BORRAR_CONDENSADOS).execute()

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
    print("OK.")


if __name__ == "__main__":
    main()
