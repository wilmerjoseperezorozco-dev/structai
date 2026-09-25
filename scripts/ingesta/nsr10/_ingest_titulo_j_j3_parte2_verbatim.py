"""
Título J — re-ingesta verbatim, Capítulo J.3 (parte 2 de 2): J.3.4 completo
(Determinación de la resistencia requerida contra fuego, con las tablas
J.3.4-1/2/3 de potencial combustible y resistencia normalizada) y J.3.5
completo (Evaluación de la provisión de resistencia contra fuego —
elementos de concreto, mampostería y acero estructural, tablas J.3.5-1 a
J.3.5-10 y las ecuaciones J.3.5-1/2/3).

Fuente: NSR-10-1501-1570.pdf, páginas reales 44-53 (J-15 a J-24, capítulo
J.3 completo hasta la página "Notas" en blanco). Offset real confirmado:
página_J = página_real - 29 (el docstring de la parte 1 tenía un offset
equivocado, corregido aquí tras verificación visual directa).

Reemplaza 12 chunks condensados detectados por patrón "resumen disfrazado
de completo" (minúsculas sin tildes, seccion en formato genérico/rango,
mismo patrón visto repetidamente en Títulos A y B esta sesión) — verificado
leyendo su texto real antes de borrar, no solo por el nombre del id:
NSR10-J-J_3_4_r1/r2/r3, NSR10-J-J_3_5_1_a_J_3_5_2_r1/r2/r3,
NSR10-J-J_3_5_3_r1/r2/r3, NSR10-J-J_3_5_4_r1/r2/r3.
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

CAPITULO = "NSR-10 Título J — Requisitos de Protección Contra Incendios en Edificaciones"

IDS_OBSOLETOS = [
    "NSR10-J-J_3_4_r1", "NSR10-J-J_3_4_r2", "NSR10-J-J_3_4_r3",
    "NSR10-J-J_3_5_1_a_J_3_5_2_r1", "NSR10-J-J_3_5_1_a_J_3_5_2_r2", "NSR10-J-J_3_5_1_a_J_3_5_2_r3",
    "NSR10-J-J_3_5_3_r1", "NSR10-J-J_3_5_3_r2", "NSR10-J-J_3_5_3_r3",
    "NSR10-J-J_3_5_4_r1", "NSR10-J-J_3_5_4_r2", "NSR10-J-J_3_5_4_r3",
]

TABLA_J_3_4_1 = (
    "Tabla J.3.4-1 — Potencial combustible estimado para materiales distribuidos por unidad de área, en MJ/m². "
    "Abonos artificiales 9.56; Aceites en tambores 1975.50; Acumuladores 47.80; Algodón de fardos 71.70; "
    "Alimentos 47.80; Alquitrán de hulla 191.20; Aparatos eléctricos 9.56; Archivos de documentos 95.60; "
    "Artículo de odontología 19.12; Artículos de madera 71.70; Asfalto 191.20; Autos, partes 9.56; "
    "Azúcar 478.00; Barnices y afines 143.40; Bobinas de madera 28.68; Bolsas de fibra sintética 1434.00; "
    "Bolsas de papel 717.00; Bolsas de yute 43.02; Cables en bobinas de madera 35.85; Café 167.30; "
    "Canastos de mimbre 9.56; Cáñamo 71.70; Carbón 597.50; Cartón en hojas apiladas 239.00; "
    "Cartón impregnado 119.50; Cartón, objetos de 23.90; Cartón, ondulado 71.70; Caucho en bruto 1625.20; "
    "Caucho, espuma de 143.40; Caucho, objetos de 286.80; Celuloide 191.20; Ceras 191.20; "
    "Ceras para pisos 286.80; Cereales en bolsas 382.40; Cereales en silos 764.80; Chocolate 191.20; "
    "Cigarrillos 143.90; Colas, pegantes 191.20; Colchones 28.68; Corcho 47.80; "
    "Cordelería 35.85; Cosmética, artículos de 28.68; Crin animal 35.85; Cuero 95.60; "
    "Cuero sintético 95.60; Cuero sintético 95.60; Cuero, objetos de 35.85; De 95.60; "
    "Decorados de teatros 59.75; Depósito de mercaderías 23.90; Desechos de papeles en fardos 119.50; Desechos de madera 143.90; "
    "Desechos de trapos 191.20; Desechos textiles 47.80; Droguerías 19.12; Dulces 47.80; "
    "Encajes y puntillas 35.85; Escobas 23.90; Fibras de coco 71.70; Fieltro 47.80; "
    "Flores Artificiales 9.60; Flores Artificiales 9.56; Forrajes 191.20; Fósforos 47.80; "
    "Fósforos 47.80; Gas licuado en cilindros de acero 358.50; Grasas 1075.50; Harina en bolsas 478.00; "
    "Harina en silos 860.40; Heno en gavillas 59.80; Hilos de uso textil 95.60; Huevos 9.60; "
    "Impresos en estanterías 95.60; impresos en paletas 478.00; Juguetes 47.80; Lanas 107.50; "
    "Leche en polvo 597.50; Lencería, ropas 35.85; Libros 119.50; Lino 71.70; "
    "Madera en bruto 358.50; Madera laminada 239.00; Madera, viruta en silos 119.50; Malta en silos 764.80; "
    "Manteca 239.00; Material de construcción 47.80; Material de equipos de oficina 47.80; Material eléctrico 19.12; "
    "Materias Sintéticas 19.10; Materias sintéticas en bruto 334.60; Materias sintéticas en espuma 71.70; Materias sintéticas, objetos de 47.80; "
    "Medicamentos 19.12; Melaza de toneles 286.80; Muebles 47.80; Negro humo en bolsas 71.70; "
    "Nitratos 4.78; Nitrocelulosa en toneles 59.75; Paja 71.70; Papel en bobinas apiladas 573.60; "
    "Papel, objetos de 59.80; Pastas alimenticias 95.60; Perlines 59.80; Pieles 71.70; "
    "Placas de madera aglomerada 382.40; Productos de lejías 28.70; Productos químicos mezclados 47.80; Puertas de madera 100.40; "
    "Puertas en material sintético 239.00; Radios, aparatos de 12.00; Recipientes de material plástico 40.60; Refrigeradores 19.10; "
    "Resinas sintéticas en barriles 239.00; Resinas sintéticas en placas 191.20; Revestimientos orgánicos de suelos 382.40; Solventes 191.20; "
    "Tabaco en bruto 95.60; Tabaco manufacturado 119.50; Tapices 119.50; Telas de lino 47.80; "
    "Telas y tejidos 59.80; Televisores 12.00; Vendas 47.80; Ventanas de material plástico 19.10; "
    "Ventanas de madera 19.10; Vestimentas 23.90."
)

TABLA_J_3_4_2 = (
    "Tabla J.3.4-2 — Potencial combustible estimado para materiales por unidad de masa, en MJ/kg. "
    "Aceites 2.2-2.4; Acetaldehído 1.4; Acetamida 1.2; Acetato de Amilo 1.9; "
    "Acetileno 2.9; Acetona 1.7; Ácido acético 0.96; Ácido benzoico 1.4; "
    "Ácido cítrico 1.4; Acroleína 1.7; Acumuladores de auto (batería) 2.4; Albúmina vegetal 1.4; "
    "Alcohol amílico 2.4; Alcohol etílico 1.4; Algodón 0.96; Almidón 0.96; "
    "Anilina 2.1; Antraceno 2.4; Antracita 1.9; Bencilo 1.9; "
    "Bencina 2.4; Benzol 2.4; Blanco de ballena 2.4; Bobina de cable por metro 71.7; "
    "Butano 2.6; Butanol 1.9; Cable 0.2; Cable por metro 0.3; "
    "Cacao en polvo 0.96; Café 0.96; Calcio 0.24; Carbón de madera 1.7; "
    "Carbono 1.9; Carburo de alúmina 0.96; Carburo de Calcio 80% 0.96; Cartón 0.96; "
    "Cartón impregnado 1.2; Caucho 2.4; Celuloide 0.96; Cereales 0.96; "
    "Chocolate 1.4; Ciclohexano 2.6; Cidoexanol 1.9; Cloruro de polivinilo P.V.C. 1.2; "
    "Corcho 0.96; Crisol 1.4; Cuero 1.2; Dietilamina 2.4; "
    "Dietilcetona 1.9; Difenil 2.4; Dipentano 2.6; Epocita 1.9; "
    "Espíritu de vino 1.9; Estearina 2.4; Etano 2.9; Éter amílico 2.4; "
    "Éter etilénico 1.9; Extracto de malta 1.9; Fenil 1.9; Fibras artificiales 0.96; "
    "Fibras naturales (madejas) 0.96; Fósforo 1.4; Gasoil 2.4; Glicerina 0.96; "
    "Grasas 2.4; Hametileno 2.6; Harina 0.96; Heno 0.96; "
    "Heptano 2.6; Hexano 2.6; Hidrógeno 8.1; Hidruro de magnesio 0.96; "
    "Hulla 1.9; Lana comprimida 1.2; Leche en polvo 0.96; Libros y carpetas 0.96; "
    "Lignito 1.2; Lino 0.96; Maderas 1.1; Magnesio 1.4; "
    "Malta, maíz 0.96; Materiales sintéticos 0.96; Metano 2.9; Metanol 1.2; "
    "Monóxido de carbono 0.5; Nueces, avellanas 0.96; Octano 2.6; P.V.C. 1.2; "
    "Paja 0.96; Paneles de madera 1.05; Papel 0.96; Parafina 2.6; "
    "Pentano 2.9; Pescado seco 0.7; Petróleo 2.4; Poliamida 1.7; "
    "Policarbonato 1.7; Poliéster 1.4; Polietileno 2.6; Poliuretano 1.4; "
    "Polivinilo acetato 1.2; Propano 2.6; Resina de urea 0.7; Resinas 1.4; "
    "Resinas sintéticas 2.4; Seda 1.2; Sodio 0.5; Sulfuro de carbono 0.7; "
    "Tabaco 0.96; Te 0.96; Tetranidrobenzol 2.6; Tuluol 2.4; "
    "Turba 1.4; Urea 0.5; Vestimentas 0.96-1.2."
)

CHUNKS = [
    {
        "id": "NSR10-J-J_3_4_1", "seccion": "J.3.4.1",
        "titulo": "J.3.4 — Determinación de la resistencia requerida contra fuego. J.3.4.1 — Potencial combustible (carga de fuego)",
        "texto": (
            "J.3.4 — DETERMINACIÓN DE LA RESISTENCIA REQUERIDA CONTRA FUEGO. "
            "J.3.4.1 — POTENCIAL COMBUSTIBLE — El potencial combustible, o carga de fuego, se determinará sumando en "
            "los recintos el producto de la masa de cada objeto, según el uso previsto de la estructura, por el poder "
            "calorífico del respectivo material. Se expresará en términos de energía por unidad de área de piso. "
            "J.3.4.1.1 — Alternativamente, el potencial combustible se podrá expresar en términos de masa equivalente "
            "de la madera por unidad de área de piso. La conversión se hará con base en que 1 kg de madera tiene un "
            "poder calorífico de 18 MJ. "
            "J.3.4.2 — En ausencia de datos analíticos o experimentales sobre los materiales del proyecto, para el "
            "cálculo del potencial combustible el diseñador puede referirse a los valores consignados en las tablas "
            "J.3.4-1 y J.3.4-2."
        ),
    },
    {
        "id": "NSR10-J-J_3_4_tabla1", "seccion": "J.3.4-1",
        "titulo": "Tabla J.3.4-1 — Potencial combustible estimado para materiales distribuidos por unidad de área (MJ/m²)",
        "texto": TABLA_J_3_4_1,
    },
    {
        "id": "NSR10-J-J_3_4_tabla2", "seccion": "J.3.4-2",
        "titulo": "Tabla J.3.4-2 — Potencial combustible estimado para materiales por unidad de masa (MJ/kg)",
        "texto": TABLA_J_3_4_2,
    },
    {
        "id": "NSR10-J-J_3_4_3", "seccion": "J.3.4.3",
        "titulo": "J.3.4.3 — Resistencias al fuego normalizado exigidas en la tabla J.3.4-3, excepción J.3.3.3",
        "texto": (
            "J.3.4.3 — Los elementos estructurales y demás elementos de la construcción deberán tener como mínimo las "
            "resistencias al fuego normalizado exigidas en la tabla J.3.4-3. Se exceptúan de esta exigencia los "
            "contenidos en recintos que cumplan las condiciones estipuladas en el numeral J.3.3.3."
        ),
    },
    {
        "id": "NSR10-J-J_3_4_tabla3", "seccion": "J.3.4-3",
        "titulo": "Tabla J.3.4-3 — Resistencia requerida al fuego normalizado NTC 1480 (ISO 834), en horas, por categoría I/II/III",
        "texto": (
            "Tabla J.3.4-3 — Resistencia requerida al fuego normalizado NTC 1480 (ISO 834), en horas, de elementos de "
            "una edificación, según la categoría dada en J.3.3.1 (Categoría I / II / III). "
            "Muros Cortafuego — 3 / 2 1/2 / 2. "
            "Muros de cerramiento de escaleras, ascensores, buitrones, ductos para basuras y corredores de evacuación — 2 / 2 / 1 1/2. "
            "Muros divisorios entre unidades — 2 / 1 1/2 / 1. "
            "Muros interiores no portantes — 1/2 / 1/4 / sin exigencia. "
            "Columnas, vigas, viguetas, losas, y muros portantes de cualquier material, y estructuras metálicas en celosía — 2 / 1 1/2 / 1. "
            "Cubiertas — 1 / 1 / 1/2. "
            "Escaleras interiores no encerradas con muros — 2 / 1 1/2 / 1."
        ),
    },
    {
        "id": "NSR10-J-J_3_4_3_1", "seccion": "J.3.4.3.1",
        "titulo": "J.3.4.3.1 — Recubrimientos resistentes adicionales avalados y aprobados por la Comisión Asesora Permanente",
        "texto": "J.3.4.3.1 — En caso necesario, para garantizar la resistencia requerida al fuego, podrán utilizarse recubrimientos resistentes adicionales, avalados por entidades de reconocida autoridad y aprobados por la Comisión Asesora Permanente para el Régimen de Construcciones Sismo Resistentes.",
    },
    {
        "id": "NSR10-J-J_3_4_3_2", "seccion": "J.3.4.3.2",
        "titulo": "J.3.4.3.2 — Cuando un elemento cumple varias funciones, debe satisfacer siempre la mayor exigencia de resistencia al fuego",
        "texto": "J.3.4.3.2 — Si a un mismo elemento le correspondieren dos o más resistencias al fuego, por cumplir diversas funciones a la vez, deberá siempre satisfacerse la mayor de las exigencias.",
    },
    {
        "id": "NSR10-J-J_3_4_3_3", "seccion": "J.3.4.3.3",
        "titulo": "J.3.4.3.3 — Resistencia de muros de cerramiento de ascensores solo obligatoria si circula por caja cerrada; puertas exentas pero incombustibles",
        "texto": "J.3.4.3.3 — Las resistencias al fuego que se indican para los muros de cerramiento de ascensores en la tabla J.3.4-3 son obligatorios sólo si el ascensor circula por el interior de una caja cerrada por sus cuatro costados. Las puertas de acceso al ascensor estarán exentas de exigencia al fuego, pero serán de materiales no combustibles, tal como se definen en J.3.2.",
    },
    {
        "id": "NSR10-J-J_3_4_3_4", "seccion": "J.3.4.3.4",
        "titulo": "J.3.4.3.4 — Elementos protegidos por otro elemento interpuesto: el elemento pantalla debe tener al menos la resistencia exigida al elemento protegido",
        "texto": "J.3.4.3.4 — Las resistencias al fuego que se indican para elementos portantes verticales, horizontales o de escaleras en la tabla J.3.4-3, no deben exigirse para aquellos elementos estructurales verticales, horizontales o de escaleras que, por su ubicación en el edificio, queden protegidos de la acción del fuego por otro elemento, que se interponga entre ellos y el fuego. En este caso el elemento interpuesto como pantalla deberá tener, por lo menos, la resistencia al fuego exigida en la tabla J.3.4-3 para el elemento protegido, con excepción de los ingresos a las escaleras exteriores, en las cuales no se exige interponer elemento alguno entre la escalera y el edificio.",
    },
    {
        "id": "NSR10-J-J_3_4_3_5", "seccion": "J.3.4.3.5",
        "titulo": "J.3.4.3.5 — Resistencias para muros no portantes y divisiones exigibles solo cuando separan piso a techo recintos contiguos sin puertas o divisiones de vidrio",
        "texto": "J.3.4.3.5 — Las resistencias al fuego que se indican para los muros no portantes y divisiones en la tabla J.3.4-3, deben exigirse sólo cuando dichos elementos separan piso a techo, recintos contiguos, dentro de una unidad y no contienen puertas o divisiones de vidrio.",
    },
    {
        "id": "NSR10-J-J_3_4_3_6", "seccion": "J.3.4.3.6",
        "titulo": "J.3.4.3.6 — Muros perimetrales: resistencia exigida sin importar si son portantes; divisiones de vidrio, antepechos y dinteles no estructurales exentos",
        "texto": "J.3.4.3.6 — Para muros perimetrales se exigirá el cumplimiento de la resistencia al fuego que corresponda, según la tabla J.3.4-3, ya se trate de elementos portantes o no, cualquiera que sea el destino de la edificación. Las divisiones de vidrio, los antepechos y dinteles no estructurales, estarán exentos de exigencias de resistencia al fuego.",
    },
    {
        "id": "NSR10-J-J_3_4_3_7", "seccion": "J.3.4.3.7",
        "titulo": "J.3.4.3.7 — Elementos portantes con inclinación ≥20° respecto de la vertical se consideran elementos portantes horizontales",
        "texto": "J.3.4.3.7 — Los elementos portantes con 20° o más grados de inclinación respecto de la vertical, serán considerados como elementos portantes horizontales para establecer su resistencia al fuego.",
    },
    {
        "id": "NSR10-J-J_3_4_3_8", "seccion": "J.3.4.3.8",
        "titulo": "J.3.4.3.8 — Escaleras que comunican solo dos pisos dentro de una misma unidad están exentas de exigencias de resistencia al fuego",
        "texto": "J.3.4.3.8 — Las escaleras que comunican solamente dos pisos dentro de una misma unidad estarán exentas de exigencias de resistencia al fuego.",
    },
    {
        "id": "NSR10-J-J_3_5_intro", "seccion": "J.3.5",
        "titulo": "J.3.5 — Evaluación de la provisión de resistencia contra fuego: tiempo equivalente, NTC 1480/ISO 834, NFPA 259, ASTM E119",
        "texto": (
            "J.3.5 — EVALUACIÓN DE LA PROVISIÓN DE RESISTENCIA CONTRA FUEGO EN ELEMENTOS DE EDIFICACIONES. "
            "La resistencia de los elementos estructurales y de compartimentación de las edificaciones se expresa en "
            "unidades de tiempo en función del concepto de tiempo equivalente, o tiempo que tarda un elemento "
            "determinado en alcanzar, en una prueba normalizada de incendio, el máximo calentamiento que "
            "experimentaría en un incendio real. El tiempo equivalente de un elemento podrá determinarse experimental "
            "o analíticamente para el fuego normalizado estipulado en la norma NTC 1480 (ISO 834). Alternativamente se "
            "puede utilizar la norma NFPA 259 — Método de prueba normalizado para el potencial de calor de materiales "
            "de construcción. La determinación experimental se hará por medio de ensayos ajustados a la norma "
            "ASTM E119. "
            "Si se opta por la determinación analítica ésta se hará siguiendo un procedimiento racional de cálculo que "
            "incluya el potencial combustible, el área de piso, la superficie total expuesta, el área de ventilación, "
            "la altura de los muros, sus propiedades conductoras y demás factores pertinentes. Dicho procedimiento "
            "deberá ser avalado por la Comisión Asesora Permanente para el Régimen de Construcciones Sismo "
            "Resistentes. "
            "Alternativamente, la resistencia de elementos puede determinarse con base en el contenido de los "
            "numerales J.3.5.1 a J.3.5.4."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_1", "seccion": "J.3.5.1",
        "titulo": "J.3.5.1 — Elementos restringidos: sin restricción a expansión térmica salvo demostración avalada; barreras corta fuego con sellos resistentes",
        "texto": "J.3.5.1 — ELEMENTOS RESTRINGIDOS — Todo elemento estructural o no estructural debe considerarse sin restricción a la expansión térmica, a menos que el Diseñador de los elementos estructurales o el Diseñador de los elementos no estructurales, según sea el caso, demuestre que los elementos diseñados restringidos a expansión térmica. Dicha demostración debe ser avalada por la Comisión Permanente Asesora del Régimen de Construcciones Sismo Resistentes. Para que un elemento no estructural se considere como barrera corta fuego, debe garantizar la resistencia requerida en J.3.4.3, las dilataciones con respecto a la estructura, deben rellenarse con sellos o materiales resistentes al fuego.",
    },
    {
        "id": "NSR10-J-J_3_5_2_1", "seccion": "J.3.5.2.1",
        "titulo": "J.3.5.2 — Elementos de concreto (guías ACI Comité 216). J.3.5.2.1 — Dimensión mínima de columnas de concreto, Tabla J.3.5-1",
        "texto": (
            "J.3.5.2 — ELEMENTOS DE CONCRETO — Para proveer elementos de concreto de una edificación con las "
            "resistencias al fuego normalizado especificadas en el numeral J.3.4.3 pueden seguirse las guías "
            "establecidas al respecto en documentos de reconocida autoridad, tales como los ofrecidos por el "
            "Comité 216 del American Concrete Institute, ACI (Guide for Determining the fire endurance of concrete "
            "elements), u otras publicaciones similares. "
            "J.3.5.2.1 — Las columnas de concreto que requieran resistencias al fuego iguales o superiores a una "
            "(1) hora deben tener dimensiones que cumplan con los mínimos establecidos en la tabla J.3.5-1. "
            "Tabla J.3.5-1 — Dimensión mínima de columnas de concreto, en mm, para resistencias iguales o mayores a "
            "una (1) hora, según tipo de agregado y resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Silíceo — 200 / 230 / 250 / 310 / 360. Carbonato — 200 / 230 / 250 / 300 / 310. "
            "Liviano — 200 / 220 / 230 / 270 / 310. "
            "Notas: 1. Las dimensiones en estas columnas de la tabla se podrán reducir a 200 mm para columnas "
            "rectangulares de concreto que tengan dos lados paralelos de al menos 950 mm de longitud cada uno. "
            "2. Las dimensiones en esta columna de la tabla se podrán reducir a 250 mm para columnas rectangulares "
            "de concreto que tengan dos lados paralelos al menos de 950 mm de longitud cada uno."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_2_2", "seccion": "J.3.5.2.2",
        "titulo": "J.3.5.2.2 — Espesor mínimo de muros y losas de concreto, Tabla J.3.5-2",
        "texto": (
            "J.3.5.2.2 — Los muros y las losas, incluyendo las de cubierta, de concreto que requieran resistencias al "
            "fuego igual o superior a una (1) hora deben tener espesores que cumplan con los mínimos establecidos en "
            "la tabla J.3.5-2. "
            "Tabla J.3.5-2 — Espesor mínimo de muros y losas de concreto, en mm, para resistencias iguales o mayores a "
            "una (1) hora, según tipo de agregado y resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Silíceo — 90 / 110 / 130 / 160 / 180. Carbonato — 80 / 100 / 120 / 150 / 170. "
            "Finos Livianos — 70 / 80 / 100 / 120 / 140. Gruesos Livianos — 60 / 80 / 90 / 110 / 130. "
            "Nota: Para muros o losas aligerados con perforaciones de sección transversal constante en toda su "
            "longitud, el espesor se calcula dividiendo el área neta de la sección transversal del panel (área de la "
            "sección transversal menos el área de las perforaciones) entre su ancho."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_2_3", "seccion": "J.3.5.2.3",
        "titulo": "J.3.5.2.3 — Recubrimiento mínimo de losas, vigas de concreto reforzado y presforzado, Tablas J.3.5-3 a J.3.5-6",
        "texto": (
            "J.3.5.2.3 — Los elementos de concreto deben tener recubrimientos con espesores mínimos iguales o "
            "mayores que los que se especifican en las tablas J.3.5-3, J.3.5-4, J.3.5-5 y J.3.5-6, pero nunca menores "
            "que los especificados en el Título C. "
            "Tabla J.3.5-3 — Recubrimiento mínimo de losas de concreto reforzado, en mm, según tipo de agregado, "
            "expansión restringida y expansión no restringida, por resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Silíceo — restringida 20/20/20/20/20, no restringida 20/20/30/30/40. "
            "Carbonato — restringida 20/20/20/20/20, no restringida 20/20/20/30/30. "
            "Livianos — restringida 20/20/20/20/20, no restringida 20/20/20/30/30. "
            "Tabla J.3.5-4 — Recubrimiento mínimo de losas de concreto presforzado, en mm, según tipo de agregado, "
            "expansión restringida y expansión no restringida, por resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Silíceo — restringida 20/20/20/20/20, no restringida 30/40/40/60/70. "
            "Carbonato — restringida 20/20/20/20/20, no restringida 30/40/40/50/60. "
            "Livianos — restringida 20/20/20/20/20, no restringida 30/40/40/50/60. "
            "Tabla J.3.5-5 — Recubrimiento mínimo de vigas de concreto reforzado, en mm, según ancho de viga (130/180/≥250 mm), "
            "tipo de restricción y resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Expansión restringida — 130mm: 20/20/20/30/30; 180mm: 20/20/20/20/20; ≥250mm: 20/20/20/20/20. "
            "Expansión no restringida — 130mm: 20/30/30/--/--; 180mm: 20/20/20/40/80; ≥250mm: 20/20/20/30/40. "
            "Nota: los espesores mínimos de recubrimientos para anchos intermedios de vigas pueden determinarse por "
            "interpolación."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_2_3_tabla6", "seccion": "J.3.5-6",
        "titulo": "Tabla J.3.5-6 — Recubrimiento mínimo de vigas de concreto presforzado, en mm",
        "texto": (
            "Tabla J.3.5-6 — Recubrimiento mínimo de vigas de concreto presforzado, en mm, según ancho de viga "
            "(200/≥300 mm), tipo de restricción y resistencia al fuego en horas (1 / 1 1/2 / 2 / 3 / 4): "
            "Expansión restringida — 200mm: 40/40/40/50/70; ≥300mm: 40/40/40/40/50. "
            "Expansión no restringida — 200mm: 40/50/60/130/-- ; ≥300mm: 40/40/50/60/80. "
            "Nota: los espesores mínimos de recubrimientos para anchos intermedios de vigas pueden determinarse por "
            "interpolación."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_3", "seccion": "J.3.5.3",
        "titulo": "J.3.5.3 — Elementos de mampostería: espesor mínimo equivalente, Tablas J.3.5-7 (arcilla) y J.3.5-8 (concreto)",
        "texto": (
            "J.3.5.3 — ELEMENTOS DE MAMPOSTERÍA — Para proveer muros de mampostería con las resistencias al fuego "
            "normalizado especificadas en el numeral J.3.4.3, debe estimarse la resistencia al fuego de la "
            "mampostería, especificada en la tabla J.3.5-7 o en la tabla J.3.5-8 en función de su espesor mínimo "
            "equivalente. "
            "Tabla J.3.5-7 — Espesor mínimo equivalente, eE, de muros de mampostería de arcilla, en mm, en función de "
            "la resistencia al fuego en horas (1 / 2 / 3 / 4): "
            "Maciza — 70 / 100 / 120 / 150. Con perforaciones vacías — 60 / 90 / 110 / 130. "
            "Con perforaciones rellenas — 80 / 110 / 140 / 170. "
            "Tabla J.3.5-8 — Espesor mínimo equivalente, eE, de muros de mampostería de concreto, en mm, en función "
            "de la resistencia al fuego en horas (1 / 2 / 3 / 4), según tipo de agregado: "
            "Pómez o escoria expansiva — 50 / 80 / 100 / 120. Esquisto expansivo, arcilla o pizarra — 70 / 90 / 110 / 130. "
            "Caliza, ceniza o esquisto expansivo — 70 / 100 / 130 / 150. Grava silícea o calcárea — 70 / 110 / 130 / 160."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_3_1_2", "seccion": "J.3.5.3.1",
        "titulo": "J.3.5.3.1 — Ecuación J.3.5-1: espesor equivalente eE = V/(LA). J.3.5.3.2 — Medición del volumen de sólidos por desplazamiento de agua",
        "texto": (
            "J.3.5.3.1 — El espesor mínimo equivalente se calcula con base en la ecuación J.3.5-1. "
            "eE = V / (L·A)  (J.3.5-1). "
            "Donde: eE = espesor equivalente. V = volumen de sólidos de una unidad de mampostería. "
            "L = longitud de la unidad de mampostería. A = altura de la unidad de mampostería. "
            "J.3.5.3.2 — El volumen de sólidos puede calcularse midiendo el volumen de agua desplazado por la unidad "
            "de mampostería al sumergirse en un tanque de agua. Antes de la prueba, la unidad de mampostería se "
            "sumerge en agua por lo menos por 24 horas, se seca por un minuto sobre una rejilla y luego el agua "
            "superficial se remueve con un trapo húmedo. A los dos minutos la unidad se sumerge en el tanque y se "
            "mide cuidadosamente el volumen de agua desplazado, que representa el volumen de sólidos en la unidad."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_4_1_2", "seccion": "J.3.5.4",
        "titulo": "J.3.5.4 — Elementos de acero estructural sin protección: máximo 15 minutos de resistencia; ecuación J.3.5-2 con recubrimiento de concreto",
        "texto": (
            "J.3.5.4 — ELEMENTOS DE ACERO ESTRUCTURAL — Elementos de acero estructural sin ninguna protección no "
            "poseen resistencia contra fuego de más de 15 minutos y sólo son apropiados para uso en edificaciones o "
            "recintos que no requieren protección contra el fuego, de acuerdo con el numeral J.3.3.3. Para "
            "resistencias mayores el acero debe proveerse con productos adheridos para protección contra el fuego. "
            "J.3.5.4.1 — Los productos adheridos para la protección contra el fuego de elementos de acero estructural "
            "deben aplicarse de acuerdo con las indicaciones del fabricante y estar avalados por instituciones "
            "reconocidas internacionalmente para tal efecto. "
            "J.3.5.4.2 — La resistencia contra el fuego de elementos de acero estructural también puede proveerse con "
            "recubrimiento de concreto vaciado en el sitio o con placas prefabricadas de concreto y puede calcularse "
            "mediante la ecuación J.3.5-2. "
            "R = R0(1 + 0.03H)  (J.3.5-2). "
            "Donde: R = resistencia al fuego, en minutos, en condiciones de equilibrio de humedad. "
            "R0 = resistencia al fuego, en minutos, sin contenido de humedad. "
            "H = contenido de humedad, en porcentaje, de equilibrio del concreto, por volumen."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_4_3", "seccion": "J.3.5.4.3",
        "titulo": "J.3.5.4.3 — Ecuación J.3.5-3: resistencia R0 del acero sin humedad protegido con recubrimiento de concreto",
        "texto": (
            "J.3.5.4.3 — La resistencia al fuego, en minutos, R0, cuando el acero se protege con concreto que no "
            "tiene contenido de humedad se calcula mediante la ecuación J.3.5-3. "
            "R0 = 14.74(W/P)^0.7 + 0.552(e^1.6 / kc^0.2)[1 + 6.085×10^-5 · (Ta/dc) · Cc · e · (L+e))^0.8]  (J.3.5-3). "
            "Donde: W = peso promedio de la columna de acero estructural, por unidad de longitud (N/m). "
            "P = perímetro calentado de la columna de acero (mm). e = espesor del recubrimiento de concreto (mm). "
            "kc = conductividad térmica del concreto a temperatura ambiente (J/h/m/°C). "
            "Ta = capacidad térmica del acero de la columna = 46 975 × W (J/h/m/°C). "
            "dc = densidad del concreto (kg/m³). Cc = calor específico del concreto a temperatura ambiente (J/(N.°C)). "
            "L = dimensión interior de un lado del cajón cuadrado de concreto que protege la columna de acero (mm)."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_4_4", "seccion": "J.3.5.4.4",
        "titulo": "J.3.5.4.4 — Propiedades térmicas del concreto normal y liviano, Tabla J.3.5-9",
        "texto": (
            "J.3.5.4.4 — Cuando no se poseen las propiedades térmicas del hormigón concreto que se usará en la obra, "
            "pueden usarse los valores especificados en la tabla J.3.5-9. "
            "Tabla J.3.5-9 — Propiedades térmicas del concreto, según peso del concreto normal y liviano: "
            "Conductividad térmica, kc, W/m/K — Normal 1.644, Liviano 0.606. "
            "Calor específico Cc, J/kg/K — Normal 837.4, Liviano 837.4. "
            "Densidad, dc, kg/m³ — Normal 2400, Liviano 1760. "
            "Contenido de humedad de equilibrio por unidad de volumen, H, % — Normal 4, Liviano 5."
        ),
    },
    {
        "id": "NSR10-J-J_3_5_4_5_6", "seccion": "J.3.5.4.5",
        "titulo": "J.3.5.4.5 — Relación carga/resistencia en secciones huecas rellenas de concreto, Tabla J.3.5-10. J.3.5.4.6 — Perforaciones de escape de gases, Figura J.3.5-1",
        "texto": (
            "J.3.5.4.5 — Cuando se utilizan elementos de acero estructural con secciones huecas rellenas de concreto, "
            "su capacidad estructural debe diseñarse de manera que la relación entre la carga aplicada a compresión y "
            "la resistencia a la compresión del elemento no exceda los valores especificados en la tabla J.3.5-10. "
            "Tabla J.3.5-10 — Relación entre carga aplicada y resistencia a compresión, según resistencia al fuego en "
            "horas: 1 hora — 0.51; 1 1/2 horas — 0.4; 2 horas — 0.36. "
            "J.3.5.4.6 — Cuando se utilizan elementos de acero estructural con secciones huecas rellenas de concreto, "
            "las paredes del tubo deben perforarse, como se ilustra en la figura J.3.5-1, para permitir el escape de "
            "gases calientes durante el evento de un fuego. Los agujeros no deben tener un diámetro inferior a "
            "3.1 mm, ni superior a 13 mm, y deben estar separados a distancias que no excedan 500 mm. Para evitar la "
            "corrosión del tubo los agujeros deben sellarse con un material impermeable pero que se desprenda cuando "
            "se le someta a presión desde el interior. Figura J.3.5-1 — Perforaciones de las secciones de acero "
            "huecas rellenas de concreto: sección cuadrada y sección circular, cada una con agujeros distribuidos "
            "sobre las caras del tubo, señalados en la figura con el rótulo \"Agujeros\"."
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
    if IDS_OBSOLETOS:
        sb.table("nsr10_chunks").delete().in_("id", IDS_OBSOLETOS).execute()
        print(f"Borrados {len(IDS_OBSOLETOS)} chunks obsoletos: {IDS_OBSOLETOS}")

    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")


if __name__ == "__main__":
    main()
