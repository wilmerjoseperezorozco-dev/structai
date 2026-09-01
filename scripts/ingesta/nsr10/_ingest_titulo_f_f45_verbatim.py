"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.5 (Conexiones y Uniones) -- PARCIAL,
F.4.5.1 a F.4.5.4.3 (generalidades + conexiones soldadas completo +
conexiones pernadas completo + conexiones atornilladas hasta cortante,
sin tension). Quinta pieza de F.4/F.5.

F.4.5.1 (Generalidades), F.4.5.2 (Conexiones soldadas -- soldadura de
tapon, de ranura, de filete, abocinada, electrosoldada, rotura en
seccion neta/rezago de cortante), F.4.5.3 (Conexiones pernadas --
cortante/espaciamiento/borde, rotura en seccion neta, aplastamiento,
cortante y tension en pernos), F.4.5.4 parcial (Conexiones atornilladas
-- espaciamiento minimo, distancias al borde, cortante).

Falta de F.4.5 (pendiente para otra sesion): resto de F.4.5.4 (tension
en tornillos, combinacion cortante+tension), F.4.5.5, F.4.5.6
(arrancamiento, mencionado en el texto pero no leido), y todo F.5.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final igual que F.4.2/F.4.3/F.4.4.

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
paginas internas F-372 a F-392 (paginas PDF 72-92), leidas visualmente
pagina por pagina.

