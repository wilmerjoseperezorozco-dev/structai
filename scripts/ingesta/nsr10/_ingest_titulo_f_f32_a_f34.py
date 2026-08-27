"""
NSR-10 Titulo F, F.3.2 a F.3.4 -- cierra el segundo hueco elegido por el
usuario 2026-08-27 dentro del Capitulo F.3 (Provisiones sismicas para
estructuras de acero): requisitos generales de diseno (F.3.2), analisis
(F.3.3), y requisitos generales de miembros/conexiones aplicables a TODOS
los sistemas sismicos de acero (F.3.4) -- estos numerales son prerequisito
transversal para F.3.5 (PRM), F.3.6 (PAC), F.3.7 (PRMC) y F.3.8 (muros
compuestos), que ya estaban cargados sin este fundamento comun.

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
paginas internas F-222 a F-234. Leido visualmente pagina por pagina (Read
con `pages`), no el texto plano exportado por Drive -- mismo motivo que
_ingest_titulo_f_f27_a_f291.py (formulas con subindices se desordenan en el
texto plano).

5 chunks single-topic, mismo patron que scripts anteriores de Titulo F.

Uso: python _ingest_titulo_f_f32_a_f34.py
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
        "id": "NSR10-F-F_3_2_a_F_3_3",
        "seccion": "F.3.2 a F.3.3 (Requisitos generales de diseño sísmico y análisis)",
        "titulo": (
            "Requisitos generales de diseño sísmico para acero según zona de amenaza "
            "(baja=DMI mínimo, intermedia=DMO mínimo, alta=DES obligatorio), definición "
            "de las 3 capacidades de disipación de energía (DMI/DMO/DES) por numerales "
            "de referencia, coeficiente de sobre-resistencia Ω0 en cargas amplificadas, y "
            "requisitos de análisis (elástico con secciones fisuradas en compuestos, "
            "análisis no lineal según F.2)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para estructuras de "
            "acero. F.3.2 — REQUISITOS GENERALES DE DISEÑO — establece los requisitos "
            "generales para el diseño sísmico de estructuras de acero bajo este Capítulo. "
            "Secciones: F.3.2.1 Requisitos generales de diseño sísmico, F.3.2.2 Cargas, "
            "combinaciones de carga y resistencias nominales, F.3.2.3 Tipo de sistema.\n\n"
            "F.3.2.1.1 Zonas de amenaza sísmica (según A.2.3 del Título A):\n"
            "- Zona BAJA (A.2.3.1): cumplir Título A con limitaciones del Capítulo A.3; "
            "como mínimo capacidad de disipación de energía MÍNIMA (DMI, F.3.2.1.2.1); se "
            "permite también DMO o DES.\n"
            "- Zona INTERMEDIA (A.2.3.2): como mínimo capacidad MODERADA (DMO, "
            "F.3.2.1.2.2); se permite también DES.\n"
            "- Zona ALTA (A.2.3.3): SOLO se permite capacidad ESPECIAL (DES, "
            "F.3.2.1.2.3) — es la única opción, no DMI ni DMO.\n\n"
            "F.3.2.1.2 Requisitos de capacidad de disipación de energía (rango "
            "inelástico):\n"
            "- DMI (F.3.2.1.2.1): la que ofrecen elementos de acero diseñados según "
            "Capítulos F.1 y F.2, más F.3.1.10 (pórticos resistentes a momento) y F.3.1.13 "
            "(pórticos arriostrados concéntricamente).\n"
            "- DMO (F.3.2.1.2.2): F.1+F.2 más F.3.1.9 (pórticos resistentes a momento).\n"
            "- DES (F.3.2.1.2.3): F.1+F.2 más F.3.1.8 (PRM), F.3.1.11 (pórticos con "
            "cerchas dúctiles), F.3.1.12 (PAC), F.3.1.14 (pórticos arriostrados "
            "excéntricamente), F.3.1.15 (pórticos con riostras de pandeo restringido) y "
            "F.3.1.16 (estructuras con muros de cortante con placa de acero).\n\n"
            "F.3.2.2.1 Cargas y combinaciones de carga — usar las de B.2.4, más: incluir "
            "en el análisis los efectos ortogonales del sismo según A.3.6.3 a menos que se "
            "especifique lo contrario. Cuando el Capítulo pida revisiones con cargas "
            "sísmicas AMPLIFICADAS, la componente horizontal de la carga E (Título A) se "
            "multiplica por el coeficiente de sobrerresistencia Ω0 (definido en A.3.3.9).\n"
            "F.3.2.2.2 Resistencia requerida — la mayor entre: (a) la que resulte del "
            "análisis con las combinaciones de carga del Título B y F.3.3; (b) la dada "
            "explícitamente en F.3.4, F.3.5, F.3.6, F.3.7 y F.3.8.\n\n"
            "F.3.2.3 Tipo de sistema — el sistema de resistencia sísmico debe contener uno "
            "o más de: PRM (pórticos resistentes a momento), PAC (pórticos arriostrados "
            "concéntricamente) o MC (muros de cortante), según los requisitos "
            "especificados en F.3.4, F.3.5, F.3.6, F.3.7 y F.3.8.\n\n"
            "F.3.3 — ANÁLISIS — establece los requisitos de análisis. Secciones: F.3.3.1 "
            "Requisitos generales, F.3.3.2 Requisitos adicionales, F.3.3.3 Análisis no "
            "lineal.\n"
            "F.3.3.1 Requisitos generales — el análisis debe hacerse según el Título B y "
            "el Capítulo F.2. Cuando el diseño se base en análisis elástico, las "
            "propiedades de rigidez de miembros en sistemas de acero deben basarse en las "
            "secciones elásticas, y los sistemas COMPUESTOS deben incluir los efectos de "
            "las secciones FISURADAS.\n"
            "F.3.3.2 Requisitos adicionales — deben hacerse análisis adicionales según lo "
            "especifican F.3.5, F.3.6, F.3.7 y F.3.8.\n"
            "F.3.3.3 Análisis no lineal — cuando se realice para satisfacer requisitos de "
            "este Capítulo, debe hacerse de acuerdo con el Título F.2."
        ),
    },
    {
        "id": "NSR10-F-F_3_4_1_1_tabla_esbeltez",
        "seccion": "F.3.4.1.1 (Clasificación de secciones por ductilidad + Tabla F.3.4-1, límites ancho-espesor)",
        "titulo": (
            "Clasificación de miembros sísmicos de acero por ductilidad moderada o alta "
            "según límites de esbeltez ancho-espesor (Tabla F.3.4-1 completa: aletas de "
            "perfiles I/canales/T, PTE rectangular/circular, almas de vigas-columnas y "
            "riostras, elementos de miembros compuestos rellenos)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.4 — "
            "REQUISITOS GENERALES DE DISEÑO — establece los requisitos de diseño de "
            "miembros y conexiones, aplicables a TODOS los sistemas sísmicos de acero "
            "(PRM, PAC, MC) definidos en F.3.5-F.3.8. Secciones: F.3.4.1 Requisitos de "
            "los miembros, F.3.4.2 Conexiones, F.3.4.3 Compatibilidad de deformación para "
            "miembros/conexiones que no pertenezcan al SRS, F.3.4.4 Pilotes de acero.\n\n"
            "F.3.4.1 — REQUISITOS DE LOS MIEMBROS — los miembros de estructuras PRM, PAC y "
            "MC del SRS (sistema de resistencia sísmica) deben cumplir estos requisitos.\n"
            "F.3.4.1.1 Clasificación de secciones por ductilidad — algunos miembros del "
            "SRS en los que se esperan deformaciones inelásticas bajo el sismo de diseño "
            "se clasifican como de ductilidad MODERADA o ALTA. Se requiere cuando lo "
            "indican F.3.5, F.3.6, F.3.7, F.3.8 y F.3.4.4.\n"
            "F.3.4.1.1.1 Requisitos de sección en miembros dúctiles — perfiles de acero en "
            "miembros con ductilidad moderada y alta deben tener aletas conectadas "
            "continuamente al alma o almas. Columnas compuestas embebidas: cumplir "
            "F.3.4.1.4.2.1 (ductilidad moderada) o F.3.4.1.4.2.2 (ductilidad alta). "
            "Columnas compuestas rellenas: cumplir F.3.4.1.4.3. Miembros de concreto "
            "reforzado: cumplir Título C.\n"
            "F.3.4.1.1.2 Límites ancho-espesor de perfiles de acero o compuestos — "
            "ductilidad MODERADA: esbeltez de elementos a compresión < lambda_dm (Tabla "
            "F.3.4-1). Ductilidad ALTA: esbeltez < lambda_da (Tabla F.3.4-1).\n\n"
            "Tabla F.3.4-1 — Valores límite de la relación ancho-espesor para elementos a "
            "compresión (lambda_da=ductilidad alta, lambda_dm=ductilidad moderada):\n"
            "ELEMENTOS NO ATIESADOS:\n"
            "- Aletas de perfiles laminados en I, canales y secciones en T (relación b/t): "
            "lambda_da=0.30*raiz(E/Fy); lambda_dm=0.38*raiz(E/Fy).\n"
            "- Aletas de ángulos sencillos o dobles con separadores (b/t): "
            "lambda_da=0.30*raiz(E/Fy); lambda_dm=0.38*raiz(E/Fy).\n"
            "- Aletas salientes de pares de ángulos en contacto continuo (b/t): "
            "lambda_da=0.30*raiz(E/Fy); lambda_dm=0.38*raiz(E/Fy).\n"
            "- Aletas de pilotes de acero en H (F.3.4.4) (b/t): lambda_da=0.45*raiz(E/Fy); "
            "lambda_dm=NA (no aplica).\n"
            "- Almas de secciones en T (d/t): lambda_da=0.30*raiz(E/Fy) [nota a], "
            "lambda_dm=0.38*raiz(E/Fy).\n"
            "  Nota [a]: para perfiles T en compresión, este límite puede incrementarse a "
            "0.38*raiz(E/Fy) si se cumplen 2 condiciones: (1) el pandeo del miembro a "
            "compresión ocurre alrededor del plano del alma de la T; (2) la carga a "
            "compresión se transfiere en las conexiones del extremo solo a la cara "
            "exterior de la aleta de la T (conexión excéntrica que transmite esfuerzos de "
            "compresión reducidos en la punta del alma).\n"
            "ELEMENTOS ATIESADOS:\n"
            "- Paredes de PTE rectangular; aletas de perfiles I encajonados o cajones "
            "armados (b/t); placas laterales de perfiles I encajonados y paredes de "
            "cajones armados usados como diagonales (h/t): lambda_da=0.55*raiz(E/Fy) "
            "[nota b]; lambda_dm=0.64*raiz(E/Fy) [nota c].\n"
            "  Nota [b]: para aletas de perfiles I encajonados o cajones armados para "
            "columnas en sistemas PRM-DES, no debe ser mayor que 0.6*raiz(E/Fy).\n"
            "  Nota [c]: la relación ancho-espesor límite en paredes de PTE rectangular, "
            "aletas de I encajonadas y aletas de cajones armados usados como vigas y "
            "columnas no debe ser mayor que 1.12*raiz(E/Fy).\n"
            "- Almas de perfiles laminados o armados en I usados como vigas y columnas "
            "(h/tw) [nota d], y placas laterales en perfiles I encajonados usados como "
            "vigas y columnas (h/t): para Ca<=0.125: lambda_da=2.45*raiz(E/Fy)*(1-0.93*Ca), "
            "lambda_dm=3.76*raiz(E/Fy)*(1-2.75*Ca); para Ca>0.125: "
            "lambda_da=0.77*raiz(E/Fy)*(2.93-Ca)>=1.49*raiz(E/Fy), "
            "lambda_dm=1.12*raiz(E/Fy)*(2.33-Ca)>=1.49*raiz(E/Fy). Ca = Pu/(phi_b*Py).\n"
            "  Nota [d]: para vigas en I en sistemas PRM-DES con Ca<=0.125, la esbeltez "
            "h/tw mínima no debe ser mayor que 2.45*raiz(E/Fy); en PRM-DMO, no mayor que "
            "3.76*raiz(E/Fy).\n"
            "- Almas de secciones en cajón armadas usadas para vigas y columnas (h/t): "
            "misma fórmula con Ca que la fila anterior (Ca=Pu/(phi_b*Py)).\n"
            "- Almas de perfiles en I laminados o armados usados como riostras (h/tw): "
            "lambda_da=lambda_dm=1.49*raiz(E/Fy).\n"
            "- Almas de pilotes de acero en H (h/tw): lambda_da=0.94*raiz(E/Fy); "
            "lambda_dm=NA.\n"
            "- Paredes de PTE circular (D/t): lambda_da=0.038*E/Fy; "
            "lambda_dm=0.044*E/Fy [nota e].\n"
            "  Nota [e]: la relación diámetro-espesor límite para PTE circulares "
            "utilizados como vigas o columnas no debe ser mayor que 0.07*E/Fy.\n"
            "ELEMENTOS COMPUESTOS (miembros rellenos):\n"
            "- Paredes de miembros rectangulares rellenos (b/t): lambda_da=1.4*raiz(E/Fy); "
            "lambda_dm=2.26*raiz(E/Fy).\n"
            "- Paredes de miembros redondos rellenos (D/t): lambda_da=0.076*E/Fy; "
            "lambda_dm=0.15*E/Fy."
        ),
    },
    {
        "id": "NSR10-F-F_3_4_1_2_a_F_3_4_1_3",
        "seccion": "F.3.4.1.2 a F.3.4.1.3 (Arriostramiento para estabilidad de vigas, arriostramiento especial en rótulas plásticas, zonas protegidas)",
        "titulo": (
            "Requisitos de arriostramiento lateral/torsional para vigas sísmicas de "
            "ductilidad moderada y alta (espaciamiento máximo Lb en función de ry, E, Fy), "
            "arriostramiento especial adyacente a rótulas plásticas (resistencia requerida "
            "Pu/Mu en función de Ry*Z*Fy), y definición de zonas protegidas."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.4.1.2 — "
            "ARRIOSTRAMIENTO PARA LA ESTABILIDAD DE LAS VIGAS — cuando se requiera en "
            "F.3.5, F.3.6, F.3.7 y F.3.8, se debe suministrar arriostramiento al pandeo "
            "lateral-torsional de los perfiles de acero o embebidos solicitados por "
            "flexión.\n"
            "F.3.4.1.2.1 Miembros con ductilidad MODERADA:\n"
            "(a) Miembros de acero: (i) ambas aletas de la viga arriostradas lateralmente, "
            "o la sección transversal arriostrada a torsión; (ii) el arriostramiento debe "
            "cumplir los requisitos de F.2.19 para riostras de arriostramiento lateral o "
            "torsional de vigas, con resistencia a flexión esperada del miembro: "
            "Mu=Ry*Z*Fy (F.3.4.1-1), adoptando Cd (definido en F.2.19) igual a la unidad; "
            "(iii) espaciamiento máximo del arriostramiento: Lb=0.17*ry*E/Fy (F.3.4.1-2).\n"
            "(b) Vigas compuestas embebidas: (i) ambas aletas arriostradas lateralmente o "
            "sección arriostrada a torsión; (ii) cumplir requisitos del Título F.2 para "
            "arriostramiento con Mu=Mp_esp de la viga (F.3.7.2.6.4), Cd=1; (iii) "
            "espaciamiento máximo Lb=0.17*ry*E/Fy (F.3.4.1-3), usando propiedades de la "
            "sección de acero y ry calculado en el plano de pandeo con la sección "
            "transformada elástica.\n"
            "F.3.4.1.2.2 Miembros con ductilidad ALTA — adicionalmente a F.3.4.1.2.1(1)(i,"
            "ii) y (2)(i,ii): espaciamiento máximo Lb=0.086*ry*E/Fy. Para vigas compuestas "
            "embebidas, usar propiedades de sección de acero y ry en el plano de pandeo "
            "según sección transformada elástica.\n\n"
            "F.3.4.1.2.3 Arriostramiento especial en rótulas plásticas — se debe "
            "suministrar arriostramiento adyacente a zonas donde se espera se desarrolle "
            "una rótula plástica (según F.3.5, F.3.6, F.3.7, F.3.8):\n"
            "(a) Vigas de acero: (i) ambas aletas arriostradas lateralmente o sección "
            "arriostrada a torsión; (ii) resistencia requerida del arriostramiento lateral "
            "a un lado de la rótula: Pu=0.06*Ry*Z*Fy/ho (F.3.4.1-4), ho=distancia entre "
            "centroides de aletas, mm; resistencia requerida del arriostramiento torsional "
            "a un lado de la rótula: Mu=0.06*Ry*Z*Fy (F.3.4.1-5); (iii) rigidez requerida "
            "de la riostra según F.2.20 para arriostramiento lateral o torsional, Cd=1, "
            "resistencia a flexión esperada: Mu=Ry*Z*Fy (F.3.4.1-6).\n"
            "(b) Vigas compuestas embebidas: (i) ambas aletas arriostradas o sección "
            "arriostrada a torsión; (ii) resistencia requerida lateral a un lado de la "
            "rótula: Pu=0.06*Mp_esp/ho (F.3.4.1-7), Mp_esp según F.3.7.2.6.4; resistencia "
            "requerida torsional: Mu=0.06*Mp_esp de la viga; (iii) rigidez requerida según "
            "F.2.20 con Mu=Mp_esp de la viga, Cd=1.\n\n"
            "F.3.4.1.3 — ZONAS PROTEGIDAS — las discontinuidades especificadas en "
            "F.3.9.2.1 que resulten de fabricación/montaje, o de instalación de "
            "accesorios, NO pueden realizarse en el área de un miembro o elemento de "
            "conexión designado como zona protegida. Excepción: solo se permiten "
            "conectores de cortante tipo espigo, soldados, y otras conexiones si están "
            "incluidas en conexiones precalificadas según F.3.11.1, F.3.11.2 y F.3.11.3."
        ),
    },
    {
        "id": "NSR10-F-F_3_4_1_4",
        "seccion": "F.3.4.1.4 (Columnas: resistencia requerida, columnas compuestas embebidas y rellenas)",
        "titulo": (
            "Requisitos de columnas del SRS (PRM/arriostrados/muros de cortante): "
            "resistencia requerida (máxima carga transferida + sobrerresistencia), "
            "refuerzo transversal de columnas compuestas embebidas con ductilidad "
            "moderada/alta (fórmula Ash=0.09*hcc*s*(1-Fy*As/Pn)*(f'c/Fyh)), y columnas "
            "compuestas rellenas."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.4.1.4 — "
            "COLUMNAS — las que hagan parte de sistemas PRM, arriostrados y muros de "
            "cortante deben satisfacer estos requisitos.\n\n"
            "F.3.4.1.4.1 Resistencia requerida — los efectos de las cargas resultantes de "
            "los requisitos del análisis para sistemas de F.3.5, F.3.6, F.3.7 y F.3.8 "
            "(excepto que F.3.4.1.4.1 NO aplica a F.3.7.1, F.3.8.1 y F.3.8.4). La "
            "resistencia a compresión con las combinaciones de carga del Título B, "
            "incluyendo la carga sísmica amplificada, puede despreciar los momentos "
            "aplicados a menos que resulten de una carga aplicada a la columna entre "
            "puntos de soporte lateral. La resistencia a compresión no requiere ser mayor "
            "que el mayor de: (a) la máxima carga transferida a la columna por el sistema, "
            "incluyendo los efectos de la sobrerresistencia del material y el "
            "endurecimiento por deformación; (b) las fuerzas correspondientes a la "
            "resistencia de la cimentación al levantamiento por volcamiento.\n\n"
            "F.3.4.1.4.2 Columnas compuestas embebidas — las de sistemas F.3.7 y F.3.8 "
            "deben cumplir F.2.9 además de estos requisitos, para ductilidad moderada y "
            "alta.\n"
            "(1) Ductilidad MODERADA: (i) espaciamiento máximo del refuerzo transversal en "
            "extremos superior/inferior = el menor entre: mitad de la dimensión menor de "
            "la sección; 8 veces el diámetro de la barra longitudinal; 24 veces el "
            "diámetro del refuerzo transversal; 300mm. (ii) estos espaciamientos se "
            "mantienen a lo largo de: 1/6 de la altura libre de la columna; máxima "
            "dimensión de la sección transversal; 450mm — medidos desde la cara del nudo y "
            "ambos lados de secciones con articulación plástica esperada. (iii) el "
            "espaciamiento en el resto de la columna no debe exceder el doble de lo "
            "anterior. (iv) empalmes/detalles de extremo para columnas DMI (secciones "
            "F.3.7.1, F.3.8.1, F.3.8.4) deben satisfacer C.7.8.2, C.21.1.6 y C.21.1.7 — "
            "considerar cambios abruptos de rigidez y resistencia nominal a tensión "
            "(transiciones a secciones de concreto sin miembros embebidos, transiciones "
            "entre secciones distintas de acero, bases de columnas). (v) no se permiten "
            "mallas electrosoldadas como refuerzo transversal con ductilidad moderada.\n"
            "(2) Ductilidad ALTA: además de (1): (i) refuerzo longitudinal que transmite "
            "cargas cumple C.21.6.3. (ii) refuerzo transversal = estribos de confinamiento "
            "(definidos en Título C.21) que cumplen: (a) área mínima de refuerzo "
            "transversal: Ash = 0.09*hcc*s*(1-Fy*As/Pn)*(f'c/Fyh)  (F.3.4.1-8), donde "
            "hcc=dimensión de la sección transversal confinada del núcleo (centro a "
            "centro del refuerzo transversal), mm; s=espaciamiento del refuerzo "
            "transversal a lo largo del eje longitudinal, mm; Fy=esfuerzo de fluencia "
            "mínimo del núcleo de acero estructural, MPa; As=área de la sección "
            "transversal del núcleo de acero estructural, mm2; Pn=resistencia nominal a "
            "compresión axial de la columna compuesta, N; f'c=resistencia a compresión del "
            "concreto, MPa; Fyh=esfuerzo de fluencia mínimo del refuerzo transversal, MPa. "
            "No es necesario satisfacer F.3.4.1-8 si la resistencia nominal de la sección "
            "aislada de acero estructural embebida es mayor que la obtenida con la "
            "combinación 1.0D+0.5L. (b) espaciamiento máximo del refuerzo transversal a lo "
            "largo de la columna = el menor entre 6 diámetros de la barra longitudinal de "
            "transferencia de carga o 150mm. (c) en las especificaciones de F.3.4.1.4.2(1)"
            "(ii,iii,iv), el espaciamiento máximo debe ser el menor de 1/4 de la menor "
            "dimensión del miembro o 100mm; estribos cruzados y otros refuerzos de "
            "confinamiento no deben espaciarse más de 350mm a centros en la dirección "
            "transversal. (iii) columnas compuestas embebidas de un pórtico arriostrado "
            "con cargas nominales a compresión >0.2*Pn deben tener refuerzo transversal "
            "según (2)(ii)(c) en toda su longitud (excepto si la sección aislada de acero "
            "es más resistente que 1.0D+0.5L). (iv) columnas que soportan reacciones de "
            "miembros con discontinuidad en rigidez (muros/pórticos arriostrados) deben "
            "tener refuerzo transversal según (2)(ii)(c) en la longitud total por debajo "
            "de la discontinuidad si la fuerza axial a compresión excede 0.1*Pn — se "
            "extiende hacia arriba como mínimo la longitud requerida para desarrollar la "
            "fluencia total del perfil y el refuerzo longitudinal. (v) columnas compuestas "
            "embebidas en PRMC-DES: refuerzo transversal según (2)(ii) arriba/abajo de la "
            "unión en la región de F.3.4.1.4.2(1)(ii); columna fuerte-viga débil según "
            "F.3.7.3.4.1; base detallada para desarrollar articulación plástica; "
            "resistencia requerida a cortante de la columna según ACI 318 21.6.5.1. (vi) "
            "cuando la columna termina en losa de fundación/zapata, el refuerzo "
            "transversal se extiende mínimo 300mm dentro de la zapata/losa; si termina en "
            "muro, se extiende dentro del muro por lo menos la longitud requerida para "
            "desarrollo de fluencia total del acero embebido y del refuerzo longitudinal.\n\n"
            "F.3.4.1.4.3 Columnas compuestas rellenas — aplicable a columnas que cumplen "
            "las limitaciones de F.2.9.2, diseñadas según el Capítulo F.2, excepto que la "
            "resistencia nominal a cortante de la columna compuesta corresponde a la "
            "sección de acero aislada, con base en su área efectiva a cortante.\n\n"
            "F.3.4.1.5 — DIAFRAGMAS COMPUESTOS — el diseño de diafragmas de piso o techo "
            "compuestos debe cumplir estos requisitos para efectos sísmicos.\n"
            "F.3.4.1.5.1 Transferencia de carga — deben determinarse los detalles para "
            "transferir cargas entre diafragmas y miembros de borde, elementos "
            "colectores, y elementos del SRS.\n"
            "F.3.4.1.5.2 Resistencia nominal a cortante — la resistencia nominal a "
            "cortante en el plano de diafragmas compuestos con o sin tableros metálicos "
            "se toma como la resistencia a cortante nominal del concreto reforzado sobre "
            "la cresta del tablero metálico según el Título C; alternativamente puede "
            "determinarse con ensayos de corte en el plano de diafragmas de concreto."
        ),
    },
    {
        "id": "NSR10-F-F_3_4_2_a_F_3_4_4",
        "seccion": "F.3.4.2 a F.3.4.4 (Conexiones del SRS, compatibilidad de deformación, pilotes de acero)",
        "titulo": (
            "Requisitos de conexiones del sistema de resistencia sísmico: juntas pernadas "
            "(pernos alta resistencia deslizamiento crítico Clase A), uniones soldadas, "
            "empalmes de columna (localización, resistencia requerida flexión/cortante/"
            "tensión), bases de columna, conexiones compuestas, pernos de anclaje; más "
            "compatibilidad de deformación de miembros fuera del SRS y pilotes de acero."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.4.2 — "
            "CONEXIONES.\n"
            "F.3.4.2.1 Alcance — las conexiones, juntas y pernos del SRS deben cumplir "
            "F.2.10 más requisitos adicionales de este numeral. Empalmes y placas de base "
            "de columnas que NO sean parte del SRS deben satisfacer F.3.4.2.5.1, "
            "F.3.4.2.5.3 y F.3.4.2.6. Zonas protegidas en elementos de conexión: cumplir "
            "F.3.4.1.3 y F.3.9.2.1.\n"
            "F.3.4.2.2 Juntas pernadas: (1) todos los pernos deben ser de alta resistencia "
            "totalmente tensionados, superficies preparadas para juntas de deslizamiento "
            "crítico Clase A (F.2.10.3.8) — excepción: caras con recubrimientos no "
            "ensayados o pinturas con coeficiente menor que Clase A permitidas para "
            "conexiones a momento con placa de extremo (F.3.5.1) o conexiones pernadas "
            "donde los efectos sísmicos se transfieren por tensión o compresión entre "
            "placas pero no por cortante en los pernos. (2) perforaciones estándar o "
            "ranuras cortas perpendiculares a la carga — excepción: riostras de F.3.6.1-"
            "F.3.6.4 pueden usar perforaciones agrandadas en junta de deslizamiento "
            "crítico, solo en una de las placas; deben satisfacer también aplastamiento y "
            "cortante en el perno. (3) resistencia de diseño a cortante de conexiones "
            "pernadas con perforaciones estándar: calcular como aplastamiento según "
            "F.2.10.3.6-F.2.10.3.10, resistencia nominal para aplastamiento no mayor que "
            "2.4*d*t*Fu. (4) pernos y soldadura NO deben diseñarse para compartir fuerza en "
            "una misma conexión (toda con pernos o toda con soldaduras), excepto en "
            "conexión a momento donde aletas soldadas transmiten flexión y alma empernada "
            "resiste cortante.\n"
            "F.3.4.2.3 Uniones soldadas — diseñar según F.2.10.\n"
            "F.3.4.2.4 Placas de continuidad y rigidizadores — diseño considerando "
            "longitudes de contacto reducidas de aletas y alma basadas en las dimensiones "
            "del filete de esquina (F.3.9.2.4).\n"
            "F.3.4.2.5 Empalmes de columnas:\n"
            "F.3.4.2.5.1 Localización — para TODAS las columnas del edificio (incluidas "
            "las que no son del SRS), empalmes a >=1.2m de las aletas de la conexión "
            "viga-columna. Excepciones: (a) altura libre de columna <2.4m: empalme a mitad "
            "de la altura libre; (b) empalmes con aletas y alma conectadas por soldaduras "
            "de penetración completa: a distancia mayor que el peralte de la columna; (c) "
            "empalmes de columnas compuestas.\n"
            "F.3.4.2.5.2 Resistencia requerida — la mayor entre: (a) resistencia requerida "
            "de las columnas según F.3.5-F.3.8 y F.3.4.1.4.1; (b) resistencia con "
            "combinaciones del Título B incluyendo carga sísmica amplificada (no mayor que "
            "cargas máximas transferibles). Empalmes soldados sujetos a tensión con carga "
            "sísmica amplificada: (a) soldaduras a tope de penetración parcial: resistencia "
            "de diseño >=200% de la requerida; (b) resistencia de diseño de cada empalme "
            "en aletas >= 0.5*Ry*Fy*bf*tf, donde Ry*Fy=esfuerzo de fluencia esperado, "
            "bf*tf=área de la aleta de la menor columna conectada; (c) con soldaduras "
            "acanaladas de penetración completa y esfuerzo de tensión en cualquier punto "
            ">0.3*Fy, requieren transiciones graduales entre aletas de espesor/ancho "
            "distinto (AWS D1.8 cláusula 4.2).\n"
            "F.3.4.2.5.3 Resistencia requerida a cortante — para TODAS las columnas: "
            "Mpc/H, donde Mpc=menor resistencia plástica nominal a flexión de la sección "
            "de columna para la dirección considerada, H=altura de entrepiso. La "
            "resistencia requerida del SRS debe ser el mayor entre esto y lo determinado "
            "en F.3.4.2.5.2(a,b).\n"
            "F.3.4.2.5.4 Configuración de empalmes en perfiles de acero — pueden ser "
            "pernados, soldados, o mixtos (soldados en una columna, pernados en otra); "
            "cumplir requisitos específicos de F.3.5-F.3.8. Con placas o canales en ambos "
            "lados del alma; empalmes con juntas acanaladas soldadas a tope: extensiones "
            "de soldadura removidas según AWS D1.8 cláusula 6.10 (no necesario remover "
            "platinas de respaldo en soldaduras acanaladas).\n"
            "F.3.4.2.5.5 Empalmes en columnas compuestas embebidas — según F.3.4.1.4.2 y "
            "C.21.6.3.2.\n"
            "F.3.4.2.6 Bases de columnas — resistencia requerida de placas de base según "
            "esta sección. Elementos de acero en la base (placas, pernos anclaje, "
            "atiesadores, llaves de cortante) diseñados según Capítulo F.2. Columnas "
            "soldadas a placas de base con soldaduras acanaladas: remover extensiones y "
            "platinas de respaldo (excepto en interior de aletas/alma de secciones I sin "
            "remover si se añade soldadura de filete de 8mm). Elementos de concreto en la "
            "base (profundidad embebida de pernos de anclaje y refuerzo): Apéndice C-D del "
            "Título C.\n"
            "F.3.4.2.6.1 Resistencia axial requerida — suma de componentes verticales de "
            "resistencia requerida de elementos de acero conectados en la base, no menor "
            "que el mayor entre: (a) carga axial con combinaciones del Título B incluyendo "
            "carga sísmica amplificada; (b) resistencia axial requerida de empalmes de "
            "columna (F.3.4.2.5).\n"
            "F.3.4.2.6.2 Resistencia requerida a cortante — suma de componentes "
            "horizontales de elementos de acero conectados en la base: (a) riostras "
            "diagonales: componente horizontal de la resistencia requerida por las "
            "conexiones de la riostra para el SRS; (b) columnas: igual a la resistencia "
            "requerida a cortante del empalme de columna (F.3.4.2.5.3).\n"
            "F.3.4.2.6.3 Resistencia requerida a flexión (cuando la conexión a fundación se "
            "diseña como conexión a momento) — suma de resistencia requerida de elementos "
            "de acero conectados a la placa de base: (a) riostras diagonales: por lo menos "
            "la resistencia requerida de las conexiones de riostra; (b) columnas: al menos "
            "el menor entre 1.1*Ry*Fy*Z de la columna, o el momento con combinaciones de "
            "carga incluyendo la carga sísmica amplificada. Momentos de conexiones "
            "diseñadas como articulaciones pueden ignorarse.\n"
            "F.3.4.2.7 Conexiones compuestas — para edificaciones con sistemas compuestos "
            "acero-concreto donde las cargas sísmicas se transfieren entre componentes: "
            "(1) transferencia de fuerza por (a) contacto directo/aplastamiento interno, "
            "(b) conexiones de cortante, (c) cortante por fricción con fuerza de agarre "
            "por refuerzo normal al plano de transferencia, (d) combinación de los "
            "anteriores solo si compatibles en rigidez/deformación (no se cuenta con "
            "adherencia potencial). (2) resistencia nominal a aplastamiento/cortante por "
            "fricción según Capítulos C.10/C.11; reducir 25% para SRS compuestos "
            "(F.3.7.3, F.3.8.2, F.3.8.3, F.3.8.5, F.3.8.6) a menos que se sustente mayor "
            "resistencia con ensayos cíclicos. (3) vigas embebidas en columnas/muros de "
            "concreto: colocar atiesadores de cara en las aletas de la viga. (4) "
            "resistencia nominal a cortante de zona de panel de acero embebido = suma de "
            "resistencias nominales del acero (F.3.5.3.6.5) y del concreto reforzado "
            "confinado (C.21.7). (5) refuerzo para fuerzas de tensión, confinamiento "
            "transversal, longitudes de desarrollo según Capítulo C.12; sistemas F.3.7.3, "
            "F.3.8.2, F.3.8.3, F.3.8.5, F.3.8.6 cumplen además C.21.7.5. (6) requisitos "
            "adicionales: (a) placa que transfiere fuerzas de diafragma: refuerzo diseñado "
            "y anclado para conducir tensión en todas las secciones críticas (vigas "
            "colectoras, columnas, riostras, muros); (b) conexiones viga acero-columna "
            "concreto: estribos de confinamiento con ACI 21.7, la viga de acero puede "
            "considerarse que da confinamiento en ancho igual al peralte del perfil con "
            "atiesadores de cara soldados a las aletas; se permiten empalmes traslapados "
            "de barras perimetrales si el confinamiento del traslapo lo provee un "
            "atiesador u otro medio (sistemas F.3.7.1, F.3.7.2, F.3.8.1, F.3.8.4); (c) "
            "barras longitudinales de columnas de concreto/compuestas detalladas para "
            "reducir deslizamiento por altas fuerzas transferidas en conexiones "
            "viga-columna.\n"
            "F.3.4.2.8 Pernos de anclaje — cuando se usen anclajes tipo espigo o barras de "
            "refuerzo soldadas en SRS DMO o DES (F.3.7.2, F.3.7.3, F.3.7.4, F.3.8.2, "
            "F.3.8.3, F.3.8.5, F.3.8.6): resistencia a cortante y tensión reducida 25% de "
            "la especificada en F.2.9. Reducción NO necesaria para componentes de "
            "gravedad y colectores diseñados para carga sísmica amplificada.\n\n"
            "F.3.4.3 — COMPATIBILIDAD DE DEFORMACIONES DE MIEMBROS Y CONEXIONES QUE NO "
            "HAGAN PARTE DEL SRS — cuando se requiera, estos elementos deben diseñarse "
            "para resistir la combinación de: efectos de cargas de gravedad + efectos de "
            "las deformaciones que ocurran con la deriva de piso de diseño calculada según "
            "el Título A.\n\n"
            "F.3.4.4 — PILOTES DE ACERO.\n"
            "F.3.4.4.1 Requisitos de diseño — cumplir el Capítulo F.2 de diseño de "
            "miembros por cargas combinadas, más F.3.4.1.1 para miembros de ductilidad "
            "alta.\n"
            "F.3.4.4.2 Pilotes inclinados — con pilotes inclinados y verticales en un "
            "grupo, los verticales deben diseñarse para resistir los efectos combinados de "
            "cargas muertas y vivas SIN considerar los inclinados.\n"
            "F.3.4.4.3 Pilotes a tensión — la tensión en cada pilote debe transferirse a "
            "su cabeza por medios mecánicos: llaves de cortante, varillas de refuerzo o "
            "conectores soldados a la porción embebida.\n"
            "F.3.4.4.4 Zona protegida — para cada pilote, una longitud igual al peralte de "
            "la sección transversal del pilote por debajo de la cabeza del pilote se "
            "considera zona protegida, cumpliendo F.3.4.1.3 y F.3.9.2.1."
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
    print(f"OK: {len(rows)} chunks F.3.2-F.3.4 cargados con embedding.")


if __name__ == "__main__":
    main()
