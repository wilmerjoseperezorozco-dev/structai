"""
Batch 2 de reauditoria Titulo C (NSR-10): inserta chunks verbatim reales para
C.10 (Flexion y cargas axiales), C.11 (Cortante y torsion) y C.12 (Longitudes
de desarrollo y empalmes del refuerzo), corrigiendo la numeracion equivocada
de los chunks sinteticos obsoletos (C-SEC8-* decia "C.8" para contenido que
en realidad es C.10 flexion; C-SEC9-* decia "C.9" para contenido que es C.11
cortante; C-SEC10-* decia "C.10" para contenido que es C.12 desarrollo;
C-SEC11-FORM1 decia "C.11" para contenido que es C.14 muros).

Fuente: extraccion via Google Drive de NSR-10-377-387.pdf, NSR-10-389-407.pdf,
NSR-10-409-419.pdf (carpeta Drive NSR10, id 1D7-UD-r543j4hUMiegPQ4fDwialfqiEB),
verificado contra nsr10_catalogo_maestro.json (catalogo pagina por pagina).

Uso: python _ingest_titulo_c_batch2.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título C — Concreto Estructural"

CHUNKS = [
    {
        "id": "NSR10-C-C_10a",
        "seccion": "C.10.1 a C.10.7",
        "titulo": (
            "Flexion y cargas axiales: hipotesis de diseno (deformacion max. 0.003, bloque "
            "rectangular equivalente Whitney con beta1), secciones controladas por traccion/"
            "compresion, refuerzo minimo As,min, resistencia axial de diseno phi*Pn,max con "
            "ecuaciones C.10-1/C.10-2, vigas de gran altura. CORRIGE la numeracion de los "
            "chunks obsoletos C-SEC8-* que llamaban a este contenido \"C.8\" (C.8 real es "
            "Analisis y diseno - consideraciones generales, no flexion)."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.10 - Flexion y cargas axiales (C.10.1 a C.10.7).\n\n"
            "C.10.1 Alcance: las disposiciones del Capitulo C.10 se aplican al diseno de "
            "elementos sometidos a flexion o cargas axiales, o a la combinacion de ambas.\n\n"
            "C.10.2 Suposiciones de diseno: las deformaciones unitarias en el refuerzo y en "
            "el concreto se suponen directamente proporcionales a la distancia desde el eje "
            "neutro (C.10.2.2). La maxima deformacion unitaria utilizable en la fibra extrema "
            "en compresion del concreto se supone igual a 0.003 (C.10.2.3). El esfuerzo en el "
            "refuerzo cuando es menor que fy se toma como Es veces la deformacion unitaria del "
            "acero; para deformaciones mayores, el esfuerzo se considera igual a fy (C.10.2.4). "
            "La resistencia a la traccion del concreto no se considera en flexion/carga axial "
            "excepto en C.18.4 (C.10.2.5). C.10.2.7 define el bloque rectangular equivalente de "
            "esfuerzos: esfuerzo en el concreto de 0.85f'c uniformemente distribuido en una zona "
            "de compresion limitada por una linea paralela al eje neutro a distancia a = beta1*c "
            "de la fibra de deformacion maxima. Para f'c entre 17 y 28 MPa, beta1 = 0.85; para "
            "f'c mayor a 28 MPa, beta1 disminuye 0.05 por cada 7 MPa de exceso sobre 28 MPa, sin "
            "bajar de 0.65 (C.10.2.7.3).\n\n"
            "C.10.3 Principios y requisitos generales: la condicion de deformacion balanceada "
            "existe cuando el refuerzo en traccion alcanza fy al mismo tiempo que el concreto "
            "alcanza 0.003 (C.10.3.2). Secciones controladas por compresion: deformacion "
            "unitaria neta de traccion (epsilon_t) igual o menor al limite de deformacion "
            "controlada por compresion (0.002 para refuerzo Grado 420) cuando el concreto llega "
            "a 0.003 (C.10.3.3). Secciones controladas por traccion: epsilon_t >= 0.005 "
            "(C.10.3.4). Entre ambos limites hay una zona de transicion. Para elementos no "
            "preesforzados en flexion y con carga axial mayorada de compresion menor a "
            "0.10*f'c*Ag, epsilon_t en resistencia nominal no debe ser menor a 0.004 (C.10.3.5). "
            "La resistencia axial de diseno phi*Pn no debe superar phi*Pn,max:\n"
            "  - Elementos con refuerzo en espiral (C.7.10.4) o compuestos (C.10.13): "
            "phi*Pn(max) = 0.80*phi*[0.85*f'c*(Ag-Ast) + fy*Ast]  (C.10-1)\n"
            "  - Elementos con estribos (C.7.10.5): "
            "phi*Pn(max) = 0.75*phi*[0.85*f'c*(Ag-Ast) + fy*Ast]  (C.10-2)\n"
            "El momento maximo mayorado Mu debe incrementarse por los efectos de esbeltez "
            "segun C.10.10 (C.10.3.7).\n\n"
            "C.10.4 Distancia entre apoyos laterales de elementos a flexion: la separacion "
            "entre apoyos laterales de una viga no debe exceder 50 veces el menor ancho b del "
            "ala o cara de compresion (C.10.4.1).\n\n"
            "C.10.5 Refuerzo minimo en flexion: As,min = (0.25*raiz(f'c)/fy)*bw*d, pero no menor "
            "a 1.4*bw*d/fy (ecuacion C.10-3). Para elementos estaticamente determinados con el "
            "ala en traccion, se reemplaza bw por 2*bw o el ancho del ala, el menor (C.10.5.2). "
            "No se exige si el As proporcionado excede en un tercio al requerido por analisis "
            "(C.10.5.3). Para losas estructurales y zapatas de espesor uniforme aplica C.7.12.2.1 "
            "con espaciamiento maximo de 3 veces el espesor o 450 mm (C.10.5.4).\n\n"
            "C.10.6 Distribucion del refuerzo de flexion: el espaciamiento s del refuerzo mas "
            "cercano a la superficie en traccion no debe exceder s = 380*(280/fs) - 2.5*cc, ni "
            "300*(280/fs) (ecuacion C.10-4), donde cc es el recubrimiento libre y fs se puede "
            "tomar como 2/3 de fy. Para vigas o viguetas con h > 900 mm se exige refuerzo "
            "superficial longitudinal en las caras laterales dentro de h/2 cerca de la cara de "
            "traccion (C.10.6.7).\n\n"
            "C.10.7 Vigas de gran altura: son elementos con luz libre ln <= 4 veces la altura "
            "total, o con cargas concentradas a menos de 2 veces la altura desde el apoyo "
            "(C.10.7.1). Deben disenarse considerando distribucion no lineal de deformaciones "
            "unitarias o el Apendice C-A (modelo puntal-tensor); Vn debe cumplir C.11.7."
        ),
    },
    {
        "id": "NSR10-C-C_10b",
        "seccion": "C.10.8 a C.10.14",
        "titulo": (
            "Columnas: limites de refuerzo longitudinal (1% a 4% Ag), cuantia minima de "
            "espiral, efectos de esbeltez (klu/r <= 22 no arriostradas, <= 34-12*M1/M2 "
            "arriostradas), procedimiento de magnificacion de momentos (delta*M2), "
            "transmision de cargas de columna a traves de losa de entrepiso, elementos "
            "compuestos, resistencia al aplastamiento."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.10 - Flexion y cargas axiales (C.10.8 a C.10.14, "
            "columnas y elementos a compresion).\n\n"
            "C.10.9 Limites del refuerzo de columnas: el area de refuerzo longitudinal Ast no "
            "debe ser menor que 0.01*Ag ni mayor que 0.04*Ag (C.10.9.1); estructuras DMO/DES "
            "(Capitulo C.21) restringen aun mas el area maxima. Numero minimo de barras "
            "longitudinales: 4 en estribos rectangulares/circulares, 3 en estribos triangulares, "
            "6 en elementos con espiral (C.10.9.2). Cuantia volumetrica minima de espiral: "
            "rho_s = 0.45*(Ag/Ach - 1)*(f'c/fyt), con fyt <= 700 MPa (ecuacion C.10-5).\n\n"
            "C.10.10 Efectos de esbeltez en elementos a compresion: se permiten ignorar cuando "
            "k*lu/r <= 22 en columnas no arriostradas contra desplazamiento lateral (C.10-6), o "
            "k*lu/r <= 34 - 12*(M1/M2) <= 40 en columnas arriostradas (C.10-7), donde M1/M2 es "
            "positivo en curvatura simple y negativo en curvatura doble. Un piso se considera "
            "arriostrado si Q = (suma Pu * delta_o)/(Vus * lc) <= 0.05 (ecuacion C.10-10). "
            "Cuando no se pueden ignorar, el diseno se basa en analisis de segundo orden "
            "(no lineal, elastico, o procedimiento de magnificacion de momentos).\n\n"
            "Procedimiento de magnificacion de momentos (estructuras SIN desplazamiento "
            "lateral, C.10.10.6): Mc = delta*M2 (C.10-11), donde delta = Cm / (1 - Pu/(0.75*Pc)) "
            ">= 1.0 (C.10-12), y Pc = pi^2*EI / (k*lu)^2 (C.10-13). El momento M2 no debe ser "
            "menor que M2,min = Pu*(15 + 0.03*h) en mm (C.10-17). Para elementos sin cargas "
            "transversales entre apoyos, Cm = 0.6 + 0.4*(M1/M2) (C.10-16), o 1.0 con cargas "
            "transversales.\n\n"
            "Procedimiento de magnificacion de momentos (estructuras CON desplazamiento "
            "lateral, C.10.10.7): M1 = M1ns + delta_s*M1s, M2 = M2ns + delta_s*M2s "
            "(C.10-18/19), con delta_s = 1/(1-Q) >= 1 (C.10-20); si delta_s excede 1.5 debe "
            "usarse analisis elastico de segundo orden o la formula alternativa C.10-21 basada "
            "en la sumatoria de cargas verticales del piso.\n\n"
            "C.10.12 Transmision de cargas de columnas a traves de losas de entrepiso: si el "
            "f'c de la columna supera 1.4 veces el de la losa (columnas interiores/de borde) o "
            "1.2 veces (columnas esquineras), debe usarse una resistencia efectiva (f'c)e "
            "calculada con las ecuaciones C.10-22 a C.10-24, o colocar concreto de resistencia "
            "de columna en la zona de la columna extendido 600 mm dentro de la losa "
            "(C.10.12.2).\n\n"
            "C.10.13 Elementos compuestos sometidos a compresion: incluyen elementos reforzados "
            "longitudinalmente con perfiles de acero estructural, tuberias o tubos. El radio de "
            "giro para efectos de esbeltez se calcula con la ecuacion C.10-25. El nucleo de "
            "concreto confinado por acero estructural, el refuerzo en espiral alrededor de un "
            "nucleo de acero, y los estribos alrededor de un nucleo de acero tienen requisitos "
            "detallados en C.10.13.6 a C.10.13.8 (espesor minimo de confinamiento, fy del nucleo "
            "de acero no mayor a 350 MPa, cuantias de barras longitudinales entre 0.01 y 0.08 "
            "del area neta).\n\n"
            "C.10.14 Resistencia al aplastamiento: la resistencia de diseno al aplastamiento "
            "del concreto no debe exceder phi*(0.85*f'c*A1), salvo que la superficie de soporte "
            "sea mas ancha que el area cargada, en cuyo caso se multiplica por raiz(A2/A1), pero "
            "no mas de 2 (C.10.14.1). No aplica a anclajes de postensado (C.10.14.2)."
        ),
    },
    {
        "id": "NSR10-C-C_11a",
        "seccion": "C.11.1 a C.11.4",
        "titulo": (
            "Resistencia al cortante Vn = Vc + Vs; formulas de Vc para elementos no "
            "preesforzados (metodo simplificado y detallado), tipos de refuerzo a cortante, "
            "espaciamiento maximo, refuerzo minimo Av,min, diseno del refuerzo a cortante "
            "(estribos perpendiculares e inclinados). CORRIGE la numeracion de los chunks "
            "obsoletos C-SEC9-* que llamaban a este contenido \"C.9\" (C.9 real es Requisitos "
            "de resistencia y funcionamiento, combinaciones de carga, no cortante)."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.11 - Cortante y torsion (C.11.1 a C.11.4, resistencia "
            "al cortante).\n\n"
            "C.11.1.1 Diseno por resistencia al cortante: phi*Vn >= Vu (ecuacion C.11-1), donde "
            "Vn = Vc + Vs (ecuacion C.11-2). Vc es la resistencia nominal aportada por el "
            "concreto, Vs la aportada por el refuerzo de cortante. Los valores de f'c usados en "
            "este capitulo no deben exceder 8.3 MPa salvo excepciones de C.11.1.2.1.\n\n"
            "C.11.2 Resistencia al cortante del concreto en elementos NO preesforzados:\n"
            "  - Metodo simplificado, solo cortante y flexion: "
            "Vc = 0.17*lambda*raiz(f'c)*bw*d  (C.11-3)\n"
            "  - Elementos con compresion axial: "
            "Vc = 0.17*(1 + Nu/(14*Ag))*lambda*raiz(f'c)*bw*d  (C.11-4), con Nu/Ag en MPa\n"
            "  - Elementos con traccion axial significativa: Vc = 0 salvo calculo detallado\n"
            "  - Metodo detallado (C.11.2.2.1): "
            "Vc = (0.16*lambda*raiz(f'c) + 17*rho_w*Vu*d/Mu)*bw*d  (C.11-5), sin exceder "
            "0.29*lambda*raiz(f'c)*bw*d, con Vu*d/Mu limitado a 1.0\n\n"
            "C.11.4 Resistencia al cortante aportada por el refuerzo:\n"
            "Tipos de refuerzo permitidos (C.11.4.1): estribos perpendiculares al eje, refuerzo "
            "electrosoldado perpendicular, espirales/estribos circulares/estribos cerrados de "
            "confinamiento; en elementos no preesforzados tambien estribos inclinados >=45 grados "
            "o refuerzo longitudinal doblado >=30 grados. fy y fyt del refuerzo a cortante no "
            "deben exceder 420 MPa (550 MPa para electrosoldado corrugado).\n\n"
            "Limites de espaciamiento (C.11.4.5): el refuerzo perpendicular al eje no debe "
            "exceder d/2 en elementos no preesforzados, 0.75h en preesforzados, ni 600 mm. Si "
            "Vs supera 0.33*raiz(f'c)*bw*d, estos limites se reducen a la mitad.\n\n"
            "Refuerzo minimo a cortante (C.11.4.6): obligatorio donde Vu exceda 0.5*phi*Vc, con "
            "excepciones (zapatas y losas solidas, ciertos elementos alveolares, losas nervadas "
            "con viguetas, vigas con h <= 250 mm, vigas integrales con losa h <= 600 mm, vigas "
            "de concreto reforzado con fibra de acero). Av,min = 0.062*raiz(f'c)*bw*s/fyt, pero "
            "no menor que 0.35*bw*s/fyt (ecuacion C.11-13).\n\n"
            "Diseno del refuerzo a cortante (C.11.4.7): con estribos perpendiculares, "
            "Vs = Av*fyt*d/s  (C.11-15). Con estribos inclinados a angulo alpha respecto al eje "
            "longitudinal, Vs = Av*fyt*(sen(alpha)+cos(alpha))*d/s  (C.11-16). Con barra doblada "
            "individual, Vs = Av*fy*sen(alpha)  (C.11-17), sin exceder 0.25*raiz(f'c)*bw*d. Vs no "
            "debe considerarse mayor que 0.66*raiz(f'c)*bw*d (C.11.4.7.9)."
        ),
    },
    {
        "id": "NSR10-C-C_11b",
        "seccion": "C.11.5 a C.11.6",
        "titulo": (
            "Diseno para torsion: umbral de torsion (se puede despreciar Tu por debajo de un "
            "limite), resistencia al momento torsional phi*Tn >= Tu, refuerzo minimo para "
            "torsion, detalles de anclaje. Cortante por friccion (Vn = Avf*fy*mu) con "
            "coeficientes de friccion segun tipo de interfaz."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.11 - Cortante y torsion (C.11.5 a C.11.6, torsion y "
            "cortante por friccion).\n\n"
            "C.11.5.1 Umbral de torsion: se permite despreciar los efectos de la torsion si el "
            "momento torsional mayorado Tu es menor que phi*0.083*lambda*raiz(f'c)*(Acp^2/pcp) "
            "en elementos no preesforzados, con formulas ajustadas para preesforzados y para "
            "elementos con traccion/compresion axial. En elementos monoliticos con losa, el "
            "ancho de ala sobresaliente usado para Acp y pcp debe cumplir C.13.2.4.\n\n"
            "C.11.5.3 Resistencia al momento torsional: donde Tu excede el umbral, el diseno se "
            "basa en phi*Tn >= Tu (ecuacion C.11-20). Tn se calcula como "
            "Tn = 2*Ao*At*fyt*cot(theta)/s  (ecuacion C.11-21), donde Ao se puede tomar como "
            "0.85*Aoh; theta no debe ser menor a 30 grados ni mayor a 60 grados (45 grados para "
            "elementos no preesforzados o con preesforzado bajo; 37.5 grados para preesforzados "
            "con fuerza efectiva >= 40% de la resistencia a traccion del refuerzo longitudinal). "
            "El area adicional de refuerzo longitudinal para torsion, Al, se calcula con la "
            "ecuacion C.11-22 usando el mismo theta.\n\n"
            "Las dimensiones de la seccion transversal deben satisfacer, en secciones solidas, "
            "la ecuacion C.11-18: raiz[(Vu/(bw*d))^2 + (Tu*ph/(1.7*Aoh^2))^2] <= "
            "phi*(Vc/(bw*d) + 0.66*raiz(f'c)); en secciones huecas aplica la ecuacion C.11-19 "
            "sin la raiz cuadrada (suma directa de terminos).\n\n"
            "C.11.5.4 Detalles del refuerzo para torsion: consiste en barras longitudinales o "
            "tendones mas estribos cerrados perpendiculares al eje (o refuerzo electrosoldado "
            "equivalente, o espiral en vigas no preesforzadas). El refuerzo transversal debe "
            "anclarse con gancho estandar de 135 grados o gancho sismico alrededor de una barra "
            "longitudinal.\n\n"
            "C.11.5.5 Refuerzo minimo para torsion: area minima de estribos cerrados "
            "(Av + 2*At) = 0.062*raiz(f'c)*bw*s/fyt, no menor que 0.35*bw*s/fyt (ecuacion "
            "C.11-23). Area minima total de refuerzo longitudinal Al,min segun ecuacion "
            "C.11-24.\n\n"
            "C.11.5.6 Espaciamiento del refuerzo para torsion: el refuerzo transversal no debe "
            "exceder el menor entre ph/8 y 300 mm. El refuerzo longitudinal debe distribuirse a "
            "lo largo del perimetro del estribo cerrado con espaciamiento maximo 300 mm, con al "
            "menos una barra en cada esquina.\n\n"
            "C.11.6 Cortante por friccion: se aplica cuando es relevante la transmision de "
            "cortante a traves de un plano (fisura existente o potencial, superficie entre "
            "materiales distintos, o entre concretos colocados en momentos diferentes). Con "
            "refuerzo perpendicular al plano de cortante: Vn = Avf*fy*mu (ecuacion C.11-25). "
            "Con refuerzo inclinado a angulo alpha: Vn = Avf*fy*(mu*sen(alpha)+cos(alpha)) "
            "(ecuacion C.11-26). Coeficiente de friccion mu (C.11.6.4.3): 1.4*lambda para "
            "concreto colocado monoliticamente; 1.0*lambda para concreto sobre concreto "
            "endurecido con superficie intencionalmente rugosa; 0.6*lambda para concreto sobre "
            "concreto endurecido no rugoso; 0.7*lambda para concreto anclado a acero estructural "
            "mediante pernos con cabeza o barras de refuerzo soldadas. lambda = 1.0 para "
            "concreto normal, 0.75 para concreto liviano."
        ),
    },
    {
        "id": "NSR10-C-C_11c",
        "seccion": "C.11.7 a C.11.11",
        "titulo": (
            "Vigas altas (Vn <= 0.83*raiz(f'c)*bw*d), disposiciones especiales para menSulas y "
            "cartelas (av/d < 2), disposiciones para muros (cortante en el plano, Vc segun "
            "ecuaciones C.11-27/28), transmision de momentos a columnas, punzonamiento en "
            "losas y zapatas (comportamiento en dos direcciones, Vc segun beta y alpha_s)."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.11 - Cortante y torsion (C.11.7 a C.11.11, "
            "disposiciones especiales).\n\n"
            "C.11.7 Vigas altas: aplica a elementos con ln <= 4 veces la altura total, o con "
            "cargas concentradas a menos de 2 veces la altura del apoyo (misma definicion que "
            "C.10.7.1). Vn no debe exceder 0.83*raiz(f'c)*bw*d (C.11.7.3). El area de refuerzo "
            "a cortante perpendicular al refuerzo de flexion, Av, no debe ser menor que "
            "0.0025*bw*s (s <= d/5 o 300 mm); el area paralela, Avh, no menor que 0.0015*bw*s2 "
            "(s2 <= d/5 o 300 mm).\n\n"
            "C.11.8 Mensulas y cartelas: aplica cuando la relacion luz de cortante a altura "
            "av/d < 2. Para av/d <= 1 y fuerza de traccion horizontal Nuc <= Vu se puede usar "
            "el metodo simplificado (phi = 0.75 en todos los calculos). La altura en el borde "
            "exterior del area de apoyo no debe ser menor que 0.5*d. El refuerzo principal de "
            "traccion Asc no debe ser menor que el mayor entre (Af + An) y (2*Avf/3 + An); "
            "Asc/(b*d) no debe ser menor que 0.04*(f'c/fy) (C.11.8.5).\n\n"
            "C.11.9 Disposiciones especiales para muros: el diseno de cortante horizontal en el "
            "plano del muro se basa en Vn = Vc + Vs, con Vn <= 0.83*raiz(f'c)*h*d (C.11.9.3), "
            "donde d = 0.8*lw salvo analisis de compatibilidad de deformaciones mas detallado. "
            "Vc puede tomarse como el menor de: "
            "Vc = 0.27*raiz(f'c)*h*d + Nu*d/(4*lw)  (C.11-27), o "
            "Vc = [0.05*raiz(f'c) + lw*(0.1*raiz(f'c)+0.2*Nu/(lw*h))/(Mu/Vu - lw/2)]*h*d "
            "(C.11-28). La cuantia de refuerzo horizontal para cortante rho_t no debe ser menor "
            "que 0.0025, con espaciamiento maximo el menor entre lw/5, 3h, o 450 mm (C.11.9.9.2/"
            "9.9.3). La cuantia de refuerzo vertical rho_l se calcula con la ecuacion C.11-30 en "
            "funcion de la relacion hw/lw.\n\n"
            "C.11.10 Transmision de momentos a columnas: cuando cargas gravitacionales, viento "
            "o sismo producen transmision de momento en conexiones de elementos a columnas, el "
            "cortante derivado debe considerarse en el diseno del refuerzo transversal de la "
            "columna, con refuerzo transversal minimo segun la ecuacion C.11-13 dentro de la "
            "columna.\n\n"
            "C.11.11 Disposiciones para losas y zapatas (punzonamiento): la resistencia a "
            "cortante en la cercania de columnas/cargas concentradas se rige por la mas severa "
            "entre comportamiento como viga (secciones criticas que cruzan el ancho total, "
            "C.11.1 a C.11.4) y comportamiento en dos direcciones (punzonamiento, seccion "
            "critica a d/2 del borde de la columna). Para losas no preesforzadas y zapatas, Vc "
            "es el menor entre:\n"
            "  (a) Vc = 0.17*(1 + 2/beta)*lambda*raiz(f'c)*bo*d  (C.11-31), beta = relacion "
            "lado largo/lado corto de la columna\n"
            "  (b) Vc = 0.083*(alpha_s*d/bo + 2)*lambda*raiz(f'c)*bo*d  (C.11-32), alpha_s = 40 "
            "columnas interiores, 30 de borde, 20 en esquina\n"
            "  (c) Vc = 0.33*lambda*raiz(f'c)*bo*d  (C.11-33)\n"
            "donde bo es el perimetro de la seccion critica. Vn no debe considerarse mayor que "
            "0.5*raiz(f'c)*bo*d cuando se usa refuerzo de cortante en losas (C.11.11.3.2)."
        ),
    },
    {
        "id": "NSR10-C-C_12a",
        "seccion": "C.12.1 a C.12.9",
        "titulo": (
            "Desarrollo del refuerzo: longitud de desarrollo a traccion ld (formula simplificada "
            "y detallada con factores psi_t, psi_e, psi_s, lambda), longitud a compresion ldc, "
            "ganchos estandar ldh, barras corrugadas con cabeza, torones de preesforzado. "
            "CORRIGE la numeracion de los chunks obsoletos C-SEC10-* que llamaban a este "
            "contenido \"C.10\" (C.10 real es Flexion y cargas axiales, no desarrollo)."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.12 - Longitudes de desarrollo y empalmes del refuerzo "
            "(C.12.1 a C.12.9).\n\n"
            "C.12.1 Generalidades: la traccion o compresion calculada en el refuerzo debe "
            "desarrollarse hacia cada lado de la seccion mediante longitud embebida, gancho, "
            "barra corrugada con cabeza, dispositivo mecanico, o combinacion. Los ganchos y "
            "barras con cabeza NO se emplean para desarrollar barras en compresion (C.12.1.1). "
            "f'c usado en este capitulo no debe exceder 8.3 MPa (C.12.1.2).\n\n"
            "C.12.2 Desarrollo de barras corrugadas a TRACCION: ld no debe ser menor que 300 mm. "
            "Formula simplificada (C.12.2.2), para barras No.6/20M o menores con espaciamiento y "
            "recubrimiento normales: ld = (fy*psi_t*psi_e)/(2.1*lambda*raiz(f'c)) * db. Formula "
            "detallada (C.12.2.3, ecuacion C.12-1): "
            "ld = [fy*psi_t*psi_e*psi_s*lambda / (1.1*raiz(f'c)*((cb+Ktr*db)/db))] * db "
            "donde (cb+Ktr*db)/db no debe tomarse mayor a 2.5. Ktr = 40*Atr/(s*n) (ecuacion "
            "C.12-2), se puede usar Ktr=0 como simplificacion.\n"
            "Factores de modificacion (C.12.2.4): psi_t = 1.3 si hay mas de 300 mm de concreto "
            "fresco debajo del refuerzo horizontal, si no 1.0. psi_e (recubrimiento epoxico) = "
            "1.5 con recubrimiento < 3db o separacion < 6db, 1.2 en otros casos con epoxico, 1.0 "
            "sin epoxico (psi_t*psi_e no necesita exceder 1.7). psi_s = 0.8 para barras "
            "No.6/20M o menores, 1.0 para No.7/22M o mayores. lambda = 0.75 en concreto liviano "
            "sin especificar fct, 1.0 en concreto normal.\n\n"
            "C.12.3 Desarrollo de barras corrugadas a COMPRESION: ldc no debe ser menor de "
            "200 mm. Se toma como el mayor entre (0.24*fy/(lambda*raiz(f'c)))*db y "
            "(0.043*fy)*db (C.12.3.2). Se puede multiplicar por (As requerido)/(As "
            "proporcionado), o por 0.75 si el refuerzo esta confinado por espiral (diametro "
            ">=6mm, paso <=100mm) o estribos No.13 espaciados <=100mm.\n\n"
            "C.12.4 Desarrollo de paquetes de barras: la longitud de desarrollo de cada barra "
            "individual dentro de un paquete se aumenta 20% para paquetes de 3 barras y 33% "
            "para paquetes de 4 barras.\n\n"
            "C.12.5 Ganchos estandar en TRACCION: ldh no debe ser menor que el mayor entre 8*db "
            "y 150 mm. ldh = (0.24*psi_e*fy)/(lambda*raiz(f'c)) * db (C.12.5.2), con psi_e=0.75 "
            "para concreto liviano, 1.0 en otros casos. Se puede multiplicar por 0.7 (ganchos "
            "No.36 o menores con recubrimiento lateral >=65mm y extension >=50mm en ganchos de "
            "90 grados), o por 0.8 si estan confinados con estribos perpendiculares espaciados "
            "<=3db.\n\n"
            "C.12.6 Barras corrugadas con cabeza en traccion: ldt = (0.19*psi_e*fy)/raiz(f'c) * "
            "db, con f'c limitado a 40 MPa para este calculo; requiere fy <= 420 MPa, barra "
            "<= No.11/36M, concreto de peso normal, area de apoyo de cabeza Abrg >= 4*Ab, "
            "recubrimiento libre >= 2*db, espaciamiento libre >= 4*db.\n\n"
            "C.12.9 Desarrollo de torones de preesforzado: los torones de siete alambres deben "
            "adherirse mas alla de la seccion critica en ld = (fse/21)*db + ((fps-fse)/7)*db "
            "(ecuacion C.12-4), donde fse es el esfuerzo efectivo de preesforzado y fps el "
            "esfuerzo de diseno del toron."
        ),
    },
    {
        "id": "NSR10-C-C_12b",
        "seccion": "C.12.10 a C.12.19",
        "titulo": (
            "Desarrollo del refuerzo para momento positivo y negativo, desarrollo del refuerzo "
            "del alma (anclaje de estribos), empalmes por traslapo generalidades (clases A y "
            "B), empalmes a traccion y compresion, requisitos especiales de empalmes en "
            "columnas, empalmes de refuerzo electrosoldado."
        ),
        "texto": (
            "NSR-10 Titulo C, Capitulo C.12 - Longitudes de desarrollo y empalmes del refuerzo "
            "(C.12.10 a C.12.19).\n\n"
            "C.12.10 Desarrollo del refuerzo de flexion, generalidades: el refuerzo debe "
            "extenderse mas alla del punto donde ya no es necesario para resistir flexion una "
            "distancia igual a d o 12*db, la mayor (C.12.10.3, excepto apoyos de vigas "
            "simplemente apoyadas y extremos libres de voladizos). El refuerzo por flexion NO "
            "debe terminarse en zona de traccion salvo que se cumpla una de tres condiciones "
            "(C.12.10.5.1 a .3): que Vu en el punto terminal no exceda (2/3)*phi*Vn, que se "
            "provea exceso de estribos en una distancia de 3d/4, o (para barras No.36 y menores) "
            "que el refuerzo continuo tenga el doble del area requerida y Vu no exceda "
            "(3/4)*phi*Vn.\n\n"
            "C.12.11 Desarrollo del refuerzo para MOMENTO POSITIVO: al menos 1/3 del refuerzo "
            "positivo en elementos simplemente apoyados (1/4 en continuos) debe prolongarse "
            "hasta el apoyo, con al menos 150 mm dentro del apoyo en vigas (C.12.11.1). En "
            "apoyos simples y puntos de inflexion, el diametro del refuerzo esta limitado por "
            "ld <= Mn/Vu + la, donde la es la longitud embebida mas alla del centro del apoyo "
            "(ecuacion C.12-5); este limite puede aumentarse 30% si los extremos estan "
            "confinados por una reaccion de compresion.\n\n"
            "C.12.12 Desarrollo del refuerzo para MOMENTO NEGATIVO: debe anclarse en o a traves "
            "de los elementos de apoyo. Al menos 1/3 del refuerzo total en el apoyo debe tener "
            "longitud embebida mas alla del punto de inflexion no menor que d, 12*db, o ln/16, "
            "la mayor (C.12.12.3).\n\n"
            "C.12.13 Desarrollo del refuerzo del alma (anclaje de estribos): para barras No.16/"
            "MD200 y menores, y No.6/20M, No.7/22M, No.8/25M con fyt <= 280 MPa, gancho estandar "
            "alrededor del refuerzo longitudinal (C.12.13.2.1). Para fyt > 280 MPa se exige "
            "gancho de estribo mas longitud embebida adicional (C.12.13.2.2).\n\n"
            "C.12.14 Empalmes, generalidades: solo se permiten cuando lo requieran o permitan "
            "los planos, especificaciones, o el profesional facultado (C.12.14.1). Barras "
            "mayores de No.36 no admiten empalme por traslapo salvo excepciones (C.12.14.2.1). "
            "Un empalme mecanico o soldado completo debe desarrollar al menos 1.25*fy de la "
            "barra (C.12.14.3.2/.4).\n\n"
            "C.12.15 Empalmes de barras corrugadas a TRACCION: longitud minima segun clase — "
            "Clase A = 1.0*ld, Clase B = 1.3*ld, no menor que 300 mm. Deben ser Clase B salvo "
            "que el area proporcionada sea al menos el doble de la requerida Y no mas de la "
            "mitad del refuerzo total este empalmado dentro de la longitud de empalme "
            "(condiciones para admitir Clase A, C.12.15.2).\n\n"
            "C.12.16 Empalmes de barras corrugadas a COMPRESION: longitud = 0.071*fy*db para "
            "fy <= 420 MPa, o (0.13*fy - 24)*db para fy > 420 MPa, no menor a 300 mm; se "
            "incrementa 1/3 si f'c < 21 MPa (C.12.16.1).\n\n"
            "C.12.17 Requisitos especiales de empalmes en COLUMNAS: si el esfuerzo es de "
            "compresion, aplican las reglas de empalme a compresion (C.12.17.2.1). Si es de "
            "traccion y no excede 0.5*fy, empalmes Clase B (o Clase A si la mitad o menos de "
            "las barras se empalman en la seccion y estan escalonados una distancia ld). Si "
            "excede 0.5*fy en traccion, siempre Clase B (C.12.17.2.2/.3). Con estribos "
            "confinantes de area efectiva >= 0.0015*h*s en ambas direcciones, la longitud de "
            "empalme se puede multiplicar por 0.83 (no menos de 300 mm); con espiral, por 0.75 "
            "(C.12.17.2.4/.5).\n\n"
            "C.12.18/C.12.19 Empalmes de refuerzo electrosoldado: para alambre corrugado, la "
            "longitud minima de traslapo es el mayor entre 1.3*ld y 200 mm, con ld calculado "
            "segun C.12.7 para desarrollar fy. Para alambre liso, depende de si el As "
            "suministrado es menor o al menos el doble del requerido por analisis en la zona "
            "del empalme (C.12.19.1/.2)."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local (paraphrase-multilingual-MiniLM-L12-v2)...")
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
    print(f"OK: {len(rows)} chunks C.10/C.11/C.12 cargados con embedding.")


if __name__ == "__main__":
    main()