Uso: python _ingest_titulo_f_f45_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    # ── F.4.5.1 ─────────────────────────────────────────────────
    {
        "id": "NSR10-F-F_4_5_1_generalidades",
        "seccion": "F.4.5.1 (Generalidades)",
        "titulo": "Diseño de conexiones para transmitir la resistencia requerida actuante sobre los miembros conectados, considerando la excentricidad.",
        "texto": (
            "NSR-10 Título F, Capítulo F.4 — F.4.5 — CONEXIONES Y UNIONES. "
            "F.4.5.1 — GENERALIDADES — Las conexiones se diseñarán para "
            "transmitir la resistencia requerida actuante sobre los "
            "miembros conectados, teniendo en cuenta la excentricidad "
            "cuando sea aplicable."
        ),
    },
    # ── F.4.5.2 — Conexiones soldadas ───────────────────────────
    {
        "id": "NSR10-F-F_4_5_2_1_soldaduras_arco_generalidades",
        "seccion": "F.4.5.2 (Conexiones soldadas — generalidades y soldaduras acanaladas en juntas a tope, ecuaciones F.4.5.2-1 a -3)",
        "titulo": "Alcance (espesor ≤4.76mm), remisión a F.2 para mayor espesor, Tabla F.4.5.2-1 posiciones para soldar, y resistencia nominal de soldadura acanalada.",
        "texto": (
            "F.4.5.2 — CONEXIONES SOLDADAS — El siguiente criterio de "
            "diseño aplicará a conexiones soldadas utilizadas para miembros "
            "estructurales de acero formado en frío en los cuales el "
            "espesor de la parte conectada más delgada es 4.76 mm o menos. "
            "Para el diseño de conexiones soldadas en las cuales el "
            "espesor de la parte conectada más delgada sea mayor a 4.76mm "
            "debe remitirse a las especificaciones establecidas en el "
            "numeral F.2. La sección F.4.4.5 aplicará para los casos donde "
            "se utilicen diafragmas. Las soldaduras de arco en las que al "
            "menos una de las partes conectadas sea de un espesor de 4.76 "
            "mm o menor deben realizarse de acuerdo con las disposiciones "
            "AWS D1.3, a menos que se especifique algo diferente en este "
            "Reglamento. Los soldadores y procedimientos de soldadura "
            "deben estar calificados como se especifica en AWS D1.3. Las "
            "soldaduras por procesos de resistencia deben ser realizadas "
            "de conformidad con los procedimientos dados en AWS C1.1 ó "
            "AWS C1.3. F.4.5.2.1 — Soldaduras acanaladas en juntas a tope "
            "— La resistencia nominal, Pn, de una soldadura acanalada en "
            "una junta a tope, por uno o ambos lados, se determinará de "
            "acuerdo con los incisos (a) o (b), el que sea aplicable. (a) "
            "Para tensión o compresión normales al área efectiva o "
            "paralelas al eje de la soldadura: Pn = L·te·Fy (F.4.5.2-1). "
            "φ = 0.90. (b) Para cortante en el área efectiva, la "
            "resistencia nominal, Pn, será el menor valor calculado de "
            "acuerdo con las ecuaciones F.4.5.2-2 y F.4.5.2-3: "
            "Pn = L·te·0.6Fxx (F.4.5.2-2). φ = 0.80. "
            "Pn = L·te·Fy/√3 (F.4.5.2-3). φ = 0.90. Donde: Pn = "
            "resistencia nominal de la soldadura acanalada. L = longitud "
            "de la soldadura. te = dimensión de la garganta efectiva de la "
            "soldadura acanalada. Fy = esfuerzo de fluencia del acero base "
            "de más baja resistencia. Fxx = resistencia última del "
            "electrodo. F.4.5.2.2 — Soldadura de tapón — Las soldaduras de "
            "tapón permitidas por este Reglamento se usarán para soldar "
            "láminas a miembros de soporte de espesor mayor o para soldar "
            "láminas entre sí, en posición plana."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_2_tapon_generalidades",
        "seccion": "F.4.5.2.2 (Soldadura de tapón — límites de espesor, arandelas, diámetro mínimo)",
        "titulo": "Límite de espesor 3.8mm para poder usar soldadura de tapón, requisito de arandela para lámina delgada, y diámetro efectivo mínimo 9.5mm.",
        "texto": (
            "Estas soldaduras no pueden realizarse cuando el espesor más "
            "delgado a conectar sea mayor de 3.8mm, ni cuando una "
            "combinación de láminas exceda dicho espesor. Se deben "
            "utilizar arandelas para soldar, como se muestra en las "
            "figuras F.4.5.2-1 y F.4.5.2-2, cuando el espesor de lámina "
            "sea menor a 0.711 mm. Las arandelas para soldar deben tener "
            "espesores entre 1.27 y 2.03 mm, con una perforación mínima "
            "de 9.53 mm de diámetro. Las soldaduras lámina a lámina no "
            "requerirán arandelas para soldar. Las soldaduras de tapón "
            "deben especificarse con un diámetro efectivo de área de "
            "fusión mínimo, de, que no puede ser menor a 9.5 mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_2_1_1_tapon_cortante_emin",
        "seccion": "F.4.5.2.2.1.1 (Distancia mínima al borde de soldaduras de tapón — ecuación F.4.5.2-4)",
        "titulo": "emin=P̄/(φFut) y distancia mínima al eje de cualquier soldadura de 1.5d, distancia libre borde-soldadura no menor a 1.0d.",
        "texto": (
            "F.4.5.2.2.1 — Cortante. F.4.5.2.2.1.1 — Distancia mínima al "
            "borde — La distancia medida en la línea de la fuerza, a "
            "partir del eje central de una soldadura, al borde más "
            "cercano de otra soldadura adyacente o al borde final de la "
            "parte conectada hacia la cual se dirige la fuerza, no será "
            "menor que el valor emin determinado con las ecuación "
            "F.4.5.2-4. emin = P̄/(φFut) (F.4.5.2-4). Cuando Fu/Fsy ≥ "
            "1.08: φ = 0.70. Cuando Fu/Fsy < 1.08: φ = 0.60. Donde: "
            "Fu = resistencia última de acuerdo con F.4.1.2.1, F.4.1.2.2 "
            "ó F.4.1.2.3.2. t = espesor combinado total del acero base "
            "(sin incluir recubrimientos) de las láminas involucradas en "
            "la transferencia de cortante arriba del plano de máxima "
            "transferencia de corte. P̄ = resistencia a cortante de "
            "diseño transmitida por la soldadura, P̄=Pu. Fsy = esfuerzo "
            "de fluencia de acuerdo con la sección F.4.1.2.1, F.4.1.2.2 "
            "ó F.4.1.2.3.2. Adicionalmente, la distancia desde el eje de "
            "cualquier soldadura hasta el borde extremo o límite del "
            "miembro conectado no será menor a 1.5d. En ningún caso la "
            "distancia libre entre soldaduras y el borde extremo del "
            "miembro será menor a 1.0d."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_2_1_2_tapon_soporte_mayor_5_9",
        "seccion": "F.4.5.2.2.1.2 (Resistencia a cortante para láminas soldadas a soporte de mayor espesor — ecuaciones F.4.5.2-5 a -9)",
        "titulo": "Pn=menor de 4 valores según da/t (ecuaciones 5-8), y de (diámetro efectivo, ecuación 9).",
        "texto": (
            "F.4.5.2.2.1.2 — Resistencia a cortante para láminas soldadas "
            "a un miembro de soporte de mayor espesor — La resistencia "
            "nominal a cortante, Pn, de cada soldadura de tapón entre la "
            "lámina, ó láminas, y un miembro de apoyo de mayor espesor se "
            "determinará el valor más pequeño entre los incisos (a) o "
            "(b). (a) Pn = (π·de²/4)·0.75·Fxx (F.4.5.2-5). φ = 0.60. (b) "
            "Para (da/t) ≤ 0.815·√(E/Fu): Pn = 2.20·t·da·Fu "
            "(F.4.5.2-6). φ = 0.70. (c) Para 0.815·√(E/Fu) < (da/t) < "
            "1.397·√(E/Fu): Pn = 0.280·[1 + 5.59·√(E/Fu)/(da/t)]·t·da·Fu "
            "(F.4.5.2-7). φ = 0.55. (d) Para (da/t) ≥ 1.397·√(E/Fu): "
            "Pn = 1.40·t·da·Fu (F.4.5.2-8). φ = 0.50. Donde: Pn = "
            "resistencia nominal a cortante de la soldadura de tapón. "
            "de = diámetro efectivo del área de fusión en el plano de la "
            "máxima transferencia de cortante = 0.7d − 1.5t ≤ 0.55d "
            "(F.4.5.2-9). Donde: d = diámetro visible de la superficie "
            "exterior de la soldadura de tapón. t = espesor combinado "
            "total del acero base (sin incluir recubrimientos) de las "
            "láminas involucradas en la transferencia de cortante arriba "
            "del plano de máxima transferencia de corte. Fxx = "
            "resistencia última del electrodo. da = diámetro promedio de "
            "la soldadura de tapón en la mitad del espesor t, donde "
            "da=(d−t) para una lámina o para no más de cuatro láminas "
            "sobrepuestas sobre el miembro de soporte. E = módulo de "
            "elasticidad del acero. Fu = resistencia última determinada "
            "conforme con la sección F.4.1.2.1, F.4.1.2.2 ó F.4.1.2.3.2."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_2_1_3_tapon_lamina_lamina_10",
        "seccion": "F.4.5.2.2.1.3 (Resistencia a cortante para conexiones lámina a lámina — ecuación F.4.5.2-10)",
        "titulo": "Pn=1.65·t·da·Fu, y 3 límites (Fu≤407MPa, Fxx>Fu, 0.70≤t≤1.60mm).",
        "texto": (
            "F.4.5.2.2.1.3 — Resistencia a cortante para conexiones "
            "lámina a lámina — La resistencia nominal a cortante para "
            "cada soldadura entre dos láminas de igual espesor se "
            "determinará de acuerdo con la ecuación F.4.5.2-10. "
            "Pn = 1.65·t·da·Fu (F.4.5.2-10). φ = 0.70. Donde: Pn = "
            "resistencia nominal a cortante de la conexión lámina a "
            "lámina. t = espesor combinado total del acero base (sin "
            "incluir recubrimientos) de las láminas involucradas en la "
            "transferencia de cortante arriba del plano de máxima "
            "transferencia de corte. da = diámetro promedio de la "
            "soldadura de tapón en la mitad del espesor t = (d−t). "
            "Fu = resistencia última de la lámina determinada de acuerdo "
            "con la sección F.4.1.2.1 ó F.4.1.2.2. Adicionalmente, se "
            "deben aplicar los siguientes límites: (1) Fu ≤ 407 MPa "
            "(59 ksi). (2) Fxx > Fu. (3) 0.70 mm ≤ t ≤ 1.60 mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_2_2_tapon_tension_11_12",
        "seccion": "F.4.5.2.2.2 (Tensión — ecuaciones F.4.5.2-11, -12)",
        "titulo": "Pn=menor de 2 valores (ecuaciones 11-12), límites de aplicación, y 50% de reducción para carga excéntrica de levantamiento.",
        "texto": (
            "F.4.5.2.2.2 — Tensión — La resistencia última nominal a "
            "tensión de levantamiento, Pn, de cada soldadura de tapón "
            "cargada concéntricamente y que conecta láminas y miembros "
            "de soporte, se calculará como el menor valor de las "
            "ecuaciones F.4.5.2-11 ó F.4.5.2-12. Pn = (π·de²/4)·Fxx "
            "(F.4.5.2-11). Pn = 0.8·(Fu/Fy)²·t·da·Fu (F.4.5.2-12). Para "
            "aplicación a tableros metálicos y paneles: φ = 0.60. Para "
            "otras aplicaciones: φ = 0.50. Deben aplicarse los "
            "siguientes límites: t·da·Fu ≤ 13.34 kN. emin ≥ d. Fxx ≥ "
            "410 MPa. Fu ≤ 565 MPa (de las láminas conectadas). Fxx > "
            "Fu. Remitirse a la sección F.4.5.2.2.1 para la definición "
            "de las variables. Para soldaduras de tapón cargadas "
            "excéntricamente sujetas a una carga de tensión de "
            "levantamiento, la resistencia última nominal se tomará "
            "como el 50% del valor obtenido en las ecuaciones "
            "anteriores. Para conexiones de láminas múltiples, la "
            "resistencia se determinará mediante la suma de los "
            "espesores de lámina cuando se utilice la ecuación "
            "F.4.5.2-12. La resistencia última nominal en las "
            "conexiones soldadas de traslapo lateral, dentro de un "
            "sistema de tableros, será el 70% de los anteriores "
            "valores. Cuando se demuestre mediante ensayos que un "
            "procedimiento de soldadura proporciona consistentemente "
            "un diámetro efectivo mayor, de, o un diámetro promedio, "
            "da, cuando aplique, se permitirá el uso de este diámetro "
            "más grande siempre y cuando se haya seguido el "
            "procedimiento de soldadura específico para su realización."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_3_ranura_13_15",
        "seccion": "F.4.5.2.3 (Soldadura de ranura — ecuaciones F.4.5.2-13 a -15)",
        "titulo": "Aplicabilidad (2 tipos de junta), Pn=menor de 2 valores (ecuaciones 13-14), ancho efectivo de fusión de (ecuación 15).",
        "texto": (
            "F.4.5.2.3 — Soldadura de ranura — Las soldaduras de ranura "
            "cubiertas por esta especificación se aplicarán solo a los "
            "siguientes tipos de juntas: (a) Entre lámina y un miembro de "
            "apoyo de mayor espesor en posición plana, y (b) Lámina a "
            "lámina en posición plana u horizontal. La resistencia "
            "nominal a cortante, Pn, de una soldadura de ranura se "
            "determinará con el menor valor de las ecuaciones F.4.5.2-13 "
            "y F.4.5.2-14. Pn = (π·de²/4 + L·de)·0.75·Fxx (F.4.5.2-13). "
            "Pn = 2.5·t·Fu·(0.25L + 0.96da) (F.4.5.2-14). φ = 0.60. "
            "Donde: Pn = resistencia nominal a cortante de la soldadura "
            "de ranura. de = ancho efectivo de la ranura en las "
            "superficies fundidas = 0.7d − 1.5t (F.4.5.2-15). Donde: "
            "d = ancho de la soldadura de ranura. L = longitud de la "
            "soldadura de ranura sin incluir los extremos redondeados "
            "(para efectos de cálculo L no excederá 3d). da = ancho "
            "promedio de la soldadura de ranura = (d−t) para una lámina "
            "sencilla o láminas dobles. Fu, Fxx y t = Valores definidos "
            "en la sección F.4.5.2.2.1. La mínima distancia al borde se "
            "determinará tal como se hace con las soldaduras de tapón "
            "de la sección F.4.5.2.2.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_4_filete_16_18",
        "seccion": "F.4.5.2.4 (Soldaduras de filete — ecuaciones F.4.5.2-16 a -19)",
        "titulo": "Pn para carga longitudinal según L/t (ecuaciones 16-17) y carga transversal (ecuación 18), y límite adicional Pn=0.75twLFxx para t>2.54mm (ecuación 19).",
        "texto": (
            "F.4.5.2.4 — Soldaduras de filete — Las soldaduras de filete "
            "cubiertas por esta especificación aplicarán a la soldadura "
            "de juntas en cualquier posición, sea esta lámina a lámina o "
            "lámina a un miembro de acero de mayor espesor. La "
            "resistencia nominal a cortante, Pn, de una soldadura de "
            "filete se determinará de acuerdo con esta sección. (1) Para "
            "carga longitudinal: Para L/t < 25: "
            "Pn = (1 − 0.01L/t)·L·t·Fu (F.4.5.2-16). φ = 0.60. Para "
            "L/t ≥ 25: Pn = 0.75·t·L·Fu (F.4.5.2-17). φ = 0.50. (2) "
            "Para carga transversal: Pn = t·L·Fu (F.4.5.2-18). φ = "
            "0.65. Donde: t = mínimo valor de t1 o t2. Adicionalmente, "
            "para t > 2.54 mm, la resistencia nominal a cortante "
            "determinada de acuerdo con (1) y (2), anteriormente "
            "descritos, no excederá el siguiente valor de Pn: "
            "Pn = 0.75·tw·L·Fxx (F.4.5.2-19). φ = 0.60. Donde: Pn = "
            "resistencia nominal de la soldadura de filete. L = "
            "longitud de la soldadura de filete. Fu y Fxx = valores "
            "definidos en la sección F.4.5.2.2.1. tw = garganta "
            "efectiva = 0.707w1 ó 0.707w2, el que sea menor. Se permite "
            "una garganta efectiva más grande si mediante ensayos se "
            "demuestra que el procedimiento de soldadura que se usará "
            "permite producir de manera consistente un valor mayor de "
            "tw. Donde: w1 y w2 = espesor en la base de la soldadura "
            "(juntas traslapadas ó en T) y w1=t1 en las juntas "
            "traslapadas."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_5_abocinadas_media_v_20",
        "seccion": "F.4.5.2.5 (Soldaduras abocinadas — introducción y media V cargadas transversalmente, ecuación F.4.5.2-20)",
        "titulo": "Aplicabilidad (V/media V, lámina-lámina/lámina-miembro mayor espesor), y Pn=0.833tLFu para media V transversal.",
        "texto": (
            "F.4.5.2.5 — Soldaduras abocinadas — Las soldaduras "
            "abocinadas cubiertas por esta especificación se aplicarán a "
            "juntas soldadas en cualquier posición, ya sea lámina a "
            "lámina para soldaduras abocinadas en V, lámina a lámina "
            "para soldaduras abocinadas en media V o lámina a un miembro "
            "de acero de mayor espesor para soldaduras abocinadas en "
            "media V. La resistencia nominal a cortante, Pn, de una "
            "soldadura abocinada se determinará de acuerdo con esta "
            "sección. (a) Para soldaduras abocinadas en media V cargadas "
            "transversalmente (véase la figura F.4.5.2-12): "
            "Pn = 0.833·t·L·Fu (F.4.5.2-20). φ = 0.60."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_5_abocinadas_longitudinal_21_23",
        "seccion": "F.4.5.2.5 (Soldaduras abocinadas cargadas longitudinalmente — ecuaciones F.4.5.2-21 a -23)",
        "titulo": "Pn según relación tw/t y altura del labio h vs. L (ecuaciones 21-22), y límite adicional para t>2.5mm (ecuación 23).",
        "texto": (
            "(b) Para soldaduras abocinadas cargadas longitudinalmente "
            "(véase las figuras F.4.5.2-13 a F.4.5.2.5-7): (1) Para "
            "t ≤ tw < 2t o si la altura del labio o pestaña, h, es "
            "menor que la longitud de soldadura, L: "
            "Pn = 0.75·t·L·Fu (F.4.5.2-21). φ = 0.55. (2) Para tw ≥ 2t "
            "con la altura del labio o pestaña, h, igual o más grande "
            "que la longitud de soldadura, L: Pn = 1.50·t·L·Fu "
            "(F.4.5.2-22). φ = 0.55. Adicionalmente, para t > 2.5 mm, "
            "la resistencia nominal determinada de acuerdo con (a) y "
            "(b) no excederá el valor de Pn calculado conforme a la "
            "ecuación F.4.5.2-23. Pn = 0.75·tw·L·Fxx (F.4.5.2-23). "
            "φ = 0.60. Donde: Pn = resistencia nominal de la soldadura "
            "abocinada. t = espesor del miembro soldado. L = longitud "
            "de la soldadura. Fu y Fxx = valores que se definen en la "
            "sección F.4.5.2.2.1. h = altura de la pestaña o labio."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_5_garganta_efectiva_tw",
        "seccion": "F.4.5.2.5 (Garganta efectiva tw llenada a ras de superficie o no)",
        "titulo": "tw según tipo de soldadura abocinada llenada a ras (5/16R, 1/2R, 3/8R) o no a ras (0.707w1/w2, el menor).",
        "texto": (
            "tw = garganta efectiva de la soldadura abocinada llenada a "
            "ras de la superficie (véase las figuras F.4.5.2-15 y "
            "F.4.5.2-16): = (5/16)R para soldadura de ranura abocinada "
            "en media V. = (1/2)R cuando R ≤ 12.7 mm para soldadura "
            "abocinada en V. = (3/8)R cuando R > 12.7 mm para soldadura "
            "abocinada en V. = garganta efectiva de la soldadura de "
            "ranura abocinada no a ras de la superficie: 0.707w1 ó "
            "0.707w2, el que sea menor (véase las figuras F.4.5.2-17 y "
            "F.4.5.2-18). Se permite una garganta efectiva más grande "
            "si mediante ensayos se demuestra que el procedimiento de "
            "soldadura que se usará produce de manera consistente un "
            "valor mayor de tw. Donde: R = radio de la superficie de "
            "doblez exterior. w1 y w2 = espesor en la base de la "
            "soldadura (véase las figuras F.4.5.2-17 y F.4.5.2-18)."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_6_electrosoldadas_24_25",
        "seccion": "F.4.5.2.6 (Soldaduras electrosoldadas — ecuaciones F.4.5.2-24, -25)",
        "titulo": "Pn según espesor t en 2 rangos (fórmulas potencial y lineal), φ=0.65.",
        "texto": (
            "F.4.5.2.6 — Soldaduras electrosoldadas — La resistencia "
            "nominal a cortante, Pn, de puntos de soldadura por el "
            "proceso de resistencia (electrosoldadas) se determinará de "
            "acuerdo con esta sección. φ = 0.65. Con t en milímetros y "
            "Pn en kN: Para 0.25 mm ≤ t < 3.6 mm: Pn = 5.51·t^1.47 "
            "(F.4.5.2-24). Para 3.6 mm ≤ t ≤ 4.6 mm: Pn = 7.6t + 8.57 "
            "(F.4.5.2-25). Donde: Pn = resistencia nominal de la "
            "soldadura por electrosoldado. t = espesor de la lámina "
            "exterior más delgada."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_7_rotura_seccion_neta_26",
        "seccion": "F.4.5.2.7 (Rotura en la sección neta de miembros diferentes a láminas planas — rezago de cortante, ecuación F.4.5.2-26)",
        "titulo": "Pn=Ae·Fu con Ae=A·U, y definición de U=1.0 para carga solo por soldaduras transversales o distribuida a todos los elementos.",
        "texto": (
            "F.4.5.2.7 — Rotura en la sección neta de miembros diferentes "
            "a láminas planas (Rezago de cortante) — La resistencia "
            "nominal a tensión de un miembro soldado se determinará de "
            "acuerdo con la sección F.4.3.2. Para rotura y/o fluencia en "
            "la sección neta efectiva de la parte conectada, la "
            "resistencia última nominal de tensión, Pn, se determinará "
            "de acuerdo con la ecuación F.4.5.2-26. Pn = Ae·Fu "
            "(F.4.5.2-26). φ = 0.60. Donde: Fu = resistencia última a "
            "tensión de la parte conectada de acuerdo con la sección "
            "F.4.1.2.1 ó F.4.1.2.3.2. Ae = A·U, área neta efectiva con "
            "U definida como sigue: Cuando la carga se transmite solo "
            "por soldaduras transversales: A = área de los elementos "
            "directamente conectados. U = 1.0. Cuando la carga se "
            "transmite solo con soldaduras longitudinales o con "
            "soldaduras longitudinales en combinación con soldaduras "
            "transversales: A = área bruta del miembro, Ag. U = 1.0 "
            "para miembros en los que la carga se transmite "
            "directamente con todos los elementos de la sección "
            "transversal. En caso contrario, el coeficiente de "
            "reducción U se determinará de acuerdo con los incisos "
            "(a) o (b) a continuación."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_2_7_u_angulo_canal_27_28",
        "seccion": "F.4.5.2.7 (Coeficiente U para miembros en ángulo y en canal — ecuaciones F.4.5.2-27, -28)",
        "titulo": "U=1.0−1.20x̄/L≥0.4 para ángulos, U=1.0−0.36x̄/L≥0.5 para canales, con x̄ (distancia del plano de corte al centroide) y L (longitud de la conexión).",
        "texto": (
            "(a) Para miembros en ángulo: U = 1.0 − 1.20·x̄/L < 0.9. Pero "
            "U ≥ 0.4 (F.4.5.2-27). (b) Para miembros en canal: "
            "U = 1.0 − 0.36·x̄/L < 0.90. Pero U ≥ 0.5 (F.4.5.2-28). "
            "Donde: x̄ = distancia a partir del plano de corte al "
            "centroide de la sección transversal. L = longitud de la "
            "conexión."
        ),
    },
    # ── F.4.5.3 — Conexiones pernadas ───────────────────────────
    {
        "id": "NSR10-F-F_4_5_3_generalidades_perforaciones",
        "seccion": "F.4.5.3 (Conexiones pernadas — generalidades y perforaciones)",
        "titulo": "Alcance (espesor ≤4.76mm), Tabla F.4.5.3-1a de tamaños de perforación, y disposiciones sobre perforaciones agrandadas/ranura en secciones Z traslapadas.",
        "texto": (
            "F.4.5.3 — CONEXIONES PERNADAS — Los requisitos de esta "
            "sección son aplicables a conexiones pernadas para miembros "
            "estructurales de acero formados en frío en los cuáles el "
            "espesor de la parte conectada más delgada sea de 4.76 mm o "
            "menor. Para el diseño de conexiones pernadas en las cuáles "
            "el espesor de la parte conectada más delgada sea mayor a "
            "4.76 mm debe remitirse al Capítulo F.2. Las perforaciones "
            "para pernos no excederán los tamaños especificados en la "
            "tabla F.4.5.3-1, excepto que se permita el uso de "
            "perforaciones de mayor tamaño en placas bases para columnas "
            "o sistemas estructurales conectados a muros de concreto. "
            "Siempre se utilizarán las perforaciones estándar en "
            "conexiones con pernos, excepto que se permite el uso de "
            "perforaciones agrandadas y tipo ranura aprobados por el "
            "diseñador. La longitud de las perforaciones tipo ranura "
            "debe ser normal a la dirección de la carga. Siempre se "
            "deberán instalar arandelas o placas de respaldo por encima "
            "de la lámina sobre las perforaciones agrandadas o tipo "
            "ranura, a menos que se demuestre un comportamiento adecuado "
            "sin estas, mediante ensayos que estén de acuerdo con las "
            "especificaciones del numeral F.4.6. Se permite la no "
            "aplicación de los anteriores requisitos, respecto a la "
            "dirección de la ranura y el uso de arandelas, en los casos "
            "en los que se presenten perforaciones en los traslapos de "
            "miembros en sección Z, sujeto a las siguientes limitaciones: "
            "(1) Pernos de 12.7 mm diámetro únicamente. (2) El tamaño "
            "máximo de perforación tipo ranura es de 14.3 mm x 22.2 mm "
            "realizada en forma vertical. (3) El diámetro máximo de la "
            "perforación agrandada es de 15.9 mm. (4) El espesor nominal "
            "mínimo del miembro es 1.5 mm. (5) El esfuerzo máximo de "
            "fluencia del miembro es 410 MPa. (6) La longitud mínima de "
            "traslapo, medida desde el centro del apoyo hasta el final "
            "del traslapo, es 1.5 veces la altura del miembro."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_pernos_normas_instalacion",
        "seccion": "F.4.5.3 (Normas de pernos, tuercas y arandelas; instalación)",
        "titulo": "10 normas NTC/ASTM aceptadas para pernos/tuercas/arandelas, y requisito de instalación/ajuste para comportamiento satisfactorio.",
        "texto": (
            "Tabla F.4.5.3-1a — Tamaño máximo de perforaciones para "
            "pernos, mm: para diámetro nominal del perno d < 12.7mm, "
            "perforación estándar dh=d+0.8, agrandada dh=d+1.6, ranura "
            "corta (d+0.8)x(d+6.4), ranura larga (d+0.8)x(2.5d). Para "
            "d ≥ 12.7mm: estándar d+1.6, agrandada d+3.2, ranura corta "
            "(d+1.6)x(d+6.4), ranura larga (d+1.6)x(2.5d). Los pernos, "
            "tuercas y arandelas deben cumplir con una de las siguientes "
            "especificaciones: NTC 4028 (ASTM A490M), NTC 4029 (ASTM "
            "A325M), NTC 4031 (ASTM F436M), NTC 4034 (ASTM A307 Tipo A), "
            "NTC 4035 (ASTM A194/A194M), NTC 4479 (ASTM A449, diámetro "
            "inferior a 12.7mm), NTC 4511 (ASTM A563M), NTC 4512 (ASTM "
            "A354 Grado BD, diámetro inferior a 12.7mm), NTC 4701 (ASTM "
            "F959), NTC 4965 (ASTM A563). Cuando se utilice alguna norma "
            "diferente a las presentadas anteriormente los planos deben "
            "indicar claramente el tipo y tamaño de los pernos a ser "
            "empleados y la resistencia nominal supuesta en el diseño. "
            "Los pernos se instalarán y ajustarán para conseguir un "
            "comportamiento satisfactorio."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_1_cortante_espaciamiento_1",
        "seccion": "F.4.5.3.1 (Cortante, espaciamiento y distancia al borde — ecuación F.4.5.3-1)",
        "titulo": "Pn=teFu, distancia mínima entre centros de perforaciones (3 veces diámetro), distancia al borde 1.5d, y límites para perforaciones agrandadas/ranura.",
        "texto": (
            "F.4.5.3.1 — Cortante, espaciamiento y distancia al borde — "
            "La resistencia nominal a cortante, Pn, de la parte "
            "conectada cuando es afectada por el espaciamiento y la "
            "distancia al borde en la dirección de la fuerza aplicada "
            "se calculará de acuerdo con la ecuación F.4.5.3-1. "
            "Pn = t·e·Fu (F.4.5.3-1). (a) Cuando Fu/Fsy ≥ 1.08: "
            "φ = 0.70. (b) Cuando Fu/Fsy < 1.08: φ = 0.60. Donde: "
            "Pn = resistencia nominal de cada perno. e = distancia "
            "medida en la línea de la fuerza a partir del centro de la "
            "perforación estándar al borde más cercano de la "
            "perforación adyacente o al borde de la parte conectada. "
            "t = espesor de la parte conectada más delgada. Fu = "
            "resistencia última de tensión de la parte conectada tal "
            "como se especifica en la sección F.4.1.2.1, F.4.1.2.2 ó "
            "F.4.1.2.3.2. Fsy = esfuerzo de fluencia de la parte "
            "conectada tal como se especifica en la sección F.4.1.2.1, "
            "F.4.1.2.2 ó F.4.1.2.3.2. Adicionalmente, la distancia "
            "mínima entre centros de perforaciones preverá la "
            "suficiente separación para las cabezas de los pernos, "
            "tuercas, arandelas y la llave, pero no debe ser menor a 3 "
            "veces el diámetro nominal del perno, d. Asimismo, la "
            "distancia desde el centro de cualquier perforación "
            "estándar al borde del miembro conectado, u otra frontera, "
            "no será menor a 1.5d. Para perforaciones agrandadas y "
            "perforaciones tipo ranura, la distancia entre bordes de "
            "dos perforaciones adyacentes y la distancia medida desde "
            "el borde de la perforación al borde del miembro conectado, "
            "u otra frontera, en la línea del esfuerzo, no será menor "
            "al valor de e−(dh/2), en donde e es la distancia requerida "
            "usada en la ecuación F.4.5.3-1, y dh es el diámetro de la "
            "perforación estándar definido en la tabla F.4.5.3-1. En "
            "cada caso la distancia libre entre bordes de dos "
            "perforaciones adyacentes será menor a 2d y la distancia "
            "entre el borde de la perforación y el borde extremo del "
            "miembro será menor a d."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_2_rotura_seccion_neta_2_4",
        "seccion": "F.4.5.3.2 (Rotura en la sección neta — sin patrón escalonado, ecuaciones F.4.5.3-2 a -4)",
        "titulo": "Pn=An·Ft, y Ft según arandelas (2 vs 1) y patrón de pernos (perno sencillo/hilera vs múltiples paralelos), con factores de resistencia según tipo de cortante.",
        "texto": (
            "F.4.5.3.2 — Rotura en la sección neta — La resistencia "
            "última nominal a tensión de un miembro conectado con "
            "pernos se determinará de acuerdo con la sección F.4.3.2. "
            "Para rotura en la sección neta efectiva de la parte "
            "conectada, la resistencia última nominal de tensión, Pn, "
            "se determinará de acuerdo con las disposiciones de esta "
            "sección. (a) Para conexiones de láminas planas sin un "
            "patrón de perforaciones escalonadas: Pn = An·Ft "
            "(F.4.5.3-2). (1) Cuando se instalan dos arandelas, una "
            "bajo la cabeza del perno y otra en la tuerca: Para un "
            "perno sencillo, o una hilera sencilla de pernos "
            "perpendicular a la fuerza: Ft = (0.1 + 3d/s)·Fu ≤ Fu "
            "(F.4.5.3-3). Para múltiples pernos en una línea paralela "
            "a la fuerza: Ft = Fu (F.4.5.3-4). Para cortante doble: "
            "φ = 0.65. Para cortante sencillo: φ = 0.55."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_2_rotura_seccion_neta_5_9",
        "seccion": "F.4.5.3.2 (Rotura sin arandela — ecuaciones F.4.5.3-5, -6, y con patrón escalonado — ecuaciones -7, -8, -9)",
        "titulo": "Ft sin arandelas o con solo una (ecuaciones 5-6), Pn con patrón escalonado (ecuación 7) y área neta reducida An (ecuación 8).",
        "texto": (
            "(2) Cuando no se instalan arandelas o se instala solo una "
            "bajo la cabeza del perno, o en la tuerca: Para un perno "
            "sencillo, o una hilera sencilla de pernos perpendicular a "
            "la fuerza: Ft = (2.5d/s)·Fu ≤ Fu (F.4.5.3-5). Para "
            "múltiples pernos en una línea paralela a la fuerza: "
            "Ft = Fu (F.4.5.3-6). φ = 0.65. Donde: An = área neta de "
            "la parte conectada. Ft = esfuerzo nominal de tensión en "
            "la lámina plana. d = diámetro nominal del perno. s = "
            "ancho de la lámina dividido por el número de perforaciones "
            "de pernos en la sección transversal analizada (cuando se "
            "evalúa Ft). Fu = resistencia última de tensión de la "
            "parte conectada tal como se especifica en la sección "
            "F.4.1.2.1, F.4.1.2.2 ó F.4.1.2.3.2. (b) Para conexiones de "
            "láminas planas con un patrón de perforaciones escalonadas: "
            "Pn = An·Ft (F.4.5.3-7). φ = 0.65. Donde: Ft = se determina "
            "de acuerdo con las ecuaciones F.4.5.3-3 a F.4.5.3-6. "
            "An = 0.90·[Ag − nb·dh·t + (Σs'²/4g)·t] (F.4.5.3-8). "
            "Ag = área bruta del miembro. s' = espaciamiento longitudinal "
            "centro a centro de dos perforaciones consecutivas "
            "cualquiera. g = espaciamiento transversal centro a centro "
            "entre ejes de pernos. nb = número de perforaciones de "
            "pernos en la sección transversal analizada. dh = diámetro "
            "de la perforación estándar. Véase la sección F.4.5.3.1 "
            "para la definición de t."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_2_c_diferentes_planas_9_11",
        "seccion": "F.4.5.3.2(c) (Conexiones diferentes a láminas planas — ecuaciones F.4.5.3-9 a -11)",
        "titulo": "Pn=Ae·Fu (ecuación 9) con Ae=An·U, y U para miembros en ángulo/canal con 2+ pernos en la línea de fuerza (ecuaciones 10-11).",
        "texto": (
            "(c) Para conexiones diferentes a láminas planas: "
            "Pn = Ae·Fu (F.4.5.3-9). φ = 0.65. Donde: Ae = An·U, área "
            "neta efectiva con U definido como sigue: U = 1.0 para "
            "miembros en los que la carga se transmite directamente a "
            "todos los elementos de la sección transversal. En caso "
            "contrario, el coeficiente de reducción U se determina como "
            "sigue: (1) Para miembros en ángulo con dos o más pernos en "
            "la línea de la fuerza: U = 1.0 − 1.20·x̄/L < 0.9. Pero "
            "U ≥ 0.4 (F.4.5.3-10). (2) Para miembros en canal con dos o "
            "más pernos en la línea de la fuerza: "
            "U = 1.0 − 0.36·x̄/L < 0.9. Pero U ≥ 0.5 (F.4.5.3-11). "
            "Donde: x̄ = Distancia desde al plano de corte al centroide "
            "de la sección transversal. L = Longitud de la conexión."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_3_aplastamiento_intro_12",
        "seccion": "F.4.5.3.3-F.4.5.3.3.1 (Aplastamiento — sin consideración de deformaciones, ecuación F.4.5.3-12)",
        "titulo": "Pn=Cmf·d·t·Fu, con C de Tabla F.4.5.3-2 y mf de Tabla F.4.5.3-3.",
        "texto": (
            "F.4.5.3.3 — Aplastamiento — La resistencia nominal por "
            "aplastamiento en una conexión con pernos se determinará de "
            "acuerdo con las secciones F.4.5.3.3.1 y F.4.5.3.3.2. Para "
            "condiciones que no se incluyan, la resistencia de diseño "
            "por aplastamiento de las conexiones con pernos debe ser "
            "determinada mediante ensayos. F.4.5.3.3.1 — Resistencia "
            "sin consideración de deformaciones de la perforación — "
            "Cuando la deformación alrededor de las perforaciones de "
            "los pernos no es una consideración de diseño, la "
            "resistencia nominal al aplastamiento, Pn, de la lámina "
            "conectada por cada perno cargado debe determinarse de "
            "acuerdo con la ecuación F.4.5.3-12. Pn = C·mf·d·t·Fu "
            "(F.4.5.3-12). φ = 0.60. Donde: C = factor de aplastamiento, "
            "determinado de acuerdo con la tabla F.4.5.3-2. mf = factor "
            "de modificación para el tipo de conexión por aplastamiento, "
            "el cual se determinará de acuerdo con la tabla F.4.5.3-3. "
            "d = diámetro nominal del perno. t = espesor de la lámina "
            "sin recubrimiento. Fu = resistencia última de la lámina "
            "tal como se define en la sección F.4.1.2.1 ó F.4.1.2.2."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_3_tablas_c_mf",
        "seccion": "F.4.5.3.3 (Tabla F.4.5.3-2 factor C, y Tabla F.4.5.3-3 factor mf)",
        "titulo": "3 rangos de C según d/t (3.0, 4−0.1(d/t), 1.8), y 3 valores de mf según tipo de conexión (1.00 cortante sencillo, 0.75 sin arandelas, 1.33 lámina interna).",
        "texto": (
            "Tabla F.4.5.3-2 — Factor de aplastamiento C: espesor de la "
            "parte conectada, t, entre 0.61 y 4.76mm: para relación "
            "d/t < 10, C=3.0. Para 10 ≤ d/t ≤ 22, C = 4 − 0.1·(d/t). "
            "Para d/t > 22, C=1.8. Tabla F.4.5.3-3 — Factor de "
            "modificación, mf, para conexiones por aplastamiento: "
            "cortante sencillo y láminas exteriores de conexión en "
            "cortante doble con arandelas bajo la cabeza del perno y la "
            "tuerca, mf=1.00. Cortante sencillo y láminas exteriores de "
            "conexión en cortante doble sin arandelas bajo la cabeza "
            "del perno y tuerca, o con solo una arandela, mf=0.75. "
            "Lámina interna de conexión en cortante doble con y sin "
            "arandelas, mf=1.33."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_3_2_deformaciones_13",
        "seccion": "F.4.5.3.3.2 (Resistencia con consideración de deformaciones — ecuación F.4.5.3-13)",
        "titulo": "Pn=(4.64αt+1.53)dtFu, con α=0.0394 (sistema internacional), limitado por F.4.5.3.3.1.",
        "texto": (
            "F.4.5.3.3.2 — Resistencia con consideración de "
            "deformaciones de la perforación — Cuando la deformación "
            "alrededor de las perforaciones de pernos es una "
            "consideración de diseño, la resistencia nominal al "
            "aplastamiento, Pn, se calculará de acuerdo con la ecuación "
            "F.4.5.3-13. Adicionalmente, la resistencia de diseño no "
            "debe exceder la resistencia de diseño obtenida de acuerdo "
            "con la sección F.4.5.3.3.1. Pn = (4.64·α·t + 1.53)·d·t·Fu "
            "(F.4.5.3-13). φ = 0.65. α = 0.0394 para el sistema "
            "internacional de unidades (t en milímetros). Remitirse a "
            "la sección F.4.5.3.3.1 para la definición de las otras "
            "variables."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_4_cortante_tension_pernos_14_15",
        "seccion": "F.4.5.3.4 (Cortante y tensión en pernos — ecuaciones F.4.5.3-14, -15)",
        "titulo": "Pn=AbFn (ecuación 14), Fn según cortante/tensión solos (Tabla F.4.5.3-4) o combinados (F'nt, ecuación 15).",
        "texto": (
            "F.4.5.3.4 — Cortante y tensión en pernos — La resistencia "
            "nominal del perno, Pn, resultante del cortante, la tensión "
            "o una combinación de cortante y tensión, se calculará de "
            "acuerdo con lo estipulado en esta sección. Pn = Ab·Fn "
            "(F.4.5.3-14). Donde: Ab = área bruta de la sección "
            "transversal del perno. Fn = la resistencia nominal en MPa "
            "se determina de acuerdo con (a) o (b) como sigue: (a) "
            "Cuando los pernos están sujetos solo a cortante o tensión, "
            "no combinadas, Fn se obtendrá mediante Fnv ó Fnt en la "
            "tabla F.4.5.3-4. Los correspondientes factores de "
            "resistencia, φ, se muestran en la tabla F.4.5.3-4. Debe "
            "tenerse en cuenta la resistencia al arrancamiento de la "
            "lámina conectada a la cabeza del perno, tuerca o arandela, "
            "cuando el perno está sometido a tensión. Véase la sección "
            "F.4.5.6.2. (b) Cuando los pernos están sujetos a una "
            "combinación de cortante y tensión, Fn, se obtiene a partir "
            "de F'nt en la siguiente ecuación F.4.5.3-15 como sigue: "
            "F'nt = 1.3·Fnt − (Fnt/(φFnv))·fv ≤ Fnt (F.4.5.3-15). "
            "Donde: F'nt = esfuerzo nominal a tensión modificado para "
            "incluir los efectos del esfuerzo cortante requerido, MPa. "
            "Fnt = esfuerzo nominal a tensión de la tabla F.4.5.3-4. "
            "Fnv = esfuerzo cortante nominal de la tabla F.4.5.3-4. "
            "fv = esfuerzo cortante requerido, MPa. φ = factor de "
            "resistencia para cortante tomado de la tabla F.4.5.3-4. "
            "Adicionalmente, el esfuerzo cortante requerido, fv, no "
            "excederá el esfuerzo cortante de diseño, φFnv, del perno."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_3_4_tabla4_resumen",
        "seccion": "F.4.5.3.4 (Resumen de la Tabla F.4.5.3-4 — resistencias nominales por tipo de perno)",
        "titulo": "Resistencias últimas a tensión (φ=0.75) y a cortante (φ=0.65) para pernos A307/A325/A354/A449/A490 según diámetro y si la rosca está incluida/excluida del plano de corte.",
        "texto": (
            "Tabla F.4.5.3-4 — Resistencia nominal a tensión y cortante "
            "para pernos: Pernos A307 Grado A (6.4≤d≤12.7mm): Fnt=279 "
            "MPa, Fnv=165 MPa. A307 Grado A (d≥12.7mm): Fnt=310, "
            "Fnv=186. A325, rosca incluida en planos de corte: Fnt=621, "
            "Fnv=372. A325, rosca excluida: Fnt=621, Fnv=496. A354 "
            "Grado BD (6.4-12.7mm), rosca incluida: Fnt=696, Fnv=407. "
            "A354 Grado BD, rosca excluida: Fnt=696, Fnv=621. A449 "
            "(6.4-12.7mm), rosca incluida: Fnt=558, Fnv=324. A449, "
            "rosca excluida: Fnt=558, Fnv=496. A490, rosca incluida: "
            "Fnt=776, Fnv=465. A490, rosca excluida: Fnt=776, Fnv=621. "
            "Factor de resistencia φ para tensión: 0.75, para todos. "
            "Factor de resistencia φ para cortante: 0.65, para todos. "
            "En la tabla F.4.5.3-4, la resistencia a cortante aplicará "
            "a pernos en perforaciones limitadas por los requisitos de "
            "la tabla F.4.5.3-1. Las arandelas y placas de respaldo se "
            "instalarán sobre las perforaciones tipo ranura larga y la "
            "capacidad de esta conexión se determinará mediante "
            "ensayos de carga de acuerdo con el numeral F.4.6."
        ),
    },
    # ── F.4.5.4 — Conexiones atornilladas (parcial) ─────────────
    {
        "id": "NSR10-F-F_4_5_4_generalidades",
        "seccion": "F.4.5.4 (Conexiones atornilladas — generalidades)",
        "titulo": "Alcance (2mm≤d≤6.35mm), rosca por laminación, remisión a F.4.3.2 y F.4.4.5, factor de resistencia general φ=0.50, y notación de variables.",
        "texto": (
            "F.4.5.4 — CONEXIONES ATORNILLADAS — Todos los requisitos de "
            "esta sección aplicarán a tornillos con 2 mm ≤ d ≤ 6.35 mm. "
            "Los tornillos deben tener una rosca realizada por "
            "laminación por corte, con o sin punta auto-perforante. Los "
            "tornillos deben instalarse y ajustarse de acuerdo con las "
            "recomendaciones del fabricante. Las resistencias nominales "
            "de las conexiones atornilladas también se deben limitar de "
            "acuerdo con la sección F.4.3.2. Para aplicaciones en "
            "diafragmas se debe referirá la sección F.4.4.5. El "
            "siguiente factor de resistencia debe utilizarse para "
            "determinar la resistencia de diseño. φ = 0.50. "
            "Alternativamente, se permite el uso de valores de diseño "
            "para una aplicación en particular, basados en ensayos, con "
            "un factor de resistencia, φ, determinado de acuerdo a las "
            "disposiciones del numeral F.4.6. La siguiente notación "
            "aplicará a esta sección: d = diámetro nominal del "
            "tornillo. dh = diámetro de la cabeza del tornillo ó "
            "diámetro de la arandela en los tornillos de cabeza "
            "hexagonal con arandela integrada. dw = diámetro de la "
            "arandela de acero. d'w = diámetro efectivo de resistencia "
            "al desgarramiento del material en contacto con la cabeza "
            "o arandela. Pns = resistencia nominal a cortante del "
            "tornillo. Pss = resistencia nominal a cortante del "
            "tornillo suministrada por el fabricante o determinada por "
            "ensayos en un laboratorio independiente. Pnot = resistencia "
            "nominal al desgarramiento para cada tornillo. Pnov = "
            "resistencia nominal al desgarramiento del material en "
            "contacto con la cabeza y la arandela, si existe, para cada "
            "tornillo. Pts = resistencia nominal a la tensión del "
            "tornillo suministrada por el fabricante o determinada por "
            "ensayos en un laboratorio independiente. t1 = espesor del "
            "miembro en contacto con la cabeza del tornillo o arandela. "
            "t2 = espesor del miembro que no está en contacto con la "
            "cabeza del tornillo o arandela. tc = el menor valor entre "
            "la profundidad de penetración y el espesor t2. Fu1 = "
            "resistencia última del miembro en contacto con la cabeza "
            "del tornillo o arandela. Fu2 = resistencia última del "
            "miembro que no está en contacto con la cabeza del tornillo "
            "o arandela."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_1_2_espaciamiento_borde",
        "seccion": "F.4.5.4.1-F.4.5.4.2 (Espaciamiento mínimo, y distancias mínimas al borde y extremos)",
        "titulo": "Distancia mínima entre centros de tornillos (3d) y desde el centro al borde (1.5d), con remisión a F.4.5.4.3.2 si la distancia final es paralela a la fuerza.",
        "texto": (
            "F.4.5.4.1 — Espaciamiento mínimo — La distancia entre "
            "centros de tornillos no será menor a 3d. F.4.5.4.2 — "
            "Distancias mínimas al borde y extremos — La distancia "
            "desde el centro de un sujetador al borde de cualquier "
            "parte no será menor a 1.5d. Si la distancia final es "
            "paralela a la fuerza sobre el tornillo, la resistencia "
            "nominal a cortante por tornillo, Pns, se limitará por la "
            "sección F.4.5.4.3.2."
        ),
    },
    {
        "id": "NSR10-F-F_4_5_4_3_1_cortante_inclinacion_1_5",
        "seccion": "F.4.5.4.3.1 (Cortante — conexión limitada por inclinación y aplastamiento, ecuaciones F.4.5.4-1 a -5)",
        "titulo": "Pns=menor valor según t2/t1≤1.0 (ecuaciones 1-3) o ≥2.5 (ecuaciones 4-5), interpolación lineal en el rango intermedio.",
        "texto": (
            "F.4.5.4.3 — Cortante. F.4.5.4.3.1 — Conexión a cortante "
            "limitada por inclinación y aplastamiento — La resistencia "
            "nominal a cortante por tornillo, Pns, se determinará de "
            "acuerdo con esta sección. Para t2/t1 ≤ 1.0, Pns se tomará "
            "como el menor valor de: Pns = 4.2·(t2³·d)^0.5·Fu2 "
            "(F.4.5.4-1). Pns = 2.7·t1·d·Fu1 (F.4.5.4-2). "
            "Pns = 2.7·t2·d·Fu2 (F.4.5.4-3). Para t2/t1 ≥ 2.5, Pns se "
            "tomará como el menor valor de: Pns = 2.7·t1·d·Fu1 "
            "(F.4.5.4-4). Pns = 2.7·t2·d·Fu2 (F.4.5.4-5). Para "
            "1.0 < t2/t1 < 2.5, Pns se calculará mediante interpolación "
            "lineal entre los dos casos presentados anteriormente. "
            "F.4.5.4.3.2 — Conexión a cortante limitada por la "
            "distancia al borde de la parte conectada — La resistencia "
            "nominal a cortante por tornillo, Pns, no excederá la "
            "calculada de acuerdo con la ecuación F.4.5.4-6, donde la "
            "distancia al borde de la parte conectada es paralela a la "
            "línea de la fuerza aplicada."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.5 (parcial) cargados.")


if __name__ == "__main__":
    main()
