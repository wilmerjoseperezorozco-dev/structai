"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.3 (Miembros) completo, en verbatim real.
Tercera pieza de F.4/F.5 (F.4.1 y F.4.2 ya cerrados en sesiones
anteriores).

F.4.3 -- MIEMBROS: F.4.3.1 (Propiedades de la seccion), F.4.3.2
(Miembros en tension), F.4.3.3 (Miembros a flexion -- resistencia
nominal por 2 procedimientos, pandeo lateral torsional secciones
abiertas/cajon/tubulares, pandeo distorsional, cortante, flexion+corte
combinados, arrugamiento del alma con 5 tablas de factores,
flexion+arrugamiento combinados, flexion+torsion combinadas,
rigidizadores de apoyo y de cortante), F.4.3.4 (Miembros en compresion
cargados concentricamente -- fluencia/pandeo flector/flexo-
torsional/torsional, pandeo distorsional), F.4.3.5 (Carga axial y
momento combinados -- tension+momento, compresion+momento).

CHUNKS escritos directamente en piezas chicas (~100 tokens, ~450 chars)
desde el principio -- aprendido de F.4.2 (donde se escribieron 6 chunks
grandes por numeral y hubo que re-trocearlos despues al descubrir que
el modelo de embeddings trunca a 128 tokens, ver
[[project_construdata_limite_tokens_embeddings]]).

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
paginas internas F-329 a F-358 (paginas PDF 29-58), leidas visualmente
pagina por pagina.

Uso: python _ingest_titulo_f_f43_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"
SECCION_BASE = "F.4.3 (Miembros)"

