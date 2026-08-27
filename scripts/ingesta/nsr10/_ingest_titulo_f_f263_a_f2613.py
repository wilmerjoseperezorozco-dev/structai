"""
NSR-10 Titulo F, F.2.6.3 a F.2.6.13 -- cierra el hallazgo colateral
documentado en _ingest_titulo_f_f27_a_f291.py (commit f7c25d8, 2026-08-27):
11 numerales completos sobre flexion de vigas de acero (miembros seccion I
con distintas combinaciones de alma/aleta compacta-no compacta-esbelta, PTE
cuadrados/rectangulares/circulares, secciones T y angulos dobles, angulos
sencillos, barras rectangulares/circulares, secciones no simetricas, y el
numeral final de dimensionamiento de vigas: agujeros, limites I, cubreplacas,
vigas armadas, redistribucion de momentos) que quedaban sin ingestar en el
mismo PDF fuente ya usado para F.2.7-F.2.9.1.

Fuente: NSR-10-743-770.pdf (Drive, id 15RBFpErGNE3cYaDsVGIYyVbwCu0NbdCF),
paginas internas F-62 a F-77. Leido visualmente pagina por pagina (Read con
`pages`), no el texto plano exportado por Drive -- mismo motivo documentado
en el script anterior de este mismo lote (formulas con subindices/simbolos
matematicos se desordenan en el texto plano de Drive, confirmado en vivo).

6 chunks single-topic, mismo patron que los scripts anteriores de Titulo F.

Uso: python _ingest_titulo_f_f263_a_f2613.py
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
        "id": "NSR10-F-F_2_6_3_a_F_2_6_4",
        "seccion": "F.2.6.3 a F.2.6.4 (Miembros sección I: alma compacta con aletas no compactas/esbeltas; otros miembros I con alma compacta o no compacta)",
        "titulo": (
            "Resistencia nominal a flexión Mn de miembros de sección en I alrededor del "
            "eje mayor: alma compacta con aletas no compactas o esbeltas (F.2.6.3), y el "
            "caso general de alma no compacta / simetría simple (F.2.6.4) con factor de "
            "plastificación del alma Rpc, longitudes límite Lp/Lr, y radio de giro "
            "efectivo rt."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. "
            "F.2.6.3 — MIEMBROS DE SECCIÓN EN I CON SIMETRÍA DOBLE, CON ALMA COMPACTA Y "
            "ALETAS NO COMPACTAS O ESBELTAS, SOLICITADOS POR FLEXIÓN ALREDEDOR DE SU EJE "
            "MAYOR — aplica a miembros con alma compacta y aletas no compactas o esbeltas "
            "(definiciones F.2.2.4.1). Mn = menor entre pandeo lateral-torsional (aplicar "
            "provisiones de F.2.6.2.2) y pandeo local de la aleta a compresión:\n"
            "(a) aletas no compactas: "
            "Mn = Mp - (Mp - 0.7*Fy*Sx)*((λ-λpf)/(λrf-λpf))  (F.2.6.3-1)\n"
            "(b) aletas esbeltas: Mn = 0.9*E*kc*Sx / λ²  (F.2.6.3-2)\n"
            "donde: λ=bf/2tf; λpf=λp (tabla F.2.2.4-1b); λrf=λr (tabla F.2.2.4-1b); "
            "kc=4/raiz(h/tw), no menor que 0.35 ni mayor que 0.76; h según F.2.2.4.1.2.\n\n"
            "F.2.6.4 — OTROS MIEMBROS DE SECCIÓN EN I CON ALMA COMPACTA O NO COMPACTA, "
            "SOLICITADOS POR FLEXIÓN ALREDEDOR DE SU EJE MAYOR — aplica a: (a) simetría "
            "doble con alma NO compacta; (b) simetría simple con alma compacta o no "
            "compacta (F.2.2.4) conectada a las aletas por líneas medias. Pueden diseñarse "
            "conservadoramente con F.2.6.5. Mn = menor entre: fluencia aleta compresión, "
            "pandeo lateral-torsional, pandeo local aleta compresión, fluencia aleta "
            "tensión.\n"
            "F.2.6.4.1 Fluencia aleta compresión: Mn = Rpc*Myc = Rpc*Fy*Sxc  (F.2.6.4-1)\n"
            "F.2.6.4.2 Pandeo lateral-torsional:\n"
            "(a) Lb<=Lp: no aplica\n"
            "(b) Lp<Lb<=Lr: "
            "Mn = Cb*[Rpc*Myc - (Rpc*Myc-FL*Sxc)*((Lb-Lp)/(Lr-Lp))] <= Rpc*Myc  "
            "(F.2.6.4-2)\n"
            "(c) Lb>Lr: Mn = Fcr*Sxc <= Rpc*Myc  (F.2.6.4-3)\n"
            "donde: Myc=Fy*Sxc  (F.2.6.4-4)\n"
            "Fcr = [Cb*pi^2*E/(Lb/rt)^2] * raiz(1 + 0.078*(J/(Sxc*ho))*(Lb/rt)^2)  "
            "(F.2.6.4-5). Para Iyc/Iy<=0.23, J=0. Iyc=momento de inercia de la aleta a "
            "compresión respecto al eje y, mm4.\n"
            "FL: Sxt/Sxc>=0.7: FL=0.7*Fy  (F.2.6.4-6a); Sxt/Sxc<0.7: "
            "FL=Fy*(Sxt/Sxc)>=0.5*Fy  (F.2.6.4-6b)\n"
            "Lp = 1.1*rt*raiz(E/Fy)  (F.2.6.4-7)\n"
            "Lr = 1.95*rt*(E/FL)*raiz(J/(Sxc*ho) + raiz[(J/(Sxc*ho))^2 + "
            "6.76*(FL/E)^2])  (F.2.6.4-8)\n"
            "Rpc (factor de plastificación del alma):\n"
            "Cuando Iyc/Iy>0.23: hc/tw<=λpw: Rpc=Mp/Myc  (F.2.6.4-9a); hc/tw>λpw: "
            "Rpc=[Mp/Myc - (Mp/Myc-1)*((λ-λpw)/(λrw-λpw))] <= Mp/Myc  (F.2.6.4-9b)\n"
            "Cuando Iyc/Iy<=0.23: Rpc=1.0\n"
            "donde: Mp=Zx*Fy<=1.6*Sxc*Fy; Sxc,Sxt=módulo elástico referido a aletas "
            "tensión/compresión, mm3; λ=hc/tw; λpw=λp (tabla F.2.2.4-1b); λrw=λr (tabla "
            "F.2.2.4-1b); hc=para perfiles laminados, 2 veces la distancia centroide-cara "
            "interna aleta compresión menos filete/radio esquina; para perfiles armados, "
            "2 veces la distancia centroide-línea de pernos aleta compresión, o cara "
            "interior aleta compresión con soldadura, mm.\n"
            "Radio de giro efectivo pandeo lateral-torsional, rt:\n"
            "(i) secciones I con aleta compresión rectangular: "
            "rt = bfc / raiz[12*(ho/d + (1/6)*aw*(h^2/(ho*d)))]  (F.2.6.4-10), donde "
            "aw = hc*tw/(bfc*tfc)  (F.2.6.4-11); bfc=ancho aleta compresión, mm; "
            "tfc=espesor aleta compresión, mm.\n"
            "(ii) secciones I con canales o cubreplacas sobrepuestas: rt=radio de giro "
            "eje y de componentes aleta compresión por flexión + 1/3 de la zona del alma "
            "a compresión, mm; aw=relación entre el doble del área de la zona del alma a "
            "compresión y el área de los componentes de la aleta a compresión. Para "
            "aleta compresión rectangular, aproximación conservadora: "
            "rt = bfc / raiz[12*(1 + (1/6)*aw)].\n"
            "F.2.6.4.3 Pandeo local aleta compresión:\n"
            "(a) aletas compactas: no aplica\n"
            "(b) aletas no compactas: "
            "Mn = Rpc*Myc - (Rpc*Myc - FL*Sxc)*((λ-λpf)/(λrf-λpf))  (F.2.6.4-12)\n"
            "(c) aletas esbeltas: Mn = 0.90*E*kc*Sxc / λ^2  (F.2.6.4-13)\n"
            "donde: FL definido en F.2.6.4-6a/6b; Rpc según F.2.6.4-9; kc=4/raiz(h/tw), "
            "0.35<=kc<=0.76; λ=bfc/2tfc; λpf=λp, λrf=λr (tabla B.4-1, tal como aparece en "
            "el texto de esta subsección específica).\n"
            "F.2.6.4.4 Fluencia aleta tensión:\n"
            "(a) Sxt>=Sxc: no aplica\n"
            "(b) Sxt<Sxc: Mn = Rpt*Myt  (F.2.6.4-14), donde Myt=Fy*Sxt\n"
            "Rpt: (i) hc/tw<=λpw: Rpt=Mp/Myt  (F.2.6.4-15a); (ii) hc/tw>λpw: "
            "Rpt=[Mp/Myt - (Mp/Myt-1)*((λ-λpw)/(λrw-λpw))] <= Mp/Myt  (F.2.6.4-15b)\n"
            "donde: λ=hc/tw; λpw=λp, λrw=λr (tabla B.4-1b, tal como aparece en el texto "
            "de esta subsección)."
        ),
    },
    {
        "id": "NSR10-F-F_2_6_5_a_F_2_6_6",
        "seccion": "F.2.6.5 a F.2.6.6 (Miembros sección I con alma esbelta; miembros I y canales solicitados por flexión sobre eje menor)",
        "titulo": (
            "Resistencia nominal a flexión Mn para miembros de sección I con alma "
            "ESBELTA (factor de reducción Rpg, F.2.6.5) y para flexión alrededor del eje "
            "menor en perfiles I y canales (F.2.6.6) — cierra la parte de F.2.6 dedicada a "
            "eje mayor y abre la de eje menor."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. "
            "F.2.6.5 — MIEMBROS DE SECCIÓN EN I CON SIMETRÍA DOBLE O SIMPLE, CON ALMA "
            "ESBELTA, SOLICITADOS POR FLEXIÓN ALREDEDOR DE SU EJE MAYOR — alma esbelta "
            "según F.2.2.4.1, conectada por líneas medias. Mn = menor entre: fluencia "
            "aleta compresión, pandeo lateral-torsional, pandeo local aleta compresión, "
            "fluencia aleta tensión.\n"
            "F.2.6.5.1 Fluencia aleta compresión: Mn = Rpg*Fy*Sxc  (F.2.6.5-1)\n"
            "F.2.6.5.2 Pandeo lateral-torsional: Mn = Rpg*Fcr*Sxc  (F.2.6.5-2)\n"
            "(a) Lb<=Lp: no aplica\n"
            "(b) Lp<Lb<=Lr: Fcr = Cb*[Fy - 0.3*Fy*((Lb-Lp)/(Lr-Lp))] <= Fy  (F.2.6.5-3)\n"
            "(c) Lb>Lr: Fcr = Cb*pi^2*E/(Lb/rt)^2 <= Fy  (F.2.6.5-4)\n"
            "donde: Lp según F.2.6.4-7; Lr = pi*rt*raiz(E/(0.7*Fy))  (F.2.6.5-5)\n"
            "Rpg = 1 - [aw/(1200+300*aw)]*(hc/tw - 5.7*raiz(E/Fy)) <= 1.0  (F.2.6.5-6) "
            "(factor de reducción de la resistencia a flexión); aw definido en "
            "F.2.6.4-11, no debe exceder 10; rt=radio de giro efectivo para pandeo "
            "lateral, definido en F.2.6.4.\n"
            "F.2.6.5.3 Pandeo local aleta compresión: Mn = Rpg*Fcr*Sxc  (F.2.6.5-7)\n"
            "(a) aletas compactas: no aplica\n"
            "(b) aletas no compactas: Fcr = Fy - 0.3*Fy*((λ-λpf)/(λrf-λpf))  (F.2.6.5-8)\n"
            "(c) aletas esbeltas: Fcr = 0.9*E*kc / (bf/2tf)^2  (F.2.6.5-9)\n"
            "donde: kc=4/raiz(h/tw), 0.35<=kc<=0.76; λ=bf/2tf; λpf=λp, λrf=λr (tabla "
            "F.2.2.4-1b).\n"
            "F.2.6.5.4 Fluencia aleta tensión:\n"
            "(a) Sxt>=Sxc: no aplica\n"
            "(b) Sxt<Sxc: Mn = Fy*Sxt  (F.2.6.5-10)\n\n"
            "F.2.6.6 — MIEMBROS DE SECCIÓN EN I Y CANALES SOLICITADOS POR FLEXIÓN "
            "ALREDEDOR DE SU EJE MENOR — Mn = menor entre plastificación de la sección "
            "(momento plástico) y pandeo local de la aleta.\n"
            "F.2.6.6.1 Plastificación (momento plástico): "
            "Mn = Mp = Fy*Zy <= 1.6*Fy*Sy  (F.2.6.6-1)\n"
            "F.2.6.6.2 Pandeo local aleta:\n"
            "(a) aletas compactas: no aplica\n"
            "(b) aletas no compactas: "
            "Mn = Mp - (Mp-0.7*Fy*Sy)*((λ-λpf)/(λrf-λpf))  (F.2.6.6-2)\n"
            "(c) aletas esbeltas: Mn = Fcr*Sy  (F.2.6.6-3), donde "
            "Fcr = 0.69*E / (bf/tf)^2  (F.2.6.6-4)\n"
            "donde: λ=b/tf; λpf=λp (tabla F.2.2.4-1b); λrf=raiz(E/Fy), límite de "
            "esbeltez para aletas no compactas (tabla F.2.2.4-1b); b=para aletas de "
            "perfiles I, la mitad del ancho total de la aleta bf; para aletas de "
            "canales, el ancho total de la aleta, mm; tf=espesor de la aleta, mm; "
            "Sy=módulo de sección elástico respecto al eje y, mm3 (para canal, el "
            "módulo de sección mínimo)."
        ),
    },
    {
        "id": "NSR10-F-F_2_6_7_a_F_2_6_9",
        "seccion": "F.2.6.7 a F.2.6.9 (PTE cuadrados/rectangulares y miembros en cajón, PTE circulares, secciones T y ángulos dobles)",
        "titulo": (
            "Resistencia nominal a flexión para perfiles tubulares estructurales (PTE) "
            "cuadrados/rectangulares y miembros en cajón (F.2.6.7), PTE circulares "
            "(F.2.6.8), y secciones en T y ángulos dobles cargados en el plano de "
            "simetría con pandeo lateral-torsional (F.2.6.9)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. "
            "F.2.6.7 — PERFILES TUBULARES ESTRUCTURALES (PTE) CUADRADOS O RECTANGULARES Y "
            "MIEMBROS DE SECCIÓN EN CAJÓN — simetría doble, flexión sobre cualquiera de "
            "sus ejes, almas compactas o no compactas, aletas compactas/no compactas/"
            "esbeltas (F.2.2.4). Mn = menor entre plastificación de la sección (momento "
            "plástico), pandeo local de la aleta y pandeo local del alma bajo flexión "
            "pura. Para PTE rectangulares de gran longitud (eje mayor) puede alcanzarse "
            "pandeo lateral-torsional, pero no se suministra fórmula: generalmente la "
            "deflexión de la viga controla en estos casos.\n"
            "F.2.6.7.1 Plastificación (momento plástico): Mn = Mp = Fy*Z  (F.2.6.7-1); "
            "Z=módulo de sección plástico sobre el eje de flexión, mm3.\n"
            "F.2.6.7.2 Pandeo local aleta:\n"
            "(a) secciones compactas: no aplica\n"
            "(b) aletas no compactas: "
            "Mn = Mp - (Mp-Fy*S)*[3.57*(b/t)*raiz(Fy/E) - 4.0] <= Mp  (F.2.6.7-2)\n"
            "(c) aletas esbeltas: Mn = Fy*Se  (F.2.6.7-3), donde Se=módulo de sección "
            "efectivo, con ancho efectivo de aleta compresión: "
            "be = 1.92*tf*raiz(E/Fy)*[1 - (0.38/(b/tf))*raiz(E/Fy)] <= b  (F.2.6.7-4)\n"
            "F.2.6.7.3 Pandeo local alma:\n"
            "(a) secciones compactas: no aplica\n"
            "(b) almas no compactas: "
            "Mn = Mp - (Mp-Fy*Sx)*[0.305*(h/tw)*raiz(Fy/E) - 0.738] <= Mp  (F.2.6.7-5)\n\n"
            "F.2.6.8 — PERFILES TUBULARES ESTRUCTURALES CIRCULARES — aplica a PTE "
            "circulares con D/t menor que 0.45*E/Fy. Mn = menor entre plastificación "
            "(momento plástico) y pandeo local.\n"
            "F.2.6.8.1 Plastificación: Mn = Mp = Fy*Z  (F.2.6.8-1)\n"
            "F.2.6.8.2 Pandeo local:\n"
            "(a) secciones compactas: no aplica\n"
            "(b) secciones no compactas: Mn = (0.021*E/(D/t) + Fy)*S  (F.2.6.8-2)\n"
            "(c) paredes esbeltas: Mn = Fcr*S  (F.2.6.8-3), donde "
            "Fcr = 0.33*E/(D/t)  (F.2.6.8-4)\n"
            "donde: S=módulo de sección elástico, mm3; D=diámetro exterior, mm; "
            "t=espesor de la pared, mm.\n\n"
            "F.2.6.9 — SECCIONES EN T Y ÁNGULOS DOBLES CARGADOS EN EL PLANO DE SIMETRÍA — "
            "Mn = menor entre plastificación (momento plástico), pandeo lateral-torsional "
            "y pandeo local de la aleta.\n"
            "F.2.6.9.1 Plastificación: Mn = Mp  (F.2.6.9-1), donde: "
            "Mp = Fy*Zx <= 1.6*My cuando el alma está a tensión  (F.2.6.9-2); "
            "Mp = Fy*Zx <= My cuando el alma está a compresión  (F.2.6.9-3)\n"
            "F.2.6.9.2 Pandeo lateral-torsional: "
            "Mn = Mcr = [pi*raiz(E*Iy*G*J)/Lb] * [B + raiz(1+B^2)]  (F.2.6.9-4), donde "
            "B = ±2.3*(d/Lb)*raiz(Iy/J)  (F.2.6.9-5). B es positivo cuando el alma está "
            "a tensión y negativo cuando está a compresión; si la fibra extrema del alma "
            "está sometida a compresión en algún punto de la longitud no arriostrada, se "
            "usa el valor negativo de B.\n"
            "F.2.6.9.3 Pandeo local de aletas en secciones T:\n"
            "(a) aletas compactas solicitadas a compresión por flexión: no aplica\n"
            "(b) aletas no compactas: "
            "Mn = [Mp - (Mp-0.7*Fy*Sxc)*((λ-λpf)/(λrf-λpf))] <= 1.6*My  (F.2.6.9-6)\n"
            "(c) aletas esbeltas: Mn = 0.7*E*Sxc / (bf/2tf)^2  (F.2.6.9-7)\n"
            "donde: Sxc=módulo elástico referido a la aleta a compresión, mm3; λ=bf/2tf; "
            "λpf=λp, λrf=λr (tabla F.2.2.4-1b). Para ángulos dobles con aletas "
            "perpendiculares al eje de simetría solicitadas por compresión, Mn para "
            "pandeo local se determina con F.2.6.10.3, usando el b/t de dichas aletas y "
            "tomando F.2.6.10-1 como límite superior.\n"
            "F.2.6.9.4 Pandeo local del alma de secciones T solicitadas a compresión por "
            "flexión: Mn = Fcr*Sx  (F.2.6.9-8), donde Sx=módulo de sección elástico; Fcr:\n"
            "d/tw<=0.84*raiz(E/Fy): Fcr=Fy  (F.2.6.9-9)\n"
            "0.84*raiz(E/Fy) < d/tw <= 1.03*raiz(E/Fy): "
            "Fcr = [2.55 - 1.84*(d/tw)*raiz(Fy/E)]*Fy  (F.2.6.9-10)\n"
            "d/tw > 1.03*raiz(E/Fy): Fcr = 0.69*E / (d/tw)^2  (F.2.6.9-11)\n"
            "Para ángulos dobles con aletas que conforman el alma solicitadas a "
            "compresión, Mn para pandeo local se determina con F.2.6.10.3, con el b/t de "
            "dichas aletas y tomando F.2.6.10-1 como límite superior."
        ),
    },
    {
        "id": "NSR10-F-F_2_6_10",
        "seccion": "F.2.6.10 (Perfiles angulares sencillos — plastificación, pandeo lateral-torsional, pandeo local de aleta)",
        "titulo": (
            "Resistencia nominal a flexión de perfiles angulares sencillos, con o sin "
            "restricción lateral continua: ejes geométricos vs. principales, momento de "
            "pandeo lateral-torsional elástico Me para 3 casos (eje mayor aletas iguales/"
            "desiguales, eje geométrico), y pandeo local de la aleta."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.6.10 — PERFILES "
            "ANGULARES SENCILLOS — aplica a perfiles angulares sencillos con o sin "
            "restricción lateral continua sobre su longitud. Con restricción continua "
            "contra pandeo lateral-torsional: diseño con base en flexión alrededor de "
            "ejes geométricos (x,y). Sin dicha restricción: diseño con provisiones para "
            "flexión sobre ejes principales, excepto cuando se permita usar requisitos de "
            "eje geométrico. Cuando el momento resultante tiene componentes sobre ambos "
            "ejes principales (con o sin carga axial), o un eje principal en combinación "
            "con carga axial, la relación de esfuerzos combinados se determina con "
            "F.2.8.2. Diseño ejes geométricos: propiedades calculadas para ejes x,y del "
            "ángulo, direcciones paralela/perpendicular a las aletas. Diseño ejes "
            "principales: propiedades calculadas para ejes principales mayor/menor. "
            "Mn = menor entre plastificación (momento plástico), pandeo lateral-torsional "
            "y pandeo local en las aletas. Para flexión sobre el eje menor: solo aplican "
            "plastificación y pandeo local de aleta.\n"
            "F.2.6.10.1 Plastificación (momento plástico): Mn = 1.5*My  (F.2.6.10-1); "
            "My=momento de fluencia alrededor del eje de flexión, N·mm.\n"
            "F.2.6.10.2 Pandeo lateral-torsional (sin restricción continua):\n"
            "(a) Me<=My: Mn = (0.92 - 0.17*Me/My)*Me  (F.2.6.10-2)\n"
            "(b) Me>My: Mn = (1.92 - 1.17*raiz(My/Me))*My <= 1.5*My  (F.2.6.10-3)\n"
            "donde Me (momento de pandeo lateral-torsional elástico):\n"
            "(i) flexión eje principal mayor, ángulo aletas iguales: "
            "Me = 0.46*E*b^2*t^2*Cb / L  (F.2.6.10-4)\n"
            "(ii) flexión eje principal mayor, ángulo aletas desiguales: "
            "Me = (4.9*E*Iz*Cb/L^2) * [raiz(βw^2 + 0.052*(L*t/rz)^2) + βw]  "
            "(F.2.6.10-5), donde: Cb se calcula con F.2.6.1-1, valor máximo 1.5; "
            "L=longitud sin arriostramiento lateral, mm; Iz=momento de inercia eje "
            "principal menor, mm4; rz=radio de giro eje principal menor, mm; t=espesor "
            "de la aleta del ángulo, mm; βw=propiedad de sección para ángulos aletas "
            "desiguales, positiva para aleta corta a compresión y negativa para aleta "
            "larga a compresión — si la aleta larga está a compresión en cualquier punto "
            "de la longitud no arriostrada, usar el valor negativo de βw. La fórmula "
            "para βw y valores comunes están en los comentarios de ANSI/AISC 360.\n"
            "(iii) flexión eje geométrico, ángulo aletas iguales, sin carga axial "
            "actuando, sin restricción contra pandeo lateral-torsional:\n"
            "(a) compresión máxima en el borde de la aleta: "
            "Me = (0.66*E*b^4*t*Cb/L^2) * [raiz(1+0.78*(L*t/b^2)^2) - 1]  (F.2.6.10-6a)\n"
            "(b) tensión máxima en el borde de la aleta: "
            "Me = (0.66*E*b^4*t*Cb/L^2) * [raiz(1+0.78*(L*t/b^2)^2) + 1]  (F.2.6.10-6b)\n"
            "My se toma igual a 0.80 veces el momento de fluencia calculado con el "
            "módulo de sección elástico del eje geométrico. Mn puede tomarse igual a My "
            "para ángulos sencillos con el borde de la aleta vertical a compresión y "
            "relación luz/aleta <= 1.64*(E/Fy)*raiz((t/b)^2 - 1.4*Fy/E). Con restricción "
            "contra pandeo lateral-torsional en el punto de momento máximo únicamente: "
            "Me se toma como 1.25 veces el Me calculado con F.2.6.10-6a o 6b; My igual al "
            "momento de fluencia con el módulo de sección elástico del eje geométrico.\n"
            "F.2.6.10.3 Pandeo local de la aleta — aplica cuando el borde de la aleta "
            "está a compresión.\n"
            "(a) secciones compactas: no aplica\n"
            "(b) aletas no compactas: "
            "Mn = Fy*Sc*[2.43 - 1.72*(b/t)*raiz(Fy/E)]  (F.2.6.10-7)\n"
            "(c) aletas esbeltas: Mn = Fcr*Sc  (F.2.6.10-8), donde "
            "Fcr = 0.71*E / (b/t)^2  (F.2.6.10-9)\n"
            "donde: b=ancho de la aleta a compresión, mm; Sc=módulo de sección elástico "
            "para el borde a compresión relativo al eje de flexión, mm3 — para flexión "
            "sobre un eje geométrico de ángulo aletas iguales sin restricción contra "
            "pandeo lateral-torsional, Sc se toma como 0.80 veces el módulo de sección "
            "para el eje geométrico."
        ),
    },
    {
        "id": "NSR10-F-F_2_6_11_a_F_2_6_12",
        "seccion": "F.2.6.11 a F.2.6.12 (Barras rectangulares y circulares; secciones no simétricas)",
        "titulo": (
            "Resistencia nominal a flexión de barras rectangulares y circulares "
            "(plastificación y pandeo lateral-torsional según relación Lb*d/t²), y "
            "criterio general de fluencia/pandeo lateral-torsional/pandeo local para "
            "cualquier perfil no simétrico distinto de ángulos sencillos."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.6.11 — BARRAS "
            "RECTANGULARES Y BARRAS CIRCULARES — aplica a barras rectangulares "
            "solicitadas por flexión alrededor de cualquiera de sus ejes geométricos y a "
            "barras circulares. Mn = menor entre plastificación (momento plástico) y "
            "pandeo lateral-torsional.\n"
            "F.2.6.11.1 Plastificación — para barras rectangulares con Lb*d/t^2 <= "
            "0.08*E/Fy solicitadas por flexión sobre su eje mayor, barras rectangulares "
            "sobre su eje menor, y barras circulares: "
            "Mn = Mp = Fy*Z <= 1.60*My  (F.2.6.11-1)\n"
            "F.2.6.11.2 Pandeo lateral-torsional:\n"
            "(a) barras rectangulares con 0.08*E/Fy < Lb*d/t^2 <= 1.9*E/Fy, eje mayor: "
            "Mn = Cb*[1.52 - 0.274*(Lb*d/t^2)*(Fy/E)]*My <= Mp  (F.2.6.11-2)\n"
            "(b) barras rectangulares con Lb*d/t^2 > 1.9*E/Fy, eje mayor: "
            "Mn = Fcr*Sx <= Mp  (F.2.6.11-3), donde "
            "Fcr = 1.9*E*Cb / (Lb*d/t^2)  (F.2.6.11-4)\n"
            "donde: t=ancho de la barra rectangular (dimensión paralela al eje de "
            "flexión), mm; d=peralte de la barra, mm; Lb=longitud entre puntos "
            "arriostrados contra desplazamiento lateral o torsión, mm.\n"
            "(c) barras rectangulares sobre su eje menor y barras circulares: no se "
            "requiere considerar pandeo lateral-torsional.\n\n"
            "F.2.6.12 — SECCIONES NO SIMÉTRICAS — aplica a todos los perfiles no "
            "simétricos, excepto los ángulos sencillos (cubiertos en F.2.6.10). "
            "Mn = menor entre fluencia (momento de fluencia), pandeo lateral-torsional y "
            "pandeo local: Mn = Fn*Smin  (F.2.6.12-1); Smin=mínimo módulo de sección "
            "elástico para el eje de flexión considerado, mm3.\n"
            "F.2.6.12.1 Fluencia: Fn = Fy  (F.2.6.12-2)\n"
            "F.2.6.12.2 Pandeo lateral-torsional: Fn = Fcr <= Fy  (F.2.6.12-3); "
            "Fcr=esfuerzo de pandeo lateral-torsional determinado analíticamente, MPa. "
            "Para miembros con sección en Z, se recomienda tomar Fcr como el 50% del "
            "Fcr de una sección en canal con aletas y alma de las mismas dimensiones.\n"
            "F.2.6.12.3 Pandeo local: Fn = Fcr <= Fy  (F.2.6.12-4); Fcr=esfuerzo de "
            "pandeo local determinado analíticamente, MPa."
        ),
    },
    {
        "id": "NSR10-F-F_2_6_13",
        "seccion": "F.2.6.13 (Dimensionamiento de vigas: agujeros en aleta a tensión, límites en I con almas esbeltas, cubreplacas, vigas armadas, redistribución de momentos)",
        "titulo": (
            "Cierra el numeral F.2.6 (flexión) con las reglas prácticas de dimensionamiento "
            "de vigas: reducción de resistencia por agujeros en la aleta a tensión, "
            "límites Iyc/Iy y h/tw para miembros de sección I con almas esbeltas, diseño "
            "de cubreplacas (longitud de soldadura a'), vigas armadas, y la longitud "
            "límite Lm para redistribución de momentos."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.6.13 — "
            "DIMENSIONAMIENTO DE VIGAS.\n"
            "F.2.6.13.1 Reducción de la resistencia para miembros con agujeros en la "
            "aleta a tensión — aplica a perfiles laminados/armados y vigas con "
            "cubreplacas con perforaciones, dimensionados con base en la resistencia a "
            "flexión de la sección bruta. Además de los demás estados límite, evaluar la "
            "rotura por tensión de la aleta a tensión.\n"
            "(a) Fu*Afn >= Yt*Fy*Afg: no aplica el estado límite de rotura por tensión\n"
            "(b) Fu*Afn < Yt*Fy*Afg: la resistencia nominal a flexión, en una sección con "
            "agujeros en la aleta a tensión, no se toma mayor que: "
            "Mn = (Fu*Afn/Afg)*Sx  (F.2.6.13-1)\n"
            "donde: Afg=área bruta de la aleta a tensión (F.2.2.4.3.1), mm2; Afn=área "
            "neta de la aleta a tensión (F.2.2.4.3.2), mm2; Yt=1.0 para Fy/Fu<=0.8, =1.1 "
            "en caso contrario.\n"
            "F.2.6.13.2 Límites para el dimensionamiento de miembros de sección en I — "
            "los de simetría simple deben satisfacer: 0.10 <= Iyc/Iy <= 0.90  "
            "(F.2.6.13-2). Los miembros con almas esbeltas deben satisfacer además:\n"
            "(a) a/h<=1.5: (h/tw)max = 12.0*raiz(E/Fy)  (F.2.6.13-3)\n"
            "(b) a/h>1.5: (h/tw)max = 0.40*E/Fy  (F.2.6.13-4)\n"
            "donde a=distancia libre entre rigidizadores transversales, mm. En vigas no "
            "rigidizadas, h/tw no debe exceder 260. La relación del área del alma al "
            "área de la aleta a compresión no debe exceder 10.\n"
            "F.2.6.13.3 Cubreplacas — el espesor y ancho de aletas de vigas soldadas "
            "pueden variarse mediante empalme de platinas o uso de cubreplacas. El área "
            "total de la sección transversal de cubreplacas en vigas armadas con pernos "
            "no debe exceder el 70% del área total de la aleta. Pernos de alta "
            "resistencia o soldaduras que conectan aleta-alma o cubreplaca-aleta: "
            "diseñados para resistir la fuerza cortante horizontal total resultante de "
            "las fuerzas de flexión; distribución longitudinal en proporción a la "
            "intensidad de la fuerza cortante, sin exceder el espaciamiento máximo "
            "permitido para miembros a compresión/tensión (F.2.5.6/F.2.4.4); también "
            "diseñados para transmitir a la aleta al alma cualquier carga aplicada "
            "directamente a la aleta, salvo que se tomen medidas de apoyo directo. "
            "Cubreplacas de longitud parcial: se extienden más allá del punto teórico "
            "donde dejan de requerirse; la porción extendida se conecta con pernos de "
            "alta resistencia en junta de deslizamiento crítico o con soldaduras de "
            "filete, con resistencia de diseño según F.2.10.2.2, F.2.10.3.8 o "
            "F.2.2.3.10, adecuada para desarrollar la porción de resistencia a flexión "
            "correspondiente en el punto teórico de suspensión. En cubreplacas "
            "soldadas, las soldaduras del tramo final son continuas sobre ambos bordes "
            "en una longitud a', adecuadas para desarrollar la porción de resistencia "
            "de diseño correspondiente a esa distancia a' desde el extremo:\n"
            "(a) soldadura continua a través del extremo, tamaño>=3/4 del espesor: "
            "a'=w  (F.2.6.13-5); w=ancho de la cubreplaca, mm\n"
            "(b) soldadura continua a través del extremo, tamaño<3/4 del espesor: "
            "a'=1.5*w  (F.2.6.13-6)\n"
            "(c) sin soldadura transversal en el extremo: a'=2*w  (F.2.6.13-7)\n"
            "F.2.6.13.4 Vigas armadas — cuando 2 o más vigas o canales se usan una al "
            "lado de la otra para formar un miembro a flexión, deben conectarse entre sí "
            "según F.2.5.6.2. Con cargas concentradas que se transfieren o distribuyen "
            "entre ellas, usar diafragmas soldados o conectados con pernos, con rigidez "
            "suficiente para distribuir la carga.\n"
            "F.2.6.13.5 Longitud no soportada para redistribución de momentos — para "
            "redistribución según F.2.2.3.7, la longitud no arriostrada Lb de la aleta a "
            "compresión en la zona adyacente al punto de redistribución no debe exceder "
            "Lm:\n"
            "(a) miembros sección I, simetría simple o doble, aleta compresión>=aleta "
            "tensión, cargados en el plano del alma: "
            "Lm = [0.12 + 0.076*(M1/M2)] * (E/Fy) * ry  (F.2.6.13-8)\n"
            "donde: Fy=esfuerzo mínimo de fluencia de la aleta a compresión, MPa; "
            "M1=menor momento de extremo de la longitud no arriostrada, N·mm; M2=mayor "
            "momento de extremo, N·mm; ry=radio de giro respecto al eje y, mm; (M1/M2) "
            "es positivo para doble curvatura y negativo para curvatura simple.\n"
            "(b) barras rectangulares sólidas y vigas cajón simétricas, eje mayor: "
            "Lm = [0.17 + 0.10*(M1/M2)] * (E/Fy) * ry >= 0.10*(E/Fy)*ry  (F.2.6.13-9)\n"
            "No hay límite para Lb en miembros con sección transversal circular o "
            "rectangular, ni para vigas de cualquier sección sometidas a flexión "
            "alrededor de su eje débil."
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
    print(f"OK: {len(rows)} chunks F.2.6.3-F.2.6.13 cargados con embedding. Numeral F.2.6 completo.")


if __name__ == "__main__":
    main()
