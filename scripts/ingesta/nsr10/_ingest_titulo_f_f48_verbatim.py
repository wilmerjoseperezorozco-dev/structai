"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.8 (ESPECIFICACIONES PARA CONSTRUCCION
DE ENTRAMADOS DE ACERO FORMADO EN FRIO, SISTEMAS DE CONSTRUCCION EN
SECO Y ENTRAMADOS DE CERCHAS) COMPLETO. Novena pieza de F.4/F.5, la
mas grande de F.4 hasta ahora (27 paginas, ~23 ecuaciones, 10+ tablas).

F.4.8.1 (Generalidades), F.4.8.2 (Materiales -- especificaciones,
espesor Tabla F.4.8.2-1, proteccion corrosion Tabla F.4.8.2-2),
F.4.8.3 (Productos -- designacion, geometria estandar Figura
F.4.8.3-1 + Tablas F.4.8.3-1 a -5 por tipo P/G/U/O/L, radio interno
de doblez Tabla F.4.8.3-6, longitud de pestana Tabla F.4.8.3-7,
perforaciones, marcacion del producto + codificacion por colores
Tabla F.4.8.3-8, tolerancias de fabricacion Tablas F.4.8.3-9/-10 +
Figuras F.4.8.3-2/-3), F.4.8.4 (Diseno -- propiedades de la seccion,
diseno de parales de muro con ecuaciones F.4.8.4-1 a -4 + Tabla
F.4.8.4-1 + Figura F.4.8.4-1 + arriostramiento, diseno de cerchas con
analisis + diseno de miembros cordones/alma + excentricidad en
uniones + diseno de cartelas ecuaciones F.4.8.4-5 a -10 + Figuras
Whitmore/paral-intermedio + diseno de conexiones + conexiones por
recorte ecuaciones F.4.8.4-11/-12 + Figura de recorte, dinteles --
tipo espalda con espalda, tipo cajon con ecuaciones F.4.8.4-13 a -15
+ Figuras F.4.8.4-5/-6, tipo L doble/sencilla con ecuaciones
F.4.8.4-16 a -23 + Figuras F.4.8.4-7/-8, conjuntos de dinteles tipo L
invertidos, instalacion de dinteles), F.4.8.5 (Estado de servicio).

Con esto F.4.8 queda COMPLETO -- y con esto TODO F.4 (F.4.1 a F.4.8)
queda completo. Solo falta F.5 (Aluminio, PDF distinto) para cerrar
el Titulo F entero.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final CON verificacion real de tokens (metodo de F.4.6/F.4.7, no el
deprecado de F.4.2) via _resplit_titulo_f_f48_por_limite_tokens.py.

Fuente: NSR-10-1083-1182.pdf (Drive id 1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi),
paginas internas F-411 a F-437 (paginas PDF 10-37), leidas visualmente
pagina por pagina, re-verificadas contra el PDF antes de transcribir.

