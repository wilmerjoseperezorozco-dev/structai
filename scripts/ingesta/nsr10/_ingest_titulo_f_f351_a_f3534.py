"""
NSR-10 Titulo F, F.3.5.1 (PRM-DMI) + F.3.5.2 (PRM-DMO) + F.3.5.3.1 a
F.3.5.3.4.1 (inicio de PRM-DES: alcance, bases, analisis, relacion de
momentos columna fuerte-viga debil) -- cierra el hueco que dejo el chunk
viejo NSR10-F-F_3_5_PRM (resumen de sesiones anteriores) tras el batch de
hoy de F.3.5.3.4(resto)-F.3.6.5 (commit 4b8fbdb), que ya cubria el RESTO de
F.3.5.3 (arriostramiento de columnas, miembros, conexiones) pero no el
inicio de F.3.5 (PRM-DMI, PRM-DMO, ni la formula de relacion de momentos
F.3.5.3-1 a F.3.5.3-5).

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
paginas internas F-235 a F-240. Leido visualmente pagina por pagina.

2 chunks. Tras cargar estos, se borra el chunk viejo NSR10-F-F_3_5_PRM
(queda completamente reemplazado por este batch + el commit 4b8fbdb).

Uso: python _ingest_titulo_f_f351_a_f3534.py
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
        "id": "NSR10-F-F_3_5_1_PRM_DMI",
        "seccion": "F.3.5.1 (Pórticos Resistentes a Momentos con capacidad de disipación de energía mínima PRM-DMI, completo)",
        "titulo": (
            "PRM-DMI completo: sin requisitos especiales de análisis/sistema/miembros "
            "(deformaciones inelásticas mínimas), conexiones viga-columna TR (momento "
            "1.1·Ry·Mp) o PR (momento nominal ≥0.5Mp), resistencia a cortante "
            "requerida Emh=2(1.1Ry·Mp)/Lcf."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "Numerales de F.3.5: F.3.5.1 PRM-DMI, F.3.5.2 PRM-DMO, F.3.5.3 PRM-DES, "
            "F.3.5.4 PCD, F.3.5.5 SCV-DMI, F.3.5.6 SCV-DES.\n\n"
            "F.3.5.1 — PÓRTICOS RESISTENTES A MOMENTOS CON CAPACIDAD DE DISIPACIÓN DE "
            "ENERGÍA MÍNIMA (PRM-DMI).\n"
            "F.3.5.1.1 Alcance — diseñarse de acuerdo con esta sección.\n"
            "F.3.5.1.2 Bases de diseño — diseñados para resistir deformaciones "
            "inelásticas MÍNIMAS en sus miembros y conexiones.\n"
            "F.3.5.1.3 Análisis — no se especifican requisitos especiales.\n"
            "F.3.5.1.4 Requisitos del sistema — no se especifican requisitos "
            "especiales.\n"
            "F.3.5.1.5 Miembros — no se especifican requisitos especiales a las "
            "relaciones ancho-espesor ni de arriostramiento para estabilidad de vigas "
            "o uniones, adicionales a las del Capítulo F.2. No se consideran zonas "
            "protegidas. Se permite usar vigas formadas con perfiles de acero "
            "compuestas con placas de concreto reforzado para resistir cargas de "
            "gravedad.\n"
            "F.3.5.1.6 Conexiones — las conexiones viga-columna pueden ser totalmente "
            "restringidas (TR) o parcialmente restringidas (PR).\n"
            "F.3.5.1.6.1 Soldaduras de demanda crítica — las soldaduras acanaladas de "
            "penetración completa de las aletas de las vigas a las columnas son de "
            "demanda crítica, cumplen F.3.1.3.4.2.\n"
            "F.3.5.1.6.2 Conexiones a momento totalmente restringidas (TR) — que "
            "formen parte del SRS deben satisfacer al menos una de las siguientes "
            "condiciones: (1) diseñarse para resistencia a flexión requerida "
            "1.1*Ry*Mp de la viga; la resistencia requerida a cortante Vu se basa en "
            "combinaciones del Título B con carga sísmica amplificada, con "
            "Emh = 2*(1.1*Ry*Mp)/Lcf  (F.3.5.1-1), donde Ry=relación esfuerzo "
            "fluencia esperado/mínimo especificado, Fy; Mp=Fy*Z, N·mm; Lcf=longitud "
            "libre de la viga, mm; (2) diseñarse para el momento máximo y cortante "
            "correspondiente transmisible al sistema, incluyendo efectos de "
            "sobrerresistencia y endurecimiento por deformación, limitados por la "
            "resistencia de la columna o de la cimentación al levantamiento. Para "
            "ambas opciones, colocar placas de continuidad según F.2.10.1, F.2.10.2 "
            "y F.2.10.3, usando el mismo momento que para el diseño de la conexión "
            "viga-columna. (3) alternativamente, satisfacer los requisitos de "
            "F.3.5.2.6 o F.3.5.3.6, o cumplir: (a) soldaduras de la conexión "
            "viga-columna según el Capítulo 3 de ANSI/AISC 358; (b) aletas de viga "
            "conectadas a aletas de columna con soldaduras acanaladas de penetración "
            "completa; (c) forma de agujeros de acceso según AWS D1.8 numeral 6.9.1.2 "
            "y calidad según 6.9.2; (d) placas de continuidad según F.3.5.3.6.6, "
            "excepto que pueden ser de penetración completa, penetración parcial por "
            "2 lados, o filetes por ambos lados; resistencia requerida no menor que "
            "resistencia diseño del área de contacto de placa-aleta de columna; (e) "
            "alma de viga conectada a aleta de columna con soldadura acanalada de "
            "penetración completa entre agujeros de acceso, o conexión con placa de "
            "cortante sencilla pernada diseñada para la resistencia a cortante de la "
            "ecuación F.3.5.1-1. Para conexiones TR, la resistencia de la zona de "
            "panel se revisa según F.2.10.10.6; resistencia requerida a cortante "
            "basada en momentos en el extremo de la viga con combinaciones del "
            "Título B, SIN incluir la carga sísmica amplificada.\n"
            "F.3.5.1.6.3 Conexiones a momento parcialmente restringidas (PR) — deben "
            "cumplir: (1) diseñarse para el momento máximo y cortante de las "
            "combinaciones de F.3.2.2 y F.3.2.3; (2) la rigidez, resistencia y "
            "capacidad de deformación de la conexión PR debe considerarse en el "
            "diseño, incluyendo su efecto en la estabilidad general de la estructura; "
            "(3) la resistencia nominal a flexión de la conexión, MnPR, no debe ser "
            "menor que 0.5*Mp de la viga conectada, excepto en estructuras de un "
            "nivel donde MnPR no debe ser menor que 0.5*Mp de la columna conectada; "
            "(4) para conexiones PR, Vu se determina según F.3.5.1.6.2(1), tomando "
            "MnPR como Mp en la ecuación F.3.5.1-1."
        ),
    },
    {
        "id": "NSR10-F-F_3_5_2_PRM_DMO_a_F_3_5_3_inicio",
        "seccion": "F.3.5.2 (PRM-DMO completo) + F.3.5.3.1 a F.3.5.3.4.1 (PRM-DES: alcance, bases, análisis, relación de momentos columna fuerte-viga débil con fórmulas)",
        "titulo": (
            "PRM-DMO completo: deriva mínima 0.02 rad, resistencia conexión ≥0.8Mp, "
            "validación por ensayos F.3.11. Inicio de PRM-DES: alcance/bases/análisis, "
            "y la fórmula de relación de momentos columna fuerte-viga débil "
            "ΣM*pc/ΣM*pb>1 con las 5 ecuaciones completas y su excepción."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "F.3.5.2 — PÓRTICOS RESISTENTES A MOMENTOS CON CAPACIDAD DE DISIPACIÓN DE "
            "ENERGÍA MODERADA (PRM-DMO).\n"
            "F.3.5.2.1 Alcance — diseñarse según esta sección.\n"
            "F.3.5.2.2 Bases de diseño — capacidad de deformación inelástica LIMITADA "
            "a partir de la fluencia por flexión de vigas y columnas, y fluencia por "
            "cortante de la zona de panel en la columna. Diseño de conexiones "
            "viga-columna (incluyendo zona de panel y placas de continuidad) basado "
            "en ensayos que garanticen el desempeño requerido (F.3.5.2.6.2), "
            "demostrado según F.3.5.2.6.3.\n"
            "F.3.5.2.3 Análisis — no se especifican requisitos de diseño especiales.\n"
            "F.3.5.2.4 Requisitos del sistema: F.3.5.2.4.1 Arriostramiento para "
            "estabilidad de vigas — arriostradas para satisfacer ductilidad moderada "
            "(F.3.4.1.2.1). Adicionalmente, salvo que ensayos indiquen otra cosa, los "
            "arriostramientos deben colocarse cerca de fuerzas concentradas, cambios "
            "de sección transversal, y otras ubicaciones donde el análisis indique "
            "posible rótula plástica; consistente con lo documentado para conexión "
            "precalificada según ANSI/AISC 358, o precalificación (F.3.11.1) o "
            "programa de ensayos (F.3.11.2). Resistencia requerida del "
            "arriostramiento lateral adyacente a rótulas plásticas según F.3.4.1.2.3.\n"
            "F.3.5.2.5 Miembros: F.3.5.2.5.1 Requisitos básicos — vigas y columnas "
            "satisfacen F.3.4.1 para ductilidad moderada, salvo que ensayos de "
            "calificación lo precisen. Vigas con perfiles de acero pueden ser "
            "compuestas con placa de concreto reforzado para cargas de gravedad. "
            "F.3.5.2.5.2 Aletas de vigas — no cambios abruptos en zonas de rótulas "
            "plásticas; sin perforaciones ni recortes en el ancho de aleta salvo "
            "demostración por ensayos de calificación; consistente con conexión "
            "precalificada ANSI/AISC 358 o precalificación (F.3.11.1) o programa de "
            "ensayos (F.3.11.2). F.3.5.2.5.3 Zonas protegidas — región en extremos de "
            "viga sujeta a deformaciones inelásticas es zona protegida (F.3.4.1.3), "
            "extensión según ANSI/AISC 358 o precalificación/programa de ensayos; para "
            "conexiones sin reforzar, desde la cara de columna hasta la mitad del "
            "peralte de viga más allá de la rótula plástica.\n"
            "F.3.5.2.6 Conexiones: F.3.5.2.6.1 Soldaduras de demanda crítica — según "
            "F.3.1.3.4.2: (1) empalmes de columna; (2) columna-placa de base, salvo "
            "impedimento de rótula; (3) acanaladas de penetración completa de aletas "
            "y almas de vigas a columnas, salvo otra especificación en ANSI/AISC 358 "
            "o precalificación/programa de ensayos. F.3.5.2.6.2 Requisitos de "
            "conexiones viga-columna del SRS: (1) capaz de acomodar ángulo de deriva "
            "de piso de 0.02 rad como mínimo; (2) resistencia medida a flexión, en "
            "cara de columna, >=0.8*Mp de la viga conectada a 0.02 rad. F.3.5.2.6.3 "
            "Validación de la conexión — satisfacer F.3.5.2.6.2 mediante: (1) "
            "conexiones PRM-DMO según ANSI/AISC 358; (2) conexión precalificada "
            "PRM-DMO según F.3.11.1; (3) resultados de ensayos cíclicos de "
            "calificación según F.3.11.2 (mínimo 2, basados en literatura o ensayos "
            "específicos del proyecto, con límites F.3.11.2). F.3.5.2.6.4 Resistencia "
            "a cortante requerida — Vu basada en combinaciones del Título B "
            "incluyendo carga sísmica amplificada: Emh = 2*(1.1*Ry*Mp)/Lh  "
            "(F.3.5.2-1), donde Lh=distancia entre rótulas plásticas, mm. En lugar de "
            "esta ecuación, se puede usar la especificada en ANSI/AISC 358 o "
            "precalificación/programa de ensayos. F.3.5.2.6.5 Zona de panel — no se "
            "especifican requisitos especiales; resistencia se revisa según "
            "F.2.10.10.6, resistencia requerida basada en momentos en extremo de "
            "viga con combinaciones del Título B sin carga sísmica amplificada. "
            "F.3.5.2.6.6 Placas de continuidad — suministrarse según F.3.5.3.6.6 "
            "(nota: numeral referenciado F.5.3.6.6 en el texto original, corresponde "
            "a F.3.5.3.6.6). F.3.5.2.6.7 Empalmes de columnas — F.3.4.2.5; con "
            "soldaduras, acanaladas de penetración completa. Con pernos, resistencia "
            "requerida a flexión >= Ry*Fy*Zx de la menor columna; resistencia "
            "requerida a cortante del empalme del alma >= suma(Mpc)/H. Excepción: la "
            "resistencia requerida del empalme no necesita ser mayor que la "
            "determinada por análisis no lineal (F.3.3), considerando factores de "
            "concentración de esfuerzos o intensidad de esfuerzos de mecánica de "
            "fracturas.\n\n"
            "F.3.5.3 — PÓRTICOS RESISTENTES A MOMENTOS CON CAPACIDAD DE DISIPACIÓN DE "
            "ENERGÍA ESPECIAL (PRM-DES).\n"
            "F.3.5.3.1 Alcance — diseñarse según esta sección.\n"
            "F.3.5.3.2 Bases de diseño — capacidad de deformación inelástica "
            "SIGNIFICATIVA a partir de la fluencia por flexión de vigas y fluencia "
            "limitada por cortante de la zona de panel. Excepto que se permita otra "
            "cosa, las columnas se diseñan para ser MÁS FUERTES que las vigas en "
            "fluencia completa y con endurecimiento por deformación; se permite "
            "fluencia por flexión de columnas en la base. Diseño de conexiones "
            "viga-columna (incluyendo zona de panel y placas de continuidad) basado "
            "en ensayos que garanticen el desempeño de F.3.5.3.6.2, demostrado según "
            "F.3.5.3.6.3.\n"
            "F.3.5.3.3 Análisis — no se especifican requisitos de diseño especiales.\n"
            "F.3.5.3.4 Requisitos del sistema.\n"
            "F.3.5.3.4.1 Relación de momentos — deben satisfacerse en las conexiones "
            "viga-columna: suma(M*pc)/suma(M*pb) > 1  (F.3.5.3-1)\n"
            "donde: suma(M*pc)=suma de proyecciones al eje de la viga, de la "
            "resistencia nominal a flexión de las columnas (incluidas ménsulas si se "
            "usan) arriba y abajo de la unión, con reducción por la fuerza axial de "
            "la columna, calculada como suma(M*pc) = suma[Zc*(Fyc - Puc/Ag)]  "
            "(F.3.5.3-2); suma(M*pb)=suma de proyecciones al eje de la columna de las "
            "resistencias esperadas a flexión de las vigas en la rótula plástica, "
            "calculada como suma(M*pb) = suma(1.1*Ry*Fyb*Zb + Muv)  (F.3.5.3-3). "
            "Cuando los ejes de vigas opuestas en la misma conexión no coincidan, "
            "usar la línea intermedia entre ejes. Alternativamente, suma(M*pb) puede "
            "determinarse consistentemente con el diseño de la conexión precalificada "
            "según ANSI/AISC 358, precalificación (F.3.11.1) o programa de ensayos "
            "(F.3.11.2). Con conexiones de viga de sección reducida: "
            "suma(M*pb) = suma(1.1*Ry*Fyb*ZRBS + Muv)  (F.3.5.3-4), donde: "
            "Ag=área bruta de la columna, mm2; Fyc=esfuerzo fluencia mínimo "
            "especificado de la columna, MPa; Muv=momento adicional en el eje de la "
            "columna por la amplificación del cortante desde la rótula plástica "
            "hasta el eje de la columna, N·mm; Puc=resistencia a compresión requerida "
            "(valor absoluto), N; Zb=módulo de sección plástico de la viga, mm3; "
            "Zc=módulo de sección plástico de la columna, mm3; ZRBS=módulo de "
            "sección plástico mínimo en la sección reducida de la viga, mm3.\n"
            "Excepción — este requisito no aplica si se cumplen las dos condiciones "
            "siguientes: (1) para columnas con Puc < 0.3*Pc para todas las "
            "combinaciones excepto las que incluyan carga sísmica amplificada, y que "
            "cumplan cualquiera de: (a) columnas de edificios de un piso o el piso "
            "superior de uno de varios pisos; (b) columnas donde: la suma de "
            "resistencias a cortante de diseño de columnas del piso donde se aplica "
            "la excepción es menor que 20% de la suma de resistencias a cortante de "
            "diseño de todas las columnas de pórticos resistentes a momento en el "
            "piso que actúan en la misma dirección, Y la suma de resistencias a "
            "cortante de diseño de las columnas a las que se aplica en cada eje de "
            "columnas es menor que 33% de la resistencia a cortante de diseño de "
            "todas las columnas de ese eje — eje de columnas: línea o líneas "
            "paralelas de columnas separadas menos de 10% de la dimensión en planta "
            "perpendicular; resistencia a cortante de diseño calculada limitada por "
            "la resistencia a flexión en cada extremo (de vigas que conectan, o de "
            "las columnas mismas), dividida por H (altura de piso, mm); donde "
            "Pc = Fyc*Ag, N  (F.3.5.3-5); Puc=resistencia requerida a compresión, N. "
            "(2) las columnas en cualquier piso tienen relación de resistencia de "
            "diseño a cortante / resistencia requerida a cortante 50% mayor que el "
            "piso inmediatamente superior."
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
    print(f"OK: {len(rows)} chunks F.3.5.1-F.3.5.3(inicio) cargados con embedding.")


if __name__ == "__main__":
    main()
