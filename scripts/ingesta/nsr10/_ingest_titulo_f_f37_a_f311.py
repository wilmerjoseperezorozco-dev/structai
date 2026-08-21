"""
NSR-10 Titulo F, F.3.7 a F.3.11 -- cierra el capitulo F.3 (Provisiones
sismicas para acero) en su totalidad: sistemas COMPUESTOS acero-concreto
(F.3.7 PRMC, F.3.8 arriostrados/muros compuestos) y las provisiones
administrativas/de calidad (F.3.9 fabricacion, F.3.10 control de calidad,
F.3.11 ensayos de calificacion de conexiones).

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
extraido en bruto localmente en F_901_980_raw.txt (paginas internas F-269 a
F-298, fin del capitulo F.3). 6 chunks single-topic.

Uso: python _ingest_titulo_f_f37_a_f311.py
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
        "id": "NSR10-F-F_3_7_PRMC",
        "seccion": "F.3.7 (Pórticos Resistentes a Momentos Compuestos)",
        "titulo": (
            "Porticos Resistentes a Momentos Compuestos acero-concreto (PRMC): "
            "4 niveles DMI/DMO/DES/PR (parcialmente restringido). Columnas "
            "compuestas o de concreto reforzado + vigas de acero/embebidas/"
            "compuestas. Angulos de deriva de conexion 0.02 rad (DMO/PR) o "
            "0.04 rad (DES), formula de resistencia a cortante requerida "
            "Emh=2(1.1Ry*Mp,esp)/Lh igual a la de PRM de acero puro (F.3.5) "
            "pero con Mp,esp calculado por compatibilidad de deformaciones."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "F.3.7 — Pórticos Resistentes a Momentos Compuestos (PRMC): "
            "columnas compuestas (embebidas/rellenas) o de concreto reforzado, "
            "vigas de acero, embebidas en concreto, o compuestas. 4 niveles.\n\n"
            "F.3.7.1 PRMC-DMI (capacidad mínima): sin requisitos especiales de "
            "análisis/sistema. Miembros: sin requisitos adicionales a F.2 para "
            "acero/compuestos; columnas de concreto reforzado cumplen Título C "
            "excluyendo C.21 (sin detallado sísmico especial). Conexiones "
            "totalmente restringidas (TR).\n\n"
            "F.3.7.2 PRMC-DMO (capacidad moderada): deformación inelástica "
            "limitada por fluencia a flexión de vigas y fluencia a cortante en "
            "zona de panel de columnas — requiere ENSAYOS de calificación de la "
            "conexión (no solo cálculo). Miembros con ductilidad moderada "
            "(F.3.4.1.1). Conexión viga-columna debe acomodar 0.02 rad de "
            "deriva mínimo, con resistencia medida >=0.8*Mp de la viga a esa "
            "deriva. Resistencia a cortante requerida (ecuación F.3.7.2-1):\n"
            "  Emh = 2*(1.1*Ry*Mp,esp)/Lh\n"
            "donde Mp,esp = resistencia a flexión plástica esperada (para vigas "
            "embebidas/compuestas, por distribución plástica de esfuerzos o "
            "compatibilidad de deformaciones; para vigas de acero puro, "
            "simplemente Ry*Mp), Lh = distancia entre rótulas plásticas.\n\n"
            "F.3.7.3 PRMC-DES (capacidad especial, el más exigente): "
            "deformación inelástica SIGNIFICATIVA por fluencia en vigas + "
            "fluencia limitada a cortante en zona de panel — columnas "
            "generalmente más resistentes que vigas totalmente plastificadas "
            "(diseño por capacidad, columna-fuerte/viga-débil, igual principio "
            "que PRM de acero puro), se permite plastificación por flexión SOLO "
            "en la base de columnas. Relación de momentos ΣM*pcc/ΣM*p,esp > 1 "
            "(ecuación F.3.7.3-1) — análoga a la relación 1.2ΣMpc/ΣMpb del PRM "
            "puro de acero. Miembros con ductilidad ALTA. Conexión debe "
            "acomodar 0.04 rad mínimo (el doble que DMO), validada por ENSAYOS "
            "CÍCLICOS: mínimo 2 ensayos de calificación cuando las vigas se "
            "interrumpen en la conexión.\n\n"
            "F.3.7.4 PRMC-PR (parcialmente restringido): columnas de acero + "
            "vigas compuestas totalmente compuestas (no embebidas), conexiones "
            "PR (no TR) — el análisis debe considerar explícitamente la "
            "flexibilidad de la conexión y la acción compuesta en rigidez/"
            "deriva. La conexión debe acomodar 0.02 rad, con resistencia "
            "medida creciendo monotónicamente hasta al menos 0.5*Mp de la viga "
            "(la mitad de exigencia que DMO/DES — refleja que la conexión PR "
            "es deliberadamente más flexible por diseño).\n\n"
            "Común a los 4 niveles: empalmes de columna deben desarrollar "
            "resistencia a flexión y cortante ΣMpc/Hc (mismo principio de "
            "diseño por capacidad usado en todos los sistemas sísmicos de "
            "acero de F.3). Placas de continuidad/diafragma en columnas "
            "rellenas: espesor >= espesor de aleta de viga, soldadas en todo "
            "el perímetro con penetración completa o filete por ambos lados."
        ),
    },
    {
        "id": "NSR10-F-F_3_8_arriostrados_compuestos",
        "seccion": "F.3.8.1 a F.3.8.3 (Pórticos arriostrados/excéntricos compuestos)",
        "titulo": (
            "Porticos arriostrados compuestos acero-concreto: PACC-DMI/DES "
            "(concentricamente arriostrados, columnas embebidas/rellenas/"
            "concreto, riostras de acero o rellenas de concreto) y PAEC "
            "(excentricamente arriostrados, con vinculo obligatoriamente de "
            "acero). Remiten en gran parte a los requisitos ya establecidos "
            "para PAC/PAE de acero puro (F.3.6), con ajustes de esbeltez para "
            "riostras rellenas."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3. F.3.8.1 a F.3.8.3 — Pórticos "
            "arriostrados compuestos acero-concreto.\n\n"
            "F.3.8.1 PACC-DMI: columnas de acero, embebidas, rellenas o de "
            "concreto reforzado; vigas de acero o compuestas; riostras de "
            "acero o compuestas rellenas de concreto. Deben satisfacer los "
            "requisitos de PAC-DMI de acero puro (F.3.6.1), sin requisitos "
            "especiales adicionales de análisis, sistema o miembros — "
            "columnas de concreto reforzado cumplen C.21.\n\n"
            "F.3.8.2 PACC-DES: columnas SOLO embebidas o rellenas (no permite "
            "concreto reforzado puro, a diferencia de DMI); deformación "
            "inelástica significativa por pandeo de riostra + fluencia a "
            "tensión, igual mecanismo que PAC-DES de acero (F.3.6.2). "
            "Columnas compuestas y riostras: ductilidad alta; vigas: "
            "ductilidad moderada. AJUSTE CLAVE para riostras rellenas "
            "cuadradas/rectangulares: la relación ancho-espesor límite se "
            "multiplica por el factor (0.264 + 0.0082*Kl/r) para Kl/r entre 35 "
            "y 90 — el relleno de concreto retrasa el pandeo local, "
            "permitiendo secciones relativamente más esbeltas que en acero "
            "puro. Conexiones viga-columna: mismas 2 opciones que PAC-DES "
            "(simple con rotación 0.025 rad, o a momento TR).\n\n"
            "F.3.8.3 PAEC (Pórticos Arriostrados Excéntricamente Compuestos): "
            "columnas embebidas o rellenas; VIGAS de acero o compuestas; "
            "VÍNCULOS obligatoriamente de ACERO (nunca compuestos — el "
            "mecanismo dúctil de fluencia a cortante del vínculo requiere "
            "acero puro); riostras de acero o rellenas. Remite íntegramente a "
            "los requisitos de PAE de acero puro (F.3.6.3: bases de diseño, "
            "análisis, sistema, miembros, conexiones) — la única diferencia "
            "relevante es que las columnas ahora pueden ser compuestas. "
            "Mismo mecanismo de disipación: fluencia a cortante del vínculo, "
            "mismas 2 opciones de conexión viga-columna (simple 0.025 rad, o "
            "TR según F.3.7.2.6.4-6).\n\n"
            "Principio general de F.3.8: los sistemas arriostrados compuestos "
            "no reinventan la mecánica de PAC/PAE de acero puro — la añaden "
            "una capa de verificación de la interacción acero-concreto "
            "(esbeltez efectiva de riostras rellenas, columnas compuestas "
            "según F.2.9), reutilizando el resto del capítulo F.3.6 por "
            "referencia directa."
        ),
    },
    {
        "id": "NSR10-F-F_3_8_muros_compuestos",
        "seccion": "F.3.8.4 a F.3.8.6 (Muros de cortante compuestos)",
        "titulo": (
            "Muros de cortante compuestos acero-concreto: MCC-DMI/DES (muro de "
            "concreto reforzado + elementos de borde y vigas de acople de "
            "acero) y MCAC (placas de acero embebidas en concreto por uno o "
            "ambos lados). Vigas de acople de acero: formula de resistencia a "
            "cortante esperada Vn=2Ry*Mp/g y longitud de empotramiento en el "
            "muro."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3. F.3.8.4 a F.3.8.6 — Muros de "
            "cortante compuestos acero-concreto.\n\n"
            "F.3.8.4 MCC-DMI: muros de concreto reforzado con elementos de "
            "borde de acero/compuestos (perfiles como columnas de borde) y "
            "vigas de acople de acero o compuestas conectando muros "
            "adyacentes. Deformación inelástica LIMITADA. Muros cumplen "
            "Título C excluyendo C.21 (sin detallado sísmico especial de "
            "concreto). Para muros acoplados: se permite plastificar vigas de "
            "acople en toda la altura, redistribuyendo cortante hasta 20% "
            "hacia pisos adyacentes.\n\n"
            "Vigas de acople de acero (secciones I) — resistencia a cortante "
            "esperada (ecuación F.3.8.4-1):\n"
            "  Vn = 2*Ry*Mp/g  <=  Ry*Vp\n"
            "donde Mp=Fy*Z, Vp=0.6*Fy*Atw, g=distancia libre de la viga de "
            "acople. La LONGITUD DE EMPOTRAMIENTO Le en el muro (ecuación "
            "F.3.8.4-2, función de f'c, ancho de aleta, espesor de muro) es el "
            "parámetro crítico — debe llevar refuerzo vertical en el muro con "
            "resistencia axial nominal igual a Vn de la viga, sobre esa "
            "longitud de empotramiento.\n\n"
            "F.3.8.5 MCC-DES: mismo concepto que DMI pero deformación "
            "inelástica SIGNIFICATIVA — muros cumplen Título C INCLUYENDO C.21 "
            "(detallado sísmico especial completo). Para muros acoplados: "
            "plastificación de vigas de acople en toda la altura SEGUIDA por "
            "plastificación en la base de los muros (secuencia de falla "
            "controlada). Resistencia esperada de vigas de acople amplificada "
            "por 1.1 (endurecimiento por deformación): Vn,comp = "
            "1.1*Ry*Vp+... (ecuación F.3.8.5-3). Columnas de acero no "
            "embebidas: ductilidad alta.\n\n"
            "F.3.8.6 MCAC (Muros de Cortante de Acero Compuestos): variante "
            "reforzada del MCA de acero puro (F.3.6.5) — placa de acero con "
            "recubrimiento de concreto reforzado en uno o ambos lados (el "
            "concreto RIGIDIZA la placa contra pandeo, permitiendo mayor "
            "resistencia efectiva). Espesor mínimo de placa: 9.5 mm (NO se "
            "permiten placas más delgadas). Recubrimiento de concreto: mínimo "
            "100 mm por lado si es a ambos lados, 200 mm si es a un solo lado. "
            "Cuantía mínima de refuerzo del recubrimiento: 0.0025 en ambas "
            "direcciones, espaciamiento máximo 450 mm. Resistencia a cortante "
            "del tablero (ecuación F.3.8.6-1, phi=0.9):\n"
            "  Vn = 0.6*Asp*Fy\n"
            "donde Asp=área horizontal de la placa de acero atiesada. Si la "
            "placa NO cumple los requisitos de rigidización del recubrimiento "
            "(F.3.8.6.5.3), se diseña con la resistencia reducida del MCA de "
            "acero puro (F.3.6.5) en vez de esta fórmula compuesta.\n\n"
            "Comparación clave MCC vs MCAC: MCC es un muro de CONCRETO "
            "reforzado con acero como elemento de borde/acople (el concreto "
            "es el elemento principal); MCAC es una placa de ACERO como "
            "elemento principal, con concreto solo como recubrimiento "
            "rigidizante — mecanismos de falla y fórmulas de resistencia "
            "completamente distintos aunque ambos sean 'compuestos'."
        ),
    },
    {
        "id": "NSR10-F-F_3_9_fabricacion_montaje",
        "seccion": "F.3.9 (Fabricación y Montaje)",
        "titulo": (
            "Requisitos de fabricacion y montaje para el Sistema de "
            "Resistencia Sismica (SRS) de acero: contenido obligatorio de "
            "planos de fabricacion/montaje (localizacion de pernos "
            "pretensionados, acabado de agujeros de acceso, ensayos no "
            "destructivos requeridos), y restricciones en zonas protegidas "
            "(prohibicion de soldar/perforar fijaciones de fachada dentro de "
            "ellas)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.9, Fabricación y Montaje del "
            "Sistema de Resistencia Sísmica (SRS) de acero. Se cumplen todos "
            "los requisitos de F.2.13 (fabricación general), más lo "
            "específico de esta sección.\n\n"
            "F.3.9.1.1 Planos de fabricación — deben indicar, cuando "
            "aplique: localización de pernos pretensionados; superficies con "
            "acabados especiales clase A o mejores; placas de unión a escala "
            "cuando se diseñan para rotaciones inelásticas; dimensiones y "
            "acabado de agujeros de acceso de soldadura; sitios donde deben "
            "removerse platinas de respaldo o extensiones de soldadura; "
            "ensayos no destructivos que debe realizar el fabricante.\n\n"
            "F.3.9.1.2 Planos de montaje — contenido análogo (localización de "
            "pernos pretensionados, remoción de platinas de respaldo, "
            "secuencia especial de soldadura/ensamble cuando se requiera).\n\n"
            "F.3.9.1.3 Construcción compuesta — los planos de fabricación y "
            "montaje de los componentes de acero en sistemas compuestos "
            "(F.3.7/F.3.8) deben cumplir además los requisitos de F.3.1.4.3.\n\n"
            "F.3.9.2.1 ZONAS PROTEGIDAS — restricciones obligatorias: "
            "(1) toda discontinuidad de fabricación/montaje (soldaduras "
            "provisionales, ayudas de montaje, corte con soplete) debe "
            "repararse; (2) NO se permiten conectores de cortante soldados ni "
            "fijaciones de lámina colaborante que penetren la aleta de la "
            "viga dentro de la zona protegida — solo soldaduras de tapón para "
            "fijar el tablero metálico; (3) NO se permite fijar accesorios de "
            "fachada, particiones, ductos o tuberías (soldados, pernados, con "
            "pernos autoperforantes o disparados) dentro de la zona "
            "protegida. Esta prohibición evita introducir concentradores de "
            "esfuerzo justo donde se espera que ocurra la fluencia dúctil "
            "controlada del sistema sísmico.\n\n"
            "F.3.9.2.3 Uniones soldadas — deben cumplir AWS D.1.1 y AWS D.1.8 "
            "(esta última específica para aplicaciones sísmicas), tanto en "
            "soldadura de taller como de campo. F.3.9.2.4 — esquinas de "
            "placas de continuidad y atiesadores en almas de perfiles "
            "laminados se detallan según AWS D.1.8 numeral 4.1."
        ),
    },
    {
        "id": "NSR10-F-F_3_10_control_calidad",
        "seccion": "F.3.10 (Control de Calidad y Supervisión Técnica)",
        "titulo": (
            "Control de calidad e inspeccion para el Sistema de Resistencia "
            "Sismica de acero: inspeccion visual de soldaduras (antes/"
            "durante/despues), ensayos no destructivos obligatorios (100% "
            "ultrasonido en soldaduras acanaladas de penetracion completa "
            ">=8mm, 25% particulas magneticas en soldaduras viga-columna), e "
            "inspeccion de pernos pretensionados."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.10, Control de Calidad y "
            "Supervisión Técnica para estructuras del Sistema de Resistencia "
            "Sísmica (SRS). Se cumplen todos los requisitos de F.2.14 más lo "
            "adicional de esta sección — obligatorio incluirlo en el plan de "
            "calidad del proyecto (Título I).\n\n"
            "F.3.10.2.1 Inspección visual de soldaduras (AWS D.1.8) — método "
            "PRINCIPAL de control, en 3 etapas:\n"
            "  ANTES de soldar: preparación de junta (alineamiento, abertura "
            "de raíz), limpieza de superficies, puntos de soldadura, "
            "acondicionamiento de platinas de respaldo y agujeros de acceso.\n"
            "  DURANTE la soldadura: parámetros del equipo, velocidad de "
            "avance, precalentamiento y temperatura entre pases, posición de "
            "soldadura, calificación del operario, condiciones ambientales "
            "(viento, lluvia, temperatura).\n"
            "  DESPUÉS de soldar: limpieza, identificación del operario, "
            "tamaño/longitud/localización, ausencia de fisuras, fusión "
            "adecuada, tamaño de cráteres, socavación, porosidad; remoción de "
            "platinas de respaldo y extensiones.\n\n"
            "F.3.10.2.2 Ensayos NO destructivos OBLIGATORIOS (más allá de la "
            "inspección visual):\n"
            "  Área 'k' (soldaduras de placas de enchape/continuidad/"
            "atiesadores): partículas magnéticas hasta 75 mm de la soldadura.\n"
            "  Soldaduras acanaladas de penetración completa: ULTRASONIDO al "
            "100% en espesores >=8 mm; RADIOGRÁFICO en espesores <8 mm; "
            "PARTÍCULAS MAGNÉTICAS al 25% de todas las soldaduras "
            "viga-columna acanaladas de penetración completa.\n"
            "  Material base >38 mm con carga perpendicular a la laminación: "
            "ultrasonido para desgarramiento lamelar.\n"
            "  Reparaciones en vigas de sección reducida (RBS): partículas "
            "magnéticas en toda soldadura de reparación.\n"
            "  Reducción de porcentaje de ensayo permitida (a 25% ultrasonido/"
            "radiográfico, o 10% partículas magnéticas) SOLO si el operario "
            "demuestra <5% de rechazos — NUNCA en área 'k', reparaciones, o "
            "remoción de respaldos/extensiones (ahí siempre 100%/25% fijo).\n\n"
            "F.3.10.3 Inspección de pernos pretensionados — 3 etapas: "
            "ANTES (selección correcta de pernos y procedimiento, "
            "almacenamiento adecuado); DURANTE (colocación, apriete inicial, "
            "no-rotación de un componente durante el tensionamiento, "
            "verificación de pretensionamiento según F.2.10.3.1, orden desde "
            "el punto más rígido hacia los bordes libres); DESPUÉS "
            "(documentación de conexiones aceptadas/rechazadas)."
        ),
    },
    {
        "id": "NSR10-F-F_3_11_ensayos_calificacion",
        "seccion": "F.3.11 (Ensayos para Calificación de Conexiones)",
        "titulo": (
            "Marco de calificacion de conexiones sismicas de acero por "
            "ensayo: (1) precalificacion via ANSI/AISC 358 o aprobacion de "
            "la Comision Asesora Permanente; (2) ensayos ciclicos de "
            "conexiones viga-columna/vinculo-columna con secuencia de carga "
            "estandarizada (6 ciclos crecientes hasta fractura); (3) ensayos "
            "ciclicos especificos para riostras de pandeo restringido (BRB), "
            "incluyendo el criterio de aceptacion beta<=1.3."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.11, Ensayos para "
            "Calificación de Conexiones. Marco completo para demostrar que "
            "una conexión sísmica puede sostener la deriva de piso o el "
            "ángulo de rotación de vínculo requerido, sin depender solo del "
            "cálculo.\n\n"
            "F.3.11.1 PRECALIFICACIÓN de conexiones viga-columna (PRM-DES/"
            "DMO) y vínculo-columna (PAE) — dos caminos: (1) usar una "
            "conexión ya precalificada del estándar ANSI/AISC 358 "
            "'Prequalified Connections for Special and Intermediate Steel "
            "Moment Frames', sin necesidad de ensayos cíclicos adicionales — "
            "el camino más común en la práctica; o (2) obtener aprobación "
            "directa de la Comisión Asesora Permanente para el Régimen de "
            "Construcciones Sismo Resistentes. Una conexión precalificada "
            "requiere un registro escrito con: descripción gráfica, "
            "comportamiento esperado elástico/inelástico, sistemas para los "
            "que aplica, límites de todas las variables, soldaduras de "
            "demanda crítica, zona protegida, procedimiento de diseño, y "
            "referencias de los ensayos que la sustentan.\n\n"
            "F.3.11.2 ENSAYOS CÍCLICOS DE CALIFICACIÓN (viga-columna en PRM, "
            "vínculo-columna en PAE) — cuando no se usa una conexión "
            "precalificada. Requisitos clave del espécimen: mínimo una "
            "columna con vigas/vínculos a uno o ambos lados; la rotación "
            "inelástica del ensayo debe distribuirse entre los mismos "
            "elementos que en el prototipo real, dentro del 25%; peralte del "
            "espécimen >=90% del prototipo, peso por unidad de longitud "
            ">=75%; esfuerzo de fluencia medido por ENSAYO REAL del material "
            "(nunca certificados de acería), dentro de ±15% de Ry*Fy.\n\n"
            "SECUENCIA DE CARGA para conexiones viga-columna (control por "
            "ángulo de deriva θ, ciclos crecientes hasta fractura):\n"
            "  6 ciclos a θ=0.00375 rad, 6 a 0.005, 6 a 0.0075, 4 a 0.01, "
            "2 a 0.015, 2 a 0.02, 2 a 0.03, 2 a 0.04 rad — luego continuar "
            "con incrementos de 0.01 rad, 2 ciclos cada paso, hasta la "
            "falla.\n"
            "SECUENCIA DE CARGA para conexiones vínculo-columna (control por "
            "ángulo de rotación del vínculo γtotal): arranca igual (6 ciclos "
            "a 0.00375-0.01 rad) pero incluye más pasos intermedios hasta "
            "γtotal=0.09 rad, reflejando la mayor capacidad de rotación "
            "esperada de un vínculo corto frente a una rótula de viga "
            "normal.\n\n"
            "Criterio de aceptación (F.3.11.2.9): el espécimen debe sostener "
            "el ángulo de deriva/rotación requerido durante al menos UN "
            "ciclo completo de carga sin perder la resistencia mínima "
            "exigida.\n\n"
            "F.3.11.3 ENSAYOS CÍCLICOS PARA RIOSTRAS DE PANDEO RESTRINGIDO "
            "(BRB, sistema PAPR de F.3.6.4) — obligatorios siempre (no hay "
            "camino de precalificación tipo ANSI 358 para BRB), porque el "
            "comportamiento depende del sistema de restricción patentado de "
            "cada fabricante, no solo de la sección de acero. Requiere "
            "MÍNIMO 1 ensayo de CONJUNTO (riostra+conexiones, reproduciendo "
            "rotaciones del prototipo) y MÍNIMO 1 ensayo de RIOSTRA sola "
            "(uniaxial). Secuencia de carga por deformación axial Δb "
            "(relativa a Δby=fluencia y Δbm=deriva de diseño): 2 ciclos a "
            "Δby, 2 a 0.5Δbm, 2 a Δbm, 2 a 1.5Δbm, 2 a 2Δbm, luego ciclos "
            "adicionales a 1.5Δbm hasta acumular deformación inelástica "
            "total >=200 veces la deformación de fluencia.\n\n"
            "Criterios de aceptación específicos de BRB (F.3.11.3.10): "
            "comportamiento histerético estable con incremento de rigidez, "
            "sin fractura/inestabilidad/falla de conexión; fuerza máxima en "
            "cada ciclo >= resistencia nominal del núcleo; y la relación "
            "entre fuerza máxima de COMPRESIÓN y fuerza máxima de TENSIÓN "
            "(el factor β usado en el diseño, F.3.6.4.2.1) NO debe exceder "
            "1.3 — este es el límite numérico que en la práctica acota qué "
            "tan asimétrico puede ser el comportamiento de una riostra BRB "
            "real frente al ideal simétrico tensión=compresión."
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
    print(f"OK: {len(rows)} chunks F.3.7-F.3.11 cargados con embedding. Titulo F.3 completo.")


if __name__ == "__main__":
    main()