Uso: python _ingest_titulo_f_f48_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    # ── F.4.8.1 / F.4.8.2 — Generalidades y Materiales ──────────────
    {
        "id": "NSR10-F-F_4_8_1_generalidades",
        "seccion": "F.4.8.1 (Generalidades — alcance de espesores)",
        "titulo": "Aplica a miembros estructurales y no estructurales para entramados con espesor entre 0.46mm y 3.00mm.",
        "texto": (
            "F.4.8 — ESPECIFICACIONES PARA CONSTRUCCIÓN DE ENTRAMADOS DE "
            "ACERO FORMADO EN FRÍO, SISTEMAS DE CONSTRUCCIÓN EN SECO Y "
            "ENTRAMADOS DE CERCHAS. F.4.8.1 — GENERALIDADES — Las "
            "disposiciones de esta sección son aplicables al diseño e "
            "instalación de miembros estructurales y no estructurales "
            "para entramados de acero formado en frío (especificaciones "
            "para entramados de sistemas de construcción en seco / "
            "Drywall), en los que el espesor mínimo del acero esté entre "
            "0.46 mm y 3.00 mm. Los miembros cubiertos por esta sección "
            "incluyen parales de secciones C, viguetas, canales guía, "
            "secciones en U, secciones omega, ángulos y otros miembros "
            "de comportamiento similar."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_2_1_2_materiales_especificaciones_espesor",
        "seccion": "F.4.8.2 / F.4.8.2.1 / F.4.8.2.2 (Materiales — especificaciones y espesor del acero base)",
        "titulo": "Láminas según ASTM A1003/A1003M; espesor mínimo según Tabla F.4.8.2-1.",
        "texto": (
            "F.4.8.2 — MATERIALES. F.4.8.2.1 — Especificaciones del "
            "material — Los miembros estructurales y no estructurales se "
            "deben formar en frío a partir de láminas de acero de "
            "acuerdo con los requisitos de la norma ASTM A1003/A1003M. "
            "F.4.8.2.2 — Espesor del acero base — Los miembros "
            "estructurales y no estructurales se deben formar en frío a "
            "partir de láminas de acero con el espesor mínimo listado en "
            "la tabla F.4.8.2-1."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_2_tabla1_espesores",
        "seccion": "Tabla F.4.8.2-1 (Espesores estándar — diseño y mínimo del acero base)",
        "titulo": "8 espesores estándar de 0.478/0.455mm a 3.155/2.997mm (diseño/mínimo).",
        "texto": (
            "Tabla F.4.8.2-1 — Espesores estándar (Espesor de diseño mm/"
            "pulg — Espesor mínimo del acero base mm/pulg). "
            "0.478/0.0188 — 0.455/0.0179. 0.719/0.0283 — 0.683/0.0269. "
            "0.792/0.0312 — 0.752/0.0296. 0.879/0.0346 — 0.836/0.0329. "
            "1.146/0.0451 — 1.087/0.0428. 1.438/0.0566 — 1.367/0.0538. "
            "1.811/0.0713 — 1.720/0.0677. 2.583/0.1017 — 2.454/0.0966. "
            "3.155/0.1242 — 2.997/0.1180."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_2_3_tabla2_proteccion_corrosion",
        "seccion": "F.4.8.2.3 (Protección contra corrosión — Tabla F.4.8.2-2)",
        "titulo": "Recubrimiento mínimo G60/AZ50 (Tipo H/L) o G40/AZ50 (Tipo NS), NTC 4011/4015.",
        "texto": (
            "F.4.8.2.3 — Protección contra corrosión — Los miembros "
            "estructurales y no estructurales deben cumplir con los "
            "requisitos mínimos de recubrimiento metálico listados en la "
            "tabla F.4.8.2-2 (masa de recubrimiento por unidad de área). "
            "Se permite el uso de recubrimientos alternativos si se "
            "demuestra su equivalencia. Tabla F.4.8.2-2 — Requerimientos "
            "mínimos de recubrimientos metálicos: Tipo H y Tipo L: "
            "G60 [Z180] o AZ50 [AZM150]. Tipo NS: G40 [Z120] o AZ50 "
            "[AZM150]. Láminas de acero recubiertas en zinc de acuerdo "
            "con la especificación NTC 4011 (ASTM A653/A653M); láminas "
            "de acero recubiertas con aleación 55% aluminio-zinc de "
            "acuerdo con la especificación NTC 4015 (ASTM A792/A792M)."
        ),
    },
    # ── F.4.8.3 — Productos ──────────────────────────────────────────
    {
        "id": "NSR10-F-F_4_8_3_1_designacion_producto",
        "seccion": "F.4.8.3 / F.4.8.3.1 (Productos — designación del producto)",
        "titulo": "Nomenclatura de 4 partes: altura del alma + letra de estilo (P/G/U/O/L) + ancho de aleta + espesor.",
        "texto": (
            "F.4.8.3 — PRODUCTOS. F.4.8.3.1 — Designación del producto — "
            "Para referenciar los miembros estructurales y no "
            "estructurales, debe utilizarse una nomenclatura de cuatro "
            "partes, que identifique el tamaño (tanto altura del alma "
            "como ancho de aleta), estilo, y espesor, de acuerdo a los "
            "siguientes códigos secuenciales: Un primer número de 3 ó 4 "
            "dígitos indicando la altura del alma del miembro en "
            "milímetros, seguido de una letra que indica: P = miembro de "
            "un entramado, paral o vigueta, con pestañas. G = sección "
            "canal guía. U = sección canal o paral de un entramado sin "
            "pestañas. O = sección omega. L = sección en ángulo. Un "
            "tercer número de 3 ó 4 dígitos que indica el ancho de aleta "
            "en milímetros, seguido por un guión, y un último número "
            "indicando el espesor en milímetros. Cuando se utilicen "
            "miembros para aplicaciones estructurales, debe "
            "especificarse el grado (resistencia) del material en todos "
            "los documentos y planos."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_2_geometria_estandar",
        "seccion": "F.4.8.3.2 (Geometría estándar — Figura F.4.8.3-1)",
        "titulo": "5 tipos de perfil: Paral/Vigueta (P) con pestaña, Canal Guía (G), Canal U, Canal Omega (O), Ángulo (L).",
        "texto": (
            "F.4.8.3.2 — Geometría estándar — La geometría estándar para "
            "miembros estructurales y no estructurales se muestra en la "
            "figura F.4.8.3-1 y puede corresponder a cualquier "
            "combinación de las dimensiones básicas listadas en las "
            "tablas F.4.8.3-1 a F.4.8.3-5, dependiendo del tipo de "
            "miembro. Figura F.4.8.3-1 — Miembros típicos para "
            "entramados de lámina formada en frío: Paral o Vigueta (P) — "
            "sección C con ancho del ala, altura del alma, longitud de "
            "la pestaña y radio interno de doblez. Canal Guía (G) — "
            "ancho del ala y altura del alma. Canal en U — ancho del ala "
            "y altura del alma, sin pestañas. Canal Omega (O) — ancho "
            "del ala y altura del alma, con 12.7 mm (1/2\") en la base. "
            "Ángulo (L) — anchos de aleta \"A\" y \"B\"."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_tabla1_dimensiones_P",
        "seccion": "Tabla F.4.8.3-1 (Dimensiones estándar para parales y viguetas en sección C — P)",
        "titulo": "Altura del alma 41.3-356mm (10 valores), ancho de aleta 31.8-88.9mm (7 valores).",
        "texto": (
            "Tabla F.4.8.3-1 — Dimensiones estándar para parales y "
            "viguetas en sección C (P). Altura del alma (mm/pulg): "
            "41.3/1-5/8, 63.5/2-1/2, 88.9/3-1/2, 92.1/3-5/8, 102/4, "
            "140/5-1/2, 152/6, 203/8, 254/10, 356/14. Ancho de aleta "
            "(mm/pulg): 31.8/1-1/4, 34.9/1-3/8, 41.3/1-5/8, 50.8/2, "
            "63.5/2-1/2, 76.2/3, 88.9/3-1/2."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_tabla2_3_dimensiones_GU",
        "seccion": "Tablas F.4.8.3-2 y F.4.8.3-3 (Dimensiones estándar para canales guía G y secciones U)",
        "titulo": "Canal guía (G): altura 41.3-356mm, ancho aleta 31.8-76.2mm. Sección U: altura 19.1-63.5mm, ancho aleta 12.7-19.1mm.",
        "texto": (
            "Tabla F.4.8.3-2 — Dimensiones estándar para canales guía "
            "(G). Altura del alma (mm/pulg): 41.3/1-5/8, 63.5/2-1/2, "
            "88.9/3-1/2, 92.1/3-5/8, 102/4, 140/5-1/2, 152/6, 203/8, "
            "254/10, 356/14. Ancho de aleta (mm/pulg): 31.8/1-1/4, "
            "50.8/2, 63.5/2-1/2, 76.2/3. Tabla F.4.8.3-3 — Dimensiones "
            "estándar para secciones U (U). Altura del alma (mm/pulg): "
            "19.1/3/4, 38.1/1-1/2, 50.8/2, 63.5/2-1/2. Ancho de aleta "
            "(mm/pulg): 12.7/1/2, 19.1/3/4."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_tabla4_5_dimensiones_OL",
        "seccion": "Tablas F.4.8.3-4 y F.4.8.3-5 (Dimensiones estándar para perfiles omega O y ángulos L)",
        "titulo": "Perfil omega (O): altura 22.2-38.1mm, ancho aleta 31.8mm. Ángulo (L): aletas A y B, 15.9-76.2mm.",
        "texto": (
            "Tabla F.4.8.3-4 — Dimensiones estándar para perfiles omega "
            "(O). Altura del alma (mm/pulg): 22.2/7/8, 38.1/1-1/2. Ancho "
            "de aleta (mm/pulg): 31.8/1-1/4. Tabla F.4.8.3-5 — "
            "Dimensiones estándar para ángulos (L). Ancho de aleta \"A\" "
            "y ancho de aleta \"B\" (mm/pulg, ambos): 15.9/5/8, "
            "22.2/7/8, 34.9/1-3/8, 38.1/1-1/2, 50.8/2, 76.2/3."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_3_radio_doblez_intro",
        "seccion": "F.4.8.3.3 (Radio interno de doblez — remisión a Tabla F.4.8.3-6)",
        "titulo": "El radio interno de doblez debe cumplir la Tabla F.4.8.3-6.",
        "texto": (
            "F.4.8.3.3 — Radio interno de doblez — El tamaño del radio "
            "interno de doblez utilizado para el diseño debe cumplir con "
            "los requisitos mostrados en la tabla F.4.8.3-6."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_tabla6_radio_doblez",
        "seccion": "Tabla F.4.8.3-6 (Radio interno de doblez para diseño)",
        "titulo": "8 pares espesor de diseño / radio interno de doblez, de 0.478mm→2.141mm a 3.155mm→4.732mm.",
        "texto": (
            "Tabla F.4.8.3-6 — Radio interno de doblez para diseño "
            "(Espesor de diseño mm(pulg) — Radio interno de doblez mm/"
            "pulg): 0.478(0.0188) — 2.141/0.0843. 0.719(0.0283) — "
            "2.022/0.0796. 0.792(0.0312) — 1.984/0.0781. 0.879(0.0346) — "
            "1.941/0.0764. 1.146(0.0451) — 1.808/0.0712. 1.438(0.0566) — "
            "2.156/0.0849. 1.811(0.0713) — 2.715/0.1069. 2.583(0.1017) "
            "— 3.874/0.1525. 3.155(0.1242) — 4.732/0.1863."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_4_longitud_pestana_tabla7",
        "seccion": "F.4.8.3.4 (Longitud de la pestaña — Tabla F.4.8.3-7)",
        "titulo": "Longitud de pestaña relacionada con ancho de aleta, de 4.8mm (P31.8) a 25.4mm (P88.9).",
        "texto": (
            "F.4.8.3.4 — Longitud de la pestaña — La longitud de la "
            "pestaña en un miembro estructural o no estructural, paral o "
            "vigueta, en sección C debe estar relacionada con el ancho "
            "de aleta, tal como se muestra en la tabla F.4.8.3-7. Tabla "
            "F.4.8.3-7 — Longitud de diseño de la pestaña para parales y "
            "viguetas en secciones C (Sección — Ancho de aleta mm/pulg — "
            "Longitud de diseño de la pestaña mm/pulg): P31.8 — "
            "31.8/1-1/4 — 4.8/3/16. P34.9 — 34.9/1-3/8 — 9.5/3/8. "
            "P41.3 — 41.3/1-5/8 — 12.7/1/2. P50.8 — 50.8/2 — 15.9/5/8. "
            "P63.5 — 63.5/2-1/2 — 15.9/5/8. P76.2 — 76.2/3 — 15.9/5/8. "
            "P88.9 — 88.9/3-1/2 — 25.4/1."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_5_perforaciones",
        "seccion": "F.4.8.3.5 (Perforaciones — 5 condiciones)",
        "titulo": "Espaciamiento mínimo 600mm, ancho máximo 63.5mm, longitud máxima 114mm, distancia al extremo mínima 305mm.",
        "texto": (
            "F.4.8.3.5 — Perforaciones — Las perforaciones realizadas "
            "por el fabricante deben cumplir con las siguientes "
            "condiciones, a menos que el fabricante especifique otras "
            "distintas: (1) Las perforaciones deben realizarse a lo "
            "largo del eje longitudinal del alma del miembro de "
            "entramado. (2) Las perforaciones deben tener un "
            "espaciamiento centro a centro no menor a 600 mm. (3) Las "
            "perforaciones deben tener un ancho no mayor a la mitad de "
            "la altura del miembro ó 63.5 mm, el que sea menor. (4) Las "
            "perforaciones deben tener una longitud no mayor a 114 mm. "
            "(5) La distancia desde el centro de la última perforación "
            "hasta el extremo final del miembro estructural no debe ser "
            "menor a 305 mm, a menos que se especifique algo diferente. "
            "Se permite cualquier configuración o combinación de "
            "perforaciones que se ajusten a las limitaciones, en anchos "
            "y longitud, anteriormente expuestas."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_6_marcacion_producto",
        "seccion": "F.4.8.3.6 (Marcación del producto — miembros estructurales y no estructurales)",
        "titulo": "Marcación mínima: fabricante, espesor, fluencia (salvo Grado 33), recubrimiento (salvo G60/G40).",
        "texto": (
            "F.4.8.3.6 — Marcación del producto. F.4.8.3.6.1 — Miembros "
            "estructurales — Los miembros estructurales deben ser "
            "marcados de manera legible con la siguiente información "
            "mínima: (1) Fabricante (Nombre, logotipo o iniciales). "
            "(2) Espesor del acero base. (3) Esfuerzo mínimo de fluencia "
            "(no es necesario si es Grado 33 [230 MPa]). (4) "
            "Recubrimiento (no es necesario si es G60 [Z180]). F.4.8.3.6.2 "
            "— Miembros no estructurales — Los miembros no estructurales "
            "deben ser marcados de manera legible con la siguiente "
            "información mínima: (1) Fabricante (Nombre, logotipo o "
            "iniciales). (2) Espesor del acero base. (3) Esfuerzo mínimo "
            "de fluencia (no es necesario si es Grado 33 [230 MPa]). "
            "(4) Recubrimiento (no es necesario si es G40 [Z120])."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_6_3_tabla8_codificacion_colores",
        "seccion": "F.4.8.3.6.3 (Codificación por colores — Tabla F.4.8.3-8)",
        "titulo": "8 colores según espesor de diseño, de Ninguno (0.478mm) a Azul (3.155mm).",
        "texto": (
            "F.4.8.3.6.3 — Codificación por colores — Cuando se utiliza "
            "una codificación por colores para miembros o paquetes de "
            "miembros similares debe utilizarse la clasificación "
            "presentada en la tabla F.4.8.3-8. Tabla F.4.8.3-8 — "
            "Codificación estándar por colores (Espesor de diseño mm — "
            "Color): 0.478 — Ninguno. 0.719 — Negro. 0.792 — Rosado. "
            "0.879 — Blanco. 1.146 — Amarillo. 1.438 — Verde. "
            "1.811 — Naranja. 2.583 — Rojo. 3.155 — Azul."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_7_tolerancias_estructurales_tabla9",
        "seccion": "F.4.8.3.7 (Tolerancias de fabricación — Tabla F.4.8.3-9, miembros estructurales, Figura F.4.8.3-2)",
        "titulo": "9 dimensiones (A-I: longitud, altura, acampanado, huecos, corona, curvatura, arco, torsión) con tolerancias para parales y canales guía.",
        "texto": (
            "F.4.8.3.7 — Tolerancias de fabricación — Los miembros "
            "estructurales deben cumplir con las tolerancias de "
            "fabricación listadas en la tabla F.4.8.3-9. Los miembros no "
            "estructurales deberán cumplir con las tolerancias de "
            "fabricación listadas en la tabla F.4.8.3-10. Figura "
            "F.4.8.3-2 — Tolerancias de fabricación para miembros "
            "estructurales (ilustra las dimensiones A-I sobre secciones "
            "en perspectiva y sobre el detalle de acampanado/exceso en "
            "doblez). Tabla F.4.8.3-9 — Tolerancias de fabricación para "
            "miembros estructurales (Dimensión, Ítem revisado, Parales "
            "mm, Canales Guías mm): A Longitud: +2.38/-2.38, "
            "+12.7/-6.35. B Altura del alma: +0.79/-0.79, +0.79/-3.18. "
            "C Acampanado/Exceso en doblez: +1.59/-1.59, +0/-2.38. "
            "D Ancho a centro de hueco: +1.59/-1.59, NA. E Longitud de "
            "centro de huecos: +6.35/-6.35, NA. F Corona: +1.59/-1.59, "
            "+1.59/-1.59. G Curvatura lateral: 2.6 por m / 12.7 máx "
            "(ambos). H Arco: 2.6 por m / 12.7 máx (ambos). I Torsión "
            "(giro axial): 2.6 por m / 12.7 máx (ambos). Todas las "
            "medidas se toman a una distancia no menor de 305 mm desde "
            "el extremo; dimensión B es entre caras externas para "
            "Parales, caras internas para Canales Guía."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_3_7_tolerancias_no_estructurales_tabla10",
        "seccion": "Tabla F.4.8.3-10 (Tolerancias de fabricación para miembros no estructurales, Figura F.4.8.3-3)",
        "titulo": "Mismas 9 dimensiones que la Tabla 9, con tolerancias más amplias para miembros no estructurales.",
        "texto": (
            "Figura F.4.8.3-3 — Tolerancias de fabricación para miembros "
            "no estructurales (misma ilustración que la Figura F.4.8.3-2). "
            "Tabla F.4.8.3-10 — Tolerancias de fabricación para miembros "
            "no estructurales (Dimensión, Ítem revisado, Parales mm, "
            "Canales Guías mm): A Longitud: +3.18/-6.35, +25.4/-6.35. "
            "B Altura del alma: +0.79/-0.79, +3.18/-0. C Acampanado/"
            "Exceso en doblez: +1.59/-1.59, +0/-4.76. D Ancho a centro "
            "de hueco: +3.18/-3.18, NA. E Longitud de centro de huecos: "
            "+6.35/-6.35, NA. F Corona: +3.18/-3.18, +3.18/-3.18. "
            "G Curvatura lateral: 2.6 por m / 12.7 máx (ambos). H Arco: "
            "2.6 por m / 12.7 máx (ambos). I Torsión (giro axial): "
            "2.6 por m / 12.7 máx (ambos). Todas las medidas se toman a "
            "una distancia no menor de 305 mm desde el extremo."
        ),
    },
    # ── F.4.8.4 — Diseño ─────────────────────────────────────────────
    {
        "id": "NSR10-F-F_4_8_4_1_propiedades_seccion",
        "seccion": "F.4.8.4 / F.4.8.4.1 (Diseño — propiedades de la sección)",
        "titulo": "Determinación de resistencias según F.4.1-F.4.4; propiedades con métodos convencionales o ensayos (F.4.6).",
        "texto": (
            "F.4.8.4 — DISEÑO — La determinación de las resistencias de "
            "los miembros para sistemas de entramado estará de acuerdo "
            "con lo estipulado en los numerales F.4.1, F.4.2, F.4.3 y "
            "F.4.4 de este Reglamento, excepto cuando sea modificado en "
            "esta sección. F.4.8.4.1 — Propiedades de la sección — Para "
            "secciones C y otras secciones transversales con geometría "
            "simple (véase figura F.4.8.3-1), las propiedades se "
            "determinan de acuerdo con los métodos convencionales del "
            "diseño estructural. Estas propiedades deben basarse en las "
            "secciones transversales totales, excepto cuando se requiera "
            "el uso de una sección transversal reducida o se requiera un "
            "ancho efectivo de diseño de acuerdo con las especificaciones "
            "de los numerales F.4.2 a F.4.4 de este Reglamento. Para "
            "otras geometrías de sección transversal, las propiedades "
            "deben basarse en ensayos, de acuerdo con la sección F.4.6."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_diseno_parales_muro_intro",
        "seccion": "F.4.8.4.2 (Diseño de parales de muros — generalidades, criterios acero/tablero)",
        "titulo": "Parales diseñados completamente en acero o arriostrados por tableros idénticos a ambos lados.",
        "texto": (
            "F.4.8.4.2 — Diseño de parales de muros — Los miembros para "
            "sistemas de entramado estarán de acuerdo con lo especificado "
            "en este Reglamento. Los conjuntos con parales de muros "
            "deben estar de acuerdo con lo estipulado en este "
            "Reglamento. Los miembros deben estar en buenas condiciones. "
            "Los miembros dañados deberán reemplazarse o repararse de "
            "acuerdo con el diseño aprobado. Los parales de muros deben "
            "diseñarse con base en un diseño completamente en acero o "
            "arriostrado por los tableros. Las almas no deben tener "
            "perforaciones, o en caso de tenerlas deben estar de acuerdo "
            "con lo dispuesto en las secciones F.4.2 a F.4.5. (a) Diseño "
            "completamente en acero — Los conjuntos con parales de muro "
            "que utilicen el criterio de un comportamiento completamente "
            "en acero se deben diseñar sin tomar en cuenta el "
            "arriostramiento estructural y/o la contribución de la "
            "acción compuesta de los tableros a los que están unidos. "
            "(b) Diseño arriostrado por tableros — Los conjuntos con "
            "parales de muro que utilicen un criterio que incluya al "
            "tablero, se deben diseñar suponiendo que se instalan "
            "tableros idénticos a ambos lados del paral y están "
            "conectados a los miembros horizontales ubicados en la parte "
            "superior e inferior del muro para proveer soporte lateral y "
            "torsional al paral en el plano del muro. Los parales cuyos "
            "tableros de cerramiento laterales instalados a ambos lados "
            "no sean idénticos se deben diseñar suponiendo que el más "
            "débil de los dos tableros está sujeto a ambos lados."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_combinacion_carga_1",
        "seccion": "F.4.8.4.2 (Combinación de carga para revisión sin arriostramiento del tablero, ecuación F.4.8.4-1)",
        "titulo": "1.2D + (0.5L ó 0.2G) + 0.2W — revisión de parales sin considerar el arriostramiento por el tablero.",
        "texto": (
            "Cuando se utiliza un diseño arriostrado por tableros, los "
            "planos deben especificar el tablero como un elemento "
            "estructural. Sin embargo, se deben revisar los parales sin "
            "considerar el arriostramiento debido al tablero, para la "
            "siguiente combinación de carga: 1.2D + (0.5L ó 0.2G) + 0.2W "
            "(F.4.8.4-1). Donde: D = carga muerta. L = carga viva. "
            "G = carga de granizo. W = carga de viento."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_1_carga_axial",
        "seccion": "F.4.8.4.2.1 (Carga axial — restricción de extremos, capacidad en acero (a) y arriostrado por tableros (b))",
        "titulo": "Extremos restringidos contra rotación y desplazamiento perpendicular; longitudes efectivas según F.4.3.4/F.4.4.4.1.",
        "texto": (
            "F.4.8.4.2.1 — Carga axial — Ambos extremos del paral deben "
            "estar restringidos contra rotación alrededor del eje "
            "longitudinal del miembro, así como desplazamiento "
            "perpendicular al mismo. (a) Para parales en compresión, "
            "considerando el diseño completamente en acero, la capacidad "
            "de carga axial se define en las secciones F.4.3.4 y "
            "F.4.4.4.1. La longitud efectiva, KL, se determina por medio "
            "de un análisis adecuado y/o ensayos, o en la ausencia de "
            "éstos, Kx, Ky y Kt se deben tomar igual a la unidad. La "
            "longitud no arriostrada con respecto al eje principal, Lx, "
            "se debe tomar como la distancia entre apoyos extremos del "
            "miembro, mientras que las longitudes no arriostradas Ly y "
            "Lt se deben tomar como las distancias entre riostras. "
            "(b) Para parales en compresión, considerando el "
            "arriostramiento de los tableros, la resistencia axial se "
            "debe determinar de acuerdo con las disposiciones de esta "
            "sección. La resistencia axial se debe calcular de acuerdo "
            "con la sección F.4.3.4. La longitud no arriostrada con "
            "respecto al eje principal, Lx, se debe tomar como la "
            "distancia entre apoyos extremos del miembro. La longitud no "
            "arriostrada con respecto al eje menor, Ly, y la longitud no "
            "arriostrada para torsión, Lt, se deben tomar como el doble "
            "de la distancia entre los conectores del tablero. Los "
            "coeficientes de pandeo Kx, Ky y Kt se deben tomar igual a "
            "la unidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_tabla1_carga_axial_max",
        "seccion": "Tabla F.4.8.4-1 (Carga nominal axial máxima por capacidad de la conexión paral-tablero en yeso)",
        "titulo": "4 combinaciones de tablero de yeso (12.7/15.9mm) y tornillo (No.6/No.8), carga nominal 25.8-34.7kN.",
        "texto": (
            "Para prevenir fallas de la conexión paral-tablero, cuando se "
            "instalen tableros iguales de yeso a ambos lados del muro, "
            "con tornillos espaciados centro a centro 305 mm como "
            "máximo, la carga nominal axial máxima en el paral de muro "
            "se debe limitar a los valores dados en la tabla F.4.8.4-1. "
            "Tabla F.4.8.4-1 — Carga nominal axial máxima por capacidad "
            "de la conexión paral-tablero en yeso (Tablero en Yeso — "
            "Tamaño del tornillo — Carga nominal especificada máxima por "
            "paral): 12.7 mm — No. 6 — 25.8 kN. 12.7 mm — No. 8 — "
            "29.8 kN. 15.9 mm — No. 6 — 30.2 kN. 15.9 mm — No. 8 — "
            "34.7 kN."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_2_a_2_6_flexion_cortante_secciones_armadas",
        "seccion": "F.4.8.4.2.2 a F.4.8.4.2.6 (Flexión, cortante, carga axial+flexión, arrugamiento del alma, secciones armadas)",
        "titulo": "Flexión/cortante según F.4.3.3.1.2.1/F.4.3.3.1.4/F.4.3.3.2; arrugamiento con incremento por canal guía (F.4.8.4.2.7.2); secciones armadas F.4.4.1.",
        "texto": (
            "F.4.8.4.2.2 — Flexión — Para diseño completamente en acero "
            "se seguirán los lineamientos de la sección F.4.3.3.1.2.1 y "
            "F.4.3.3.1.4, para la determinación de la resistencia a "
            "flexión. Para diseño considerando el arriostramiento por "
            "los tableros, y desconociendo cualquier restricción "
            "rotacional provista por éstos, se utilizarán las "
            "disposiciones de la sección F.4.3.3.1.1 para la "
            "determinación de la resistencia de diseño a flexión. "
            "F.4.8.4.2.3 — Cortante — Para un diseño completamente en "
            "acero, o considerando el comportamiento compuesto con los "
            "tableros de yeso, la resistencia de diseño a cortante debe "
            "ser la definida en el numeral F.4.3.3.2. F.4.8.4.2.4 — "
            "Carga axial y flexión — Para diseño completamente en acero, "
            "o considerando el comportamiento compuesto con los "
            "tableros, la resistencia axial y la resistencia a flexión "
            "deben satisfacer las ecuaciones de interacción de la "
            "sección F.4.3.5. F.4.8.4.2.5 — Arrugamiento del alma — Para "
            "diseño completamente en acero, o diseño compuesto con los "
            "tableros, la resistencia a arrugamiento del alma del "
            "miembro, Pn, se debe determinar de acuerdo con la sección "
            "F.4.3.3.4, o Pn debe ser modificado de acuerdo con la "
            "sección F.4.8.4.2.7.2 para tomar en cuenta el incremento en "
            "la resistencia debido al canal guía. F.4.8.4.2.6 — "
            "Secciones armadas — Para diseño completamente en acero, o "
            "en conjunto con los tableros, la resistencia de diseño de "
            "secciones armadas se define en F.4.4.1. Cuando los "
            "requisitos aplicables de conexiones no se cumplan, la "
            "resistencia de diseño de las secciones armadas debe ser "
            "igual a la suma de las resistencias de diseño de los "
            "miembros individuales de la sección transversal del "
            "miembro armado."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_7_conexiones_metodos",
        "seccion": "F.4.8.4.2.7 / F.4.8.4.2.7.1 (Diseño de conexiones para parales de muro — métodos de sujeción)",
        "titulo": "Tornillos/pernos/soldaduras según F.4.5; otros sujetadores requieren ensayos (F.4.6.1).",
        "texto": (
            "F.4.8.4.2.7 — Diseño de conexiones para parales de muro. "
            "F.4.8.4.2.7.1 — Métodos de sujeción — Los tornillos, pernos "
            "y conexiones soldadas deben diseñarse de acuerdo con los "
            "requisitos del numeral F.4.5 y lo descrito en esta sección. "
            "Para conexiones con otro tipo de sujetador, la resistencia "
            "de diseño se debe determinar mediante ensayos de acuerdo "
            "con la sección F.4.6.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_7_2_a_conexion_paral_canal_ec2",
        "seccion": "F.4.8.4.2.7.2(a) (Conexión de paral en sección C a canal guía — ecuación F.4.8.4-2, aletas conectadas)",
        "titulo": "Pnst=Ct²Fy(1−CR√(R/t))(1+CN√(N/t))(1−Ch√(h/t)), φ=0.90, para muros cortina con ambas aletas conectadas.",
        "texto": (
            "F.4.8.4.2.7.2 — Conexión de paral en sección C a canal guía "
            "— La conexión del paral al canal guía debe satisfacer los "
            "requisitos de resistencia al arrugamiento del alma del "
            "paral, de acuerdo con la sección F.4.8.4.2.5, o tal como se "
            "define en esta sección. (a) Para parales de muros cortina "
            "que no sean adyacentes a las aberturas (puertas y ventanas), "
            "en los que ambas aletas del paral estén conectadas a los "
            "canales guía y el espesor del canal guía sea mayor o igual "
            "al espesor del paral, la resistencia nominal Pnst, se "
            "determina de acuerdo con la ecuación F.4.8.4-2: "
            "Pnst = Ct²Fy(1 − CR√(R/t))(1 + CN√(N/t))(1 − Ch√(h/t)) "
            "(F.4.8.4-2). Donde: C = coeficiente de arrugamiento del "
            "alma = 3.7. CR = coeficiente de radio interno de doblez = "
            "0.19. CN = coeficiente de longitud de apoyo = 0.74. "
            "Ch = coeficiente de esbeltez del alma = 0.019. R = radio "
            "interno de doblez del paral. N = longitud de apoyo del "
            "paral. h = altura de la porción plana del alma del paral, "
            "medida a lo largo de su plano. t = espesor de diseño del "
            "paral. φ = 0.90. La anterior ecuación es válida para el "
            "siguiente rango de parámetros: Tamaño del tornillo: No. 8, "
            "mínimo. Sección del paral — espesor de diseño 0.88 mm a "
            "1.96 mm, resistencia de diseño a la fluencia 228 MPa a "
            "345 MPa, altura nominal 88.9 mm a 152.4 mm. Sección del "
            "canal guía — espesor de diseño 0.88 mm a 1.96 mm, "
            "resistencia a la fluencia 228 MPa a 345 MPa."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_7_2_b_e_conexion_paral_canal_resto",
        "seccion": "F.4.8.4.2.7.2(b)-(e) (Conexión paral-canal guía — canal más delgado, y casos de abertura/sin ambas aletas)",
        "titulo": "Ecuación F.4.8.4-3 (Pnst=0.6ttwstFut) cuando el canal es más delgado; casos (c)(d)(e) remiten a F.4.3.3.4.1.",
        "texto": (
            "(b) Para parales de muro cortina que no sean adyacentes a "
            "aberturas y cuando ambas aletas del paral estén conectadas "
            "a las aletas del canal guía y el espesor del canal guía es "
            "menor que el espesor del paral, la resistencia nominal, "
            "Pnst, será el menor valor obtenido de las ecuaciones "
            "F.4.8.4-2 ó F.4.8.4-3: Pnst = 0.6·tt·wst·Fut (F.4.8.4-3). "
            "Donde: tt = espesor de diseño del canal guía en mm. "
            "wst = 20·tt + 0.56·α. α = 25.4. Fut = resistencia última a "
            "tensión del canal guía. Pnst = resistencia nominal para la "
            "conexión del paral a la canal guía cuando está sujeta a "
            "cargas transversales. φ = 0.90. Válida para: tamaño del "
            "tornillo No. 8 mínimo; sección del paral (espesor 0.88-"
            "1.96mm, fluencia 228-345MPa, altura 88.9-152.4mm); sección "
            "del canal guía (espesor 0.88-1.96mm, fluencia 228-345MPa, "
            "altura 88.9-152.4mm, ancho de aleta 31.8-60.3mm). "
            "(c) Para parales de muro cortina adyacentes a aberturas y "
            "cuando el canal guía termina en la abertura, la resistencia "
            "nominal se deberá tomar como 0.5·Pnst usando Pnst y φ de "
            "F.4.8.4.2.7.2(a) o (b) según el espesor relativo. "
            "(d) Para parales de muro cortina no adyacentes a aberturas "
            "y sin ambas aletas conectadas a las aletas de los canales "
            "guía, con espesor del canal mayor o igual al del paral, la "
            "resistencia nominal Pnst es igual a Pn, con φ según "
            "F.4.3.3.4.1. (e) Para parales de muro cortina adyacentes a "
            "aberturas y sin ambas aletas conectadas, con espesor del "
            "canal guía mayor o igual al del paral, la resistencia "
            "nominal Pnst es igual a 0.5·Pn, con φ según F.4.3.3.4.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_7_3_conexion_canal_deformaciones",
        "seccion": "F.4.8.4.2.7.3 (Conexión de canal guía sujeta a deformaciones — ecuación F.4.8.4-4, Figura F.4.8.4-1)",
        "titulo": "Pndt=wdt·t²·Fy/(4e), φ=0.55; wdt=longitud efectiva del canal guía; Figura muestra la conexión con parámetros e, D, wdt.",
        "texto": (
            "F.4.8.4.2.7.3 — Conexión de canal guía sujeta a "
            "deformaciones — Para parales de muros cortina usados en "
            "conexiones de canales guía sujetas a deformaciones, Pnst "
            "será igual a Pn, con φ tal como se determina en la sección "
            "F.4.3.3.4.1. La longitud de apoyo que debe ser usada en "
            "estos cálculos no excederá el mínimo ajuste entre el paral "
            "y el canal guía ó 25.4 mm. La resistencia nominal de un "
            "canal guía sujeta a deflexión bajo cargas transversales, y "
            "conectada a su apoyo con un espaciamiento del sujetador no "
            "mayor que el espaciamiento entre parales, se determina de "
            "acuerdo con la ecuación F.4.8.4-4: Pndt = wdt·t²·Fy/(4e) "
            "(F.4.8.4-4). Donde: wdt = longitud efectiva del canal guía "
            "= 0.11(α²)(e^0.5/t^1.5) + 5.5α ≤ S. S = espaciamiento centro "
            "a centro de parales. t = espesor de diseño del canal guía. "
            "Fy = resistencia de diseño a la fluencia. e = distancia de "
            "diseño en el extremo o de deslizamiento (distancia entre el "
            "alma del paral en su extremo y el alma del canal guía, "
            "medida perpendicularmente al alma del canal guía). "
            "α = 25.4. φ = 0.55. Válida para: sección del paral "
            "(espesor 1.14-1.81mm, fluencia 228-345MPa, altura 88.9-"
            "152.4mm, ancho de aleta 41.3-63.5mm, espaciamiento entre "
            "parales 305-610mm, longitud de apoyo del paral 19.1mm); "
            "sección del canal guía (espesor 1.14-1.81mm, fluencia "
            "228-345MPa, altura 88.9-152.4mm, ancho de aleta 50.8-"
            "76.3mm). La distancia horizontal medida desde el lado del "
            "alma del paral hasta el borde terminal del perfil guía no "
            "será menor que la mitad de la longitud efectiva del canal "
            "guía wdt. Figura F.4.8.4-1 — Conexión de Canal Guía sujeta "
            "a deformaciones: muestra el canal guía, el paral, y los "
            "parámetros wdt (longitud efectiva), e (distancia de "
            "deslizamiento), D (diámetro), θ (ángulo) y bparal (ancho "
            "del paral)."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_2_8_arriostramiento_parales",
        "seccion": "F.4.8.4.2.8 (Arriostramiento de parales de muro — riostras intermedias)",
        "titulo": "Riostra intermedia: F.4.4.3 para flexión; 2% de la fuerza de compresión para carga axial; combinación de ambos.",
        "texto": (
            "F.4.8.4.2.8 — Arriostramiento de parales de muro. "
            "F.4.8.4.2.8.1 — Diseño de riostras intermedias — Para "
            "miembros a flexión, cada riostra intermedia se debe "
            "diseñar de acuerdo con la sección F.4.4.3. Para miembros "
            "sometidos a carga axial, cada riostra intermedia se debe "
            "diseñar para el 2% de la fuerza de diseño a compresión en "
            "el miembro. Para cargas a flexión y axiales combinadas, "
            "cada riostra intermedia se debe diseñar para la fuerza "
            "combinada en la riostra determinada de acuerdo con la "
            "sección F.4.4.3 y el 2% de la fuerza de diseño a compresión "
            "en el miembro."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_diseno_cerchas_intro_analisis",
        "seccion": "F.4.8.4.3 / F.4.8.4.3.1 (Diseño de cerchas para sistemas de entramados — análisis)",
        "titulo": "Miembros cordones continuos por defecto; alma con articulaciones en extremos; se permite rigidez de nudo definida.",
        "texto": (
            "F.4.8.4.3 — Diseño de cerchas para sistemas de entramados. "
            "F.4.8.4.3.1 — Análisis — En lugar de un análisis racional "
            "para definir la flexibilidad de los nudos, se pueden hacer "
            "las siguientes suposiciones para el análisis: (1) Los "
            "miembros cordones son continuos, a menos que se supongan "
            "con articulaciones en los talones, puntos de quiebre o en "
            "empalmes en su longitud. (2) Los miembros en el alma de la "
            "cercha (diagonales y verticales) se suponen con "
            "articulaciones en los extremos. Se permite el uso de una "
            "rigidez específica en el nudo, distinta a la consideración "
            "de completa libertad al giro de una rótula, si la conexión "
            "se diseña para las fuerzas provenientes de un análisis "
            "estructural con la rigidez de nudo definida inicialmente."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_1_cordones_compresion_secciones_c",
        "seccion": "F.4.8.4.3.2 / F.4.8.4.3.2.1 (Diseño de miembros — cordones en compresión, carga axial, caso (a) secciones C)",
        "titulo": "Cordones en compresión revisados por F.4.3.4/F.4.3.3.1/F.4.3.5.2; secciones C: eje x de simetría, Cm/Kx/Ky/Kt según continuidad.",
        "texto": (
            "F.4.8.4.3.2 — Diseño de miembros. F.4.8.4.3.2.1 — Miembros "
            "cordones en compresión — Los miembros cordones en "
            "compresión se deben revisar solamente para carga axial "
            "utilizando las disposiciones de la sección F.4.3.4, sólo a "
            "flexión bajo las disposiciones de la sección F.4.3.3.1 y, "
            "carga axial y flexión combinadas, usando la sección "
            "F.4.3.5.2. F.4.8.4.3.2.1.1 — Carga axial — Para la "
            "determinación de la resistencia bajo carga axial, la "
            "longitud efectiva, KL, se debe establecer por medio de un "
            "análisis racional, ensayos, o las siguientes "
            "consideraciones de diseño, según sea apropiado: (a) Para "
            "secciones C el eje x es el eje de simetría. Lx es igual a "
            "la distancia entre los puntos de panel, y Cm se toma como "
            "0.85, a menos que se realice algún análisis para justificar "
            "un valor diferente. Cuando el miembro cordón sea continuo, "
            "al menos en un punto de panel intermedio y exista un "
            "tablero sujeto directamente al mismo, Kx se toma como "
            "0.75. En otros casos, Kx se toma igual a la unidad. Como "
            "alternativa, Lx puede tomarse como la distancia entre "
            "puntos de cambio de curvatura por flexión con Cm y Kx "
            "tomados como la unidad. Cuando el tablero esté sujeto al "
            "miembro cordón, Ly es igual a la distancia entre "
            "conectores del tablero y Ky se debe tomar como 0.75. "
            "Cuando las correas estén sujetas al miembro cordón, Ly es "
            "la distancia entre correas con Ky igual a la unidad. Lt es "
            "igual a la distancia entre puntos de panel. Cuando el "
            "cordón es continuo al menos en un punto de panel "
            "intermedio entre el talón y un punto de quiebre del cordón "
            "y cuando el tablero está sujetado directamente al cordón, "
            "Kt se toma como 0.75. En otros casos, Kt se toma como la "
            "unidad. Alternativamente, Lt puede ser la distancia entre "
            "puntos de cambio de curvatura por flexión con Kt tomado "
            "como la unidad. Donde: Cm = coeficiente de momento en los "
            "extremos, en la fórmula de interacción. Kt = factor de "
            "longitud efectiva para torsión. Kx/Ky = factor de longitud "
            "efectiva para pandeo alrededor del eje x/y. Lt/Lx/Ly = "
            "longitud no arriostrada para torsión/flexión x/flexión y "
            "del miembro en compresión."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_1_cordones_compresion_sombrero_z",
        "seccion": "F.4.8.4.3.2.1.1(b)(c) (Carga axial — secciones sombrero y secciones Z)",
        "titulo": "Sombrero: eje x de simetría, mismas reglas que C. Z: eje x fuera del plano, Lt depende de altura del cordón (≥152mm).",
        "texto": (
            "(b) Para secciones sombrero el eje x es el eje de simetría. "
            "Cuando el tablero esté sujeto al miembro cordón, Lx es "
            "igual a la distancia entre conectores del tablero y Kx se "
            "toma como 0.75. Cuando las correas estén sujetas al miembro "
            "cordón, Lx es la distancia entre correas con Kx igual a la "
            "unidad. Ly es igual a la distancia entre puntos de panel, y "
            "Cm se toma como 0.85, a menos que se realice algún análisis "
            "para justificar un valor diferente. Cuando el miembro "
            "cordón es continuo al menos en un punto de panel "
            "intermedio y cuando el tablero está sujeto directamente al "
            "mismo, Ky se toma como 0.75. De otra manera, Ky se toma "
            "como la unidad. Alternativamente, Ly puede ser igual a la "
            "distancia entre puntos de cambio de curvatura por flexión "
            "con Cm y Ky tomados como la unidad. Lt es igual a la "
            "distancia entre conectores del tablero o espaciamiento de "
            "correas. Cuando el miembro cordón sea continuo al menos en "
            "un punto de panel intermedio entre el talón y un punto de "
            "quiebre, y cuando el tablero es sujetado directamente al "
            "miembro cordón, Kt se toma como 0.75. En otros casos, Kt "
            "será tomado como la unidad. Alternativamente, Lt puede ser "
            "la distancia entre puntos de cambio de curvatura por "
            "flexión con Kt tomado como la unidad. (c) Para secciones Z "
            "el eje x está fuera del plano de la cercha. Lx es igual a "
            "la distancia entre puntos de panel, y Cm se toma como "
            "0.85, a menos que se realice algún análisis para justificar "
            "un valor diferente. Cuando el miembro cordón es continuo "
            "al menos sobre un punto de panel intermedio y cuando el "
            "tablero está directamente sujeto al mismo, Kx se toma como "
            "0.75. En otros casos, Kx se toma como la unidad. "
            "Alternativamente, Lx es igual a la distancia entre puntos "
            "de cambio de curvatura por flexión con Cm y Kx tomados "
            "como la unidad. Cuando el tablero esté sujeto al miembro "
            "cordón, Ly es igual a la distancia entre conectores del "
            "tablero y Ky se toma como 0.75. Cuando las correas estén "
            "sujetas al miembro cordón, Ly es la distancia entre correas "
            "con Ky igual a la unidad. Cuando la altura del miembro "
            "cordón sea menor a 152 mm, Lt es igual a la distancia entre "
            "conectores del tablero o el espaciamiento entre correas. "
            "Para secciones Z en las que la altura del miembro cordón "
            "sea mayor o igual a 152 mm, Lt es igual a la distancia "
            "entre puntos de panel. Cuando el miembro cordón es continuo "
            "al menos en un punto de panel intermedio entre el talón y "
            "un punto de quiebre del cordón, y cuando el tablero está "
            "directamente sujeto al miembro cordón, Kt se toma como "
            "0.75. En otros casos, Kt se toma como la unidad. "
            "Alternativamente, Lt es igual a la distancia entre puntos "
            "de cambio de curvatura por flexión con Kt tomado como la "
            "unidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_1_2_flexion",
        "seccion": "F.4.8.4.3.2.1.2 (Flexión de miembros cordones — casos (a)(b)(c))",
        "titulo": "Mn con tablero en compresión (Sc·Fy), correas (Sc·Fc), o tablero en tensión (Sc·Fc con Cb=1 en punto de panel).",
        "texto": (
            "F.4.8.4.3.2.1.2 — Flexión — Para la determinación de la "
            "resistencia a flexión, la longitud efectiva, KL, se debe "
            "establecer por medio de un análisis racional, ensayos, o "
            "las siguientes consideraciones de diseño según sea "
            "apropiado: (a) Cuando el tablero esté sujeto a la aleta en "
            "compresión el valor de Mn del miembro cordón bajo carga "
            "axial se debe tomar como Sc·Fy de acuerdo con la sección "
            "F.4.3.3.1.1. (b) Cuando las correas estén sujetas a la "
            "aleta en compresión entre puntos de panel, Mn = Sc·Fc de "
            "acuerdo con las secciones F.4.3.3.1.2.1 y F.4.3.3.1.4 con "
            "KLy y KLt para secciones C y Z, y KLx y KLt para secciones "
            "sombrero, tomadas como la distancia entre correas. "
            "(c) Cuando el tablero o correas estén sujetos a la aleta en "
            "tensión, y la aleta en compresión no esté arriostrada "
            "lateralmente, Mn se toma como Sc·Fc de acuerdo con las "
            "secciones F.4.3.3.1.2.1 y F.4.3.3.1.4. Para miembros "
            "cordones con luces continuas, Mn en la región del punto de "
            "panel se determina con KLy y KLt para secciones C y Z, y "
            "KLx y KLt para secciones sombrero, tomadas como la "
            "distancia entre el punto de panel y el punto de cambio de "
            "curvatura por flexión, con Cb tomado como la unidad. Para "
            "luces simples y continuas de miembros cordones, Mn en la "
            "región entre apoyos, se determina con la longitud efectiva "
            "tomada como la distancia entre puntos de panel y Cb se "
            "calcula de acuerdo con la sección F.4.3.3.1.2.1. Donde: "
            "Cb = coeficiente de flexión dependiente del gradiente de "
            "momento. Fc = esfuerzo crítico de pandeo. Fy = esfuerzo de "
            "fluencia usado en el diseño. Mn = resistencia nominal a "
            "flexión. Sc/Se = módulo elástico de la sección efectiva "
            "calculado con respecto a la fibra extrema en compresión "
            "para el esfuerzo Fc/Fy."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_1_3_cargas_concentradas_ec5",
        "seccion": "F.4.8.4.3.2.1.3 (Cargas concentradas sobre puntos de panel — ecuación F.4.8.4-5, interacción)",
        "titulo": "P̄/Pno + M̄x/Mnxo + R̄/Rn ≤ 1.49φ, φ=0.85, para miembros cordón sección C con cargas concentradas en punto de panel.",
        "texto": (
            "F.4.8.4.3.2.1.3 — Cargas concentradas sobre puntos de panel "
            "— Cuando un miembro cordón, conformado por una sección C, "
            "está sujeto a cargas concentradas en un punto de panel, la "
            "interacción entre la compresión axial, flexión y "
            "arrugamiento del alma se considera como sigue: "
            "P̄/Pno + M̄x/Mnxo + R̄/Rn ≤ 1.49φ (F.4.8.4-5). Donde: "
            "P̄ = resistencia axial requerida a compresión. M̄x = "
            "resistencia requerida a flexión. R̄ = resistencia requerida "
            "bajo la carga concentrada por arrugamiento. Pno = "
            "resistencia nominal axial calculada con f=Fy. Mnxo = "
            "resistencia nominal a flexión calculada con f=Fy. Rn = "
            "resistencia nominal al arrugamiento del alma bajo la "
            "condición de carga interior sobre una aleta. φ = 0.85."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_2_4_cordones_tension_alma_tension",
        "seccion": "F.4.8.4.3.2.2 / F.4.8.4.3.2.4 (Cordones en tensión; miembros del alma en tensión)",
        "titulo": "Cordones en tensión: F.4.3.2 axial, F.4.3.3.1 flexión, F.4.3.5.1 combinado. Alma en tensión: F.4.3.2, considerar excentricidad si no simétrica.",
        "texto": (
            "F.4.8.4.3.2.2 — Miembros cordones en tensión — Los miembros "
            "cordones a tensión se deben revisar para carga axial "
            "únicamente utilizando la sección F.4.3.2, para flexión "
            "únicamente utilizando la sección F.4.3.3.1, y carga axial "
            "y flexión combinadas usando la sección F.4.3.5.1. Se "
            "permite tomar la carga axial actuando en el centroide de "
            "la sección. F.4.8.4.3.2.4 — Miembros del alma en tensión "
            "(verticales y diagonales) — Los miembros del alma "
            "(diagonales y verticales) en tensión se deben revisar para "
            "carga axial únicamente utilizando las disposiciones de la "
            "sección F.4.3.2. Para miembros del alma cargados "
            "simétricamente, se permite tomar la carga axial de tensión "
            "actuando a través del centroide de la sección. Para otros "
            "miembros en tensión, no cargados simétricamente, se debe "
            "tener en cuenta la excentricidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_3_alma_compresion_ec6_7",
        "seccion": "F.4.8.4.3.2.3 (Miembros del alma en compresión — caso (a), sección C — ecuaciones F.4.8.4-6 y -7)",
        "titulo": "Interacción flexo-compresión fuera del plano: RP̄/φcPn + CmyRP̄e/φbMnyαy ≤ 1.0; R según fórmula empírica de L/r.",
        "texto": (
            "F.4.8.4.3.2.3 — Miembros del alma en compresión (verticales "
            "y diagonales) — Los miembros del alma (diagonales y "
            "verticales) en compresión se deben revisar para carga "
            "axial únicamente utilizando la sección F.4.3.4, y carga "
            "axial y flexión combinada usando la sección F.4.3.5.2, y "
            "los requisitos de esta sección, según sea aplicable: "
            "(a) Para un miembro en el alma de la cercha (vertical o "
            "diagonal) de sección C, bajo carga de compresión, sujeto en "
            "los extremos a través de su alma, espalda con espalda con "
            "el alma de un miembro cordón en sección C y que no esté "
            "sujeto a cargas aplicadas entre sus extremos, la "
            "interacción entre la carga axial a compresión y la flexión "
            "fuera de su plano se determina por medio de la siguiente "
            "ecuación de interacción: RP̄/(φcPn) + CmyRP̄e/(φbMnyαy) "
            "≤ 1.0 (F.4.8.4-6). Donde: R = −(L/r)²/173 + (L/r)/88 "
            "− 0.22 ≥ 0.6 (F.4.8.4-7). L = longitud no arriostrada del "
            "miembro del alma en compresión. r = radio de giro de la "
            "sección completa alrededor del eje menor. Pn = resistencia "
            "nominal axial basada en la sección F.4.3.4.1.1. Sólo se "
            "considera pandeo flector. e = excentricidad de la fuerza "
            "de compresión con respecto al centroide de la sección "
            "completa del miembro del alma. P, Cmy, Mny, P̄, φc, φb y αy "
            "se definen en la sección F.4.3.5.2. En el cálculo de la "
            "resistencia de diseño, las longitudes efectivas, KxLx, KyLy "
            "y KtLt se toman como la distancia entre los centros de los "
            "patrones de conexiones de los extremos de miembros."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_3_alma_compresion_bc",
        "seccion": "F.4.8.4.3.2.3(b)(c) (Miembros del alma en compresión — otros miembros, cargados concéntricamente y no concéntricamente)",
        "titulo": "Otros miembros de alma: se permite carga a través del centroide si cargados concéntricamente; considerar excentricidad si no.",
        "texto": (
            "(b) Para otros miembros del alma bajo cargas de compresión, "
            "cargados concéntricamente, se permite tomar la carga axial "
            "actuando a través del centroide de la sección. (c) Para "
            "otros miembros del alma bajo carga de compresión, no "
            "cargados concéntricamente, se deben tener en cuenta la "
            "excentricidad."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_2_5_excentricidad_uniones",
        "seccion": "F.4.8.4.3.2.5 (Excentricidad en uniones (juntas) — revisión de cortante y momento sobre el miembro cordón)",
        "titulo": "Análisis de nodos múltiples o nudos sencillos; traslapo ≥75% del alma revisa F.4.3.3-55, <75% revisa F.4.3.3-54.",
        "texto": (
            "F.4.8.4.3.2.5 — Excentricidad en uniones (juntas) — Se debe "
            "realizar un análisis utilizando nodos múltiples o un "
            "análisis usando nudos sencillos incluyendo las apropiadas "
            "consideraciones para los efectos de excentricidad. El "
            "cálculo del cortante y el momento para el miembro cordón "
            "sobre las uniones debe incluir las siguientes "
            "consideraciones: (a) Cuando la longitud de traslapo del "
            "miembro del alma sea más grande o igual al 75% de la "
            "altura del miembro cordón, este se debe revisar a flexión "
            "y cortante combinado de acuerdo con la ecuación "
            "F.4.3.3-55. Para cerchas en secciones C en las que se "
            "utilicen tornillos como conectores, debe colocarse un "
            "mínimo de cuatro unidades en la conexión del miembro alma "
            "(vertical o diagonal) al miembro cordón y deben "
            "distribuirse de manera uniforme en el área traslapada. "
            "(b) Cuando la longitud de traslapo del miembro del alma es "
            "menor al 75% de la altura del miembro cordón, este se debe "
            "revisar a flexión y cortante combinado de acuerdo con la "
            "ecuación F.4.3.3-54. A lo largo de la longitud del miembro "
            "cordón, en el punto medio entre la intersección con "
            "miembros del alma en una junta, se debe revisar el "
            "cortante de acuerdo con la sección F.4.3.3.2. El "
            "coeficiente de pandeo por cortante se determina con "
            "cualquiera de las ecuaciones F.4.3.3-49 ó F.4.3.3-50 con "
            "\"a\" tomada como el valor más pequeño de la distancia "
            "entre grupos de sujetadores, o centro a centro de los "
            "miembros del alma."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_3_diseno_cartelas_ec8_10",
        "seccion": "F.4.8.4.3.3 (Diseño de cartelas — ecuaciones F.4.8.4-8, -9 y -10)",
        "titulo": "Pn=Rg·b·t·Fy, φc=0.60; Rg según relación Wmin/Leff (0.47·Wmin/Leff+0.3 si ≤1.5, ó 1.0 si >1.5).",
        "texto": (
            "F.4.8.4.3.3 — Diseño de cartelas — La resistencia nominal "
            "bajo carga axial a compresión, Pn, de cartelas planas y "
            "delgadas se calcula como sigue: Pn = Rg·b·t·Fy (F.4.8.4-8). "
            "Para Wmin/Leff ≤ 1.5: Rg = (0.47·Wmin/Leff + 0.3) "
            "(F.4.8.4-9). Para Wmin/Leff > 1.5: Rg = 1.0 (F.4.8.4-10). "
            "Donde: b = ancho efectivo determinado de acuerdo con la "
            "sección F.4.2.2.1, con f=Fy, k=4 y w=Wmin. Fy = resistencia "
            "a la fluencia mínima especificada. t = espesor de diseño "
            "de la cartela. φc = 0.60."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_3_whitmore_parametros",
        "seccion": "F.4.8.4.3.3 (Figura F.4.8.4-1 Whitmore, Wmin/Leff, parámetros válidos, patrón de sujetadores)",
        "titulo": "Wmin = menor entre ancho real de cartela y sección Whitmore (30° a cada lado); Leff = distancia entre últimas filas de sujetadores.",
        "texto": (
            "Figura F.4.8.4-1 — Ancho de placa Whitmore: muestra la "
            "primera fila de sujetadores, la sección Whitmore a 30°, y "
            "el miembro de cercha. Wmin es el menor valor del ancho de "
            "cartela real y la sección Whitmore, la cual se determina "
            "utilizando un ángulo de distribución de 30° a ambos lados "
            "de la conexión, comenzando en la primera fila de "
            "sujetadores en la conexión. Leff se toma como la longitud "
            "promedio entre las últimas filas de sujetadores de miembros "
            "de cercha adyacentes en la conexión. Las anteriores "
            "ecuaciones son válidas para los siguientes parámetros: "
            "Espesor de diseño de placa de cartela: 1.438 mm a 2.583 mm. "
            "Esfuerzo de fluencia de diseño de la placa de cartela: "
            "228 MPa a 345 MPa. Relación Wmin/Leff: 0.8 a 6.0. Patrón de "
            "sujetadores de cartela a miembro cordón: mínimo dos filas "
            "con dos sujetadores por fila."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_3_tension_cartelas_conexiones",
        "seccion": "F.4.8.4.3.3-.4.3.4 (Resistencia a tensión de cartelas; diseño de conexiones — métodos de sujeción, conexiones por recorte)",
        "titulo": "Tensión axial de cartelas según F.4.3.2; conexiones aprobadas por el diseñador; se permite recorte en talones/puntos de quiebre.",
        "texto": (
            "La resistencia nominal a tensión axial de placas planas y "
            "delgadas de cartelas se calcula de acuerdo con los "
            "requisitos de la sección F.4.3.2. F.4.8.4.3.4 — Diseño de "
            "conexiones. F.4.8.4.3.4.1 — Métodos de sujeción o fijación "
            "— Los sistemas de sujeción o fijación deben ser aprobados "
            "por el diseñador de la cercha. Los tornillos, pernos y "
            "conexiones soldadas se deben diseñar de acuerdo con las "
            "disposiciones de este Reglamento. Para conexiones que "
            "utilicen otro tipo de sujetadores, los valores de diseño se "
            "deben determinar mediante ensayos de acuerdo con la sección "
            "F.4.6.1. Para otros métodos de sujeción deben seguirse las "
            "especificaciones del fabricante. F.4.8.4.3.4.2 — Conexiones "
            "por recorte para secciones C — Se permite el recorte entre "
            "miembros en sección C en conexiones sobre puntos de quiebre "
            "y talones, de acuerdo con el diseño de la cercha."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_3_4_recorte_ec11_12",
        "seccion": "F.4.8.4.3.4.2 (Conexiones por recorte — ecuaciones F.4.8.4-11 y -12, Figura F.4.8.4-4)",
        "titulo": "Factor de reducción R para conexiones de talón con aleta recortada: R según Imin≥67.000mm⁴ (ec.11) o menor (ec.12).",
        "texto": (
            "Figura F.4.8.4-4 — Definición de dimensiones de recorte en "
            "cerchas: muestra la altura de recorte y la longitud de "
            "recorte sobre un miembro en sección C. (a) En conexiones de "
            "talones, con una aleta recortada, y un rigidizador de apoyo "
            "con un momento de inercia (Imin) mayor o igual a "
            "67.000 mm⁴, la resistencia a la fuerza cortante se calcula "
            "de acuerdo con la sección F.4.3.3.2 y se deberá reducir por "
            "el siguiente factor, R: R = 0.976 − 0.556c/h − 0.532dc/h "
            "≤ 1.0 (F.4.8.4-11), con los siguientes límites: h/t ≤ 200, "
            "0.10 < c/h < 1.0 y 0.10 < dc/h < 0.4. (b) En conexiones de "
            "talones, con una aleta recortada y un rigidizador de apoyo "
            "con un momento de inercia (Imin) menor a 67.000 mm⁴, la "
            "resistencia calculada en el talón es gobernada por el "
            "arrugamiento del alma de acuerdo con la sección F.4.3.3.4 "
            "y debe ser reducida por el siguiente factor, R: "
            "R = 1.036 − 0.668c/h − 0.0505dc/h ≤ 1.0 (F.4.8.4-12), con "
            "los siguientes límites: h/t ≤ 200, 0.10 < c/h < 1.0 y "
            "0.10 < dc/h < 0.4. Donde: c = longitud del recorte. "
            "dc = altura del recorte. h = ancho plano del alma de la "
            "sección recortada. Imin = se calcula con respecto a un eje "
            "paralelo al alma del miembro cordón. t = espesor de diseño "
            "de la sección recortada."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_dinteles_intro_espalda_espalda",
        "seccion": "F.4.8.4.4 / F.4.8.4.4.1.1 (Dinteles — introducción y dintel tipo espalda con espalda, remisiones a F.4.3)",
        "titulo": "Diseño de dinteles cajón/espalda con espalda/L según F.4.2-F.4.5; espalda con espalda: flexión/cortante/arrugamiento remiten a F.4.3.",
        "texto": (
            "F.4.8.4.4 — Dinteles — El diseño e instalación de dinteles "
            "de acero formado en frío tipo cajón, tipo espalda con "
            "espalda y tipo L, sencillos y dobles, con el propósito de "
            "soportar cargas, se hará de acuerdo con las secciones "
            "F.4.2 a F.4.5 y lo estipulado en este numeral. "
            "F.4.8.4.4.1 — Diseño de dinteles. F.4.8.4.4.1.1 — Dinteles "
            "tipo espalda con espalda — Las disposiciones de esta "
            "sección se limitan a vigas dintel tipo espalda con espalda "
            "que se construyen usando secciones C de acero formado en "
            "frío de acuerdo con la sección F.4.8.4.4.2. F.4.8.4.4.1.1.1 "
            "— Flexión — La flexión debe revisarse utilizando las "
            "disposiciones de la sección F.4.3.3.1.1. F.4.8.4.4.1.1.2 — "
            "Cortante — El cortante debe revisarse utilizando las "
            "disposiciones de la sección F.4.3.3.2. F.4.8.4.4.1.1.3 — "
            "Arrugamiento del alma — El arrugamiento del alma debe "
            "revisarse de acuerdo a la sección F.4.3.3.4. Para vigas "
            "dintel tipo espalda con espalda deben utilizarse las "
            "ecuaciones para miembros armados. F.4.8.4.4.1.1.4 — Flexión "
            "y cortante — La combinación de flexión y cortante debe "
            "revisarse utilizando la sección F.4.3.3.3. F.4.8.4.4.1.1.5 "
            "— Flexión y arrugamiento del alma — Las almas de vigas "
            "dintel tipo espalda con espalda sujetas a una combinación "
            "de flexión y arrugamiento del alma deben diseñarse "
            "utilizando la sección F.4.3.3.5. Para vigas dintel tipo "
            "espalda con espalda deben utilizarse las ecuaciones para "
            "miembros armados."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_2_dintel_cajon_ec13_15",
        "seccion": "F.4.8.4.4.1.2 (Dintel tipo cajón — flexión/cortante/arrugamiento remiten a F.4.3; ecuaciones F.4.8.4-13 a -15)",
        "titulo": "α=2.3(tt/tc)≥1.0 (factor de incremento por Canal Guía, ecuación 13) o α=1.0 fuera de límites; interacción flexión+arrugamiento ec.15.",
        "texto": (
            "F.4.8.4.4.1.2 — Dinteles tipo cajón — Las disposiciones de "
            "esta sección se limitan a vigas dintel tipo cajón que sean "
            "instaladas usando secciones C de acero formado en frío de "
            "acuerdo con la sección F.4.8.4.4.2. F.4.8.4.4.1.2.1 — "
            "Flexión — La flexión se evalúa utilizando las disposiciones "
            "de la sección F.4.3.3.1.1. F.4.8.4.4.1.2.2 — Cortante — El "
            "cortante se evalúa utilizando las disposiciones de la "
            "sección F.4.3.3.2. F.4.8.4.4.1.2.3 — Arrugamiento del alma "
            "— El arrugamiento del alma se evalúa utilizando la sección "
            "F.4.3.3.4. Para vigas dintel tipo cajón se utilizan las "
            "ecuaciones para geometrías con almas sencillas. Se "
            "permitirá que el valor de Pn, para una condición de carga "
            "interior sobre una aleta, con el respectivo factor de "
            "resistencia φ, pueda ser multiplicado por α, donde α tiene "
            "en cuenta el incremento en resistencia debido al Canal "
            "Guía y se define como sigue: α = Parámetro definido por la "
            "ecuación F.4.8.4-13 ó F.4.8.4-14. Cuando el espesor de "
            "diseño de la sección del Canal Guía sea ≥0.879 mm, el "
            "ancho de la aleta del Canal Guía sea ≥25.4 mm, la altura de "
            "la sección C sea ≤305 mm y el espesor de diseño de la "
            "sección C sea ≥0.879 mm, entonces: α = 2.3·tt/tc ≥ 1.0 "
            "(F.4.8.4-13). Donde: tt = 0.879 mm. tc = espesor de diseño "
            "de la sección C. En caso de que los límites antes expuestos "
            "no se cumplan: α = 1.0 (F.4.8.4-14). F.4.8.4.4.1.2.4 — "
            "Flexión y cortante — La combinación de flexión y cortante "
            "se evalúa utilizando la sección F.4.3.3.3. F.4.8.4.4.1.2.5 "
            "— Flexión y arrugamiento del alma — Las almas de vigas "
            "dintel tipo cajón, sujetas a una combinación de flexión y "
            "arrugamiento del alma se diseñan utilizando, ya sea la "
            "sección F.4.3.3.5 o la siguiente ecuación: "
            "Pu/Pn + Mu/Mn ≤ 1.5φ (F.4.8.4-15). Donde: Pu = resistencia "
            "requerida al arrugamiento del alma. Mu = resistencia "
            "requerida a flexión. Pn = resistencia nominal a "
            "arrugamiento del alma calculada en la sección "
            "F.4.8.4.4.1.2.3. φ = 0.85. Mn = como se define en la "
            "sección F.4.3.3.1."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_3_dintel_l_doble_parametros",
        "seccion": "F.4.8.4.4.1.3 (Dinteles tipo L doble — parámetros de validez 1 a 10)",
        "titulo": "10 parámetros: aleta sup mín 38.1mm, lado vertical máx 254mm, espesor 0.838-1.829mm, Fy 230-345MPa, apoyo mín 38.1mm, luz máx 4.88m.",
        "texto": (
            "F.4.8.4.4.1.3 — Dinteles tipo L doble — Las disposiciones "
            "de esta sección se limitan a dinteles tipo L doble que sean "
            "instalados utilizando ángulos de acero formado en frío de "
            "acuerdo con la sección F.4.8.4.4.2 y que cumpla con los "
            "siguientes parámetros: (1) Ancho mínimo de aleta superior = "
            "38.1 mm. (2) Dimensión máxima del lado vertical = 254 mm. "
            "(3) Espesor mínimo del acero base = 0.838 mm. (4) Espesor "
            "máximo de diseño = 1.829 mm. (5) Esfuerzo de fluencia "
            "mínimo de diseño, Fy = 230 MPa. (6) Esfuerzo de fluencia "
            "máximo de diseño, Fy = 345 MPa. (7) Paral para arrugamiento "
            "localizado en todos los puntos de carga. (8) Longitud de "
            "apoyo mínima de 38.1 mm en los puntos de carga. (9) Ancho "
            "mínimo del muro = 88.9 mm (3.5 pulgadas). (10) Luz máxima "
            "entre apoyos = 4.88 m."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_3_1_flexion_gravitacional_ec16_17",
        "seccion": "F.4.8.4.4.1.3.1.1 (Dintel L doble — flexión, carga gravitacional, ecuaciones F.4.8.4-16 y -17)",
        "titulo": "Mng=Sec·Fy (lado vertical ≤203mm o luz/lado≥10); Mng=0.9·Sec·Fy si lado vertical>203mm y luz/lado<10.",
        "texto": (
            "F.4.8.4.4.1.3.1 — Flexión. F.4.8.4.4.1.3.1.1 — Carga "
            "gravitacional — (a) Para vigas dintel tipo L doble con el "
            "lado vertical de 203 mm de longitud o menos, el diseño debe "
            "basarse en la capacidad a flexión de las secciones L "
            "únicamente. La resistencia nominal a flexión bajo carga "
            "gravitacional, Mng, se determina como sigue: Mng = Sec·Fy "
            "(F.4.8.4-16). Donde: Fy = esfuerzo de fluencia utilizado en "
            "el diseño. Sec = módulo elástico de la sección efectiva "
            "calculado con f=Fy con respecto a las fibras extremas a "
            "compresión. (b) Para vigas dintel tipo L doble con el lado "
            "vertical mayor a 203 mm, y una relación Luz/Lado vertical "
            "del dintel mayor o igual a 10, el diseño debe basarse en la "
            "capacidad a flexión de las secciones L únicamente "
            "(ecuación F.4.8.4-16). (c) Para vigas dintel tipo L doble "
            "con el lado vertical mayor a 203 mm, y una relación "
            "Luz/Lado vertical del dintel menor a 10, la resistencia "
            "nominal a flexión bajo carga gravitacional, Mng, se "
            "determina como sigue: Mng = 0.9·Sec·Fy (F.4.8.4-17). Donde: "
            "Fy = esfuerzo de fluencia utilizado en el diseño. Sec = "
            "módulo elástico de la sección efectiva calculado con f=Fy "
            "con respecto a las fibras extremas a compresión."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_3_1_succion_ec18_20",
        "seccion": "F.4.8.4.4.1.3.1.2-3 (Dintel L doble — carga de succión ecuación F.4.8.4-18, capacidad de diseño a momento ecuaciones -19/-20)",
        "titulo": "Mnu=R·Mng con R=0.25 (Lh/t≤150) ó 0.20 (Lh/t≥170); φ=0.90/0.70 según Lh gravitacional, φ=0.80 succión.",
        "texto": (
            "F.4.8.4.4.1.3.1.2 — Carga de succión — Para vigas dintel "
            "tipo L doble, la resistencia nominal a flexión bajo cargas "
            "de succión, Mnu, se determina como sigue: Mnu = R·Mng "
            "(F.4.8.4-18). Donde: Mng = resistencia nominal a flexión "
            "bajo carga gravitacional determinada por la ecuación "
            "F.4.8.4-16. R = factor de succión = 0.25 para Lh/t ≤ 150. "
            "= 0.20 para Lh/t ≥ 170. = utilizar interpolación lineal "
            "para 150 < Lh/t < 170. Lh = dimensión del lado vertical del "
            "ángulo. t = espesor de diseño. F.4.8.4.4.1.3.1.3 — "
            "Capacidad de diseño a momento — La resistencia a flexión de "
            "diseño se determina como sigue: Para cargas gravitacionales: "
            "Mu = φMng (F.4.8.4-19). φ = 0.90 para vigas con Lh ≤ 203 mm. "
            "φ = 0.70 para vigas con Lh > 203 mm. Para cargas de "
            "succión: Mu = φMnu (F.4.8.4-20). φ = 0.80."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_3_no_considerados",
        "seccion": "F.4.8.4.4.1.3.2-5 (Dintel L doble — cortante, arrugamiento, y combinaciones no requieren revisión)",
        "titulo": "Cortante, arrugamiento del alma, flexión+cortante y flexión+arrugamiento NO necesitan considerarse en dinteles tipo L.",
        "texto": (
            "F.4.8.4.4.1.3.2 — Cortante — El cortante no necesita ser "
            "considerado para el diseño de vigas dintel tipo L que sean "
            "fabricadas e instaladas de acuerdo con este Reglamento. "
            "F.4.8.4.4.1.3.3 — Arrugamiento del alma — El arrugamiento "
            "del alma no necesita ser considerado para el diseño de "
            "vigas dintel tipo L que sean fabricadas e instaladas de "
            "acuerdo con este Reglamento. F.4.8.4.4.1.3.4 — Flexión y "
            "cortante — La combinación de flexión y cortante no "
            "necesita ser considerada para el diseño de vigas dintel "
            "tipo L fabricadas e instaladas de acuerdo con este "
            "Reglamento. F.4.8.4.4.1.3.5 — Flexión y arrugamiento del "
            "alma — La combinación de flexión y arrugamiento del alma no "
            "necesita ser considerada para el diseño de vigas dintel "
            "tipo L fabricadas e instaladas de acuerdo con este "
            "Reglamento."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_4_dintel_l_sencilla",
        "seccion": "F.4.8.4.4.1.4 (Dinteles tipo L sencilla — parámetros, flexión ecuaciones F.4.8.4-21 a -23)",
        "titulo": "10 parámetros (luz máx 1.22m); Mng=Sec·Fy (lado≤152mm) ó 0.9·Sec·Fy (152-203mm); succión no aplica; Mu=φMng, φ=0.90.",
        "texto": (
            "F.4.8.4.4.1.4 — Dinteles tipo L sencilla — Las disposiciones "
            "de esta sección se limitan a dinteles tipo L sencilla que "
            "sean instalados utilizando ángulos de acero formado en frío "
            "de acuerdo con la sección F.4.8.4.4.2 y que cumpla con los "
            "siguientes parámetros: (1) Ancho mínimo de la aleta "
            "superior = 38.1 mm. (2) Dimensión máxima del lado vertical "
            "= 203 mm. (3) Espesor mínimo del acero base = 0.838 mm. "
            "(4) Espesor máximo de diseño = 1.448 mm. (5) Esfuerzo de "
            "fluencia mínimo de diseño, Fy = 230 MPa. (6) Esfuerzo de "
            "fluencia máximo de diseño, Fy = 345 MPa. (7) Paral para "
            "arrugamiento localizado en todos los puntos de carga. "
            "(8) Longitud de apoyo mínima de 38.1 mm en los puntos de "
            "carga. (9) Ancho mínimo del muro = 88.9 mm. (10) Luz máxima "
            "entre apoyos = 1.22 m. F.4.8.4.4.1.4.1 — Flexión. "
            "F.4.8.4.4.1.4.1.1 — Carga gravitacional — (a) Para vigas "
            "dintel tipo L sencilla con el lado vertical de 152 mm de "
            "longitud o menos, el diseño debe basarse en la capacidad a "
            "flexión de la sección L únicamente. La resistencia nominal "
            "a flexión bajo carga gravitacional, Mng, se determina como "
            "sigue: Mng = Sec·Fy (F.4.8.4-21). (b) Para vigas dintel "
            "tipo L sencilla con el lado vertical mayor a 152 mm, pero "
            "menor o igual a 203 mm, la resistencia nominal a flexión "
            "bajo carga gravitacional, Mng, se determina como sigue: "
            "Mng = 0.9·Sec·Fy (F.4.8.4-22). Donde (ambas ecuaciones): "
            "Fy = esfuerzo de fluencia utilizado en el diseño. Sec = "
            "módulo elástico de la sección efectiva calculado con f=Fy "
            "con respecto a las fibras extremas a compresión. "
            "F.4.8.4.4.1.4.1.2 — Carga de succión — No aplica. "
            "F.4.8.4.4.1.4.1.3 — Capacidad de diseño a momento — La "
            "resistencia a flexión de diseño se determina como sigue: "
            "Para cargas gravitacionales: Mu = φMng (F.4.8.4-23). "
            "φ = 0.90."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_1_4_no_considerados_l_invertidos",
        "seccion": "F.4.8.4.4.1.4.2-5 / F.4.8.4.4.1.5 (Dintel L sencilla — no considerados; conjuntos tipo L invertidos)",
        "titulo": "Cortante/arrugamiento/combinados no considerados en L sencilla; L invertido: resistencia = suma de gravitacional+succión (doble) o solo gravitacional (sencilla).",
        "texto": (
            "F.4.8.4.4.1.4.2 — Cortante — El cortante no necesita ser "
            "considerado para el diseño de vigas dintel tipo L que sean "
            "fabricadas e instaladas de acuerdo con este Reglamento. "
            "F.4.8.4.4.1.4.3 — Arrugamiento del alma — El arrugamiento "
            "del alma no necesita ser considerado para el diseño de "
            "vigas dintel tipo L que sean fabricadas e instaladas de "
            "acuerdo con este Reglamento. F.4.8.4.4.1.4.4 — Flexión y "
            "cortante — La combinación de flexión y cortante no "
            "necesita ser considerada para el diseño de vigas dintel "
            "tipo L fabricadas e instaladas de acuerdo con este "
            "Reglamento. F.4.8.4.4.1.4.5 — Flexión y arrugamiento del "
            "alma — La combinación de flexión y arrugamiento del alma no "
            "necesita ser considerada para el diseño de vigas dintel "
            "tipo L fabricadas e instaladas de acuerdo con este "
            "Reglamento. F.4.8.4.4.1.5 — Conjuntos de dinteles tipo L "
            "invertidos — (a) Las disposiciones de esta sección se "
            "limitan a dinteles tipo L invertidos que satisfacen los "
            "requisitos definidos en las secciones F.4.8.4.4.1.3 y "
            "F.4.8.4.4.1.4 para dinteles dobles y sencillos, "
            "respectivamente. (b) Para dinteles tipo L doble, la "
            "resistencia nominal a flexión del conjunto L combinado "
            "(ej: un dintel tipo L más un dintel L invertido), se "
            "determina por la suma de las resistencias nominales a "
            "flexión bajo carga gravitacional y de succión tal como se "
            "determina en la sección F.4.8.4.4.1.3.1. (c) Para dinteles "
            "tipo L sencilla, la resistencia nominal a flexión del "
            "conjunto L combinado (ej: un dintel L más un dintel L "
            "invertido), debe basarse en la resistencia nominal a "
            "flexión bajo carga gravitacional tal como se determina en "
            "la sección F.4.8.4.4.1.4.1. (d) El cortante, arrugamiento "
            "del alma, flexión y cortante combinados, y flexión y "
            "arrugamiento del alma combinados, no necesitan ser "
            "considerados para el diseño de dinteles L invertidos "
            "fabricados e instalados de acuerdo con este Reglamento."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_2_instalacion_dinteles_espalda_cajon",
        "seccion": "F.4.8.4.4.2 / F.4.8.4.4.2.1 (Instalación de dinteles — tipo espalda con espalda y cajón, Figuras F.4.8.4-5/-6)",
        "titulo": "Instalación según Figuras F.4.8.4-5 (espalda con espalda) y -6 (cajón); soldadura alternativa 25.4mm cada 610mm en vez de tornillos No.8.",
        "texto": (
            "F.4.8.4.4.2 — Instalación de dinteles — Los dinteles deben "
            "instalarse de acuerdo con las provisiones dadas en el "
            "numeral F.4.8 y los requisitos de las secciones "
            "F.4.8.4.4.2.1, F.4.8.4.4.2.2 y F.4.8.4.4.2.3, según sea "
            "aplicable. F.4.8.4.4.2.1 — Dinteles tipo espalda con "
            "espalda y cajón — Los dinteles tipo espalda con espalda y "
            "cajón se deben instalar de acuerdo con las figuras "
            "F.4.8.4-5 y F.4.8.4-6, respectivamente. Para dinteles tipo "
            "cajón se permite conectar Canales Guías a las almas de las "
            "secciones C utilizando cordones de soldadura de 25.4 mm "
            "espaciados cada 610 mm a centros, en lugar de tornillos "
            "No. 8. Figura F.4.8.4-5 — Dintel tipo espalda con espalda: "
            "muestra mínimo 2 tornillos #8 cada 600mm a centros (2 "
            "tornillos sobre las alas superiores y 2 tornillos sobre las "
            "alas inferiores), canal guía en esta posición o al revés, "
            "secciones C espalda con espalda, mínimo 2 tornillos #8 "
            "cada 600mm a centros. Figura F.4.8.4-6 — Dintel tipo cajón: "
            "muestra mínimo 2 tornillos #8 cada 600mm a centros (a "
            "través de alas del Canal Guía a las secciones C, un "
            "tornillo por cada ala, ó 2 tornillos a través del Canal "
            "Guía a las alas de las secciones C, un tornillo por cada "
            "ala), canal guía hacia abajo, secciones C, canal guía en "
            "esta posición o al revés."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_4_4_2_2_3_instalacion_dintel_l",
        "seccion": "F.4.8.4.4.2.2 (Instalación de dinteles tipo L doble y sencilla — Figuras F.4.8.4-7 y F.4.8.4-8)",
        "titulo": "Dintel L doble/sencilla apoyado totalmente sobre el ancho del paral, mín. 40mm; tornillos #8 en extremos y cada 300mm; paral bajo cargas.",
        "texto": (
            "F.4.8.4.4.2.2 — Dinteles tipo L doble y sencilla — Los "
            "dinteles tipo L doble y sencilla se deben instalar de "
            "acuerdo con las figuras F.4.8.4-7 y F.4.8.4-8, "
            "respectivamente. Figura F.4.8.4-7 — Dintel tipo L doble: "
            "muestra canal guía superior, paral típico espaciado de "
            "manera convencional según diseño, mínimo tornillos #8 en "
            "cada extremo, el dintel tipo \"L\" debe apoyarse totalmente "
            "sobre el ancho del paral como mínimo en cada extremo, eje "
            "del paral para arrugamiento sujeto a cargas desde la parte "
            "superior, dintel tipo L, mínimo tornillos #8 por cada paral "
            "en la parte superior e inferior del lado del cabecero, "
            "40mm (1-1/2\") mínimo lado horizontal del cabecero L, "
            "mínimo tornillos #8 cada 300mm (12\"), canal guía en "
            "aberturas, parales para arrugamiento requeridos en puntos "
            "de carga con máximo de 600mm (24\") a centro, conexión del "
            "canal guía no mostrada, parales adicionales según se "
            "requiera, vano de la abertura o luz simple (puerta o "
            "ventana). Figura F.4.8.4-8 — Dintel tipo L sencilla: misma "
            "disposición general que la Figura F.4.8.4-7, con un solo "
            "dintel tipo L en vez de doble."
        ),
    },
    {
        "id": "NSR10-F-F_4_8_5_estado_servicio",
        "seccion": "F.4.8.5 (Estado de servicio)",
        "titulo": "Requisitos de servicio según criterios del diseñador; se permite usar sección transversal completa para deflexiones.",
        "texto": (
            "F.4.8.5 — ESTADO DE SERVICIO — Los requisitos para estados "
            "de servicio, tal como se describen en este Reglamento, "
            "deben determinarse por el diseñador de la edificación o "
            "con criterios de acuerdo a las especificaciones descritas "
            "en este Reglamento. Se permite el uso de áreas de sección "
            "transversal completas para los miembros de entramados en "
            "el cálculo de las deflexiones."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.8 cargados. F.4.8 queda COMPLETO -- y con esto TODO F.4.")


if __name__ == "__main__":
    main()
