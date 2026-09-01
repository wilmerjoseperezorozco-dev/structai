"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.4 (Miembros Armados y Sistemas
Estructurales) completo, en verbatim real. Cuarta pieza de F.4/F.5
(F.4.1, F.4.2, F.4.3 ya cerrados en sesiones anteriores).

F.4.4 -- MIEMBROS ARMADOS Y SISTEMAS ESTRUCTURALES: F.4.4.1 (Secciones
armadas -- vigas compuestas de 2 C espalda con espalda, miembros a
compresion compuestos, espaciamiento de conectores con cubreplacas),
F.4.4.2 (Sistemas mixtos), F.4.4.3 (Arriostramiento lateral y
estabilidad -- vigas/columnas simetricas, secciones C/Z, arriostramiento
de miembros en compresion), F.4.4.4 (Construccion de entramados
livianos), F.4.4.5 (Construccion de diafragmas, Tabla F.4.4.5-1),
F.4.4.6 (Sistemas de muros y cubiertas metalicas -- correas/largueros,
Standing Seam, arriostramiento y anclaje con 3 tablas de coeficientes).

CHUNKS escritos en piezas chicas desde el principio, re-trocheadas
programaticamente al final igual que F.4.2/F.4.3 (ver
_resplit_titulo_f_f44_por_limite_tokens.py) -- no confiar en el conteo
manual de caracteres, medir con len() real.

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
paginas internas F-358 a F-371 (paginas PDF 58-71), leidas visualmente
pagina por pagina.

