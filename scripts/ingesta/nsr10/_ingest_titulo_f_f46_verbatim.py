"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.6 (ENSAYOS PARA CASOS ESPECIALES)
COMPLETO. Septima pieza de F.4/F.5.

F.4.6.1 (Ensayos para determinacion del comportamiento estructural --
procedimiento DCCR completo con la ecuacion estadistica del factor de
resistencia phi F.4.6.1-2, el factor de correccion Cp F.4.6.1-3, y la
Tabla F.4.6.1-1 completa de datos estadisticos Mm/Vm/Fm/VF para ~30
tipos de componente), F.4.6.2 (Ensayos de confirmacion del
comportamiento estructural) y F.4.6.3 (Ensayos para determinacion de
las propiedades mecanicas -- seccion completa, elementos planos de
secciones formadas, acero virgen).

Con esto F.4.6 queda COMPLETO. F.4.7 (Tableros metalicos para trabajo
en seccion compuesta) arranca justo despues, en la ultima pagina de
este PDF (F-401) -- solo su titulo y alcance quedaron visibles, el
resto sigue en el siguiente PDF de Drive, no es parte de este chunk.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final igual que F.4.2/F.4.3/F.4.4/F.4.5.

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
paginas internas F-396 (final) a F-400 (paginas PDF 96-100), leidas
visualmente pagina por pagina.

