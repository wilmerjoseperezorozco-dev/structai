"""
NSR-10 Titulo F, F.2.7 a F.2.9.1 -- cierra los huecos F.2.7 (diseno por
cortante) y F.2.8 (fuerzas combinadas y torsion) del Capitulo F.2
(Estructuras de acero con perfiles laminados, armados y tubulares), mas
F.2.9.1 (provisiones generales de secciones compuestas, primer numeral de
F.2.9). Prioridad elegida por el usuario 2026-08-27 (issue de continuar
"capitulos que faltan de la NSR-10").

Fuente: NSR-10-743-770.pdf (Drive, id 15RBFpErGNE3cYaDsVGIYyVbwCu0NbdCF),
paginas internas F-77 a F-89. Leido visualmente pagina por pagina (Read con
`pages`, no el texto plano exportado por Drive -- el texto plano desordena
subindices/simbolos de formulas matematicas, confirmado en vivo: la misma
pagina via texto plano vs. via imagen PDF da resultados incomparables en
legibilidad de formulas. Ver tambien el hallazgo colateral real: F.2.6.3 a
F.2.6.13 (11 numerales completos sobre flexion de vigas, paginas F-62 a
F-77) tambien estan sin ingestar -- NO se cubre en este batch (fuera del
alcance elegido hoy), queda documentado para el proximo batch de F.2.

7 chunks single-topic, mismo patron que _ingest_titulo_f_f37_a_f311.py.

Uso: python _ingest_titulo_f_f27_a_f291.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_2_7_1_a_F_2_7_3",
        "seccion": "F.2.7.1 a F.2.7.3 (Diseño por cortante — provisiones generales, almas rigidizadas/no rigidizadas, acción del campo tensionado)",
        "titulo": (
            "Diseño de elementos por cortante en estructuras de acero (F.2.7.1-F.2.7.3): "
            "resistencia nominal a cortante Vn=0.6*Fy*Aw*Cv para almas rigidizadas o no "
            "rigidizadas, coeficiente de cortante del alma Cv según esbeltez h/tw, "
            "coeficiente de pandeo del alma kv, rigidizadores transversales, y el método "
            "alterno de acción del campo tensionado (post-pandeo) que da mayor resistencia "
            "cuando el tablero está soportado en sus 4 lados."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.7 — DISEÑO DE "
            "ELEMENTOS POR CORTANTE. Aplica al diseño del alma para miembros de simetría "
            "doble o simple sujetos a cortante en el plano del alma, al diseño a cortante "
            "de ángulos sencillos y PTE (perfiles tubulares estructurales), y al diseño "
            "para cortante en la dirección débil. Secciones: F.2.7.1 Provisiones "
            "Generales, F.2.7.2 Miembros con Almas Rigidizadas o no Rigidizadas, F.2.7.3 "
            "Acción del Campo Tensionado, F.2.7.4 Ángulos Sencillos, F.2.7.5 PTE de "
            "Sección Rectangular y Miembros en Cajón, F.2.7.6 PTE Circulares, F.2.7.7 "
            "Cortante en el Eje Débil, F.2.7.8 Vigas con Aberturas en el Alma. Para "
            "condiciones no incluidas aquí ver F.2.8.3.3 (secciones no simétricas), "
            "F.2.10.4.2 (resistencia a cortante de elementos de conexión), F.2.10.10.6 "
            "(cortante en zona de panel del alma).\n\n"
            "F.2.7.1 — PROVISIONES GENERALES — Dos métodos: F.2.7.2 no usa la resistencia "
            "postpandeo (acción del campo tensionado); F.2.7.3 sí la usa. La resistencia "
            "de diseño a cortante es phi_v*Vn, con phi_v=0.90 para todas las provisiones "
            "de F.2.7 excepto F.2.7.2.1(a).\n\n"
            "F.2.7.2 — MIEMBROS CON ALMAS RIGIDIZADAS O NO RIGIDIZADAS.\n"
            "F.2.7.2.1 Resistencia nominal a cortante — aplica a almas de miembros de "
            "simetría doble o simple y a canales solicitados por cortante en el plano "
            "del alma.\n"
            "Vn = 0.60*Fy*Aw*Cv  (F.2.7.2-1)\n"
            "(a) Para almas de perfiles laminados en I con h/tw <= 2.24*raiz(E/Fy): "
            "phi_v=1.00 y Cv=1.0  (F.2.7.2-2)\n"
            "(b) Para almas de todos los demás perfiles de simetría doble o simple y "
            "canales (sin incluir PTE circulares), el coeficiente de cortante del alma "
            "Cv se determina:\n"
            "  i) h/tw <= 1.10*raiz(kv*E/Fy): Cv=1.00  (F.2.7.2-3)\n"
            "  ii) 1.10*raiz(kv*E/Fy) < h/tw <= 1.37*raiz(kv*E/Fy): "
            "Cv = 1.10*raiz(kv*E/Fy) / (h/tw)  (F.2.7.2-4)\n"
            "  iii) h/tw > 1.37*raiz(kv*E/Fy): Cv = 1.51*kv*E / [(h/tw)^2*Fy]  (F.2.7.2-5)\n"
            "donde: Aw = area del alma = d*tw, mm2. h = para perfiles laminados, distancia "
            "libre entre aletas menos el filete/radio en la union alma-aleta; para "
            "perfiles armados con soldadura, distancia libre entre aletas; para perfiles "
            "armados con pernos, distancia entre lineas de conectores; para secciones en "
            "T, el peralte. tw = espesor del alma, mm.\n"
            "Coeficiente de pandeo del alma kv: (i) almas sin rigidizadores transversales "
            "y con h/tw < 260: kv=5, excepto almas de perfiles en T donde kv=1.2. "
            "(ii) almas con rigidizadores transversales: kv = 5 + 5/(a/h)^2  (F.2.7.2-6); "
            "kv=5 cuando a/h>3.0 o a/h>[260/(h/tw)]^2, donde a=distancia libre entre "
            "rigidizadores transversales, mm.\n"
            "F.2.7.2.2 Rigidizadores transversales — no se requieren cuando h/tw <= "
            "2.46*raiz(E/Fy), o cuando la resistencia requerida a cortante <= resistencia "
            "de diseño con kv=5 (F.2.7.2.1). Cuando se requieren: Ist >= b*tw^3*j  "
            "(F.2.7.2-7), donde Ist=momento de inercia del rigidizador respecto al plano "
            "medio del alma (par de rigidizadores) o a la cara en contacto con el alma "
            "(rigidizador simple); b=menor entre a y h; j = 2.5/(a/h)^2 - 2 >= 0.50  "
            "(F.2.7.2-8). Los rigidizadores pueden interrumpirse antes de la aleta a "
            "tensión si no transmiten carga concentrada/reacción; la soldadura que conecta "
            "un rigidizador transversal al alma debe terminar a distancia >=4*tw y "
            "<=6*tw desde el borde de la soldadura alma-aleta; rigidizadores simples con "
            "aleta a compresión de platina rectangular deben conectarse a esa aleta contra "
            "levantamiento por torsión. Pernos de rigidizadores: espaciamiento <=305mm "
            "centro a centro; soldaduras de filete intermitentes: distancia libre "
            "<=16*tw, sin exceder 250mm.\n\n"
            "F.2.7.3 — ACCIÓN DEL CAMPO TENSIONADO.\n"
            "F.2.7.3.1 Limitaciones para el uso — se permite contar con la acción del "
            "campo tensionado para miembros con aletas cuando el tablero del alma está "
            "soportado en sus 4 lados por aletas o rigidizadores. NO se permite en: "
            "(a) tableros extremos con rigidizadores transversales; (b) miembros con a/h>3 "
            "o a/h>[260/(h/tw)]^2; (c) miembros con 2*Aw/(Afc+Aft)>2.5; (d) miembros con "
            "h/bfc o h/bft>6.0, donde Afc,Aft=área aleta compresión/tensión, mm2; "
            "bfc,bft=ancho aleta compresión/tensión, mm. En estos casos, Vn se determina "
            "según F.2.7.2.\n"
            "F.2.7.3.2 Resistencia nominal con acción del campo tensionado (estado límite "
            "de fluencia por tensión):\n"
            "(a) h/tw <= 1.10*raiz(kv*E/Fy): Vn = 0.60*Fy*Aw  (F.2.7.3-1)\n"
            "(b) h/tw > 1.10*raiz(kv*E/Fy): "
            "Vn = 0.60*Fy*Aw*[Cv + (1-Cv)/(1.15*raiz(1+(a/h)^2))]  (F.2.7.3-2), "
            "con kv y Cv definidos en F.2.7.2.1.\n"
            "F.2.7.3.3 Rigidizadores transversales con campo tensionado — además de "
            "F.2.7.2.2: (b/t)_st <= 0.56*raiz(E/Fyst)  (F.2.7.3-3); "
            "Ist >= Ist1 + (Ist2-Ist1)*[(Vr-Vc1)/(Vc2-Vc1)]  (F.2.7.3-4), donde "
            "Ist1=momento de inercia mínimo requerido según F.2.7.2.2; Ist2 = "
            "h^4*rho_st^1.3*(Fyw/E)^1.5 / 40  (F.2.7.3-5), momento de inercia mínimo "
            "requerido para desarrollar Vr=Vc2 (resistencia con campo tensionado); "
            "Vr=mayor resistencia requerida a cortante en los paneles adyacentes al "
            "rigidizador, N; Vc1=menor resistencia disponible a cortante en paneles "
            "adyacentes según F.2.7.2.1, N; Vc2=menor resistencia disponible según "
            "F.2.7.3.2, N; rho_st=Fyw/Fyst>=1.0; Fyw=esfuerzo de fluencia mínimo del "
            "material del alma, MPa; Fyst=esfuerzo de fluencia mínimo del rigidizador, "
            "MPa; (b/t)_st=relación ancho-espesor del rigidizador."
        ),
    },
    {
        "id": "NSR10-F-F_2_7_4_a_F_2_7_8",
        "seccion": "F.2.7.4 a F.2.7.8 (Cortante en ángulos sencillos, PTE rectangular/circular, eje débil, vigas con aberturas)",
        "titulo": (
            "Diseño por cortante para ángulos sencillos, PTE rectangulares/en cajón, PTE "
            "circulares, flexión sobre el eje débil, y vigas con aberturas en el alma "
            "(F.2.7.4-F.2.7.8) — cierre del numeral F.2.7 de la NSR-10 Título F."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.7.4 — ÁNGULOS "
            "SENCILLOS — la resistencia nominal a cortante Vn de la aleta se determina "
            "usando F.2.7.2-1 y F.2.7.2.1(b) con Aw=b*t, donde b=ancho de la aleta que "
            "resiste la fuerza cortante, mm; t=espesor de la aleta, mm; h/tw=b/t; kv=1.2.\n\n"
            "F.2.7.5 — PERFILES TUBULARES ESTRUCTURALES (PTE) DE SECCIÓN RECTANGULAR Y "
            "MIEMBROS EN CAJÓN — Vn se determina con F.2.7.2.1 y Aw=2*h*t, donde "
            "h=ancho de la cara que resiste la fuerza cortante = dimensión exterior menos "
            "2 veces el radio de esquina en cada extremo (si no se conoce el radio, h se "
            "toma como la dimensión exterior menos 3 veces el espesor); t=espesor de "
            "diseño de la pared = 0.93*espesor nominal si el PTE fue fabricado con "
            "soldadura por resistencia eléctrica (ERW), o igual al espesor nominal si fue "
            "fabricado con soldadura por arco sumergido (SAW); tw=t; kv=5.\n\n"
            "F.2.7.6 — PERFILES TUBULARES ESTRUCTURALES (PTE) CIRCULARES — "
            "Vn = Fcr*Ag/2  (F.2.7.6-1), donde Fcr es el mayor entre:\n"
            "Fcr = 1.60*E / [raiz(Lv/D)*(D/t)^(5/4)]  (F.2.7.6-2a)\n"
            "Fcr = 0.78*E / (D/t)^(3/2)  (F.2.7.6-2b), sin exceder 0.60*Fy.\n"
            "donde: Ag=área bruta total de la sección transversal, mm2; D=diámetro "
            "exterior, mm; Lv=distancia entre puntos de fuerza cortante máxima y cortante "
            "cero, mm; t=espesor de diseño de la pared, igual a 0.93 veces el espesor "
            "nominal para PTE fabricado por soldadura ERW, e igual al espesor nominal si "
            "se usó SAW. Las fórmulas F.2.7.6-2a/2b (pandeo por cortante) controlan para "
            "relaciones D/t mayores que 100, aceros de alta resistencia, y longitudes "
            "considerables. Para secciones estándar, el diseño estará usualmente "
            "controlado por fluencia por cortante.\n\n"
            "F.2.7.7 — CORTANTE SOBRE EL EJE DÉBIL PARA PERFILES DE SIMETRÍA DOBLE O "
            "SIMPLE — para perfiles cargados en el eje débil sin torsión, Vn se determina "
            "para cada elemento resistente usando F.2.7.2-1 y F.2.7.2.1(b) con Aw=bf*tf, "
            "h/tw=b/tf y kv=1.2, donde b=para aletas de miembros en I, la mitad del ancho "
            "total de la aleta bf; para aletas de canales, la dimensión nominal total de "
            "la aleta, mm. Para todos los perfiles W, S, M y HP según ASTM A6, Cv=1.00 "
            "cuando Fy<=345 MPa.\n\n"
            "F.2.7.8 — VIGAS CON ABERTURAS EN EL ALMA — se debe determinar el efecto de "
            "todas las aberturas en el alma sobre la resistencia nominal a cortante de "
            "vigas de acero o de construcción compuesta. Cuando la resistencia requerida "
            "exceda la resistencia de diseño en una sección con abertura, se debe proveer "
            "el refuerzo necesario para suplir la deficiencia."
        ),
    },
    {
        "id": "NSR10-F-F_2_8_1",
        "seccion": "F.2.8.1 (Miembros con simetría doble o simple solicitados por flexión y fuerza axial)",
        "titulo": (
            "Diseño de miembros con simetría doble o simple por flexión combinada con "
            "compresión (viga-columna, fórmulas de interacción P-M) o con tensión — "
            "ecuaciones de interacción F.2.8.1-1a/1b, y el método alterno F.2.8.1-2 para "
            "perfiles laminados compactos con momento dominante en el eje mayor."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.8 — DISEÑO DE "
            "MIEMBROS SOLICITADOS POR FUERZAS COMBINADAS Y POR TORSIÓN. Aplica a miembros "
            "solicitados por carga axial y flexión respecto a uno o ambos ejes, con o sin "
            "torsión, y a miembros solo por torsión. Secciones: F.2.8.1 Miembros con "
            "Simetría Doble o Simple Solicitados por Flexión y Fuerza Axial, F.2.8.2 "
            "Miembros Asimétricos y Otros Miembros, F.2.8.3 Miembros Solicitados por "
            "Torsión o Combinación de Torsión/Flexión/Cortante/Fuerza Axial, F.2.8.4 "
            "Rotura de Aletas con Perforaciones bajo Fuerzas de Tensión. Para miembros de "
            "construcción compuesta ver F.2.9.\n\n"
            "F.2.8.1 — MIEMBROS CON SIMETRÍA DOBLE O SIMPLE SOLICITADOS POR FLEXIÓN Y "
            "FUERZA AXIAL.\n"
            "F.2.8.1.1 Flexión y compresión — para miembros con simetría doble, y con "
            "simetría simple con 0.1<=(Iyc/Iy)<=0.9 restringidos de forma que la flexión "
            "sea alrededor de ejes geométricos (x o y), limitada por:\n"
            "(a) Pu/(phi*Pn) >= 0.2: "
            "Pu/(phi*Pn) + (8/9)*[Mux/(phi_b*Mnx) + Muy/(phi_b*Mny)] <= 1.0  (F.2.8.1-1a)\n"
            "(b) Pu/(phi*Pn) < 0.2: "
            "Pu/(2*phi*Pn) + [Mux/(phi_b*Mnx) + Muy/(phi_b*Mny)] <= 1.0  (F.2.8.1-1b)\n"
            "donde: Pu=resistencia requerida a compresión, N; phi*Pn=phi_c*Pn=resistencia "
            "de diseño a compresión según F.2.5, N; Mu=resistencia requerida a flexión, "
            "N·mm; phi_b*Mn=resistencia de diseño a flexión según F.2.6, N·mm; x=subíndice "
            "eje mayor; y=subíndice eje menor; phi_c=0.90; phi_b=0.90. Se permite usar "
            "F.2.8.2 en vez de este numeral.\n\n"
            "F.2.8.1.2 Flexión y tensión — misma interacción F.2.8.1-1a/1b, tomando: "
            "Pu=resistencia requerida a tensión; phi*Pn=phi_t*Pn según F.2.4; phi_t=coef. "
            "reducción tensión (F.2.4.2). Para simetría doble, el coeficiente Cb del "
            "numeral F.2.6 puede multiplicarse por raiz(1+Pu/Pey) cuando hay tensión "
            "axial concurrente con flexión, donde Pey = pi^2*E*Iy/Lb^2. Se permite un "
            "análisis más detallado en vez de F.2.8.1-1a/1b.\n\n"
            "F.2.8.1.3 Perfiles laminados de simetría doble y sección compacta, "
            "(KLz)<=(KLy), solicitados por flexión y compresión, con momento actuando "
            "básicamente sobre el eje mayor (Muy/phi*Mny < 0.05): pueden considerarse por "
            "separado 2 estados límite (en vez del enfoque combinado F.2.8.1.1):\n"
            "(a) Inestabilidad en el plano: usar F.2.8.1-1 con phi*Pn, Mux y phi_b*Mnx "
            "calculados EN el plano de flexión.\n"
            "(b) Pandeo fuera del plano y pandeo lateral-torsional: "
            "[Pu/(phi_c*Pny)]*(1.5-0.5*Pu/(phi_c*Pny)) + [Mux/(Cb*phi_b*Mcx)]^2 <= 1.0  "
            "(F.2.8.1-2), donde phi_c*Pny=resistencia diseño compresión para pandeo fuera "
            "del plano; Cb=coeficiente de modificación según F.2.6.1; Mcx=resistencia "
            "diseño pandeo lateral-torsional con flexión sobre el eje mayor, calculada "
            "según F.2.6 usando Cb=1.0. Con momentos significativos en ambos ejes "
            "(Muy/phi*Mny>=0.05) aplicar F.2.8.1.1. En F.2.8.1-2, Cb*phi_b*Mnx puede ser "
            "mayor que phi_b*Mpx; la plastificación de la sección de la viga-columna está "
            "controlada por F.2.8.1-1."
        ),
    },
    {
        "id": "NSR10-F-F_2_8_2",
        "seccion": "F.2.8.2 (Miembros asimétricos y otros miembros solicitados por flexión y fuerza axial)",
        "titulo": (
            "Interacción de esfuerzos axiales y de flexión para secciones NO cubiertas en "
            "F.2.8.1 (asimétricas o cualquier otra) — criterio general en términos de "
            "esfuerzos combinados, aplicable a cualquier sección transversal."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.8.2 — MIEMBROS "
            "ASIMÉTRICOS Y OTROS MIEMBROS SOLICITADOS POR FLEXIÓN Y FUERZA AXIAL — se "
            "refiere a la interacción de esfuerzos axiales y de flexión para secciones no "
            "cubiertas en F.2.8.1. Se permite usar este numeral en lugar de F.2.8.1 para "
            "cualquier sección transversal. Debe satisfacerse:\n"
            "|fra/Fca| + |frbw/Fcbw| + |frbz/Fcbz| <= 1.0  (F.2.8.2-1)\n"
            "donde: fra=resistencia requerida (esfuerzo axial debido a cargas mayoradas) "
            "en el punto en consideración, MPa; Fca=phi_c*Fcr o phi_t*Ft = resistencia de "
            "diseño a carga axial en términos de esfuerzos, según F.2.5 (compresión) o "
            "F.2.4.2 (tensión), MPa; frbw, frbz = resistencia requerida (esfuerzos de "
            "flexión debidos a cargas mayoradas) en un punto específico de la sección "
            "transversal, MPa; Fcbw, Fcbz = phi_b*Mn/S = resistencia de diseño a flexión "
            "en el punto en consideración, en términos de esfuerzos, según F.2.6, usando "
            "el módulo de sección correspondiente a la ubicación específica en la sección "
            "y considerando el signo del esfuerzo, MPa; w=subíndice eje mayor; z=subíndice "
            "eje menor; phi_c=0.90 (compresión); phi_t=coef. tensión (F.2.4.2); phi_b=0.90 "
            "(flexión). La ecuación F.2.8.2-1 debe evaluarse usando los ejes principales "
            "de flexión y considerando el sentido de los esfuerzos de flexión para los "
            "puntos críticos de la sección transversal — los términos de flexión se suman "
            "o restan al término de carga axial según corresponda. Cuando la fuerza axial "
            "es de compresión, deben incluirse los efectos de segundo orden según F.2.3. "
            "Se permite un análisis más detallado de la interacción flexión-tensión en "
            "vez de F.2.8.2-1."
        ),
    },
    {
        "id": "NSR10-F-F_2_8_3",
        "seccion": "F.2.8.3 (Miembros solicitados por torsión o combinación de torsión, flexión, cortante o fuerza axial)",
        "titulo": (
            "Diseño por torsión de PTE (rectangulares y circulares) y de otros perfiles: "
            "resistencia nominal a torsión Tn=Fcr*C, interacción con flexión/cortante/"
            "fuerza axial cuando la torsión requerida supera el 20% de la resistencia de "
            "diseño a torsión."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.8.3 — MIEMBROS "
            "SOLICITADOS POR TORSIÓN O POR UNA COMBINACIÓN DE TORSIÓN, FLEXIÓN, CORTANTE O "
            "FUERZA AXIAL.\n"
            "F.2.8.3.1 Resistencia a la torsión de PTE rectangulares y circulares — "
            "resistencia de diseño phi_T*Tn, phi_T=0.90. Tn = Fcr*C  (F.2.8.3-1), para "
            "los estados límite de fluencia por torsión y pandeo por torsión, donde "
            "C=constante torsional del PTE y Fcr:\n"
            "(a) PTE circular, Fcr=mayor entre:\n"
            "  Fcr = 1.23*E / [raiz(L/D)*(D/t)^(5/4)]  (F.2.8.3-2a)\n"
            "  Fcr = 0.60*E / (D/t)^(3/2)  (F.2.8.3-2b), sin exceder 0.6*Fy. "
            "L=longitud del elemento, mm; D=diámetro exterior, mm.\n"
            "(b) PTE rectangular:\n"
            "  i) h/t <= 2.45*raiz(E/Fy): Fcr = 0.6*Fy  (F.2.8.3-3)\n"
            "  ii) 2.45*raiz(E/Fy) < h/t <= 3.07*raiz(E/Fy): "
            "Fcr = 0.6*Fy*(2.45*raiz(E/Fy))/(h/t)  (F.2.8.3-4)\n"
            "  iii) 3.07*raiz(E/Fy) < h/t <= 260: "
            "Fcr = 0.458*pi^2*E / (h/t)^2  (F.2.8.3-5), donde h=ancho plano del lado "
            "mayor (F.2.2.4.1b(d)); t=espesor de diseño de la pared (F.2.2.4.2). "
            "Constante de cortante torsional C (conservadora): PTE circular: "
            "C = pi*(D-t)^2*t/2. PTE rectangular: C = 2*(B-t)*(H-t)*t - 4.5*(4-pi)*t^3, "
            "con B,H=dimensiones exteriores del PTE rectangular.\n\n"
            "F.2.8.3.2 PTE solicitados por combinación de torsión, cortante, flexión y "
            "fuerza axial — cuando la resistencia requerida a torsión Tu <= 20% de "
            "phi_T*Tn, la interacción se determina según F.2.8.1 despreciando los efectos "
            "torsionales. Cuando Tu excede el 20%, la interacción está limitada por:\n"
            "[Pu/(phi*Pn) + Mu/(phi_b*Mn)] + [Vu/(phi_v*Vn) + Tu/(phi_T*Tn)]^2 <= 1.0  "
            "(F.2.8.3-6)\n"
            "donde: Pu=resistencia requerida carga axial, N; phi*Pn=resistencia diseño "
            "tensión/compresión según F.2.4/F.2.5, N; Mu=resistencia requerida flexión, "
            "N·mm; phi_b*Mn=resistencia diseño flexión según F.2.6, N·mm; Vu=resistencia "
            "requerida cortante, N; phi_v*Vn=resistencia diseño cortante según F.2.7, N; "
            "Tu=resistencia requerida torsión, N·mm; phi_T*Tn=resistencia diseño torsión "
            "según F.2.8.3.1, N·mm.\n\n"
            "F.2.8.3.3 Resistencia de miembros distintos de PTE solicitados por torsión y "
            "fuerzas combinadas — phi_T*Tn = menor entre fluencia bajo esfuerzos normales, "
            "fluencia por cortante bajo esfuerzos cortantes, y pandeo, phi_T=0.90:\n"
            "(a) Fluencia esfuerzos normales: Fn = Fy  (F.2.8.3-7)\n"
            "(b) Fluencia por cortante: Fn = 0.6*Fy  (F.2.8.3-8)\n"
            "(c) Pandeo: Fn = Fcr  (F.2.8.3-9), donde Fcr=esfuerzo de pandeo para la "
            "sección determinado mediante análisis, MPa. Se permite algún grado de "
            "fluencia local restringida en la vecindad de zonas que permanezcan elásticas."
        ),
    },
    {
        "id": "NSR10-F-F_2_8_4",
        "seccion": "F.2.8.4 (Rotura de aletas con perforaciones bajo fuerzas de tensión)",
        "titulo": (
            "Verificación de rotura por tensión en la aleta perforada bajo carga axial + "
            "flexión combinadas sobre el eje mayor — ecuación de interacción F.2.8.4-1, "
            "cada aleta se verifica por separado."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.8.4 — ROTURA DE "
            "ALETAS CON PERFORACIONES BAJO ESFUERZOS DE TENSIÓN — donde se tengan "
            "perforaciones en una aleta bajo esfuerzos de tensión por la combinación de "
            "carga axial y flexión sobre el eje mayor, la resistencia a la rotura por "
            "tensión en la aleta está limitada por:\n"
            "Pu/(phi_t*Pn) + Mux/(phi_b*Mnx) <= 1.0  (F.2.8.4-1)\n"
            "Cada aleta solicitada por tensión bajo carga axial y flexión debe verificarse "
            "por separado. Donde: Pu=resistencia requerida a carga axial en el miembro en "
            "la sección con perforaciones, positiva para tensión, negativa para "
            "compresión, N; phi_t*Pn=resistencia de diseño a carga axial para el estado "
            "límite de rotura a tensión por el área neta en la sección, según F.2.4.2(b), "
            "N; Mux=resistencia requerida a flexión sobre el eje x en la sección con "
            "perforaciones, positiva para tensión en la aleta bajo consideración, negativa "
            "para compresión, N·mm; phi_b*Mnx=resistencia de diseño a flexión sobre el eje "
            "x para el estado límite de rotura por tensión de la aleta, según F.2.6.13.1 — "
            "cuando no sea aplicable el estado límite de rotura por flexión, se toma como "
            "resistencia nominal el momento plástico Mp calculado sin tener en cuenta las "
            "perforaciones, N·mm; phi_t=coef. reducción resistencia rotura a tensión=0.75; "
            "phi_b=coef. reducción resistencia flexión=0.90."
        ),
    },
    {
        "id": "NSR10-F-F_2_9_1",
        "seccion": "F.2.9.1 (Secciones compuestas — provisiones generales, límites del material, clasificación pandeo local)",
        "titulo": (
            "Provisiones generales de F.2.9 (miembros compuestos acero-concreto): "
            "aplicación de requisitos del Título C con excepciones, métodos de cálculo de "
            "resistencia nominal (plástico y compatibilidad de deformaciones), límites del "
            "material (f'c 21-70 MPa peso normal, Fy<=525 MPa), y clasificación de "
            "secciones tipo perfil relleno para pandeo local (Tabla F.2.9.1-1a)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.9 — DISEÑO DE "
            "MIEMBROS DE SECCIÓN COMPUESTA. Aplica a miembros compuestos conformados por "
            "perfiles laminados, armados o PTE que actúan conjuntamente con una sección "
            "de concreto estructural, y a vigas de acero que soportan una losa de "
            "concreto reforzado interconectadas para actuar en conjunto a flexión (vigas "
            "compuestas simplemente apoyadas o continuas con conectores, y vigas tipo "
            "perfil relleno o revestido de concreto, con o sin apuntalamiento temporal). "
            "Secciones: F.2.9.1 Provisiones Generales, F.2.9.2 Fuerza Axial, F.2.9.3 "
            "Flexión, F.2.9.4 Cortante, F.2.9.5 Combinación de Fuerza Axial y Flexión, "
            "F.2.9.6 Transferencia de Fuerzas, F.2.9.7 Diafragmas Compuestos y Vigas "
            "Colectoras, F.2.9.8 Conectores de Acero, F.2.9.9 Casos Especiales.\n\n"
            "F.2.9.1 — PROVISIONES GENERALES — para determinar los efectos de las cargas "
            "en miembros y conexiones de una estructura con miembros compuestos, se deben "
            "considerar las secciones efectivas al momento de aplicación de cada "
            "incremento de carga.\n"
            "F.2.9.1.1 Concreto y Acero de Refuerzo — las propiedades de materiales, "
            "diseño y detallado deben cumplir las especificaciones del Título C, con "
            "excepciones: (a) se excluyen completamente los numerales C.7.8.2 y C.10.13 y "
            "el Capítulo C.21; (b) limitaciones para materiales de concreto y acero de "
            "refuerzo longitudinal según F.2.9.1.3; (c) limitaciones para refuerzo "
            "transversal según F.2.9.2.1.1(2), además de las del Título C; (d) cuantía "
            "mínima de refuerzo longitudinal para miembros tipo perfil revestido según "
            "F.2.9.2.1.1(3). Se pretende que el concreto y acero de refuerzo de miembros "
            "compuestos se detallen aplicando las provisiones de construcción NO compuesta "
            "del Título C, modificadas según F.2.9.\n"
            "F.2.9.1.2 Resistencia Nominal de Secciones Compuestas — se usa el método "
            "plástico de distribución de esfuerzos o el método de compatibilidad de "
            "deformaciones. Al determinar la resistencia nominal se desprecia la "
            "resistencia del concreto a tensión. Para perfil relleno a compresión deben "
            "considerarse los efectos de pandeo local según F.2.9.1.4; no se requiere "
            "considerar pandeo local para perfil revestido.\n"
            "  F.2.9.1.2.1 Método Plástico de Distribución de Esfuerzos — la resistencia "
            "nominal se calcula suponiendo que los componentes de acero alcanzaron un "
            "esfuerzo Fy en tensión o compresión, y que los componentes de concreto en "
            "compresión alcanzaron 0.85*f'c. Para PTE circulares rellenos de concreto, el "
            "confinamiento permite usar 0.95*f'c en los componentes de concreto por carga "
            "axial o flexión.\n"
            "  F.2.9.1.2.2 Método de Compatibilidad de Deformaciones — distribución lineal "
            "de deformaciones, deformación unitaria máxima 0.003 mm/mm en el concreto a "
            "compresión; relaciones esfuerzo-deformación del acero y concreto a partir de "
            "ensayos o resultados publicados. Para secciones irregulares o acero sin "
            "comportamiento elasto-plástico, se debe usar este método (ver Título C y Guía "
            "de Diseño No. 6 del AISC para columnas tipo perfil revestido).\n"
            "F.2.9.1.3 Limitaciones del Material:\n"
            "(1) Resistencia de diseño del concreto f'c: no menor que 21 MPa ni mayor que "
            "70 MPa para concreto de peso normal; no menor que 21 MPa ni mayor que 42 MPa "
            "para concreto aligerado. Se pueden usar valores mayores de f'c para cálculos "
            "de rigidez, pero no para cálculos de resistencia a menos que se justifique "
            "mediante ensayos o análisis.\n"
            "(2) Esfuerzos de fluencia mínimos especificados para el acero estructural y "
            "para las barras de refuerzo: no mayores que 525 MPa, al calcular la "
            "resistencia de una columna compuesta.\n"
            "F.2.9.1.4 Clasificación de Secciones Compuestas Tipo Perfil Relleno para "
            "Pandeo Local — para compresión: compacta si la relación ancho/espesor no "
            "excede lambda_p de la Tabla F.2.9.1-1a en ningún elemento de acero a "
            "compresión; no compacta si excede lambda_p pero no lambda_r en ninguno; "
            "sección con elementos esbeltos si algún elemento excede lambda_r (limitado al "
            "máximo de la tabla). Igual criterio para flexión con Tabla F.2.9.1-1b "
            "(lambda_p, lambda_r propios de flexión). Definiciones de ancho (b o D) y "
            "espesor (t) para PTE rectangulares y circulares: tablas F.2.2.4.1a y "
            "F.2.2.4.1b.\n\n"
            "Tabla F.2.9.1-1a — Valores Límite de la Relación Ancho a Espesor para "
            "Elementos de Acero a Compresión en Miembros de Construcción Compuesta "
            "Solicitados por Carga Axial de Compresión (para aplicar en F.2.9.2.2):\n"
            "Paredes de PTE y perfiles en cajón, sección rectangular y espesor uniforme "
            "(relación b/t): lambda_p (compacto/no compacto) = 2.26*raiz(E/Fy); "
            "lambda_r (no compacto/esbelto) = 3.0*raiz(E/Fy); máximo permitido = "
            "5.0*raiz(E/Fy).\n"
            "Secciones circulares rellenas (relación D/t): lambda_p = 0.15*E/Fy; "
            "lambda_r = 0.19*E/Fy; máximo permitido = 0.31*E/Fy."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

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
    print(f"OK: {len(rows)} chunks F.2.7-F.2.9.1 cargados con embedding.")


if __name__ == "__main__":
    main()
