"""
NSR-10 Titulo F, Capitulo F.5 (Estructuras de Aluminio) -- F.5.1
(GENERALIDADES) COMPLETO. Primera pieza de F.5, la ultima seccion del
Titulo F -- con F.4 ya completo (F.4.1-F.4.8), F.5 es lo unico que
falta para cerrar el Titulo F entero.

F.5.1.1 (Alcance), F.5.1.2 (Definiciones -- ~30 terminos), F.5.1.3
(Simbolos principales -- glosario extenso, agrupado en piezas densas
por ser referencia de simbolos/definicion, no numerales tecnicos
individuales).

HALLAZGO REAL IMPORTANTE: F.5 usa un sistema de unidades DISTINTO al
resto de la NSR-10 -- kgf y kgf/mm^2 en vez de N y MPa (SI), segun
declara el propio F.5.1.1: "En el presente Capitulo no se empleo el
sistema de unidades internacional SI, por lo tanto las fuerzas estan
en kgf y los esfuerzos en kgf/mm^2." Cuando este mismo capitulo se
remite a F.1/F.2/F.3 (que si usan SI), debe reinterpretarse: donde
alli se dice N debe interpretarse aqui como kgf, MPa como kgf/mm^2, y
N.mm como kgf.mm. NO mezclar unidades al citar F.5 -- las tablas de
propiedades de aleaciones (F.5.2.2-1/-2/-3) ya estan en kgf/mm^2
verbatim del original, no convertidas.

Con esto F.5.1 queda COMPLETO. F.5.2 (Propiedades y seleccion de
materiales) ya arranco al final de este PDF (F-444) pero NO se ha
ingestado -- queda para la proxima pieza. F.5 completo es MUY grande:
sigue denso (F.5.2, F.5.3, F.5.4 diseno de miembros) hasta la ultima
pagina de este PDF (F-501, todavia dentro de F.5.4) y continua en el
siguiente PDF de Drive (NSR-10-1183-1283.pdf, F.5.5-F.5.8 + apendices
F.5.A-F.5.F, cierra el Titulo F) -- no descargado todavia.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final CON verificacion real de tokens (metodo de F.4.6/F.4.7/F.4.8).

Fuente: NSR-10-1083-1182.pdf (Drive id 1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi,
ya descargado localmente desde F.4.7/F.4.8), paginas internas F-439 a
F-444 (paginas PDF 38-43), leidas visualmente pagina por pagina,
re-verificadas contra el PDF antes de transcribir.

Uso: python _ingest_titulo_f_f51_verbatim.py
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
        "id": "NSR10-F-F_5_1_1_alcance",
        "seccion": "F.5.1.1 (Alcance — sistema de unidades kgf/kgf·mm², no SI)",
        "titulo": "Requisitos de diseño de miembros de aluminio; unidades en kgf y kgf/mm² (no SI); no cubre estructuras aeroespaciales/tanques/tuberías.",
        "texto": (
            "CAPÍTULO F.5 — ESTRUCTURAS DE ALUMINIO. F.5.1 — "
            "GENERALIDADES. F.5.1.1 — ALCANCE — Este Capítulo establece "
            "los requisitos para el diseño de miembros de aluminio de "
            "estructuras aporticadas, en celosía y de lámina "
            "rigidizada, conformados por elementos extruídos o "
            "laminados. Si se usan piezas coladas o forjadas en "
            "caliente, éstas deben ser fabricadas y diseñadas de "
            "acuerdo con normas apropiadas reconocidas, a juicio del "
            "Comisión Asesora Permanente para el Régimen de "
            "Construcciones Sismo Resistentes, y en consulta con el "
            "fabricante específico. En el presente Capítulo no se "
            "empleó el sistema de unidades internacional SI, por lo "
            "tanto las fuerzas están en kgf y los esfuerzos en "
            "kgf/mm². En aquellos términos que se emplean en el "
            "presente Capítulo, pero cuya definición está en los "
            "Capítulos F.1, F.2 o F.3, (en los cuales se emplea el "
            "sistema SI), cuando allí se diga N debe interpretarse "
            "aquí como kgf, cuando allí se diga MPa debe interpretarse "
            "aquí como kgf/mm², y cuando allí se diga N·mm debe "
            "interpretarse aquí como kgf·mm. Estos requisitos de "
            "diseño se dirigen a una gran variedad de aleaciones de "
            "aluminio apropiadas para uso estructural y pueden "
            "aplicarse a estructuras sujetas a condiciones atmosféricas "
            "normales tales como puentes, edificios, torres, vehículos "
            "de carretera y sobre rieles, naves marinas, grúas y "
            "estructuras sobre cubierta ubicadas mar adentro. Las "
            "prescripciones no cubren aleaciones aeroespaciales, el "
            "diseño de detalles de piezas coladas, estructuras de "
            "cascarones curvos ni estructuras sujetas a condiciones "
            "térmicas o químicas severas. No están dirigidas al diseño "
            "de tanques de contención, tuberías, estructuras que se "
            "muevan en el aire o embarcaciones, ni para ninguna otra "
            "aplicación para la cual existan códigos específicos de "
            "diseño, expedidos por entidades de reconocida autoridad."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_2_definiciones_p1",
        "seccion": "F.5.1.2 (Definiciones — sección transversal compacta a frontera de fusión)",
        "titulo": "Términos: sección compacta, vida de diseño, espectro/clase de detalle, distancia al borde, longitud efectiva, carga/vida mayorada, resistencia de diseño, fatiga, frontera de fusión.",
        "texto": (
            "F.5.1.2 — DEFINICIONES — Para el propósito de este "
            "Capítulo, se aplican las siguientes definiciones: Sección "
            "transversal compacta — Una sección transversal que puede "
            "desarrollar su capacidad plástica total, sujeta a "
            "compresión o flexión, sin reducción debida a pandeo local "
            "de elementos de pared delgada. Vida de diseño — Período "
            "durante el cual la estructura o componente debe "
            "comportarse con seguridad, con una probabilidad aceptable "
            "de que no requerirá reparación ni retiro de servicio. "
            "Espectro de diseño — Tabulación del número de ocurrencias "
            "de todos los rangos de esfuerzos causados por eventos de "
            "carga. Clase de detalle — Calificación dada a un detalle "
            "indicando su nivel de resistencia a la fatiga. Distancia "
            "al borde — Distancia desde el centro de un agujero para "
            "un sujetador hasta el borde más próximo del elemento. "
            "Longitud efectiva — Longitud entre puntos de restricción "
            "efectiva de un miembro multiplicada por un coeficiente "
            "que tiene en cuenta las condiciones en los extremos y la "
            "carga. Carga mayorada — Carga nominal multiplicada por el "
            "coeficiente de mayoración de carga pertinente. Vida "
            "mayorada — Es la vida de diseño multiplicada por el "
            "coeficiente parcial de vida pertinente. Resistencia de "
            "diseño — Es la resistencia nominal del miembro "
            "multiplicada por el coeficiente de reducción pertinente. "
            "Seguridad en la falla — Es la capacidad de la estructura "
            "para mantenerse utilizable después del descubrimiento y "
            "monitoreo de grietas por fatiga. Fatiga — Daño por "
            "agrietamiento gradual ocurrido a un miembro estructural "
            "debido a aplicaciones repetidas de un esfuerzo que es "
            "insuficiente para causar la falla por una sola aplicación. "
            "Frontera de fusión — Material afectado por el calor en la "
            "zona inmediatamente adyacente al lado de un cordón de "
            "soldadura."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_2_definiciones_p2",
        "seccion": "F.5.1.2 (Definiciones — zona afectada por el calor a historia de esfuerzo)",
        "titulo": "Términos: zona afectada por calor, inestabilidad, pandeo torsional lateral/local, estado límite, elemento saliente/reforzado/rigidizado, esbeltez.",
        "texto": (
            "Zona afectada por el calor — Zona en la cual hay una "
            "reducción en la resistencia del material y que se "
            "presenta en la vecindad de las soldaduras en ciertas "
            "clases de aleaciones de aluminio. Carga impuesta — Toda "
            "carga en una estructura que no sea carga muerta o de "
            "viento. Inestabilidad — Pérdida de rigidez de una "
            "estructura (usualmente súbita) que limita su capacidad de "
            "soportar carga y, en ciertos casos, puede causar una "
            "falla catastrófica. Pandeo torsional lateral — Pandeo de "
            "una viga acompañado por una combinación de desplazamiento "
            "lateral y torcedura. Restricción lateral — Restricción "
            "que limita el movimiento lateral de la aleta a compresión "
            "de una viga. Estado límite — Condición más allá de la "
            "cual la estructura es inadecuada para su uso previsto. "
            "Evento de carga — Ciclo de carga definido que, para "
            "propósitos de diseño, se supone que se repite un número "
            "dado de veces. Espectro de carga — Tabulación que muestra "
            "las frecuencias relativas de eventos de carga de "
            "diferentes intensidades sobre una estructura. Pandeo "
            "local — Pandeo de las paredes delgadas de un componente a "
            "compresión caracterizado por la formación de ondas o "
            "rizamientos a lo largo del miembro. Gran total de Miner — "
            "Gran total de daño por fatiga acumulativo calculado con "
            "base en una regla desarrollada por Palmagren y Miner. "
            "Carga nominal — Carga a la cual puede esperarse que una "
            "estructura esté sujeta durante su servicio normal. "
            "Elemento saliente — Elemento de una sección, compuesta de "
            "elementos planos o curvos, que está soportado a lo largo "
            "de un borde longitudinal y libre a lo largo del otro. "
            "Elemento reforzado — Elemento de una sección que está "
            "rigidizado por la introducción de un refuerzo "
            "longitudinal a lo largo del borde del elemento o dentro "
            "de su ancho. Resistencia — Es la resistencia de un "
            "miembro basada en cálculos usando valores máximos "
            "aceptables para la resistencia del material. Vida segura "
            "— Diseño contra la fatiga en el que la vida calculada es "
            "varias veces más larga que la vida requerida de servicio. "
            "Sección transversal semi-compacta — Sección transversal "
            "de una viga en la que el esfuerzo en las fibras extremas "
            "está limitado al esfuerzo de prueba del 0.2% debido a que "
            "el pandeo local de los elementos a compresión no "
            "permitiría el desarrollo de la capacidad total de momento "
            "plástico. Estados límite de servicio — Son aquellos "
            "estados límite que cuando son excedidos pueden llevar la "
            "estructura a ser inadecuada para el uso propuesto aunque "
            "no haya colapso. Esbeltez — Es la longitud efectiva de un "
            "miembro a compresión dividida por su radio de giro. "
            "Elemento rigidizado — Elemento de una sección, compuesta "
            "de elementos planos o curvos, que está soportado a lo "
            "largo de sus bordes longitudinales. Ciclo de esfuerzo — "
            "Patrón de variación del esfuerzo en un punto. Normalmente "
            "tiene la forma de dos media-ondas opuestas. Historia de "
            "esfuerzo — Registro que muestra cómo varía el esfuerzo en "
            "un punto durante la carga."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_2_definiciones_p3_rango_esfuerzo",
        "seccion": "F.5.1.2 (Definiciones — rango de esfuerzo a estados límite últimos)",
        "titulo": "Términos finales: rango de esfuerzo (2 definiciones), espectro de esfuerzo, pandeo torsional/flexo-torsional, estados límite últimos.",
        "texto": (
            "Rango de esfuerzo — (1) Es la mayor diferencia algebraica "
            "entre los esfuerzos principales que ocurren sobre planos "
            "principales apartados no más de 45°, en cualquier ciclo "
            "de esfuerzo, sobre una lámina o elemento. (2) Es la "
            "diferencia algebraica o vectorial entre la mayor y la "
            "menor suma vectorial de los esfuerzos en cualquier ciclo "
            "de esfuerzos sobre una soldadura. Espectro de esfuerzo — "
            "Tabulación del número de ocurrencias de todos los rangos "
            "de esfuerzo de diferentes magnitudes durante un evento de "
            "carga. Pandeo torsional — Pandeo de un elemento "
            "acompañado de torcedura. Pandeo flexo-torsional — Pandeo "
            "de un elemento acompañado de flexión total y torcedura. "
            "Estados límite últimos — Son aquellos estados límite que "
            "cuando son excedidos pueden causar el colapso parcial o "
            "total de la estructura."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_A_K",
        "seccion": "F.5.1.3 (Símbolos principales — A a K2)",
        "titulo": "Glosario de símbolos: área, aletas, dimensiones geométricas, módulos, esfuerzos límite de fatiga, momentos de inercia, coeficientes.",
        "texto": (
            "F.5.1.3 — SÍMBOLOS PRINCIPALES. A = área. Clasificación de "
            "durabilidad. Ae = área efectiva de la sección. Av = área "
            "efectiva de corte. a = espaciamiento de rigidizadores "
            "transversales. Ancho de láminas sin rigidizar. B = ancho "
            "total de lámina multi-rigidizada. Clasificación de "
            "durabilidad. BRF = resistencia de diseño al aplastamiento "
            "de un sujetador. b = ancho de elemento plano. be = ancho "
            "efectivo de la lámina del alma (vigas ensambladas). "
            "C = clasificación de durabilidad. D = diámetro de un tubo "
            "redondo hasta la parte media de la pared de metal. Altura "
            "total del alma hasta la parte externa de las aletas. "
            "d = altura del alma entre las aletas. Altura de láminas no "
            "rigidizadas. df = diámetro nominal del sujetador o pasador. "
            "E = módulo de elasticidad. F = coeficiente de prueba de "
            "fatiga. F = frontera de fusión de la zona afectada por "
            "calor. Fc = capacidad de agarre por fricción de un perno "
            "de alta resistencia debidamente apretado. f = coeficiente "
            "de reducción aplicado a kz. foc = esfuerzo límite de "
            "amplitud constante. fov = esfuerzo límite de amplitud "
            "variable. fr = rango de esfuerzos de diseño. fu = esfuerzo "
            "último de tensión. f0.2 = esfuerzo mínimo de prueba del "
            "0.2%. G = módulo de cortante. g = coeficiente de gradiente "
            "de esfuerzos. gt = garganta de una soldadura. ge = "
            "longitud del lado del cordón de una soldadura. H = "
            "coeficiente de alabeo. h = coeficiente de elementos "
            "reforzados. Distancia al borde libre. Is = segundo "
            "momento del área de la sección completa de un rigidizador "
            "efectivo (viga ensamblada). ISU = segundo momento del "
            "área de una sub-unidad de lámina (láminas "
            "multi-rigidizadas). Iy = segundo momento del área "
            "alrededor del eje centroidal. J = constante de torsión. "
            "K = coeficiente de longitud efectiva para miembros a "
            "compresión. K1 = coeficiente para el cálculo de la "
            "resistencia de pernos. K2 = constante para el criterio de "
            "falla por fatiga."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_kL_M2",
        "seccion": "F.5.1.3 (Símbolos principales — kL a M2)",
        "titulo": "Coeficientes de pandeo local y cortante, longitudes, momentos (mayorado, crítico, resistencia a momento en sus variantes).",
        "texto": (
            "kL = coeficiente de pandeo local. kv = coeficiente de "
            "reducción de la resistencia longitudinal que se tiene en "
            "cuenta para valores de cortante altos. kz = coeficiente de "
            "resistencia para el material de la zona afectada por el "
            "calor. k'z = coeficiente de resistencia modificado para el "
            "material de la zona afectada por el calor. L = longitud "
            "entre apoyos. l = longitud efectiva entre apoyos "
            "laterales. le = longitud efectiva de una soldadura a tope. "
            "lf = longitud efectiva de una soldadura de filete. "
            "M = momento producido por la carga mayorada. M̄ = momento "
            "uniforme equivalente. Mcr = momento uniforme crítico en el "
            "rango elástico para pandeo torsional lateral. Mf = valor "
            "totalmente compacto de MRS. MRF = valor reducido de MRS "
            "para aletas únicamente. MRS = resistencia de diseño a "
            "momento de una sección en ausencia de cortante. MRSO = "
            "resistencia de diseño a momento de una sección, reducida "
            "para tener en cuenta el cortante. MRSx = resistencia de "
            "diseño a momento uniaxial con respecto al eje mayor "
            "(teniendo en cuenta el cortante). MRSy = resistencia de "
            "diseño a momento uniaxial con respecto al eje menor "
            "(teniendo en cuenta el cortante). MRx = momento de diseño "
            "basado en la resistencia a pandeo torsional lateral. "
            "Ms = valor semi-compacto de MRS. Mx = momento uniaxial con "
            "respecto al eje mayor. M̄h = momento uniforme equivalente "
            "con respecto al eje mayor. My = momento uniaxial con "
            "respecto al eje menor. M̄y = momento uniforme equivalente "
            "con respecto al eje menor. M1 = momento mayorado máximo. "
            "M2 = momento mayorado mínimo."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_m_P",
        "seccion": "F.5.1.3 (Símbolos principales — m a P)",
        "titulo": "Pendiente de fatiga, número de almas/ciclos, fuerza axial P, cargas críticas/prueba/preesfuerzo, resistencias de diseño con subíndice R.",
        "texto": (
            "m = pendiente inversa de la curva fr−N (fatiga). m1, m2 = "
            "coeficientes de pandeo por cortante (vigas ensambladas). "
            "N = número de almas. Ciclos previstos hasta la falla "
            "(resistencia a la fatiga). n = número equivalente de "
            "ciclos de un rango de esfuerzo (fatiga). Tiempo en días "
            "entre la soldadura y la carga. P = fuerza axial de "
            "tensión o compresión debida a la carga mayorada. "
            "Protección. Pcr = carga crítica elástica para pandeo "
            "torsional. Po = carga de prueba para un perno. Pp = carga "
            "de preesfuerzo. PR = resistencia axial de diseño "
            "calculada con base en el pandeo general como columna o "
            "en el pandeo torsional. PRB = resistencia de diseño de "
            "una soldadura a tope. PRF = resistencia de diseño de una "
            "soldadura de filete. PRFB = resistencia de diseño de la "
            "zona afectada por el calor adyacente a la frontera de "
            "fusión de una soldadura a tope (fuerza de tensión normal "
            "directa). PRFF = resistencia de diseño de la zona "
            "afectada por el calor adyacente a la frontera de fusión "
            "de una soldadura de filete (fuerza de tensión normal "
            "directa). PRG = resistencia de diseño de una unión "
            "pegada. PRS = resistencia axial de diseño (tensión o "
            "compresión). PRTB = resistencia de diseño de la zona "
            "afectada por el calor adyacente al borde de una soldadura "
            "a tope (fuerza de tensión normal directa). PRTF = "
            "resistencia de diseño de la zona afectada por el calor "
            "adyacente al borde de una soldadura de filete (fuerza de "
            "tensión normal directa)."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_PRx_S",
        "seccion": "F.5.1.3 (Símbolos principales — PRx a S)",
        "titulo": "Resistencias axiales de diseño por pandeo (ejes mayor/menor), zona afectada por calor, esfuerzos límite de capacidad, módulos plásticos.",
        "texto": (
            "PRx = resistencia axial de diseño para el pandeo general "
            "como columna con respecto al eje mayor. PRy = resistencia "
            "axial de diseño para el pandeo general como columna con "
            "respecto al eje menor. PRZ = resistencia de diseño de la "
            "zona afectada por el calor bajo carga directa. pa = "
            "esfuerzo límite para capacidad local (tensión y "
            "compresión). paz = esfuerzo límite directo en la zona "
            "afectada por el calor. pf = esfuerzo límite para remaches "
            "sólidos y pernos. po = esfuerzo límite para flexión y "
            "fluencia total. pof = esfuerzo límite del material de las "
            "aletas. pow = esfuerzo límite del material del alma. "
            "ps = esfuerzo límite para estabilidad al pandeo total. "
            "Esfuerzo de pandeo torsional lateral. Esfuerzo de pandeo "
            "para el alma tratada como una columna delgada entre "
            "aletas. pt = penetración de la soldadura. pv = esfuerzo "
            "límite a cortante. pvz = esfuerzo límite a cortante de la "
            "zona afectada por el calor. pw = esfuerzo límite del "
            "metal de aporte. pw1 = esfuerzo originado en el borde "
            "extremo del alma debido a una fuerza localizada. pw2 = "
            "esfuerzo originado en el punto medio del alma debido a "
            "una fuerza localizada. p1 = valor en el eje de esfuerzos "
            "de ps en los diagramas curvos para miembros a compresión. "
            "Valor de po para la sección totalmente compacta sin "
            "soldar. R = radio de curvatura hasta la mitad del metal "
            "de un elemento interno curvo. ry = radio de giro respecto "
            "al eje menor. S = módulo plástico de la sección bruta sin "
            "reducción por zona afectada por el calor, pandeo local o "
            "agujeros. Sa, Sb = acciones de la carga externa producidas "
            "por la carga mayorada. Sf = módulo plástico de la sección "
            "de aleta efectiva (viga ensamblada). Sn = módulo plástico "
            "de la sección neta. Sne = módulo plástico de la sección "
            "neta efectiva. S0 = área de la sección transversal del "
            "miembro."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_s_V",
        "seccion": "F.5.1.3 (Símbolos principales — s a VRZ)",
        "titulo": "Tolerancias de rectitud, zona afectada por calor, espesores, cortante, resistencias a cortante de soldaduras y de la zona afectada por calor.",
        "texto": (
            "s = coeficiente sobre p1 para tener en cuenta que un "
            "miembro a compresión no cumpla con las tolerancias de "
            "rectitud o torcedura. T = límite de la zona afectada por "
            "el calor. t = espesor. tA = el menor entre 0.5(tB+tC) y "
            "1.5tB. tB = espesor del elemento más delgado conectado "
            "por soldadura. tC = espesor del elemento más grueso "
            "conectado por soldadura. te = espesor de garganta "
            "efectivo. tf = espesor de aleta. t2 = espesor de aleta. "
            "V = fuerza cortante producida por la carga mayorada. "
            "VRFB = resistencia de diseño a cortante de la zona "
            "afectada por el calor adyacente a la frontera de fusión "
            "de una soldadura a tope. VRFF = resistencia de diseño a "
            "cortante de la zona afectada por el calor adyacente a la "
            "frontera de fusión de una soldadura de filete. VRS = "
            "resistencia de diseño a fuerza cortante. VRTB = "
            "resistencia de diseño a cortante de la zona afectada por "
            "el calor adyacente al borde de una soldadura a tope. "
            "VRTF = resistencia de diseño a cortante de la zona "
            "afectada por el calor adyacente al borde de una soldadura "
            "de filete. VRW = valor reducido de VRS. VRZ = resistencia "
            "de diseño a cortante de la zona afectada por el calor."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_v_z",
        "seccion": "F.5.1.3 (Símbolos principales — v (minúscula) a z, sección efectiva/neta)",
        "titulo": "Coeficientes de campo tensional, separación de rigidizadores, distancias del eje neutro, módulos de sección efectiva/neta.",
        "texto": (
            "vrf = coeficiente de campo tensional (vigas ensambladas). "
            "v1 = coeficiente de pandeo crítico al corte en el rango "
            "elástico. v2 = coeficiente básico de pandeo al corte "
            "considerando campo tensionado. v3 = coeficiente de pandeo "
            "al corte considerando campo tensionado y contribución de "
            "la aleta. W = metal de aporte. w = separación de "
            "rigidizadores en una lámina multi-rigidizada. y = "
            "distancia desde el centro de una lámina multi-rigidizada "
            "hasta el centro del rigidizador más extremo. yc = "
            "distancia desde el eje neutro hasta el borde más "
            "comprimido. yo = distancia desde el eje neutro hasta el "
            "borde menos comprimido, o en tensión. y1 = distancia "
            "desde el eje neutro hasta las fibras más esforzadas en "
            "una viga. y2 = distancia desde el eje neutro hasta el "
            "elemento de aleta a compresión en una viga. Ze = módulo "
            "elástico de la sección efectiva. Zn = módulo elástico de "
            "la sección neta. Zne = módulo elástico de la sección "
            "neta efectiva. z = distancia que se extiende la zona "
            "afectada por el calor desde una soldadura. z0 = valor "
            "básico de z."
        ),
    },
    {
        "id": "NSR10-F-F_5_1_3_simbolos_griegos",
        "seccion": "F.5.1.3 (Símbolos principales — letras griegas α a μs)",
        "titulo": "Coeficientes de cortante, esbeltez β, factor de reducción φ, coeficientes de carga γ, esfuerzos críticos σ/τ, coeficiente de deslizamiento μs.",
        "texto": (
            "α = relación entre el esfuerzo cortante en el alma "
            "mínimo y el máximo (distribución elástica de esfuerzos). "
            "Coeficiente modificador de la extensión de la zona "
            "afectada por el calor para tener en cuenta una "
            "temperatura elevada. αs = coeficiente para el cálculo de "
            "pernos o remaches en corte simple. β = parámetro de "
            "esbeltez. β0 = valor límite semi-compacto de β. β1 = "
            "valor límite totalmente compacto de β. φ = coeficiente de "
            "reducción de capacidad. γc = coeficiente de consecuencias "
            "de falla. γ = coeficiente de mayoración de carga. "
            "γL = coeficiente de fatiga. γmf = coeficiente de fatiga "
            "del material. γs = coeficiente para el cálculo de "
            "capacidad por fricción. ε = constante (25/po)^(1/2). "
            "λ = parámetro de esbeltez para pandeo como columna, "
            "pandeo torsional y pandeo torsional lateral. λy = "
            "relación de esbeltez de un miembro a compresión respecto "
            "a su eje menor. η = coeficiente modificador de la "
            "extensión de la zona afectada por el calor para tener en "
            "cuenta la acumulación incremental de calor. σcr = "
            "esfuerzo elástico crítico de un elemento con refuerzo. "
            "σcro = esfuerzo elástico crítico de un elemento sin "
            "refuerzo. σ1 = esfuerzo normal en una soldadura bajo "
            "carga mayorada. τ1 = esfuerzo cortante perpendicular al "
            "eje de la soldadura. τ2 = esfuerzo cortante paralelo al "
            "eje de la soldadura. μs = coeficiente de deslizamiento."
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
    print(f"Max chars: {max_len}")

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

    print(f"\nOK: {len(rows)} chunks verbatim de F.5.1 cargados. F.5.1 queda COMPLETO.")


if __name__ == "__main__":
    main()