Uso: python _ingest_titulo_f_f46_verbatim.py
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
        "id": "NSR10-F-F_4_6_alcance",
        "seccion": "F.4.6 (Ensayos para casos especiales — alcance)",
        "titulo": "Ensayos por laboratorio independiente o del fabricante; no aplica a diafragmas (remitirse a F.4.4.5).",
        "texto": (
            "F.4.6 — ENSAYOS PARA CASOS ESPECIALES — Los ensayos pueden "
            "realizarse por medio de un laboratorio independiente o por "
            "un laboratorio de pruebas del fabricante. Las disposiciones "
            "de este capítulo no se deben aplicar a diafragmas de acero "
            "formados en frío. Para estos elementos, se debe remitir a "
            "las especificaciones de la sección F.4.4.5."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_a_evaluacion_estadistica",
        "seccion": "F.4.6.1.1(a) (DCCR — evaluación estadística de resultados de ensayo)",
        "titulo": "Mínimo 3 especímenes idénticos, desviación ≤15% del promedio o más ensayos; promedio de todos = Rn.",
        "texto": (
            "F.4.6.1 — ENSAYOS PARA DETERMINACIÓN DEL COMPORTAMIENTO "
            "ESTRUCTURAL. F.4.6.1.1 — Diseño con Coeficientes de Carga y "
            "Resistencia (DCCR) — Cuando se requiera determinar el "
            "comportamiento estructural mediante ensayos se debe seguir "
            "el procedimiento descrito a continuación: (a) La evaluación "
            "de los resultados debe basarse en el valor promedio de los "
            "datos obtenidos del ensayo con no menos de tres especímenes "
            "idénticos, siempre y cuando la desviación entre el resultado "
            "de cualquier ensayo individual y el valor promedio de todo "
            "el estudio no exceda ±15%. Si tal desviación del valor "
            "promedio excede el 15% deben hacerse más pruebas de la "
            "misma clase hasta que la desviación no exceda el 15% o "
            "hasta que, al menos, se hayan realizado tres ensayos "
            "adicionales. Ningún resultado de ensayo será eliminado a "
            "menos que existan bases sólidas para su exclusión. El valor "
            "promedio de todos los ensayos será considerado, entonces, "
            "como la resistencia nominal, Rn, para la serie de pruebas. "
            "El valor Rn y el coeficiente de variación Vp de los "
            "resultados de la prueba se deberían determinar por medio de "
            "un análisis estadístico."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_b_ecuacion1_phi",
        "seccion": "F.4.6.1.1(b) (Ecuación de diseño F.4.6.1-1 y factor de resistencia φ, ecuación F.4.6.1-2)",
        "titulo": "ΣγᵢQᵢ ≤ φRn; φ = Cφ(MmFmPm)·e^(−βo√(VM²+VF²+CpVP²+VQ²)).",
        "texto": (
            "(b) La resistencia de los elementos ensayados, conjuntos, "
            "conexiones, o miembros deben satisfacer la ecuación "
            "F.4.6.1-1: ΣγᵢQᵢ ≤ φRn (F.4.6.1-1). Donde: ΣγᵢQᵢ = "
            "resistencia requerida basada en la combinación de carga más "
            "crítica y determinada de acuerdo con la sección "
            "F.4.1.5.1.2. γᵢ y Qᵢ son factores de carga y efectos de "
            "carga, respectivamente. φ = factor de resistencia = "
            "Cφ(MmFmPm)·e^(−βo√(VM²+VF²+CpVP²+VQ²)) (F.4.6.1-2)."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_b_definiciones_cphi_mm_fm_pm",
        "seccion": "F.4.6.1.1(b) (Definiciones de la ecuación F.4.6.1-2 — Cφ, Mm, Fm, Pm, e, βo)",
        "titulo": "Cφ=1.52 (1.6 caso especial), Mm/Fm de la Tabla F.4.6.1-1, Pm=1.0, e=2.718, βo=2.5 miembros/3.5 conexiones (1.5 caso especial).",
        "texto": (
            "Donde: Cφ = coeficiente de calibración = 1.52. = 1.6 para "
            "vigas con la aleta en tensión sujeta, en toda su longitud, "
            "a un tablero metálico o panel de cerramiento y con la aleta "
            "en compresión no arriostrada lateralmente. Mm = valor medio "
            "del factor de material, M, presentado en la tabla "
            "F.4.6.1-1 para el tipo de componente involucrado. Fm = "
            "valor medio del factor de fabricación, F, presentado en la "
            "tabla F.4.6.1-1 para el tipo de componente involucrado. "
            "Pm = valor medio del factor profesional, P, para el "
            "componente ensayado = 1.0. e = base de logaritmo natural = "
            "2.718. βo = índice de confiabilidad del objetivo = 2.5 para "
            "miembros estructurales y 3.5 para conexiones. = 1.5 para "
            "vigas con la aleta en tensión sujeta, en toda su longitud, "
            "a un tablero metálico o panel de cerramiento y con la "
            "aleta en compresión no arriostrada lateralmente."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_b_definiciones_vm_vf_cp",
        "seccion": "F.4.6.1.1(b) (Definiciones de la ecuación F.4.6.1-2 — VM, VF, factor de corrección Cp, ecuación F.4.6.1-3)",
        "titulo": "VM/VF de la Tabla F.4.6.1-1; Cp=(1+1/n)m/(m−2) para n≥4, Cp=5.7 para n=3.",
        "texto": (
            "VM = coeficiente de variación del factor de material "
            "presentado en la tabla F.4.6.1-1 para el tipo de componente "
            "involucrado. VF = coeficiente de variación del factor de "
            "fabricación presentado en la tabla F.4.6.1-1 para el tipo "
            "de componente involucrado. Cp = factor de corrección = "
            "(1+1/n)m/(m−2) para n ≥ 4 (F.4.6.1-3). = 5.7 para n = 3."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_b_definiciones_n_m_vp_vq_rn",
        "seccion": "F.4.6.1.1(b) (Definiciones finales — n, m, Vp, VQ, Rn)",
        "titulo": "n=número de ensayos, m=n−1, Vp≥6.5%, VQ=0.21 (0.43 caso especial), Rn=valor promedio de la prueba.",
        "texto": (
            "Donde: n = número de ensayos. m = grados de libertad = "
            "n − 1. Vp = coeficiente de variación de los resultados de "
            "la prueba, no menor al 6.5%. VQ = coeficiente de variación "
            "del efecto de la carga = 0.21. = 0.43 para vigas con la "
            "aleta en tensión sujeta, en toda su longitud, a un tablero "
            "metálico o panel de cerramiento y con la aleta en "
            "compresión no arriostrada lateralmente. Rn = valor promedio "
            "de todos los resultados de la prueba."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_notas_datos_estadisticos_distorsion",
        "seccion": "F.4.6.1.1 (Notas — otros datos estadísticos, aceros no listados, distorsiones)",
        "titulo": "Se permiten datos estadísticos alternativos documentados; para distorsiones que interfieren, φ=1.0 y factor de carga muerta=1.0.",
        "texto": (
            "Los valores registrados en la tabla F.4.6.1-1 no excluirán "
            "la utilización de otros datos estadísticos documentados si "
            "estos últimos son establecidos a partir de suficientes "
            "resultados sobre las propiedades del material y su "
            "fabricación. Para aceros que no estén listados en la "
            "sección F.4.1.2.1, los valores Mm y Vm serán determinados "
            "por análisis estadístico de los materiales usados. Cuando "
            "algunas distorsiones interfieren con el adecuado "
            "funcionamiento del espécimen en su uso real, los efectos de "
            "la carga basados en la combinación de carga crítica y la "
            "incidencia de la distorsión aceptable también deben "
            "satisfacer la ecuación F.4.6.1-1, excepto que el factor de "
            "resistencia φ se tomará como la unidad y el factor de carga "
            "para la carga muerta se tomará como 1.0."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_1_c_propiedades_mecanicas_lamina",
        "seccion": "F.4.6.1.1(c) (Propiedades mecánicas de la lámina — ajuste de resultados)",
        "titulo": "Propiedades de muestras representativas del ensayo, no del proveedor; ajuste al fluencia mínimo especificado si el real es mayor.",
        "texto": (
            "(c) Las propiedades mecánicas de la lámina de acero se "
            "determinarán con base en muestras representativas del "
            "material tomado del espécimen de prueba o la lámina plana "
            "usada para formar el espécimen de prueba. Las propiedades "
            "mecánicas reportadas por el proveedor del acero no se "
            "usarán en la evaluación de los resultados del ensayo. Si el "
            "esfuerzo de fluencia del acero del cual se forman las "
            "secciones ensayadas es mayor que el valor especificado, los "
            "resultados de la prueba se deberán disminuir al esfuerzo de "
            "fluencia mínimo especificado del acero que el fabricante "
            "pretende utilizar. Los resultados de la prueba no se "
            "aumentarán si el esfuerzo de fluencia del espécimen de "
            "prueba es menor que el esfuerzo de fluencia mínimo "
            "especificado. Deben hacerse ajustes similares con base en "
            "la resistencia última en aquellos casos donde ésta sea el "
            "factor crítico. Deben considerarse también las variaciones "
            "que puedan presentarse entre el espesor de diseño y el "
            "espesor de los especímenes usados en las pruebas."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_tabla_1_rigidizadores_tension_flexion",
        "seccion": "Tabla F.4.6.1-1 (Datos estadísticos Mm/Vm/Fm/VF — rigidizadores, miembros a tensión, miembros a flexión)",
        "titulo": "Rigidizadores transversales/cortante, miembros a tensión, y flexión (resistencia, pandeo LT, cortante, arrugamiento, combinados) — todos Mm≈1.00-1.10, Vm/VF 0.05-0.10.",
        "texto": (
            "Tabla F.4.6.1-1 — Datos estadísticos para la determinación "
            "del factor de resistencia (Mm, Vm, Fm, VF). Rigidizadores "
            "transversales: 1.10, 0.10, 1.00, 0.05. Rigidizadores de "
            "cortante: 1.00, 0.06, 1.00, 0.05. Miembros a tensión: 1.10, "
            "0.10, 1.00, 0.05. Miembros a flexión — Resistencia a la "
            "flexión: 1.10, 0.10, 1.00, 0.05. Resistencia al pandeo "
            "lateral torsional: 1.00, 0.06, 1.00, 0.05. Una aleta sujeta "
            "en toda su longitud a un panel o tablero: 1.10, 0.10, 1.00, "
            "0.05. Resistencia a cortante: 1.10, 0.10, 1.00, 0.05. "
            "Flexión y cortante combinados: 1.10, 0.10, 1.00, 0.05. "
            "Resistencia a arrugamiento del alma: 1.10, 0.10, 1.00, "
            "0.05. Arrugamiento del alma y flexión combinados: 1.10, "
            "0.10, 1.00, 0.05. Miembros en compresión cargados "
            "concéntricamente: 1.10, 0.10, 1.00, 0.05. Carga axial y "
            "flexión combinados: 1.05, 0.10, 1.00, 0.05."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_tabla_1_tubulares_parales_soldadas",
        "seccion": "Tabla F.4.6.1-1 (continuación — miembros tubulares cilíndricos, parales de muro, conexiones soldadas)",
        "titulo": "Miembros tubulares y parales de muro Mm≈1.05-1.10; conexiones soldadas (arco, filete, ranura, resistencia) Mm=1.10, VF 0.10-0.15 según falla de placa.",
        "texto": (
            "Tabla F.4.6.1-1 (continuación). Miembros tubulares "
            "cilíndricos — Resistencia a flexión: 1.10, 0.10, 1.00, "
            "0.05. Compresión axial: 1.10, 0.10, 1.00, 0.05. Parales de "
            "muros y ensambles de paneles de muros — Parales de muro en "
            "compresión: 1.10, 0.10, 1.00, 0.05. Parales de muro en "
            "flexión: 1.10, 0.10, 1.00, 0.05. Parales de muro con carga "
            "axial y flexión combinados: 1.05, 0.10, 1.00, 0.05. "
            "Miembros estructurales no listados en esta tabla: 1.00, "
            "0.10, 1.00, 0.05. Conexiones soldadas — Puntos de soldadura "
            "de arco: cortante 1.10/0.10/1.00/0.10, tensión última "
            "1.10/0.10/1.00/0.10, falla de placas 1.10/0.08/1.00/0.15. "
            "Cordones de soldadura de arco: cortante 1.10/0.10/1.00/0.10, "
            "desgarramiento de placa 1.10/0.10/1.00/0.10. Soldaduras de "
            "filete: cortante 1.10/0.10/1.00/0.10, falla de placas "
            "1.10/0.08/1.00/0.15. Soldaduras de ranura abocinada: "
            "cortante 1.10/0.10/1.00/0.10, falla de placas "
            "1.10/0.08/1.00/0.15. Soldaduras por resistencia: 1.10, "
            "0.10, 1.00, 0.10."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_1_tabla_1_pernos_tornillos",
        "seccion": "Tabla F.4.6.1-1 (continuación — conexiones con pernos y conexiones atornilladas)",
        "titulo": "Pernos: Mm=1.10, VF=0.05 (todas las categorías); tornillos: Mm=1.10, VF=0.10-0.15 según categoría; no listadas VF=0.15.",
        "texto": (
            "Tabla F.4.6.1-1 (continuación). Conexiones con pernos — "
            "Resistencia a cortante del perno: 1.10, 0.08, 1.00, 0.05. "
            "Resistencia última a tensión del perno: 1.10, 0.08, 1.00, "
            "0.05. Mínimo espaciamiento y distancia al borde: 1.10, "
            "0.08, 1.00, 0.05. Resistencia a la tensión en la sección "
            "neta: 1.10, 0.08, 1.00, 0.05. Resistencia al aplastamiento: "
            "1.10, 0.08, 1.00, 0.05. Conexiones atornilladas — "
            "Resistencia a cortante del tornillo: 1.10, 0.10, 1.00, "
            "0.10. Resistencia última a tensión del tornillo: 1.10, "
            "0.10, 1.00, 0.10. Mínimo espaciamiento y distancia al "
            "borde: 1.10, 0.10, 1.00, 0.10. Resistencia a tensión en la "
            "sección neta: 1.10, 0.10, 1.00, 0.10. Resistencia ante "
            "inclinación y aplastamiento: 1.10, 0.08, 1.00, 0.05. "
            "Desgarramiento del tornillo: 1.10, 0.10, 1.00, 0.10. "
            "Desgarramiento del material en contacto con la cabeza del "
            "tornillo o la arandela: 1.10, 0.10, 1.00, 0.10. Cortante y "
            "fuerzas de desgarramiento del material en contacto con la "
            "cabeza o arandela combinados: 1.10, 0.10, 1.00, 0.10. "
            "Conexiones no listadas en esta tabla: 1.10, 0.10, 1.00, "
            "0.15."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_2_ensayos_confirmacion",
        "seccion": "F.4.6.2 (Ensayos de confirmación del comportamiento estructural)",
        "titulo": "Se permiten ensayos de confirmación para demostrar que la resistencia real no es menor a Rn calculada según el Reglamento.",
        "texto": (
            "F.4.6.2 — ENSAYOS DE CONFIRMACIÓN DEL COMPORTAMIENTO "
            "ESTRUCTURAL — Para miembros estructurales, conexiones y "
            "conjuntos para los cuales la resistencia nominal se calcula "
            "de acuerdo con las disposiciones de este Reglamento o sus "
            "referencias específicas, se permitirá la realización de "
            "ensayos de confirmación para demostrar que la resistencia "
            "no es menor a la resistencia nominal, Rn, especificada en "
            "este Reglamento o sus referencias específicas para el tipo "
            "de comportamiento en estudio."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_3_1_seccion_completa_ab",
        "seccion": "F.4.6.3.1 (Ensayos de propiedades mecánicas — sección completa, casos (a) y (b))",
        "titulo": "Tensión vía NTC 3353 (ASTM A370-05); fluencia a compresión con especímenes cortos, diagrama autográfico o paralela al 0.2%.",
        "texto": (
            "F.4.6.3 — ENSAYOS PARA DETERMINACIÓN DE LAS PROPIEDADES "
            "MECÁNICAS. F.4.6.3.1 — Sección completa — Los ensayos para "
            "la determinación de las propiedades mecánicas de las "
            "secciones completas a ser utilizadas en el numeral "
            "F.4.1.6.2 serán realizados de acuerdo con lo descrito a "
            "continuación: (a) Los procedimientos de la prueba a tensión "
            "deben estar de acuerdo con la norma NTC 3353 (ASTM A370-05). "
            "(b) Las determinaciones del esfuerzo de fluencia a "
            "compresión se harán por medio de ensayos de compresión "
            "sobre especímenes cortos de la sección completa. El "
            "esfuerzo de fluencia a compresión se tomará como el menor "
            "valor de la resistencia máxima a compresión dividida por el "
            "área de la sección transversal o el esfuerzo definido por "
            "alguno de los dos siguientes métodos: (1) Para aceros con "
            "fluencia bien definida el esfuerzo de fluencia se determina "
            "por el método del diagrama autográfico o por el método de "
            "deformación total bajo cargas. (2) Para aceros con fluencia "
            "gradual, el esfuerzo se determina por el método de "
            "deformación bajo carga o por el método de la paralela al "
            "0.2%. Cuando se utilice el método de deformación total bajo "
            "carga, el esfuerzo de fluencia determinado no debe tener "
            "una diferencia mayor al 5% con respecto al esfuerzo de "
            "fluencia determinado por el método de la paralela al 0.2%. "
            "Para mayor información sobre el ensayo de especímenes "
            "cortos remitirse al documento AISI S902."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_3_1_seccion_completa_c",
        "seccion": "F.4.6.3.1 (Sección completa, caso (c) — fluencia a flexión)",
        "titulo": "Fluencia a flexión determinada solo sobre aletas, espécimen con ρ=1.",
        "texto": (
            "(c) Cuando el efecto principal sobre el miembro corresponda "
            "a esfuerzos de flexión para cargas de servicio, el esfuerzo "
            "de fluencia se determinará sólo para las aletas. Para la "
            "determinación de tal esfuerzo de fluencia cada espécimen "
            "consistirá de una aleta completa, más una porción del alma "
            "con una relación de ancho plano tal que el valor de ρ para "
            "el espécimen sea igual a la unidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_3_1_seccion_completa_de",
        "seccion": "F.4.6.3.1 (Sección completa, casos (d) y (e))",
        "titulo": "Un ensayo de sección completa por rollo madre; opción del fabricante para aprobación de rutina con demostración de confiabilidad.",
        "texto": (
            "(d) Para propósitos de aceptación y control debe hacerse un "
            "ensayo de sección completa por cada rollo madre. (e) Se "
            "permitirá, como opción del fabricante, el uso de ensayos, "
            "ya sean de tensión o compresión, para aprobación de rutina "
            "y propósitos de control, siempre y cuando el fabricante "
            "demuestre que tales ensayos indican de manera confiable el "
            "esfuerzo de fluencia de la sección cuando está sujeta a la "
            "clase de esfuerzo bajo el cual va a ser utilizado el "
            "miembro."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_3_2_elementos_planos",
        "seccion": "F.4.6.3.2 (Elementos planos de secciones formadas — esfuerzo de fluencia de partes planas Fyf)",
        "titulo": "Fyf = promedio ponderado de fluencia de muestras longitudinales de partes planas, ajustado si el real virgen excede el mínimo especificado.",
        "texto": (
            "F.4.6.3.2 — Elementos planos de secciones formadas — Los "
            "ensayos para la determinación de las propiedades mecánicas "
            "de elementos planos de secciones formadas y las "
            "propiedades mecánicas representativas del acero virgen a "
            "ser usadas en la sección F.4.1.6.2 serán realizados de "
            "acuerdo con esta sección. El esfuerzo de fluencia de partes "
            "planas, Fyf, se establecerá por medio de un promedio "
            "ponderado de los esfuerzos de fluencia de muestras para "
            "ensayo de tensión estándar, tomadas longitudinalmente de "
            "las porciones planas de un miembro representativo formado "
            "en frío. El promedio ponderado será la suma de los "
            "productos del esfuerzo de fluencia promedio para cada "
            "porción plana multiplicado por el área de la sección "
            "transversal, dividida por el área total de las partes "
            "planas en la sección transversal. El número exacto de "
            "tales muestras de ensayo dependerá de la forma del miembro. "
            "En la sección transversal debe tomarse al menos una "
            "muestra de la mitad de cada parte plana. Si el esfuerzo "
            "real de fluencia virgen excede el esfuerzo de fluencia "
            "mínimo especificado, el esfuerzo de fluencia de las partes "
            "planas, Fyf, será ajustado multiplicando los valores del "
            "ensayo por la relación del esfuerzo de fluencia mínimo "
            "especificado al esfuerzo real de fluencia virgen."
        ),
    },
    {
        "id": "NSR10-F-F_4_6_3_3_acero_virgen",
        "seccion": "F.4.6.3.3 (Acero virgen — mínimo cuatro especímenes por rollo madre)",
        "titulo": "Aplica a aceros no listados en F.4.1.2.1; mínimo 4 especímenes a tensión por rollo madre, tomados a un cuarto del ancho.",
        "texto": (
            "F.4.6.3.3 — Acero virgen — Las siguientes disposiciones "
            "aplicarán a aceros producidos de manera diferente a los "
            "listados en la sección F.4.1.2.1, bajo especificaciones "
            "NTC (o ASTM), y utilizados en secciones para las cuales el "
            "esfuerzo de fluencia incrementado del acero después del "
            "formado en frío se calcula a partir de las propiedades del "
            "acero virgen de acuerdo con la sección F.4.1.6.2. Para "
            "propósitos de aceptación y control, deben tomarse al menos "
            "cuatro especímenes a tensión de cada rollo madre para el "
            "establecimiento de los valores representativos del "
            "esfuerzo de fluencia a tensión virgen y la resistencia "
            "última a tensión. Las muestras de ensayo deben ser tomadas "
            "longitudinalmente a una distancia del borde externo del "
            "rollo igual a la cuarta parte del ancho."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.6 cargados. F.4.6 queda COMPLETO.")


if __name__ == "__main__":
    main()