Uso: python _ingest_titulo_f_f44_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    # ── F.4.4.1 — Secciones armadas ────────────────────────────
    {
        "id": "NSR10-F-F_4_4_1_1_vigas_dos_c_espalda_1_2",
        "seccion": "F.4.4.1.1 (Miembros a flexión compuestos por dos secciones C espalda con espalda)",
        "titulo": "Espaciamiento máximo smax entre soldaduras/conectores (ecuación F.4.4.1-1) y resistencia de conexión Ts (ecuación F.4.4.1-2).",
        "texto": (
            "NSR-10 Título F, Capítulo F.4 — F.4.4 — MIEMBROS ARMADOS Y "
            "SISTEMAS ESTRUCTURALES. F.4.4.1 — SECCIONES ARMADAS. F.4.4.1.1 "
            "— Miembros a flexión compuestos por dos secciones C espalda con "
            "espalda — La máxima separación longitudinal entre soldaduras u "
            "otros conectores, smax, que unen dos secciones C para formar "
            "una sección I será: smax = L/6 ≤ 2gTs/mq (F.4.4.1-1). Donde: "
            "L = luz de la viga. g = distancia vertical entre las dos líneas "
            "de conexiones más cercanas a las aletas superior e inferior. "
            "Ts = resistencia de diseño de la conexión a tensión (véase "
            "F.4.5). m = distancia desde el centro de cortante de una sola "
            "sección C al plano medio del alma. q = carga de diseño sobre la "
            "viga para espaciamiento de los conectores. La carga, q, se "
            "obtendrá dividiendo la magnitud de las cargas concentradas o "
            "reacciones mayoradas entre la longitud de apoyo. En vigas "
            "diseñadas para una carga uniformemente distribuida, q, se "
            "tomará igual a tres veces la carga uniformemente distribuida, "
            "basándose en las combinaciones de carga críticas. Si la "
            "longitud de apoyo de una carga concentrada o reacción es más "
            "pequeña que el espacio entre soldaduras, s, la resistencia de "
            "diseño de las soldaduras o conexiones más cercanas a la carga o "
            "reacción se calculará como sigue: Ts = Ps·m/(2g) (F.4.4.1-2). "
            "Donde: Ps = carga concentrada o reacción basada en las "
            "combinaciones de carga crítica."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_1_1_espaciamiento_metodos",
        "seccion": "F.4.4.1.1 (Métodos alternativos de espaciamiento de conexiones)",
        "titulo": "2 métodos permitidos cuando un espaciamiento uniforme resulta antieconómico: variar el espaciamiento, o colocar cubreplacas de refuerzo.",
        "texto": (
            "El máximo espaciamiento permisible de las conexiones, smax, "
            "dependerá de la intensidad de carga aplicada directamente sobre "
            "la conexión. Por lo tanto, si se desea utilizar un espaciamiento "
            "uniforme sobre toda la longitud de la viga, este se determinará "
            "en el punto de máxima intensidad de carga local. En casos donde "
            "este procedimiento resulte en un espaciamiento muy cercano y "
            "antieconómico, se permitirá la adopción de cualquiera de los "
            "siguientes métodos: (a) El espaciamiento de la conexión varía a "
            "lo largo de la viga de acuerdo con la variación de la "
            "intensidad de la carga. (b) Colocación de cubreplacas de "
            "refuerzo soldadas a las aletas en los puntos donde se presentan "
            "las cargas concentradas. La resistencia a cortante de diseño de "
            "las conexiones que unan estas placas a las aletas se usará para "
            "el valor de Ts y g se tomará como la altura de la viga."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_1_2_miembros_compresion_dos_contacto",
        "seccion": "F.4.4.1.2 (Miembros a compresión compuestos por dos secciones en contacto)",
        "titulo": "Modificación de resistencia axial cuando el modo de pandeo genera cortante entre conectores: (KL/r)m combinado (ecuación F.4.4.1-3).",
        "texto": (
            "F.4.4.1.2 — Miembros a compresión compuestos por dos secciones "
            "en contacto — Para miembros en compresión compuestos de dos "
            "secciones en contacto, la resistencia axial de diseño se "
            "determinará de acuerdo con la sección F.4.3.4.1(a) con la "
            "siguiente modificación: Si el modo de pandeo implica una "
            "deformación relativa que produce fuerzas cortantes en los "
            "conectores entre secciones individuales, KL/r se reemplaza por "
            "(KL/r)m calculado como sigue: (KL/r)m = √((KL/r)o² + (a/ri)²) "
            "(F.4.4.1-3). Donde: (KL/r)o = relación de esbeltez total de la "
            "sección completa alrededor del eje del miembro armado. a = "
            "espaciamiento del sujetador intermedio, punto o cordón de "
            "soldadura. ri = radio de giro mínimo del área transversal total "
            "no reducida de una sección individual en un miembro armado. "
            "Remitirse a la sección F.4.3.4.1.1 para definición de los otros "
            "símbolos."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_1_2_limites_1_3",
        "seccion": "F.4.4.1.2 (3 requisitos del sujetador/soldadura y su espaciamiento)",
        "titulo": "Límite del espaciamiento a/ri, conexión de extremos, y capacidad de transmisión de fuerza del 2.5% de la resistencia axial nominal.",
        "texto": (
            "Adicionalmente, la resistencia del sujetador y su espaciamiento "
            "deben satisfacer lo siguiente: (1) El espaciamiento del "
            "sujetador intermedio, del punto o cordón de soldadura, a, está "
            "limitado de tal forma que a/ri no excede la mitad de la "
            "relación de esbeltez que gobierne del miembro armado. (2) Los "
            "extremos de un miembro en compresión armado estarán conectados "
            "por soldadura con longitud no menor que el máximo ancho del "
            "miembro o por conectores espaciados longitudinalmente no más de "
            "cuatro (4) veces su diámetro sobre una distancia igual a 1.5 "
            "veces el ancho máximo del miembro. (3) Los sujetadores "
            "intermedios o soldaduras en cualquier punto de unión del "
            "miembro longitudinal serán capaces de transmitir una fuerza en "
            "cualquier dirección igual al 2.5% de la resistencia nominal "
            "axial del miembro armado."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_1_2_1_cajon_dos_c_4_5",
        "seccion": "F.4.4.1.2.1 (Miembros a compresión en sección cajón compuestos por dos secciones C en contacto)",
        "titulo": "(KL/r)m según a/ri≷50 (ecuaciones F.4.4.1-4, -5), y límite de espaciamiento a≤300mm.",
        "texto": (
            "F.4.4.1.2.1 — Miembros a compresión en sección cajón compuestos "
            "por dos secciones C en contacto — Para miembros en sección "
            "cajón, formados a partir de dos secciones C en contacto a "
            "través de sus pestañas o labios rigidizadores y unidas por "
            "cordones intermitentes de soldadura, se tiene que: Cuando "
            "a/ri > 50: (KL/r)m = √((KL/r)o² + (a/ri − 50)²) (F.4.4.1-4). "
            "Cuando a/ri ≤ 50: (KL/r)m = (KL/r)o (F.4.4.1-5). Todas las "
            "variables se definen y limitan en la sección F.4.4.1.2. El "
            "valor de a no excederá los 300 mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_1_3_espaciamiento_cubreplacas",
        "seccion": "F.4.4.1.3 (Espaciamiento de conectores en secciones con cubreplacas)",
        "titulo": "3 límites del espaciamiento s (transmisión de cortante, condición b con espesor, y condición c con ancho plano triplicado) y las excepciones.",
        "texto": (
            "F.4.4.1.3 — Espaciamiento de conectores en secciones con "
            "cubreplacas — El espaciamiento, s, en la línea del esfuerzo, de "
            "soldaduras, remaches o pernos que conectan una cubreplaca, "
            "lámina o un rigidizador no integral en compresión a otro "
            "elemento no excederá (a), (b) y (c) como sigue: (a) Al "
            "espaciamiento, s, requerido para transmitir el cortante entre "
            "las partes conectadas sobre la base de la resistencia de diseño "
            "por conexión especificado en cualquier otra parte de este "
            "Título. (b) 1.16t·√(E/fc). Donde: t = espesor de cubreplaca o "
            "lámina. fc = esfuerzo de compresión para la carga nominal en la "
            "cubreplaca o lámina. (c) Tres veces el ancho plano, w, del "
            "elemento más angosto en compresión no rigidizado tributario a "
            "las conexiones, pero no tiene que ser menor que 1.11t·√(E/Fy) "
            "si w/t < 0.50·√(E/Fy), ó 1.33t·√(E/Fy) si w/t ≥ 0.50·√(E/Fy), a "
            "menos que se requiera un menor espaciamiento en los incisos (a) "
            "o (b) especificados anteriormente. En el caso de soldaduras "
            "intermitentes de filete paralelas a la dirección del esfuerzo, "
            "el espaciamiento se tomará como la distancia libre entre "
            "soldaduras más 12.7 mm. En todos los otros casos, el "
            "espaciamiento se tomará como la distancia centro a centro entre "
            "las conexiones. Excepción: Los requerimientos de esta sección "
            "no aplican a placas o láminas que actúan solo en función de "
            "cubiertas o material para traslape y no se consideren como "
            "elementos portantes."
        ),
    },
    # ── F.4.4.2 — Sistemas mixtos ──────────────────────────────
    {
        "id": "NSR10-F-F_4_4_2_sistemas_mixtos",
        "seccion": "F.4.4.2 (Sistemas mixtos)",
        "titulo": "Diseño de miembros de acero formado en frío en conjunto con otros materiales, según este Reglamento y la especificación aplicable a cada material.",
        "texto": (
            "F.4.4.2 — SISTEMAS MIXTOS — El diseño de miembros en sistemas "
            "mixtos que utilicen componentes de acero formado en frío en "
            "conjunto con otros materiales se hará conforme a lo estipulado "
            "en este Reglamento y cualquier otra especificación aplicable al "
            "otro material."
        ),
    },
    # ── F.4.4.3 — Arriostramiento lateral y estabilidad ────────
    {
        "id": "NSR10-F-F_4_4_3_1_2_intro_vigas_c_z",
        "seccion": "F.4.4.3.1-F.4.4.3.2 (Arriostramiento lateral y estabilidad — vigas/columnas simétricas, y vigas en sección C y Z)",
        "titulo": "Requisitos generales de riostras (resistencia y rigidez), y aplicabilidad de las disposiciones de arriostramiento torsional para secciones C/Z sin aleta conectada a panel.",
        "texto": (
            "F.4.4.3 — ARRIOSTRAMIENTO LATERAL Y ESTABILIDAD — Las riostras "
            "deben diseñarse para restringir la flexión lateral o torsión de "
            "una viga o columna cargada, y para evitar el arrugamiento local "
            "en los puntos de fijación. F.4.4.3.1 — Vigas y columnas "
            "simétricas — Las riostras y los sistemas de arriostramiento, "
            "incluyendo las conexiones, se diseñarán considerando los "
            "requerimientos de resistencia y rigidez. F.4.4.3.2 — Vigas en "
            "sección C y sección Z — Las siguientes disposiciones de "
            "arriostramiento para restringir la torsión en secciones C y "
            "secciones Z que se utilicen como vigas cargadas en el plano del "
            "alma se aplicarán solamente cuando ninguna aleta esté conectada "
            "a un tablero metálico o panel de tal manera que restrinja de "
            "manera efectiva la deflexión lateral de la aleta conectada. "
            "Cuando solo la aleta superior esté conectada de esta forma debe "
            "remitirse a la sección F.4.4.6.3.1. Cuando ambas aletas están "
            "conectadas de manera que efectivamente se restrinja la "
            "deflexión lateral no es necesario más arriostramiento."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_2_1_riostras_intro",
        "seccion": "F.4.4.3.2.1 (Ninguna aleta conectada a un panel — riostras intermedias, definición de PL1/PL2)",
        "titulo": "Cada riostra intermedia se diseña con resistencias PL1 y PL2 sobre las aletas superior e inferior, según el sistema de coordenadas x-y de la figura F.4.4.3-1.",
        "texto": (
            "F.4.4.3.2.1 — Ninguna aleta conectada a un panel que contribuya "
            "a la resistencia y estabilidad de la sección C o sección Z — "
            "Cada riostra intermedia en las aletas superior e inferior de "
            "miembros en sección C o Z se diseñará con una resistencia PL1 y "
            "PL2, donde PL1 es la fuerza de riostra requerida sobre la "
            "aleta, en el cuadrante con ambos ejes x y y positivos, y PL2 es "
            "la fuerza de riostra sobre la otra aleta. El eje x será el eje "
            "centroidal perpendicular al alma y el eje y el eje centroidal "
            "paralelo al alma. Las coordenadas x y y se orientarán de tal "
            "forma que una de las aletas esté localizada en el cuadrante "
            "donde ambos ejes, x y y, son positivos. Remitirse a la figura "
            "F.4.4.3-1 para la esquematización de los sistemas de "
            "coordenadas y direcciones positivas de las fuerzas."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_2_1_a_cargas_uniformes_1_5",
        "seccion": "F.4.4.3.2.1(a) (Para cargas uniformes — ecuaciones F.4.4.3-1 a -5)",
        "titulo": "PL1, PL2 para cargas uniformes (ecuaciones 1-2), casos especiales cuando la carga actúa en el plano del alma para secciones C y Z (ecuaciones 3-4), y factor K' (ecuación 5).",
        "texto": (
            "(a) Para cargas uniformes: PL1 = 1.5·[Wy·K' − (Wx/2) + "
            "(Mz/d)] (F.4.4.3-1). PL2 = 1.5·[Wy·K' − (Wx/2) − (Mz/d)] "
            "(F.4.4.3-2). Cuando la carga uniforme, W, actúa a través del "
            "plano del alma, entonces Wy=W: PL1 = −PL2 = 1.5·(m/d)·W para "
            "secciones C (F.4.4.3-3). PL1 = PL2 = 1.5·(Ixy/(2Ix))·W para "
            "secciones Z (F.4.4.3-4). Donde: Wx, Wy = componentes de la "
            "carga de diseño W paralelas a los ejes x e y, respectivamente. "
            "Wx y Wy son positivos si apuntan en la dirección positiva de "
            "los ejes x y y, respectivamente. W = carga de diseño dentro de "
            "una distancia de 0.5a a cada lado de la riostra. a = distancia "
            "longitudinal entre ejes de riostras. K' = 0 para secciones C. "
            "K' = Ixy/(2Ix) para secciones Z (F.4.4.3-5)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_2_1_a_variables_mz",
        "seccion": "F.4.4.3.2.1(a) (Variables Ixy, Iy, Mz, esx, esy, d, m — para cargas uniformes)",
        "titulo": "Definición de producto de inercia Ixy, momento torsional Mz, excentricidades esx/esy, altura d y distancia m al plano medio del alma.",
        "texto": (
            "Donde: Ixy = producto de inercia de la sección completa no "
            "reducida. Iy = momento de inercia de la sección completa no "
            "reducida alrededor del eje x. Mz = −Wx·esy + Wy·esx, momento "
            "torsional de W alrededor del centro de cortante. Donde: esx, "
            "esy = excentricidades de las componentes de las cargas medidas "
            "desde el centro de cortante en las direcciones x e y, "
            "respectivamente. d = altura de la sección. m = distancia desde "
            "el centro de cortante al plano medio del alma de la sección C. "
            "Ver figura F.4.4.3-1 para la esquematización del sistema de "
            "coordenadas, el centro de cortante C.C., el centroide C., y las "
            "direcciones positivas de las fuerzas PL1 y PL2."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_2_1_b_cargas_concentradas_6_9",
        "seccion": "F.4.4.3.2.1(b) (Para cargas concentradas — ecuaciones F.4.4.3-6 a -9)",
        "titulo": "PL1, PL2 para cargas concentradas (ecuaciones 6-7), casos especiales secciones C/Z (ecuaciones 8-9), y definición de la carga de diseño P considerando el efecto de cargas vecinas.",
        "texto": (
            "(b) Para cargas concentradas: PL1 = Py·K' − (Px/2) + (Mz/d) "
            "(F.4.4.3-6). PL2 = Py·K' − (Px/2) + (Mz/d) (F.4.4.3-7). Cuando "
            "una carga de diseño actúa a través del plano del alma, "
            "entonces Py=P: PL1 = −PL2 = (m/d)·P para secciones C "
            "(F.4.4.3-8). PL1 = PL2 = (Ixy/(2Ix))·P para secciones Z "
            "(F.4.4.3-9). Donde: Px, Py = componentes de la carga de diseño "
            "P paralelas a los ejes x y y, respectivamente. Px y Py son "
            "positivos si apuntan en la dirección positiva de los ejes x y "
            "y, respectivamente. Mz = −Px·esy + Py·esx, momento torsional de "
            "P alrededor del centro de cortante. P = carga concentrada de "
            "diseño dentro de una distancia de 0.3a sobre cada lado de la "
            "riostra, más 1.4·(1−l/a) veces cada carga concentrada de diseño "
            "localizada más allá de 0.3a pero no más allá de 1.0a a partir "
            "de la riostra. La carga concentrada de diseño es la carga "
            "aplicada determinada de acuerdo con la combinación de carga más "
            "crítica. Donde: l = distancia desde la carga concentrada hasta "
            "la riostra. Remitirse a la sección F.4.4.3.2.1(a) para "
            "definición de las otras variables."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_2_1_signo_condiciones",
        "seccion": "F.4.4.3.2.1 (Convención de signo de la fuerza de riostra, condiciones de sujeción y arriostramiento adicional)",
        "titulo": "PL1/PL2 positiva si previene movimiento en dirección x negativa; requisito de restricción torsional en extremos; excepción cuando cargas/reacciones ya restringen la sección.",
        "texto": (
            "La fuerza de arriostramiento, PL1 o PL2, es positiva cuando la "
            "restricción se requiera para prevenir el movimiento de la aleta "
            "correspondiente a la dirección x negativa. Donde se provean "
            "riostras, estas deben estar sujetadas de tal manera que "
            "restrinjan efectivamente la sección contra la deflexión lateral "
            "de ambas aletas en los extremos y en cualquier punto de "
            "arriostramiento intermedio. Cuando todas las cargas y "
            "reacciones sobre una viga se transmiten a través de miembros "
            "que ajustan dentro de la sección de forma tal que restrinjan la "
            "sección contra la rotación torsional y el desplazamiento "
            "lateral, no se requerirán riostras adicionales, excepto "
            "aquellas que se requieran por resistencia de acuerdo con la "
            "sección F.4.3.3.1.2.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_3_3_arriostramiento_compresion_10_11",
        "seccion": "F.4.4.3.3 (Arriostramiento de miembros en compresión axialmente cargados — ecuaciones F.4.4.3-10, -11)",
        "titulo": "Resistencia requerida Pbr,1 (ecuación 10) y rigidez requerida βbr,1 (ecuación 11) de la riostra para restringir la traslación lateral en un punto de arriostramiento.",
        "texto": (
            "F.4.4.3.3 — Arriostramiento de miembros en compresión "
            "axialmente cargados — La resistencia requerida en las riostras "
            "para restringir la traslación lateral en un punto de "
            "arriostramiento para un miembro individual en compresión se "
            "calculará como sigue: Pbr,1 = 0.01·Pn (F.4.4.3-10). La rigidez "
            "requerida en la riostra para restringir la traslación lateral "
            "en un punto de arriostramiento para un miembro individual en "
            "compresión se debe calcular como sigue: "
            "βbr,1 = 2·[4−(2/n)]·Pn / Lb (F.4.4.3-11). Donde: Pbr,1 = "
            "resistencia nominal requerida de la riostra para un miembro "
            "sencillo en compresión. Pn = resistencia nominal bajo "
            "compresión axial de un miembro sencillo. βbr,1 = rigidez "
            "requerida de riostra para un miembro sencillo en compresión. "
            "n = número de puntos de arriostramiento intermedio igualmente "
            "espaciados. Lb = distancia entre riostras sobre un miembro en "
            "compresión."
        ),
    },
    # ── F.4.4.4 — Entramados livianos ──────────────────────────
    {
        "id": "NSR10-F-F_4_4_4_entramados_livianos_intro",
        "seccion": "F.4.4.4 (Construcción de entramados livianos con miembros de acero formado en frío)",
        "titulo": "Alcance (espesor 0.455-2.997mm) y remisión a F.4.8, y las 5 disposiciones (a)-(e) para dinteles, cerchas, parales de muro, entrepisos/cubierta, y muros de corte.",
        "texto": (
            "F.4.4.4 — CONSTRUCCIÓN DE ENTRAMADOS LIVIANOS CON MIEMBROS DE "
            "ACERO FORMADO EN FRÍO — El diseño e instalación de miembros "
            "estructurales y no estructurales utilizados en aplicaciones de "
            "entramados repetitivos en acero formado en frío en los que el "
            "espesor mínimo especificado del acero base sea entre 0.455 mm y "
            "2.997 mm estará de acuerdo con F.4.8 de este Reglamento y lo "
            "siguiente, según sea aplicable: (a) Los dinteles, incluyendo "
            "miembros dinteles cajón y espalda con espalda, y dinteles tipo "
            "L, dobles y sencillos, se diseñarán de acuerdo de acuerdo con "
            "la sección F.4.8.4.4 de esta norma. (b) Las cerchas para "
            "entramados de acero formado en frío se diseñarán de acuerdo "
            "con la sección F.4.8.4.3 de esta norma. (c) Los parales de "
            "muro se diseñarán de acuerdo con la sección F.4.8.4.2, ya sea "
            "sobre la base de un sistema completamente en acero conforme "
            "con la sección F.4.4.4.1 ó sobre la base de un diseño "
            "arriostrado a paneles de cerramiento conforme a una apropiada "
            "teoría, ensayos o un análisis racional de ingeniería. Se "
            "permiten almas con y sin perforaciones. Ambos extremos deben "
            "estar conectados para restringir la rotación alrededor del eje "
            "longitudinal del paral y el desplazamiento horizontal "
            "perpendicular al eje del paral. (d) Los entramados para "
            "sistemas de entrepiso y cubierta en edificios se diseñarán de "
            "acuerdo con esta parte del Reglamento. (e) Los muros de corte "
            "para entramados livianos, arriostramiento mediante bandas "
            "diagonales (elementos que son parte del muro estructural) y "
            "diafragmas para resistir viento, sismo y otras cargas laterales "
            "en su propio plano, se diseñarán de acuerdo con AISI S213."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_4_1_ensambles_parales_muro",
        "seccion": "F.4.4.4.1 (Diseño completamente en acero de ensambles de parales de muro)",
        "titulo": "Se desprecia la contribución estructural de los paneles de cerramiento; deben cumplir F.4.3; propiedades de sección efectiva para miembros con perforaciones según F.4.2.2.2.",
        "texto": (
            "F.4.4.4.1 — Diseño completamente en acero de ensambles de "
            "parales de muro — En los ensambles de parales de muro que "
            "utilizan un diseño completamente en acero se despreciará la "
            "contribución estructural de los paneles de cerramiento sujetos "
            "a estos y deberán cumplir con los requisitos de F.4.3. Para "
            "miembros en compresión con perforaciones en el alma circulares "
            "o circulares, las propiedades de la sección efectiva se "
            "determinarán de acuerdo con la sección F.4.2.2.2."
        ),
    },
    # ── F.4.4.5 — Diafragmas ────────────────────────────────────
    {
        "id": "NSR10-F-F_4_4_5_diafragmas_intro",
        "seccion": "F.4.4.5 (Construcción de diafragmas en acero para entrepisos, cubiertas o muros)",
        "titulo": "Resistencia nominal al cortante Sn por cálculo o ensayo, factores φd de la Tabla F.4.4.5-1 según sismo/viento/otras combinaciones y tipo de conexión.",
        "texto": (
            "F.4.4.5 — CONSTRUCCIÓN DE DIAFRAGMAS EN ACERO PARA ENTREPISOS, "
            "CUBIERTAS O MUROS — La resistencia nominal al cortante en su "
            "propio plano de un diafragma, Sn, se establecerá mediante "
            "cálculo o ensayos. Los factores de resistencia para los "
            "diafragmas dados en la tabla F.4.4.5-1 se aplicarán a ambos "
            "métodos. Si la resistencia nominal al cortante se establece "
            "solo por ensayos y no definen todos los umbrales de estados "
            "límites, los factores de resistencia se limitarán a los "
            "valores dados en la tabla F.4.4.5-1 para las conexiones tipo y "
            "los modos de falla relacionados con la conexión. El estado "
            "límite multiplicado por un factor más desfavorable controlará "
            "el diseño. Donde se empleen combinaciones de sujetadores "
            "dentro de un sistema de diafragma se utilizará el factor más "
            "desfavorable. φd = como se especifica en la tabla F.4.4.5-1. "
            "Tabla F.4.4.5-1 — Factores de resistencia para diafragmas: "
            "Sismo con conexión soldada, φd=0.55 (relativa a la conexión); "
            "sismo atornillada, 0.65. Viento soldada, 0.70; viento "
            "atornillada, 0.60. Todas las demás soldada, 0.60; atornillada, "
            "0.65. Pandeo del panel (deformación fuera del plano, no "
            "relacionada con el pandeo local de los sujetadores): 0.80 para "
            "todos los casos."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_5_diafragmas_otros_sujetadores",
        "seccion": "F.4.4.5 (Sujetadores mecánicos diferentes a tornillos, calibración)",
        "titulo": "φd para sujetadores mecánicos distintos de tornillos limitado a los valores de la tabla; requisito de calibración de resistencia al cortante según F.4.6.1.1.",
        "texto": (
            "Para otro tipo de sujetadores mecánicos diferentes a tornillos "
            "φd no será mayor que los valores mostrados en la tabla "
            "F.4.4.5-1 para tornillos. Adicionalmente, los valores de φd "
            "utilizando sujetadores mecánicos diferentes deben limitarse a "
            "los valores de φ establecidos a través de calibración de la "
            "resistencia al cortante de un sujetador individual, a menos "
            "que existan los datos suficientes para establecer un efecto de "
            "sistema de diafragma acorde con la sección F.4.6.1.1. La "
            "calibración de la resistencia al cortante del sujetador "
            "incluirá el tipo de material del diafragma. La calibración de "
            "las resistencias al cortante de sujetadores individuales estará "
            "de acuerdo con la sección F.4.6.1.1. El conjunto para ensayo "
            "debe ser tal que el modo de falla evaluado sea representativo "
            "del diseño. Debe considerarse el impacto del espesor del "
            "material de soporte sobre el modo de falla."
        ),
    },
    # ── F.4.4.6.1 — Correas, largueros ─────────────────────────
    {
        "id": "NSR10-F-F_4_4_6_intro_6_1_1_1_1",
        "seccion": "F.4.4.6-F.4.4.6.1.1 (Sistemas de muros y cubiertas metálicas — introducción, y aleta sujeta a tableros — ecuación F.4.4.6-1)",
        "titulo": "Alcance de F.4.4.6.1-6.3 (correas/largueros/paneles/Standing Seam), y Mn=R·Se·Fy para sección C/Z con aleta a compresión no arriostrada.",
        "texto": (
            "F.4.4.6 — SISTEMAS DE MUROS Y CUBIERTAS METÁLICAS — Las "
            "disposiciones de la sección F.4.4.6.1 a la sección F.4.4.6.3 "
            "aplicarán para sistemas de muro y cubierta metálicos que "
            "incluyan correas de acero formado en frío, largueros, paneles "
            "de cubierta y muro, o paneles de cubierta tipo junta continua "
            "(Standing Seam), según sea aplicable. F.4.4.6.1 — Correas, "
            "Largueros y otros miembros. F.4.4.6.1.1 — Miembros en flexión "
            "con una aleta completamente sujeta a tableros o a paneles de "
            "cerramiento — Esta sección no aplica a una viga continua en la "
            "región entre puntos de inflexión adyacentes al soporte o a "
            "vigas en voladizo. La resistencia nominal a flexión, Mn, de una "
            "sección C ó Z cargada en un plano paralelo al alma, con la "
            "aleta a tensión sujeta a un tablero o panel y con la aleta a "
            "compresión no arriostrada lateralmente, se calculará de "
            "acuerdo con la ecuación F.4.4.6-1. Mn = R·Se·Fy (F.4.4.6-1). "
            "φb = 0.90."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_1_factor_r_limites_1_5",
        "seccion": "F.4.4.6.1.1 (Factor R — Tabla F.4.4.6-1, y límites 1-5)",
        "titulo": "R según Tabla F.4.4.6-1 (0.60 para C, 0.70 para Z en luces continuas), y primeros 5 de 14 límites de aplicabilidad.",
        "texto": (
            "Donde R se obtiene de la tabla F.4.4.6-1 para una luz simple "
            "con secciones C o Z, y R=0.60 para secciones C en luces "
            "continuas, R=0.70 para secciones Z en luces continuas. Se y Fy "
            "son los valores definidos en la sección F.4.3.3.1.1. El factor "
            "de reducción, R, se limitará a sistemas de cubierta y muro que "
            "cumplan las siguientes condiciones: (1) Altura del miembro ≤ "
            "292 mm. (2) Aletas en el miembro con rigidizadores de borde. "
            "(3) 60 ≤ altura/espesor ≤ 170. (4) 2.8 ≤ altura/ancho del ala "
            "≤ 4.5. (5) 16 ≤ ancho plano/espesor del ala ≤ 43."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_1_limites_6_14",
        "seccion": "F.4.4.6.1.1 (Límites 6-14, y remisión a ensayos si no se cumplen)",
        "titulo": "Límites 6-14 restantes (traslapo, longitud del vano, ambas aletas restringidas, paneles de acero mínimo 340 MPa, aislamiento, tornillería, fluencia máxima), y disposición para tramos con luces variables.",
        "texto": (
            "(6) Para sistemas de luz continua, la longitud del traslapo en "
            "cada apoyo interior hacia cada lado (distancia del centro del "
            "apoyo al final del traslapo) no será menor que 1.5d. (7) "
            "Longitud del vano para el miembro no mayor a 10 m. (8) Ambas "
            "aletas están restringidas al movimiento lateral en los apoyos. "
            "(9) Los paneles de muro o cubierta serán láminas de acero con "
            "340 MPa como esfuerzo mínimo de fluencia y un mínimo de 0.46 mm "
            "para el espesor del metal base, con una altura de formación de "
            "crestas mínima de 29 mm espaciadas un máximo de 305 mm a "
            "centros, y sujetas de tal forma que inhiban de manera efectiva "
            "el movimiento relativo entre el panel y la aleta de la correa. "
            "(10) El aislamiento es una capa en fibra de vidrio de hasta 152 "
            "mm de espesor localizada entre el miembro y el panel de una "
            "manera compatible con el sujetador usado. (11) Tipo de "
            "sujetador: mínimo tornillos de lámina de metal No.12 "
            "autorroscante o autorremachante o remaches de 4.76 mm y "
            "arandelas de 12.7 mm de diámetro. (12) Los sujetadores deben "
            "ser tornillos de tipo estructural. (13) La distancia entre "
            "sujetadores no debe ser mayor que 305 mm centro a centro y "
            "éstos deben estar localizados cerca del centro de la aleta de "
            "la viga y adyacentes a la cresta del panel. (14) El punto de "
            "fluencia de diseño del miembro no debe exceder 410 MPa. Si "
            "alguna de las variables no cumple con los límites establecidos "
            "anteriormente, deben realizarse ensayos a escala natural de "
            "acuerdo con la sección F.4.6.1, o diseñar utilizando un método "
            "racional de análisis. Para sistemas de correas continuos en los "
            "cuales las luces de vanos adyacentes varían más del 20%, los "
            "valores de R para los vanos adyacentes deben tomarse de la "
            "tabla F.4.4.6-1. Se permite la realización de ensayos de "
            "acuerdo con la sección F.4.6.1 como procedimiento alternativo "
            "al descrito en este numeral."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_1_tabla1_reduccion_2",
        "seccion": "F.4.4.6.1.1 (Tabla F.4.4.6-1 y factor de corrección por aislamiento comprimido — ecuación F.4.4.6-2)",
        "titulo": "4 rangos de altura d con su R (0.70 a 0.40 según C/Z), y factor de corrección r según espesor del aislamiento ti.",
        "texto": (
            "Tabla F.4.4.6-1 — Valores de R para secciones C ó Z en luces "
            "simples: d ≤ 165mm, perfil C o Z, R=0.70. 165<d≤216mm, perfil "
            "C o Z, R=0.65. 216<d≤292mm, perfil Z, R=0.50. 216<d≤292mm, "
            "perfil C, R=0.40. Para miembros en luces simples, R se reducirá "
            "debido a los efectos del aislamiento comprimido entre la "
            "lámina de acero y el miembro. La reducción debe ser calculada "
            "multiplicando R de la tabla F.4.4.6-1 por el siguiente factor "
            "de corrección, r: r = 1.00 − 0.0004·ti, con ti en milímetros "
            "(F.4.4.6-2). Donde: ti = espesor del aislamiento en fibra de "
            "vidrio no comprimido, mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_2_standing_seam_flexion_3",
        "seccion": "F.4.4.6.1.2 (Miembros a flexión con aleta sujeta a Standing Seam — ecuación F.4.4.6-3)",
        "titulo": "Mn=R·Se·Fy con R determinado por AISI S908 o método discreto de arriostramiento (ecuación 3).",
        "texto": (
            "F.4.4.6.1.2 — Miembros a flexión con una aleta sujeta a un "
            "sistema de cubierta de junta continua (Standing Seam) — La "
            "resistencia nominal a flexión, Mn, de una sección C o Z, "
            "cargada en un plano paralelo al alma que soporte un sistema de "
            "cubierta de junta continua en la aleta superior se determinará "
            "utilizando un arriostramiento discreto y las especificaciones "
            "de la sección F.4.3.3.1.2.1 o podrá calcularse de acuerdo con "
            "este numeral. Mn = R·Se·Fy (F.4.4.6-3). φb = 0.90. Donde: R = "
            "Factor de reducción determinado de acuerdo con AISI S908. Se y "
            "Fy son definidos en la sección F.4.3.3.1.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_3_compresion_eje_debil_4_7",
        "seccion": "F.4.4.6.1.3 (Miembros en compresión con aleta sujeta a tablero — eje débil, ecuaciones F.4.4.6-4 a -7)",
        "titulo": "Pn=C1·C2·C3·A·E/29500 (ecuación 4) y coeficientes C1, C2, C3 (ecuaciones 5-7), aplicable a secciones C/Z cargadas concéntricamente con una sola aleta sujeta.",
        "texto": (
            "F.4.4.6.1.3 — Miembros en compresión con una aleta sujeta "
            "completamente a un tablero o panel de cerramiento — Las "
            "disposiciones aquí dadas son aplicables a secciones C ó Z "
            "cargadas concéntricamente a lo largo de su eje longitudinal con "
            "solo una aleta sujeta a un tablero o panel de cerramiento con "
            "elementos de conexión. La resistencia nominal bajo carga axial "
            "de una sección C ó Z, en una luz simple o continua, se "
            "calculará como sigue: (a) La resistencia nominal en el eje "
            "débil se calculará de acuerdo con la ecuación F.4.4.6-5. "
            "Pn = C1·C2·C3·A·E/29500 (F.4.4.6-4). φc = 0.85. Donde: "
            "C1 = (0.79x + 0.54) (F.4.4.6-5). C2 = (1.17·α·t + 0.93) "
            "(F.4.4.6-6). C3 = α·(2.5b − 1.63d) + 22.8 (F.4.4.6-7)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_3_variables_x_alpha",
        "seccion": "F.4.4.6.1.3 (Variables x, α, t, b, d, A, E de las ecuaciones F.4.4.6-4 a -7)",
        "titulo": "Definición de x (posición del conector), α (constante 0.0394 en mm), y dimensiones t/b/d/A/E; y 10 condiciones de aplicabilidad de la ecuación F.4.4.6-5.",
        "texto": (
            "Donde: x = para secciones Z es la distancia al conector o "
            "elemento de sujeción, medida desde el lado exterior del alma, "
            "dividido entre el ancho de la aleta, tal como se muestra en la "
            "figura F.4.4.6-1. = para secciones C, es el ancho de la aleta "
            "menos la distancia al sujetador, medido a partir del lado "
            "externo del alma, dividido entre el ancho de la aleta, tal "
            "como se muestra en la figura F.4.4.6-1. α = 0.0394 cuando t, b "
            "y d están en milímetros. t = espesor de la sección C o Z, mm. "
            "b = ancho de aleta de la sección C o Z, mm. d = altura de la "
            "sección C o Z, mm. A = área completa transversal no reducida "
            "para secciones C o Z. E = módulo de elasticidad del acero, "
            "203 000 MPa. La ecuación F.4.4.6-5 será aplicable a sistemas de "
            "cubiertas y muros que cumplan las siguientes condiciones: (1) "
            "t ≤ 3.22 mm. (2) 152 mm ≤ d ≤ 305 mm. (3) Las aletas son "
            "elementos en compresión rigidizados en el borde. (4) 70 ≤ d/t "
            "≤ 170. (5) 2.8 ≤ d/b ≤ 5. (6) 70 ≤ ancho plano del ala/t ≤ 50. "
            "(7) La cubierta metálica o los paneles de muro en acero "
            "tendrán conectores o elementos de sujeción espaciados entre "
            "centros 305 mm como máximo, con una rigidez lateral-rotacional "
            "mínima de 10 300 N/m/m (sujeto en la mitad del ancho de la "
            "aleta para determinación de la rigidez) como se determina con "
            "el procedimiento de ensayo del AISI. (8) Las secciones C y Z "
            "tendrán un punto de fluencia mínimo de 230 MPa. (9) La "
            "longitud de la luz no excederá 10 m."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_3_eje_fuerte_remision",
        "seccion": "F.4.4.6.1.3(b) (Resistencia nominal en el eje fuerte)",
        "titulo": "Remisión a las ecuaciones de F.4.3.4.1 y F.4.3.4.1.1 para la resistencia en el eje fuerte.",
        "texto": (
            "(b) Para la resistencia nominal en el eje fuerte deben "
            "utilizarse las ecuaciones de las secciones F.4.3.4.1 y "
            "F.4.3.4.1.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_4_standing_seam_compresion_8_9",
        "seccion": "F.4.4.6.1.4 (Miembros en compresión de secciones Z con aleta sujeta a Standing Seam — ecuaciones F.4.4.6-8, -9)",
        "titulo": "Pn=kaf·R·Fy·A para eje débil (ecuación 8) con kaf según d/t (3 rangos, ecuación 9), y 8 límites de aplicabilidad.",
        "texto": (
            "F.4.4.6.1.4 — Miembros en compresión de secciones Z con una "
            "aleta sujeta a un sistema de cubierta de junta continua "
            "(Standing Seam) — Las disposiciones de este numeral aplican a "
            "secciones Z cargadas concéntricamente a lo largo de su eje "
            "longitudinal, con una sóla aleta sujeta a paneles de cubierta "
            "de junta continua (Standing Seam). Alternativamente, los "
            "valores de diseño de un sistema particular podrán tomarse con "
            "base en puntos de arriostramiento discreto, o en ensayos de "
            "acuerdo con F.4.6. La resistencia nominal axial de secciones "
            "Z, en luces simples o continuas, se calculará de acuerdo con "
            "los incisos a) y b). (a) Para la resistencia de diseño en el "
            "eje débil: Pn = kaf·R·Fy·A (F.4.4.6-8). φ = 0.85. Donde: Para "
            "d/t ≤ 90: kaf = 0.36. Para 90 < d/t ≤ 130: "
            "kaf = 0.72 − d/(250t) (F.4.4.6-9). Para d/t > 130: "
            "kaf = 0.20. R = factor de reducción determinado de pruebas de "
            "carga de succión realizadas acorde con AISI S908. A = área "
            "transversal total no reducida de la sección Z. d = altura de "
            "la sección Z. t = espesor de la sección Z. Remitirse a la "
            "sección F.4.3.3.1.1 para definición de Fy."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_1_4_limites_1_8",
        "seccion": "F.4.4.6.1.4 (8 límites de aplicabilidad de la ecuación F.4.4.6-9, y eje fuerte)",
        "titulo": "8 condiciones geométricas/materiales, y remisión a F.4.3.4.1/F.4.3.4.1.1 para la resistencia en el eje fuerte.",
        "texto": (
            "El uso de la ecuación F.4.4.6-9 se limitará a los sistemas de "
            "cubierta que cumplan con las siguientes condiciones: (1) "
            "Espesor de correa, 1.37 mm ≤ t ≤ 3.22 mm. (2) 152 mm ≤ d ≤ "
            "305 mm. (3) Las aletas son elementos en compresión rigidizados "
            "en el borde. (4) 70 ≤ d/t ≤ 170. (5) 2.8 ≤ d/b < 5 donde b = "
            "ancho de aleta de la sección Z. (6) 16 ≤ ancho plano del "
            "ala/t < 50. (7) Ambas aletas están restringidas a movimiento "
            "lateral en los apoyos. (8) Esfuerzo de fluencia, Fy ≤ 483 MPa. "
            "(b) Para la resistencia de diseño alrededor del eje fuerte "
            "deben utilizarse las ecuaciones de las secciones F.4.3.4.1 y "
            "F.4.3.4.1.1."
        ),
    },
    # ── F.4.4.6.2 — Standing Seam ────────────────────────────
    {
        "id": "NSR10-F-F_4_4_6_2_1_standing_seam_resistencia",
        "seccion": "F.4.4.6.2.1 (Resistencia de sistema de panel de cubierta de junta continua — Standing Seam)",
        "titulo": "Resistencia bajo cargas gravitacionales (según F.4.2/F.4.3 o AISI S906) y bajo succión (AISI S906), con 3 excepciones de ensayo (procedimientos alternativos aceptados).",
        "texto": (
            "F.4.4.6.2 — Sistema de panel de cubierta de junta continua "
            "(Standing Seam). F.4.4.6.2.1 — Resistencia de sistema de panel "
            "de cubierta de junta continua (Standing Seam) — Bajo cargas "
            "gravitacionales, la resistencia nominal de los paneles de "
            "cubierta de junta continua se determinará de acuerdo con F.4.2 "
            "y F.4.3 de este Reglamento o mediante ensayos de acuerdo con el "
            "documento AISI S906. Bajo cargas de succión, la resistencia "
            "nominal del panel de cubierta de junta continua se determinará "
            "de acuerdo con las especificaciones AISI S906. Se deberán "
            "realizar ensayos de acuerdo con el documento AISI S906 con las "
            "siguientes excepciones: (1) Se permitirá el procedimiento de "
            "ensayo de succión para cubiertas de paneles clase 1 descrito "
            "en FM 4471 (Factory Mutual). (2) Se permitirán ensayos "
            "existentes conducidos de acuerdo con el procedimiento de "
            "ensayo de succión descrito por el CEGS 07416 (Corps of "
            "Engineers of USA) y anteriores a esta norma. Se permite el uso "
            "de los procedimientos de ensayo descritos en la norma ASTM "
            "E1592 para las pruebas de carga sobre cubierta. El factor de "
            "resistencia, φ, no debe ser mayor a 0.90. Cuando el número de "
            "conjuntos para ensayo es menor a 3, se usará un factor de "
            "resistencia, φ, de 0.80."
        ),
    },
    # ── F.4.4.6.3 — Arriostramiento y anclaje ──────────────────
    {
        "id": "NSR10-F-F_4_4_6_3_1_anclaje_intro",
        "seccion": "F.4.4.6.3.1 (Anclaje del arriostramiento para sistemas cubierta-correa — introducción)",
        "titulo": "Requisito de dispositivo de anclaje capaz de transferir las fuerzas del diafragma al apoyo, diseñado según la ecuación F.4.4.6-11 y con rigidez mínima según F.4.4.6-17.",
        "texto": (
            "F.4.4.6.3 — Arriostramiento y anclaje de sistemas de cubierta. "
            "F.4.4.6.3.1 — Anclaje del arriostramiento para sistemas "
            "cubierta-correa bajo carga gravitacional con la aleta superior "
            "conectada a un tablero metálico — Para sistemas de cubierta con "
            "secciones C y Z, con un tablero metálico, o una cubierta de "
            "junta continua (Standing Seam), conectados a las aletas "
            "superiores y diseñados de acuerdo con las secciones F.4.3.3.1 y "
            "F.4.4.6.1, debe suministrarse un dispositivo de anclaje capaz "
            "de transferir las fuerzas del diafragma de cubierta al apoyo. "
            "Cada dispositivo de anclaje debe diseñarse para resistir una "
            "fuerza, PL, determinada por la ecuación F.4.4.6-11 y debe "
            "satisfacer los requisitos de rigidez mínima de la ecuación "
            "F.4.4.6-17. Adicionalmente, las correas deben ser restringidas "
            "por el tablero metálico de tal forma que los desplazamientos "
            "laterales máximos de la aleta superior entre líneas de anclaje "
            "lateral, evaluado con las cargas de servicio, no excedan la "
            "longitud del vano dividida por 360."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_dispositivos_anclaje_10",
        "seccion": "F.4.4.6.3.1 (Dispositivos de anclaje — ecuación F.4.4.6-10)",
        "titulo": "Localización de anclajes, y la fórmula general de fuerza lateral por dispositivo PLj (sumatoria sobre líneas de correas, ecuación 10).",
        "texto": (
            "Los dispositivos de anclaje, o riostras, se localizarán en "
            "cada vano de correas y se conectarán al miembro en la aleta "
            "superior o cerca de ella. Si los dispositivos de anclaje no "
            "están directamente conectados a todas las líneas de correas de "
            "cada vano, se suministrarán mecanismos para transmitir las "
            "fuerzas desde otra línea de correas a los dispositivos de "
            "anclaje. Debe demostrarse que la fuerza requerida, PL, puede "
            "transferirse al dispositivo de anclaje a través del tablero de "
            "cubierta y su sistema de sujeción. La rigidez lateral del "
            "dispositivo de anclaje se determinará mediante análisis o "
            "ensayos. Estos análisis o ensayos deben tomar en cuenta los "
            "efectos de la flexibilidad del alma de la correa sobre la "
            "conexión del dispositivo de anclaje. PL,j = Σ(i=1 a Np) de "
            "Pi·(Keffi,j/ktotali) (F.4.4.6-10). Donde: PL,j = fuerza lateral "
            "que debe ser resistida por el dispositivo de anclaje "
            "j-ésimo (es positiva cuando la restricción se requiere para "
            "restringir el movimiento de las correas en la dirección hacia "
            "arriba de la pendiente de cubierta). Np = número de líneas de "
            "correas en la pendiente de cubierta. i = índice para cada "
            "línea de correas (i=1,2,...,Np). j = índice para cada "
            "dispositivo de anclaje (j=1,2,...,Na)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_pi_11",
        "seccion": "F.4.4.6.3.1 (Fuerza Pi introducida por cada correa — ecuación F.4.4.6-11)",
        "titulo": "Pi = fórmula con coeficientes C1-C4 (tablas F.4.4.6-2 a -4) y variables geométricas de la correa.",
        "texto": (
            "Na = número de dispositivos de anclaje a lo largo de una línea "
            "de anclajes. Pi = fuerza lateral introducida al sistema en la "
            "i-ésima correa = (C1)·WPi·{[(C2/1000)·(Ixy·L/(Ix·d)) + "
            "(C3)·((m+0.25b)·t/d²)]·α·cosθ − (C4)·senθ} (F.4.4.6-11). "
            "Donde: C1, C2, C3 y C4 = Coeficientes presentados en las tablas "
            "F.4.4.6-2 a F.4.4.6-4. WPi = carga total vertical requerida "
            "soportada por la i-ésima correa en un solo vano = wi·L "
            "(F.4.4.6-12)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_variables_wi_ixy_12",
        "seccion": "F.4.4.6.3.1 (Variables wi, Ixy, L, m, b, t, Ix, d, α, θ)",
        "titulo": "Definición completa de las variables de la ecuación F.4.4.6-11: carga wi, producto de inercia Ixy, luz L, distancia m, ancho b, espesor t, momento Ix, altura d, orientación α y θ.",
        "texto": (
            "Donde: wi = carga gravitacional distribuida soportada por la "
            "i-ésima correa, por unidad de longitud (determinada a partir "
            "de la combinación crítica para diseño). Ixy = producto de "
            "inercia de la sección completa no reducida alrededor de ejes "
            "centroidales paralelos y perpendiculares al alma de la correa "
            "(Ixy=0 para secciones C). L = longitud del vano de la correa. "
            "m = distancia desde el centro de cortante al plano medio del "
            "alma (m=0 para secciones Z). b = ancho de la aleta superior "
            "de la correa. t = espesor de la correa. Ix = momento de "
            "inercia de la sección completa no reducida alrededor del eje "
            "centroidal perpendicular al alma de la correa. d = altura de "
            "la correa. α = +1 si la aleta superior de la correa señala "
            "hacia arriba de la pendiente. = −1 si la aleta superior de la "
            "correa señala hacia abajo de la pendiente. θ = ángulo entre la "
            "vertical y el plano del alma de la correa."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_keff_13",
        "seccion": "F.4.4.6.3.1 (Rigidez lateral efectiva Keffi,j — ecuación F.4.4.6-13)",
        "titulo": "Keffi,j en función de la rigidez del dispositivo de anclaje Ka y las propiedades del panel de cubierta (área bruta Ap, coeficiente C6).",
        "texto": (
            "Keffi,j = rigidez lateral efectiva del j-ésimo dispositivo de "
            "anclaje con respecto a la i-ésima correa = [1/Ka + "
            "dPi,j/((C6)·L·Ap·E)]⁻¹ (F.4.4.6-13). Donde: dPi,j = distancia "
            "medida a lo largo de la pendiente de cubierta entre la i-ésima "
            "línea de correas y el j-ésimo dispositivo de anclaje. Ka = "
            "rigidez lateral del dispositivo de anclaje. C6 = coeficiente "
            "tomado de las tablas F.4.4.6-2 a F.4.4.6-4. Ap = área bruta de "
            "la sección transversal del panel de cubierta, por unidad de "
            "ancho. E = módulo de elasticidad del acero."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_ktotal_14_15",
        "seccion": "F.4.4.6.3.1 (Rigidez lateral total ktotali — ecuaciones F.4.4.6-14, -15)",
        "titulo": "ktotali como suma de las rigideces de todos los dispositivos de anclaje más la rigidez del sistema de cubierta Ksys (ecuación 15).",
        "texto": (
            "Ktotali = rigidez lateral efectiva de todos los elementos que "
            "resisten la fuerza Pi = Σ(j=1 a Na) de (Keffi,j) + Ksys "
            "(F.4.4.6-14). Donde: Ksys = rigidez lateral del sistema de "
            "cubierta, despreciando el aporte de los dispositivos de "
            "anclaje = (C5/1000)·Np·(E·L·t²/d²) (F.4.4.6-15)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_luces_multiples",
        "seccion": "F.4.4.6.3.1 (Sistemas con luces múltiples — promedio de valores)",
        "titulo": "Regla del 80% para línea exterior/primer pórtico interior/anclaje exterior, y promedio ponderado de L/t/d y Pi/Ksys/Keffi,j para vanos adyacentes con diferentes propiedades.",
        "texto": (
            "Para sistemas con luces múltiples la fuerza Pi, calculada de "
            "acuerdo con la ecuación F.4.4.6-12 y los coeficientes C1 a C4 "
            "de las tablas F.4.4.6-2 a F.4.4.6-4, en los casos de línea "
            "exterior de pórticos, vano de extremo o anclaje exterior del "
            "vano de extremo, debe ser mayor al 80% de la fuerza "
            "determinada usando los coeficientes C2 a C4 para todas las "
            "otras posiciones del área de cubierta. Para sistemas con "
            "luces múltiples y dispositivos de anclaje en los apoyos, "
            "cuándo los dos vanos adyacentes tengan diferentes propiedades "
            "de sección o luces diferentes, los valores de Pi en la "
            "ecuación F.4.4.6-11 y ecuación F.4.4.6-18 deben tomarse como "
            "el promedio de los valores encontrados a partir de la ecuación "
            "F.4.4.6-12, evaluados separadamente para cada uno de los dos "
            "vanos. Los valores de Ksys y Keffi,j en las ecuaciones "
            "F.4.4.6-11 y F.4.4.6-15 se calcularán usando las ecuaciones "
            "F.4.4.6-14 y F.4.4.6-16, con los valores promedios de L, t y d "
            "de ambos vanos."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_luces_multiples_tercios",
        "seccion": "F.4.4.6.3.1 (Sistemas con luces múltiples — anclajes en tercios/puntos medios)",
        "titulo": "Promedio ponderado (1 vano extremo + 2 veces interior, dividido por 3) para Pi, y regla de promedio en L para Ksys.",
        "texto": (
            "Para sistemas con luces múltiples y dispositivos de anclaje en "
            "los tercios o puntos medios, cuándo los vanos adyacentes "
            "tienen diferentes propiedades de sección o luces diferentes al "
            "vano bajo consideración, se debe utilizar el siguiente "
            "procedimiento para tener en cuenta la influencia de los vanos "
            "adyacentes. Los valores para Pi en la ecuación F.4.4.6-11 y la "
            "ecuación F.4.4.6-18 deben tomarse como el promedio de los "
            "valores encontrados a partir de la ecuación F.4.4.6-12, "
            "evaluada separadamente para cada uno de los tres vanos. El "
            "valor de Ksys en la ecuación F.4.4.6-15 debe calcularse "
            "usando la ecuación F.4.4.6-16, con L, t y d tomados como el "
            "promedio de los valores en los tres vanos. Los valores de "
            "Keffi,j deben calcularse usando la ecuación F.4.4.6-14, con L "
            "tomado como la luz del vano bajo consideración. En un vano de "
            "extremo, cuando se calculan los valores promedio para Pi o se "
            "promedian las propiedades para el cálculo de Ksys, éstos deben "
            "hallarse mediante la suma del valor proveniente del primer "
            "vano interior más dos veces el valor obtenido del vano de "
            "extremo y dividiendo el total de la suma por tres."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_1_rigidez_total_16_18",
        "seccion": "F.4.4.6.3.1 (Rigidez total mínima y análisis alternativo — ecuaciones F.4.4.6-16 a -18)",
        "titulo": "Requisito Ktotali≥Kreq (ecuación 16), Kreq (ecuación 17), y desplazamiento lateral máximo permitido Δtf en la línea de restricción (ecuación 18).",
        "texto": (
            "La rigidez total efectiva en cada correa debe satisfacer la "
            "siguiente ecuación: Ktotali ≥ Kreq (F.4.4.6-16). Donde: "
            "Kreq = (1/φ)·(20·|Σ(i=1 a Np) Pi|/d) (F.4.4.6-17). φ = 0.75. "
            "En lugar de las ecuaciones F.4.4.6-11 a F.4.4.6-16, se permite "
            "un análisis alternativo para las fuerzas de restricción "
            "lateral. Un análisis de este tipo debe incluir los efectos de "
            "primer o segundo orden y tener en cuenta también los efectos "
            "de la pendiente de cubierta, torsión resultante debido a "
            "cargas excéntricas al centro de cortante, torsión resultante "
            "de la resistencia lateral suministrada por el cerramiento y "
            "cargas aplicadas oblicuamente a los ejes principales. Este "
            "análisis alternativo debe incluir también los efectos de la "
            "restricción lateral y rotacional suministrada por el tablero "
            "sujeto a la aleta superior de los miembros. Debe considerarse "
            "la rigidez del dispositivo de anclaje y tomarse en cuenta el "
            "efecto de la flexibilidad del alma de la correa sobre la "
            "conexión del dispositivo de anclaje. Cuando las fuerzas de "
            "restricción lateral se determinan por medio de un análisis "
            "racional, el máximo desplazamiento lateral de la aleta "
            "superior de la correa entre líneas de arriostramiento lateral "
            "evaluado con las cargas de servicio no excederá la luz del "
            "vano dividida por 360. El desplazamiento lateral de la aleta "
            "superior de la correa en la línea de restricción, Δtf se "
            "calcula a los niveles de cargas mayoradas de diseño y debe "
            "limitarse a: Δtf ≤ φ·d/20 (F.4.4.6-18)."
        ),
    },
    {
        "id": "NSR10-F-F_4_4_6_3_2_arriostramiento_alternativo",
        "seccion": "F.4.4.6.3.2 (Arriostramiento lateral y de estabilidad alternativo para sistemas cubierta-correa)",
        "titulo": "Riostra torsional en lugar de F.4.4.6.3.1: límite de desplazamiento φd/20 en la línea de pórtico y L/180 entre líneas de pórticos.",
        "texto": (
            "F.4.4.6.3.2 — Arriostramiento lateral y de estabilidad "
            "alternativo para sistemas cubierta-correa — Se permite el "
            "arriostramiento torsional que evite el giro alrededor del eje "
            "longitudinal de un miembro, en combinación con restricciones "
            "laterales que eviten el desplazamiento lateral de la aleta "
            "superior en la línea del pórtico, en lugar de los requisitos "
            "de la sección F.4.4.6.3.1. La riostra torsional debe prevenir "
            "la rotación de la sección transversal en el punto de "
            "arriostramiento discreto a lo largo de la luz del miembro. La "
            "conexión de las riostras debe hacerse en, o cerca de, ambas "
            "aletas de secciones abiertas comunes, incluyendo las secciones "
            "C y Z. La efectividad de las riostras torsionales en la "
            "prevención de la rotación de la sección transversal y la "
            "resistencia requerida de las riostras laterales en la línea "
            "del pórtico se determinará por medio de un análisis racional "
            "de ingeniería o ensayos. El desplazamiento lateral de la aleta "
            "superior de la sección C o Z en la línea del pórtico deberá "
            "limitarse a φd/20, calculado para carga mayorada, donde d es "
            "la altura del miembro en sección C ó Z, y φ es el factor de "
            "resistencia. El desplazamiento lateral entre líneas de "
            "pórticos, calculado para carga de servicio, se limita a "
            "L/180, donde L es la luz del vano del miembro. Para parejas "
            "de correas adyacentes, que se restrinjan contra rotación la "
            "una a la otra, no se requiere anclaje externo para el "
            "arriostramiento torsional. φ = 0.75."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.4 cargados. Numeral F.4.4 completo.")


if __name__ == "__main__":
    main()
