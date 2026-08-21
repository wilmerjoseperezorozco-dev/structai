"""
Batch 2 de reauditoria Titulo F (NSR-10, Estructuras Metalicas): F.2.6
(Diseno de miembros a flexion -- provisiones generales + el caso mas comun,
perfiles I/canales compactos de doble simetria) y F.2.10 (Conexiones:
soldadura y pernos).

Fuente: NSR-10-712-742.pdf (F-58 a F-61) + NSR-10-743-770.pdf (F-62, cierre
de F.2.6.2) para flexion; NSR-10-771-800.pdf (F-102 a F-119) para conexiones.
Carpeta Drive NSR10 (id 1D7-UD-r543j4hUMiegPQ4fDwialfqiEB).

Uso: python _ingest_titulo_f_batch2.py
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
        "id": "NSR10-F-F_2_6a",
        "seccion": "F.2.6.1 a F.2.6.2",
        "titulo": (
            "Diseno de miembros a flexion, caso general y el mas comun en la practica: "
            "perfiles I/canales de doble simetria, alma y aletas compactas, flexion "
            "alrededor del eje mayor. Resistencia phi_b*Mn=0.90*Mn, factor Cb de "
            "modificacion por pandeo lateral-torsional, momento plastico Mp=Fy*Zx, y los "
            "3 regimenes de pandeo lateral-torsional segun Lb vs Lp/Lr. CORRIGE la "
            "numeracion de los chunks obsoletos E-SEC6-FORM1/E-SEC6-FORM2 que trataban "
            "esto como capitulo independiente \"F.6\" (en realidad es el numeral F.2.6 "
            "dentro del capitulo unico F.2)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.6 — Diseño de "
            "miembros a flexión (F.2.6.1 Provisiones generales, F.2.6.2 Perfiles I de "
            "doble simetría y canales compactos, flexión eje mayor).\n\n"
            "Se aplica a miembros solicitados por flexión simple alrededor de un eje "
            "principal, cuando el plano de carga es paralelo a un eje principal y pasa por "
            "el centro de corte, o el miembro está restringido contra torsión en cargas y "
            "apoyos. Incluye 13 numerales según tipo de sección (F.2.6.2 a F.2.6.13: I "
            "compacta, I con aletas no compactas/esbeltas, I con alma esbelta, flexión eje "
            "menor, PTE cuadrado/rectangular, PTE circular, T y ángulos dobles, ángulo "
            "sencillo, barras, secciones no simétricas, dimensionamiento). La tabla F.2.6-1 "
            "guía qué numeral aplicar según esbeltez de aleta/alma. Para flexión biaxial o "
            "combinada con axial ver F.2.8; flexión+torsión ver F.2.8.4; fatiga ver F.2.17; "
            "cortante ver F.2.7.\n\n"
            "F.2.6.1 Provisiones generales: la resistencia de diseño a flexión es "
            "phi_b*Mn, con phi_b = 0.90. Mn se determina según F.2.6.2 a F.2.6.13. Se "
            "asume que los apoyos de la viga están restringidos contra rotación alrededor "
            "de su eje longitudinal.\n\n"
            "Factor Cb (modificación por pandeo lateral-torsional, para diagramas de "
            "momento NO uniformes entre puntos arriostrados):\n"
            "Cb = (12.5*Mmax) / (2.5*Mmax + 3*MA + 4*MB + 3*MC) * Rm  <= 3.00 "
            "(ecuación F.2.6.1-1)\n"
            "donde Mmax = momento máximo absoluto en el segmento; MA, MB, MC = momentos "
            "absolutos a 1/4, 1/2 y 3/4 de la longitud del segmento; Rm = parámetro de "
            "monosimetría (Rm=1.0 para doble simetría o simetría simple en curvatura "
            "simple; Rm = 0.5 + 2*(Iyc/Iy)^2 para simetría simple en curvatura doble, "
            "donde Iyc es la inercia de la aleta a compresión). Conservadoramente se puede "
            "asumir Cb=1.0 siempre (obligatorio en voladizos con extremo libre sin "
            "arriostrar). Para miembros de doble simetría sin cargas transversales entre "
            "arriostramientos, la fórmula da Cb=1.0 para momento uniforme, 2.27 para doble "
            "curvatura de igual magnitud, y 1.67 cuando el momento es nulo en un extremo.\n\n"
            "F.2.6.2 Perfiles I de doble simetría y canales, alma y aletas COMPACTAS, "
            "flexión eje mayor — el caso de diseño de vigas de acero más común en la "
            "práctica: Mn es el MENOR entre plastificación de la sección y pandeo "
            "lateral-torsional.\n\n"
            "Plastificación (momento plástico): Mn = Mp = Fy*Zx (ecuación F.2.6.2-1), "
            "donde Zx = módulo plástico de la sección alrededor del eje x.\n\n"
            "Pandeo lateral-torsional, según la longitud no arriostrada Lb:\n"
            "  (a) Lb <= Lp: no aplica el estado límite de pandeo lateral-torsional "
            "(Mn = Mp)\n"
            "  (b) Lp < Lb <= Lr: "
            "Mn = Cb*[Mp - (Mp - 0.70*Fy*Sx)*((Lb-Lp)/(Lr-Lp))] <= Mp "
            "(ecuación F.2.6.2-2)\n"
            "  (c) Lb > Lr: Mn = Fcr*Sx <= Mp (ecuación F.2.6.2-3), donde\n"
            "      Fcr = (Cb*pi^2*E)/(Lb/rts)^2 * raiz[1 + 0.078*(J*c/(Sx*ho))*(Lb/rts)^2] "
            "(ecuación F.2.6.2-4; el término bajo la raíz puede tomarse "
            "conservadoramente como 1.0)\n"
            "donde E = 200000 MPa, J = constante torsional, Sx = módulo elástico de "
            "sección eje x, ho = distancia entre centroides de aletas.\n\n"
            "Límites de longitud:\n"
            "Lp = 1.76*ry*raiz(E/Fy)  (ecuación F.2.6.2-5)\n"
            "Lr = 1.95*rts*(E/(0.7*Fy)) * raiz[(J*c/(Sx*ho)) + raiz((J*c/(Sx*ho))^2 + "
            "6.76*(0.7*Fy/E)^2)]  (ecuación F.2.6.2-6)\n"
            "con rts^2 = raiz(Iy*Cw)/Sx (ecuación F.2.6.2-7), y el factor c: c=1 para "
            "perfiles I de doble simetría (ecuación F.2.6.2-8a); para canales "
            "c = (ho/2)*raiz(Iy/Cw) (ecuación F.2.6.2-8b). Para I de doble simetría con "
            "aletas rectangulares, Cw = Iy*ho^2/4, por lo que rts^2 se simplifica a "
            "Iy*ho/(2*Sx); rts puede aproximarse conservadoramente al radio de giro de la "
            "aleta a compresión más 1/6 del alma."
        ),
    },
    {
        # Nota 2026-08-20: originalmente un solo chunk NSR10-F-F_2_10a con
        # soldaduras+pernos juntos (5106 chars) -- verificado en vivo que
        # retrieval fallaba (no aparecía top-4 ni para preguntas centradas
        # en soldadura). Dividido en dos chunks de un solo subtema cada uno,
        # igual patron que F.2.5a/F.2.5b -- confirmado que mejora retrieval.
        "id": "NSR10-F-F_2_10_soldaduras",
        "seccion": "F.2.10.1 a F.2.10.2",
        "titulo": (
            "Diseno de conexiones soldadas: requisitos generales (conexiones simples vs a "
            "momento, agujeros de acceso), soldaduras acanaladas y de filete, resistencia "
            "de diseno Rn=Fnw*Awe con Fnw=0.60*FEXX y phi=0.75 para filete, formula angular "
            "F.2.10.2-5 (factor de carga transversal). CORRIGE la numeracion de los chunks "
            "obsoletos E-SEC8-FORM2/E-SEC8-IMG1 y parte de ntc_chunks id 295 que trataban "
            "esto como capitulo independiente \"F.8\" (en realidad es el numeral F.2.10 "
            "dentro del capitulo unico F.2)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.10 — Diseño de "
            "conexiones (F.2.10.1 Requisitos generales, F.2.10.2 Soldaduras).\n\n"
            "F.2.10 se aplica a elementos de conexión, conectores y elementos afectados de "
            "miembros conectados no sometidos a fatiga.\n\n"
            "F.2.10.1.1 Bases de diseño: la resistencia de diseño de las conexiones, "
            "R*phi_n, se determina según este numeral y F.2.2.\n\n"
            "F.2.10.1.2 Conexiones simples: se diseñan como conexiones flexibles, "
            "típicamente solo para reacciones de cortante; deben permitir rotación de "
            "extremos de vigas simplemente apoyadas.\n\n"
            "F.2.10.1.3 Conexiones a momento: se diseñan para las fuerzas resultantes de "
            "los efectos combinados de momento y cortante inducidos por la rigidez de la "
            "conexión.\n\n"
            "F.2.10.1.6 Agujeros de acceso para soldadura: longitud mínima 1.5 veces el "
            "espesor del material (no menor a 38 mm) medida desde el talón de la "
            "preparación; altura mínima igual al espesor del material (no menor a 19 mm, "
            "no necesita exceder 50 mm); radio mínimo de cualquier arco: 10 mm.\n\n"
            "F.2.10.1.10 Limitaciones: deben usarse pernos pretensionados o soldadura "
            "(no apriete ajustado simple) en: empalmes de columnas en edificios de más de "
            "38 m de altura, conexiones viga-columna en edificios de más de 38 m, "
            "estructuras con puentes grúa de más de 50 kN, y conexiones para maquinaria en "
            "movimiento con impacto o inversión de esfuerzos.\n\n"
            "F.2.10.2 SOLDADURAS: rigen las provisiones del Código de Soldadura Estructural "
            "AWS D1.1, con excepciones específicas del Capítulo F.2.\n\n"
            "F.2.10.2.1 Soldaduras acanaladas: área efectiva = longitud × espesor efectivo "
            "de garganta. Para penetración completa, el espesor efectivo es el menor entre "
            "los espesores de las partes unidas. Para penetración parcial, según tabla "
            "F.2.10.2-1 (depende del proceso: SMAW/GMAW/FCAW/SAW y tipo de canal J/U/V).\n\n"
            "F.2.10.2.2 Soldaduras de filete: área efectiva = longitud efectiva × garganta "
            "efectiva (distancia más corta entre la raíz y la cara exterior esquemática). "
            "Tamaño mínimo según tabla F.2.10.2-4 (3 mm hasta 6.4 mm de espesor de parte más "
            "delgada, 5 mm de 6.4 a 12.7 mm, 6 mm de 12.7 a 19.1 mm, 8 mm para más de "
            "19.1 mm). Tamaño máximo: el espesor del material si es menor a 6 mm; espesor "
            "menos 1.6 mm si es de 6 mm o más. Longitud mínima: 4 veces el tamaño nominal. "
            "Para soldaduras longitudinales de filete que transmiten carga axial con "
            "longitud > 100 veces el tamaño del filete, la longitud efectiva se reduce por "
            "beta = 1.2 - 0.002*(l/w) <= 1.0 (ecuación F.2.10.2-1); si la longitud excede "
            "300 veces el tamaño, la longitud efectiva se toma como 180*w.\n\n"
            "F.2.10.2.4 Resistencia de diseño de soldaduras: R*phi_n (resistencia de "
            "diseño, ó phi_Rn) es el MENOR entre la resistencia del metal base (rotura por "
            "tensión/cortante) y la resistencia del metal de soldadura (rotura):\n"
            "  Metal base: Rn = FnBM * ABM  (ecuación F.2.10.2-2)\n"
            "  Metal de soldadura: Rn = Fnw * Awe  (ecuación F.2.10.2-3)\n"
            "Valores según Tabla F.2.10.2-5: para soldaduras acanaladas de penetración "
            "completa a tensión/compresión, la resistencia la controla el metal base "
            "(phi=0.90, Fy). Para SOLDADURAS DE FILETE a cortante (el caso más común en la "
            "práctica): phi = 0.75, Fnw = 0.60*FEXX, donde FEXX = número de clasificación "
            "del electrodo (resistencia mínima especificada, MPa; para electrodo E70XX, "
            "FEXX = 480 MPa).\n\n"
            "Alternativamente, para un grupo de soldaduras de filete cargado en su propio "
            "plano a través del centro de gravedad, con phi=0.75:\n"
            "  Rn = Fnw*Awe  (ecuación F.2.10.2-4)\n"
            "  Fnw = 0.60*FEXX*(1.0 + 0.50*sen^1.5(θ))  (ecuación F.2.10.2-5)\n"
            "donde θ = ángulo de aplicación de la carga medido desde el eje longitudinal de "
            "la soldadura (el factor (1.0+0.50*sen^1.5θ) refleja que la resistencia real de "
            "un filete cargado transversalmente es mayor que cargado longitudinalmente, "
            "hasta 50% más a 90°). Para grupos de filetes concéntricos con elementos "
            "longitudinales y transversales del mismo tamaño, la resistencia combinada es "
            "el mayor entre Rn = Rnw1 + Rnwt (ecuación F.2.10.2-10a) y "
            "Rn = 0.85*Rnw1 + 1.5*Rnwt (ecuación F.2.10.2-10b)."
        ),
    },
    {
        "id": "NSR10-F-F_2_10_pernos",
        "seccion": "F.2.10.3",
        "titulo": (
            "Diseno de conexiones apernadas: pernos de alta resistencia A325/A490 y A307, "
            "tabla de resistencia nominal Fnt/Fnv, y las 3 formulas de resistencia de "
            "diseno Rn=Fn*Ab (phi=0.75, tipo aplastamiento), F'nt modificada por cortante "
            "combinado, y Rn=mu*Du*hf*Tb*ns (deslizamiento critico, phi segun tipo de "
            "perforacion). CORRIGE la numeracion equivocada del chunk obsoleto "
            "E-SEC8-FORM1, que ADEMAS tenia valores Fnv incorrectos (330/415 MPa para "
            "A325/A490 en vez de los reales 372/457 y 457/579 MPa) -- error de contenido, "
            "no solo de formato."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.10.3 — Pernos y "
            "partes roscadas.\n\n"
            "Rigen las especificaciones RCSC (Consejo de Investigación de Conexiones "
            "Estructurales) para pernos ASTM A325/A490. Grupo A = A325, A325M, F1852, "
            "A354 Gr. BC, A449. Grupo B = A490, A490M, F2280, A354 Gr. BD.\n\n"
            "Se permite instalar los pernos con apriete ajustado en conexiones tipo "
            "aplastamiento (salvo excepciones de F.2.5.6/F.2.10.1.10), o en conexiones a "
            "tensión/cortante combinado solo para pernos Grupo A sin riesgo de aflojamiento "
            "por vibración o fatiga. Los pernos pretensionados o de deslizamiento crítico "
            "deben apretarse hasta la tensión mínima de instalación de la Tabla F.2.10.3-1 "
            "(igual a 0.70 veces la resistencia mínima a tensión del perno).\n\n"
            "Tabla F.2.10.3-2 — Resistencia NOMINAL para pernos y piezas roscadas (MPa) — "
            "valores de Fnt (tensión) y Fnv (cortante en conexiones tipo aplastamiento):\n"
            "  Pernos A307: Fnt = 310 MPa, Fnv = 188 MPa\n"
            "  Grupo A (tipo A325), roscas INCLUIDAS en el plano de corte: "
            "Fnt = 620 MPa, Fnv = 372 MPa\n"
            "  Grupo A (tipo A325), roscas EXCLUIDAS del plano de corte: "
            "Fnt = 620 MPa, Fnv = 457 MPa\n"
            "  Grupo B (tipo A490), roscas INCLUIDAS en el plano de corte: "
            "Fnt = 780 MPa, Fnv = 457 MPa\n"
            "  Grupo B (tipo A490), roscas EXCLUIDAS del plano de corte: "
            "Fnt = 780 MPa, Fnv = 579 MPa\n"
            "  Piezas roscadas (F.2.1.3.4), roscas incluidas: Fnt = 0.75*Fu, "
            "Fnv = 0.450*Fu\n"
            "  Piezas roscadas (F.2.1.3.4), roscas excluidas: Fnt = 0.75*Fu, "
            "Fnv = 0.563*Fu\n\n"
            "Notas de la tabla: para conexiones de extremo con un patrón de perforaciones "
            "de longitud mayor a 965 mm, Fnv se reduce al 83.3% de los valores tabulados. "
            "Para pernos A307, los valores se reducen 1% por cada 1.6 mm de longitud de "
            "agarre por encima de 5 diámetros.\n\n"
            "F.2.10.3.6 Resistencia de diseño a tensión y cortante (conexiones tipo "
            "APLASTAMIENTO, pernos con apriete ajustado o pretensionados): phi = 0.75, y\n"
            "  Rn = Fn * Ab  (ecuación F.2.10.3-1)\n"
            "donde Fn = Fnt (tensión) o Fnv (cortante) de la Tabla F.2.10.3-2 anterior, "
            "Ab = área nominal del perno o parte roscada antes de roscar (mm²).\n\n"
            "F.2.10.3.7 Esfuerzos combinados de cortante y tensión (conexiones tipo "
            "aplastamiento): phi = 0.75, y\n"
            "  Rn = F'nt * Ab  (ecuación F.2.10.3-2)\n"
            "  F'nt = 1.3*Fnt - (Fnt/(phi*Fnv))*fv <= Fnt  (ecuación F.2.10.3-3)\n"
            "donde F'nt = resistencia nominal a tensión modificada por el esfuerzo cortante "
            "presente, fv = resistencia requerida a cortante por unidad de área (MPa). No "
            "se requiere verificar esfuerzos combinados si la resistencia requerida (cortante "
            "o tensión) es <= 30% de la resistencia de diseño correspondiente.\n\n"
            "F.2.10.3.8 Conexiones de DESLIZAMIENTO CRÍTICO (slip-critical): phi depende del "
            "tipo de perforación — phi=1.00 (perforaciones estándar o de ranura corta "
            "perpendicular a la carga), phi=0.85 (perforaciones agrandadas o ranura corta "
            "paralela), phi=0.70 (ranura larga). Resistencia nominal:\n"
            "  Rn = mu * Du * hf * Tb * ns  (ecuación F.2.10.3-4)\n"
            "donde mu = coeficiente de fricción (0.30 para superficies Clase A sin tratar/"
            "galvanizadas rugosas; 0.50 para superficies Clase B tratadas con chorro), "
            "Du = 1.13 (factor de pretensión promedio), Tb = tensión mínima del perno "
            "(Tabla F.2.10.3-1, kN), hf = factor de platinas de relleno (1.0 sin relleno o "
            "con pernos añadidos para distribuir carga; 0.85 con 2+ platinas de relleno sin "
            "pernos añadidos), ns = número de planos de deslizamiento."
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
    print(f"OK: {len(rows)} chunks F.2.6/F.2.10 cargados con embedding.")


if __name__ == "__main__":
    main()