CHUNKS = [
    # ── F.4.3.1 y F.4.3.2 ──────────────────────────────────────────
    {
        "id": "NSR10-F-F_4_3_1_2_propiedades_tension",
        "seccion": "F.4.3.1-F.4.3.2 (Propiedades de la sección; Miembros en tensión)",
        "titulo": "Propiedades de la sección por métodos convencionales, y resistencia nominal a tensión Tn (fluencia sección bruta, ecuación F.4.3.2-1; rotura sección neta, F.4.3.2-2).",
        "texto": (
            "NSR-10 Título F, Capítulo F.4 — F.4.3 — MIEMBROS. F.4.3.1 — "
            "PROPIEDADES DE LA SECCIÓN — Las propiedades de la sección (Área "
            "transversal, momento de inercia, módulo de sección, radio de giro, "
            "etc) se determinarán de acuerdo con los métodos convencionales del "
            "diseño estructural. Estas propiedades se basarán en las secciones "
            "transversales totales de los miembros estructurales (o en secciones "
            "netas cuando sea aplicable su uso) excepto donde se requiera el uso "
            "de una sección transversal reducida o ancho de diseño efectivo."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_2_miembros_tension_ecuaciones",
        "seccion": "F.4.3.2 (Miembros en tensión)",
        "titulo": "Ecuaciones F.4.3.2-1 (fluencia en sección bruta) y F.4.3.2-2 (rotura en sección neta lejos de la conexión), y remisión a resistencia por conexión.",
        "texto": (
            "F.4.3.2 — MIEMBROS EN TENSIÓN — Para miembros en tensión cargados "
            "axialmente, la resistencia nominal a tensión, Tn, será el menor "
            "valor obtenido de acuerdo con los estados límite de a), b) ó c). "
            "a) Para fluencia en la sección bruta: Tn = Ag·Fy (F.4.3.2-1). "
            "φt = 0.90. Donde: Tn = resistencia nominal del miembro bajo "
            "tensión. Ag = área bruta o completa de la sección transversal. "
            "Fy = esfuerzo de fluencia de diseño como se define en la sección "
            "F.4.1.6.1. b) Para rotura en la sección neta lejos de la "
            "conexión: Tn = An·Fu (F.4.3.2-2). φt = 0.75. Donde: An = área "
            "neta de la sección transversal. Fu = resistencia a tensión como "
            "se especifica en la sección F.4.1.2.1 ó F.4.1.2.3.2. c) Para "
            "rotura en la sección neta en la conexión — La resistencia de "
            "diseño a tensión también se limitará por las secciones F.4.5.2.7, "
            "F.4.5.3, y F.4.5.5 para miembros en tensión cuando se usen "
            "conexiones soldadas, conexiones pernadas y conexiones atornilladas."
        ),
    },
    # ── F.4.3.3.1 — Flexión, resistencia nominal ──────────────────
    {
        "id": "NSR10-F-F_4_3_3_1_flexion_general",
        "seccion": "F.4.3.3.1 (Miembros a flexión — general)",
        "titulo": "Resistencia nominal a flexión Mn según secciones aplicables, y remisión a F.4.3.3.6 para cargas torsionales.",
        "texto": (
            "F.4.3.3 — MIEMBROS A FLEXIÓN. F.4.3.3.1 — Flexión — La resistencia "
            "nominal a flexión, Mn, será el valor calculado de acuerdo con las "
            "secciones F.4.3.3.1.1, F.4.3.3.1.2, F.4.3.3.1.3, F.4.3.3.1.4, "
            "F.4.4.6.1.1, F.4.4.6.1.2, y F.4.4.6.2.1, según sea aplicable. Para "
            "miembros en flexión no restringidos lateralmente sujetos a flexión "
            "y carga torsional, tales como cargas que no pasan por el centro "
            "de cortante de la sección transversal, se deberá aplicar la "
            "sección F.4.3.3.6."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_1_1_resistencia_seccion",
        "seccion": "F.4.3.3.1.1 (Resistencia nominal de la sección — Procedimiento 1)",
        "titulo": "Ecuación F.4.3.3-1 (Mn=Se·Fy) para secciones con aletas a compresión rigidizadas (φb=0.95) o no rigidizadas (φb=0.90), procedimiento basado en iniciación de la fluencia.",
        "texto": (
            "F.4.3.3.1.1 — Resistencia nominal de la sección — La resistencia "
            "nominal a flexión, Mn, se calculará, bien sea a partir de la base "
            "del punto de iniciación de la fluencia en la sección efectiva "
            "(Procedimiento 1) o sobre la base de la capacidad de reserva "
            "inelástica (Procedimiento 2), según sea aplicable. Para secciones "
            "con aletas a compresión rigidizadas o parcialmente rigidizadas: "
            "φb = 0.95. Para secciones con aletas a compresión no rigidizadas: "
            "φb = 0.90. a) Procedimiento 1 — Basado en la iniciación de la "
            "fluencia — La resistencia nominal a flexión, Mn, para el momento "
            "de fluencia efectivo se calculará de acuerdo con la ecuación "
            "F.4.3.3-1, como sigue: Mn = Se·Fy (F.4.3.3-1). Donde: Se = "
            "módulo elástico de la sección efectiva, calculado respecto a la "
            "fibra extrema en compresión o tensión al alcanzar Fy. Fy = "
            "esfuerzo de fluencia de diseño determinado en la sección F.4.1.6.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_1_2_procedimiento2_reserva",
        "seccion": "F.4.3.3.1.1 (Procedimiento 2 — capacidad de reserva inelástica, condiciones y factor Cy)",
        "titulo": "5 condiciones para usar el procedimiento 2, límite Mn≤1.25·Se·Fy, y el factor de deformación unitaria Cy para elementos rigidizados sin rigidizadores intermedios (ecuaciones F.4.3.3-2 a -4).",
        "texto": (
            "b) Procedimiento 2 — Basado en la capacidad de reserva inelástica. "
            "Se permite utilizar la capacidad de reserva inelástica a flexión "
            "cuando se cumplen las siguientes condiciones: (1) El miembro no "
            "está sujeto a torsión o a pandeo lateral, torsional o "
            "flexo-torsional. (2) El efecto del trabajo de formación en frío "
            "no se incluye en la determinación del esfuerzo de fluencia Fy. "
            "(3) La relación entre la altura de la porción en compresión del "
            "alma y su espesor no excede λ1. (4) La fuerza de corte no excede "
            "0.6Fy veces el área del alma (el área es igual a ht para "
            "elementos rigidizados ó wt para elementos no rigidizados). (5) El "
            "ángulo entre cualquier alma y la vertical no excede 30 grados. La "
            "resistencia nominal a flexión, Mn, no debe exceder 1.25·Se·Fy "
            "determinado de acuerdo con el procedimiento 1 de la sección "
            "F.4.3.3.1.1(a) ni el momento que causa la deformación unitaria "
            "máxima en compresión igual a Cy·ey (no se limita la deformación "
            "unitaria máxima para la tensión). Donde: h = altura plana del "
            "alma. t = espesor del acero base del elemento. ey = deformación "
            "unitaria en la fluencia = Fy/E. Cy = factor de deformación "
            "unitaria a compresión determinado como sigue: (a) Elementos en "
            "compresión rigidizados sin rigidizadores intermedios: Cy = 3.0 "
            "cuando w/t ≤ λ1. Cy = 3−2·((w/t−λ1)/(λ2−λ1)) cuando λ1<w/t<λ2 "
            "(F.4.3.3-2). Cy = 1.0 cuando w/t ≥ λ2. Donde: λ1 = 1.11/√(Fy/E) "
            "(F.4.3.3-3). λ2 = 1.28/√(Fy/E) (F.4.3.3-4)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_1_3_cy_no_rigidizados",
        "seccion": "F.4.3.3.1.1 (Factor Cy para elementos no rigidizados — 3 casos)",
        "titulo": "Cy para elementos en compresión no rigidizados: gradiente de esfuerzo con tensión (ecuaciones F.4.3.3-5, -6), gradiente con compresión en ambos bordes, y compresión uniforme; y elementos multirigidizados/con rigidizador de borde.",
        "texto": (
            "(b) Elementos en compresión no rigidizados — Para elementos en "
            "compresión no rigidizados, Cy se calculará como sigue: (i) "
            "Elementos en compresión no rigidizados bajo gradiente de esfuerzo "
            "causando compresión en un borde longitudinal y tensión en el otro "
            "borde longitudinal: Cy = 3.0 cuando λ ≤ λ3. "
            "Cy = 3−2·[(λ−λ3)/(λ4−λ3)] cuando λ3<λ<λ4 (F.4.3.3-5). Cy = 1.0 "
            "cuando λ ≥ λ4. Donde: λ3 = 0.43. λ4 = 0.673·(1+ψ) (F.4.3.3-6). "
            "ψ = Valor definido en la sección F.4.2.3.2. (ii) Elementos en "
            "compresión no rigidizados bajo gradiente de esfuerzo que cause "
            "compresión en ambos bordes longitudinales: Cy = 1. (iii) "
            "Elementos no rigidizados bajo compresión uniforme: Cy = 1. (c) "
            "Elementos en compresión multirigidizados y elementos en "
            "compresión con rigidizadores de borde: Cy = 1. Cuando sea "
            "aplicable, se usarán los anchos efectivos de diseño en el cálculo "
            "de las propiedades de las secciones. Mn debe ser calculado "
            "considerando equilibrio de esfuerzos, suponiendo una curva "
            "esfuerzo-deformación elasto-plástica, la cual es la misma para "
            "tensión y compresión, pequeñas deformaciones y que las secciones "
            "permanecen planas durante la flexión. El efecto de la flexión y "
            "arrugamiento del alma combinados debe ser revisado de acuerdo con "
            "las especificaciones de la sección F.4.3.3.5."
        ),
    },
    # ── F.4.3.3.1.2 — Pandeo lateral torsional ────────────────────
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_plt_secciones_abiertas_intro",
        "seccion": "F.4.3.3.1.2.1 (Resistencia al pandeo lateral torsional de secciones abiertas — introducción, ecuación F.4.3.3-7)",
        "titulo": "Aplicabilidad (secciones I/Z/C simetría sencilla, φb=0.90) y la ecuación general Mn=Sc·Fc para segmentos no arriostrados lateralmente.",
        "texto": (
            "F.4.3.3.1.2 — Resistencia al pandeo lateral torsional — Las "
            "especificaciones de esta sección aplicarán a miembros con "
            "secciones abiertas como se definen en la sección F.4.3.3.1.2.1 ó "
            "con secciones cerradas tipo cajón como se definen en la sección "
            "F.4.3.3.1.2.2. El factor de resistencia en estas secciones será: "
            "φb = 0.90. F.4.3.3.1.2.1 — Resistencia al pandeo lateral "
            "torsional de miembros de secciones abiertas — Las "
            "especificaciones de esta sección aplican a miembros en flexión "
            "de secciones I, Z, C y otras secciones de simetría sencilla (no "
            "se incluyen tableros de almas múltiples, U, miembros de cajones "
            "cerrados y miembros curvos o en arco) sujetos a pandeo lateral "
            "torsional. Las especificaciones de esta sección no se aplican a "
            "aletas en compresión no arriostradas lateralmente de secciones "
            "estables lateralmente. Los perfiles C y Z en los que la aleta en "
            "tensión está sujeta a un tablero de cerramiento se deberán "
            "calcular de acuerdo a la sección F.4.4.6.1.1. Para segmentos no "
            "arriostrados lateralmente de secciones de simetría sencilla, "
            "doble y de punto, sujetas a pandeo lateral torsional la "
            "resistencia nominal a flexión Mn, se calculará como sigue: "
            "Mn = Sc·Fc (F.4.3.3-7). Donde: Sc = Módulo elástico de la "
            "sección efectiva calculado con respecto a la fibra extrema en "
            "compresión sometida a un esfuerzo Fc."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_fc_ecuaciones_8_9",
        "seccion": "F.4.3.3.1.2.1 (Determinación de Fc — 3 rangos según Fe)",
        "titulo": "Fc según el rango de Fe (≥2.78Fy, entre 0.56Fy y 2.78Fy con ecuación F.4.3.3-8, y ≤0.56Fy) y esfuerzo crítico elástico de pandeo lateral torsional Fe.",
        "texto": (
            "Fc se determina como sigue: Para Fe ≥ 2.78Fy — El segmento del "
            "miembro no está sujeto a pandeo lateral torsional para momentos "
            "menores o iguales a My. La resistencia de diseño a flexión se "
            "determinará conforme a la sección F.4.3.3.1.1(a). Para "
            "2.78Fy > Fe > 0.56Fy: Fc = (10/9)·Fy·(1 − 10Fy/(36Fe)) "
            "(F.4.3.3-8). Para Fe ≤ 0.56Fy: Fc = Fe (F.4.3.3-9). Donde: "
            "Fy = esfuerzo de fluencia de diseño determinado de acuerdo con "
            "la sección F.4.1.6.1. Fe = esfuerzo crítico elástico de pandeo "
            "lateral torsional calculado de acuerdo con (a) o (b), a "
            "continuación: (a) Para secciones de simetría sencilla, doble y "
            "de punto: (i) Para flexión alrededor del eje de simetría: para "
            "secciones de simetría sencilla y doble: "
            "Fe = Cb·ro·A·√(σey·σt) / Sf (F.4.3.3-10). Para secciones de "
            "simetría de punto: Fe = Cb·ro·A·√(σey·σt) / (2Sf) (F.4.3.3-11)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_cb_ecuacion_12",
        "seccion": "F.4.3.3.1.2.1 (Factor Cb, ecuación F.4.3.3-12)",
        "titulo": "Coeficiente de flexión Cb en función de los momentos Mmax, MA, MB, MC del segmento no arriostrado.",
        "texto": (
            "Donde: Cb = 12.5·Mmax / (2.5·Mmax + 3MA + 4MB + 3MC) "
            "(F.4.3.3-12). Donde: Mmax = valor absoluto del momento máximo en "
            "el segmento no arriostrado. MA = valor absoluto del momento en el "
            "cuarto del segmento no arriostrado. MB = valor absoluto del "
            "momento en el centro del segmento no arriostrado. MC = valor "
            "absoluto del momento a los tres-cuartos del segmento no "
            "arriostrado. Cb puede ser tomado, de manera conservadora, igual a "
            "la unidad para todos los casos. Para voladizos donde el extremo "
            "libre no está arriostrado, Cb se tomará igual a la unidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_ro_sigmaey_sigmat",
        "seccion": "F.4.3.3.1.2.1 (Radio polar ro y esfuerzos elásticos σey, σt — ecuaciones F.4.3.3-13 a -15)",
        "titulo": "Radio polar de giro ro (ecuación 13), esfuerzo de pandeo flector elástico σey (ecuación 14) y esfuerzo de pandeo torsional σt (ecuación 15).",
        "texto": (
            "ro = radio polar de giro de la sección transversal alrededor del "
            "centro de corte = √(rx² + ry² + xo²) (F.4.3.3-13). Donde: rx, "
            "ry = radios de giro de la sección transversal alrededor de los "
            "ejes centroidales principales. xo = distancia desde el centro de "
            "cortante al centroide, medida a lo largo del eje principal x, se "
            "toma como negativo. A = área transversal completa no reducida. "
            "Sf = módulo elástico de la sección completa no reducida respecto "
            "a la fibra extrema en compresión. σey = π²E / (Ky·Ly/ry)² "
            "(F.4.3.3-14). Donde: E = módulo de elasticidad del acero. "
            "Ky = factor de longitud efectiva para flexión alrededor del eje "
            "y. Ly = longitud no arriostrada del miembro para flexión "
            "alrededor del eje y. σt = (1/(A·ro²))·[GJ + π²E·Cw/(Kt·Lt)²] "
            "(F.4.3.3-15). Donde: G = módulo de cortante. J = constante de "
            "torsión de Saint-Venant de la sección transversal. Cw = "
            "constante de alabeo torsional de la sección transversal. Kt = "
            "factor de longitud efectiva para torsión. Lt = longitud no "
            "arriostrada del miembro para torsión."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_ejes_simetria",
        "seccion": "F.4.3.3.1.2.1 (Ejes de simetría según tipo de sección)",
        "titulo": "Orientación del eje x para secciones de simetría sencilla y de punto, y remisión a fórmulas alternativas para secciones I doble simetría, C simetría sencilla, Z simetría de punto.",
        "texto": (
            "Para secciones de simetría sencilla el eje x es el eje de "
            "simetría orientado de tal forma que el centro de cortante tenga "
            "una coordenada x negativa. Para secciones de simetría de punto, "
            "tales como secciones Z, el eje x debe ser el eje centroidal "
            "perpendicular al alma. Alternativamente, Fe puede ser calculado "
            "usando la ecuación dada en (b) para secciones I de simetría "
            "doble, secciones C de simetría sencilla, o secciones Z de "
            "simetría de punto."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_fe_simetria_sencilla_16_19",
        "seccion": "F.4.3.3.1.2.1 (Fe para secciones de simetría sencilla — ecuaciones F.4.3.3-16 a -19)",
        "titulo": "Fe para flexión alrededor del eje centroidal perpendicular al eje de simetría, factor Cs, σex (ecuación 17), CTF (ecuación 18), constante j (ecuación 19).",
        "texto": (
            "(ii) Para secciones de simetría sencilla con flexión alrededor "
            "del eje centroidal perpendicular al eje de simetría: "
            "Fe = (Cs·A·σex)/(CTF·Sf) · [j + Cs·√(j² + ro²·(σt/σex))] "
            "(F.4.3.3-16). Cs = +1 para momento que produzca compresión en el "
            "lado del centro de corte, medido desde el centroide. Cs = −1 "
            "para momento que produzca tensión en el lado del centro de "
            "corte, medido desde el centroide. σex = π²E / (Kx·Lx/rx)² "
            "(F.4.3.3-17). Donde: Kx = factor de longitud efectiva para "
            "flexión alrededor del eje x. Lx = longitud no arriostrada del "
            "miembro para flexión alrededor del eje x. CTF = 0.6 − "
            "0.4·(M1/M2) (F.4.3.3-18). Donde: M1 es el momento menor y M2 es "
            "el momento mayor en los extremos de la longitud no arriostrada "
            "en el plano de flexión, y donde M1/M2 (relación de momentos en "
            "el extremo) es positiva cuando M1 y M2 tienen el mismo signo "
            "(flexión en curvatura doble) y negativa cuando son de signos "
            "opuestos (flexión en curvatura sencilla). Cuando el momento "
            "flector en cualquier punto dentro de la longitud no arriostrada "
            "es más grande que los momentos en ambos extremos de esta "
            "longitud, CTF será tomado igual a la unidad. "
            "j = (1/(2Iy))·[∫x³dA + ∫xy²dA] − xo (F.4.3.3-19)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_1_fe_alterno_20_21",
        "seccion": "F.4.3.3.1.2.1 (Fe alternativo para flexión alrededor del eje perpendicular al alma — ecuaciones F.4.3.3-20 a -21)",
        "titulo": "Ecuaciones alternativas de Fe para secciones I doble simetría/C simetría sencilla (F.4.3.3-20) y secciones Z simetría de punto (F.4.3.3-21), en flexión alrededor del eje perpendicular al alma.",
        "texto": (
            "(b) Para secciones I, secciones C de simetría sencilla, o "
            "secciones Z sometidas a flexión alrededor del eje centroidal "
            "perpendicular al alma (eje x), se permite el uso de las "
            "siguientes ecuaciones para el cálculo de Fe, en lugar de las "
            "presentadas en el inciso a): Para secciones I con simetría doble "
            "y secciones C de simetría sencilla: Fe = (Cb·π²·E·d·Iyc) / "
            "(Sf·(Ky·Ly)²) (F.4.3.3-20). Para secciones Z con simetría de "
            "punto: Fe = (Cb·π²·E·d·Iyc) / (2Sf·(Ky·Ly)²) (F.4.3.3-21). "
            "Donde: d = altura de la sección. Iyc = momento de inercia de la "
            "porción en compresión de la sección, alrededor del eje "
            "centroidal paralelo al alma, utilizando la sección completa no "
            "reducida. Los otros términos son definidos en (a)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_2_2_3_cajon_tubular_22_27",
        "seccion": "F.4.3.3.1.2.2-F.4.3.3.1.3 (Secciones cajón cerradas y tubulares cilíndricas cerradas)",
        "titulo": "Lu y Fe para secciones cajón (ecuaciones F.4.3.3-22, -23), y Mn=Fc·Sf para tubos cilíndricos con 3 rangos de D/t (ecuaciones F.4.3.3-24 a -27).",
        "texto": (
            "F.4.3.3.1.2.2 — Resistencia al pandeo lateral torsional de "
            "miembros de secciones cajón cerradas — Para miembros en cajón "
            "cerrados, la resistencia nominal a flexión, Mn, se determinará "
            "así: Si la longitud no arriostrada lateralmente del miembro es "
            "menor o igual a Lu, la resistencia nominal a flexión se "
            "determinará utilizando la sección F.4.3.3.1.1. Lu debe ser "
            "calculado como sigue: Lu = 0.36·Cb·π/(Fy·Sf) · √(E·G·J·Iy) "
            "(F.4.3.3-22). Si la longitud no arriostrada lateralmente es "
            "mayor que Lu, la resistencia nominal a flexión se determinará de "
            "acuerdo con la sección F.4.3.3.1.2.1, donde el esfuerzo crítico "
            "de pandeo lateral torsional, Fe, se calcula como sigue: "
            "Fe = (Cb·π)/(Ky·Ly·Sf) · √(E·G·J·Iy) (F.4.3.3-23). Donde: "
            "J = constante torsional de la sección cajón. Iy = momento de "
            "inercia de la sección completa no reducida alrededor de su eje "
            "centroidal paralelo al alma. F.4.3.3.1.3 — Resistencia a flexión "
            "de miembros de sección tubular cilíndrica cerrada — Para "
            "miembros de sección tubular cilíndrica cerrada que tienen una "
            "relación diámetro exterior a espesor de pared, D/t, no mayor a "
            "0.441E/Fy, la resistencia nominal a flexión Mn, se calculará de "
            "acuerdo con la ecuación F.4.3.3-24. Mn = Fc·Sf (F.4.3.3-24). "
            "φb = 0.95. Para D/t ≤ 0.0714E/Fy: Fc = 1.25Fy (F.4.3.3-25). Para "
            "0.0714E/Fy < D/t ≤ 0.318E/Fy: "
            "Fc = [0.970 + 0.020·(E/Fy)/(D/t)]·Fy (F.4.3.3-26). Para "
            "0.318E/Fy < D/t ≤ 0.441E/Fy: Fc = 0.328E/(D/t) (F.4.3.3-27). "
            "Donde: D = diámetro externo del tubo cilíndrico. t = espesor. "
            "Fc = esfuerzo crítico de pandeo flector. Sf = módulo elástico de "
            "la sección transversal completa no reducida respecto a la fibra "
            "extrema en compresión."
        ),
    },
    # ── F.4.3.3.1.4 — Pandeo distorsional ─────────────────────────
    {
        "id": "NSR10-F-F_4_3_3_1_4_intro_28_32",
        "seccion": "F.4.3.3.1.4 (Resistencia al pandeo distorsional — introducción y ecuaciones F.4.3.3-28 a -32)",
        "titulo": "Aplicabilidad (secciones I/Z/C/otras con aletas rigidizadas de borde), Mn según λd (ecuaciones 28-29), y Mcrd (ecuación 32).",
        "texto": (
            "F.4.3.3.1.4 — Resistencia al pandeo distorsional — Las "
            "especificaciones de este numeral aplicarán a secciones I, Z, C y "
            "otros miembros de sección transversal abierta que emplean "
            "aletas en compresión con rigidizadores de borde, con la "
            "excepción de miembros que cumplen el criterio de la sección "
            "F.4.4.6.1.1, F.4.4.6.1.2 cuando se emplea el factor R de la "
            "ecuación F.4.4.6-4, ó sección F.4.4.6.2.1. La resistencia "
            "nominal a flexión se calculará de acuerdo con las ecuaciones "
            "F.4.3.3-28 ó F.4.3.3-29. φb = 0.90. Para λd ≤ 0.673: Mn = My "
            "(F.4.3.3-28). Para λd > 0.673: "
            "Mn = (1 − 0.22·(Mcrd/My)^0.5)·(Mcrd/My)^0.5 · My (F.4.3.3-29). "
            "Donde: λd = √(My/Mcrd) (F.4.3.3-30). My = Sfy·Fy (F.4.3.3-31). "
            "Donde: Sfy = módulo elástico de la sección completa no reducida "
            "respecto a la fibra extrema en la primera fluencia. "
            "Mcrd = Sf·Fd (F.4.3.3-32). Donde: Sf = módulo elástico de la "
            "sección completa no reducida respecto a la fibra extrema en "
            "compresión. Fd = esfuerzo de pandeo elástico distorsional "
            "calculado de acuerdo con cualquiera de las secciones "
            "F.4.3.3.1.4(a), (b) ó (c)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_4_a_simplificada_33_36",
        "seccion": "F.4.3.3.1.4(a) (Disposición simplificada para secciones C y Z no restringidas con pestaña rigidizadora simple)",
        "titulo": "6 límites dimensionales, y ecuaciones F.4.3.3-33 a -36 para Fd, β, Lcr/Lm, y kd.",
        "texto": (
            "(a) Disposición simplificada para secciones C y Z no "
            "restringidas con pestaña rigidizadora simple — Para secciones C "
            "y Z que no tienen restricciones rotacionales en la aleta a "
            "compresión y están dentro de los límites dimensionales "
            "suministrados en esta sección, se permite el uso de la ecuación "
            "F.4.3.3-33 para un cálculo predictivo conservador del esfuerzo "
            "de pandeo distorsional, Fd. Límites: (1) 50 ≤ ho/t ≤ 200. (2) "
            "25 ≤ bo/t ≤ 100. (3) 6.25 < D/t ≤ 50. (4) 45° ≤ θ < 90°. (5) "
            "2 ≤ ho/bo ≤ 8. (6) 0.04 ≤ D·senθ/bo ≤ 0.5. Donde: ho = altura "
            "entre bordes externos del alma. t = espesor del metal base. "
            "bo = ancho de bordes externos de la aleta. D = dimensión entre "
            "bordes externos de la pestaña. θ = ángulo de la pestaña. El "
            "esfuerzo de pandeo distorsional se calcula así: "
            "Fd = β·kd·π²E / (12·(1−μ²)·(t/bo)²) (F.4.3.3-33). Donde: "
            "α (β) = un valor que toma en cuenta el beneficio de una "
            "longitud no arriostrada, Lm, más corta que Lcr, el cual "
            "conservadoramente puede tomarse igual a 1.0. = 1.0 para "
            "Lm ≥ Lcr. = (Lm/Lcr)^ln(Lm/Lcr) para Lm < Lcr (F.4.3.3-34). "
            "Donde: Lm = distancia entre puntos de restricción contra el "
            "pandeo distorsional (para miembros restringidos en forma "
            "continua, Lcr = Lm, sin embargo la restricción puede ser "
            "incluida como un resorte rotacional según F.4.3.3.1.4(b) ó (c). "
            "Lcr = 1.2·ho·(bo·D·senθ/(ho·t))^0.6 ≤ 10ho (F.4.3.3-19bis). "
            "kd = 0.05 ≤ 0.1·(bo·D·senθ/(ho·t))^1.4 ≤ 8.0 (F.4.3.3-36)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_4_bc_complejo_37_39",
        "seccion": "F.4.3.3.1.4(b)-(c) (Rigidizador de borde complejo — ecuaciones F.4.3.3-37 a -39, análisis racional)",
        "titulo": "Fórmula general Fd para secciones con rigidizador complejo (ecuación 37) y Lcr (ecuación 39), y opción de análisis racional elástico (inciso c).",
        "texto": (
            "(b) Para secciones C y Z, sombrero ó cualquier sección abierta "
            "con aletas rigidizadas de igual dimensión donde el rigidizador "
            "es una pestaña (labio) simple o un rigidizador de borde "
            "complejo — Las disposiciones de esta parte aplicarán a cualquier "
            "sección abierta con aletas rigidizadas de igual dimensión, "
            "incluyendo aquellas que cumplen los límites geométricos de la "
            "sección F.4.3.3.1.4(a). Fd = β·(kφfe + kφwe + kφ) / "
            "(K̃φfg + K̃φwg) (F.4.3.3-37). Donde β se calcula igual que en "
            "(a), con Lcr = ((6π⁴ho·(1−μ²)/t³)·(Ixf·(xo−hx)² + Cwf − "
            "(Ixyf²/Iyf)·(xo−hx)²) + π⁴ho⁴/720)^(1/4) (F.4.3.3-39bis) — "
            "remitirse a la sección F.4.3.3.1.4(a) para Lm. Los términos "
            "kφfe, kφwe, kφ, K̃φfg, K̃φwg corresponden a rigideces "
            "rotacionales elásticas y geométricas provistas por la aleta, el "
            "alma, y elementos de restricción a la unión aleta-alma — "
            "remitirse a las ecuaciones F.4.3.3-40 a F.4.3.3-43 para su "
            "cálculo detallado. (c) Análisis racional de pandeo elástico — "
            "Se permitirá el uso de un análisis racional elástico que "
            "considere el pandeo distorsional en lugar de las expresiones "
            "dadas en la sección F.4.3.3.1.4(a) ó (b). Se aplicará el factor "
            "de resistencia de la sección F.4.3.3.1.4."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_4_b_kfe_kwe_40_41",
        "seccion": "F.4.3.3.1.4(b) (Rigideces rotacionales elásticas kφfe, kφwe — ecuaciones F.4.3.3-40, -41)",
        "titulo": "kφfe (rigidez elástica rotacional de la aleta a la unión aleta-alma) y kφwe (rigidez elástica del alma), con las propiedades de aleta+rigidizador involucradas.",
        "texto": (
            "kφfe = rigidez elástica rotacional provista por la aleta a la "
            "unión aleta-alma = (π/L)⁴·[E·Ixf·(xo−hx)² + E·Cwf − "
            "E·(Ixyf²/Iyf)·(xo−hx)²] + (π/L)²·G·Jf (F.4.3.3-40). Donde: "
            "E = módulo de elasticidad del acero. G = módulo de corte. "
            "Jf = constante de torsión de Saint-Venant de la aleta en "
            "compresión, más el rigidizador de borde alrededor de un sistema "
            "coordenado x-y localizado en el centroide de la aleta, con el "
            "eje x positivo y el eje y positivo medido hacia la derecha y "
            "hacia abajo del centroide, respectivamente. Ixf, xo, hx, Cwf, "
            "Ixyf, Iyf son propiedades de la aleta en compresión más el "
            "rigidizador de borde alrededor de ese mismo sistema coordenado. "
            "kφwe = rigidez elástica rotacional provista por el alma a la "
            "unión aleta-alma = (E·t³)/(12·(1−μ²)·ho) (F.4.3.3-41)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_4_b_kphi_kfg_42",
        "seccion": "F.4.3.3.1.4(b) (Rigidez kφ y rigidez geométrica K̃φfg de la aleta — ecuación F.4.3.3-42)",
        "titulo": "kφ (rigidez de un elemento de restricción externo, riostra/panel/tablero) y K̃φfg (rigidez geométrica rotacional de la aleta a partir de la unión aleta-alma).",
        "texto": (
            "kφ = rigidez rotacional provista por un elemento de restricción "
            "(riostra, panel, tablero de cerramiento) a la unión aleta-alma "
            "de un miembro (cero si la aleta en compresión no está "
            "restringida). K̃φfg = rigidez geométrica rotacional (dividida "
            "por el esfuerzo Fd) demandada por la aleta a partir de la unión "
            "aleta-alma = (π/L)²·[Af·((xo−hx)² · (Ixyf/Iyf)² − "
            "2yo·(xo−hx)·(Ixyf/Iyf) + ho² + yo²) + Ixf + Iyf] (F.4.3.3-42). "
            "Donde: Af = área de la sección transversal de la aleta en "
            "compresión más el rigidizador de borde alrededor de un sistema "
            "coordenado x-y localizado en el centroide de la aleta, con el "
            "eje x positivo y el eje y positivo medido hacia la derecha y "
            "hacia abajo del centroide, respectivamente. yo = distancia en y "
            "a partir de la unión aleta-alma hasta el centroide de la aleta."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_1_4_b_kwg_xiweb_43",
        "seccion": "F.4.3.3.1.4(b) (Rigidez geométrica del alma K̃φwg — ecuación F.4.3.3-43, y gradiente de esfuerzo ξweb)",
        "titulo": "K̃φwg (rigidez geométrica del alma, fórmula extensa) y ξweb (gradiente de esfuerzo en el alma en función de f1 y f2, con ejemplo para flexión simétrica pura ξweb=2).",
        "texto": (
            "K̃φwg = rigidez geométrica rotacional (dividida por el esfuerzo "
            "Fd) demandada por el alma a partir de la unión aleta-alma = "
            "(ho·t·π²)/13440 · [([45360·(1−ξweb) + 62160]·(L/ho)² + 448π² + "
            "(ho/L)²·[53+3·(1−ξweb)]·π⁴) / (π⁴ + 28π²·(L/ho)² + "
            "420·(L/ho)⁴)] (F.4.3.3-43). Donde: ξweb = (f1−f2)/f1, gradiente "
            "de esfuerzo en el alma, donde f1 y f2 son los esfuerzos en los "
            "extremos opuestos del alma, f1 > f2, compresión es positiva, "
            "tensión es negativa, y los esfuerzos se calculan sobre la base "
            "de la sección bruta (ej: para la flexión simétrica pura, "
            "f1 = −f2, ξweb = 2)."
        ),
    },
    # ── F.4.3.3.2 — Cortante ────────────────────────────────────
    {
        "id": "NSR10-F-F_4_3_3_2_1_cortante_almas_sin_huecos_44_50",
        "seccion": "F.4.3.3.2.1 (Resistencia al corte de almas sin huecos — ecuaciones F.4.3.3-44 a -50)",
        "titulo": "Vn=Aw·Fv (ecuación 44), 3 rangos de h/t para Fv (ecuaciones 45-47b), Aw=ht (ecuación 48), y coeficiente kv según rigidizadores transversales (ecuaciones 49-50).",
        "texto": (
            "F.4.3.3.2 — Cortante. F.4.3.3.2.1 — Resistencia al corte de "
            "almas sin huecos — La resistencia nominal a cortante, Vn, se "
            "calculará de acuerdo con la ecuación F.4.3.3-44. Vn = Aw·Fv "
            "(F.4.3.3-44). φv = 0.95. (a) Para h/t ≤ √(E·kv/Fy): "
            "Fv = 0.60Fy (F.4.3.3-45). (b) Para √(E·kv/Fy) < h/t ≤ "
            "1.51·√(E·kv/Fy): Fv = 0.60·√(E·kv·Fy) / (h/t) (F.4.3.3-46). "
            "(c) Para h/t > 1.51·√(E·kv/Fy): "
            "Fv = π²·E·kv / (12·(1−μ²)·(h/t)²) = 0.904·E·kv/(h/t)² "
            "(F.4.3.3-47a/b). Donde: Vn = resistencia nominal al corte. "
            "Aw = área del elemento alma = ht (F.4.3.3-48). Donde: h = "
            "altura de la porción plana del alma medida a lo largo de su "
            "plano. t = espesor del alma. Fv = esfuerzo nominal de corte. "
            "E = módulo de elasticidad del acero. kv = coeficiente de "
            "pandeo al corte calculado de acuerdo con: (1) Para almas no "
            "reforzadas, kv=5.34. (2) Para almas con rigidizadores "
            "transversales que satisfacen los requisitos de F.4.3.3.7: "
            "cuando a/h ≤ 1.0, kv = 4.00 + 5.34/(a/h)² (F.4.3.3-49). "
            "cuando a/h > 1.0, kv = 5.34 + 4.00/(a/h)² (F.4.3.3-50). Donde: "
            "a = longitud del panel de corte para el elemento alma no "
            "reforzado, o distancia libre entre rigidizadores transversales "
            "de elementos alma reforzados. Fy = esfuerzo de fluencia de "
            "diseño (F.4.1.6.1). μ = relación de Poisson = 0.3. Cuando el "
            "alma conste de dos o más láminas, cada lámina debe considerarse "
            "como un elemento separado que soporta su parte correspondiente "
            "de cortante."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_2_2_cortante_almas_c_huecos_51_53",
        "seccion": "F.4.3.3.2.2 (Resistencia al corte de almas de secciones C con huecos)",
        "titulo": "8 límites de aplicabilidad, y factor de reducción qs según c/t (ecuaciones F.4.3.3-51 a -53).",
        "texto": (
            "F.4.3.3.2.2 — Resistencia al corte de almas de secciones C con "
            "huecos — Las disposiciones de este numeral serán aplicables "
            "dentro de los siguientes límites: (1) dh/h ≤ 0.7. (2) h/t ≤ 200. "
            "(3) Huecos centrados en la mitad de la altura del alma. (4) "
            "Distancia libre entre huecos ≥ 457 mm. (5) Radio en la esquina "
            "≥ 2t para huecos no circulares. (6) dh ≤ 64 mm y Lh ≤ 114 mm "
            "para huecos no circulares. (7) Diámetro ≤ 152 mm para huecos "
            "circulares. (8) dh > 14 mm. Donde: dh = altura del hueco en el "
            "alma. h = altura la porción plana del alma. t = espesor del "
            "alma. Lh = longitud del hueco en el alma. Para almas de "
            "secciones C con huecos, la resistencia a cortante se calculará "
            "de acuerdo con la sección F.4.3.3.2.1, multiplicada por el "
            "factor de reducción, qs. Cuando c/t ≥ 54: qs = 1.0. Cuando "
            "5 ≤ c/t < 54: qs = c/(54t) (F.4.3.3-51). Donde: "
            "c = h/2 − dh/2.83 para huecos circulares (F.4.3.3-52). "
            "c = h/2 − dh/2 para huecos no circulares (F.4.3.3-53)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_3_flexion_corte_combinados_54_55",
        "seccion": "F.4.3.3.3 (Flexión y corte combinados — DCCR, ecuaciones F.4.3.3-54, -55)",
        "titulo": "Interacción flexión-corte para almas no reforzadas (ecuación 54) y con rigidizadores transversales (ecuación 55).",
        "texto": (
            "F.4.3.3.3 — Flexión y corte combinados. F.4.3.3.3.1 — Método de "
            "Diseño con Coeficientes de Carga y Resistencia (DCCR) — Para "
            "vigas bajo flexión y cortante combinados, la resistencia "
            "requerida a flexión M̄, y la resistencia requerida al corte, "
            "V̄, no deben exceder φb·Mn y φv·Vn, respectivamente. Para vigas "
            "con almas no reforzadas, la resistencia requerida a flexión M̄, "
            "y la resistencia requerida al corte, V̄, deben también "
            "satisfacer la siguiente ecuación de interacción: "
            "√[(M̄/(φb·Mnxo))² + (V̄/(φv·Vn))²] ≤ 1.0 (F.4.3.3-54). Para "
            "vigas con rigidizadores transversales en el alma, cuando "
            "M̄/(φb·Mnxo) > 0.5 y V̄/(φv·Vn) > 0.7, M̄ y V̄ deben también "
            "satisfacer la siguiente ecuación de interacción: "
            "0.6·(M̄/(φb·Mnxo)) + (V̄/(φv·Vn)) ≤ 1.3 (F.4.3.3-55). Donde: "
            "Mn = resistencia nominal cuando solo se considera flexión. "
            "M̄ = resistencia requerida a flexión, M̄=Mu. φb = factor de "
            "resistencia para flexión (F.4.3.3.1.1). Mnxo = resistencia "
            "nominal a flexión alrededor del eje centroidal x determinada de "
            "acuerdo con F.4.3.3.1.1. V̄ = resistencia requerida a cortante, "
            "V̄=Vu. φv = factor de resistencia para cortante (F.4.3.3.2). "
            "Vn = resistencia nominal cuando solo se considera cortante."
        ),
    },
    # ── F.4.3.3.4 — Arrugamiento del alma ──────────────────────
    {
        "id": "NSR10-F-F_4_3_3_4_1_arrugamiento_sin_huecos_56_58",
        "seccion": "F.4.3.3.4.1 (Resistencia a arrugamiento de almas sin huecos — ecuaciones F.4.3.3-56 a -58)",
        "titulo": "Pn (fórmula general con coeficientes de tabla) y Pnc para condición de carga de extremo sobre una aleta con voladizo (ecuación 57, factor α ecuación 58).",
        "texto": (
            "F.4.3.3.4 — Arrugamiento del alma. F.4.3.3.4.1 — Resistencia a "
            "arrugamiento de almas sin huecos — La resistencia nominal a "
            "arrugamiento del alma, Pn, se determinará de acuerdo con la "
            "ecuación F.4.3.3-56 ó F.4.3.3-57, según sea aplicable. Se "
            "usarán los factores de resistencia en las tablas F.4.3.3-1 a "
            "F.4.3.3-5 para la determinación de la resistencia de diseño: "
            "Pn = C·t²·Fy·senθ · (1 − CR·√(R/t)) · (1 + CN·√(N/t)) · "
            "(1 − Ch·√(h/t)) (F.4.3.3-56). Donde: Pn = resistencia nominal a "
            "arrugamiento del alma. C = coeficiente de la tabla F.4.3.3-1 a "
            "F.4.3.3-5. t = espesor del alma. Fy = esfuerzo de fluencia de "
            "diseño (F.4.1.6.1). θ = ángulo entre el plano del alma y el "
            "plano de la superficie de soporte, 45°≤θ≤90°. CR = coeficiente "
            "de radio de doblez interno de la tabla. R = radio de doblez "
            "interno. CN = coeficiente de longitud de apoyo de la carga. "
            "N = longitud de apoyo de la carga (mínimo 19 mm). Ch = "
            "coeficiente de esbeltez del alma de la tabla. h = dimensión "
            "plana del alma. Alternativamente, para la condición de carga de "
            "extremo sobre una aleta en una sección C ó Z, la resistencia "
            "nominal a arrugamiento del alma, Pnc, con voladizo sobre un "
            "lado, puede calcularse así, excepto que Pnc no debe ser mayor "
            "al valor obtenido para la condición de carga interior sobre una "
            "aleta: Pnc = α·Pn (F.4.3.3-57). Donde: α = "
            "1.34·(Lo/h)^0.26 / (0.009·(h/t)+0.3) ≥ 1.0 (F.4.3.3-58). "
            "Donde: Lo = longitud del voladizo medido desde el borde del "
            "apoyo hasta el extremo del miembro."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_4_1_terminologia_pn_pnc",
        "seccion": "F.4.3.3.4.1 (Terminología de casos de carga: aleta simple/doble, extremo/interior)",
        "titulo": "Definiciones de 'carga sobre una aleta', 'carga sobre las dos aletas', 'carga de extremo' y 'carga interior' según distancia entre bordes de aplicación de carga y apoyos.",
        "texto": (
            "El uso de la ecuación F.4.3.3-57 se limita a 0.5 ≤ Lo/h ≤ 1.5 y "
            "h/t ≤ 154. Para Lo/h ó h/t fuera de estos límites, α=1.0. Las "
            "almas de miembros a flexión con relación h/t mayor a 200 deben "
            "ser provistas con los medios adecuados para la transmisión de "
            "cargas concentradas o reacciones directamente sobre estas. Pn y "
            "Pnc representan las resistencias nominales para la carga o "
            "reacción de un alma sólida conectada a la aleta superior e "
            "inferior de un perfil. Se utiliza el término carga sobre una "
            "aleta o reacción sobre una aleta cuando la distancia entre los "
            "bordes de las áreas de aplicación de las cargas concentradas "
            "opuestas adyacentes o las reacciones es igual o mayor a 1.5h. "
            "Se utiliza carga sobre las dos aletas o reacción sobre las dos "
            "aletas cuando la distancia entre los bordes de las áreas de "
            "aplicación de las cargas concentradas opuestas adyacentes a las "
            "reacciones es menor a 1.5h. Se utiliza carga de extremo o "
            "reacción de extremo cuando la distancia entre el borde del área "
            "cargada y el extremo del miembro es igual o menor a 1.5h. Se "
            "utiliza carga interior o reacción interior cuando la distancia "
            "entre el borde del área cargada y el extremo del miembro es "
            "mayor a 1.5h, excepto cuando se especifique algo diferente."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_4_1_tablas_1_5_resumen",
        "seccion": "F.4.3.3.4.1 (Tablas F.4.3.3-1 a F.4.3.3-5 — factores de resistencia y coeficientes)",
        "titulo": "Resumen de las 5 tablas de coeficientes C/CR/CN/Ch/φw para secciones armadas espalda con espalda, secciones canal/C, secciones Z, sombrero sencillo y tablero de almas múltiples, según condición de apoyo/aleta y caso de carga.",
        "texto": (
            "Tabla F.4.3.3-1 aplica para vigas I constituidas por dos "
            "canales conectados espalda con espalda donde h/t≤200, N/t≤210, "
            "N/h≤1.0 y θ=90°. Tabla F.4.3.3-2 aplica a secciones canal con "
            "almas sencillas y miembros en sección C donde h/t≤200, N/t≤210, "
            "N/h≤2.0 y θ=90°. Para carga interior, o reacción, sobre las dos "
            "aletas sujetas al apoyo, la distancia desde el borde del apoyo "
            "de la carga al extremo del miembro se extenderá al menos 2.5h. "
            "Para los casos de aletas no sujetas, la distancia desde el "
            "borde del apoyo de la carga al extremo del miembro se extenderá "
            "al menos 1.5h. Tabla F.4.3.3-3 aplica a secciones Z con almas "
            "sencillas donde h/t≤200, N/t≤210, N/h≤2.0 y θ=90°, mismas "
            "condiciones de extensión que la tabla anterior. Tabla "
            "F.4.3.3-4 aplica a miembros con sección sombrero sencillo donde "
            "h/t≤200, N/t≤200, N/h≤2 y θ=90°. Tabla F.4.3.3-5 aplica a "
            "miembros con secciones tablero de almas múltiples donde "
            "h/t≤200, N/t≤210, N/h≤3, y 45°≤θ≤90°. Cada tabla desglosa los "
            "coeficientes C, CR, CN, Ch, φw y los límites de aplicabilidad "
            "(R/t) según condición de apoyo (sujeta/no sujeta al apoyo), "
            "condición de aleta (rigidizada/parcialmente rigidizada/no "
            "rigidizada), y caso de carga (extremo/interior, una aleta/dos "
            "aletas)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_4_2_arrugamiento_c_huecos_59_60",
        "seccion": "F.4.3.3.4.2 (Resistencia al arrugamiento de almas de secciones C con huecos — ecuaciones F.4.3.3-59, -60)",
        "titulo": "9 límites de aplicabilidad, y factor de reducción Rc para reacción de extremo (ecuación 59) e interior (ecuación 60) sobre una sola aleta.",
        "texto": (
            "F.4.3.3.4.2 — Resistencia al arrugamiento de almas de secciones "
            "C con huecos — Cuando un hueco en el alma queda dentro de la "
            "longitud de soporte, debe utilizarse un rigidizador de apoyo. "
            "Para vigas con huecos, la resistencia al arrugamiento debe "
            "calcularse utilizando la sección F.4.3.3.4.1, multiplicando el "
            "valor obtenido por el factor de reducción, Rc, dado en esta "
            "sección. Límites: (1) dh/h ≤ 0.7. (2) h/t ≤ 200. (3) Huecos "
            "centrados en la mitad de la altura del alma. (4) Distancia "
            "libre entre huecos ≥ 457 mm (18 pulgadas). (5) Distancia entre "
            "el extremo del miembro y el borde del hueco ≥ d. (6) Radio en "
            "la esquina ≥ 2t para huecos no circulares. (7) dh ≤ 64 mm (2.5 "
            "pulgadas) y Lh ≤ 114 mm (4.5 pulgadas) para huecos no "
            "circulares. (8) Diámetro ≤ 152 mm (6 pulgadas) para huecos "
            "circulares. (9) dh > 14 mm (9/16 pulgada). Donde: dh = altura "
            "del hueco en el alma. h = altura de la porción plana del alma. "
            "t = espesor del alma. d = altura de la sección transversal. "
            "Lh = longitud del hueco en el alma. Para reacción en el "
            "extremo sobre una sola aleta (ecuación F.4.3.3-56 con la tabla "
            "F.4.3.3-2), cuando ninguna porción de un hueco en el alma está "
            "dentro de la longitud del apoyo, el factor de reducción, Rc, se "
            "calculará como sigue: "
            "Rc = 1.01 − 0.325·dh/h + 0.083·x/h ≤ 1.0 (F.4.3.3-59). "
            "N ≥ 25 mm. Para reacción interior sobre una sola aleta "
            "(ecuación F.4.3.3-56 con la tabla F.4.3.3-2) cuando cualquier "
            "porción de un hueco en el alma no está dentro de la longitud "
            "del apoyo, el factor de reducción, Rc, se calculará así: "
            "Rc = 0.90 − 0.047·dh/h + 0.053·x/h ≤ 1.0 (F.4.3.3-60). "
            "N ≥ 76 mm (3 pulgadas). Donde: x = distancia más corta entre el "
            "hueco en el alma y el borde del área de aplicación de la "
            "carga. N = longitud de apoyo de la carga."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_5_flexion_arrugamiento_61_63",
        "seccion": "F.4.3.3.5 (Flexión y arrugamiento del alma combinados — ecuaciones F.4.3.3-61 a -63)",
        "titulo": "3 ecuaciones de interacción DCCR: almas sencillas no reforzadas (61), almas múltiples tipo I armadas de dos C (62), y dos secciones Z traslapadas sobre el apoyo (63, con límites y 4 condiciones geométricas).",
        "texto": (
            "F.4.3.3.5 — Flexión y arrugamiento del alma combinados. "
            "F.4.3.3.5.1 — Método de Diseño con Coeficientes de Carga y "
            "Resistencia (DCCR) — Para almas planas no reforzadas de "
            "secciones sujetas a la combinación de flexión y carga "
            "concentrada o reacción, se diseñará de tal forma que el "
            "momento, M̄, y la carga concentrada o reacción, P̄, satisfagan "
            "las relaciones M̄≤φb·Mnxo, y P̄≤φw·Pn. Adicionalmente: (a) Para "
            "secciones con almas sencillas no reforzadas: "
            "0.91·(P̄/Pn) + (M̄/Mnxo) ≤ 1.33φ (F.4.3.3-61). Donde φ=0.90. "
            "Excepción: en los apoyos interiores de luces continuas, la "
            "anterior ecuación no es aplicable a tableros metálicos o vigas "
            "con dos o más almas sencillas, cuando la parte en compresión de "
            "las almas adyacentes estén lateralmente soportadas en la región "
            "del momento negativo por elementos continuos o intermitentes "
            "conectados a la aleta, chapas rígidas o arriostramiento "
            "lateral, y el espaciamiento entre almas adyacentes no exceda "
            "254mm. (b) Para secciones con almas múltiples no reforzadas "
            "tales como vigas tipo I armadas de dos secciones C conectadas "
            "espalda con espalda, o secciones similares las cuales proveen "
            "un alto grado de restricción al giro del alma (tales como "
            "secciones I armadas por dos ángulos soldados a una sección C): "
            "0.88·(P̄/Pn) + (M̄/Mnxo) ≤ 1.46φ (F.4.3.3-62). Donde φ=0.90. "
            "(c) Para dos secciones Z traslapadas sobre el apoyo: "
            "0.86·(P̄/Pn) + (M̄/Mnxo) ≤ 1.65φ (F.4.3.3-63). Donde φ=0.90. La "
            "ecuación anterior es válida para secciones dentro de los "
            "siguientes límites: h/t≤150, N/t≤140, Fy≤483 MPa, R/t≤5.5. "
            "Deben satisfacerse también: (1) El extremo final de un miembro "
            "debe conectarse al otro por al menos dos tornillos A307 con "
            "diámetro de 12.7mm a través del alma. (2) La sección combinada "
            "en el traslapo se conectará al apoyo por al menos dos tornillos "
            "A307 con diámetro de 12.7mm a través de las aletas. (3) Las "
            "almas de las dos secciones estarán en contacto. (4) La relación "
            "entre el mayor espesor y el menor espesor del conjunto no "
            "excederá 1.3."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_6_flexion_torsion_64",
        "seccion": "F.4.3.3.6 (Cargas de flexión y torsión combinadas — ecuación F.4.3.3-64)",
        "titulo": "Factor de reducción R para miembros bajo flexión no restringidos lateralmente sujetos a cargas de flexión y torsión simultáneas.",
        "texto": (
            "F.4.3.3.6 — Cargas de flexión y torsión combinadas — Para "
            "miembros bajo flexión no restringidos lateralmente, sujetos a "
            "cargas de flexión y torsión simultáneamente, la resistencia "
            "disponible a flexión (resistencia a momento multiplicada por un "
            "factor) calculada de acuerdo con la sección F.4.3.3.1.1(a) debe "
            "ser reducida al ser multiplicada por un factor de reducción, R. "
            "Como se especifica en la ecuación F.4.3.3-64, el factor de "
            "reducción, R, será igual a la relación de los esfuerzos "
            "normales debido a solo la flexión dividido por los esfuerzos "
            "combinados de ambos, flexión y alabeo torsional, en el punto de "
            "esfuerzo combinado máximo de la sección transversal. "
            "R = fflexión / (fflexión + ftorsión) ≤ 1.0 (F.4.3.3-64). Los "
            "esfuerzos deben calcularse utilizando las propiedades de la "
            "sección completa para los esfuerzos torsionales y las "
            "propiedades de la sección efectiva para los esfuerzos por "
            "flexión. Para secciones C de aletas con bordes rigidizados, si "
            "el máximo esfuerzo de compresión combinado ocurre en la unión "
            "del alma con la aleta se puede incrementar el factor R en un "
            "15%, pero nunca será mayor a la unidad (1.0). Las disposiciones "
            "de esta sección no aplicarán cuando se utilicen las "
            "especificaciones de los numerales F.4.4.6.1.1 y F.4.4.6.1.2."
        ),
    },
    # ── F.4.3.3.7 — Rigidizadores ──────────────────────────────
    {
        "id": "NSR10-F-F_4_3_3_7_1_rigidizadores_apoyo_65_71",
        "seccion": "F.4.3.3.7.1 (Rigidizadores de apoyo — ecuaciones F.4.3.3-65 a -71)",
        "titulo": "Pn=menor de dos valores (ecuación 65), área efectiva Ac según posición (66-67), área bruta Ab (68-69), ancho b1/b2 (70-71).",
        "texto": (
            "F.4.3.3.7 — Rigidizadores. F.4.3.3.7.1 — Rigidizadores de apoyo "
            "— Los rigidizadores (transversales) de apoyo, anexos a las "
            "almas de vigas en los puntos de cargas concentradas, o "
            "reacciones, se diseñarán como miembros en compresión. Las "
            "cargas concentradas, o reacciones, se aplicarán directamente en "
            "los rigidizadores, o cada rigidizador será ajustado exactamente "
            "a la porción plana de la aleta de tal manera que la carga se "
            "apoye directamente sobre el extremo de este. Se proveerán los "
            "mecanismos para transferencia de cortante entre el rigidizador "
            "y el alma, de acuerdo a las especificaciones de F.4.5. Para "
            "carga concentrada, o reacciones, la resistencia nominal es "
            "igual a Pn, donde Pn es el valor más pequeño obtenido entre (a) "
            "y (b) de este numeral. φc = 0.85. (a) Pn = Fwy·Ac "
            "(F.4.3.3-65). (b) Pn = resistencia nominal axial evaluada de "
            "acuerdo con la sección F.4.3.4.1(a), con Ae reemplazado por Ab. "
            "Donde: Fwy = valor menor de Fy para almas de vigas, o Fys para "
            "la sección del rigidizador. Para rigidizadores de apoyo en "
            "soportes interiores o bajo cargas concentradas: "
            "Ac = 18t² + As (F.4.3.3-66). Para rigidizadores de apoyo en "
            "soportes de extremos: Ac = 10t² + As (F.4.3.3-67). Donde: "
            "t = espesor del acero base del alma de la viga. As = área de "
            "la sección transversal del rigidizador de apoyo. Para "
            "rigidizadores de apoyo en soportes interiores o bajo cargas "
            "concentradas: Ab = b1·t + As (F.4.3.3-68). Para rigidizadores "
            "de apoyo en soportes de extremos: Ab = b2·t + As "
            "(F.4.3.3-69). Donde: b1 = 25t·[0.0024·(Lst/t)+0.72] ≤ 25t "
            "(F.4.3.3-70). b2 = 12t·[0.0044·(Lst/t)+0.83] ≤ 12t "
            "(F.4.3.3-71). Donde: Lst = longitud del rigidizador de apoyo. "
            "La relación w/ts para los elementos rigidizados y no "
            "rigidizados de los rigidizadores de apoyo no excederá "
            "1.28√(E/Fys) y 0.42√(E/Fys), respectivamente, donde Fys es el "
            "esfuerzo de fluencia, y ts es el espesor del rigidizador de "
            "acero."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_7_2_rigidizadores_secc_c_72",
        "seccion": "F.4.3.3.7.2 (Rigidizadores de apoyo en miembros en sección C a flexión — ecuación F.4.3.3-72)",
        "titulo": "Pn=0.7(Pwc+Ae·Fy) para carga sobre las dos aletas con rigidizadores que no cumplen F.4.3.3.7.1, y 6 requisitos geométricos del rigidizador.",
        "texto": (
            "F.4.3.3.7.2 — Rigidizadores de apoyo en miembros en sección C "
            "a flexión — Para carga sobre las dos aletas de miembros en "
            "sección C bajo flexión, con rigidizadores de apoyo que no "
            "cumplan los requerimientos de la sección F.4.3.3.7.1, la "
            "resistencia nominal, Pn, se determinará de acuerdo con la "
            "ecuación F.4.3.3-72. Pn = 0.7·(Pwc + Ae·Fy) ≥ Pwc "
            "(F.4.3.3-72). φc = 0.90. Donde: Pwc = resistencia nominal a "
            "arrugamiento del alma para miembros en sección C a flexión, "
            "calculada de acuerdo con la ecuación F.4.3.3-56 para miembros "
            "con almas sencillas, en puntos extremos o interiores. Ae = "
            "área efectiva del rigidizador de apoyo sujeto a esfuerzos de "
            "compresión uniforme, calculada en el esfuerzo de fluencia. "
            "Fy = esfuerzo de fluencia del acero del rigidizador de apoyo. "
            "La ecuación F.4.3.3-72 aplica para los siguientes límites: (1) "
            "Se requiere apoyo completo del rigidizador. Si el ancho del "
            "apoyo es más angosto que el ancho de rigidizador de tal forma "
            "que una de las aletas del rigidizador se considere no apoyada, "
            "Pn se reducirá en un 50%. (2) Los rigidizadores serán en "
            "sección C o canal con una altura mínima del alma base de 89mm "
            "y espesor mínimo del acero base de 0.84mm. (3) El rigidizador "
            "se sujetará al alma del miembro en flexión con un mínimo de 3 "
            "tornillos o pernos. (4) La distancia desde las aletas del "
            "miembro a flexión al primer tornillo no será menor a d/8 donde "
            "d es la altura total del miembro en flexión. (5) La longitud "
            "del rigidizador no será menor que la altura del miembro en "
            "flexión menos 9mm. (6) El ancho de apoyo no será menor a "
            "38mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_3_7_3_4_rigidizadores_cortante_73_78",
        "seccion": "F.4.3.3.7.3-F.4.3.3.7.4 (Rigidizadores de cortante — ecuaciones F.4.3.3-73 a -78, y rigidizadores que no cumplen los requisitos)",
        "titulo": "Momento de inercia mínimo real Ismin (73), área bruta Ast (74) con Cv (75-76) y kv (77-78); rigidizadores fuera de estos requisitos se calculan por ensayo o análisis racional.",
        "texto": (
            "F.4.3.3.7.3 — Rigidizadores de cortante — En aquellas zonas "
            "donde se requieran rigidizadores de cortante, el espaciamiento "
            "se basará en la resistencia nominal a cortante, Vn, permitida "
            "en la sección F.4.3.3.2, y la relación a/h no excederá el "
            "valor de [260/(h/t)]² ni 3.0. El momento de inercia real, Is, "
            "de un par de rigidizadores de cortante conectados, o un "
            "rigidizador de cortante sencillo, con referencia a un eje en "
            "el plano del alma, deberá tener un valor mínimo de: "
            "Ismin = 5·h·t³·[h/a − 0.7·(a/h)] ≥ (h/50)⁴ (F.4.3.3-73). "
            "Donde: t y h se definen de acuerdo a la sección F.4.2.1.2. "
            "a = distancia entre rigidizadores de cortante. El área bruta "
            "de los rigidizadores de cortante no será menor a: "
            "Ast = ((1−Cv)/2)·[a/h − (a/h)²/√((a/h)²+1+(a/h))]·Y·D·h·t "
            "(F.4.3.3-74). Donde: Cv = 1.53·E·kv/(Fy·(h/t)²) cuando "
            "Cv ≤ 0.8 (F.4.3.3-75). Cv = 1.11/(h/t)·√(E·kv/Fy) cuando "
            "Cv > 0.8 (F.4.3.3-76). Donde: kv = 4.00 + 5.34/(a/h)² cuando "
            "a/h ≤ 1.0 (F.4.3.3-77). kv = 5.34 + 4.00/(a/h)² cuando a/h > "
            "1.0 (F.4.3.3-78). Y = esfuerzo de fluencia del acero del alma / "
            "esfuerzo de fluencia del acero del rigidizador. D=1.0 para "
            "rigidizadores dispuestos en pares. D=1.8 para rigidizadores de "
            "ángulo sencillo. D=2.4 para rigidizadores de placa sencilla. "
            "F.4.3.3.7.4 — Rigidizadores que no cumplen estos requisitos — "
            "La resistencia de diseño de miembros con rigidizadores que no "
            "cumplen los requisitos de la sección F.4.3.3.7.1, F.4.3.3.7.2 "
            "y F.4.3.3.7.3, tales como rigidizadores hechos con acero "
            "estampado o laminado, se determinará mediante ensayos de "
            "acuerdo con F.4.6 o análisis racional de ingeniería de acuerdo "
            "con la sección F.4.1.2."
        ),
    },
    # ── F.4.3.4 — Compresión concéntrica ───────────────────────
    {
        "id": "NSR10-F-F_4_3_4_1_1_fluencia_pandeo_1_4",
        "seccion": "F.4.3.4.1.1 (Resistencia nominal por fluencia, pandeo flector — ecuaciones F.4.3.4-1 a -4)",
        "titulo": "Pn=Ae·Fn (ecuación 1), Fn según λc (ecuaciones 2-3), λc (ecuación 4), y área efectiva Ae con excepción para huecos ≤1.5% de longitud efectiva.",
        "texto": (
            "F.4.3.4 — MIEMBROS EN COMPRESIÓN CARGADOS CONCÉNTRICAMENTE — La "
            "resistencia de diseño a carga axial debe ser el menor valor de "
            "los calculados de acuerdo con las secciones F.4.3.4.1, "
            "F.4.3.4.2, F.4.4.1.2, F.4.4.6.1.3, y F.4.4.6.1.4, según sea "
            "aplicable. F.4.3.4.1 — Resistencia nominal por fluencia, "
            "pandeo flector, pandeo flexo-torsional y torsional — Esta "
            "sección se aplica a miembros cuya resultante de todas las "
            "cargas actuantes sobre el miembro es una carga axial que pasa "
            "a través del centroide de la sección efectiva calculada para "
            "el esfuerzo, Fn, definido en esta parte del Reglamento. (a) La "
            "resistencia nominal bajo carga axial Pn, se calculará de "
            "acuerdo con la ecuación F.4.3.4-1. Pn = Ae·Fn (F.4.3.4-1). "
            "φc = 0.85. Donde: Ae = área efectiva calculada con el esfuerzo "
            "Fn. Para secciones con huecos circulares, Ae debe determinarse "
            "de acuerdo con la sección F.4.2.2.2(a), sujeta a las "
            "limitaciones de esa sección. Si el número de huecos en la "
            "región de longitud efectiva multiplicado por el diámetro del "
            "hueco y dividido por la longitud efectiva no excede 0.015, Ae "
            "se puede determinar ignorando los huecos. Para miembros "
            "tubulares cilíndricos cerrados, Ae se calculará de acuerdo con "
            "F.4.3.4.1.5. Fn se determina así: Para λc ≤ 1.5: "
            "Fn = (0.658^λc²)·Fy (F.4.3.4-2). Para λc > 1.5: "
            "Fn = (0.877/λc²)·Fy (F.4.3.4-3). Donde: λc = √(Fy/Fe) "
            "(F.4.3.4-4). Fe = es el valor mínimo del esfuerzo de pandeo "
            "flector elástico, de pandeo torsional y de pandeo "
            "flexo-torsional determinado de acuerdo con las secciones "
            "F.4.3.4.1.1 a la F.4.3.4.1.5."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_1_1_no_torsional_5",
        "seccion": "F.4.3.4.1.1 (Secciones no sujetas a pandeo torsional o flexo-torsional — ecuación F.4.3.4-5)",
        "titulo": "Fe=π²E/(KL/r)² para secciones de simetría doble/cerradas, y el criterio del factor K para pórticos arriostrados/no arriostrados.",
        "texto": (
            "F.4.3.4.1.1 — Secciones no sujetas a pandeo torsional o "
            "flexo-torsional — Para secciones de simetría doble, secciones "
            "cerradas o cualquier otra sección para la cual se puede "
            "demostrar que no está sujeta a pandeo torsional o "
            "flexo-torsional, el esfuerzo de pandeo flector elástico, Fe, se "
            "determinará como sigue: Fe = π²E / (KL/r)² (F.4.3.4-5). Donde: "
            "E = módulo de elasticidad del acero. K = factor de longitud "
            "efectiva. L = longitud no arriostrada lateralmente del "
            "miembro. r = radio de giro de la sección transversal completa "
            "no reducida alrededor del eje de pandeo. En pórticos donde la "
            "estabilidad lateral sea provista por arriostramiento diagonal, "
            "muros de cortante, sujeciones a estructuras adyacentes con "
            "adecuada estabilidad lateral, o por tableros de pisos o "
            "tableros de cubiertas asegurados horizontalmente por muros o "
            "sistemas de riostras paralelos al plano del pórtico, y en "
            "cerchas, el factor de longitud efectiva, K, para el miembro en "
            "compresión, el cual no depende de su propia rigidez a flexión "
            "para la estabilidad lateral del pórtico o cercha, se tomará "
            "igual a la unidad, a menos que un análisis muestre que un "
            "menor valor pueda ser utilizado. En un pórtico que dependa de "
            "su propia rigidez a flexión para la estabilidad lateral, la "
            "longitud efectiva, KL, del miembro en compresión se determinará "
            "por un método racional y no será menor que la longitud real no "
            "arriostrada."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_1_2_sencilla_flexotorsional_6_8",
        "seccion": "F.4.3.4.1.2 (Secciones de simetría sencilla sujetas a pandeo flexo-torsional — ecuaciones F.4.3.4-6 a -8)",
        "titulo": "Fe (fórmula exacta y estimación conservadora), factor β, y remisiones para secciones de simetría doble sujetas a pandeo torsional y secciones angulares.",
        "texto": (
            "F.4.3.4.1.2 — Secciones de simetría doble y simetría sencilla "
            "sujetas a pandeo torsional o flexo-torsional — Para secciones "
            "de simetría sencilla sujetas a pandeo flexo-torsional, Fe se "
            "tomará como el menor valor de Fe calculado de acuerdo a la "
            "sección F.4.3.4.1.1 y Fe calculado como sigue: "
            "Fe = (1/(2β))·[(σex+σt) − √((σex+σt)² − 4β·σex·σt)] "
            "(F.4.3.4-6). Alternativamente, se puede obtener una estimación "
            "conservadora de Fe a partir de la siguiente ecuación: "
            "Fe = σt·σex / (σt+σex) (F.4.3.4-7). Donde: β = 1 − (xo/ro)² "
            "(F.4.3.4-8). σt y σex se definen en la sección F.4.3.3.1.2.1. "
            "Para secciones de simetría sencilla, se supone el eje x como "
            "eje de simetría. Para secciones de simetría doble sujetas a "
            "pandeo torsional, Fe se tomará como el menor valor de Fe "
            "calculado de acuerdo a la sección F.4.3.4.1.1 y Fe=σt, donde σt "
            "se define en la sección F.4.3.3.1.2.1. Para secciones de "
            "simetría sencilla en ángulo en las cuales el área efectiva (Ae) "
            "para el esfuerzo Fy es igual al área completa de la sección "
            "transversal no reducida (A), Fe se calculará utilizando la "
            "ecuación F.4.3.4-5 donde r es el radio de giro mínimo."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_1_3_4_5_punto_asimetrica_tubular",
        "seccion": "F.4.3.4.1.3-F.4.3.4.1.5 (Secciones de simetría de punto, no simétricas, y tubulares cilíndricas cerradas)",
        "titulo": "Fe para secciones de simetría de punto (menor entre σt y F.4.3.4.1.1 con eje principal menor), análisis racional para secciones no simétricas, y Ae para tubos cilíndricos (ecuaciones F.4.3.4-9 a -11).",
        "texto": (
            "F.4.3.4.1.3 — Secciones de simetría de punto — Para secciones "
            "de simetría de punto, Fe se tomará como el menor valor entre "
            "σt, como se define en la sección F.4.3.3.1.2.1 y Fe como se "
            "calcula en la sección F.4.3.4.1.1 utilizando el eje principal "
            "menor de la sección. F.4.3.4.1.4 — Secciones no simétricas — "
            "Para miembros cuyas secciones transversales no poseen ninguna "
            "simetría, sea alrededor de un eje o de un punto, Fe se "
            "determinará por medio de un análisis racional. "
            "Alternativamente, a los miembros en compresión con tales "
            "secciones transversales se les podrá realizar ensayos de "
            "comportamiento de acuerdo con lo especificado en la sección "
            "F.4.6. F.4.3.4.1.5 — Secciones tubulares cilíndricas cerradas "
            "— Para miembros tubulares cilíndricos cerrados que tienen una "
            "relación diámetro externo a espesor de pared, D/t, no mayor a "
            "0.441E/Fy y en los cuales la resultante de todas las cargas y "
            "momentos actuantes son equivalentes a una fuerza puntual en la "
            "dirección del eje de miembro pasando a través del centroide de "
            "la sección, el esfuerzo de pandeo flector, Fe, se calculará de "
            "acuerdo con la sección F.4.3.4.1.1, y el área efectiva, Ae, se "
            "calculará como sigue: Ae = Ao + R·(A−Ao) (F.4.3.4-9). Donde: "
            "Ao = [0.037/((D·Fy)/(tE)) + 0.667]·A ≤ A para D/t ≤ "
            "0.441E/Fy (F.4.3.4-10). D = diámetro externo del tubo "
            "cilíndrico. Fy = esfuerzo de fluencia. t = espesor. E = módulo "
            "de elasticidad del acero. A = área de la sección transversal "
            "completa no reducida. R = Fy/(2Fe) ≤ 1.0 (F.4.3.4-11)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_2_pandeo_distorsional_12_20",
        "seccion": "F.4.3.4.2 (Resistencia al pandeo distorsional — ecuaciones F.4.3.4-12 a -20)",
        "titulo": "Pn según λd (ecuaciones 12-13), Pcrd (ecuación 16), y disposición simplificada (a) para secciones C/Z con pestaña rigidizadora simple con Fd, α, Lcr, kd (ecuaciones 17-20).",
        "texto": (
            "F.4.3.4.2 — Resistencia al pandeo distorsional — Las "
            "especificaciones de este numeral aplicarán a secciones I, Z, "
            "C, sombrero, y otros miembros de sección transversal abierta "
            "que empleen aletas con rigidizadores de borde, con la "
            "excepción de miembros que cumplen el criterio de la sección "
            "F.4.4.6.1.2. La resistencia nominal bajo carga axial se "
            "calculará de acuerdo con las ecuaciones F.4.3.4-12 y "
            "F.4.3.4-13. φc = 0.85. Para λd ≤ 0.561: Pn = Py "
            "(F.4.3.4-12). Para λd > 0.561: "
            "Pn = (1 − 0.25·(Pcrd/Py)^0.6)·(Pcrd/Py)^0.6·Py "
            "(F.4.3.4-13). Donde: λd = √(Py/Pcrd) (F.4.3.4-14). "
            "Pn = resistencia nominal axial. Py = Ag·Fy (F.4.3.4-15). "
            "Donde: Ag = área bruta de la sección transversal. Fy = "
            "esfuerzo de fluencia. Pcrd = Ag·Fd (F.4.3.4-16). Donde: "
            "Fd = Esfuerzo de pandeo distorsional elástico calculado de "
            "acuerdo con la sección F.4.3.4.2(a), (b) ó (c). (a) "
            "Disposición simplificada para secciones C y Z no restringidas "
            "con pestaña rigidizadora simple — Para secciones C y Z que no "
            "tienen restricciones rotacionales en la aleta a compresión, y "
            "que están dentro de los límites dimensionales indicados en "
            "esta sección, se permite el uso de la ecuación F.4.3.4-17 para "
            "un cálculo predictivo conservador del esfuerzo de pandeo "
            "distorsional, Fd. Serán aplicables los siguientes límites "
            "dimensionales: (1) 50 ≤ ho/t ≤ 200."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_2_a_limites_ecs17_20",
        "seccion": "F.4.3.4.2(a) (Límites 2-6 y ecuaciones F.4.3.4-17 a -20 para pandeo distorsional simplificado)",
        "titulo": "Límites 2-6 restantes, ecuación Fd (17), factor α con Lm/Lcr (18), Lcr (19) y kd (20).",
        "texto": (
            "(2) 25 ≤ bo/t ≤ 100. (3) 6.25 < D/t ≤ 50. (4) 45° ≤ θ < 90°. "
            "(5) 2 ≤ ho/bo ≤ 8. (6) 0.04 ≤ D·senθ/bo ≤ 0.5. Donde: ho = "
            "altura entre bordes externos del alma. t = espesor del metal "
            "base. bo = ancho de bordes externos de la aleta. D = dimensión "
            "entre bordes externos de la pestaña. θ = ángulo de la "
            "pestaña. El esfuerzo de pandeo distorsional se calculará como "
            "sigue: Fd = α·kd·π²E / (12·(1−μ²)·(t/bo)²) (F.4.3.4-17). "
            "Donde: α = un valor que toma en cuenta el beneficio de una "
            "longitud no arriostrada, Lm, más corta que Lcr, el cual, "
            "conservadoramente, puede tomarse igual a 1.0. = 1.0 para "
            "Lm ≥ Lcr. = (Lm/Lcr)^ln(Lm/Lcr) para Lm < Lcr (F.4.3.4-18). "
            "Donde: Lm = distancia entre puntos de restricción contra el "
            "pandeo distorsional (para miembros restringidos en forma "
            "continua, Lcr=Lm, sin embargo la restricción puede ser "
            "incluida como un resorte rotacional, kφ, de acuerdo a las "
            "disposiciones de la sección F.4.3.4.2(b) ó (c)). "
            "Lcr = 1.2·ho·(bo·D·senθ/(ho·t))^0.6 ≤ 10ho (F.4.3.4-19). "
            "kd = 0.5 ≤ 0.1·(bo·D·senθ/(ho·t))^0.7 ≤ 8.0 (F.4.3.4-20)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_4_2_bc_complejo_21_24",
        "seccion": "F.4.3.4.2(b)-(c) (Rigidizador de borde complejo — ecuaciones F.4.3.4-21 a -24, y análisis racional)",
        "titulo": "Fd para secciones C/Z/sombrero con rigidizador complejo (fórmula general 21), rigideces kφfe/kφwe (22-23), Lcr (24), y opción de análisis racional elástico.",
        "texto": (
            "(b) Para secciones C y Z, sombrero, u otra sección abierta con "
            "aletas rigidizadas de igual dimensión donde el rigidizador es "
            "una pestaña simple o un rigidizador de borde complejo — Las "
            "disposiciones de esta parte de la norma aplicarán a cualquier "
            "sección abierta con aletas rigidizadas de igual dimensión "
            "donde el rigidizador es una pestaña (labio) simple o un "
            "rigidizador de borde complejo, incluyendo aquellas que cumplen "
            "los límites geométricos de la sección F.4.3.4.2(a). "
            "Fd = β·kφfe+kφwe+kφ / (K̃φfg+K̃φwg) (F.4.3.4-21). Donde: "
            "kφwe = rigidez elástica rotacional provista por el alma a la "
            "unión aleta-alma = E·t³ / (6ho·(1−μ²)) (F.4.3.4-22). "
            "K̃φwg = rigidez geométrica rotacional (dividida por el "
            "esfuerzo Fd) demandada por el alma a partir de la unión "
            "aleta-alma = (π/L)²·t·ho³/60 (F.4.3.4-23). Donde: L = valor "
            "mínimo entre Lcr y Lm. Lcr = ((6π⁴ho·(1−μ²)/t³)·(Ixf·(xo−hx)² "
            "+ Cwf − (Ixyf²/Iyf)·(xo−hx)²))^(1/4) (F.4.3.4-24). Lm = "
            "distancia entre puntos de restricción contra el pandeo "
            "distorsional (para miembros restringidos en forma continua, "
            "Lcr=Lm). Remitirse a la sección F.4.3.3.1.4(b) para definición "
            "de las demás variables en la ecuación F.4.3.4-24. (c) Análisis "
            "racional de pandeo elástico — Se permitirá el uso de un "
            "análisis racional elástico que considere el pandeo "
            "distorsional en lugar de las expresiones dadas en la sección "
            "F.4.3.4.2(a) ó (b). Se aplicará el factor de resistencia de la "
            "sección F.4.3.4.2."
        ),
    },
    # ── F.4.3.5 — Carga axial y momento combinados ─────────────
    {
        "id": "NSR10-F-F_4_3_5_1_tension_momento_1_3",
        "seccion": "F.4.3.5.1 (Carga axial a tensión y momento combinados — ecuaciones F.4.3.5-1 a -3)",
        "titulo": "2 ecuaciones de interacción DCCR para tensión+flexión biaxial (ecuaciones 1-2), y Mnxt/Mnyt (ecuación 3) según los 3 casos de φb.",
        "texto": (
            "F.4.3.5 — CARGA AXIAL Y MOMENTO COMBINADOS. F.4.3.5.1 — Carga "
            "axial a tensión y momento combinados. F.4.3.5.1.1 — Método de "
            "Diseño con Coeficientes de Carga y Resistencia (DCCR) — Las "
            "resistencias requeridas (tensión y momentos mayorados) T̄, M̄x "
            "y M̄y deben satisfacer las siguientes ecuaciones de "
            "interacción: M̄x/(φb·Mnxt) + M̄y/(φb·Mnyt) + T̄/(φt·Tn) ≤ 1.0 "
            "(F.4.3.5-1). M̄x/(φb·Mnx) + M̄y/(φb·Mny) − T̄/(φt·Tn) ≤ 1.0 "
            "(F.4.3.5-2). Donde: M̄x, M̄y = resistencias requeridas a "
            "flexión con respecto a los ejes centroidales. M̄x=Mux, "
            "M̄y=Muy. φb = para resistencia a flexión (sección "
            "F.4.3.3.1.1), φb=0.90 ó 0.95. Para vigas no arriostradas "
            "lateralmente (sección F.4.3.3.1.2), φb=0.90. Para miembros "
            "tubulares cilíndricos cerrados (sección F.4.3.3.1.3), "
            "φb=0.95. Mnxt, Mnyt = Sft·Fy (F.4.3.5-3). Donde: Sft = módulo "
            "de la sección completa no reducida respecto a la fibra extrema "
            "a tensión alrededor del eje apropiado. Fy = esfuerzo de "
            "fluencia de diseño determinado de acuerdo con la sección "
            "F.4.1.6.1. T̄ = resistencia requerida a tensión axial, "
            "T̄=Tu. φt=0.95. Tn = resistencia nominal bajo carga axial de "
            "acuerdo con la sección F.4.3.2. Mnx, Mny = resistencias "
            "nominales a flexión alrededor de los ejes centroidales de "
            "acuerdo con la sección F.4.3.3.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_5_2_compresion_momento_4_6",
        "seccion": "F.4.3.5.2.1 (Carga axial a compresión y momento combinados — ecuaciones F.4.3.5-4 a -6)",
        "titulo": "3 ecuaciones de interacción DCCR (análisis primer/segundo orden), casos especiales para secciones ángulo, y remisión a variables definidas.",
        "texto": (
            "F.4.3.5.2 — Carga axial a compresión y momento combinados. "
            "F.4.3.5.2.1 — Método de Diseño con Coeficientes de Carga y "
            "Resistencia (DCCR) — Las resistencias requeridas P̄, M̄x y M̄y "
            "deben determinarse utilizando un análisis elástico de primer "
            "orden y deben satisfacer las siguientes ecuaciones de "
            "interacción. Alternativamente, las resistencias requeridas "
            "P̄, M̄x y M̄y se determinarán de acuerdo con un análisis de "
            "segundo orden y deben satisfacer las siguientes ecuaciones de "
            "interacción usando los valores para Kx=Ky=1.0, αx=αy=1.0, y "
            "Cmx=Cmy=1.0. Adicionalmente, cada relación individual en las "
            "ecuaciones F.4.3.5-4 a F.4.3.5-6 no excederá la unidad. Para "
            "secciones ángulo no rigidizadas, de simetría sencilla, con "
            "área efectiva no reducida, se permitirá tomar My como la "
            "resistencia requerida a flexión solamente. Para otro tipo de "
            "secciones en ángulo o ángulos no rigidizados de simetría "
            "sencilla para los cuales el área efectiva (Ae) en el esfuerzo "
            "Fy es menor que el área de la sección transversal completa no "
            "reducida (A), My se tomará ya sea como la resistencia "
            "requerida a flexión o la resistencia requerida a flexión más "
            "PL/1000, el que resulte en un valor mínimo permisible para P. "
            "P̄/(φc·Pn) + Cmx·M̄x/(φb·Mnx·αx) + Cmy·M̄y/(φb·Mny·αy) ≤ 1.0 "
            "(F.4.3.5-4). P̄/(φc·Pno) + M̄x/(φb·Mnx) + M̄y/(φb·Mny) ≤ 1.0 "
            "(F.4.3.5-5). Cuando P̄/(φc·Pn) ≤ 0.15 se permitirá el uso de "
            "la siguiente ecuación en lugar de las dos anteriores: "
            "P̄/(φc·Pn) + M̄x/(φb·Mnx) + M̄y/(φb·Mny) ≤ 1.0 (F.4.3.5-6)."
        ),
    },
    {
        "id": "NSR10-F-F_4_3_5_2_variables_7_11",
        "seccion": "F.4.3.5.2.1 (Variables y ecuaciones F.4.3.5-7 a -11 para el método de interacción compresión+momento)",
        "titulo": "Definición de Pn/Pno/Mnx/Mny/φc/φb, factores αx/αy (ecuaciones 7-8), cargas de pandeo elástico PEX/PEY (ecuaciones 9-10), y coeficientes Cmx/Cmy (3 casos, ecuación 11).",
        "texto": (
            "Donde: φc = 0.85. Pn = resistencia nominal axial determinada "
            "de acuerdo con la sección F.4.3.4. M̄x, M̄y = resistencias "
            "requeridas a flexión con respecto a los ejes centroidales de "
            "la sección efectiva determinada solo para la resistencia "
            "requerida bajo compresión axial. M̄x=Mux, M̄y=Muy. φb = "
            "factor para resistencia a flexión (sección F.4.3.3.1.1), "
            "φb=0.90 ó 0.95. Para vigas no arriostradas lateralmente "
            "(sección F.4.3.3.1.2), φb=0.90. Para miembros tubulares "
            "cilíndricos cerrados (sección F.4.3.3.1.3), φb=0.95. Mnx, "
            "Mny = resistencia nominal a flexión alrededor de los ejes "
            "centroidales de acuerdo con la sección F.4.3.3.1. "
            "αx = 1 − P̄/PEX > 0 (F.4.3.5-7). αy = 1 − P̄/PEY > 0 "
            "(F.4.3.5-8). Donde: PEX = π²·E·Ix / (Kx·Lx)² (F.4.3.5-9). "
            "PEY = π²·E·Iy / (Ky·Ly)² (F.4.3.5-10). Donde: Ix = momento de "
            "inercia de la sección transversal completa no reducida "
            "alrededor del eje x. Kx = factor de longitud efectiva para "
            "pandeo alrededor del eje x. Lx = longitud no arriostrada para "
            "flexión alrededor del eje x. Iy, Ky, Ly = análogos para el "
            "eje y. Pno = resistencia nominal axial determinada de acuerdo "
            "con la sección F.4.3.4 con Fn=Fy. Cmx, Cmy = coeficientes "
            "cuyos valores se determinarán como sigue: (a) Para miembros "
            "bajo compresión en pórticos sujetos a traslación de los nudos "
            "(inclinación lateral): Cm=0.85. (b) Para miembros "
            "restringidos en compresión en pórticos arriostrados contra la "
            "traslación de nudos y no sujetos a carga lateral entre sus "
            "apoyos, en plano de la flexión: Cm = 0.6 − 0.4·(M1/M2) "
            "(F.4.3.5-11). Donde: M1/M2 es la relación entre el momento "
            "menor y el mayor en los extremos del segmento del miembro bajo "
            "consideración, el cual no está arriostrado en el plano de la "
            "flexión. M1/M2 es positivo cuando el miembro se flexiona en "
            "curvatura doble y negativa cuando se flexiona en curvatura "
            "simple. (c) Para miembros en compresión en pórticos "
            "arriostrados contra la traslación de los nudos en el plano de "
            "la carga y sujetos a carga transversal entre sus apoyos, el "
            "valor de Cm podrá ser determinado por un análisis racional de "
            "ingeniería. No obstante, en lugar de tal análisis, se permite "
            "utilizar los siguientes valores: (1) Para miembros cuyos "
            "extremos están restringidos, Cm=0.85. (2) Para miembros cuyos "
            "extremos no están restringidos, Cm=1.00."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.3 cargados. Numeral F.4.3 completo.")


if __name__ == "__main__":
    main()
